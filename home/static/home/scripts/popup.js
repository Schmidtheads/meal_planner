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


function centerWindowPosition(h, w) {
    // Fixes dual-screen position                             Most browsers      Firefox
    const dualScreenLeft = window.screenLeft !==  undefined ? window.screenLeft : window.screenX;
    const dualScreenTop = window.screenTop !==  undefined   ? window.screenTop  : window.screenY;

    const width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
    const height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;

    const systemZoom = width / window.screen.availWidth;
    const left = (width - w) / 2 / systemZoom + dualScreenLeft;
    const top = (height - h) / 2 / systemZoom + dualScreenTop;

    return { left, top }
}

function showEditPopup(triggeringLink, url) {
    var baseURI = triggeringLink.baseURI;
    var href = baseURI.substring(0, baseURI.lastIndexOf("/") + 1) + url;
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

function showAddPopup(triggeringLink) {
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

function closePopup(win, newID, newRepr, id, element_type="option") {
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

