/*
 * Calendar functions
 * 
 * Functions in this file will allow for dynamic update of a calendar on an html page
 */

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


function createDayElement(date, meal, month, year) {
    // Get the recipe for the current day (meals indexed from zero, so need to subtract 1 from day)
    let recipe_name = meal.recipe_name;
    let cookbook_abbr = meal.abbr;
    let page_number = meal.page;
    let meal_id = meal.meal_id;

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

        // Create a link from the date to the meal details
        let dayMealLink = document.createElement('a');
        let dayText = document.createTextNode(date);
        dayMealLink.append(dayText);
        dayMealLink.title = 'Edit meal for ' + date + ' of month';
        dayMealLink.href = '/meal/' + meal_id;
        daySpan.appendChild(dayMealLink);

        // Create span to hold recipe name so we can control font size
        let recipeSpan = document.createElement('span');
        recipeSpan.classList.add('recipe_text');
        let recipeText = document.createTextNode(recipe_name);
        recipeSpan.appendChild(recipeText);

        // Create span to hold cookbook abbreviation and page number
        let cookbookSpan = document.createElement('span');
        cookbookSpan.classList.add('cookbook_text', 'left');
        let cookbookText = document.createTextNode(cookbook_abbr);
        cookbookSpan.appendChild(cookbookText);

        let pageSpan = document.createElement('span');
        pageSpan.classList.add('cookbook_text', 'right');
        let pageText = document.createTextNode('p' + page_number);
        pageSpan.appendChild(pageText);

        // Add new line after day of month
        dayDiv.appendChild(document.createElement('br'));
        dayDiv.appendChild(recipeSpan);
        dayDiv.appendChild(document.createElement('br')); // create line break
        dayDiv.append(cookbookSpan);
        dayDiv.appendChild(pageSpan);
    }
    else {
        // For days with no recipe, the clicking on the date will link to a 
        // new meal form.

        // Create a link from the date to the new meal page
        let dayMealLink = document.createElement('a');
        let dayText = document.createTextNode(date);
        dayMealLink.append(dayText);
        dayMealLink.title = 'Set meal for ' + date  + ' of month';
        dayMealLink.href = '/meal/new?date=' + year + '-' + (month+1) + '-' + date;
        daySpan.appendChild(dayMealLink);
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

    setCookie("yearmonth", year.toString() + "-" + month.toString(), 8);

}


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

    get_meals_by_month(currentMonth, currentYear);
}

function setCookie(cname, cvalue, exhours) {
    /*
     * Helper function to set a cookie
     * 
     * @param cname: name of cookie
     * @param cvalue: value of cookie
     * @param exhours: number of hours in which cookie will expire
    */

    var d = new Date();
    d.setTime(d.getTime() + (exhours * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

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