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
 * @param {*} recipe_list list of recipes that will be displayed.
 * 
 * Notes:
 *  This code will update a table element with each recipe in a new row.
 *  User needs at the very least see the recipe name and probably cookbook and author
 *  If a match score has been calculated then that would be good to show.
 */
function showResults(recipe_list) {
    // This will simulate a search by populating the
    // custom recipe search widget with "results"

    // Find a <table> element with id="myTable":
    var table = document.getElementById("id_recipe_search_results");

    // Clear any previous results
    clearResults();

    // Check if any results found
    if (recipe_list.recipes.length == 0) {
        var row = table.insertRow(0);
        var cell = row.insertCell(0);
        cell.innerHTML = "<b>No Results</b>";
    }
    else {
        // Add table headers
        // Create an empty <thead> element and add it to the table:
        var header = table.getElementsByTagName('thead')[0];

        // Create an empty <tr> element and add it to the first position of <thead>:
        var row = header.insertRow(0);
        row.onclick = rowClick();    

        // Insert a new cell (<td>) at the first position of the "new" <tr> element:
        var hcell1 = row.insertCell(0);
        var hcell2 = row.insertCell(1);
        var hcell3 = row.insertCell(2);

        // Add some bold text in the new cell:
        hcell1.innerHTML = "<b>Recipe</b>";
        hcell2.innerHTML = "<b>Cookbook</b>";
        hcell3.innerHTML = "<b>Author</b>";

        var tbody = table.getElementsByTagName('tbody')[0];

        for (let i = 0; i < recipe_list.recipes.length; i++) {
            var recipe = recipe_list.recipes[i];

            // Create an empty <tr> element and add it to the 1st position of the table:
            var row = tbody.insertRow(0);

            // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:
            var cell1 = row.insertCell(0);
            var cell2 = row.insertCell(1);
            var cell3 = row.insertCell(2);

            // Add some text to the new cells:
            cell1.innerHTML = recipe.name;
            cell2.innerHTML = recipe.cookbook;
            cell3.innerHTML = recipe.author;  
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
 * Set a value for the Search criteria
 */
function setSearchInput(text) {
    document.getElementById("id_recipe_search_keys").value = text;
}


$(document).ready(function(){
    // Set the disabled state of search button on page load
    stoppedTyping();

    /*$("#showSearchButton").click(function(){
        $("#queryBuilder").modal("show");
    });
    */
    /**
     * Clear result rows when Recipe Search modal appears
     */
    $( "#queryBuilder" ).on('show.bs.modal', function(){
        clearResults();
        setSearchInput("");
    });
  });