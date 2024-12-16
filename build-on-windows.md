Building the Dial Generator on Windows

This document provides a concise guide on setting up and building the Dial Generator application on a Windows machine that has no prior installations of Python or other dependencies.

1. Install Python

	1.	Download Python Installer
	•	Go to the official Python website and download the latest Windows Installer (e.g., python-3.x.x-amd64.exe).
	2.	Run the Installer
	•	Check “Add Python 3.x to PATH” during installation to ensure you can use Python and pip from the command line.

2. Install Dependencies

	1.	Open Command Prompt
	•	Press Win+R, type cmd, and press Enter.
	2.	Install Pip Packages
	•	Install the required libraries:

pip install reportlab
pip install pyinstaller


These commands install ReportLab (for PDF generation) and PyInstaller (for creating an executable).

3. Project Setup

	1.	Project Structure
Assuming you have a directory structure like:

dial_generator/
    main.py
    src/
        dialgenerator.py
        font/
            din1451ef.ttf
        config.ini
    ...


	2.	Verify Files
	•	main.py: The GUI entry point.
	•	src/dialgenerator.py: Dial logic and PDF generation.
	•	font/din1451ef.ttf: Optional custom font.
	•	config.ini: Default dial settings.

4. Build the Executable

	1.	Open Command Prompt in Project Directory

cd path\to\dial_generator


	2.	Run PyInstaller
Include the custom font and config file in the build:

pyinstaller --onefile --windowed ^
    --add-data "src\font\din1451ef.ttf;src\font" ^
    --add-data "src\config.ini;src" ^
    main.py

Explanation:
	•	--onefile produces a single .exe
	•	--windowed hides the console window when running the GUI
	•	--add-data "src\font\din1451ef.ttf;src\font" bundles the TTF file inside the executable (on Windows, use a semicolon ; to separate source and destination).
	•	--add-data "src\config.ini;src" ensures config.ini is included and placed in the src directory at runtime.

	3.	Check Output
	•	After a successful build, PyInstaller creates a dist folder containing main.exe.

5. Run the Application

	1.	Locate the Executable
	•	Find main.exe in the dist folder.
	2.	Launch the Dial Generator
	•	Double-click main.exe. The GUI should appear, allowing you to configure the dial and generate a PDF.

6. Common Issues & Tips

	•	Missing Files:
If PyInstaller can’t find din1451ef.ttf or config.ini, verify paths in your command (especially on Windows).
	•	Paths & Directory Structure:
Ensure your src folder has an __init__.py if you’re importing as a module.
	•	Adjusting Dial Settings:
The final .exe will read config.ini from the embedded resources. You can modify the GUI fields or manually edit config.ini before building if you want default changes.

You have now built a standalone Windows executable for the Dial Generator application!