#!/bin/bash

# Function to confirm deletion
confirm_deletion() {
  read -p "Do you want to remove $1? (y/n): " choice
  case "$choice" in
    y|Y ) rm -rf "$1"; echo "$1 removed.";;
    n|N ) echo "$1 kept.";;
    * ) echo "Invalid input. Skipping $1.";;
  esac
}

# Check and ask for permission to delete 'dist'
if [ -d "dist" ]; then
  confirm_deletion "dist"
fi

# Check and ask for permission to delete 'build'
if [ -d "build" ]; then
  confirm_deletion "build"
fi

# Check and ask for permission to delete 'main.spec'
if [ -f "main.spec" ]; then
  confirm_deletion "main.spec"
fi

# Run PyInstaller command
echo "Running PyInstaller..."
python3 -m PyInstaller --onefile --windowed --add-data "config.ini:." --add-data "src/font/din1451ef.ttf:font" main.py

echo "Build process complete."