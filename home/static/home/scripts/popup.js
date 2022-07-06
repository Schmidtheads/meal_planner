/*
 * Name:        popup.js
 * Description: Popup functions - Functions in this file will allow for
 *              the edit and creation of model items via a popup window
 * Author:      M. Schmidt
 * Date:        5-Jul-2022
 *
 * Notes:
 *  Guidance on implementing the edit/creation of authors from this page:
 *  https://tinyurl.com/4b5yt3rw
*/

function showEditPopup(triggeringLink, url) {
    var baseURI = triggeringLink.baseURI;
    var href = baseURI.substring(0, baseURI.lastIndexOf("/") + 1) + url;
    var win = window.open(href, "_blank",
        'height=300,width=600,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function showAddPopup(triggeringLink) {
    href = triggeringLink.href;
    var win = window.open(href, "_blank", 
        'height=300,width=600,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function closePopup(win, newID, newRepr, id) {
    $(id).append('<option value=' + newID + ' selected >' + newRepr + '</option>')
    win.close();
}
