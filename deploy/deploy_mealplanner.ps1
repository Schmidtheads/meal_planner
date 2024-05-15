<#
    Name        : deploy_mealplanner.ps1
    Description : Script to deploy Meal Planner web application
    Date        : 23-Jan-2024
    Author      : M. Schmidt

    Usage:

    install_mp.ps1 <config_file>
#>

#Requires -RunAsAdministrator

# Script Parameters
param (
    # ConfigFile - (required) full path to configuration JSON file defining deployment
    [Parameter(Mandatory=$true)]
    [string]$ConfigFile,
    [switch]$DebugMode
)

# Script Variables
$Script:DefaultApacheConfFile="/etc/apache2/sites-available/000-default.conf"
$Script:DEBUG = $false


function Backup-File {
    <#
        .SYNOPSIS
        Creates a copy of specific file for backup purposes 
        .DESCRIPTION
        Creates a copy of the specified file by putting a time stamp and
        .bak extension on copy of file. Timestamp is in YYYYMMDDHHmm format
        where YYYY is four digit year; MM is two digit month, DD two digit
        day, HH two digit hour (24hr) and mm two digit minutes
        .INPUTS
        (required) file path to file
        .OUTPUTS
        File path to backup file
    #>
    param (
        # SourcePath - (required) file path to be backed up
        [Parameter(Mandatory=$true)]
        [string]$SourcePath
    )

    # Backup up existing file
    $backupFile = "$($SourcePath).$(Get-Date -Format yyyyMMddHHmm).bak"
    Write-Host "Backing up $($SourcePath) file to $($backupFile)..."
    Copy-Item $SourcePath $backupFile -Force

    # Test if backup file path is valid, if not
    # return empty string
    if ((Test-Path -Path $backupFile) -eq $false) {
        $backupFile = ""
    }

    return $backupFile
}


function Get-TempFolder {
    <#
        .SYNOPSIS
        Get path to temporary folder
        .DESCRIPTION
        Get the temporary folder based on the current operating system.
        .OUTPUTS
        Full path to temporary folder
    #>

    if ($IsLinux) {
        return "/tmp"
    } else {
        return $env:TEMP
    }
}


function Get-PythonExe {
    <#
        .SYNOPSIS
        Provide full path to Python executable
        .DESCRIPTION
        Determine the path to the Python executable, assiming version 3.x.
        Considers operating system and if virtual envrionment provided.
        User has option to override path.
        .INPUTS
        (optional) path to Python virtual environment
        .OUTPUTS
        File path to Python executable.
    #>
    param (
        # VenvPath - (optional) Path to Python virtual environment
        [string]$VenvPath = ""
    )

    $pythonPath = ""
    if ($IsLinux) {
        if ($VenvPath.Length -eq 0) {
        $pythonPath = which python3
        }
        else {
            $pythonPath = "$($VenvPath)/bin/python"
        }
    }
    else {
        if ($VenvPath.Length -eq 0) {
            # If multiple Python versions installed, return first
            $pythonPath = (where.exe python)[0]
        }
        else {
            $pythonPath = "$($VenvPath)\Scripts\python.exe"
        }
    }

    If ($VenvPath.Length -eq 0) {
        Write-Host "Found BASE Python exe at $($pythonPath)."

    } else {
        Write-Host "Found VIRTUAL ENV Python exe at $($pythonPath)."
    }

    $userPythonPath = Read-Host "Press <ENTER> to use Python exe, or enter alternative location"
    if ($userPythonPath.Length -gt 0) {
        if (Test-Path -Path $userPythonPath) {
            $pythonPath = $userPythonPath
        }
        else {
            Write-Host "***ERR*** Invalid path to Python executable. ABORTING."
            Exit
        }
    }

    return $pythonPath
}


function Get-IsPythonVersionValid {
    <#
        .SYNOPSIS
        Check that version of Python reaches minimum requirements
        .DESCRIPTION
        Verifies that the available Python version meetings minimum
        requirements.
        .INPUTS
        Path to Python executable.
        .OUTPUTS
        True if Python Version is valid, False if not
    #>
    param (
        # PythonPath - (required) File path to Python executable
        [Parameter(Mandatory=$true)]
        [string]$PythonPath
    )

    $pyFullVersion = (Invoke-Expression "$($PythonPath) --version").Split()[1]
    Write-Host "Version of Python is $($pyFullVersion)"
    $pyVersion = $pyFullVersion.Split(".")

    $pyMinVersion = $config.settings.python.minVersion.Split(".")

    # Check major, minor and release
    $valid = [int]$pyVersion[0] -ge [int]$pyMinVersion[0] -and [int]$pyVersion[1] -ge [int]$pyMinVersion[1] -and [int]$pyVersion[2] -ge [int]$pyMinVersion[2]

    return $valid
}


