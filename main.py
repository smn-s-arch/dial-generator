import tkinter as tk
from tkinter import filedialog, messagebox
import os
import configparser

# Import functions from dialgenerator
from src.dialgenerator import read_config, draw_thermometer_dial, config_file_path, output_dir

def load_config():
    """Load the current config.ini settings into a dictionary."""
    if not os.path.exists(config_file_path):
        messagebox.showerror("Error", f"Configuration file '{config_file_path}' not found.")
        return None

    config = configparser.ConfigParser()
    config.read(config_file_path)

    dial_settings = config['DialSettings']

    settings = {
        'filename': dial_settings.get('filename', 'thermometer_dial.pdf'),
        'dial_radius_mm': dial_settings.getfloat('dial_radius_mm', 90),
        'temperature_start': dial_settings.getfloat('temperature_start', 0),
        'temperature_end': dial_settings.getfloat('temperature_end', 200),
        'angle_start': dial_settings.getfloat('angle_start', 0),
        'angle_end': dial_settings.getfloat('angle_end', 270),
        'major_tick_division': dial_settings.getfloat('major_tick_division', 10),
        'minor_tick_division': dial_settings.getint('minor_tick_division', 1),
        'major_tick_length_mm': dial_settings.getfloat('major_tick_length_mm', 10),
        'major_tick_width': dial_settings.getfloat('major_tick_width', 1),
        'major_tick_inner_width': dial_settings.getfloat('major_tick_inner_width', 3),
        'minor_tick_length_mm': dial_settings.getfloat('minor_tick_length_mm', 5),
        'minor_tick_width': dial_settings.getfloat('minor_tick_width', 0.5),
        'middle_minor_tick_length_mm': dial_settings.getfloat('middle_minor_tick_length_mm', 7),
        'scale_text_radius_mm': dial_settings.getfloat('scale_text_radius_mm', 29),
        'font_size': dial_settings.getint('font_size', 12),
        'font_family': dial_settings.get('font_family', 'Helvetica')
    }

    # Load existing MajorTickPositions if any
    major_positions = {}
    if 'MajorTickPositions' in config:
        for t, a in config['MajorTickPositions'].items():
            # t: temperature (string), a: angle (string)
            # Convert them to float if possible
            try:
                temp_val = float(t)
                angle_val = float(a)
                major_positions[temp_val] = angle_val
            except ValueError:
                # If invalid, skip
                pass

    return settings, major_positions


def save_config(settings, major_positions):
    """Save the updated settings and major positions to config.ini."""
    config = configparser.ConfigParser()
    config['DialSettings'] = {
        'filename': settings['filename'],
        'dial_radius_mm': str(settings['dial_radius_mm']),
        'temperature_start': str(settings['temperature_start']),
        'temperature_end': str(settings['temperature_end']),
        'angle_start': str(settings['angle_start']),
        'angle_end': str(settings['angle_end']),
        'major_tick_division': str(settings['major_tick_division']),
        'minor_tick_division': str(settings['minor_tick_division']),
        'major_tick_length_mm': str(settings['major_tick_length_mm']),
        'major_tick_width': str(settings['major_tick_width']),
        'major_tick_inner_width': str(settings['major_tick_inner_width']),
        'minor_tick_length_mm': str(settings['minor_tick_length_mm']),
        'minor_tick_width': str(settings['minor_tick_width']),
        'middle_minor_tick_length_mm': str(settings['middle_minor_tick_length_mm']),
        'scale_text_radius_mm': str(settings['scale_text_radius_mm']),
        'font_size': str(settings['font_size']),
        'font_family': settings['font_family']
    }

    if major_positions:
        config['MajorTickPositions'] = {}
        for temp_val, angle_val in major_positions.items():
            config['MajorTickPositions'][str(temp_val)] = str(angle_val)

    with open(config_file_path, 'w') as f:
        config.write(f)

