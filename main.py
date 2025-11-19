# HD Homerun Scan Channels and produce a CSV file of discovered programs
# Version 3.0 2025-11-19 Enhanced with comprehensive error handling and logging

import os
import csv
import re
import time
import sys
import shutil
import argparse
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
import platform
from typing import List, Dict, Optional, Tuple
import openai

# Version information
VERSION = "3.0"
VERSION_DATE = "2025-11-19"

# Setup logging
logger = logging.getLogger(__name__)

# Constants for discovered program count from HDHR
MIN_PROGRAM = 1
MAX_PROGRAM = 20

# Signal quality validation ranges
MIN_SIGNAL_QUALITY = 0
MAX_SIGNAL_QUALITY = 100


# Custom Exception Classes
class HDHRConfigNotFoundError(Exception):
    """Raised when hdhomerun_config utility is not found."""
    pass


class DeviceDiscoveryError(Exception):
    """Raised when device discovery fails."""
    pass


class TunerLockError(Exception):
    """Raised when tuner fails to lock."""
    pass


class InvalidInputError(Exception):
    """Raised when user input is invalid."""
    pass


def setup_logging(debug: bool = False) -> None:
    """
    Setup logging configuration with log rotation.

    Args:
        debug (bool): Enable debug level logging if True.
    """
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))

    # File handler with rotation (5MB max per file, keep 5 backup files)
    # This prevents unlimited log growth - max ~25MB total
    file_handler = RotatingFileHandler(
        'hdhr_scan.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=[console_handler, file_handler]
    )


def check_hdhomerun_config() -> bool:
    """
    Check if hdhomerun_config utility is available in the system PATH.

    Returns:
        bool: True if hdhomerun_config is found, False otherwise.

    Raises:
        HDHRConfigNotFoundError: If hdhomerun_config is not found in PATH.
    """
    if shutil.which("hdhomerun_config") is None:
        logger.error("hdhomerun_config utility not found in system PATH")
        raise HDHRConfigNotFoundError(
            "hdhomerun_config utility is required but not found. "
            "Please install from https://www.silicondust.com/support/downloads/"
        )
    logger.debug("hdhomerun_config utility found in PATH")
    return True


