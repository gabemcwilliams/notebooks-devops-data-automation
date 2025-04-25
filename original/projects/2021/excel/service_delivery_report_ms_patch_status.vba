' # -----------------------------------------------------------------------------------------------
' # Title: Excel VBA Macro - Daily Service Delivery Report - MS Patching Status (DattoRMM)
' # Author: Gabe McWilliams
' # Purpose: Attempt to automate the steps taken for morning reports
' # Date of Creation: 2022/03/08
' # Version 1.0
' # -----------------------------------------------------------------------------------------------



Sub ms_patch_status()
'
' ms_patch_status Macro
'

'
    Dim Pt As PivotTable
    Dim sh As Worksheet

    For Each sh In Sheets
        For Each Pt In sh.PivotTables
            Pt.TableRange2.Clear
        Next Pt
    Next sh
    
    Cells.Select
    ActiveSheet.Name = "source_data"
    Sheets.Add(After:=Sheets("source_data")).Name = "pivot_table"
    
        
        
    ActiveWorkbook.PivotCaches.Create(SourceType:=xlDatabase, SourceData:= _
    "source_data!R1C1:R110000C17", Version:=7).CreatePivotTable TableDestination _
    :="pivot_table!R3C1", TableName:="PivotTable", DefaultVersion:=7
   
        
        
    Sheets("pivot_table").Select
    Cells(3, 1).Select
    With ActiveSheet.PivotTables("PivotTable")
        .ColumnGrand = True
        .HasAutoFormat = True
        .DisplayErrorString = False
        .DisplayNullString = True
        .EnableDrilldown = True
        .ErrorString = ""
        .MergeLabels = False
        .NullString = ""
        .PageFieldOrder = 2
        .PageFieldWrapCount = 0
        .PreserveFormatting = True
        .RowGrand = True
        .SaveData = True
        .PrintTitles = False
        .RepeatItemsOnEachPrintedPage = True
        .TotalsAnnotation = False
        .CompactRowIndent = 1
        .InGridDropZones = False
        .DisplayFieldCaptions = True
        .DisplayMemberPropertyTooltips = False
        .DisplayContextTooltips = True
        .ShowDrillIndicators = True
        .PrintDrillIndicators = False
        .AllowMultipleFilters = False
        .SortUsingCustomLists = True
        .FieldListSortAscending = False
        .ShowValuesRow = False
        .CalculatedMembersInFilters = False
        .RowAxisLayout xlCompactRow
    End With
    With ActiveSheet.PivotTables("PivotTable").PivotCache
        .RefreshOnFileOpen = False
        .MissingItemsLimit = xlMissingItemsDefault
    End With
    ActiveSheet.PivotTables("PivotTable").RepeatAllLabels xlRepeatLabels
    ActiveSheet.Shapes.AddChart2(201, xlColumnClustered).Select
    ActiveChart.SetSourceData Source:=Range("pivot_table!$A$3:$C$20")
    With ActiveChart.PivotLayout.PivotTable.PivotFields("Last Seen")
        .Orientation = xlRowField
        .Position = 1
    End With
    ActiveChart.PivotLayout.PivotTable.PivotFields("Last Seen").AutoGroup
    With ActiveChart.PivotLayout.PivotTable.PivotFields("Patch Status")
        .Orientation = xlRowField
        .Position = 4
    End With
    With ActiveChart.PivotLayout.PivotTable.PivotFields("Last Reboot")
        .Orientation = xlRowField
        .Position = 5
    End With
    ActiveChart.PivotLayout.PivotTable.PivotFields("Last Reboot").AutoGroup
    With ActiveChart.PivotLayout.PivotTable.PivotFields("Reboot required")
        .Orientation = xlRowField
        .Position = 8
    End With
    With ActiveChart.PivotLayout.PivotTable.PivotFields("Device Hostname")
        .Orientation = xlRowField
        .Position = 9
    End With
    With ActiveChart.PivotLayout.PivotTable.PivotFields("Device Hostname")
        .Orientation = xlColumnField
        .Position = 1
    End With
    ActiveChart.PivotLayout.PivotTable.PivotFields("Device Hostname").Orientation _
        = xlHidden
    With ActiveChart.PivotLayout.PivotTable.PivotFields("Site Name")
        .Orientation = xlRowField
        .Position = 9
    End With
    With ActiveChart.PivotLayout.PivotTable.PivotFields("Site Name")
        .Orientation = xlColumnField
        .Position = 1
    End With
    ActiveChart.PivotLayout.PivotTable.AddDataField ActiveChart.PivotLayout. _
        PivotTable.PivotFields("Reboot required"), "Count of Reboot required", xlCount
    ActiveChart.PivotLayout.PivotTable.AddDataField ActiveChart.PivotLayout. _
        PivotTable.PivotFields("Patch Status"), "Count of Patch Status", xlCount
    ActiveSheet.Shapes("Chart 1").ScaleWidth 1.0462633452, msoFalse, _
        msoScaleFromTopLeft
    ActiveSheet.Shapes("Chart 1").ScaleHeight 2.7899307378, msoFalse, _
        msoScaleFromTopLeft
    Sheets("pivot_table").Select
End Sub
