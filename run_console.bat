@echo off
echo ================================
echo 💻 Ultimate Korean Translator (Console)
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

:: Check if main translator exists
if not exist "ultimateTranslator.py" (
    echo ❌ Main translator file not found!
    echo Looking for: ultimateTranslator.py
    echo.
    echo Available Python files:
    dir *.py /b
    pause
    exit /b 1
)

echo 🚀 Starting Console Application...
echo.
echo 💡 This is the command-line interface for batch processing
echo    Use this for automated workflows and folder processing
echo.

python ultimateTranslator.py

:: Keep window open after execution
echo.
echo 📋 Console application finished
pause