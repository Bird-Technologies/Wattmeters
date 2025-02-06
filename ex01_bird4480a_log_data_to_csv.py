"""
Example Description:
        This example samples forward and reflected power, VSWR, and the
        meter's temperature, calculates return loss for a specified duration
        and logs to time-stamped *.csv file. 

@verbatim

The MIT License (MIT)

Copyright (c) 2025 Bird

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

@file ex01_bird4480a_log_data_to_csv.py
 
"""

import pyvisa as visa
import csv
import time
import math

# Function to convert VSWR to return loss
def vswr_to_return_loss(VSWR:float) -> float:
    """Converts the VSWR value to return loss in dB.

    Args:
        VSWR (float): VSWR value. 

    Returns:
        float: Computed return loss in dB. If there is a problem with
        the math on the input value, the 9.99e+37 value will be returned
        to indicate the error condition.
    """
    try:
        VSWR = float(VSWR)
        if VSWR <= 1:
            return 9.999e+37
        Return_Loss = -20 * math.log10((VSWR - 1)/(VSWR + 1))
        return f"{Return_Loss:.2f}"
    except:
        return 9.999e+37

    
# Create a file to save data to
output_data_path = time.strftime("C:\\Temp\\rf_power_data_%Y-%m-%d_%H-%M-%S.csv")

# Instrument resource string
MY4480 = "USB0::0x1422::0x4480::152256401::INSTR"

# Open the resource manager and instrument
rm = visa.ResourceManager()
my4480 = rm.open_resource(MY4480)
my4480.write("*RST")
my4480.write("*CLS")
time.sleep(1.5)

# Set the band based on the frequency: 0 for 2-30 MHz, 1 for 30-1000 MHz
my4480.write("MEAS:BAND 0")
time.sleep(1.5)

# Define the header for the CSV
header = ['Time (s)', 'Fwd_Power (W)', 'Refl_Power (W)', 'VSWR', "Return Loss (dB)", "Temperature (deg C)"]

# Write data to CSV
with open(output_data_path, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)  # Write the header

    log_duration = 1800.0
    elapsed_time = 0.0
    print_interval_flag = 60.0

    t1 = time.time() # Start the timer...
    print("Testing started....")

    while elapsed_time < log_duration:
        # Loop to for the expected duration and log data points to file
        # Fetch readings from the instrument
        forward_power = round(float(my4480.query("FETC:FORW?").strip()), 2)
        reflected_power = round(float(my4480.query("FETC:REFL?").strip()), 2)
        vswr = round(float(my4480.query("FETC:VSWR?").strip()), 2)
        rl = vswr_to_return_loss(vswr)
        temp = round(float(my4480.query("FETC:TEMP?").strip()), 2)

        t2 = time.time()
        elapsed_time = t2-t1
        etime = f"{elapsed_time:0.3f}"

        data = [etime, forward_power, reflected_power, vswr, rl, temp]

        writer.writerow(data)   # Write the data

        if elapsed_time > print_interval_flag:
            print(f"Elapsed time: {t2-t1:0.3f} s")
            print_interval_flag += 60.0

    print("Testing ended!!!")
    
my4480.close()
rm.close()
