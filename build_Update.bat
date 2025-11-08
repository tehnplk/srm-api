@echo off
echo Activating virtual environment...
call .venv\Scripts\activate
echo Building Update application...
pyinstaller --clean --onefile --console --name Update Update.py
echo Build complete! The executable is available in the dist folder.
pause
