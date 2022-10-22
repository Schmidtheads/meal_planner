# meal_planner
Web application for meal plan management

Conists of three apps:
- coobook app: view cookbooks and their authors
- recipe app: view recipes, their type and rating, and from which cookbook they are from
- meal app: view meals, when they took place, and what recipe was used


## Data Loader

The data loader (data_manager.py) is used to perform an intial load of the Django database from an SQL Lite database, but the data capture is completed in an MS Access database. 

The MS Access database is then converted to SQL Lite using the Python Script found [here](https://gist.github.com/snorfalorpagus/8578272).  SQL Lite is used because loading MS Access database when a 32-bit version of Office 365 is installed is problematic when using 64-bit Python.


