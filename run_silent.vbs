Dim shell
Set shell = CreateObject("WScript.Shell")
shell.Run "python ""C:\Projects\Bash\0604_simple-tracker\tracker_quick.py""", 0, True
Set shell = Nothing