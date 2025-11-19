
# HDHomeRun Channel Scanner

## Version 3.0 - Enhanced Edition

A robust, production-ready Python utility for discovering and scanning channels on SiliconDust HDHomeRun devices with comprehensive error handling, structured logging, and AI-powered geographic identification.

## Overview

This Python script serves as a professional-grade utility for discovering and scanning channels on SiliconDust HDHomeRun devices. HDHomeRun devices are network-attached TV tuners that allow users to receive over-the-air (OTA) video signals from local broadcast stations. This utility provides a user-friendly interface to identify HDHomeRun devices on your network, select a specific tuner, scan for available channels, and optionally identify your broadcast region using AI.

## What's New in Version 3.0

### Critical Bug Fixes
- **Fixed**: Negative signal strength parsing bug that caused data loss
- **Fixed**: Input validation crashes on non-numeric input
- **Fixed**: Fragile string matching in lock detection

### Major Enhancements
- **Structured Logging**: Professional logging system with file output and debug levels
- **Command-Line Interface**: Full argparse integration with multiple options
- **Modern APIs**: Upgraded from deprecated OpenAI Completion to ChatCompletion API
- **Security**: Replaced deprecated `os.popen()` with secure `subprocess.run()`
- **Error Handling**: Comprehensive exception handling with specific error types
- **Input Validation**: Robust validation for all user inputs
- **Progress Indicators**: Real-time feedback during scanning operations
- **Data Validation**: Signal quality range checking and validation
- **Permission Checks**: Pre-flight checks for file write permissions and utilities

### Code Quality Improvements
- Custom exception classes for better error handling
- Type hints throughout the codebase
- Comprehensive unit test suite (27 tests)
- Improved documentation and docstrings
- Better separation of concerns

## Requirements

