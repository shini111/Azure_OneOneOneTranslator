@echo off
echo ================================
echo 🚀 Ultimate Korean Translator Setup
echo ================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.9+ and add it to PATH
    pause
    exit /b 1
)

echo ✅ Python found
python --version

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

:: Activate virtual environment
echo.
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo.
echo 📈 Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo.
echo 📚 Installing requirements...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo Installing core dependencies...
    pip install customtkinter
    pip install pandas
    pip install PyPDF2
    pip install python-docx
    pip install beautifulsoup4
    pip install azure-ai-inference
    pip install azure-core
    pip install streamlit
    pip install openpyxl
)

if errorlevel 1 (
    echo ❌ Failed to install some packages
    echo You may need to install them manually
) else (
    echo ✅ All packages installed successfully
)

echo.
echo 🎉 Setup complete!
echo.
echo Available commands:
echo   • run_desktop_app.bat    - Launch CustomTkinter GUI
echo   • run_streamlit_app.bat  - Launch web interface  
echo   • run_console_app.bat    - Launch command-line version
echo   • activate_env.bat       - Activate environment for development
echo.
pause