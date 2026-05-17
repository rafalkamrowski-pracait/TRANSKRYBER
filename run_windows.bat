@echo off
chcp 65001 >nul

if "%~1" == "" (
    echo Blad: Nie podano URL ani sciezki do pliku!
    echo Uzycie: .\run_windows.bat [URL_LUB_PLIK] [NAZWA_WYJSCIOWA] [FORMAT] [MODEL]
    exit /b 1
)

set "SOURCE=%~1"
set "OUTPUT=transkrypcja"
set "FORMAT=txt"
set "MODEL=small"

if not "%~2" == "" set "OUTPUT=%~2"
if not "%~3" == "" set "FORMAT=%~3"
if not "%~4" == "" set "MODEL=%~4"

echo %SOURCE% | findstr /I "http:// https://" >nul
if %errorlevel% equ 0 (
    set "PARAM=--url"
) else (
    set "PARAM=--file"
)

call .\venv\Scripts\activate
python main.py %PARAM% "%SOURCE%" --output "%OUTPUT%" --format "%FORMAT%" --model "%MODEL%"
call .\venv\Scripts\deactivate
pause