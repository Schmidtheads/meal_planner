/*
 * Name:        table.js
 * Description: Functions related to manipulating tables in html
 * Author:      M. Schmidt
 * Date:        20-May-2021
 *
 * Notes:
 */

/**
 * Sorts the rows in an HTML table 
 *  
 * @param {*} tableName - name of the table element
 * @param {*} n         - column number to sort by
 */
function sortTable(tableName, n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById(tableName);
    switching = true;
    //Set the sorting direction to ascending:
    dir = "asc";
    /*Make a loop that will continue until
    no switching has been done:*/
    while (switching) {
        //start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /*Loop through all table rows (except the
        first, which contains table headers):*/
        for (i = 1; i < (rows.length - 1); i++) {
            //start by saying there should be no switching:
            shouldSwitch = false;
            /*Get the two elements you want to compare,
            one from current row and one from the next:*/
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];
            /*check if the two rows should switch place,
            based on the direction, asc or desc:*/
            if (dir == "asc") {
                if (x.innerText.toLowerCase() > y.innerText.toLowerCase()) {
                    //if so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (x.innerText.toLowerCase() < y.innerText.toLowerCase()) {
                    //if so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            /*If a switch has been marked, make the switch
            and mark that a switch has been done:*/
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            //Each time a switch is done, increase this count by 1:
            switchcount++;
        } else {
            /*If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again.*/
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}


/**
 * Make form busy and sort table column. Used when not making
 * a callback to the server.
 * 
 * @param {str} table_name - name of table to sort
 * @param {int} col - column number to sort on
 */
function sortTableColumn(table_name, col) {
    let DELAY_FOR_REFRESH = 1000; // 1000ms, minimum setting
    
    // Set busy cusrsor for page while sorting
    $("body").css("cursor", "progress");

    // Change default header cursor to progess
    setTimeout( () => {
        sortTable(table_name, col);
        // set cursor to normal after sort complete
        $("body").css("cursor", "default");
    }, DELAY_FOR_REFRESH)     
}