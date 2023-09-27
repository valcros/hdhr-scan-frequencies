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

USE_LOCAL_TEST_FILE = False  # True for local testing with ScanData.txt, otherwise False

# Constants for discovered program count from HDHR
MIN_PROGRAM = 1
MAX_PROGRAM = 20

# Check hdhomerun_config before anything else
# if not os.path.exists("hdhomerun_config"):
#     print("Error: hdhomerun_config not found")
#     exit()


# Discover HDHomeRun devices
def discover_devices() -> List[str]:
    """
    Discover Silicon Dust HDHomeRun devices on the local network.

    This function uses the 'hdhomerun_config' command to discover HDHomeRun devices
    connected to the local network. It returns a list of discovered devices as returned
    by the hdhomerun_config utility which can be downloaded here:
    https://www.silicondust.com/support/downloads/

    Returns:
        List[str]: A list of discovered HDHomeRun devices as strings.

    Raises:
        Exception: If an error occurs during the discovery process.

    Note:
        The function filters out devices with the message 'no devices found' to
        prevent attempting to use that as a device id

    Example:
        >>> discovered = discover_devices()
        >>> print(discovered)
        ['hdhomerun device 12345678 found at 192.168.1.100']
    """
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
    """
    Select an HDHomeRun device from the discovered devices.

    This function displays a menu of discovered HDHomeRun devices and allows the user
    to choose one. If no devices are found initially, it provides an option to retry.

    Returns:
        str: The selected HDHomeRun device as a string.

    Note:
        If there are multiple discovered devices, the user is prompted to enter the
        device number to make a selection. The function handles automatic retries if
        no devices are found initially.

    Example:
        >>> selected = select_device()
        Select an HDHomeRun device:
        1) hdhomerun device 12345678 found at 192.168.1.100
        2) hdhomerun device 98765432 found at 192.168.1.101
        3) Rediscover devices
        Enter the device number: 2
        >>> print(selected)
        'hdhomerun device 98765432 found at 192.168.1.101'
    """
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
    """
    Parse the frequency and US-Bcast Channel from a line of HDHomeRun scan data.

    This function takes a line of scan data from an HDHomeRun device and extracts
    the frequency and US-Bcast Channel information. It returns a dictionary containing
    these values.

    Args:
        line (str): A line of scan data from an HDHomeRun device.

    Returns:
        Dict[str, str]: A dictionary containing the parsed frequency and US-Bcast Channel.

    Example:
        >>> data_line = "SCANNING: 569000000 (us-bcast:23)"
        >>> result = parse_frequency(data_line)
        >>> print(result)
        {'Frequency': '569000000', 'US-Bcast Channel': '23'}
    """
    parts = line.split()
    if len(parts) >= 2:
        return {"Frequency": parts[1], "US-Bcast Channel": get_us_bcast(line)}
    return {}


def get_us_bcast(line: str) -> str:
    """
    Extract the US-Bcast Channel from a line of HDHomeRun scan data.

    This function searches for the US-Bcast Channel information in the provided line
    of HDHomeRun scan data using a regular expression. If found, it returns the channel
    as a string. If not found, it returns an empty string.

    Args:
        line (str): A line of scan data from an HDHomeRun device.

    Returns:
        str: The extracted US-Bcast Channel as a string, or an empty string if not found.

    Example:
        >>> data_line = "SCANNING: 569000000 (us-bcast:23)"
        >>> result = get_us_bcast(data_line)
        >>> print(result)
        '23'
    """
    match = re.search(r"us-bcast:(\d+)", line)
    if match:
        return match.group(1)
    return ""


# Parse lock status
def parse_lock(line: str) -> Dict[str, str]:
    """
    Parse lock status information from a line of HDHomeRun scan data.

    This function extracts lock status details, including Lock, Signal Strength (dBmV),
    Signal to Noise Quality, and Symbol Error Quality, from a line of scan data obtained
    from an HDHomeRun device. It uses a regular expression to match and capture these
    details if they are present in the provided line.

    Args:
        line (str): A line of scan data from an HDHomeRun device.

    Returns:
        dict: A dictionary containing lock status information with the following keys:
            - 'Lock': The lock status ('none' or 'some').
            - 'Signal Strength (dBmV)': The signal strength in dBmV.
            - 'Signal to Noise Quality': The signal-to-noise quality.
            - 'Symbol Error Quality': The symbol error quality.

    Example:
        >>> data_line = "LOCK: none (ss=-20 snq=42 seq=100)"
        >>> result = parse_lock(data_line)
        >>> print(result)
        {
            'Lock': 'none',
            'Signal Strength (dBmV)': '-20',
            'Signal to Noise Quality': '42',
            'Symbol Error Quality': '100'
        }
    """
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
    """
    Parse TSID (Transport Stream ID) information from a line of HDHomeRun scan data.

    This function extracts the TSID from a line of scan data obtained from an HDHomeRun
    device. The TSID represents the Transport Stream ID, which can be useful for identifying
    specific broadcasts or channels.

    Args:
        line (str): A line of scan data from an HDHomeRun device.

    Returns:
        dict: A dictionary containing the TSID information with the following key:
            - 'TSID': The Transport Stream ID.

    Example:
        >>> data_line = "TSID: 12345"
        >>> result = parse_tsid(data_line)
        >>> print(result)
        {'TSID': '12345'}
    """
    parts = line.split()
    if len(parts) == 2:
        return {"TSID": parts[1]}
    return {}


