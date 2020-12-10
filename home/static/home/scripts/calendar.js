/*
 * Calendar functions
 * 
 * Functions in this file will allow for dynamica upudate of a calendar on an html page
 */

//import { get } from "jquery";

let today = new Date();
let currentMonth = today.getMonth();
let currentYear = today.getFullYear();
let selectYear = document.getElementById("year");
let selectMonth = document.getElementById("month");

let months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

let monthAndYear = document.getElementById("monthAndYear");
get_meals_by_month(currentMonth, currentYear);


function next() {
    currentYear = (currentMonth === 11) ? currentYear + 1 : currentYear;
    currentMonth = (currentMonth + 1) % 12;
    get_meals_by_month(currentMonth, currentYear);
}

function jumpToToday() {
    currentYear = today.getFullYear();
    currentMonth = today.getMonth();
    get_meals_by_month(currentMonth, currentYear);
}

function previous() {
    currentYear = (currentMonth === 0) ? currentYear - 1 : currentYear;
    currentMonth = (currentMonth === 0) ? 11 : currentMonth - 1;
    get_meals_by_month(currentMonth, currentYear);
}

function jump() {
    currentYear = parseInt(selectYear.value);
    currentMonth = parseInt(selectMonth.value);
    get_meals_by_month(currentMonth, currentYear);

}

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

                let recipe = meals.month_meals[date - 1];
                let day_element = createDayElement(date, recipe, month, year);
                cell.appendChild(day_element);
                row.appendChild(cell);
                date++;
            }


        }

        tbl.appendChild(row); // appending each row into calendar body.
    }

}


function createDayElement(date, recipe, month, year) {
    // Get the recipe for the current day (meals indexed from zero, so need to subtract 1 from day)
    let recipe_name = recipe.recipe_name;
    let cookbook_abbr = recipe.abbr;
    let page_number = recipe.page;

    let dayDiv = document.createElement('div');

    let daySpan = document.createElement('span');
    daySpan.classList.add('date', 'right');
    let dayText = document.createTextNode(date);
    daySpan.appendChild(dayText);
    dayDiv.appendChild(daySpan);

    if (date === today.getDate() && year === today.getFullYear() && month === today.getMonth()) {
        daySpan.classList.add("today-cell");
    } // color today's date

    // If recipe_name is non-zero length, then there was a meal planned for the day
    if (recipe_name.length > 0) {
 
        // Create span to hold recipe name so we can control font size
        let recipeSpan = document.createElement('span');
        recipeSpan.classList.add('recipe_text');
        let recipeText = document.createTextNode(recipe_name);
        recipeSpan.appendChild(recipeText);

         // Create span to hold cookbook abbreviation and page number
        let cookbookSpan = document.createElement('span');
        cookbookSpan.classList.add('recipe_text', 'left');
        let cookbookText = document.createTextNode(cookbook_abbr);
        cookbookSpan.appendChild(cookbookText);

        let pageSpan = document.createElement('span');
        pageSpan.classList.add('recipe_text', 'right');
        let pageText = document.createTextNode('p' + page_number);
        pageSpan.appendChild(pageText);

        // Add new line after day of month
        dayDiv.appendChild(document.createElement('br'));
        dayDiv.appendChild(recipeSpan);
        dayDiv.appendChild(document.createElement('br')); // create line break
        dayDiv.append(cookbookSpan);
        dayDiv.appendChild(pageSpan);
    }

    return dayDiv;
}


function get_meals_by_month(month, year) {
    // When submitting the month, add one because for some
    // stupid reason, JavaScript has January = 0,.. December = 11
    $.ajax({
        url: '/meal/meals_by_month',
        data: {
            'year': year,
            'month': month + 1
        },
        dataType: 'json',
        success: function (data) {
            showCalendar(month, year, data)
        }
    });

}
