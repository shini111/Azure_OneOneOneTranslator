@echo off
setlocal enabledelayedexpansion
echo ================================
echo 📚 Glossary Auto-Detection Status Check
echo ================================
echo.

echo 🔍 CHECKING YOUR TRANSLATION SETUP...
echo.

echo 📋 What your recent log shows:
echo   "📚 Auto-detecting glossaries..." = Started looking
echo   No follow-up messages = No .csv files found in your folder
echo.

echo ❓ HOW TO CHECK GLOSSARY STATUS:
echo.
echo 1. 🖥️ IN THE DESKTOP APP:
echo    • Open the "📚 Glossaries" tab
echo    • Check "Currently Loaded Glossaries" section
echo    • Look at "Active Glossary" dropdown
echo.

echo 2. 📁 FOLDER SCAN OPTIONS:
echo    Choose how to scan your folder:
echo.
echo    A) Drag and drop your folder here
echo    B) Type/paste the folder path
echo    C) Skip folder scan
echo.

set /p choice="Enter choice (A/B/C): "

if /i "!choice!"=="C" goto :skip_scan
if /i "!choice!"=="A" goto :drag_drop
if /i "!choice!"=="B" goto :manual_path

:drag_drop
echo.
echo 📁 DRAG & DROP METHOD:
echo    1. Open File Explorer
echo    2. Navigate to your document folder
echo    3. Drag the folder and drop it here, then press Enter
echo.
set /p "folder_path=Drag folder here: "
goto :scan_folder

:manual_path
echo.
echo ✏️ MANUAL PATH ENTRY:
echo    Example: C:\Users\YourName\Documents\Translations
echo    Tip: Use quotes if path has spaces: "C:\My Folder\Documents"
echo.
set /p "folder_path=Enter folder path: "
goto :scan_folder

:scan_folder
:: Remove quotes if present
set "folder_path=!folder_path:"=!"

:: Check if folder exists
if not exist "!folder_path!" (
    echo.
    echo ❌ Folder not found: !folder_path!
    echo.
    echo 💡 Common issues:
    echo    • Check spelling and path
    echo    • Use quotes for paths with spaces
    echo    • Make sure folder exists
    goto :end_scan
)

echo.
echo 📂 Scanning folder: !folder_path!
echo ================================================
echo.

echo 📄 DOCUMENT FILES FOUND:
set doc_count=0
for %%e in (html txt pdf docx doc htm) do (
    for %%f in ("!folder_path!\*.%%e") do (
        if exist "%%f" (
            echo    ✅ %%~nxf
            set /a doc_count+=1
        )
    )
)

if !doc_count!==0 (
    echo    ❌ No supported document files found
    echo    💡 Looking for: .html, .txt, .pdf, .docx, .doc
)

echo.
echo 📚 GLOSSARY FILES FOUND:
set csv_count=0
for %%f in ("!folder_path!\*.csv") do (
    if exist "%%f" (
        echo    ✅ %%~nxf (%%~zf bytes^)
        set /a csv_count+=1
    )
)

echo.
if !csv_count!==0 (
    echo ❌ NO GLOSSARY FILES FOUND
    echo.
    echo 💡 TO ENABLE GLOSSARY AUTO-DETECTION:
    echo    1. Create a .csv file with this format:
    echo       ┌─────────────────────────────────────────┐
    echo       │ type,raw_name,translated_name,gender    │
    echo       │ character,이시헌,Lee Si-heon,male         │
    echo       │ character,산수유,Sansuyu,female          │
    echo       │ location,세계수,World Tree,              │
    echo       └─────────────────────────────────────────┘
    echo.
    echo    2. Save as 'characters.csv' in: !folder_path!
    echo    3. Run translation again - you'll see loading messages
    echo.
    echo    🎯 Quick way: Use "⬇️ Download Sample" in the Glossaries tab
) else (
    echo ✅ FOUND !csv_count! GLOSSARY FILE(S^)
    echo.
    echo 💡 These should auto-load during translation.
    echo    If they didn't load, check the CSV format:
    echo    • Must have headers: type,raw_name,translated_name
    echo    • Korean text should be in UTF-8 encoding
    echo    • No empty rows at the top
)

:skip_scan
echo.
echo ================================================
echo 🎯 QUICK GLOSSARY REFERENCE:
echo.
echo ✅ How to verify glossaries loaded:
echo    • Check "📚 Glossaries" tab in your app
echo    • Look for "Active Glossary: [name]" in translation log
echo    • Statistics will show "Total Terms: [number]"
echo.
echo 📝 How to create glossaries:
echo    • Use the "⬇️ Download Sample" button in your app
echo    • Edit in Excel/Notepad with UTF-8 encoding
echo    • Save as .csv in the same folder as your documents
echo.
echo 🔄 How to test:
echo    • Add a .csv file to your document folder
echo    • Run translation again
echo    • Check for "✅ Loaded: [filename]" in the log
echo.

:end_scan
echo ================================================
echo.
echo Press any key to exit...
pause >nul