# Parse program
def parse_program(line: str) -> Dict[str, str]:
    """
    Parse program information from a line of HDHomeRun scan data.

    This function extracts program information from a line of scan data obtained from
    an HDHomeRun device. It splits the line into program number and program name and
    returns a dictionary with a key-value pair representing the program.

    Args:
        line (str): A line of scan data from an HDHomeRun device.

    Returns:
        dict: A dictionary containing program information with keys in the format
        'ProgramX' (e.g., 'Program1', 'Program2') and values as program names.

    Example:
        >>> data_line = "PROGRAM 1: Example Program 1"
        >>> result = parse_program(data_line)
        >>> print(result)
        {'Program1': 'Example Program 1'}
    """
    parts = line.split(":")
    if len(parts) == 2:
        program_num = parts[0].split()[-1]
        program_name = parts[1].strip()
        return {f"Program{program_num}": program_name}
    return {}


# Update lock info
def update_lock_info(lock_info: Dict, new_data: Dict) -> None:
    """
    Update a lock information dictionary with new data.

    This function takes an existing lock information dictionary and updates it with new
    data. It's commonly used to combine lock information from different sources.

    Args:
        lock_info (dict): The existing lock information dictionary to be updated.
        new_data (dict): A dictionary containing new lock information to be added.

    Returns:
        None: This function doesn't return a value. It updates the `lock_info` dictionary
        in place.

    Example:
        >>> existing_info = {'Lock': 'Locked', 'Signal Strength (dBmV)': '10.5'}
        >>> new_data = {'Signal to Noise Quality': '25', 'Symbol Error Quality': '0'}
        >>> update_lock_info(existing_info, new_data)
        >>> print(existing_info)
        {'Lock': 'Locked', 'Signal Strength (dBmV)': '10.5',
         'Signal to Noise Quality': '25', 'Symbol Error Quality': '0'}
    """
    lock_info.update(new_data)


# parse_results_info function
def parse_results_info(scan_results: List[str]) -> List[Dict[str, str]]:
    """
    Parse scan results from an HDHomeRun device.

    This function takes a list of scan results lines from an HDHomeRun device and parses
    them to extract information about frequencies, locks, TSIDs, and programs.

    Args:
        scan_results (List[str]): A list of strings representing the scan results.

    Returns:
        List[Dict[str, str]]: A list of dictionaries where each dictionary contains
        information about a frequency, including its lock status, TSID, and programs.

    Example:
        >>> scan_results = [
        ...     'SCANNING: 489000000 (us-bcast:3)',
        ...     'LOCK: 8vsb (ss=87 snq=100 seq=100)',
        ...     'TSID: 12345',
        ...     'PROGRAM 1: ProgramName1',
        ...     'PROGRAM 2: ProgramName2',
        ... ]
        >>> parsed_data = parse_results_info(scan_results)
        >>> print(parsed_data)
        [{'Frequency': '489000000', 'US-Bcast Channel': '3',
          'Lock': '8vsb', 'Signal Strength (dBmV)': '87',
          'Signal to Noise Quality': '100', 'Symbol Error Quality': '100',
          'TSID': '12345', 'Program1': 'ProgramName1', 'Program2': 'ProgramName2'}]
    """
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
    """
    Query HDHomeRun tuners for scan results.

    This function queries HDHomeRun tuners to perform channel scans and retrieve scan results.
    It iterates through the provided list of tuners, sends scan commands, and returns the scan results.

    Args:
        device_id (str): The unique identifier of the HDHomeRun device.
        tuners (List[int]): A list of tuner numbers to query.

    Returns:
        List[str]: A list of strings representing the scan results.

    Example:
        >>> device_id = "192.168.254.18"
        >>> tuners = [0, 1, 2, 3]
        >>> scan_results = query_tuner(device_id, tuners)
        >>> for result in scan_results:
        ...     print(result)
        'SCANNING: 489000000 (us-bcast:3)'
        'LOCK: 8vsb (ss=87 snq=100 seq=100)'
        'TSID: 12345'
        'PROGRAM 1: ProgramName1'
        'PROGRAM 2: ProgramName2'
    """
    for tuner in tuners:
        try:
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


