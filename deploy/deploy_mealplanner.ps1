<#
    Name        : deploy_mealplanner.ps1
    Description : Script to deploy Meal Planner web application
    Date        : 23-Jan-2024
    Author      : M. Schmidt

    Usage:

    install_mp.ps1 <config_file>
#>

# Global Settings

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
            Set-Variable -Name $variableName -Value $variableValue -Scope Global
        }

    }
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

    # Create Python virtual environment
    Write-Host "`nSet up Python Virtual Environment"
    $pythonVenvFullPath = "$($appRoot)\$($appName)\$($pythonVenvHome)"
    Invoke-Expression "$($pythonHome)\python.exe -m venv $($pythonVenvFullPath)"

    # Upgrade pip
    Invoke-Expression "$($pythonVenvFullPath)\Scripts\python.exe -m pip install --upgrade pip"

    # Deploy Python packages & other dependencies
    Invoke-Expression "$($appRoot)\$($appName)\$($pythonVenvHome)\Scripts\python.exe -m pip install -r $($appRoot)\$($appName)\requirements.txt"

    # Check OS 
    if ($IsLinux) {
        # TODO: check if Apache is running
        
    }

    # Modify Web Server (Apache)
    
    # Make changes to 000-default.conf
    # Locate any existing WSGI settings
    # ScriptAlias; Alias [media, static]
    # DaemonProcess; ProcessGroup
    
    Write-Host "---Done---"
}

# MAIN
main $args[0]
