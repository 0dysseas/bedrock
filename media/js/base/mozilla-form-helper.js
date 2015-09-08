/**
 * Utility class for general form related operations
 *
 * This code is licensed under the Mozilla Public License 1.1.
 *
 * @copyright 2013 Mozilla Foundation
 * @license   https://www.mozilla.org/MPL/1.1/ Mozilla Public License 1.1
 * @author    Jon Petto <jon@equalpartscreative.com>
 */

// create namespace
if (typeof Mozilla == 'undefined') {
    var Mozilla = {};
}

// {{{ Mozilla.FormHelper

/**
 * FormHelper object
 */
Mozilla.FormHelper = function() {};

// }}}

// Display form errors
// {{{ displayErrors()

Mozilla.FormHelper.displayErrors = function(errors, form) {
    // context for finding fields
    var $ctx = (form) ? $(form) : $(document);

    // clear out any existing errors (.errorlist should be our convention)
    $('.errorlist').remove();

    // loop through the error object
    for (var obj in errors) {
        if(errors.hasOwnProperty(obj)) {

            // reference the corresponding field
            var $field = $ctx.find('#' + obj);

            // make sure we can find the field
            if ($field.length > 0) {
                // add error message and styling
                $field.addClass('error').parent('.field').prepend('<div class="errorlist">' + errors[obj] + '</div>');
            }

        }

    }
};

// }}}
