# Meal Planner
Web application for meal plan management.

This web-based application provides a user interface to assist in the planning of weekly meal plans. It provides the ability to search from a database of recipes based on recipe name, cookbook, author or custom tags assoicated with the recipe. It will produce a monthly calendar in PDF format that can then be printed. It allows for one week of meals to be printed at a time and can be printed over an existing calendar.

This is a data driven application. It's usefulness increases as more recipes, cookboks and meals are entered into the system. This application does not come with any data pre-loaded.

The Meal Planner Web application conists of three compnents:
- Meals app: view meals, when they took place, and what recipe was used; plan future meals
- Coobooks app: view cookbooks and their authors
- Recipes app: view recipes, their type and rating, and from which cookbook they are from

## Requirements
The Meal Planner a
pplication is written in Python 3.10.9 and requires the following packages:
- Django 3.2.16
- Fpdf 1.7.2
- Pillow 9.4.0
- pytz 2022.7
- sqlparse 0.4.3
- asgiref 3.6.0


## Data Loader

The data loader (data_manager.py) is used to perform an intial load of the Django database from an SQL Lite database, but the data capture is completed in an MS Access database. 

The MS Access database is then converted to SQL Lite using the Python Script found [here](https://gist.github.com/snorfalorpagus/8578272).  SQL Lite is used because loading MS Access database when a 32-bit version of Office 365 is installed is problematic when using 64-bit Python.