function Get-Apache {
    <#
        .SYNOPSIS
        Check if Apache is running on deployment server.
        .DESCRIPTION
        Identify Apache running process and derive path to executable from it.
        .OUTPUTS
        Return location of Apache installation.
    #>
    $apachePath = (Get-Process -Name apache2 -ErrorAction:Ignore | Select-Object CommandLine -first 1 | ForEach-Object {$_.CommandLine}[0])

    # For testing/debug purposes, return "fake" folder
    if ($null -eq $apachePath -and $DEBUG) {
        $apachePath = $env:TEMP  # Use a valid, but harmless folder for testing
    }

    return $apachePath
}


function Set-Apache {
    <#
        .SYNOPSIS
        Update conifguration for Apache Web Server
        .DESCRIPTION
        Makes a copy (as a backup) and then updates the Apache
        configuration file with virtual host information for the
        web application.
    #>

    # Check if default location for config overridded
    if ($null -eq $config.settings.apache.configFilePath) {
        $apacheConfFile = $DefaultApacheConfFile
    }
    else {
        $apacheConfFile = $config.settings.apache.configFilePath
    }

    # Check if config file exists
    if ((Test-Path -Path $apacheConfFile) -eq $false) {
        Write-Host "***ERR*** Invalid path for Apache conf file ($($apacheConfFile)). ABORTING."
        Exit
    }

    # Backup up existing conf file
    $backupFile = Backup-File $apacheConfFile

    # If backup failed, abort
    if (($backupFile) -eq "") {
        Write-Host "***WRN*** Backup of conf file failed. ABORTING."
        Exit
    }
    else {
        Write-Host "...backup successful"
    }

    # Make changes to 000-default.conf

    #Exit # TODO: Remove
     
    # Read template conf xml
    $confXML = Get-Content -Path ./apache_template.xml

    $outputXML = @()  # create new empty array for output
    # Replace tokens with settings from configuration
    ForEach ($line in $confXML) {
        $config.settings.wsgiSettings.PSObject.Properties | ForEach-Object {
            if ($line.contains("[$($_.Name)]")) {
                $line = $line.replace("[$($_.Name)]", $_.Value)
            }
        }
        
        if ($line.contains("[venv]")) {
            $line = $line.replace("[venv]", $config.settings.python.venvHome)
        }

        if ($line.contains("[appname]")) {
            $line = $line.replace("[appname]", $config.settings.appName)
        }
        
        $outputXML += $line
    }
    Out-File -InputObject $outputXML -Append -FilePath "$($apacheConfFile)"
    # Locate any existing WSGI settings
    # ScriptAlias; Alias [media, static]
    # DaemonProcess; ProcessGroup
}


function Get-SourceCode {
    <#
       .SYNOPSIS
       Downloads source code from GitHub
       .DESCRIPTION
       The source is downloaded as a zip file to a temporary location.
       .INPUTS
       GitHubURL - (required) URL to repo zip file
       OutFile - (required) Location where repo is downloaded
    #>
    param (
        # GitHubURL - URL to zip file of repo
        [Parameter(Mandatory=$true)]
        [string]$GitHubURL,
        # OutFile - File path to location where zip file will be saved
        [Parameter(Mandatory=$true)]
        [string]$OutFile
    )

    #$credentials = Get-Credential -Message "Enter credentials for URL $($GitHubURL)"
    
    Write-Host ="`nDownloading Meal Planner repo from $($config.settings.appRepoZipfile)..."    
    #Invoke-WebRequest $githubURL -Credential $credentials -Outfile $outFile
    Invoke-WebRequest $githubURL -Outfile $outFile

}


