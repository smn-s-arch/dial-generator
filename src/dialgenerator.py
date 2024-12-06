import configparser
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont 
import math
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))  # directory of dial-generator.py
parent_dir = os.path.dirname(script_dir)  # parent directory of src
output_dir = os.path.join(parent_dir, 'dials') #output dir for dials

if getattr(sys, 'frozen', False):
    # Running inside a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running normally (not frozen)
    base_path = os.path.dirname(os.path.abspath(__file__))

font_path = os.path.join(base_path, 'font', 'din1451ef.ttf')

os.makedirs(output_dir, exist_ok=True)

pdfmetrics.registerFont(TTFont('din1451ef', font_path))

config_file_path = os.path.join(parent_dir, 'config.ini')

def read_config(config_file_path):
    """
    Read configuration values from a given INI file and return them as parameters.

    Parameters:
        config_file (str): Path to the configuration file.

    Returns:
        tuple: A tuple containing all necessary configuration parameters for drawing the dial.
    """

    config = configparser.ConfigParser()
    config.read(config_file_path)

    dial_settings = config['DialSettings']
    filename = os.path.join(output_dir, dial_settings.get('filename', 'thermometer_dial.pdf'))
    dial_radius_mm = dial_settings.getfloat('dial_radius_mm', 90)
    temperature_start = dial_settings.getfloat('temperature_start', 0)
    temperature_end = dial_settings.getfloat('temperature_end', 200)
    angle_start = dial_settings.getfloat('angle_start', 0)
    angle_end = dial_settings.getfloat('angle_end', 270)
    scale_division = dial_settings.getfloat('major_tick_division', 10)
    minor_tick_division = dial_settings.getint('minor_tick_division', 1)

    major_tick_length_mm = dial_settings.getfloat('major_tick_length_mm', 10)
    major_tick_width = dial_settings.getfloat('major_tick_width', 1)
    major_tick_inner_width = dial_settings.getfloat('major_tick_inner_width', 3)
    minor_tick_length_mm = dial_settings.getfloat('minor_tick_length_mm', 5)
    minor_tick_width = dial_settings.getfloat('minor_tick_width', 0.5)
    middle_minor_tick_length_mm = dial_settings.getfloat('middle_minor_tick_length_mm', 7)
    scale_text_radius_mm = dial_settings.getfloat('scale_text_radius_mm', 29)
    font_size = dial_settings.getint('font_size', 12)
    font_family = dial_settings.get('font_family', 'Helvetica')

    if 'MajorTickPositions' in config:
        major_tick_positions = {}
        for temp_str, angle_str in config['MajorTickPositions'].items():
            temp = float(temp_str)
            angle = float(angle_str)
            major_tick_positions[temp] = angle
    else:
        major_tick_positions = None

    return (filename, dial_radius_mm, temperature_start, temperature_end, angle_start, angle_end,
            scale_division, minor_tick_division, major_tick_positions,
            major_tick_length_mm, major_tick_width, minor_tick_length_mm,
            minor_tick_width, middle_minor_tick_length_mm, scale_text_radius_mm,
            font_size, font_family, major_tick_inner_width)


def interpolate_angles(temperature_start, temperature_end, major_tick_positions, scale_division, minor_tick_division):
    """
    Interpolate angles for minor tick marks between defined major tick positions.

    Parameters:
        temperature_start (float): The starting temperature of the scale.
        temperature_end (float): The ending temperature of the scale.
        major_tick_positions (dict): A dictionary of major ticks {temp: angle}.
        scale_division (float): The temperature difference between major ticks.
        minor_tick_division (int): The temperature increment between minor ticks.

    Returns:
        tuple:
            interpolated_angles (dict): {temp: angle} for major ticks (including interpolated major).
            minor_tick_angles (dict): {temp: angle} for minor ticks.
    """
    sorted_temps = sorted(major_tick_positions.keys())
    interpolated_angles = {}
    minor_tick_angles = {}

    # Interpolate between defined major ticks
    for i in range(len(sorted_temps) - 1):
        temp1 = sorted_temps[i]
        temp2 = sorted_temps[i + 1]
        angle1 = major_tick_positions[temp1]
        angle2 = major_tick_positions[temp2]
        temp_range = temp2 - temp1
        angle_range = angle2 - angle1
        steps = int(temp_range / minor_tick_division)

        for j in range(steps + 1):
            temp = temp1 + j * minor_tick_division
            if temp <= temp2:
                angle = angle1 + ((temp - temp1) / temp_range) * angle_range
                if temp % scale_division == 0:
                    # This is a major tick
                    interpolated_angles[temp] = angle
                else:
                    # This is a minor tick
                    minor_tick_angles[temp] = angle

    return interpolated_angles, minor_tick_angles


