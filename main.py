# HD Homerun Scan Channels and produce a CSV file of discovered programs
# Version 2.2 2023-09-25 Mark Munger

import os
import csv
import re
import time
from datetime import datetime
import platform
from typing import List, Dict
import openai

USE_LOCAL_TEST_FILE = True  # True for local testing with ScanData.txt, otherwise False

# Constants for discovered program count from HDHR
MIN_PROGRAM = 1
MAX_PROGRAM = 20

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
    except Exception as discover_error:
        print("Error discovering devices:", discover_error)
        return []


# Display a numbered choice menu for devices
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


# parse_results_info function
def parse_results_info(scan_results: List[str]) -> List[Dict[str, str]]:
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


# Query the selected tuner and return lines of scan results
# Modified Query the selected tuner or Auto select tuner
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

        except Exception as query_error:
            print(f"Unexpected error: {query_error}")
            return []

    print("All tuners are either locked or failed to lock. Exiting.")
    return []


def prepare_openai_prompt(filename: str) -> str:
    try:
        with open(filename, 'r') as file:
            file_content = file.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return ""

    prompt = "What city or region is this broadcast TV tuner scan data from. Respond with City and State only"

    # Combine the prompt and the file content
    full_scan_text = re.sub('[^a-zA-Z]', ' ', file_content)
    full_text = f"{prompt}\n{full_scan_text}"

    return full_text


def get_openai_response(prompt: str) -> str:
    # Read the API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")

    if api_key is None:
        print("API key not found in environment variables.")
        return ""

    openai.api_key = api_key

    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=60
        )
        return response.choices[0].text.strip()
    except Exception as error:
        print(f"An error occurred: {error}")
        return ""


# Main program
if __name__ == "__main__":

    # Get system name
    system_name = platform.node()

    # Get current date and time
    current_datetime = datetime.now()
    date_str = current_datetime.strftime("%Y%m%d")
    hour_str = current_datetime.strftime("%H")

    # Generate filename
    filename = f"{system_name}_{date_str}_{hour_str}.CSV"

    try:
        # Open CSV file for output, scan and output data
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

                # Set list of tuners based on selected tuner or AUTO to find an open tuner
                tuners = [mode] if mode != 4 else [0, 1, 2, 3]

                # Query the selected tuner(s), return all scan frequency info from HDHR
                results = query_tuner(device_number, tuners)

            else:
                # Load from a local test file
                with open('ScanData.txt', 'r') as result_file:
                    results = result_file.readlines()

            # Parse the results
            print("Parsing Scan Results")
            parsed_data = parse_results_info(results)

            if not parsed_data:
                print("No valid data parsed.")
                exit()

            # Write Header row to the csv file
            print("Writing header to CSV file")
            header = ['Frequency', 'US-Bcast Channel', 'Lock', 'Signal Strength (dBmV)',
                      'Signal to Noise Quality', 'Symbol Error Quality', 'TSID']

            for i in range(MIN_PROGRAM, MAX_PROGRAM + 1):  # Interate through program headers
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

                for i in range(MIN_PROGRAM, MAX_PROGRAM + 1):  # Interate through program data
                    program_key = f'Program{i}'
                    program_value = data.get(program_key, '')
                    row.append(program_value)

                output_writer.writerow(row)

            print(f"Data successfully written to {filename}")

    except Exception as general_error:  # Will add specific exceptions in future
        print(f"An error occurred: {general_error}")

    # Ask the user if they want to send the scan results to OpenAI
    user_response = input("Send results to OpenAI to determine the city/region? (1 for yes / 2 for no): ")

    # If 1 (yes) then prepare the prompt prepending the question to the data and send to openai
    if user_response == '1':
        full_text = prepare_openai_prompt(filename)
        openai_response = get_openai_response(full_text)
        if openai_response:
            print(f"The city or region is {openai_response}")
        else:
            print("Could not get a response from OpenAI.")
    elif user_response == '2':
        print("Not sending data to OpenAI.")
    else:
        print("Invalid input. Please respond with '1' for yes or '2' for no.")