def browse_output_pdf():
    """Open a 'Save As' dialog to select where to save the output PDF."""
    # Provide a default filename and .pdf extension
    new_filename = filedialog.asksaveasfilename(
        title="Choose PDF Output Location",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    if new_filename:
        entries['filename'].set(new_filename)  # Update the filename entry with the chosen path

def generate_dial():
    """Called when user clicks 'Generate Dial' button."""
    updated_settings = {}
    float_fields = ['dial_radius_mm', 'temperature_start', 'temperature_end',
                    'angle_start', 'angle_end', 'major_tick_division', 'major_tick_length_mm',
                    'major_tick_width', 'major_tick_inner_width', 'minor_tick_length_mm',
                    'minor_tick_width', 'middle_minor_tick_length_mm', 'scale_text_radius_mm']
    int_fields = ['minor_tick_division', 'font_size']

    # Convert main settings
    for field, var in entries.items():
        val = var.get()
        if field in float_fields:
            try:
                val = float(val)
            except ValueError:
                messagebox.showerror("Error", f"Invalid float value for {field}")
                return
        elif field in int_fields:
            try:
                val = int(val)
            except ValueError:
                messagebox.showerror("Error", f"Invalid integer value for {field}")
                return
        updated_settings[field] = val

    # Handle major tick positions
    major_positions = {}
    for i in range(10):
        temp_str = major_tick_temp_vars[i].get().strip()
        angle_str = major_tick_angle_vars[i].get().strip()
        if not temp_str and not angle_str:
            # Both empty, skip this one
            continue
        if not temp_str or not angle_str:
            # One is empty, one is not
            messagebox.showerror("Error", f"Major tick position {i+1} is incomplete.")
            return
        try:
            t_val = float(temp_str)
            a_val = float(angle_str)
            major_positions[t_val] = a_val
        except ValueError:
            messagebox.showerror("Error", f"Invalid float values for major tick position {i+1}.")
            return

    # Save config
    save_config(updated_settings, major_positions)

    # Now read config and generate the dial
    try:
        (filename, dial_radius_mm, temperature_start, temperature_end, angle_start, angle_end,
         scale_division, minor_tick_division, read_positions,
         major_tick_length_mm, major_tick_width, minor_tick_length_mm,
         minor_tick_width_, middle_minor_tick_length_mm, scale_text_radius_mm,
         font_size, font_family, major_tick_inner_width) = read_config(config_file_path)

        # filename is already potentially overridden in entries['filename']
        # If user picked a custom path, it overrides config.ini setting
        chosen_filename = entries['filename'].get().strip()
        if chosen_filename:
            filename = chosen_filename

        draw_thermometer_dial(filename, dial_radius_mm, temperature_start, temperature_end,
                              angle_start, angle_end, scale_division, minor_tick_division,
                              read_positions, major_tick_length_mm, major_tick_width,
                              minor_tick_length_mm, minor_tick_width_,
                              middle_minor_tick_length_mm, scale_text_radius_mm,
                              font_size, font_family, major_tick_inner_width)

        messagebox.showinfo("Success", f"Dial generated and saved as {filename}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def main():
    global entries, major_tick_temp_vars, major_tick_angle_vars
    root = tk.Tk()
    root.title("Dial Generator")

    result = load_config()
    if result is None:
        return
    settings, loaded_positions = result

    fields = [
        ('filename', 'Filename'),
        ('dial_radius_mm', 'Dial Radius (mm)'),
        ('temperature_start', 'Temperature Start'),
        ('temperature_end', 'Temperature End'),
        ('angle_start', 'Angle Start'),
        ('angle_end', 'Angle End'),
        ('major_tick_division', 'Major Tick Division'),
        ('minor_tick_division', 'Minor Tick Division'),
        ('major_tick_length_mm', 'Major Tick Length (mm)'),
        ('major_tick_width', 'Major Tick Width'),
        ('major_tick_inner_width', 'Major Tick Inner Width'),
        ('minor_tick_length_mm', 'Minor Tick Length (mm)'),
        ('minor_tick_width', 'Minor Tick Width'),
        ('middle_minor_tick_length_mm', 'Middle Minor Tick Length (mm)'),
        ('scale_text_radius_mm', 'Scale Text Radius (mm)'),
        ('font_size', 'Font Size'),
        ('font_family', 'Font Family')
    ]

    entries = {}

    # Create main setting fields
    for i, (field, label_text) in enumerate(fields):
        lbl = tk.Label(root, text=label_text)
        lbl.grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)

        var = tk.StringVar()
        var.set(str(settings[field]))
        ent = tk.Entry(root, textvariable=var, width=30)
        ent.grid(row=i, column=1, padx=5, pady=5)
        entries[field] = var

        # If this is the filename field, add a "Browse" button
        if field == 'filename':
            browse_btn = tk.Button(root, text="Browse...", command=browse_output_pdf)
            browse_btn.grid(row=i, column=2, padx=5, pady=5)

    # Major Tick Positions
    start_row = len(fields)
    tick_label = tk.Label(root, text="Major Tick Positions (Temp/Angle):")
    tick_label.grid(row=start_row, column=0, columnspan=4, pady=(10,5), sticky=tk.W)

    major_tick_temp_vars = []
    major_tick_angle_vars = []
    loaded_items = list(loaded_positions.items())
    for i in range(10):
        temp_lbl = tk.Label(root, text=f"Pos {i+1} Temp:")
        temp_lbl.grid(row=start_row+1+i, column=0, sticky=tk.E, padx=5, pady=2)
        temp_var = tk.StringVar()
        angle_var = tk.StringVar()

        # Prefill if we have preloaded positions
        if i < len(loaded_items):
            t_val, a_val = loaded_items[i]
            temp_var.set(str(t_val))
            angle_var.set(str(a_val))

        temp_entry = tk.Entry(root, textvariable=temp_var, width=10)
        temp_entry.grid(row=start_row+1+i, column=1, sticky=tk.W, padx=5, pady=2)

        angle_lbl = tk.Label(root, text="Angle:")
        angle_lbl.grid(row=start_row+1+i, column=2, sticky=tk.E, padx=5, pady=2)

        angle_entry = tk.Entry(root, textvariable=angle_var, width=10)
        angle_entry.grid(row=start_row+1+i, column=3, sticky=tk.W, padx=5, pady=2)

        major_tick_temp_vars.append(temp_var)
        major_tick_angle_vars.append(angle_var)

    generate_btn = tk.Button(root, text="Generate Dial", command=generate_dial)
    generate_btn.grid(row=start_row+11, column=0, columnspan=4, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()