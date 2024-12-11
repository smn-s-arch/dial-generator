Thermometer Dial Generator

This application allows you to generate a custom thermometer-style dial PDF based on configurable settings. You can adjust parameters like dial radius, temperature range, tick marks, and font. You can also specify custom major tick positions and choose a custom output filename.

Requirements

	•	Python 3.8 or higher
	•	ReportLab for PDF generation
	•	Tkinter (included with most Python installations)
	•	(Optional) A custom font file if specified in config.ini

Setup

	1.	Install dependencies:

pip install reportlab


	2.	Ensure config.ini and font files (if any) are placed as described in the project’s directory structure.

Running the Application

	1.	Activate your virtual environment (if using one).
	2.	Run the GUI:

python main.py


	3.	In the GUI, adjust the dial settings and major tick positions as desired.
	4.	Click “Browse…” next to the Filename field to choose an output PDF file location (optional).
	5.	Click “Generate Dial” to produce the PDF.

Configuration

	•	config.ini stores default dial parameters.
	•	Adjust parameters like temperature_start, temperature_end, angle_start, angle_end, etc.
	•	Add custom major tick positions under [MajorTickPositions] or input them directly in the GUI.

Notes

	•	If using a custom font, ensure the font file is correctly referenced and included in the src/font directory.
	•	After generating the dial, the PDF file will be saved at the chosen location.