'---------------------------------------------------------------------------------------
'[REDACTED]/.csv conditioning 
' Author: Dale Havens
' Based on sub_splitdatabycol.vbs by Gabe McWilliams
'[REDACTED]/.csv receieved from Datto report
' Date of Creation: 2021/12/08
' Version: 1.0
'---------------------------------------------------------------------------------------

Sub DataConditioning() 
'updateby Extendoffice 
Dim lr As Long 
Dim ws As Worksheet 
Dim vcol, i As Integer 
Dim icol As Long 
Dim myarr As Variant 
Dim title As String 
Dim titlerow As Integer 
Dim xTRg As Range 
Dim xVRg As Range 
Dim xWSTRg As Worksheet 
On Error Resume Next 
Set xTRg = Application.InputBox("Please select the header rows:", "Kutools for Excel", "", Type:=8) 
If TypeName(xTRg) = "Nothing" Then Exit Sub 
Set xVRg = Application.InputBox("Please select the column you want to split data based on:", "Kutools for Excel", "", Type:=8) 
If TypeName(xVRg) = "Nothing" Then Exit Sub 
vcol = xVRg.Column 
Set ws = xTRg.Worksheet 
lr = ws.Cells(ws.Rows.Count, vcol).End(xlUp).Row 
title = xTRg.AddressLocal 
titlerow = xTRg.Cells(1).Row 
icol = ws.Columns.Count 
ws.Cells(1, icol) = "Unique" 
Application.DisplayAlerts = False 
If Not Evaluate("=ISREF('xTRgWs_Sheet!A1')") Then 
Sheets.Add(after:=Worksheets(Worksheets.Count)).Name = "xTRgWs_Sheet" 
Else 
Sheets("xTRgWs_Sheet").Delete 
Sheets.Add(after:=Worksheets(Worksheets.Count)).Name = "xTRgWs_Sheet" 
End If 
Set xWSTRg = Sheets("xTRgWs_Sheet") 
xTRg.Copy 
xWSTRg.Paste Destination:=xWSTRg.Range("A1") 
ws.Activate 
For i = (titlerow + xTRg.Rows.Count) To lr 
On Error Resume Next 
If ws.Cells(i, vcol) <> "" And Application.WorksheetFunction.Match(ws.Cells(i, vcol), ws.Columns(icol), 0) = 0 Then 
ws.Cells(ws.Rows.Count, icol).End(xlUp).Offset(1) = ws.Cells(i, vcol) 
End If 
Next 
myarr = Application.WorksheetFunction.Transpose(ws.Columns(icol).SpecialCells(xlCellTypeConstants)) 
ws.Columns(icol).Clear 
For i = 2 To UBound(myarr) 
ws.Range(title).AutoFilter field:=vcol, Criteria1:=myarr(i) & "" 
If Not Evaluate("=ISREF('" & myarr(i) & "'!A1)") Then 
Sheets.Add(after:=Worksheets(Worksheets.Count)).Name = myarr(i) & "" 
Else 
Sheets(myarr(i) & "").Move after:=Worksheets(Worksheets.Count) 
End If 
xWSTRg.Range(title).Copy 
Sheets(myarr(i) & "").Paste Destination:=Sheets(myarr(i) & "").Range("A1") 
ws.Range("A" & (titlerow + xTRg.Rows.Count) & ":A" & lr).EntireRow.Copy Sheets(myarr(i) & "").Range("A" & (titlerow + xTRg.Rows.Count)) 
Sheets(myarr(i) & "").Columns.AutoFit 
Next 
xWSTRg.Delete 
ws.AutoFilterMode = False 
ws.Activate 
Application.DisplayAlerts = True 
Rows("1:1").Select
    Selection.AutoFilter
    Range("A1").Select
    Sheets.Add
    ActiveWorkbook.PivotCaches.Create(SourceType:=xlDatabase, SourceData:= _
        "PatchingAllSitesReport-12-08-20!R1C1:R3316C7", Version:=7).CreatePivotTable _
        TableDestination:="Sheet26!R1C1", TableName:="PivotTable1", DefaultVersion _
        :=7
    Sheets("Sheet26").Select
    Cells(1, 1).Select
    With ActiveSheet.PivotTables("PivotTable1")
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
    With ActiveSheet.PivotTables("PivotTable1").PivotCache
        .RefreshOnFileOpen = False
        .MissingItemsLimit = xlMissingItemsDefault
    End With
    ActiveSheet.PivotTables("PivotTable1").RepeatAllLabels xlRepeatLabels
    ActiveSheet.Shapes.AddChart2(201, xlColumnClustered).Select
    ActiveChart.SetSourceData Source:=Range("Sheet26!$A$1:$C$18")
    ActiveSheet.Shapes("Chart 1").IncrementLeft 192
    ActiveSheet.Shapes("Chart 1").IncrementTop 15
    With ActiveChart.PivotLayout.PivotTable.PivotFields("Site Name")
        .Orientation = xlPageField
        .Position = 1
    End With
    ActiveChart.PivotLayout.PivotTable.AddDataField ActiveChart.PivotLayout. _
        PivotTable.PivotFields("Patch Status"), "Count of Patch Status", xlCount
    With ActiveChart.PivotLayout.PivotTable.PivotFields("Patch Status")
        .Orientation = xlRowField
        .Position = 1
    End With
    ActiveChart.ClearToMatchStyle
    ActiveChart.ChartStyle = 209
    ActiveChart.FullSeriesCollection(1).Select
    ActiveChart.FullSeriesCollection(1).Points(2).Select
    With Selection.Format.Fill
        .Visible = msoTrue
        .ForeColor.RGB = RGB(0, 176, 80)
        .Transparency = 0
        .Solid
    End With
    ActiveChart.FullSeriesCollection(1).Points(1).Select
    With Selection.Format.Fill
        .Visible = msoTrue
        .ForeColor.RGB = RGB(146, 208, 80)
        .Transparency = 0
        .Solid
    End With
    ActiveChart.Axes(xlCategory).Select
    ActiveChart.FullSeriesCollection(1).Select
    ActiveChart.FullSeriesCollection(1).Points(6).Select
    With Selection.Format.Fill
        .Visible = msoTrue
        .ForeColor.RGB = RGB(255, 255, 0)
        .Transparency = 0
        .Solid
    End With
    ActiveChart.Axes(xlCategory).Select
    ActiveChart.PlotArea.Select
    ActiveChart.Axes(xlCategory).Select
    ActiveChart.FullSeriesCollection(1).Select
    ActiveChart.FullSeriesCollection(1).Points(3).Select
    With Selection.Format.Fill
        .Visible = msoTrue
        .ForeColor.RGB = RGB(255, 192, 0)
        .Transparency = 0
        .Solid
    End With
    ActiveChart.Axes(xlCategory).Select
    ActiveChart.PlotArea.Select
    ActiveChart.Axes(xlCategory).Select
    ActiveChart.PlotArea.Select
    ActiveWindow.SmallScroll Down:=-3
    ActiveChart.Axes(xlCategory).Select
    ActiveChart.ChartArea.Select
    ActiveSheet.Shapes("Chart 1").ScaleWidth 1.3608509418, msoFalse, _
        msoScaleFromTopLeft
    ActiveSheet.Shapes("Chart 1").ScaleHeight 1.5157006416, msoFalse, _
        msoScaleFromTopLeft
    ActiveChart.FullSeriesCollection(1).Select
    ActiveChart.FullSeriesCollection(1).Points(4).Select
    With Selection.Format.Fill
        .Visible = msoTrue
        .ForeColor.RGB = RGB(255, 0, 0)
        .Transparency = 0
        .Solid
    End With
    ActiveChart.FullSeriesCollection(1).Points(5).Select
    With Selection.Format.Fill
        .Visible = msoTrue
        .ForeColor.RGB = RGB(192, 0, 0)
        .Transparency = 0
        .Solid
    End With
    ActiveChart.Axes(xlValue).MajorGridlines.Select
    ActiveChart.ChartArea.Select
    ActiveChart.FullSeriesCollection(1).Select
    ActiveChart.FullSeriesCollection(1).ApplyDataLabels
End Sub 