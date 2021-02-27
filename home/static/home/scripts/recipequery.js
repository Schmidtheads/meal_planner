/*
 * Name:        recipequery.js
 * Description: Makes queries to search for recipes based on keywords
 * Author:      M. Schmidt
 * Date:        26-Feb-2021
 */

function recipe_search(search_keys) {
    $.ajax({
        url: '/recipe/[to_be_determined]',
        data: {
            'keys': search_keys
        },
        dataType: 'json',
        success: function (data) {
            /*
            Need to determine what the exact format of the recipes returned will be
            Must include the unique identifier!!!!
            */
            showResults(recipe_list)
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


}