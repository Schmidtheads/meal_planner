# meal_planner
Web application for meal plan management

Conists of three apps:
- coobook app: view cookbooks and their authors
- recipe app: view recipes, their type and rating, and from which cookbook they are from
- meal app: view meals, when they took place, and what recipe was used; plan future meals


## Managment Commands

A couple of management commands are provided for convenience of setting up the Meal Planner application. The Data Loader provides a tool to bulk load the Meal Planner database. The User Manager command provides the ability to add user accounts to the Meal Planner database.

### Data Loader

The data loader (`data_manager.py`) is used to perform an intial bulk load of the Django database from an SQL Lite database. This is provide an alternative to using the Meal Planner web application to do data entry, which would have a high level of effort for a large amount of data.

**A third party application is required for data entry** such as [SQLliteStudio](https://sqlitestudio.pl/+
398). The data module used in the SQLlite database must match that of the database used for the Meal Planner application. 

#### Usage

```
manage.py data_manager [-h] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH]
                       [--traceback] [--no-color] [--force-color] [--skip-checks]
                       db_path
```

From a terminal prompt run the Data Loader using Django's `manage.py` script

```batch
C:> python manage.py data_manager C:\
```


### User Manager
