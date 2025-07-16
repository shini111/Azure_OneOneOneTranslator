@echo off
echo ================================
echo 🖥️ Ultimate Korean Translator (Desktop)
echo ================================

:: Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Check if the main app file exists
if exist "translator_app.py" (
    echo 🚀 Starting Desktop GUI Application...
    echo.
    python translator_app.py
) else if exist "Desktop Translation App with CustomTkinter.txt" (
    echo 🚀 Starting Desktop GUI Application...
    echo Note: Rename your app file to translator_app.py for easier access
    echo.
    python "Desktop Translation App with CustomTkinter.txt"
) else (
    echo ❌ Desktop app file not found!
    echo Looking for: translator_app.py
    echo Available Python files:
    dir *.py /b
    echo.
    echo Please make sure the desktop app file is in this directory
    pause
    exit /b 1
)

:: Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo ❌ Application encountered an error
    echo Check the error messages above
    pause
)