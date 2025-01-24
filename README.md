# Meal Planner
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

The User Manager command module is used to create Groups in the Django security module in order to manage user access to the database. A configuration file in JSON format defines the names of the groups, the permissions granted to each group.

#### Usage

```
manage.py user_manager [-h] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH]
                       [--traceback] [--no-color] [--force-color] [--skip-checks]
                       [--config CONFIGFILE] 
```

#### Configuration File
The generic format for the configuration file is shown below.

```json
{
    "metadata" : {
        "description": [
            "Everything in meta data section is ignored by the application",
            "and is meant for documentation purposes"
        ]
    },
    "settings": {
        "groups": [
            {
                "name": "<Group1_Name>",
                "permissions": [
                    "<permission_1>",
                    "<permission_2>",
                    ...
                    "<permission_N>"
                ]
            },
            {
                "name": "<Group2_Name>",
                "permissions":  [
                    "<permission_1>",
                    "<permission_2>",
                    ...
                    "<permission_N>"
                ]
            },
            ...
            {
                "name": "<GroupN_Name>",
                "permissions":  [
                    "<permission_1>",
                    "<permission_2>",
                    ...
                    "<permission_N>"
                ]
            }                
        ]
    }
}
```

Where:
- **metadata**: element whose contents are ignored by the application; it can contain anything and is meant for documentation
- **description**: sample element within metadata element, other ideas: version, last_updated, author
- **settings**: element containing the configuration settings MANDATORY
- **groups**: element containing Group definitions MANDATORY
- **name**: name to be given the permission Group
- **permissions**: list of strings where each string is the name of a valid Django table permission

## Deployment

The Meal Planner web app can be deployed using the PowerShell script found in the `deploy` sub-folder. Currently the deployment is only supported on a Raspberry Pi running Linux (Ubuntu) with Apache Web Server.

Within the `deploy` folder are the following required files:
- **apache_template.xml**: template file used to configure the Apache Server
- **deploy_mealplanner.json**: sample configuration file required by the deployment script (details described below)
- **deploy_mealplanner.ps1**: Powershell script used to execute the installation

The configuration file in JSON format must be configured. Certain pre-requisites on the target system must be met prior to deploying the web application. This section describes what is needed for a successful deployment.

### Pre-Requisites

1. System Requirements
The Powershell deployment script has been designed to be cross platform (with some constraints), but has only be tested on the following platform:

```
Raspberry Pi 4 Model B Rev 1.2
ARMv7 Processor rev 3 (v7l)
Linux 5.10.103-v7l+ (Ubuntu/Linaro 8.4.0-3ubuntu1)
```
2. The user that installs the web application must have root user access.

#### Required Software

The following software _must be installed_ prior to running the deployment script:
- Apache Server version 2.4.59 / build 2024-05-24T22:36:21

#### Configuration File

The configuration file used with the deployment script has the following format:

```json
{
    "metadata": {
        "description": "",
        "notes": [
            "",
            ...
            ""
        ]
    },
    "settings": {
        "appRepoZipfile": "<url to meal planner git repo zip file downlaod>",
        "appRoot": "<full path to web app root folder>",
        "appName": "<name of web app>",
        "groupOwner": "<linux group name owning web app>",
        "allowedHosts": [
            "<FQDN for for web app|IP Address>",
            "<Alternate FQDN for web app|IP Address>"
        ],
        "python": {
            "minVersion": "<min version number of Python>",
            "venvHome": "<folder name with Python virtual environment>"
        },
        "database": "<full path to django database>",
        "apache": {
            "configFilePath": "<full path to Apache configuration file>"
        },
        "wsgiSettings": {
            "servername": "<FQDN of server>",
            "serveralias": "<FQDN of web server alias>",
            "approot": "<full path of web app root>",
            "appalias": "<alias of web app>",
            "processname": "<name to give process wsgi will run under>"
        }
    }
}
```

Where:
- **metadata**, **description**, **notes**: user defined metadata to provide meaningful information/context
    to other users; this section is ignored by the installation
- **settings**: all values in this section are used by the installation
- **appRepoZipfile**: a fully qualified URL to the Meal Planner git repo download; required to access version of
    source code to be installed on server
- **appRoot**: full path to web app root folder on server (e.g. `/srv/webapps`)
- **appName**: name to be assigned to the web app; this will become a folder undre the *appRoot* folder; the name
    must be unique in the folder (e.g. `meal_planner_v1-2`)
- **groupOwner**: the Linux group that owns the *appRoot* folder (and will hence own the web app); must be existing
    group; check server to confirm valid group (e.g. `www-data`)
- **allowedHosts**: list of fully qualified server names or IP addresses that will be used client side to access
    web app (e.g. `www.web.mealplanner.local`)
- **python**: settings used to define Python environment to be used by web app
- **minVersion**: minimum Python version number that web application will support (e.g. `3.10.9`)
- **venvHome**: name of folder (in the web app folder - *appName*) where the Python virtual environment will be
    created (e.g. `venv`)
- **database**: (optional) full path to the database of *an existing deployment of the Meal Planner app*;
    if supplied, this database will be copied into the new deployment
- **apache**: section for Apache web server settings
- **configFilePath**: full path to the Apache Web Server configuration file (e.g. `/etc/apache2/sites-available/000-default.conf`)
- **wsgiSettings**: section for WSGI settings
- **servername**: fully qualified server name (e.g. web.mealplanner.local) (must be in line with *allowedHosts*)
- **approot**: full path to web app root folder (*must* be same as *appRoot* setting above)
- **appalias**: alias of web app (e.g. `planner`)
- **processname**: name to be given to WSGI process (must not conflict with other WSGI process names) (e.g. `mpdev`)

### Running the Deployment
The run the deployment of the Meal Planner application, and assuming all pre-requisites have been met and the configuration file updated, complete the following steps:
1. Log into the server where the Meal Planner is to be installed.
2. Copy the `deploy` folder from Meal Planner source code onto the server into your home directory.
3. Open a Terminal window.
4. Use the `cd` command to enter the `deploy` folder.
3. Run the following command:
```bash
$ sudo deploy_mealplanner.ps1 deploy_mealplanner.json
```