@echo off
echo ================================
echo 🌐 Ultimate Korean Translator (Web)
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

:: Check if streamlit app exists
if not exist "streamlit_app.py" (
    echo ❌ Streamlit app file not found!
    echo Looking for: streamlit_app.py
    echo.
    echo Available Python files:
    dir *.py /b
    pause
    exit /b 1
)

echo 🚀 Starting Streamlit Web Application...
echo.
echo The web app will open in your default browser
echo URL: http://localhost:8501
echo.
echo 💡 Tips:
echo   • Close this window to stop the server
echo   • Use Ctrl+C to stop the server manually
echo   • The app will auto-reload when you make changes
echo.

:: Start streamlit with custom config
streamlit run streamlit_app.py --server.headless false --server.runOnSave true

:: Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo ❌ Streamlit failed to start
    echo Common issues:
    echo   • Port 8501 might be in use
    echo   • Missing dependencies (run setup.bat again)
    echo   • Check error messages above
    pause
)