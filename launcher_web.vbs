' launcher_web.vbs - Автозапуск дашборда через планировщик
Dim shell
Set shell = CreateObject("WScript.Shell")

' Получаем путь к директории скрипта
script_dir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Запуск команды tracker web в фоновом режиме
shell.Run "python " & script_dir & "\project_manager.py web --daemon", 0, False

' Небольшая пауза перед открытием браузера
WScript.Sleep 3000

' Открытие веб-дашборда в браузере
shell.Run "http://localhost:8080", 1, False

Set shell = Nothing

WScript.Echo "Simple Time Tracker Web Dashboard run http://localhost:8080"