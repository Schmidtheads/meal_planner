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

    // set value of hidden form feidls meal_year, meal_month
    /*
    var update_script = "<script>alert('Hello');</script>";
    */
   
    href = triggeringLink.href;
    var h = 300;
    var w = 600;
    let center = centerWindowPosition(h, w);
    let top = center.top;
    let left = center.left;
    var win = window.open(href, "_blank",
    `height=${h},width=${w},resizable=yes,scrollbars=yes,top=${top},left=${left}`);
    
    win.onload = function() {
        var s = window.document.createElement('script');
        s.innerHTML("(function () {\
            $('#id_meal_year').val(" + currentYear + ");\
            $('#id_meal_month').val(" + currentMonth + ");\
            })();");
        window.document.body.appendChild(s);
        window.document.getElementById('id_meal_year').value = currentYear;
    };
    
    win.focus();

    // disable print button on meals calendar page to avoid multiple print dialogs
    // see https://www.educba.com/jquery-disable-link/

    return false;
}

function closePrintPopup(win) {
    // re-enable Print button
    // see https://www.educba.com/jquery-disable-link/

    win.close();
}


function radio_change(r_id, value) {
    let is_disabled;

    is_disabled = value == 'ALL';

    for (let i = 1; i <= 5; i++) {
        let element = '#week' + i;
        $(element).prop( 'disabled', is_disabled );
    }    
}
