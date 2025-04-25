# -----------------------------------------------------------------------------------------------
# Title: CSV - Add Column with Date Created and Patch Policy to DattoRMM Generated CSV
# Author: Gabe McWilliams
# Purpose: When importing data from CSV the date created is missing causing data to be inaccurate for daily delta 
# Date of Creation: 2022/03/07
# Version 1.1
# -----------------------------------------------------------------------------------------------

# if patch policy variable is $true, then add patch policy coloumn
$patchpolicy = $true

# declare counter for rows processed
$row = 0

# declare table objects
$table = @()
$policytable = @()
$joined_table = @()

# assign path varaible
#$origpath = 'D:\full_export'
$origpath = 'D:\reports\source_data'

# assign destination path for csv output - include filename ie. '[REDACTED]/.csv'
$date = Get-Date -f "_yyyy_MM_dd_hhmmss"

$destpath = "D:\reports\full_export" + $date + "[REDACTED]/.csv"

# assign device export report prefix | first part of report file name
$prefix = 'devicedetailsexport*'

# assign manage policy report prefix
$manage_prefix = 'example-System*'

# assign data source application name that csv was generated from

$datasourceapp = 'DattoRMM'



$files = Get-ChildItem -Path $origpath -Recurse | Where-Object -Property Name -Like "$[REDACTED]/.csv" 

$policyfile = Get-ChildItem -Path $origpath | Where-Object -Property name -like $manage_prefix


# create policy object from csv

if ($patchpolicy) {

$manage_data = import-csv -path $policyfile.fullname


# create and order object from output to format for csv

    $policy_data = $manage_data | Select-Object -Property @{name='device_uid';expression={$_.'device uid'}},@{name='patch_policy';expression={$_.'policy'}}
            #@{name='data_creation_date';expression={Get-Item -Path $file.FullName | Select-Object -Property CreationTime | ForEach-Object {$_.CreationTime} | Get-Date -f "yyyy-MM-dd hh:mm:ss"}, 
           # @{name='data_origin_sourceapp';expression=$datasourceapp}, 
            #@{name='data_origin_source_file';expression={Get-Item -Path $file.FullName | Select-Object -Property Name | ForEach-Object {$_.Name}}}
    
    #} -ErrorAction stop 
 
}



# create original object from device export


#foreach($file in $files){

$data = Import-Csv -Path $file.FullName

# data | Select-Object -Property * 


foreach($file in $files){


# create and order object from output to format for csv

    $data | select-object -property '*',@{name='patch_policy';Expression={$device_uid = $_.'Device UID'; (@($policy_data).where({$_.device_uid -eq $device_uid})).patch_policy}} | 

    ForEach-Object{
    
    $row = $row + 1
    Write-output "processing device row: $row"
    $record = [ordered] @{
        'device_hostname' = $_.'Device Hostname'
        'device_uid' = $_.'Device UID'
        'site_name' = $_.'Site Name'
        'site_uid' = $_.'Site UID'
        'status' = $_.'Status'
        'last_audit' = ([ScriptBlock]{
         if ($_.'Last Audit' -eq ''){
            return '0000-00-00 00:00:00'}
         else{ return $_.'Last Audit Date'| Get-Date -f "yyyy-MM-dd hh:mm:ss" }
            }).InvokeReturnAsIs()
        'last_seen' = ([ScriptBlock]{
         if ($_.'Last Seen' -eq ''){
            return '0000-00-00 00:00:00'}
         else{ return $_.'Last Seen'| Get-Date -f "yyyy-MM-dd hh:mm:ss" }
            }).InvokeReturnAsIs()
        'operating_system' = $_.'Operating System'
        'patch_policy' = $_.patch_policy
        'device_groups' = $_.Group
        'device_type' = $_.'Device Type'
        'domain' = $_.'Domain'
        'patches_approved_pending' = $_.'Patches Approved Pending'
        'patches_not_approved' = $_.'Patches Not Approved'
        'patches_installed' = $_.'Patches Installed'
        'patch_status' = $_.'Patch Status'
        'device_domain' = $_.'Domain'
        'last_reboot' = ([ScriptBlock]{
         if ($_.'Last Reboot' -eq ''){
            return '0000-00-00 00:00:00'}
         else{ return $_.'Last Reboot'| Get-Date -f "yyyy-MM-dd hh:mm:ss" }
            }).InvokeReturnAsIs()
        'reboot_required_state' = $_.'Reboot required'
        'data_creation_date' = ([ScriptBlock]{
         Get-Item -Path $file.FullName | Select-Object -Property CreationTime | ForEach-Object {$_.CreationTime} | Get-Date -f "yyyy-MM-dd hh:mm:ss"
        }).InvokeReturnAsIs()
        'data_origin_sourceapp' = $datasourceapp
        'data_origin_sourcefile' = ([ScriptBlock]{
         Get-Item -Path $file.FullName | Select-Object -Property Name | ForEach-Object {$_.Name} 
        }).InvokeReturnAsIs()
    } 
    


# append object $table with each record $newobj
$newobj = New-Object psobject -Property $record
$table += $newobj }
}

# check for policy doc then run if $true


# "####################### Table Output #######################""`n"


$table | Export-Csv $destpath -NoTypeInformation

