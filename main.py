# HD Homerun Scan Channels and produce a CSV file of discovered programs
# Version 2.0 2023-09-24 Mark Munger

import os
import csv
import re
import time
from datetime import datetime
import platform
from typing import List, Dict

# Check hdhomerun_config before anything else
# if not os.path.exists("hdhomerun_config"):
#     print("Error: hdhomerun_config not found")
#     exit()


# Discover HDHomeRun devices
def discover_devices() -> List[str]:
    try:
        result = os.popen("hdhomerun_config discover -4").read()
        discovered_devices = result.strip().split("\n")
        # Filter out 'no devices found'
        return [dev for dev in discovered_devices if "no devices found" not in dev.lower()]
    except Exception as e:
        print("Error discovering devices:", e)
        return []


# Display a numbered choice menu for devices
# Modified Display a numbered choice menu for devices
def select_device() -> str:
    retry_count = 0  # Initialize a counter for automatic retries

    while True:
        discovered_devices = discover_devices()

        if discovered_devices:
            print("Select an HDHomeRun device:")
            for i, device in enumerate(discovered_devices):
                print(f"{i + 1}) {device}")
            print(f"{len(discovered_devices) + 1}) Rediscover devices")  # Add Rediscovery option

            choice = int(input("Enter the device number: ")) - 1

            if 0 <= choice < len(discovered_devices):
                return discovered_devices[choice]
            elif choice == len(discovered_devices):  # User selected Rediscovery option
                continue
            else:
                print("Invalid choice.")

        else:
            if retry_count < 1:  # Allow one automatic retry
                print("No HDHomeRun devices found. Retrying in 3 seconds...")
                time.sleep(3)  # Wait for 3 seconds
                retry_count += 1  # Increment the retry counter
                continue
            else:
                print("No HDHomeRun devices found after retry. Exiting.")
                return ""

        # Add an option to rediscover devices
        retry = input("Would you like to discover devices again? (y/n): ")
        if retry.lower() != 'y':
            return ""


# Prompt the user to choose a tuner or Auto mode
def select_tuner_mode() -> int:
    print("Select a tuner or Auto mode:")
    print("0) Tuner 0")
    print("1) Tuner 1")
    print("2) Tuner 2")
    print("3) Tuner 3")
    print("4) Auto mode (Try all tuners)")
    choice = int(input("Enter the mode number: "))
    if 0 <= choice <= 4:
        return choice
    else:
        print("Invalid choice.")
        return -1


# Parse frequency and channel
def parse_frequency(line: str) -> Dict[str, str]:
    parts = line.split()
    if len(parts) >= 2:
        return {"Frequency": parts[1], "US-Bcast Channel": get_us_bcast(line)}
    return {}


def get_us_bcast(line: str) -> str:
    match = re.search(r"us-bcast:(\d+)", line)
    if match:
        return match.group(1)
    return ""


# Parse lock status
def parse_lock(line: str) -> Dict[str, str]:
    parts = re.match(r"LOCK: (\w+) \(ss=(\d+) snq=(\d+) seq=(\d+)\)", line)
    if parts:
        return {
            "Lock": parts.group(1),
            "Signal Strength (dBmV)": parts.group(2),
            "Signal to Noise Quality": parts.group(3),
            "Symbol Error Quality": parts.group(4)
        }
    return {}


# Parse TSID
def parse_tsid(line: str) -> Dict[str, str]:
    parts = line.split()
    if len(parts) == 2:
        return {"TSID": parts[1]}
    return {}


# Parse program
def parse_program(line: str) -> Dict[str, str]:
    parts = line.split(":")
    if len(parts) == 2:
        program_num = parts[0].split()[-1]
        program_name = parts[1].strip()
        return {f"Program{program_num}": program_name}
    return {}


# Update lock info
def update_lock_info(lock_info: Dict, new_data: Dict) -> None:
    lock_info.update(new_data)


# parse_lock_info function
# Modified the parse_lock_info function to concatenate information on a single line
def parse_lock_info(scan_results: List[str]) -> List[Dict[str, str]]:
    parsed_data = []  # Initialize an empty list to store parsed data
    frequency_info = {}  # Initialize a dictionary to store information for the current frequency

    for line in scan_results:
        if line.startswith('SCANNING:'):
            if frequency_info:  # Check if there's existing frequency info
                parsed_data.append(frequency_info)  # Append the existing info to parsed_data
            frequency_info = parse_frequency(line)  # Start new frequency info

        elif line.startswith('LOCK'):
            frequency_info.update(parse_lock(line))

        elif line.startswith('TSID'):
            frequency_info.update(parse_tsid(line))

        elif line.startswith('PROGRAM'):
            frequency_info.update(parse_program(line))

    if frequency_info:  # Add the last frequency info
        parsed_data.append(frequency_info)

    return parsed_data


