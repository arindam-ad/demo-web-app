@echo off
setlocal

rem Clear Python variables that can cause "No module named encodings" on Windows.
set PYTHONHOME=
set PYTHONPATH=
set CLICK_DISABLE_WINCONSOLE=1

cd /d "%~dp0"

set "PROJECT_VENV_EXE=%CD%\.venv\Scripts\python.exe"
set "PYTHON312_EXE=C:\Users\arindam.d\AppData\Local\Programs\Python\Python312\python.exe"
set "PYTHON314_EXE=C:\Users\arindam.d\AppData\Local\Programs\Python\Python314\python.exe"
set "PYTHON_EXE="

if exist "%PROJECT_VENV_EXE%" set "PYTHON_EXE=%PROJECT_VENV_EXE%"
if not defined PYTHON_EXE if exist "%PYTHON312_EXE%" set "PYTHON_EXE=%PYTHON312_EXE%"
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

"%PYTHON_EXE%" -c "import encodings" >nul 2>nul
if errorlevel 1 (
    echo Selected Python cannot import encodings:
    echo "%PYTHON_EXE%"
    echo.
    echo Fix: recreate the project virtual environment, then install requirements:
    echo py -3.14 -m venv .venv
    echo .venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

"%PYTHON_EXE%" app.py

endlocal
