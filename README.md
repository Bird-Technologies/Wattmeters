# Wattmeters
 Examples and details for automating wattmeter measurements. 

 ## Directory

* **[bird_4480_wattmeter_datalogging.py](./bird_4480_wattmeter_datalogging.py)**  
This example acts as a PC-based, graphical tool that interacts with the Bird 4480A Digital Wattmeter over the USB bus using VISA. The program sends SCPI comands to the 4480 and gets a responce every second. It then takes the collected data such as forward and reflected power and then sends it to the GUI window and the CSV file. Some of the displayed data is calculated before it is displayed/logged.

