/*
 * Name:        table.js
 * Description: Functions related to manipulating tables in html
 * Author:      M. Schmidt
 * Date:        20-May-2021
 *
 * Notes:
 */

function getSortableValue(val) {
    if (!val) return "";
    val = val.trim();

    // 1. Check for Date Format: dd-MMM-yyyy
    const dateRegex = /^(\d{2})-([a-zA-Z]{3})-(\d{4})$/;
    const dateMatch = val.match(dateRegex);
    if (dateMatch) {
        const months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];
        const day = parseInt(dateMatch[1]);
        const monthIndex = months.indexOf(dateMatch[2].toLowerCase());
        const year = parseInt(dateMatch[3]);
        
        if (monthIndex !== -1) {
            const d = new Date(year, monthIndex, day);
            // Return timestamp for numeric comparison
            if (!isNaN(d.getTime())) return d.getTime();
        }
    }

    // 2. Check for Numeric Value
    // We remove commas (e.g., 1,200.50) to treat them as pure numbers
    const cleanNum = val.replace(/,/g, '');
    if (cleanNum !== "" && !isNaN(cleanNum)) {
        return parseFloat(cleanNum);
    }

    // 3. Default to String
    return val.toLowerCase();
}


/**
 * Enhanced Table Sort Function
 * @param {string} tableName - The table id name reference
 * @param {number} column - Index of the column
 */
function sortTable(tableName, column) {
    const table = document.getElementById(tableName);
    const tbody = table.tBodies[0];
    
    // 1. Get the specific header based on the index passed in onclick
    // We use all 'th' because your index (1, 2, etc.) includes the hidden ID column
    const allHeaders = table.querySelectorAll("th");
    const header = allHeaders[column];

    // 2. Toggle Classes (matching your 'sortableHeader' class)
    const isAsc = !header.classList.contains("asc");
    
    // Remove 'asc' and 'desc' from ALL headers to reset icons
    allHeaders.forEach(th => th.classList.remove("asc", "desc"));
    
    // Apply the new class
    header.classList.add(isAsc ? "asc" : "desc");

    const rows = Array.from(tbody.querySelectorAll("tr"));

    // 3. Sorting Logic
    const sortedRows = rows.sort((a, b) => {
        // Use column + 1 because nth-child is 1-indexed (1 = ID, 2 = Name...)
        const aCol = a.querySelector(`td:nth-child(${column + 1})`);
        const bCol = b.querySelector(`td:nth-child(${column + 1})`);
        
        const aValue = getSortableValue(aCol ? aCol.textContent : "");
        const bValue = getSortableValue(bCol ? bCol.textContent : "");

        if (aValue > bValue) return isAsc ? 1 : -1;
        if (aValue < bValue) return isAsc ? -1 : 1;
        return 0;
    });

    tbody.append(...sortedRows);
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