function Deploy-Code {
    <#
        .SYNOPSIS
        Unzip a file to specified location
        .DESCRIPTION
        Unzips a zip file into a defined application location.
        Changes group ownership on the deployed files to the specified 
        group. Changes permissions on the database file and parent folder
        so that the group can modify it.
        .INPUTS
        ZipFilePath (required) - File path to the zipfile
        AppRoot (reuquired) - Parent folder of application
        AppName (required) - Name of application
        GroupOwner (Required) - Name of group to own files
    #>
    param (
        # ZipFilePath - File path to the zipfile
        [Parameter(Mandatory=$true)]
        [string]$ZipFilePath,
        # AppRoot - Parent folder of application
        [Parameter(Mandatory=$true)]
        [string]$AppRoot,
        # AppName - Name of application
        [Parameter(Mandatory=$true)]
        [string]$AppName,
        # GroupOwner - Name of group to own files
        [Parameter(Mandatory=$true)]
        [string]$GroupOwner
    )

    # Unzip into the applicaton root (appRoot), then rename the repo
    # to actual application name
    Write-Host "`nUnzipping $($ZipFilePath) to $($AppRoot)..."
    Expand-Archive $ZipFilePath -DestinationPath $AppRoot
    
    # Loop through folders in the DestionationPath (AppRoot) and
    # find the most recent folder which will be what was just unzipped
    $unZipFolder = $null
    $mostRecent = Get-Date -Year 1970 -Month 1 -Day 1
    Get-ChildItem -Path $AppRoot -Attribute Directory | ForEach-Object `
        -Process {
            if ($_.LastWriteTime -gt $mostRecent) {
                $mostREcent = $_.LastWriteTime
                $unZipFolder = $_.Name
            }
        }

    if ($null -ne $unZipFolder) {
        $unzipFolderPath = Join-Path -Path $AppRoot -ChildPath $unZipFolder
        $appFolderPath = Join-Path -Path $AppRoot -ChildPath $AppName
        Write-Host "Renaming extracted folder $($unZipFolder) to $($appFolderPath)"
        Rename-Item -Path "$($unzipFolderPath)" -NewName "$($appFolderPath)"
    } else {
        Write-Host "***ERROR*** Could not find extracted source code"
        Exit
    }

    # Update group ownership of application
    if ($IsLinux) {
        Write-Host "Updating group ownership of files to $($GroupOwner)..."

        chgrp -R $GroupOwner (Join-Path -Path $AppRoot -ChildPath $AppNAme)
        
        # Give write access to database and parent folder of database
        # to group to allow database to be modified
        chmod g+w (Join-Path -Path $AppRoot -ChildPath $AppName)
        if (Test-Path (Join-Path $AppRoot $AppName "*.sqlite3")) {
            chmod g+w (Join-Path $AppRoot $AppName "*.sqlite3")
        } else {
            Write-Host "***WARNING*** No .sqlite3 database file found."
        }
        
    }

    # Clean up - remove temp zip file
    Write-Host "Cleaning up - deleting $($ZipFilePath)"
    Remove-Item -Path $ZipFilePath
}

function Update-AllowedHosts {
    <#
        .SYNOPSIS
        Updates the ALLOWED_HOSTS setting in the Django application
        .DESCRIPTION
        Updates the ALLOWED_HOSTS setting found in settings.py file
        of the Django web application.
        .INPUTS
        AppRoot - (required) Parent folder of application
        AppName - (required) Name of application
        HostList - (required) List of host names to add
        .OUTPUTS
        Returns $true if successful, $false if not
    #>
    param (
        # AppRoot - Parent folder of application
        [Parameter(Mandatory=$true)]
        [string]$AppRoot,
        # AppName - Name of application
        [Parameter(Mandatory=$true)]
        [string]$AppName,
        # HostList - list of hostnames to add
        [Parameter(Mandatory=$true)]
        [string[]]$HostList
    )

    Write-Host "`nUpdating ALLOWED_HOSTS in settings.py"

    $success = $true  # assume success

    # Make backup of settings.py file
    # Full path of settings.py file is <AppRoot>/<AppName>/meal_planner/settings.py
    $settingsPath = Join-Path $AppRoot $AppName "meal_planner" "settings.py"
    $backupFile = Backup-File $settingsPath

    if ($backupFile -eq "") {
        Write-Host "***ERROR*** Backup of settings.py failed"
        return $false
    }

    # Open settings file 
    # Use -Raw option to read file in as one string
    # Updated ALLOWED_HOSTS list with hostList
    try {
        (Get-Content -Path $settingsPath -Raw) `
        -replace [Regex]::Escape("ALLOWED_HOSTS = []"), ("ALLOWED_HOSTS = [" + "'$($HostList -join "','")'" + "]")  | `
        Set-Content -Path $settingsPath
        $success = $true
    }
    catch {
        Write-Host "***Error*** Unable to update settings.py"
        $success = $false
    }

    return $success
}


function Get-StaticFiles {
    <#
        .SYNOPSIS
        Copies static files in Django application to serveable location
        .DESCRIPTION
        Copies static files (images, JavaScript files, etc) to a fixed
        location from which the files can be properly served.
        .INPUTS
        PythonPath - (required) File path to the Python executable
        .OUTPUTS
        Returns $true if succesful, $false if not
    #>
    param (
        # PythonPath - File path to Python executable
        [Parameter(Mandatory=$true)]
        [string]$pythonPath,
        [string]$fullAppPath  
    )

    # - run python3 manage.py collectstatic a (files may be put in /srv/webapps/appname/srv/webapps/appname/static...)
    #   copy it to /srv/webapps/appname/home/static/... (see Trello for details)
    Write-Host "`nCollect Static Files $($fullAppPath)/manage.py"
    $result = (Invoke-Expression "$($pythonPath) $($fullAppPath)/manage.py collectstatic --clear --noinput")

    if (-not $null -eq $result) {
        $last_line = $result[-1]
        $file_count = $last_line.split()[0]
    
        $success = ($last_line.ToLower().Contains('static files copied')) -and ($file_count -gt 0)
    } else {
        $success = $false
    }

    return $success
}


