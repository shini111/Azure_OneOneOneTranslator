@echo off
echo ========================================
echo 🚀 Ultimate Korean Translator - Build Script (Fixed Missing Files)
echo ========================================
echo.

:: Check if main app file exists
if not exist "translator_app.py" (
    echo ❌ translator_app.py not found!
    echo Make sure you're running this from the correct directory
    echo Current directory: %CD%
    echo.
    echo Expected files:
    dir *.py /b 2>nul
    pause
    exit /b 1
)

echo 🔧 Activating virtual environment...
:: Try different virtual environment locations
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Using local venv
) else if exist "..\New folder\venv\Scripts\activate.bat" (
    call "..\New folder\venv\Scripts\activate.bat"
    echo ✅ Using venv from New folder
) else (
    echo ⚠️ Virtual environment not found in expected locations
    echo Trying to use system Python...
)

:: Verify Python is working
echo.
echo 🔍 Checking Python setup...
python --version
if errorlevel 1 (
    echo ❌ Python not found or not working
    pause
    exit /b 1
)

echo.
echo 📦 Installing PyInstaller if needed...
python -m pip install pyinstaller
if errorlevel 1 (
    echo ❌ Failed to install PyInstaller
    pause
    exit /b 1
)

:: Verify PyInstaller is working
echo.
echo 🔍 Verifying PyInstaller...
python -m PyInstaller --version
if errorlevel 1 (
    echo ❌ PyInstaller installation failed
    pause
    exit /b 1
)

echo.
echo 🧹 Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

:: Create missing azure_config_sample.txt if it doesn't exist
echo.
echo 📝 Checking for required files...
if not exist "azure_config_sample.txt" (
    echo ⚠️ azure_config_sample.txt not found, creating it...
    echo ENDPOINT=https://your-deployment-name.services.ai.azure.com/models > azure_config_sample.txt
    echo API_KEY=your-actual-api-key-from-azure-ai-studio >> azure_config_sample.txt
    echo. >> azure_config_sample.txt
    echo # Instructions: >> azure_config_sample.txt
    echo # 1. Copy this file and rename it to "azure_config.txt" >> azure_config_sample.txt
    echo # 2. Replace the values above with your actual Azure credentials >> azure_config_sample.txt
    echo # 3. Keep azure_config.txt secure and do not share it >> azure_config_sample.txt
    echo ✅ Created azure_config_sample.txt
)

:: Build the executable with only files that exist
echo.
echo 🔧 Building executable...
echo This may take 3-5 minutes depending on your system...
echo.

:: Use minimal build command to avoid missing file issues
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "UltimateKoreanTranslator" ^
    --distpath "dist" ^
    --workpath "build" ^
    --specpath "build" ^
    --hidden-import "azure.ai.inference" ^
    --hidden-import "azure.core.credentials" ^
    --hidden-import "azure.ai.inference.models" ^
    --hidden-import "customtkinter" ^
    --hidden-import "bs4" ^
    --hidden-import "pandas" ^
    --hidden-import "PyPDF2" ^
    --hidden-import "docx" ^
    --hidden-import "pathlib" ^
    --hidden-import "tempfile" ^
    --hidden-import "threading" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.filedialog" ^
    --hidden-import "tkinter.messagebox" ^
    --collect-all "customtkinter" ^
    --noconfirm ^
    translator_app.py

