<#
    Name        : deploy_mealplanner.ps1
    Description : Script to deploy Meal Planner web application
    Date        : 23-Jan-2024
    Author      : M. Schmidt

    Usage:

    install_mp.ps1 <config_file>
#>

# Script Parameters
# configFile -- full path to configuration json file defining deployment
param (
    [Parameter(Mandatory=$true)]
    [string]$ConfigFile
)

# Script Variables
$Script:DefaultApacheConfFile="/etc/apache2/sites-available/000-default.conf"
$Script:DEBUG = $true


function Get-Config {
    <#
    Read configuration file and create variables to hold settings

    THIS FUNCTION IS DEPRECATED
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

            # if value has a comma, create a hashtable
            if ($variableValue.contains(",")) {
                $hkey = $variableValue.split(",")[0]
                $hvalue = $variableValue.split(",")[1]
                Write-Host "Setting Hashtable variable $($variableName) to key: $($hkey) = $($hvalue)"
                Set-Variable -Name $variableName -Value @{$hkey=$hvalue} -Scope Script
            }
            else {
                Write-Host "Setting variable $($variableName) = '$($variableValue)'"
                Set-Variable -Name $variableName -Value $variableValue -Scope Script
            }
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
    if ($IsLinux) {
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

    $pyFullVersion = (Invoke-Expression "$($pythonPath) --version").Split()[1]
    Write-Host "Version of Python is $($pyFullVersion)"
    $pyVersion = $pyFullVersion.Split(".")

    $pyMinVersion = $config.settings.python.minVersion.Split(".")

    # Check major, minor and release
    $valid = [int]$pyVersion[0] -ge [int]$pyMinVersion[0] -and [int]$pyVersion[1] -ge [int]$pyMinVersion[1] -and [int]$pyVersion[2] -ge [int]$pyMinVersion[2]

    return $valid
}


function Get-Apache {
    <#
    Check if Apache is running on deployment server.
    Return location of installation.
    #>
    $apachePath = (get-process -Name apache2 -ErrorAction:Ignore | Select-Object CommandLine -first 1 | ForEach-Object {$_.CommandLine}[0])

    if ($null -eq $apachePath -and $DEBUG) {
        $apachePath = $env:TEMP  # Use a valid, but harmless folder for testing
    }
    return $apachePath
}


function Set-Apache {
    <#
        Update conifguration for Apache Web Server
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
    $backupFile = "$($apacheConfFile).$(Get-Date -Format yyyyMMddHHss).bak"
    Write-Host "Backing up Apache conf file to $($backupFile)..."
    Copy-Item $apacheConfFile $backupFile -Force

    # If backup failed, abort
    if ((Test-Path -Path $backupFile) -eq $false) {
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
        Downloads source code from GitHub
    #>
    param (
        [string]$githubURL,
        [string]$outFile
    )

    Write-Output "Enter credentials for URL $($githubURL)"
    $credentials = Get-Credential
    
    Write-Host ="`nDownloading Meal Planner repo from $($config.settings.appRepoZipfile)..."    
    Invoke-WebRequest $githubURL -Credential $credentials -Outfile $outFile

}


function Deploy-Code {
    <#
        Unzip a file to specified location
    #>
    param (
        [string]$zipfilePath,
        [string]$appRoot,
        [string]$appName
    )

    # Unzip into the applicaton root (appRoot), then rename the repo
    # to actual application name
    Write-Host "`nUnzipping $($zipfilePath) to $($appRoot)..."
    Expand-Archive $zipfilePath -DestinationPath $appRoot
    
    $UnZipFolder = (Get-ChildItem -Path $appRoot -Attributes Directory)[0].Name
    $unzipFolderPath = Join-Path -Path $appRoot -ChildPath $UnZipFolder
    $appFolderPath = Join-Path -Path $appRoot -ChildPath $appName
    Write-Host "Renaming extracted folder $($UnZipFolder) to $($appFolderPath)"
    Rename-Item -Path "$($unzipFolderPath)" -NewName "$($appFolderPath)"

}


function main {
    <#
        Main Function
    #>

    param (
        [Parameter(Mandatory=$true)]
        [string]$ConfigFile
    )

    # Validate arguments
    if ($ConfigFile.Length -eq 0) {
        Write-Host "Config file not specified"
        Exit 1
    }

    # Read in configuration file
    $Script:config = Get-Content -Raw $ConfigFile | ConvertFrom-Json

    # Download and upack zipped source code from repo
    $appZipfile = Split-Path -Path $config.settings.appRepoZipfile -Leaf
    $appZipfilePath = "$($env:TEMP)\$($appZipfile)"
    
    Get-SourceCode $config.settings.appRepoZipfile $appZipfilePath
   
    # Unzip into the applicaton root (appRoot), then rename the repo
    # to actual application name
    
    Deploy-Code $appZipfilePath $config.settings.appRoot $config.settings.appName

    # ---- Python Tasks ----
    # Create Python virtual environment
    Write-Host "`nSet up Python Virtual Environment"

    # Get Python executable and check if version meets requirements
    $pythonExePath = Get-PythonExe
    Write-Host "Found Python exe at $($pythonExePath)."
    $userPythonPath = Read-Host "Press <ENTER> to use Python exe, or enter alternative location"
    if ($userPythonPath.Length -gt 0) {
        if (Test-Path -Path $userPythonPath) {
            $pythonExePath = $userPythonPath
        }
        else {
            Write-Host "***ERR*** Invalid path to Python executable. ABORTING."
            Exit
        }
    }
    $isValid = Get-IsPythonVersionValid $pythonExePath
    if ($isValid -ne $true) {
        Write-Host "Python version does not meet minimum version requirement of $($config.settings.python.minVersion)"
        Exit
    }

    $pythonVenvFullPath = "$($config.settings.appRoot)\$($config.settings.appName)\$($config.settings.python.venvHome)"
    Invoke-Expression "$($pythonExePath) -m venv $($pythonVenvFullPath)"

    # All further work now done in virtual environment
    # Get path to Python executable in virtual environment
    $pythonVenvPythonExe = Get-PythonExe $pythonVenvFullPath

    # Upgrade pip
    Invoke-Expression "$($pythonVenvPythonExe) -m pip install --upgrade pip"

    # Deploy Python packages & other dependencies
    Invoke-Expression "$($pythonVenvPythonExe) -m pip install -r $($config.settings.appRoot)\$($config.settings.appName)\requirements.txt"

    # --- Web Server Tasks ---
    # Check OS 
    if ($IsLinux -or $DEBUG) {
        # TODO: check if Apache is running
        $apachePath = Get-Apache
        if ($apachePath.Length -gt 0) {
            Write-Host "Apache web server found running. Will modify for web app deployment."
            # Modify Web Server (Apache)
            Set-Apache

        }
    }
    
    Write-Host "---Done---"
}

# ---- MAIN ----
main $ConfigFile
