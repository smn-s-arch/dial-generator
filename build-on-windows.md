Building the Dial Generator on Windows

1. Install Python

	1.	Download Python Installer
	•	Go to the official Python website and download the latest Windows Installer (e.g., python-3.x.x-amd64.exe).
	2.	Run the Installer
	•	Check “Add Python 3.x to PATH” during installation to ensure you can use Python and pip from the command line.


2. Install Dependencies

	create venv

	`python -m venv venv`

	`venv\Scripts\activate`

	`p install -r requirements.txt`

3. Build the Executable

	Open Command Prompt in Project Directory
	`cd path\to\dial_generator`


	Run PyInstaller
	`build-windows.sh`

4. Run the Application
