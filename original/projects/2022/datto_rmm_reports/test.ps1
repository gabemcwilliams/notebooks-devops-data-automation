# -----------------------------------------------------------------------------------------------
# Component: Sophos AV Status - WinOS
# Modified by: Gabe McWilliams
# Purpose: Monitor that Sophos Antivirus is Installed
# Version 1.0
# -----------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------
# Component: Sophos Central Monitor
# Original Author: Stephen Weber
# Purpose: Installation Monitor for Sophos Central Endpoints
# Version 1.1
# -----------------------------------------------------------------------------------------------

#Define Functions

function SophosInstalled {

    $Global:installed = (gp HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*).DisplayName -contains "Sophos Endpoint Agent"
    $Global:mcsclient = Get-Service -name "Sophos MCS Client" -ea SilentlyContinue

    }

    function SophosAlert
    {
    param([string]$alert)
    Write-Host "<-Start Result->"
    Write-Host "Sophos Central Status="$alert
    Write-Host "<-End Result->"

    # add log text for install failure
    $path = 'C:\ProgramData\Sophos\CloudInstaller\Logs\SophosCloudInstaller*.log'
    $text = @(Get-Content -Path $path | Where-Object { ($_ -like '*ERROR : Exception: Setup program failed with code: 1*') -or ($_ -like '*FAILED*') })
    Write-Host "<-Start Diagnostic->"
    foreach($line in $text){
    Write-Host $line    }
    Write-Host "<-End Diagnostic->"


    exit 1
    }

    function SophosStatus
    {
    param([string]$status)
    Write-Host "<-Start Result->"
    Write-Host "Sophos Central Status="$status
    Write-Host "<-End Result->"
    Write-output '{"product":"Sophos Central Endpoint","running":true,"upToDate":true}' > $[REDACTED]/.json
    exit 0
    }

    Function EndpointMonitors
    {
    SophosInstalled
    if ((!$installed -eq "True") -and (!$mcsclient.Status -eq "Running")) {
        SophosAlert "Not Installed"


        }
    }

    try
    {
        EndpointMonitors
    }
    catch
    {
        SophosAlert $_.Exception.Message
    }
    finally
    {
    if ($installed -eq "True") {
        SophosStatus "Protected"
        }
    }