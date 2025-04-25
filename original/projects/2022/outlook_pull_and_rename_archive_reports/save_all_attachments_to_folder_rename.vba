Public Sub SaveAttachsToDisk()
'UpdatebyExtendoffice20180521
Dim xItem As Object  'Outlook.MailItem
Dim xSelection As Selection
Dim xAttachment As Outlook.Attachment
Dim xFldObj As Object
Dim xSaveFolder As String
Dim xFSO As Scripting.FileSystemObject
Dim xFile As File
Dim xFilePath As String
Dim xNewName, xTmpName As String
Dim xExt As String
Dim xCount As Integer
On Error Resume Next
Set xFldObj = CreateObject("Shell.Application").browseforfolder(0, "Select a Folder", 0, 16)
Set xFSO = New Scripting.FileSystemObject
If xFldObj Is Nothing Then Exit Sub
xSaveFolder = xFldObj.Items.Item.Path & "\"
Set xSelection = Outlook.Application.ActiveExplorer.Selection
xNewName = InputBox("Attachment Name:", "Kutools for Outlook", xNewName)
If Len(Trim(xNewName)) = 0 Then Exit Sub
For Each xItem In xSelection
    For Each xAttachment In xItem.Attachments
        xFilePath = xSaveFolder & xAttachment.FileName
        xAttachment.SaveAsFile xFilePath
        Set xFile = xFSO.GetFile(xFilePath)
        xCount = 1
        Saved = False
        xExt = "." & xFSO.GetExtensionName(xFilePath)
        xTmpName = xNewName
        xNewName = xTmpName & xExt
        If xFSO.FileExists(xSaveFolder & xNewName) = False Then
            xFile.Name = xNewName
            xNewName = xTmpName
        Else
            xTmpName = Left(xNewName, Len(xNewName) - Len(xExt))
            While Saved = False
                xNewName = xTmpName & xCount & xExt
                If xFSO.FileExists(xSaveFolder & xNewName) = False Then
                    xFile.Name = xNewName
                    xNewName = xTmpName
                    Saved = True
                Else
                    xCount = xCount + 1
                End If
            Wend
        End If
    Next
Next
Set xFSO = Nothing
End Sub



'=========================================


' Rename and save attachments with same name in a folder

' 1. Select the message which you want to save its attachments and rename to the same name.

' 2. Press Alt + F11 keys, then in the Project1 pane, double click ThisOutlookSession to create a new blank script in right section, then copy and paste the code to it.

' 3. Click Tools > References, in the popping dialog, check Microsoft Script Runtime checkbox.
' doc rename save attachments in a folder 3 	doc arrow right 	doc rename save attachments in a folder 4

' 4. Click OK, press F5 key to run the code, a Browse For Folder dialog pops out for selecting or creating a folder to place attachments.
' doc rename save attachments in a folder 5

' 5. Click OK, then give a name for the attachments.
' doc rename save attachments in a folder 6

' 6. Click OK, now the attachments are renamed with same name, if there are duplicates, the duplicate ones will be added numbers as the suffix.

' Original URL: https://www.extendoffice.com/documents/outlook/5265-outlook-rename-and-save-attachments.html