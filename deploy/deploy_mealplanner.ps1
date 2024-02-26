<#
    Name        : deploy_mealplanner.ps1
    Description : Script to deploy Meal Planner web application
    Date        : 23-Jan-2024
    Author      : M. Schmidt

    Usage:

    install_mp.ps1 <config_file>
#>

# Script Variables
$script:DefaultApacheConfFile="/etc/apache2/sites-available/000-default.conf"


function Get-Config {
    <#
    Read configuration file and create variables to hold settings
    #>
    param (
        $ConfigFile
    )

    Foreach ($i in $(Get-Content $ConfigFile)){
        # strip and part of string after and inclduing hash (#)
        $clean = $i.split('#')[0]
        if ($clean.Length -gt 0) {
            $variableName = $clean.split("=")[0]
            $variableValue = $clean.split("=",2)[1].Trim()
            Write-Host "Setting variable $($variableName) = '$($variableValue)'"
            Set-Variable -Name $variableName -Value $variableValue -Scope Script
        }

    }
}

function Get-PythonExe {
    <#
    Provide full path to Python executable. Assume Python 3.x
    #>
    param (
        $venvPath
    )

    $pythonPath = ""
    if (%$IsLinux) {
        if ($venvPath.Length -eq 0) {
        $pythonPath = which python3
        }
        else {
            $pythonPath = "$($venvPath)/bin/python"
        }
    }
    else {
        if ($venvPath.Length -eq 0) {
            # If multiple Python versions installed, return first
            $pythonPath = (where.exe python)[0]
        }
        else {
            $pythonPath = "$($venvPath)\Scripts\python.exe"
        }
    }

    return $pythonPath
}

function Get-IsPythonVersionValid {
    <#
    Check that version of Python reaches minimum requirements
    #>
    param (
        $pythonPath
    )

    $pyVersion = (Invoke-Expression "$($pythonPath) --version").Split()[1].Split(".")
    Write-Host "Version of Python is $($pyVersion)"

    $pyMinVersion = $pythonMinVersion.Split(".")

    # Check major, minor and release
    $valid = [int]$pyVersion[0] -ge [int]$pyMinVersion[0] -and [int]$pyVersion[1] -ge [int]$pyMinVersion[1] -and [int]$pytVersion[2] -ge [int]$pyMinVersion[2]

    return $valid
}


function Get-Apache {
    <#
    Check if Apache is running on deployment server.
    Return location of installation.
    #>
    $apachePath = (get-process -Name apache2 -ErrorAction:Ignore | Select-Object CommandLine -first 1 | ForEach-Object {$_.CommandLine}[0])

    return $apachePath
}


function Set-Apache {

    # Check if default location for config overridded
    if (Test-Path variable:apacheConfFile -not) {
        $apacheConfFile = $DefaultApacheConfFile
    }

    # Check if config file exists
    if (Test-Path -Path $apacheConfFile -not) {
        Write-Host "***ERR*** Invalid path for Apache conf file ($($apacheConfFile)). ABORTING."
        Exit
    }

    # Backup up existing conf file
    Write-Host "Backing up Apache conf file..."
    $backupFile = "$($apacheConfFile).$(Get-Date -Format yyyyMMddHH:ss)"
    Copy-Item $apacheConfFile $backupFile -Force

    # If backup failed, abort
    if (Test-Path -Path $backupFile -not) {
        Write-Host "***WRN*** Backup of conf file failed. ABORTING."
        Exit
    }

    # Make changes to 000-default.conf

    
    # Locate any existing WSGI settings
    # ScriptAlias; Alias [media, static]
    # DaemonProcess; ProcessGroup
}


function main {
    param (
        $ConfigFile
    )
    # Main function

    # Validate arguments
    if ($ConfigFile.Length -eq 0) {
        Write-Host "Config file not specified"
        Exit 1
    }

    # Read in configuration file
    Get-Config($ConfigFile)

    # Download and upack zipped source code from repo
    $appZipfile = Split-Path -Path $appRepoZipFile -Leaf
    $appZipfilePath = "$($env:TEMP)\$($appZipfile)"
    
    Write-Host ="`nDownloading Meal Planner repo from $($appRepoZipFile)..."
    Invoke-WebRequest $appRepoZipFile -OutFile $appZipfilePath
   
    # Unzip into the applicaton root (appRoot), then rename the repo
    # to actual application name
    Write-Host "`nUnzipping $($appZipfilePath) to $($appRoot)..."
    Expand-Archive $appZipfilePath -DestinationPath $appRoot
    
    $UnZipFolder = (Get-ChildItem -Path  $appRoot -Attributes Directory)[0].Name
    Write-Host "Renaming extracted folder $($UnZipFolder) to $($appRoot)\$($appName)"
    Rename-Item -Path "$($appRoot)\$($UnZipFolder)" -NewName "$($appRoot)\$($appName)"

    # ---- Python Tasks ----
    # Create Python virtual environment
    Write-Host "`nSet up Python Virtual Environment"

    # Get Python executable and check if version meets requirements
    $pythonExePath = Get-PythonExe
    Write-Host "Found Python exe at $($pythonExePath)."
    $userPythonPath = Read-Host "Press <ENTER> to use Python exe, or enter alternative location: "
    if ($userPythonPath.Length -gt 0) {
        if (Test-Path -Path $userPythonPath) {
            $pythonExePath = $userPythonPath
        }
        else {
            Write-Host "***ERR*** Invalid path to Python executable. ABORTING."
            Exit
        }
    }
    if (Get-IsPythonVersionValid $pythonExePath -not) {
        Write-Host "Python version does not meet minimum version requirement of $($pythonMinVersion)"
        Exit
    }

    $pythonVenvFullPath = "$($appRoot)\$($appName)\$($pythonVenvHome)"
    Invoke-Expression "$($pythonExePath) -m venv $($pythonVenvFullPath)"

    # All further work now done in virtual environment
    # Get path to Python executable in virtual environment
    $pythonVenvPythonExe = Get-PythonExe $pythonVenvFullPath

    # Upgrade pip
    Invoke-Expression "$($pythonVenvPythonExe) -m pip install --upgrade pip"

    # Deploy Python packages & other dependencies
    Invoke-Expression "$($pythonVenvPythonExe) -m pip install -r $($appRoot)\$($appName)\requirements.txt"

    # --- Web Server Tasks ---
    # Check OS 
    if ($IsLinux) {
        # TODO: check if Apache is running
        if (Get-Apache().Length -gt 0) {
            Write-Host "Apache web server found running. Will modify for web app deployment."
            # Modify Web Server (Apache)
            

        }
    }
    
    Write-Host "---Done---"
}

# ---- MAIN ----
main $args[0]
