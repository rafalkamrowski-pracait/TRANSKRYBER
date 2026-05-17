Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)

pywPath = scriptPath & "\\.venv\\Scripts\\pythonw.exe"
pyPath = scriptPath & "\\.venv\\Scripts\\python.exe"

guiPath = scriptPath & "\\gui.py"

If fso.FileExists(pywPath) Then
    cmd = Chr(34) & pywPath & Chr(34) & " " & Chr(34) & guiPath & Chr(34)
ElseIf fso.FileExists(pyPath) Then
    cmd = Chr(34) & pyPath & Chr(34) & " " & Chr(34) & guiPath & Chr(34)
Else
    cmd = "pythonw " & Chr(34) & guiPath & Chr(34)
End If

shell.Run cmd, 0, False