# Extract the program (Station) names from the scan data
def extract_programs(data: List[str]) -> List[str]:
    """
    Extract program names from scan results.

    This function extracts program (station) names from a list of scan results. It looks for lines that start with 'PROGRAM',
    splits those lines by ':' and retrieves the text after the colon, stripping any leading or trailing whitespace.

    Args:
        data (List[str]): A list of strings representing scan results.

    Returns:
        List[str]: A list of program (Station) names extracted from the scan results.

    Example:
        >>> scan_results = [
        ...     'PROGRAM 1: ProgramName1',
        ...     'PROGRAM 2: ProgramName2',
        ...     'LOCK: 8vsb (ss=87 snq=100 seq=100)',
        ...     'TSID: 12345',
        ... ]
        >>> program_names = extract_programs(scan_results)
        >>> for program_name in program_names:
        ...     print(program_name)
        'ProgramName1'
        'ProgramName2'
    """
    program_lines = []
    for line in data:
        if line.startswith('PROGRAM'):
            program_info = line.split(': ', 1)
            if len(program_info) == 2:
                program_lines.append(program_info[1].strip())
    return program_lines

def prepare_openai_prompt(list_of_stations: str) -> str:
    """
    Prepare a prompt for OpenAI based on a list of broadcast TV stations.

    This function takes a list of broadcast TV station names and prepares a prompt for OpenAI. The prompt includes a
    question asking for the city or region associated with the scan data and appends the list of station names to it.

    Args:
        list_of_stations (str): A string containing a list of broadcast TV station names.

    Returns:
        str: A prompt string ready to be sent to OpenAI.

    Example:
        >>> station_list = "Station A, Station B, Station C"
        >>> prompt = prepare_openai_prompt(station_list)
        >>> print(prompt)
        "What city or region is this broadcast TV tuner scan data from. Respond with City and State only\nStation A, Station B, Station C"
    """
    prompt = "What city or region is this broadcast TV tuner scan data from. Respond with City and State only"
    full_text = f"{prompt}\n{list_of_stations}"
    return full_text


def get_openai_response(prompt: str) -> str:
    """
    Retrieve a response from OpenAI's GPT-3.5 Turbo model based on a given prompt.

    This function sends a prompt to OpenAI's GPT-3.5 Turbo model and retrieves a response. It uses the API key
    obtained from the environment variables to authenticate the request.

    Args:
        prompt (str): The prompt to be sent to the GPT-3.5 Turbo model.

    Returns:
        str: The text response generated by the model.

    Example:
        >>> prompt = "What is the meaning of life?"
        >>> response = get_openai_response(prompt)
        >>> print(response)
        "The meaning of life is a philosophical question with no single answer..."
    """
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


def main():
    """
    Main program for HD Homerun Scan Channels.

    This program performs the following steps:
    1. Retrieves the system name and current date-time.
    2. Generates a filename for the CSV output.
    3. Initializes empty lists for parsed_data and results.
    4. Depending on the value of USE_LOCAL_TEST_FILE, it either:
       - Selects an HDHomeRun device and retrieves scan results from it, or
       - Loads scan results from a local test file.
    5. Parses the scan results.
    6. Asks the user if they want to save the scan results to a CSV file.
    7. If the user chooses to save, it writes the parsed data to the CSV file.
    8. If the user chooses not to save, it displays the parsed data.
    9. Asks the user if they want to send the scan results to OpenAI to determine the city/region.

    Note:
    - This program assumes the presence of functions such as select_device(), select_tuner_mode(), query_tuner(),
      and others which are used in the main logic but are defined elsewhere in the code.

    Returns:
        None
    """
    # Get system name
    system_name = platform.node()

    # Get current date and time
    current_datetime = datetime.now()
    date_str = current_datetime.strftime("%Y%m%d")
    hour_str = current_datetime.strftime("%H")

    # Generate filename
    filename = f"{system_name}_{date_str}_{hour_str}.CSV"

    # Initialize an empty list for parsed_data and results
    parsed_data = []
    results = []

    try:
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

    except Exception as general_error:  # Will add specific exceptions in future
        print(f"An error occurred: {general_error}")

    # Ask the user if they want to save the scan results to a CSV file
    user_response = input("Save results to a CSV file? (1 for yes / 2 for no): ")

    if user_response == '1':
        try:
            with open(filename, 'w', newline='') as output_file:
                output_writer = csv.writer(output_file)
                # Write header and parsed data to the file
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

                print(f"Data successfully written to '{filename}'.")
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")

    elif user_response == '2':
        print("Displaying the parsed data:")
        for data in parsed_data:
            print(data)
    else:
        print("Invalid input. Please respond with '1' for yes or '2' for no.")

    # Ask the user if they want to send the scan results to OpenAI
    # print(results)
    user_response = input("Send results to OpenAI to determine the city/region? (1 for yes / 2 for no): ")

    if user_response == '1' and results:
        stations_list = extract_programs(results)
        stations_string = ' '.join(stations_list) + '\n'
        # print (stations_string)
        full_text = prepare_openai_prompt(stations_string)
        openai_response = get_openai_response(full_text)
        if openai_response:
            print(f"The city or region is {openai_response}")
        else:
            print("Could not get a response from OpenAI.")
    elif user_response == '2':
        print("Not sending data to OpenAI.")
    else:
        print("Invalid input. Please respond with '1' for yes or '2' for no.")


if __name__ == "__main__":
    main()
