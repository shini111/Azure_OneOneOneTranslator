@echo off
echo ================================
echo 🔧 Activating Development Environment
echo ================================

:: Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo 🎯 Development environment activated!
echo.
echo Available commands:
echo   python translator_app.py     - Run desktop GUI
echo   python streamlit_app.py      - Run streamlit (then visit localhost:8501)
echo   python ultimateTranslator.py - Run console version
echo   pip install [package]       - Install new packages
echo   pip list                     - View installed packages
echo   deactivate                   - Exit virtual environment
echo.

:: Keep the command prompt open with activated environment
cmd /k