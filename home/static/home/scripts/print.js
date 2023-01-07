/*
 * Name:        print.js
 * Description: Print Calendar functions - Functions in this file will
 *              create a meal plan calendar as a PDF for printing.
 * Author:      M. Schmidt
 * Date:        7-Jan-2023
 *
 * Notes:
*/

function showPrintPopup(triggeringLink) {
    href = triggeringLink.href;
    var h = 300;
    var w = 600;
    let center = centerWindowPosition(h, w);
    let top = center.top;
    let left = center.left;
    var win = window.open(href, "_blank",
    `height=${h},width=${w},resizable=yes,scrollbars=yes,top=${top},left=${left}`);
    win.focus();
    return false;
}

function closePrintPopup(win, newID, newRepr, id, element_type="option") {
    switch(element_type) {
        case "checkbox":
            element_id = "id_recipe_types" + newID;
            $(id).append('<li><label for="' + element_id + '"><input type="checkbox" name="recipe_types" value="' + 
                newID + 
                '" id="' + element_id + '" checked> ' + 
                newRepr + '</label>');
            break;
        default:
            $(id).append('<option value=' + newID + ' selected >' + newRepr + '</option>');
    }
    win.close();
}
