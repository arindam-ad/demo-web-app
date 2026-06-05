@echo off
setlocal

rem Recreates the project virtual environment when Windows/PyCharm points at
rem a broken Python runtime and shows "No module named encodings".

set PYTHONHOME=
set PYTHONPATH=
cd /d "%~dp0"

set "PYTHON314_EXE=C:\Users\arindam.d\AppData\Local\Programs\Python\Python314\python.exe"

if not exist "%PYTHON314_EXE%" (
    echo Python 3.14 was not found at:
    echo "%PYTHON314_EXE%"
    echo.
    echo Install Python 3.14 or update this script with the correct python.exe path.
    pause
    exit /b 1
)

"%PYTHON314_EXE%" -c "import encodings" >nul 2>nul
if errorlevel 1 (
    echo The base Python runtime itself cannot import encodings:
    echo "%PYTHON314_EXE%"
    echo.
    echo Reinstall Python 3.14 from python.org, then run this script again.
    pause
    exit /b 1
)

if exist ".venv" (
    echo Removing old .venv...
    rmdir /s /q ".venv"
)

echo Creating .venv...
"%PYTHON314_EXE%" -m venv ".venv"
if errorlevel 1 exit /b 1

echo Installing dashboard requirements...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

if exist "backend\requirements.txt" (
    echo Installing backend requirements...
    ".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
    if errorlevel 1 exit /b 1
)

echo.
echo Python environment repaired.
echo Use launch_uhms_dashboard.bat to start the dashboard.
pause

endlocal