echo.
if exist "dist\UltimateKoreanTranslator.exe" (
    echo ✅ Build successful!
    echo.
    
    :: Get file size
    for %%A in ("dist\UltimateKoreanTranslator.exe") do (
        set /a "size=%%~zA/1024/1024"
        echo 📁 Executable created: dist\UltimateKoreanTranslator.exe
        echo 📏 File size: %%~zA bytes ^(~!size! MB^)
    )
    
    echo.
    echo 📦 Creating release package...
    
    :: Create release folder
    if not exist "release" mkdir "release"
    
    :: Copy executable
    copy "dist\UltimateKoreanTranslator.exe" "release\"
    
    :: Copy files that exist
    if exist "azure_config_sample.txt" (
        copy "azure_config_sample.txt" "release\"
        echo ✅ Copied azure_config_sample.txt
    )
    if exist "README.md" (
        copy "README.md" "release\"
        echo ✅ Copied README.md
    )
    if exist "requirements.txt" (
        copy "requirements.txt" "release\"
        echo ✅ Copied requirements.txt
    )
    
    :: Create quick start guide
    echo 🚀 Ultimate Korean Translator - Quick Start > "release\QUICK_START.txt"
    echo ================================================ >> "release\QUICK_START.txt"
    echo. >> "release\QUICK_START.txt"
    echo 1. First time setup: >> "release\QUICK_START.txt"
    echo    - Run UltimateKoreanTranslator.exe >> "release\QUICK_START.txt"
    echo    - Go to About tab and click "Configure Azure AI DeepSeek" >> "release\QUICK_START.txt"
    echo    - Enter your Azure AI credentials >> "release\QUICK_START.txt"
    echo. >> "release\QUICK_START.txt"
    echo 2. Start translating: >> "release\QUICK_START.txt"
    echo    - Go to Files tab and select documents >> "release\QUICK_START.txt"
    echo    - Add glossaries if needed ^(.csv format^) >> "release\QUICK_START.txt"
    echo    - Click Start Translation >> "release\QUICK_START.txt"
    echo. >> "release\QUICK_START.txt"
    echo 3. Supported file types: >> "release\QUICK_START.txt"
    echo    - .txt, .pdf, .docx, .html files >> "release\QUICK_START.txt"
    echo    - Korean to English translation >> "release\QUICK_START.txt"
    echo    - Preserves HTML structure and images >> "release\QUICK_START.txt"
    echo. >> "release\QUICK_START.txt"
    echo Need help? Check the About tab in the application! >> "release\QUICK_START.txt"
    
    :: Create simple sample glossary
    echo type,raw_name,translated_name,gender > "release\sample_glossary.csv"
    echo character,이시헌,Lee Si-heon,male >> "release\sample_glossary.csv"
    echo character,산수유,Sansuyu,female >> "release\sample_glossary.csv"
    echo location,세계수,World Tree, >> "release\sample_glossary.csv"
    echo skill,개화,Bloom, >> "release\sample_glossary.csv"
    echo ✅ Created sample_glossary.csv
    
    :: Try to create ZIP file
    echo.
    echo 📦 Creating release ZIP file...
    powershell -command "try { Compress-Archive -Path 'release\*' -DestinationPath 'UltimateKoreanTranslator_Release.zip' -Force; Write-Host '✅ ZIP created successfully' } catch { Write-Host '⚠️ ZIP creation failed:' $_.Exception.Message }"
    
    echo.
    echo 🎉 Build complete! Distribution ready:
    echo    📁 Single executable: dist\UltimateKoreanTranslator.exe
    echo    📦 Release package: release\ folder
    if exist "UltimateKoreanTranslator_Release.zip" (
        echo    🗜️ Release ZIP: UltimateKoreanTranslator_Release.zip
    )
    echo.
    echo 💡 Ready for distribution:
    echo    • Users can run the .exe file directly
    echo    • No Python installation required
    echo    • Azure credentials configured in the app
    echo.
    echo 🧪 Testing the executable...
    echo    You can test it now by running: release\UltimateKoreanTranslator.exe
    echo.
    echo 📂 Opening release folder...
    start release
    
) else (
    echo ❌ Build failed!
    echo.
    echo 🔍 Debugging information:
    echo Current directory: %CD%
    echo Python location: 
    where python 2>nul
    echo.
    echo Files in current directory:
    dir *.py *.txt 2>nul
    echo.
    echo 💡 Try this manual build command:
    echo python -m PyInstaller --onefile --windowed translator_app.py
    echo.
    echo If that works, the issue is with the advanced options.
    echo Check the error messages above for specific issues.
)

echo.
echo 🧹 Cleaning up build artifacts...
if exist "build" rmdir /s /q "build"

echo.
echo 📋 Build process completed!
pause