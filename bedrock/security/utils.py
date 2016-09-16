# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import codecs
from functools import wraps
import os
import re

import yaml
from django.template.loader import render_to_string
from markdown import markdown


FILENAME_RE = re.compile('mfsa(\d{4}-\d{2,3})\.(md|yml)$')


def mfsa_id_from_filename(filename):
    match = FILENAME_RE.search(filename)
    if match:
        return match.group(1)

    return None


def parse_md_front_matter(lines):
    """Return the YAML and MD sections.

    :param: lines iterator
    :return: str YAML, str Markdown
    """
    # fm_count: 0: init, 1: in YAML, 2: in Markdown
    fm_count = 0
    yaml_lines = []
    md_lines = []
    for line in lines:
        # first line we care about is FM start
        if fm_count < 2 and line.strip() == '---':
            fm_count += 1
            continue

        if fm_count == 1:
            yaml_lines.append(line)

        if fm_count == 2:
            md_lines.append(line)

    if fm_count < 2:
        raise ValueError('Front Matter not found.')

    return ''.join(yaml_lines), ''.join(md_lines)


def parse_md_file(file_name):
    """Return the YAML and MD sections for file_name."""
    with codecs.open(file_name, encoding='utf8') as fh:
        yamltext, mdtext = parse_md_front_matter(fh)

    data = yaml.safe_load(yamltext)
    if 'mfsa_id' not in data:
        mfsa_id = mfsa_id_from_filename(file_name)
        if mfsa_id:
            data['mfsa_id'] = mfsa_id
    return data, markdown(mdtext)


def parse_yml_file(file_name):
    with codecs.open(file_name, encoding='utf8') as fh:
        data = yaml.safe_load(fh)

    if 'mfsa_id' not in data:
        mfsa_id = mfsa_id_from_filename(file_name)
        if mfsa_id:
            data['mfsa_id'] = mfsa_id

    advisories = data['advisories']
    html = []
    for cve, advisory in advisories.items():
        advisory['id'] = cve
        advisory['impact_class'] = advisory['impact'].lower().split(None, 1)[0]
        for bug in advisory['bugs']:
            bug['url'] = parse_bug_url(bug['url'])
        html.append(render_to_string('security/partials/cve.html', advisory))
    return data, '\n\n'.join(html)


def parse_bug_url(url):
    """
    Take a bug number, list of bug numbers, or a URL and output a URL.

    url could be a bug number, a comma separated list of bug numbers, or a URL.
    """
    # could be an int
    url = str(url).strip()
    if re.match(r'^\d+$', url):
        url = 'https://bugzilla.mozilla.org/show_bug.cgi?id=%s' % url
    elif re.match(r'^[\d\s,]+$', url):
        url = re.sub(r'\s', '', url).replace(',', '%2C')
        url = 'https://bugzilla.mozilla.org/buglist.cgi?bug_id=%s' % url

    return url


def chdir(dirname=None):
    """Decorator to run a function in a different directory then return."""
    def decorator(func):

        @wraps(func)
        def inner(*args, **kwargs):
            curdir = os.getcwd()
            try:
                if dirname is not None:
                    os.chdir(dirname)
                return func(*args, **kwargs)
            finally:
                os.chdir(curdir)

        return inner

    return decorator
