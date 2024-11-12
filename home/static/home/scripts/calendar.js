/*
 * Name:        calendar.js
 * Description: Calendar functions - Functions in this file will allow for
 *              dynamic update of a calendar on an html page
 * Author:      M. Schmidt
 * Date:        1-Dec-2020
 * 
 * Notes:
 *  Large portions of this script related to the generation of the actual
 *  calendar are based on the code found here:
 *  https://medium.com/@nitinpatel_20236/challenge-of-building-a-calendar-with-pure-javascript-a86f1303267d
 * 
 *  This link was useful with making AJAX request with Django:
 *  https://simpleisbetterthancomplex.com/tutorial/2016/08/29/how-to-work-with-ajax-request-with-django.html
 * 
 *  And for implementing cookies to maintain the calendar month when switching 
 *  between pages in the app:
 *  https://www.w3schools.com/js/js_cookies.asp
 */

const MAX_TOOLTIP_WIDTH = 35;  // maximum character width allowed for meal notes tooltips

let today = new Date();
let selectYear = document.getElementById("year");
let selectMonth = document.getElementById("month");

let months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

let monthAndYear = document.getElementById("monthAndYear");

// initialize current month and year (will be adjusted in fetch_calendar)
let currentMonth = today.getMonth;
let currentYear = today.getFullYear;
fetch_calendar();


function next() {
    currentYear = (currentMonth === 11) ? currentYear + 1 : currentYear;
    currentMonth = (currentMonth + 1) % 12;
    get_meals_for_month(currentMonth, currentYear);
}


function jumpToToday() {
    currentYear = today.getFullYear();
    currentMonth = today.getMonth();
    get_meals_for_month(currentMonth, currentYear);
}


function previous() {
    currentYear = (currentMonth === 0) ? currentYear - 1 : currentYear;
    currentMonth = (currentMonth === 0) ? 11 : currentMonth - 1;
    get_meals_for_month(currentMonth, currentYear);
}


function jump() {
    currentYear = parseInt(selectYear.value);
    currentMonth = parseInt(selectMonth.value);
    get_meals_for_month(currentMonth, currentYear);

}


/**
 * Creates HTML for a calendar month, given the month, year and meals
 * for that month.
 * 
 * @param {*} month 
 * @param {*} year 
 * @param {*} meals 
 */
function showCalendar(month, year, meals) {

    let firstDay = (new Date(year, month)).getDay();
    let daysInMonth = 32 - new Date(year, month, 32).getDate();

    let tbl = document.getElementById("calendar-body"); // body of the calendar

    // clearing all previous cells
    tbl.innerHTML = "";

    // filing data about month and in the page via DOM.
    monthAndYear.innerHTML = months[month] + " " + year;
    selectYear.value = year;
    selectMonth.value = month;

    // creating all cells
    let date = 1;
    for (let i = 0; i < 6; i++) {
        // creates a table row
        let row = document.createElement("tr");

        //creating individual cells, filing them up with data.
        for (let j = 0; j < 7; j++) {
            if (i === 0 && j < firstDay) {
                let cell = document.createElement("td");
                let cellText = document.createTextNode("");
                cell.appendChild(cellText);
                row.appendChild(cell);
            }
            else if (date > daysInMonth) {
                break;
            }

            else {
                let cell = document.createElement("td");

                let meal = meals.month_meals[date - 1];
                let day_element = createDayElement(date, meal, month, year);
                cell.appendChild(day_element);
                row.appendChild(cell);
                date++;
            }


        }

        tbl.appendChild(row); // appending each row into calendar body.
    }

}


/**
 * Creates the html for a calendar day, populating with Meal information
 * if there is any.
 * 
 * @param {*} date 
 * @param {*} meal 
 * @param {*} month 
 * @param {*} year 
 */
