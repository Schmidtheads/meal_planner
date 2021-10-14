/*
 * Name:        cookbook.js
 * Description: Cookbook functions - Functions in this file will allow for
 *              the edit and creation of authors when creating a new cookbook
 * Author:      M. Schmidt
 * Date:        13-Oct-2021
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

$("#edit_author").click(function () {
    author_id_text = $("#id_author option:selected").val();
    author_id = parseInt(author_id_text);
    if (Number.isInteger(author_id)) {
        var url = "author/" + author_id_text + "/edit";
        showEditPopup(this, url);
    }
    else {
        alert("Something Went Wrong");
    }
})