# Query the selected tuner or tuners
# Modified Query the selected tuner or Auto select tuners
def query_tuner(device_id: str, tuners: List[int]) -> List[str]:
    for tuner in tuners:
        try:
            # command = "hdhomerun_config 192.168.254.18 scan 3"
            # command = "hdhomerun_config 10.216.0.18 scan 2"
            command = f"hdhomerun_config {device_id} scan {tuner}"
            print(f"Querying tuner {tuner} on device {device_id}...")
            print(f"executing this command with os.open {command}")

            with os.popen(command) as result_stream:
                lines = result_stream.readlines()

                if any("ERROR: resource locked" in line for line in lines):
                    print(f"Tuner {tuner} on device {device_id} is locked by another resource. Skipping to next tuner.")
                    continue

                if "LOCK: none" in lines:
                    print(f"Tuner {tuner} on device {device_id} failed to lock")
                    return []

                print(f"Query completed for tuner {tuner} on device {device_id}.")
                return lines

        except OSError as e:
            print(f"Error executing command: {e}")
            return []

        except ValueError:
            print(f"Invalid tuner number: {tuner}")
            return []

        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    print("All tuners are either locked or failed to lock. Exiting.")
    return []


# Constants for program count
MIN_PROGRAM = 1
MAX_PROGRAM = 20

# Main program
if __name__ == "__main__":
    USE_LOCAL_TEST_FILE = False  # Set this to True for local testing, otherwise False

    # Get system name
    system_name = platform.node()

    # Get current date and time
    current_datetime = datetime.now()
    date_str = current_datetime.strftime("%Y%m%d")
    hour_str = current_datetime.strftime("%H")

    # Generate filename
    filename = f"{system_name}_{date_str}_{hour_str}.CSV"

    try:
        # Use 'with' for better resource management
        with open(filename, 'w', newline='') as output_file:
            output_writer = csv.writer(output_file)

            if not USE_LOCAL_TEST_FILE:
                # Select the HDHomeRun Device
                selected_device = select_device()

                if not selected_device:
                    print("Exiting the program.")
                    exit()

                # Extract the 8-digit device number from the selected device
                device_number = selected_device.split()[2]

                # Select a tuner or Auto mode
                mode = select_tuner_mode()
                if mode == -1:
                    exit()

                # Set list of tuners based on selected mode
                tuners = [mode] if mode != 4 else [0, 1, 2, 3]

                # Query the selected tuner(s), return all scan frequency info from HDHR
                results = query_tuner(device_number, tuners)

            else:
                # Load from a local test file
                with open('ScanData.txt', 'r') as result_file:
                    results = result_file.readlines()

            # Parse the results
            print("Parsing Scan Results")
            parsed_data = parse_lock_info(results)

            if not parsed_data:
                print("No valid data parsed.")
                exit()

            # Write Header row to the csv file
            print("Writing header to CSV file")
            header = ['Frequency', 'US-Bcast Channel', 'Lock', 'Signal Strength (dBmV)',
                      'Signal to Noise Quality', 'Symbol Error Quality', 'TSID']

            for i in range(MIN_PROGRAM, MAX_PROGRAM + 1):  # Use constants for loop range
                header.append(f'Program{i}')

            output_writer.writerow(header)

            # Iterate through the parsed_data and write rows to the CSV file
            print("Iterating through the parsed_data and writing rows to the CSV file")
            for data in parsed_data:
                row = [
                    data.get('Frequency', ''),
                    data.get('US-Bcast Channel', ''),
                    data.get('Lock', ''),
                    data.get('Signal Strength (dBmV)', ''),
                    data.get('Signal to Noise Quality', ''),
                    data.get('Symbol Error Quality', ''),
                    data.get('TSID', '')
                ]

                for i in range(MIN_PROGRAM, MAX_PROGRAM + 1):  # Use constants for loop range
                    program_key = f'Program{i}'
                    program_value = data.get(program_key, '')
                    row.append(program_value)

                output_writer.writerow(row)

            print("Data successfully written to 'output.csv'.")

    except Exception as e:  # Consider catching specific exceptions
        print(f"An error occurred: {e}")

    # Close the CSV file
    output_file.close()
