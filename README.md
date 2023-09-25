
# HDHomeRun Channel Scanner README

## Overview

This Python script serves as a utility for discovering and scanning channels on SiliconDust HDHomeRun devices. HDHomeRun devices are network-attached TV tuners that allow users to receive over-the-air (OTA) video signals from local broadcast stations. This utility provides a user-friendly interface to identify HDHomeRun devices on your network, select a specific tuner, and then scan for available channels. The results of the scan are saved in a CSV file for further analysis.

### Requirements

•	Python 3.x
•	SiliconDust HDHomeRun device
•	hdhomerun_config utility installed

### Features
1.	Device Discovery: Automatically finds HDHomeRun devices on your network.
2.	Tuner Selection: Allows the user to choose a specific tuner or auto-scan through all tuners.
3.	Channel Scanning: Scans all available frequencies to find channels.
4.	Channel Information: For channels with a strong enough signal to lock onto, the script provides detailed information such as frequency, signal strength, and program listings.
5.	Output to CSV: All the scan data is exported to a CSV file, named dynamically based on the system name and current date and time (24-hour format).

### Output CSV Format

The CSV file has the following columns:
•	Frequency
•	US-Broadcast Channel
•	Lock Status
•	Signal Strength (dBmV)
•	Signal to Noise Quality
•	Symbol Error Quality
•	TSID
•	Program Listings (Program1, Program2, ... up to Program20)

### How to Run
1.	Open a terminal and navigate to the script location.
2.	Run the script: python script_name.py
3.	Follow the on-screen prompts to select a device and tuner.
4.	Wait for the scan to complete.
5.	Check the generated CSV file for the scan results.

### Understanding the Output

•	Frequency: The frequency at which a potential channel was detected.
•	US-Broadcast Channel: The corresponding broadcast channel in the US.
•	Lock Status: Whether the tuner was able to lock onto the signal at this frequency.
•	Signal Strength (dBmV): Strength of the signal received.
•	Signal to Noise Quality: The quality of the signal in terms of its noise level.
•	Symbol Error Quality: The quality of the digital signal.
•	TSID: Transport Stream ID, a unique identifier for the group of channels.
•	Program Listings: Names of the programs or channels available on this frequency.

### Troubleshooting

•	If "No HDHomeRun devices found" is displayed, ensure your device is properly connected to the same network as your computer.
•	If you encounter "resource locked," it means the tuner is being used by another application.

For any issues or further questions, please refer to SiliconDust's official documentation or support forums.

