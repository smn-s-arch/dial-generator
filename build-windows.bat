@echo off
REM build.bat: Script to build the Dial Generator on Windows using PyInstaller

echo Installing/updating PyInstaller...
pip install --upgrade pyinstaller

echo Building standalone executable with PyInstaller...
pyinstaller --onefile --windowed ^
    --add-data "src\font\din1451ef.ttf;font" ^
    --add-data "config.ini:." ^
    main.py

echo Build complete. Check the dist folder for main.exe.
pause