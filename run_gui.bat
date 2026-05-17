@echo off
setlocal
cd /d %~dp0
if not exist gui.py (
    echo Nie znaleziono pliku gui.py w %cd%
    pause
    exit /b 1
)
if exist .venv\Scripts\pythonw.exe (
    set "PYCMD=.venv\Scripts\pythonw.exe"
) else if exist .venv\Scripts\python.exe (
    set "PYCMD=.venv\Scripts\python.exe"
) else (
    set "PYCMD=pythonw"
)
%PYCMD% gui.py
if errorlevel 1 pause
endlocal
