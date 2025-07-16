@echo off
echo ================================
echo 📈 Ultimate Korean Translator - Update Dependencies  
echo ================================
echo.

:: Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo 📈 Upgrading pip...
python -m pip install --upgrade pip

echo.
echo 📚 Updating all packages...
echo 💡 Note: CustomTkinter is under active development - regular updates recommended
if exist "requirements.txt" (
    echo Using requirements.txt...
    pip install --upgrade -r requirements.txt
) else (
    echo Updating core packages...
    pip install --upgrade customtkinter pandas PyPDF2 python-docx beautifulsoup4 azure-ai-inference azure-core streamlit openpyxl
)

echo.
echo 🧹 Cleaning up cache...
pip cache purge

echo.
echo 📋 Current package versions:
pip list | findstr /i "customtkinter pandas PyPDF2 python-docx beautifulsoup4 azure streamlit"

echo.
echo ✅ Update complete!
echo.
echo If you're still having issues:
echo   • Delete the "venv" folder and run setup.bat again
echo   • Check that Python is updated to 3.9+
echo   • Ensure you have a stable internet connection
echo.
pause