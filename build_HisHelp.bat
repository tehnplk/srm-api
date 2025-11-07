@echo off
echo Activating virtual environment...
call .venv\Scripts\activate
echo Building HisHelp application...
pyinstaller --clean --onefile -w --name HisHelp --icon check.ico --add-data "*.png;." Main.py
echo Build complete! The executable is available in the dist folder.
pause
