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

    # Copy and upack zipped source code
    # Unzip into temp location, then move contents of folder within
    # temp location to actual location and clean up
    Write-Host "`nUnzipping $($appZipfile)..."
    $TempExtract = "$($env:TEMP)\_temp$($appName)"
    Expand-Archive $appZipfile -DestinationPath $TempExtract
    Read-Host -Prompt "Press any key"
    $UnZipFolder = (Get-ChildItem -Path $env:TEMP -Attributes Directory)[0].Name
    Write-Host "Moving from temp folder to $($appRoot)\$($appName)"
    Move-Item -Path "$($UnZipFolder)\*" -Destination "$($appRoot)\$($appName)\"
    Remove-Item -Path $TempExtract -Recurse
    Read-Host -Prompt "Press any key"

    # Create Python virtual environment
    Write-Host "`nSet up Python Virtual Environment"
    $pythonVenvFullPath = "$($appRoot)\$($appName)\$($pythonVenvHome)"
    Invoke-Expression "$($pythonHome)\python.exe -m venv $($pythonVenvFullPath)"

    # Upgrade pip
    Invoke-Expression "$($pythonVenvFullPath)\Scripts\python.exe -m pip install --upgrade pip"

    # Deploy Python packages & other dependencies
    Invoke-Expression "$($appRoot)\$($appName)\$($pythonVenvHome)\Scripts\python.exe -m pip install -r $($appRoot)\$($appName)\requirements.txt"

    # Modify Web Server (Apache)
    
    # Make changes to 000-default.conf
    # Locate any existing WSGI settings
    # ScriptAlias; Alias [media, static]
    # DaemonProcess; ProcessGroup
    
    Write-Host "---Done---"
}

# MAIN
main $args[0]