def draw_minor_ticks(c, center_x, center_y, dial_radius, minor_tick_angles, scale_division,
                     minor_tick_division, minor_tick_length, middle_minor_tick_length, minor_tick_width):
    """
    Draw the minor tick marks on the dial.

    Parameters:
        c (canvas.Canvas): The ReportLab canvas object.
        center_x, center_y (float): Coordinates of the dial center.
        dial_radius (float): The radius of the dial in points.
        minor_tick_angles (dict): {temp: angle} for minor ticks.
        scale_division (float): Temperature difference between major ticks.
        minor_tick_division (int): Temperature step between minor ticks.
        minor_tick_length (float): Length of the regular minor ticks in points.
        middle_minor_tick_length (float): Length of the intermediate minor ticks (like half-step ticks).
        minor_tick_width (float): Line width for minor ticks.
    """
    for temp, physical_angle in minor_tick_angles.items():
        rad_angle = math.radians(360 - physical_angle)

        # Decide tick length based on whether it's a "middle" minor tick or a regular minor tick
        if temp % (scale_division / 2) == 0:
            tick_length = middle_minor_tick_length
        else:
            tick_length = minor_tick_length

        x_start = center_x + (dial_radius - tick_length) * math.cos(rad_angle)
        y_start = center_y + (dial_radius - tick_length) * math.sin(rad_angle)
        x_end = center_x + dial_radius * math.cos(rad_angle)
        y_end = center_y + dial_radius * math.sin(rad_angle)

        c.setLineWidth(minor_tick_width)
        c.line(x_start, y_start, x_end, y_end)


def draw_major_ticks_and_labels(c, center_x, center_y, dial_radius, major_tick_positions,
                                major_tick_length, major_tick_width, font_family, font_size, scale_text_radius, major_tick_inner_width):
    """
    Draw the major tick marks and their associated temperature labels.

    Parameters:
        c (canvas.Canvas): The ReportLab canvas object.
        center_x, center_y (float): Coordinates of the dial center.
        dial_radius (float): Radius of the dial in points.
        major_tick_positions (dict): {temp: angle} with angles for major ticks.
        major_tick_length (float): Length of major ticks in points.
        major_tick_width (float): Line width for major ticks.
        font_family (str): Font family for the tick labels.
        font_size (int): Font size for the tick labels.
        scale_text_radius (float): The radius at which to place the scale numbers (inside the dial).
    """
    # This offset may be reduced or adjusted as needed
    text_offset = 0  # Start at 0 since we're now using scale_text_radius
    epsilon = 1e-6

    #Halfway points of the major tick
    half_tick_length = major_tick_length / 2.0

    for temp, physical_angle in major_tick_positions.items():
        rad_angle = math.radians(360 - physical_angle)

        # Coordinates of inner major mark
        x_inner_start = center_x + (dial_radius - major_tick_length) * math.cos(rad_angle)
        y_inner_start = center_y + (dial_radius - major_tick_length) * math.sin(rad_angle)
        x_inner_end = center_x + (dial_radius - half_tick_length) * math.cos(rad_angle)
        y_inner_end = center_y + (dial_radius - half_tick_length) * math.sin(rad_angle)

        # Coordinates of outer major mark
        x_outer_start = x_inner_end
        y_outer_start = y_inner_end
        x_outer_end = center_x + dial_radius * math.cos(rad_angle)
        y_outer_end = center_y + dial_radius * math.sin(rad_angle)

        #draw inner major mark
        c.setLineWidth(major_tick_inner_width)
        c.line(x_inner_start, y_inner_start, x_inner_end, y_inner_end)

        #draw outer major mark
        c.setLineWidth(major_tick_width)
        c.line(x_outer_start, y_outer_start, x_outer_end, y_outer_end)

        # Position text inside the scale at scale_text_radius
        # Adjust scale_text_radius_mm in your config to move text in or out.
        x_text = center_x + (scale_text_radius) * math.cos(rad_angle)
        y_text = center_y + (scale_text_radius) * math.sin(rad_angle)

        c.setFont(font_family, font_size)

        # Save graphics state before transformations
        c.saveState()

        # Move to the text position
        c.translate(x_text, y_text)

        # If the line is nearly horizontal, adjust text vertically for better centering
        if abs(y_outer_start - y_outer_end) < epsilon:
            # Adjust vertical offset if needed; try different values if not centered perfectly
            vertical_offset = font_size * 0.3  # Experiment with this value
            c.translate(0, -vertical_offset)

        # Draw the label, centered
        # Text remains horizontal; if you want to rotate it tangentially, consider c.rotate(...) here
        c.drawCentredString(0, 0, str(int(temp)))

        # Restore state
        c.restoreState()


