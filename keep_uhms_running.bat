@echo off
setlocal

rem Keeps the UHMS demo alive for long local demo sessions.
rem Close this window when you want to stop the local server.

set PYTHONHOME=
set PYTHONPATH=
set CLICK_DISABLE_WINCONSOLE=1
cd /d "%~dp0"

set "PYTHON312_EXE=C:\Users\arindam.d\AppData\Local\Programs\Python\Python312\python.exe"
set "PYTHON314_EXE=C:\Users\arindam.d\AppData\Local\Programs\Python\Python314\python.exe"
set "PYTHON_EXE="

if exist "%PYTHON312_EXE%" set "PYTHON_EXE=%PYTHON312_EXE%"
if not defined PYTHON_EXE if exist "%PYTHON314_EXE%" set "PYTHON_EXE=%PYTHON314_EXE%"

if not defined PYTHON_EXE (
    echo No supported Python runtime was found.
    echo Checked:
    echo "%PYTHON312_EXE%"
    echo "%PYTHON314_EXE%"
    echo.
    echo Install Python 3.12 from python.org, then run:
    echo "C:\Users\arindam.d\AppData\Local\Programs\Python\Python312\python.exe" -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

:restart
echo [%TIME%] Starting UHMS dashboard...
"%PYTHON_EXE%" app.py

echo.
echo [%TIME%] UHMS dashboard stopped. Restarting in 10 seconds... (Ctrl+C to quit)
timeout /t 10 /nobreak >nul
goto restart
