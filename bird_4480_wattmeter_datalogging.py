"""
Example Description:
        This example acts as a PC-based, graphical tool that interacts with
        the Bird 4480A Digital Wattmeter over the USB bus using VISA. The
        program sends SCPI comands to the 4480 and gets a responce every
        second. It then takes the collected data such as forward and reflected
        power and then sends it to the GUI window and the CSV file. Some of the
        displayed data is calculated before it is displayed/logged.

@verbatim

The MIT License (MIT)

Copyright (c) 2024 Bird

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

@endverbatim

@file bird_4480_wattmeter_datalogging.py
 
"""
import pyvisa as visa
import csv
import tkinter as tk
from tkinter import font
import math

# Instrument resource string
MY4480 = "USB0::0x1422::0x4480::152256401::INSTR"

# Open the resource manager and instrument
rm = visa.ResourceManager()
my4480 = rm.open_resource(MY4480)

# Open CSV file for data logging
csvfile = open('data_log.csv', 'w', newline='')
fieldnames = [
    'Measurment Band',
    'Forward Average Power (W)',
    'Reflected Average Power (W)',
    'Forward Average Power (dBm)',
    'Reflected Average Power (dBm)',
    'VSWR',
    'Return Loss (dB)',
    'Temp (C)',
    'Measurment Count',
    'TestTime (ms)',
    'System Up Time',
]
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

# Function to convert milliseconds to HH:MM:SS
def ms_to_hhmmss(ms):
    seconds = ms / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Function to convert watts to dBm safely
def watts_to_dbm(watts):
    try:
        watts = float(watts)
        if watts <= 0:
            return 'N/A'
        dbm = 10 * math.log10(watts * 1000)
        return f"{dbm:.2f}"
    except:
        return 'N/A'
    
# Function to convert VSWR to return loss
def vswr_to_return_loss(VSWR):
    try:
        VSWR = float(VSWR)
        if VSWR <= 1:
            return '0'
        Return_Loss = -20 * math.log10((VSWR - 1)/(VSWR + 1))
        return f"{Return_Loss:.2f}"
    except:
        return "N/A"
    
# Function to convert binary band reading to High or Low Band
def band_selection(Band):
    try:
        if Band == 1:
            return 'High Band 25 to 1000 MHz'
        elif Band == 0:
            return 'Low Band 2 to 30 MHz'
    except:
        return 'Error'


# Create the main window
root = tk.Tk()
root.title("Bird Technologies 4480")
root.configure(bg='#062f6e')  # Set background color to blue

# Set a larger, easy-to-read font
default_font = font.Font(family="Helvetica", size=16, weight="bold")
root.option_add("*Font", default_font)

# Add a label on top of the window
title_label = tk.Label(
    root,
    text="4480 Wattmeter",
    bg='#062f6e',
    fg='white',
    font=font.Font(family="Helvetica", size=20, weight="bold", underline=True)
)
title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))

# Variables to hold the readings
band_var = tk.StringVar()
forward_power_var = tk.StringVar()
reflected_power_var = tk.StringVar()
forward_power_dbm_var = tk.StringVar()
reflected_power_dbm_var = tk.StringVar()
vswr_var = tk.StringVar()
return_loss_var = tk.StringVar()
temp_var = tk.StringVar()
test_time_var = tk.StringVar()
iteration_var = tk.StringVar()
system_time_var = tk.StringVar()


# Create labels for the GUI
labels = [
    ("Measurment Band:", band_var),
    ("Forward Average Power (W):", forward_power_var),
    ("Reflected Average Power (W):", reflected_power_var),
    ("Forward Average Power (dBm):", forward_power_dbm_var),
    ("Reflected Average Power (dBm):", reflected_power_dbm_var),
    ("VSWR:", vswr_var),
    ("Return Loss:", return_loss_var),
    ("Temp (C):", temp_var),
    ("Measurment Count:", iteration_var),
    ("Test Time (ms):", test_time_var),
    ("System Up Time:", system_time_var),
]

for idx, (text, var) in enumerate(labels):
    tk.Label(
        root,
        text=text,
        bg='#062f6e',
        fg='white',
        font=default_font
    ).grid(row=idx+1, column=0, sticky='e', padx=10, pady=5)
    tk.Label(
        root,
        textvariable=var,
        bg='#062f6e',
        fg='white',
        font=default_font
    ).grid(row=idx+1, column=1, sticky='w', padx=10, pady=5)

# Initialize iteration count
i = 0

def update_readings():
    global i
    i += 1
    iteration_var.set(str(i))
    SystemTime_ms = int(my4480.query("SYST:TIM?"))  # Queries time in milliseconds
    system_time_str = ms_to_hhmmss(SystemTime_ms)
    system_time_var.set(system_time_str)

    # Fetch readings from the instrument
    forward_power = round(float(my4480.query("FETC:FORW?").strip()), 2)
    reflected_power = round(float(my4480.query("FETC:REFL?").strip()), 2)
    vswr = round(float(my4480.query("FETC:VSWR?").strip()), 2)
    temp = round(float(my4480.query("FETC:TEMP?").strip()), 2)
    TestTime_ms = int(my4480.query("SYST:TIM?")) - SystemTime_ms
    meas_band = int(my4480.query("MEAS:BAND?"))
    
    # Set active measurment band
    band = band_selection(meas_band)

    # Compute dBm values
    forward_power_dbm = watts_to_dbm(forward_power)
    reflected_power_dbm = watts_to_dbm(reflected_power)

    # Compute return loss values
    return_loss = vswr_to_return_loss(vswr)

    # Update GUI labels
    band_var.set(band)
    forward_power_var.set(forward_power)
    reflected_power_var.set(reflected_power)
    forward_power_dbm_var.set(forward_power_dbm)
    reflected_power_dbm_var.set(reflected_power_dbm)
    vswr_var.set(vswr)
    return_loss_var.set(return_loss)
    temp_var.set(temp)
    test_time_var.set(str(TestTime_ms))

    # Log data to CSV
    writer.writerow({
        'Measurment Count': i,
        'System Up Time': system_time_str,
        'Forward Average Power (W)': forward_power,
        'Reflected Average Power (W)': reflected_power,
        'Forward Average Power (dBm)': forward_power_dbm,
        'Reflected Average Power (dBm)': reflected_power_dbm,
        'VSWR': vswr,
        'Return Loss (dB)': return_loss,
        'Temp (C)': temp,
        'TestTime (ms)': TestTime_ms,
        'Measurment Band': band
    })
    csvfile.flush()  # Ensure data is written to the file

    # Schedule the next update
    root.after(1000, update_readings)  # Update every 1 second

def on_closing():
    # Close instrument and resource manager
    my4480.close()
    rm.close()
    # Close CSV file
    csvfile.close()
    root.destroy()

# Start updating readings
update_readings()

# Handle window closing event
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the GUI event loop
root.mainloop()
