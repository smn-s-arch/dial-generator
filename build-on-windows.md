Building the Dial Generator on Windows

This document provides a concise guide on setting up and building the Dial Generator application on a Windows machine that has no prior installations of Python or other dependencies.

1. Install Python

	1.	Download Python Installer
	•	Go to the official Python website and download the latest Windows Installer (e.g., python-3.x.x-amd64.exe).
	2.	Run the Installer
	•	Check “Add Python 3.x to PATH” during installation to ensure you can use Python and pip from the command line.


2. Install Dependencies

	create venv
	1. `python -m venv venv`
	2. `venv\Scripts\activate`
	3. `p install -r requirements.txt`


These commands install ReportLab (for PDF generation) and PyInstaller (for creating an executable).

3. Project Setup

	1.	Project Structure

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
		
		`build-windows.sh`

5. Run the Application