function main {
    <#
        .SYNOPSIS
        Main Function
        .DESCRIPTION
        This is where it all happens.
        .INPUTS
        ConfigFile - (required) File path to configuration file
        DebugMode - flag to indicate running in Debug mode
    #>

    param (
        # ConfigFile - File path to configuration file
        [Parameter(Mandatory=$true)]
        [string]$ConfigFile,
        [System.Boolean]$DebugMode
    )

    # Validate arguments
    if ($ConfigFile.Length -eq 0) {
        Write-Host "Config file not specified"
        Exit 1
    }

    $Debug = $DebugMode

    # Check if running as root (if using Linux)
    if ($IsLinux) {
        if ($(whoami) -ne "root") {
            Write-Host "***ERROR*** Script must be run as root"
            Exit
        }
    }

    # Read in configuration file
    $Script:config = Get-Content -Raw $ConfigFile | ConvertFrom-Json

    # Download and upack zipped source code from repo
    $appZipfile = Split-Path -Path $config.settings.appRepoZipfile -Leaf
    $appZipfilePath = Join-Path -Path (Get-TempFolder) -ChildPath $appZipfile
    
    Get-SourceCode $config.settings.appRepoZipfile $appZipfilePath
   
    # Unzip into the applicaton root (appRoot), then rename the repo
    # to actual application name
    
    Deploy-Code $appZipfilePath $config.settings.appRoot $config.settings.appName $config.settings.groupOwner

    # ------------------------ Python Tasks ------------------------

    # Create Python virtual environment
    Write-Host "`nSet up Python Virtual Environment"

    # Get base Python executable and check if version meets requirements
    $pythonExePath = Get-PythonExe
    if ((Get-IsPythonVersionValid $pythonExePath) -ne $true) {
        Write-Host "Python version does not meet minimum version requirement of $($config.settings.python.minVersion)"
        Exit
    }

    $pythonVenvFullPath = Join-Path $config.settings.appRoot $config.settings.appName $config.settings.python.venvHome
    Write-Host "`nCreating Python Virtual Env in $($pythonVenvFullPath)"
    Invoke-Expression "$($pythonExePath) -m venv $($pythonVenvFullPath)"

    # All further work now done in virtual environment
    # Get path to Python executable in virtual environment
    $pythonVenvPythonExe = Get-PythonExe $pythonVenvFullPath

    # Upgrade pip
    Invoke-Expression "$($pythonVenvPythonExe) -m pip install --upgrade pip"

    # Deploy Python packages & other dependencies
    $requirementsPath = Join-Path $config.settings.appRoot $config.settings.appName "requirements.txt" 
    Invoke-Expression "$($pythonVenvPythonExe) -m pip install -r $($requirementsPath)"

    # Collect static items
    if ((Get-StaticFiles $pythonVenvPythonExe (Join-Path $config.settings.appRoot $config.settings.appName)) -eq $false) {
        Write-Host "***ERROR*** Collect static files FAILED. ABORTING"
        Exit
    }

    # - update <app>\settings.py ALLOWED_HOSTS setting to include '<server_name>'
    if ((Update-AllowedHosts `
            $config.settings.appRoot `
            $config.settings.appName `
            $config.settings.allowedHosts ) -eq $false) {
        Write-Host "***ERROR*** Update Allowed Hosts FAILED. ABORTING"
        Exit
    }
    
    # ------------------------- Web Server Tasks -------------------------

    # Check OS 
    if ($IsLinux -or $DEBUG) {
        # TODO: check if Apache is running
        $apachePath = Get-Apache
        if ($apachePath.Length -gt 0) {
            Write-Host "`nApache web server found running. Will modify for web app deployment."
            # Modify Web Server (Apache)
            Set-Apache

        }
    }

    # Other things that need to be added to script
    # - use manage.py to create empty sqlite database?
    # - revisit collect static and how it handles admin files (see Trello for details)
    # - may need to update settings.py so that URL variables factor in application name or update WSGI Alias (See Trello)
    # - *may* have to update names of images in media/images to match what application _thinks_ they are, otherwise
    #   there will be broken images
    
    Write-Host "---Done---"
}


<#
 ------------------------- MAIN -------------------------
#>
main $ConfigFile $DebugMode.IsPresent
