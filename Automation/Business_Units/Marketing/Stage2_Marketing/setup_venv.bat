@echo off
REM Setup Virtual Environment for Stage 2 Automation
REM Uses venv from root directory

echo ========================================
echo Stage 2 Marketing - Setup Check
echo ========================================
echo.

REM Path to root venv (2 levels up)
set ROOT_DIR=..\..
set VENV_PATH=%ROOT_DIR%\venv\Scripts\python.exe

echo Checking for virtual environment at root...
if exist "%VENV_PATH%" (
    echo [OK] Virtual environment found at root
    echo.
    echo Installing/updating required packages...
    %ROOT_DIR%\venv\Scripts\pip.exe install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
    echo [OK] All packages installed/updated
) else (
    echo Virtual environment not found at root.
    echo.
    echo Creating new virtual environment...
    cd %ROOT_DIR%
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
    echo Installing required packages...
    venv\Scripts\pip.exe install -r Automation\Stage2_Marketing\requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
    echo [OK] All packages installed
    cd Automation\Stage2_Marketing
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now run the automation with:
echo   run_automation.bat
echo.
pause
