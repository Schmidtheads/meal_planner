/*
 * Name:        recipequery.js
 * Description: Makes queries to search for recipes based on keywords
 * Author:      M. Schmidt
 * Date:        26-Feb-2021
 */


function addRowHandlers(table_body) {
    var rows = table_body.getElementsByTagName("tr");
    for (i = 0; i < rows.length; i++) {
      var currentRow = table_body.rows[i];
      var createClickHandler = function(row) {
        return rowClick();
      };
      currentRow.onclick = createClickHandler(currentRow);
    }
}

/**
 * Enable/Disable Search button based on if there is search text
 * 
 */
function stoppedTyping() {
    if (document.getElementById('id_recipe_search_keys').value.length > 0) {
        document.getElementById('id_recipe_search_button').disabled = false;
    } else {
        document.getElementById('id_recipe_search_button').disabled = true;
    }
}

function rowClick() {
    $('#id_recipe_search_results tbody tr').click(function() {
        $(this).addClass('bg-primary select-row').siblings().removeClass('bg-primary select-row');
    });
}

function recipeSearch() {
    let search_keys = document.getElementById('id_recipe_search_keys').value;

    $.ajax({
        url: '/meal/recipe_search',
        data: {
            'keys': search_keys
        },
        dataType: 'json',
        success: function (data) {
            showResults(data)
        }
    });

}

/**
 * Show the results of the Recipe Search
 * 
 * @param {*} recipeList list of recipes that will be displayed as a JSON object
 * 
 * Notes:
 *  This code will update a table element with each recipe in a new row.
 *  User needs at the very least see the recipe name and probably cookbook and author
 *  If a match score has been calculated then that would be good to show.
 */
function showResults(recipeList) {
    // This will simulate a search by populating the
    // custom recipe search widget with "results"

    // Find a <table> element with id="myTable":
    var table = document.getElementById("id_recipe_search_results");

    // Clear any previous results
    clearResults();

    // Check if any results found
    if (recipeList.recipes.length == 0) {
        var row = table.insertRow(0);
        var cell = row.insertCell(0);
        cell.innerHTML = "<b>No Results</b>";
    }
    else {
        // Add table headers
        // Create an empty <thead> element and add it to the table:
        var header = table.getElementsByTagName('thead')[0];
        header.classList.add("table_header");  // make table header sticky

        // Create an empty <tr> element and add it to the first position of <thead>:
        var row = header.insertRow(0);
        row.onclick = rowClick();    

        // Grab first row of results to determine headers
        first_row = recipeList.recipes[0]

        // Insert a new cell (<td>) at the first position of the "new" <tr> element:
        var col_idx = 0;
        for (const header_title in first_row) {
            var hcell = row.insertCell(col_idx);

            // Make the first column (for the ID) hidden
            if (col_idx == 0) {
                hcell.classList.add("hidden-xs", "hidden-sm", "hidden-md", "hidden-lg");
            }

            // capitalize first character
            var header_name = header_title.charAt(0).toUpperCase() + header_title.slice(1);

            hcell.innerHTML = "<b>" + header_name + "</b>"
            col_idx++;
        }

        // Add the results to the table

        var tbody = table.getElementsByTagName('tbody')[0];

        for (let i = 0; i < recipeList.recipes.length; i++) {
            var recipe = recipeList.recipes[i];

            // Create an empty <tr> element and add it to the 1st position of the table:
            var row = tbody.insertRow(0);

            // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:

            var col_idx = 0;
            for (col in recipe) {
                var cell = row.insertCell(col_idx);

                // Hide the ID cell(s)
                if (col_idx == 0) {
                    cell.classList.add("hidden-xs", "hidden-sm", "hidden-md", "hidden-lg");
                }

                // Add column text
                cell.innerHTML = recipe[col];
                col_idx++;
            }
        }

        addRowHandlers(tbody);

    }
}

/**
 * Clear the results on the table
 */
function clearResults() {
    // Find a <table> element with id="myTable":
    var table = document.getElementById("id_recipe_search_results");

    // Clear any previous results
    while (table.rows.length > 0) {
        table.deleteRow(0);
    }
    
}


/**
 * Select a recipe for the meal
 * @param {}  
 */
function selectRecipe() {
    // Get the Recipe Search Result Table
    var resultTable = document.getElementById("id_recipe_search_results");

    // Find the selected row by class
    var selectedRows = resultTable.getElementsByClassName("select-row");

    if (selectedRows.length > 1) {
        alert("More than one row selectd");
        return;
    }
    else if (selectedRows.length == 0) {
        alert("No rows selected");
        return;
    }

    for (var i = 0; i < selectedRows.length; i++) {
        // Get the recipe id from the row
        var selectedRecipeID = selectedRows[i].cells[0].innerText;
        var selectedRecipeName = selectedRows[i].cells[1].innerText;
    }

    // Update the recipe on the main form TODO
    document.getElementById("id_recipe_name_display").value = selectedRecipeName;
    var hiddenRecipeInput = document.getElementById("id-" + widgetName);
    hiddenRecipeInput.value = selectedRecipeID;
    
    // Close the modal dialog
    $("#queryBuilder").modal('hide');
}


/**
 * Set a value for the Search criteria
 */
function setSearchInput(text) {
    document.getElementById("id_recipe_search_keys").value = text;
}


/**
 * Launch the Search Recipe Modal Dialog
 */
function launch() {
    // Set the disabled state of search button on page load
    stoppedTyping();

    var $recipe_search = $('#queryBuilder');

    $recipe_search.find('.modal-content')
    .css({
      width: 625,
      height: 425,
    })
    .resizable({
      minWidth: 625,
      minHeight: 425,
      handles: 'n, e, s, w, ne, sw, se, nw',
    })
    .draggable({
      handle: '.modal-header'
    });

    $recipe_search.modal();

    /**
     * Clear result rows when Recipe Search modal appears
     */
     $recipe_search.on('show.bs.modal', function() {
        clearResults();
        setSearchInput("");
        $('#id_recipe_search_keys').focus();  // set focus on search input
    });
}
