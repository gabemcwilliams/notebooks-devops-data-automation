# -----------------------------------------------------------------------------------------------
# Component: Scheduled Task - Run as Trusted Installer
# Author: Gabe McWilliams
# Purpose: Attempt to fix broken filestructure for Windows systems run as Trusted Installer
# Date of Creation: 2021/11/29
# Version 1.0
# -----------------------------------------------------------------------------------------------

$envloc = "D:\git\example_infrastructure_data_dev\config\env.ini"
$localstore = "D:\config\env.ini"



$taskame = "Data Science - Copy Environment Variables"

$description = "Copy Env.ini to local from git folder"

$action = New-ScheduledTaskAction -Execute "Powershell" -Argument "Copy-Item -Path $envloc -Destination $localstore -Force"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)

$principal = New-ScheduledTaskPrincipal -UserId 'NT AUTHORITY\SYSTEM' -RunLevel Highest

Register-ScheduledTask -TaskName $taskame -Description $description -Action $action -Trigger $trigger -Principal $principal