def validate_signal_quality(value: int, field_name: str) -> bool:
    """
    Validate that signal quality values are within expected range.

    Args:
        value (int): The signal quality value to validate.
        field_name (str): Name of the field for logging purposes.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not (MIN_SIGNAL_QUALITY <= value <= MAX_SIGNAL_QUALITY):
        logger.warning(f"{field_name} value {value} outside expected range "
                      f"[{MIN_SIGNAL_QUALITY}-{MAX_SIGNAL_QUALITY}]")
        return False
    return True


# Discover HDHomeRun devices
def discover_devices(quiet: bool = False) -> List[str]:
    """
    Discover Silicon Dust HDHomeRun devices on the local network.

    This function uses the 'hdhomerun_config' command to discover HDHomeRun devices
    connected to the local network. It returns a list of discovered devices as returned
    by the hdhomerun_config utility which can be downloaded here:
    https://www.silicondust.com/support/downloads/

    Args:
        quiet (bool): If True, suppress progress output (for automation).

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
        # Provide user feedback before starting (unless quiet mode)
        if not quiet:
            print("🔍 Searching for HDHomeRun devices on your network...")
            print("   (This may take up to 10 seconds)\n")

        logger.debug("Attempting to discover HDHomeRun devices")
        result = subprocess.run(
            ["hdhomerun_config", "discover", "-4"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"Device discovery failed with return code {result.returncode}")
            logger.debug(f"stderr: {result.stderr}")
            raise DeviceDiscoveryError(f"Discovery command failed: {result.stderr}")

        discovered_devices = result.stdout.strip().split("\n")
        # Filter out 'no devices found' and empty lines
        devices = [dev for dev in discovered_devices
                  if dev and "no devices found" not in dev.lower()]

        logger.info(f"Discovered {len(devices)} HDHomeRun device(s)")

        # Provide feedback on results (unless quiet mode)
        if not quiet:
            if len(devices) == 0:
                print("   → No devices found\n")
            elif len(devices) == 1:
                print(f"   → Found 1 device\n")
            else:
                print(f"   → Found {len(devices)} devices\n")

        return devices

    except subprocess.TimeoutExpired:
        logger.error("Device discovery timed out after 10 seconds")
        raise DeviceDiscoveryError("Device discovery timed out")
    except FileNotFoundError:
        logger.error("hdhomerun_config command not found")
        raise HDHRConfigNotFoundError("hdhomerun_config utility not found")
    except Exception as discover_error:
        logger.error(f"Unexpected error during device discovery: {discover_error}", exc_info=True)
        raise DeviceDiscoveryError(f"Device discovery failed: {discover_error}")


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
        try:
            discovered_devices = discover_devices()

            if discovered_devices:
                logger.info("Displaying device selection menu")
                print("\nSelect an HDHomeRun device:")
                for i, device in enumerate(discovered_devices):
                    print(f"{i + 1}) {device}")
                print(f"{len(discovered_devices) + 1}) Rediscover devices")

                while True:
                    try:
                        user_input = input("\nEnter the device number: ").strip()
                        choice = int(user_input) - 1

                        if 0 <= choice < len(discovered_devices):
                            selected = discovered_devices[choice]
                            logger.info(f"User selected device: {selected}")
                            return selected
                        elif choice == len(discovered_devices):  # User selected Rediscovery option
                            logger.info("User requested device rediscovery")
                            break
                        else:
                            logger.warning(f"Invalid device choice: {choice + 1}")
                            print(f"Invalid choice. Please enter a number between 1 and {len(discovered_devices) + 1}")
                    except ValueError:
                        logger.warning(f"Non-numeric input received: {user_input}")
                        print("Invalid input. Please enter a number.")
                    except KeyboardInterrupt:
                        logger.info("User cancelled device selection")
                        print("\nOperation cancelled by user.")
                        return ""

            else:
                if retry_count < 1:  # Allow one automatic retry
                    logger.info("No devices found, retrying in 3 seconds")
                    print("No HDHomeRun devices found. Retrying in 3 seconds...")
                    time.sleep(3)
                    retry_count += 1
                    continue
                else:
                    logger.warning("No devices found after retry")
                    print("No HDHomeRun devices found after retry.")
                    retry_input = input("Would you like to discover devices again? (y/n): ").strip().lower()
                    if retry_input == 'y':
                        logger.info("User requested manual retry")
                        continue
                    else:
                        logger.info("User chose to exit after no devices found")
                        return ""

        except DeviceDiscoveryError as e:
            logger.error(f"Device discovery error: {e}")
            print(f"Error during device discovery: {e}")
            return ""
        except KeyboardInterrupt:
            logger.info("User cancelled device selection")
            print("\nOperation cancelled by user.")
            return ""

# Prompt the user to choose a tuner or Auto mode
def select_tuner_mode() -> int:
    """
    Prompt user to select a specific tuner or auto mode.

    Returns:
        int: Selected tuner number (0-3) or 4 for auto mode, -1 on error.

    Raises:
        InvalidInputError: If input validation fails after retries.
    """
    logger.info("Displaying tuner selection menu")
    print("\nSelect a tuner or Auto mode:")
    print("0) Tuner 0")
    print("1) Tuner 1")
    print("2) Tuner 2")
    print("3) Tuner 3")
    print("4) Auto mode (Try all tuners)")

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            user_input = input("\nEnter the mode number: ").strip()
            choice = int(user_input)

            if 0 <= choice <= 4:
                logger.info(f"User selected tuner mode: {choice}")
                return choice
            else:
                logger.warning(f"Invalid tuner choice: {choice}")
                print(f"Invalid choice. Please enter a number between 0 and 4.")

        except ValueError:
            logger.warning(f"Non-numeric input received: {user_input}")
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            logger.info("User cancelled tuner selection")
            print("\nOperation cancelled by user.")
            return -1

    logger.error(f"Failed to get valid input after {max_attempts} attempts")
    print(f"Too many invalid attempts. Exiting.")
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
    # Updated regex to handle negative signal strength values
    parts = re.match(r"LOCK: (\w+) \(ss=(-?\d+) snq=(\d+) seq=(\d+)\)", line)
    if parts:
        lock_data = {
            "Lock": parts.group(1),
            "Signal Strength (dBmV)": parts.group(2),
            "Signal to Noise Quality": parts.group(3),
            "Symbol Error Quality": parts.group(4)
        }

        # Validate signal quality values
        try:
            snq = int(parts.group(3))
            seq = int(parts.group(4))
            validate_signal_quality(snq, "Signal to Noise Quality")
            validate_signal_quality(seq, "Symbol Error Quality")
        except ValueError as e:
            logger.warning(f"Failed to validate signal quality values: {e}")

        logger.debug(f"Parsed lock data: {lock_data}")
        return lock_data

    logger.debug(f"Failed to parse lock information from line: {line}")
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
def query_tuner(device_id: str, tuners: List[int], quiet: bool = False) -> List[str]:
    """
    Query HDHomeRun tuners for scan results.

    This function queries HDHomeRun tuners to perform channel scans and retrieve scan results.
    It iterates through the provided list of tuners, sends scan commands, and returns the scan results.

    Args:
        device_id (str): The unique identifier of the HDHomeRun device.
        tuners (List[int]): A list of tuner numbers to query.
        quiet (bool): If True, suppress progress output (for automation).

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
            logger.info(f"Querying tuner {tuner} on device {device_id}")
            if not quiet:
                print(f"\n📡 Scanning tuner {tuner} on device {device_id}...")
                print("   This will take 3-5 minutes. Progress shown below:")
                print()

            # Use Popen for real-time progress output
            process = subprocess.Popen(
                ["hdhomerun_config", device_id, "scan", str(tuner)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            lines = []
            scan_count = 0
            lock_count = 0
            current_channel = ""

            # Read output line by line for real-time progress
            try:
                for line in iter(process.stdout.readline, ''):
                    if not line:
                        break

                    line = line.strip()
                    if line:
                        lines.append(line)

                    # Show progress for each frequency scanned (unless quiet)
                    if line.startswith('SCANNING:'):
                        match = re.search(r'(\d+) \(us-bcast:(\d+)\)', line)
                        if match:
                            current_channel = match.group(2)
                            scan_count += 1
                            # Update on same line for cleaner output
                            if not quiet:
                                print(f"\r   Scanning: Channel {current_channel} ({scan_count} frequencies checked)     ", end='', flush=True)

                    elif line.startswith('LOCK:') and 'none' not in line:
                        lock_count += 1
                        # New line for lock success
                        if not quiet:
                            print(f"\r   ✅ Locked: Channel {current_channel} (Total locks: {lock_count})             ")

                # Wait for process to complete
                process.wait(timeout=300)

            except subprocess.TimeoutExpired:
                process.kill()
                logger.error(f"Tuner {tuner} scan timed out after 5 minutes")
                print(f"\n\n⏱️  Error: Tuner {tuner} scan timed out. Trying next tuner.")
                continue

            # Final status update
            if not quiet:
                print(f"\r   Scan progress: {scan_count} frequencies checked                                ")

            # Check for resource locked error
            if any("ERROR: resource locked" in line for line in lines):
                logger.warning(f"Tuner {tuner} is locked by another resource")
                if not quiet:
                    print(f"\n⚠️  Tuner {tuner} is locked by another resource. Skipping to next tuner.")
                continue

            # More robust check for lock failures
            if lock_count == 0:
                logger.warning(f"Tuner {tuner} failed to lock on any frequency")
                if not quiet:
                    print(f"\n⚠️  Tuner {tuner} failed to lock on any frequency.")
                continue

            logger.info(f"Successfully scanned tuner {tuner}, found {len(lines)} lines of data")
            logger.info(f"Scanned {scan_count} frequencies, locked {lock_count}")

            if not quiet:
                print(f"\n")
                print(f"   ✅ Scan completed for tuner {tuner}!")
                print(f"   📊 Results: {scan_count} frequencies scanned, {lock_count} channels found")
                print()

            return lines

        except FileNotFoundError:
            logger.error("hdhomerun_config command not found")
            raise HDHRConfigNotFoundError("hdhomerun_config utility not found")

        except ValueError as e:
            logger.error(f"Invalid tuner number: {tuner} - {e}")
            print(f"Error: Invalid tuner number: {tuner}")
            continue

        except Exception as query_error:
            logger.error(f"Unexpected error querying tuner {tuner}: {query_error}", exc_info=True)
            print(f"Unexpected error with tuner {tuner}: {query_error}")
            continue

    logger.warning("All tuners are either locked or failed to lock")
    print("\nAll tuners are either locked or failed to lock.")
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
    Retrieve a response from OpenAI's GPT model based on a given prompt.

    This function sends a prompt to OpenAI's ChatCompletion API and retrieves a response.
    It uses the API key obtained from the environment variables to authenticate the request.

    Args:
        prompt (str): The prompt to be sent to the GPT model.

    Returns:
        str: The text response generated by the model, or empty string on error.

    Example:
        >>> prompt = "What city is this from: KABC, KCBS, KTLA"
        >>> response = get_openai_response(prompt)
        >>> print(response)
        "Los Angeles, California"
    """
    # Read the API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")

    if api_key is None:
        logger.warning("OpenAI API key not found in environment variables")
        print("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        return ""

    openai.api_key = api_key

    try:
        logger.debug(f"Sending request to OpenAI API with prompt length: {len(prompt)}")

        # Use modern ChatCompletion API instead of deprecated Completion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that identifies geographic locations based on TV station call signs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60,
            temperature=0.7
        )

        result = response.choices[0].message.content.strip()
        logger.info(f"Received OpenAI response: {result}")
        return result

    except openai.error.AuthenticationError:
        logger.error("OpenAI authentication failed - invalid API key")
        print("Error: Invalid OpenAI API key. Please check your OPENAI_API_KEY environment variable.")
        return ""

    except openai.error.RateLimitError:
        logger.error("OpenAI rate limit exceeded")
        print("Error: OpenAI rate limit exceeded. Please try again later.")
        return ""

    except openai.error.APIConnectionError as e:
        logger.error(f"OpenAI API connection error: {e}")
        print(f"Error: Unable to connect to OpenAI API. Please check your internet connection.")
        return ""

    except openai.error.Timeout:
        logger.error("OpenAI API request timed out")
        print("Error: OpenAI API request timed out. Please try again.")
        return ""

    except openai.error.InvalidRequestError as e:
        logger.error(f"Invalid OpenAI API request: {e}")
        print(f"Error: Invalid request to OpenAI API: {e}")
        return ""

    except Exception as error:
        logger.error(f"Unexpected error calling OpenAI API: {error}", exc_info=True)
        print(f"An unexpected error occurred with OpenAI: {error}")
        return ""


def check_file_writable(filepath: str) -> bool:
    """
    Check if a file path is writable.

    Args:
        filepath (str): Path to check for write permissions.

    Returns:
        bool: True if writable, False otherwise.
    """
    directory = os.path.dirname(filepath) or '.'

    if not os.path.exists(directory):
        logger.error(f"Directory does not exist: {directory}")
        return False

    if not os.access(directory, os.W_OK):
        logger.error(f"No write permission for directory: {directory}")
        return False

    # If file exists, check if it's writable
    if os.path.exists(filepath) and not os.access(filepath, os.W_OK):
        logger.error(f"No write permission for file: {filepath}")
        return False

    return True


def get_yes_no_input(prompt: str, default: str = 'n') -> bool:
    """
    Get validated yes/no input from user with standard CLI format.

    Args:
        prompt (str): The prompt to display to the user.
        default (str): Default value if user just presses enter ('y' or 'n').

    Returns:
        bool: True for yes, False for no.

    Note:
        Follows GNU/POSIX convention: capital letter shows default (Y/n or y/N).
    """
    valid_yes = ['y', 'yes']
    valid_no = ['n', 'no']

    # Format prompt with capital letter showing default
    if default == 'y':
        suffix = " (Y/n): "
    else:
        suffix = " (y/N): "

    while True:
        try:
            user_input = input(f"{prompt}{suffix}").strip().lower()

            if not user_input:
                return default == 'y'

            if user_input in valid_yes:
                return True
            elif user_input in valid_no:
                return False
            else:
                print("Invalid input. Please enter 'y' for yes or 'n' for no.")

        except KeyboardInterrupt:
            logger.info("User cancelled input")
            print("\nOperation cancelled by user.")
            return False


def main():
    """
    Main program for HD Homerun Scan Channels.

    This enhanced version includes:
    - Command-line argument parsing
    - Comprehensive error handling
    - Structured logging
    - Input validation
    - Progress indicators
    - Modern OpenAI API integration

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='HDHomeRun Channel Scanner - Scan and analyze OTA TV channels',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                    # Interactive mode
  %(prog)s --debug            # Enable debug logging
  %(prog)s --test-file        # Use local test file
  %(prog)s --no-save          # Don't save to CSV
  %(prog)s --auto-openai      # Automatically query OpenAI
        '''
    )

    parser.add_argument('--version', action='version',
                       version=f'%(prog)s {VERSION} ({VERSION_DATE})',
                       help='Show program version and exit')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    parser.add_argument('--test-file', dest='use_test_file', action='store_true',
                       help='Use local ScanData.txt file for testing')
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save results to CSV file')
    parser.add_argument('--auto-openai', action='store_true',
                       help='Automatically query OpenAI without prompting')
    parser.add_argument('--output', '-o', type=str,
                       help='Specify output CSV filename')

    # Automation flags for unattended operation
    parser.add_argument('--device-id', type=str, metavar='ID',
                       help='Specify HDHomeRun device ID (e.g., 12345678) to skip device selection')
    parser.add_argument('--tuner', type=int, choices=[0, 1, 2, 3], metavar='N',
                       help='Specify tuner number (0-3) to skip tuner selection')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Quiet mode: suppress progress output (for automation/scripts)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose mode: show detailed operation info (implies --debug)')

    args = parser.parse_args()

    # Handle --verbose (implies --debug)
    if args.verbose:
        args.debug = True

    # Setup logging
    setup_logging(debug=args.debug)
    logger.info("=" * 60)
    logger.info(f"HDHomeRun Channel Scanner v{VERSION} Starting")
    logger.info("=" * 60)

    try:
        # Check for hdhomerun_config utility
        if not args.use_test_file:
            check_hdhomerun_config()

        # Get system name
        system_name = platform.node()

        # Validate and truncate system name if too long
        # Most filesystems have 255 char filename limit
        # Reserve space for: _YYYYMMDD_HH.csv (16 chars)
        MAX_SYSTEM_NAME_LENGTH = 239  # 255 - 16

        if len(system_name) > MAX_SYSTEM_NAME_LENGTH:
            original_name = system_name
            system_name = system_name[:MAX_SYSTEM_NAME_LENGTH]
            logger.warning(f"System name truncated from {len(original_name)} to {MAX_SYSTEM_NAME_LENGTH} chars")
            print(f"⚠️  Note: Hostname too long, truncated to {MAX_SYSTEM_NAME_LENGTH} characters")

        # Get current date and time
        current_datetime = datetime.now()
        date_str = current_datetime.strftime("%Y%m%d")
        hour_str = current_datetime.strftime("%H")

        # Generate filename
        if args.output:
            filename = args.output

            # Validate user-provided filename length
            if len(filename) > 255:
                logger.error(f"User-provided filename too long: {len(filename)} chars (max 255)")
                print(f"❌ Error: Filename is too long ({len(filename)} characters)")
                print(f"   Maximum allowed: 255 characters")
                print(f"   Please use a shorter filename with --output")
                return 1
        else:
            filename = f"{system_name}_{date_str}_{hour_str}.csv"

        logger.info(f"Output filename: {filename}")

        # Initialize an empty list for parsed_data and results
        parsed_data = []
        results = []

        if not args.use_test_file:
            # Select the HDHomeRun Device
            if args.device_id:
                # Use device ID from command line (automation mode)
                device_number = args.device_id
                logger.info(f"Using device from --device-id: {device_number}")
                if not args.quiet:
                    print(f"Using device: {device_number}")

                # Verify device exists
                devices = discover_devices(quiet=args.quiet)
                device_found = any(device_number in dev for dev in devices)
                if not device_found:
                    logger.error(f"Device {device_number} not found on network")
                    print(f"❌ Error: Device {device_number} not found")
                    print(f"   Available devices: {len(devices)}")
                    for dev in devices:
                        print(f"   - {dev}")
                    return 1
            else:
                # Interactive device selection
                selected_device = select_device()

                if not selected_device:
                    logger.warning("No device selected, exiting")
                    print("No device selected. Exiting the program.")
                    return 1

                # Extract the 8-digit device number from the selected device
                device_number = selected_device.split()[2]
                logger.info(f"Using device: {device_number}")

            # Select a tuner or Auto mode
            if args.tuner is not None:
                # Use tuner from command line (automation mode)
                mode = args.tuner
                logger.info(f"Using tuner from --tuner: {mode}")
                if not args.quiet:
                    print(f"Using tuner: {mode}")
            else:
                # Interactive tuner selection
                mode = select_tuner_mode()
                if mode == -1:
                    logger.warning("Invalid tuner selection, exiting")
                    return 1

            # Set list of tuners based on selected tuner or AUTO to find an open tuner
            tuners = [mode] if mode != 4 else [0, 1, 2, 3]
            logger.info(f"Scanning tuners: {tuners}")

            # Query the selected tuner(s), return all scan frequency info from HDHR
            results = query_tuner(device_number, tuners, quiet=args.quiet)

            if not results:
                logger.error("No scan results obtained from tuner")
                print("Error: Could not obtain scan results from tuner.")
                return 1

        else:
            # Load from a local test file
            logger.info("Using local test file: ScanData.txt")
            print("Loading data from local test file: ScanData.txt")
            try:
                with open('ScanData.txt', 'r') as result_file:
                    results = result_file.readlines()
                logger.info(f"Loaded {len(results)} lines from test file")
            except FileNotFoundError:
                logger.error("Test file ScanData.txt not found")
                print("Error: Test file 'ScanData.txt' not found.")
                return 1
            except IOError as e:
                logger.error(f"Error reading test file: {e}")
                print(f"Error reading test file: {e}")
                return 1

        # Parse the results
        logger.info("Parsing scan results")
        print("\nParsing scan results...")
        parsed_data = parse_results_info(results)

        if not parsed_data:
            logger.warning("No valid data parsed from results")
            print("No valid data parsed from scan results.")
            return 1

        logger.info(f"Parsed {len(parsed_data)} frequency entries")
        print(f"Successfully parsed {len(parsed_data)} frequency entries.")

        # Handle CSV output
        if not args.no_save:
            save_to_csv = get_yes_no_input("\nSave results to a CSV file?", default='y')

            if save_to_csv:
                # Check file permissions with recovery options
                if not check_file_writable(filename):
                    print(f"\n❌ Cannot write to file: {filename}")
                    print(f"   Directory: {os.path.dirname(os.path.abspath(filename)) or '.'}")
                    logger.error(f"Cannot write to file: {filename}")

                    print("\n📋 Your scan data is ready but cannot be saved to this location.")
                    print("   What would you like to do?\n")
                    print("   1) Try a different file location")
                    print("   2) Display results on screen instead")
                    print("   3) Exit (lose the data)")

                    while True:
                        try:
                            choice = input("\nChoice (1-3): ").strip()

                            if choice == '1':
                                new_path = input("Enter new file path: ").strip()
                                if check_file_writable(new_path):
                                    filename = new_path
                                    logger.info(f"User provided alternate path: {filename}")
                                    break
                                else:
                                    print(f"❌ Still cannot write to: {new_path}")
                                    print("   Try again or choose option 2 or 3.")

                            elif choice == '2':
                                # Display results instead
                                logger.info("User chose to display results instead of saving")
                                save_to_csv = False
                                break

                            elif choice == '3':
                                confirm = input("\n⚠️  Really exit and lose scan data? (yes/no): ").strip().lower()
                                if confirm == 'yes':
                                    logger.warning("User chose to exit, losing scan data")
                                    return 1
                            else:
                                print("Invalid choice. Please enter 1, 2, or 3.")

                        except KeyboardInterrupt:
                            print("\n\nOperation cancelled.")
                            return 1

                # Only try to save if we still want to save (might have switched to display)
                if save_to_csv:
                    try:
                        logger.info(f"Writing data to CSV file: {filename}")
                        print(f"\nWriting data to '{filename}'...")

                        with open(filename, 'w', newline='') as output_file:
                            output_writer = csv.writer(output_file)

                            # Write Header row to the csv file
                            header = ['Frequency', 'US-Bcast Channel', 'Lock', 'Signal Strength (dBmV)',
                                    'Signal to Noise Quality', 'Symbol Error Quality', 'TSID']

                            for i in range(MIN_PROGRAM, MAX_PROGRAM + 1):
                                header.append(f'Program{i}')

                            output_writer.writerow(header)

                            # Iterate through the parsed_data and write rows to the CSV file
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

                                for i in range(MIN_PROGRAM, MAX_PROGRAM + 1):
                                    program_key = f'Program{i}'
                                    program_value = data.get(program_key, '')
                                    row.append(program_value)

                                output_writer.writerow(row)

                        logger.info(f"Data successfully written to '{filename}'")
                        print(f"Data successfully written to '{filename}'.")

                    except IOError as e:
                        logger.error(f"IO error writing CSV file: {e}")
                        print(f"Error writing to file: {e}")
                        return 1
                    except csv.Error as e:
                        logger.error(f"CSV error: {e}")
                        print(f"Error writing CSV data: {e}")
                        return 1

            # If user chose not to save OR chose to display instead, show results
            if not save_to_csv:
                logger.info("Displaying scan results in formatted view")
                print("\n" + "="*100)
                print("📊 SCAN RESULTS")
                print("="*100)

                # Sort by channel number for easier reading
                sorted_data = sorted(parsed_data, key=lambda x: int(x.get('US-Bcast Channel', '0')) if x.get('US-Bcast Channel', '0').isdigit() else 0)

                for idx, data in enumerate(sorted_data, 1):
                    channel = data.get('US-Bcast Channel', '?')
                    freq = data.get('Frequency', '?')
                    freq_mhz = f"{int(freq)/1000000:.3f} MHz" if freq != '?' and freq.isdigit() else '?'
                    lock = data.get('Lock', '?')
                    signal = data.get('Signal Strength (dBmV)', '?')
                    snq = data.get('Signal to Noise Quality', '?')
                    seq = data.get('Symbol Error Quality', '?')

                    # Status indicator
                    status = '✅ Good' if lock != 'none' else '❌ No Lock'
                    if lock != 'none' and signal != '?' and signal.lstrip('-').isdigit():
                        sig_val = int(signal)
                        if sig_val < 0:
                            status = '⚠️  Weak'
                        elif sig_val > 15:
                            status = '✅ Excellent'

                    # Collect programs
                    programs = [v for k,v in data.items() if k.startswith('Program') and v]

                    print(f"\n[{idx}] Channel {channel} ({freq_mhz}) {status}")
                    print(f"    Frequency: {freq} Hz")
                    print(f"    Lock: {lock}")
                    print(f"    Signal: {signal} dBmV  |  SNQ: {snq}%  |  SEQ: {seq}%")
                    print(f"    TSID: {data.get('TSID', 'N/A')}")

                    if programs:
                        print(f"    Programs ({len(programs)}):")
                        for prog in programs:
                            print(f"      • {prog}")
                    else:
                        print(f"    Programs: (none detected)")

                    print("    " + "─"*80)

                print(f"\n{'='*100}")
                locked_count = sum(1 for d in sorted_data if d.get('Lock', 'none') != 'none')
                print(f"Total: {len(parsed_data)} frequency entries | Locked: {locked_count} channels")
                print("="*100 + "\n")

        # Handle OpenAI query
        if args.auto_openai or get_yes_no_input("\nSend results to OpenAI to determine the city/region?", default='n'):
            if results:
                logger.info("Querying OpenAI for geographic location")
                print("\nQuerying OpenAI to identify geographic region...")

                stations_list = extract_programs(results)
                if stations_list:
                    stations_string = ' '.join(stations_list)

                    # Truncate if too long to prevent OpenAI token limit errors
                    MAX_STATIONS_LENGTH = 2000  # Safe for OpenAI's 4096 token limit
                    if len(stations_string) > MAX_STATIONS_LENGTH:
                        logger.warning(f"Station list truncated from {len(stations_string)} to {MAX_STATIONS_LENGTH} chars")
                        stations_string = stations_string[:MAX_STATIONS_LENGTH] + "..."
                        print(f"   ⚠️  Note: Station list truncated (too many channels for OpenAI)")

                    full_text = prepare_openai_prompt(stations_string)
                    openai_response = get_openai_response(full_text)

                    if openai_response:
                        logger.info(f"OpenAI identified region: {openai_response}")
                        print(f"\nThe broadcast region is: {openai_response}")
                    else:
                        print("Could not get a response from OpenAI.")
                else:
                    logger.warning("No station data to send to OpenAI")
                    print("No station data available to send to OpenAI.")
            else:
                logger.warning("No results available for OpenAI query")
                print("No results available to send to OpenAI.")

        logger.info("Program completed successfully")
        print("\nScan completed successfully!")
        return 0

    except HDHRConfigNotFoundError as e:
        logger.error(f"HDHomeRun config utility error: {e}")
        print(f"Error: {e}")
        return 1

    except DeviceDiscoveryError as e:
        logger.error(f"Device discovery error: {e}")
        print(f"Error: {e}")
        return 1

    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        print("\n\nProgram interrupted by user. Exiting.")
        return 130  # Standard exit code for Ctrl+C

    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
