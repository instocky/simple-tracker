@echo off
echo Остановка старого процесса...

:: Ищем и убиваем процесс python, который запускает project_manager.py
wmic process where "name='python.exe' and commandline like '%%project_manager.py%%'" call terminate

echo Пауза для освобождения порта...
timeout /t 2 /nobreak >nul

echo Запуск новой версии...
:: Запускаем ваш VBS скрипт
start "" "launcher_web.vbs"

echo Готово!