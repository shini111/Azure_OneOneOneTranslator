# setup.py for cx_Freeze
# Use this if PyInstaller doesn't work well

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need help with some packages
build_options = {
    'packages': [
        'customtkinter', 
        'tkinter', 
        'azure.ai.inference', 
        'azure.core.credentials',
        'bs4',
        'pandas',
        'PyPDF2',
        'docx',
        'pathlib',
        'tempfile',
        'zipfile',
        'threading'
    ],
    'excludes': ['matplotlib', 'numpy.distutils'],  # Exclude unnecessary packages
    'include_files': [
        'ultimateTranslator.py',  # Include your translator module
        # Add any other files your app needs
    ]
}

# Base for Windows GUI applications
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

# Executable configuration
target = Executable(
    script='translator_app.py',
    base=base,
    target_name='UltimateTranslator.exe',
    icon='translator.ico'  # Add an icon if you have one
)

setup(
    name='Ultimate Korean Translator',
    version='1.0',
    description='AI-Powered Korean-English Translation Tool',
    options={'build_exe': build_options},
    executables=[target]
)