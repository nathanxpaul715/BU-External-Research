@echo off
REM Stage 2 Marketing Automation - Windows Batch Runner
REM Runs from: Automation/Stage2_Marketing/
REM Uses venv from: root (../../venv)

echo ========================================
echo Stage 2 Marketing Automation
echo ========================================
echo.

REM Path to root venv (4 levels up from Automation/Business_Units/Marketing/Stage2_Marketing)
set VENV_PATH=..\..\..\..\venv\Scripts\python.exe

REM Check if venv exists
if not exist "%VENV_PATH%" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Expected location: BU-External-Research\venv
    echo Please run setup_venv.bat first.
    echo.
    pause
    exit /b 1
)

REM Run the automation
echo Running Stage 2 Automation for Marketing...
echo.
"%VENV_PATH%" run_automation.py %*

echo.
echo ========================================
echo Automation Complete
echo ========================================
echo.
pause
