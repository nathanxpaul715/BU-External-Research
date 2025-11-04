@echo off
REM Stage 2 Marketing Automation
REM Path to root venv: 4 levels up

set VENV_PATH=..\..\..\..\venv\Scripts\python.exe

if not exist "%VENV_PATH%" (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

"%VENV_PATH%" run_automation.py %*
pause