function createDayElement(date, meal, month, year) {
    // Get the recipe for the current day (meals indexed from zero, so need to subtract 1 from day)
    let meal_notes = meal.notes;
    let recipe_name = meal.recipe_name;
    let recipe_id = meal.recipe_id;
    let cookbook_abbr = meal.abbr;
    let page_number = meal.page;
    let meal_id = meal.meal_id;
    let cookbook_id = meal.cookbook_id;
    let cookbook_title = meal.cookbook;
    let cookbook_author = meal.author;

    let dayDiv = document.createElement('div');
  
    let daySpan = document.createElement('span');
    daySpan.classList.add('date', 'right');
    //let dayText = document.createTextNode(date);
    //daySpan.appendChild(dayText);
    dayDiv.appendChild(daySpan);

    if (date === today.getDate() && year === today.getFullYear() && month === today.getMonth()) {
        daySpan.classList.add("today-cell");
    } // color today's date

    // If recipe_name is non-zero length, then there was a meal planned for the day
    if (recipe_name.length > 0) {
        
        // Create div for meal notes
        if (meal_notes.length > 0) { 
            let mealNotesImg = document.createElement('img');
            mealNotesImg.src = '/static/home/images/notes20.png';
            mealNotesImg.classList.add('left');
            mealNotesImg.classList.add('mealNoteIcon');
            mealNotesImg.title = wrap_text(meal_notes);
            dayDiv.appendChild(mealNotesImg);
        }

        // Create a link from the date to the meal details
        let dayMealLink = document.createElement('a');
        let dayText = document.createTextNode(date);
        dayMealLink.append(dayText);
        dayMealLink.title = 'Edit meal for ' + date + ' of month';
        dayMealLink.href = meal_id;
        daySpan.appendChild(dayMealLink);

        // Create span to hold recipe name so we can control font size
        let recipeSpan = document.createElement('span');
        recipeSpan.classList.add('recipe_text');
        // Link recipe name to meal details as well
        let recipeMealLink = document.createElement('a');
        let recipeText = document.createTextNode(recipe_name);
        recipeMealLink.append(recipeText);
        recipeMealLink.title = 'Recipe details';
        recipeMealLink.href = '../recipe/' + recipe_id;
        recipeSpan.appendChild(recipeMealLink);

        // Create div to hold cookbook abbreviation and page number
        let cookbookDiv = document.createElement('div');
        cookbookDiv.classList.add('cookbook_text', 'left', 'calendartooltip');
        let cookbookText = document.createTextNode(cookbook_abbr);
        cookbookDiv.appendChild(cookbookText);

        // Create tooltip for cookbook
        // to show title of cookbook, author
        // title is a hyperlink to cookbook detail page
        let cookbookTooltip = document.createElement('span');
        cookbookTooltip.classList.add('tooltiptext');
        let cookbookTitleLink = document.createElement('a');
        let cookbookTooltipText1 = document.createTextNode(cookbook_title);
        cookbookTitleLink.title = 'Cookbook details';
        cookbookTitleLink.href = '../cookbook/' + cookbook_id;
        cookbookTitleLink.append(cookbookTooltipText1);

        let tooltipBreak = document.createElement('br');
        let cookbookTooltipText2 = document.createTextNode('by: ' + cookbook_author);
        cookbookTooltip.append(cookbookTitleLink);
        cookbookTooltip.append(tooltipBreak);
        cookbookTooltip.append(cookbookTooltipText2);
        cookbookDiv.appendChild(cookbookTooltip);

        let pageSpan = document.createElement('span');
        pageSpan.classList.add('cookbook_text', 'right');
        let pageText = document.createTextNode('p' + page_number);
        pageSpan.appendChild(pageText);

        // Add new line after day of month
        dayDiv.appendChild(document.createElement('br'));
        dayDiv.appendChild(recipeSpan);
        dayDiv.appendChild(document.createElement('br')); // create line break

        // If the page number for the recipe is 0 (zero), it is either because
        // the recipe is not from a book (e.g. a website or recipe card) or
        // the meal may be "Leftovers" or "Dine Out".
        // So there is no need to add the cookbook & page number to the calendar date.
        if (page_number != 0) {
            dayDiv.append(cookbookDiv);
            dayDiv.appendChild(pageSpan);
        }
    }
    else {
        // For days with no recipe, the clicking on the date will link to a 
        // new meal form.

        // Create a link from the date to the new meal page
        let dayMealLink = document.createElement('a');
        let dayText = document.createTextNode(date);
        dayMealLink.append(dayText);
        dayMealLink.title = 'Set meal for ' + date  + ' of month';
        dayMealLink.href = 'new?date=' + year + '-' + (month+1) + '-' + date;
        daySpan.appendChild(dayMealLink);
    }
    
    return dayDiv;
}


/**
 * Inserts newlines in string of text. For use with elements with "title"
 * property to force new lines after specified number of characters.
 * 
 * @param {string} text       string of text to wrap
 * @param {int}    max_length maximum length in characters for a line
 * 
 * @returns {string} input string with newlines inserted
 */
function wrap_text(text, max_length = MAX_TOOLTIP_WIDTH) {
    let return_text = '';
    if (text.length > max_length) {
        // first split text by new lines
        let segments = text.split('\r\n');

        return_text = '';
        for (let j=0; j < segments.length; j++) {
            if (segments[j].length > max_length) {
                let line_segments = segments[j].split(' ');  // split long lines by words
                let new_line = '';
                for (let k=0; k < line_segments.length; k++) {
                    if ((new_line.length + line_segments[k].length) > max_length) {
                        return_text = return_text + new_line + '\r\n';
                        new_line = '';
                    } 
                    new_line = new_line + line_segments[k] + ' ';
                }
                return_text = return_text + new_line + '\r\n';
            } else {
                return_text = return_text + segments[j] + '\r\n';
            }
        }
    } else {
        return_text = text;
    }

    return return_text;
}


/**
 * Performs AJAX query to retrieve recipes for a month given the month and year.
 * 
 * @param {int} month month of year 1-12
 * @param {int} year  year as four digit number
 */
function get_meals_for_month(month, year) {
    // When submitting the month, add one because for some
    // stupid reason, JavaScript has January = 0,.. December = 11
    $.ajax({
        url: 'meals_by_month',
        data: {
            'year': year,
            'month': month + 1
        },
        dataType: 'json',
        success: function (data) {
            showCalendar(month, year, data)
        }
    });

    setCookie("yearmonth", year.toString() + "-" + month.toString(), 8);

}


/**
 * Restores calendar display based on stored cookies holding
 * year and month.
 */
function fetch_calendar() {
    /*
     * Determines which month and year will be used to display the calendar.
     * Will try to read stored cookie, or if not found use current month and year.
     * 
     * Note: month number is zero based; January = 0, December = 11
    */

    var yearmonth = getCookie("yearmonth");  // formmat of year month in YYYY-MM e.g. 2020-11
    if (yearmonth != "") {
        // parse out the year and month
        let elements = yearmonth.split("-");
        currentYear = parseInt(elements[0], 10);
        currentMonth = parseInt(elements[1], 10);
    } else {
        currentMonth = today.getMonth();
        currentYear = today.getFullYear();
    }

    get_meals_for_month(currentMonth, currentYear);
}


/**
 * Helper function to set a cookie
 * 
 * @param {string} cname   name of cookie
 * @param {string} cvalue  value of cookie
 * @param {string} exhours number of hours in which cookie will expire
*/
function setCookie(cname, cvalue, exhours) {

    var d = new Date();
    d.setTime(d.getTime() + (exhours * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}


/**
 * Helper function to get a cookie
 * 
 * @param {string} cname name of cookie
 *  
 * @returns {string} empty string
 */
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}
