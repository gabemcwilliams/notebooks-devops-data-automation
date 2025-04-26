# -----------------------------------------------------------------------------------------------;
# Title: CSV - Add Column with Date Created to CSV
# Author: Gabe McWilliams
# Purpose: When importing data from CSV the date created is missing causing data to be inaccurate for daily delta
# Date of Creation: 2022/03/07
# Version 1.0
# -----------------------------------------------------------------------------------------------

<#
Script to import DattoRMM device exports, append file creation timestamp as 'data_creation_date',
and export enriched CSVs for downstream ingestion.
#>



# declare counter for rows processed
$row = 0

# declare table object
$table = @()

# assign path varaible
#$origpath = 'D:\full_export'
$origpath = 'D:\reports\source_data'

# assign destination path for csv output - include filename ie. '.csv'
$date = Get-Date -f "_yyyy_MM_dd_hhmmss"

$destpath = "D:\reports\full_export" + $date + ".csv"

# assign report prefix | first part of report file name
$prefix = 'devicedetailsexport*'

# assign data source application name that csv was generated from
$datasourceapp = 'DattoRMM'


$files = Get-ChildItem -Path $origpath -Recurse | Where-Object -Property Name -Like "$.csv"

foreach ($file in $files) {

    $data = Import-Csv -Path $file.FullName

    # create and order object from output to format for csv
    try {
        $data | 
        ForEach-Object {
            $row = $row + 1
            Write-output "processing row: $row"
            $record = [ordered] @{
                'device_hostname'          = $_.'Device Hostname'
                'device_uid'               = $_.'Device UID'
                'site_name'                = $_.'Site Name'
                'site_uid'                 = $_.'Site UID'
                'status'                   = $_.'Status'
                'last_audit'               = ([ScriptBlock] {
                        if ($_.'Last Audit' -eq '') {
                            return '0000-00-00 00:00:00'
                        }
                        else { return $_.'Last Audit Date' | Get-Date -f "yyyy-MM-dd hh:mm:ss" }
                    }).InvokeReturnAsIs()
                'last_seen'                = ([ScriptBlock] {
                        if ($_.'Last Seen' -eq '') {
                            return '0000-00-00 00:00:00'
                        }
                        else { return $_.'Last Seen' | Get-Date -f "yyyy-MM-dd hh:mm:ss" }
                    }).InvokeReturnAsIs()
                'operating_system'         = $_.'Operating System'
                'device_type'              = $_.'Device Type'
                'patches_approved_pending' = $_.'Patches Approved Pending'
                'patches_not_approved'     = $_.'Patches Not Approved'
                'patches_installed'        = $_.'Patches Installed'
                'patch_status'             = $_.'Patch Status'
                'device_domain'            = $_.'Domain'
                'last_reboot'              = ([ScriptBlock] {
                        if ($_.'Last Reboot' -eq '') {
                            return '0000-00-00 00:00:00'
                        }
                        else { return $_.'Last Reboot' | Get-Date -f "yyyy-MM-dd hh:mm:ss" }
                    }).InvokeReturnAsIs()
                'reboot_required_state'    = $_.'Reboot required'
                'data_creation_date'       = ([ScriptBlock] {
                        Get-Item -Path $file.FullName | Select-Object -Property CreationTime | ForEach-Object { $_.CreationTime } | Get-Date -f "yyyy-MM-dd hh:mm:ss"
                    }).InvokeReturnAsIs()
                'data_origin_sourceapp'    = $datasourceapp
                'data_origin_sourcefile'   = ([ScriptBlock] {
                        Get-Item -Path $file.FullName | Select-Object -Property Name | ForEach-Object { $_.Name } 
                    }).InvokeReturnAsIs()
            } 
    
            # append object $table with each record $newobj
            $newobj = New-Object psobject -Property $record
            $table += $newobj } -ErrorAction stop -ErrorVariable 'err'
        # end of Get-ChildItem statement^^

    }
    # end of try statement ^^

    catch {
        Throw 'Unable to complete.  Exiting Script!'
        Write-Output $err
        Exit 1    
    }

}
# "####################### Table Output #######################""`n"
$table | Export-Csv $destpath -NoTypeInformation