### Required
- Python 3.7 or higher
- SiliconDust HDHomeRun device on your network
- `hdhomerun_config` utility ([Download](https://www.silicondust.com/support/downloads/))

### Optional
- OpenAI API key (for geographic location identification)
  - Set via environment variable: `export OPENAI_API_KEY="your-key-here"`
  - Python package: `pip install openai`


## Features

### Core Functionality
1. **Device Discovery**: Automatically finds HDHomeRun devices on your network with retry logic
2. **Tuner Selection**: Choose a specific tuner (0-3) or auto-scan through all available tuners
3. **Channel Scanning**: Scans all available frequencies to find channels with progress indicators
4. **Detailed Channel Information**:
   - Frequency and US broadcast channel number
   - Lock status (8vsb, none, etc.)
   - Signal strength (supports negative values)
   - Signal-to-noise quality (0-100)
   - Symbol error quality (0-100)
   - Transport Stream ID (TSID)
   - Up to 20 program listings per frequency
5. **CSV Export**: Dynamically named CSV files with comprehensive scan data
6. **AI-Powered Location**: Optional OpenAI integration to identify broadcast DMA/region from station call signs

### Advanced Features
- **Structured Logging**: All operations logged to `hdhr_scan.log` with timestamps
- **Debug Mode**: Verbose logging for troubleshooting (`--debug` flag)
- **Input Validation**: Robust handling of invalid inputs with helpful error messages
- **Error Recovery**: Automatic retry for locked tuners and failed operations
- **Signal Validation**: Automatic detection of out-of-range signal quality values
- **Graceful Interruption**: Proper handling of Ctrl+C interrupts
- **File Permission Checks**: Pre-flight validation before writing CSV files

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

## Installation

1. **Install hdhomerun_config utility**:
   ```bash
   # Download from https://www.silicondust.com/support/downloads/
   # Or install via package manager (Linux):
   sudo apt-get install hdhomerun-config
   ```

2. **Clone or download this repository**:
   ```bash
   git clone https://github.com/yourusername/hdhr-scan-frequencies.git
   cd hdhr-scan-frequencies
   ```

3. **(Optional) Install OpenAI package for geographic identification**:
   ```bash
   pip install openai
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Usage

### Basic Usage (Interactive Mode)
```bash
python3 main.py
```

This will:
1. Discover HDHomeRun devices on your network
2. Prompt you to select a device
3. Prompt you to select a tuner or auto mode
4. Scan for channels
5. Ask if you want to save results to CSV
6. Ask if you want to identify the broadcast region via OpenAI

### Command-Line Options

```bash
python3 main.py [OPTIONS]
```

**Available Options:**

| Option | Description |
|--------|-------------|
| `--debug` | Enable debug logging for detailed troubleshooting |
| `--test-file` | Use local `ScanData.txt` file instead of scanning device |
| `--no-save` | Skip CSV file creation (display results only) |
| `--auto-openai` | Automatically query OpenAI without prompting |
| `--output FILE`, `-o FILE` | Specify custom output CSV filename |
| `--help`, `-h` | Show help message and exit |

### Usage Examples

**Basic scan with debug logging:**
```bash
python3 main.py --debug
```

**Test mode using sample data:**
```bash
python3 main.py --test-file
```

**Automated scan with custom output file:**
```bash
python3 main.py --output my_scan_results.csv --auto-openai
```

**Quick scan without saving (display only):**
```bash
python3 main.py --no-save
```

**Full automation for scripting:**
```bash
python3 main.py --output scan.csv --auto-openai --debug
```

### Understanding the Output

•	Frequency: The frequency at which a potential channel was detected.
•	US-Broadcast Channel: The corresponding broadcast channel in the US.
•	Lock Status: Whether the tuner was able to lock onto the signal at this frequency.
•	Signal Strength (dBmV): Strength of the signal received.
•	Signal to Noise Quality: The quality of the signal in terms of its noise level.
•	Symbol Error Quality: The quality of the digital signal.
•	TSID: Transport Stream ID, a unique identifier for the group of channels.
•	Program Listings: Names of the programs or channels available on this frequency.

## Logging

The application creates a log file `hdhr_scan.log` in the current directory with detailed information about all operations.

### Log Levels
- **INFO**: Normal operation messages (default)
- **DEBUG**: Detailed diagnostic information (use `--debug` flag)
- **WARNING**: Non-critical issues (e.g., signal quality out of range)
- **ERROR**: Critical errors that may affect operation

### Example Log Output
```
2025-11-19 10:30:15 - __main__ - INFO - HDHomeRun Channel Scanner v3.0 Starting
2025-11-19 10:30:15 - __main__ - DEBUG - hdhomerun_config utility found in PATH
2025-11-19 10:30:16 - __main__ - INFO - Discovered 1 HDHomeRun device(s)
2025-11-19 10:30:20 - __main__ - INFO - User selected device: hdhomerun device 12345678 found at 192.168.1.100
```

## Testing

A comprehensive unit test suite is included with 27 tests covering all critical functionality.

### Running Tests
```bash
python3 test_main.py
```

### Test Coverage
- Parse lock data (including negative signal strength)
- Frequency and channel parsing
- TSID parsing
- Program extraction
- Signal quality validation
- File permission checks
- Edge cases and error conditions

All tests must pass before deploying to production.

## Troubleshooting

### Common Issues

**"No HDHomeRun devices found"**
- Ensure your HDHomeRun device is powered on
- Verify the device is connected to the same network as your computer
- Check firewall settings aren't blocking device discovery
- Try the device rediscovery option from the menu
- Run with `--debug` flag for detailed diagnostic information

**"hdhomerun_config utility not found"**
- Install the hdhomerun_config utility from [SiliconDust Downloads](https://www.silicondust.com/support/downloads/)
- Ensure the utility is in your system PATH
- On Linux: `sudo apt-get install hdhomerun-config`

**"ERROR: resource locked"**
- The tuner is being used by another application (TV viewer, recording software, etc.)
- The scanner will automatically try the next available tuner
- Use auto mode (option 4) to try all tuners automatically
- Close other applications using the HDHomeRun device

**"OpenAI API errors"**
- Verify your API key is set: `echo $OPENAI_API_KEY`
- Check you have sufficient API credits
- Ensure you have network connectivity
- The scanner will continue without OpenAI if there are errors

**"Permission denied" when writing CSV**
- Check write permissions in the current directory
- Specify an alternate output path: `--output /path/to/writable/file.csv`
- Run with `--no-save` to display results without saving

### Debug Mode

For detailed troubleshooting, always run with the `--debug` flag:
```bash
python3 main.py --debug
```

This will:
- Show all subprocess commands being executed
- Display detailed parsing information
- Log all validation checks
- Print full stack traces on errors
- Write comprehensive debug information to `hdhr_scan.log`

## Error Codes

The script returns standard exit codes:
- `0`: Success
- `1`: General error (check logs for details)
- `130`: User interrupted with Ctrl+C

## Architecture

### Custom Exception Classes
- `HDHRConfigNotFoundError`: hdhomerun_config utility not available
- `DeviceDiscoveryError`: Failed to discover devices
- `TunerLockError`: Tuner failed to lock on channels
- `InvalidInputError`: Invalid user input

### Key Functions
- `discover_devices()`: Network device discovery with timeout
- `query_tuner()`: Execute channel scan with progress tracking
- `parse_lock()`: Parse signal data (handles negative values)
- `validate_signal_quality()`: Validate SNQ/SEQ ranges
- `check_file_writable()`: Pre-flight permission checks
- `get_openai_response()`: AI-powered geographic identification

## Version History

### Version 3.0 (2025-11-19)
- Complete refactor with production-ready error handling
- Added structured logging system
- Implemented command-line argument parsing
- Upgraded to modern OpenAI ChatCompletion API
- Fixed critical negative signal strength parsing bug
- Added comprehensive input validation
- Replaced deprecated os.popen() with subprocess.run()
- Added 27-test unit test suite
- Enhanced documentation

### Version 2.4
- Added OpenAI integration for geographic identification
- Documentation improvements
- Refactored for modularity

### Version 2.2
- Added OpenAI integration
- Improved code organization

### Version 2.1
- Bug fixes and code cleanup
- Added sample test file

## Contributing

Contributions are welcome! Please ensure:
1. All tests pass (`python3 test_main.py`)
2. Code follows existing style conventions
3. New features include corresponding tests
4. Documentation is updated

## Support

For issues or questions:
- Check the troubleshooting section above
- Review `hdhr_scan.log` for detailed error information
- Consult [SiliconDust's official documentation](https://www.silicondust.com/support/)
- Open an issue on GitHub with debug logs attached

## License

This project is provided as-is for use with SiliconDust HDHomeRun devices.