def draw_thermometer_dial(filename, dial_radius_mm, temperature_start, temperature_end, angle_start, angle_end,
                          scale_division, minor_tick_division, major_tick_positions,
                          major_tick_length_mm, major_tick_width, minor_tick_length_mm,
                          minor_tick_width, middle_minor_tick_length_mm, scale_text_radius_mm,
                          font_size, font_family, major_tick_inner_width):
    """
    Draw a thermometer-style dial as a PDF.

    Parameters:
        filename (str): Output PDF filename.
        dial_radius_mm (float): Radius of the dial in millimeters.
        temperature_start (float): Starting temperature of the scale.
        temperature_end (float): Ending temperature of the scale.
        angle_start (float): Starting angle offset for temperature_start.
        angle_end (float): Ending angle offset for temperature_end.
        scale_division (float): Temperature difference between major ticks.
        minor_tick_division (int): Temperature increment for minor ticks.
        major_tick_positions (dict or None): If not None, user-defined major tick positions {temp: angle_offset}.
        major_tick_length_mm (float): Length of major ticks in mm.
        major_tick_width (float): Line width for major ticks.
        minor_tick_length_mm (float): Length of regular minor ticks in mm.
        minor_tick_width (float): Line width for minor ticks.
        middle_minor_tick_length_mm (float): Length of intermediate minor ticks in mm.
        scale_text_radius_mm (float): Radius at which text labels will be placed.
        font_size (int): Font size for text labels.
        font_family (str): Font family for text labels.
    """
    # The physical_start_angle shifts the entire scale. If 135 degrees is chosen,
    # it might mean that the "0" angle visually appears at top-left quadrant.
    # Adjust this angle as needed to orient your scale correctly.
    physical_start_angle = 135  # degrees

    # Convert dimensions from mm to points (ReportLab works in points)
    dial_radius = dial_radius_mm * mm
    major_tick_length = major_tick_length_mm * mm
    minor_tick_length = minor_tick_length_mm * mm
    middle_minor_tick_length = middle_minor_tick_length_mm * mm
    # scale_text_radius is currently unused, but retained for future customization
    scale_text_radius = scale_text_radius_mm * mm

    page_size = (dial_radius * 2 + 20 * mm, dial_radius * 2 + 20 * mm)
    c = canvas.Canvas(filename, pagesize=page_size)

    center_x = page_size[0] / 2
    center_y = page_size[1] / 2

    # If no major_tick_positions are given, distribute them evenly
    if major_tick_positions is None:
        major_tick_positions = {}
        total_steps = int((temperature_end - temperature_start) / scale_division)
        for i in range(total_steps + 1):
            temp = temperature_start + i * scale_division
            angle_offset = ((temp - temperature_start) / (temperature_end - temperature_start)) * (angle_end - angle_start) + angle_start
            physical_angle = physical_start_angle + angle_offset
            major_tick_positions[temp] = physical_angle

        interpolated_angles, minor_tick_angles = interpolate_angles(temperature_start, temperature_end,
                                                                    major_tick_positions, scale_division, minor_tick_division)
    else:
        # Adjust the provided major ticks by adding physical_start_angle
        adjusted_major_tick_positions = {}
        for temp, angle_offset in major_tick_positions.items():
            physical_angle = physical_start_angle + angle_offset
            adjusted_major_tick_positions[temp] = physical_angle

        interpolated_angles, minor_tick_angles = interpolate_angles(temperature_start, temperature_end,
                                                                    adjusted_major_tick_positions, scale_division, minor_tick_division)
        major_tick_positions = interpolated_angles

    # Draw minor ticks
    draw_minor_ticks(c, center_x, center_y, dial_radius, minor_tick_angles, scale_division,
                     minor_tick_division, minor_tick_length, middle_minor_tick_length, minor_tick_width)

    # Draw major ticks and labels
    draw_major_ticks_and_labels(c, center_x, center_y, dial_radius, major_tick_positions,
                                major_tick_length, major_tick_width, font_family, font_size, scale_text_radius, major_tick_inner_width)

    # Show the page and save the final result
    c.showPage()
    c.save()
    print(f"Thermometer dial saved as {filename}")


if __name__ == "__main__":
    if not os.path.exists(config_file_path):
        print(f"Configuration file '{config_file_path}' not found.")
    else:
        (filename, dial_radius_mm, temperature_start, temperature_end, angle_start, angle_end,
         scale_division, minor_tick_division, major_tick_positions,
         major_tick_length_mm, major_tick_width, minor_tick_length_mm,
         minor_tick_width, middle_minor_tick_length_mm, scale_text_radius,
         font_size, font_family, major_tick_inner_width) = read_config(config_file_path)

        draw_thermometer_dial(filename, dial_radius_mm, temperature_start, temperature_end, angle_start, angle_end,
                              scale_division, minor_tick_division, major_tick_positions,
                              major_tick_length_mm, major_tick_width, minor_tick_length_mm,
                              minor_tick_width, middle_minor_tick_length_mm, scale_text_radius,
                              font_size, font_family, major_tick_inner_width)