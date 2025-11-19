
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
| `--help`, `-h` | Show help message and exit |
| `--version` | Show program version and exit |
| `--glossary` | Show technical glossary explaining scan terms and exit |
| `--show-config` | Display current configuration and exit |
| `--edit-config` | Edit configuration interactively and exit |
| `--reset-config` | Reset configuration to defaults and exit |
| `--debug` | Enable debug logging for detailed troubleshooting |
| `--verbose`, `-v` | Verbose mode with detailed operation info (implies --debug) |
| `--quiet`, `-q` | Quiet mode: suppress progress output (for automation/scripts) |
| `--test-file` | Use local `ScanData.txt` file instead of scanning device |
| `--no-save` | Skip CSV file creation (display results only) |
| `--auto-openai` | Automatically query OpenAI without prompting |
| `--output FILE`, `-o FILE` | Specify custom output filename (CSV or JSON) |
| `--format {csv,json}` | Output format: csv (default) or json |
| `--json` | Output in JSON format (shorthand for --format json) |
| `--device-id ID` | Specify HDHomeRun device ID to skip device selection |
| `--tuner N` | Specify tuner number (0-3) to skip tuner selection |

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
python3 main.py --device-id 12345678 --tuner 0 --quiet --output scan.csv
```

**View technical glossary:**
```bash
python3 main.py --glossary
```

**Configuration management:**
```bash
# View current configuration
python3 main.py --show-config

# Edit configuration interactively
python3 main.py --edit-config

# Reset configuration to defaults
python3 main.py --reset-config
```

**JSON output format:**
```bash
# Export as JSON
python3 main.py --json -o scan.json

# Or explicitly specify format
python3 main.py --format json -o scan.json
```

## Configuration File

The scanner supports a persistent configuration file to save your preferences.

### Location

Configuration is stored at: `~/.hdhr_scanner_config.json`

### Available Settings

- **device_id**: Default HDHomeRun device ID (skip device selection)
- **tuner**: Default tuner number 0-3 (skip tuner selection)
- **output_directory**: Default location for CSV files
- **auto_openai**: Automatically query OpenAI (true/false)
- **quiet**: Enable quiet mode by default (true/false)
- **debug**: Enable debug logging by default (true/false)
- **save_csv**: Save to CSV by default (true/false)
- **last_device_id**: Last used device (auto-saved after scan)
- **last_tuner**: Last used tuner (auto-saved after scan)

### Managing Configuration

**View Current Configuration:**
```bash
python3 main.py --show-config
```

Output example:
```
⚙️  CURRENT CONFIGURATION
================================================================================

Configuration file: /home/user/.hdhr_scanner_config.json

DEFAULTS (used when flags not specified):
  Device ID:        12345678
  Tuner:            0
  Output Directory: /home/user/scans
  Auto OpenAI:      False
  Quiet Mode:       False
  Debug Mode:       False
  Save CSV:         True

LAST USED:
  Last Device ID:   12345678
  Last Tuner:       0

NOTE: Command-line flags override configuration file settings
```

**Edit Configuration Interactively:**
```bash
python3 main.py --edit-config
```

This launches an interactive editor where you can:
- Set default device ID and tuner
- Specify output directory (with directory creation)
- Configure boolean settings (auto-openai, quiet, debug, save_csv)
- Save changes when done

**Reset to Defaults:**
```bash
python3 main.py --reset-config
```

Deletes the configuration file and resets all settings to defaults.

### Configuration Precedence

Settings are applied in this order (later overrides earlier):
1. Default values (built-in)
2. Configuration file values
3. Command-line arguments (highest priority)

Example:
- Config file sets `device_id: "12345678"`
- You run: `python3 main.py --device-id ABCD1234`
- Result: Uses ABCD1234 (command-line wins)

### Example Configuration File

```json
{
    "device_id": "12345678",
    "tuner": 0,
    "output_directory": "/home/user/tv_scans",
    "auto_openai": false,
    "quiet": false,
    "debug": false,
    "save_csv": true,
    "last_device_id": "12345678",
    "last_tuner": 0
}
```

### Auto-Save Feature

After each successful scan, the tool automatically saves:
- **last_device_id**: Device you just used
- **last_tuner**: Tuner you just used

These values help you quickly repeat scans with the same setup.

## User Tutorial

### First-Time Setup

1. **Install Prerequisites**
   ```bash
   # Install HDHomeRun utility (Linux example)
   sudo apt-get install hdhomerun-config

   # Verify installation
   hdhomerun_config discover
   ```

2. **Clone and Test**
   ```bash
   git clone <repository-url>
   cd hdhr-scan-frequencies
   python3 main.py --help
   ```

3. **First Scan (Interactive)**
   ```bash
   python3 main.py
   ```

   The first time you run it, you'll see a welcome screen explaining:
   - What the tool does
   - Requirements
   - Quick tips

   Then follow the prompts:
   - Device selection → Choose your HDHomeRun from the list
   - Tuner selection → Choose a specific tuner (0-3) or AUTO mode
   - Wait 3-5 minutes → Real-time progress with ETA shown
   - Save to CSV? → Press Y to save, N to just display
   - Query OpenAI? → Press N unless you want location detection

### Understanding Your Scan Results

#### Display Mode Output

When you choose not to save (or use `--no-save`), you'll see formatted results like:

```
[1] Channel 7 (177.000 MHz) ✅ Good
    Frequency: 177000000 Hz
    Lock: 8vsb
    Signal: 5 dBmV  |  SNQ: 100%  |  SEQ: 100%
    TSID: 1234
    Programs (3):
      • 7.1 WABC-HD
      • 7.2 LiveWell
      • 7.3 Localish
```

**What each field means:**
- **Channel Number**: Logical channel (what appears on your TV)
- **Frequency**: Physical RF frequency in Hz (also shown in MHz)
- **Status**: Signal quality indicator
  - 🌟 Excellent: >15 dBmV
  - ✅ Strong: 10-15 dBmV
  - ✅ Good: 0-10 dBmV
  - ⚠️ Weak: -10 to 0 dBmV
  - ❌ Very Weak: <-10 dBmV
- **Lock**: Modulation type (8vsb = standard ATSC broadcast)
- **Signal**: Power level in dBmV (higher is better)
- **SNQ**: Signal to Noise Quality (100% = perfect)
- **SEQ**: Symbol Error Quality (100% = perfect)
- **TSID**: Transport Stream ID (broadcaster identifier)
- **Programs**: Subchannels available (7.1, 7.2, 7.3, etc.)

#### Signal Warnings

If you see warnings like:

```
⚠️  SIGNAL WARNINGS:
   • Weak channels: Ch 2, Ch 45
     → Consider repositioning antenna

   HOW TO IMPROVE:
   1. Reorient antenna (try different directions)
   2. Raise antenna height if possible
   ...
```

These are **actionable recommendations** to improve reception. Follow the numbered steps to fix issues.

#### CSV Output

The CSV file (named `hostname_YYYYMMDD_HH.csv`) contains:
- All frequency data in spreadsheet-friendly format
- Perfect for data analysis, tracking changes over time
- Import into Excel, Google Sheets, or any CSV viewer

### Automation & Scripting

#### Cron Job Example

Scan automatically every day at 3 AM:

```bash
# Add to crontab (crontab -e)
0 3 * * * cd /path/to/hdhr-scan-frequencies && python3 main.py --device-id 12345678 --tuner 0 --quiet --output ~/scans/scan_$(date +\%Y\%m\%d).csv
```

#### Bash Script Example

```bash
#!/bin/bash
# scan_channels.sh - Automated channel scanning

DEVICE_ID="12345678"
OUTPUT_DIR="$HOME/channel_scans"
mkdir -p "$OUTPUT_DIR"

python3 main.py \
    --device-id "$DEVICE_ID" \
    --tuner 0 \
    --quiet \
    --output "$OUTPUT_DIR/scan_$(date +%Y%m%d_%H%M).csv"

echo "Scan complete! Check $OUTPUT_DIR"
```

#### Python Integration Example

```python
import subprocess
import json

# Run scan and capture output
result = subprocess.run(
    ['python3', 'main.py',
     '--device-id', '12345678',
     '--tuner', '0',
     '--quiet',
     '--output', 'scan.csv'],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("Scan successful!")
    # Process scan.csv here
else:
    print(f"Scan failed: {result.stderr}")
```

### Advanced Usage

#### Comparing Scans Over Time

```bash
# Scan morning
python3 main.py -o morning_scan.csv

# Scan evening
python3 main.py -o evening_scan.csv

# Compare results
diff morning_scan.csv evening_scan.csv
```

#### Testing Different Antennas

```bash
# Document which antenna you're testing
python3 main.py -o antenna_indoor.csv
# (swap to outdoor antenna)
python3 main.py -o antenna_outdoor.csv
```

#### Finding Optimal Antenna Direction

```bash
# Scan at different directions (note: manual antenna adjustment needed)
python3 main.py -o north.csv
# (rotate antenna 90°)
python3 main.py -o east.csv
# (rotate antenna 90°)
python3 main.py -o south.csv
# (rotate antenna 90°)
python3 main.py -o west.csv
```

Compare signal strengths in each CSV to find best direction.

## Frequently Asked Questions (FAQ)

### General Questions

**Q: Do I need an OpenAI API key?**
A: No, it's optional. The scanner works perfectly without it. OpenAI is only used to identify your broadcast region from station call signs, which is mostly for curiosity. You can skip this feature by pressing 'N' when prompted or use `--no-openai` (implied default).

**Q: How long does a scan take?**
A: Typically 3-5 minutes. The tool now shows real-time progress with ETA: "Scanning: Channel 7 (25 frequencies) | ETA: 2m 30s (45%)". The first 10 scans establish the baseline, then ETA appears and updates every 5 seconds.

**Q: Can I scan multiple devices?**
A: Yes! Run the scanner once per device:
```bash
python3 main.py --device-id AAAA1111 -o device1.csv
python3 main.py --device-id BBBB2222 -o device2.csv
```

**Q: What if I don't know my device ID?**
A: Just run `python3 main.py` without `--device-id`. It will discover devices and show a menu. Or run: `hdhomerun_config discover` to see all devices.

**Q: Does this work on all HDHomeRun models?**
A: Yes! Works with all models (Connect, Extend, Flex, etc.) as long as they support the `hdhomerun_config` utility.

### Technical Questions

**Q: What does "8vsb" mean in the Lock field?**
A: It's the modulation type for ATSC 1.0 broadcasts (standard US over-the-air TV). Use `--glossary` flag for a complete technical glossary.

**Q: My signal strength is negative. Is that bad?**
A: Not necessarily! Signal strength in dBmV can be negative. The scale:
- **>15 dBmV**: Excellent
- **0-15 dBmV**: Good to Strong
- **0 to -10 dBmV**: Weak but usable
- **<-10 dBmV**: Very weak, may not work

**Q: What's the difference between SNQ and SEQ?**
A:
- **SNQ (Signal to Noise Quality)**: How clean the signal is (interference-free)
- **SEQ (Symbol Error Quality)**: How accurate the digital data is (error-free)

Both should be >90% for reliable reception.

**Q: Why do some channels show "none" for Lock?**
A: No broadcast found on that frequency. Either:
- No station broadcasting there
- Signal too weak to detect
- Outside your reception area

**Q: What's a subchannel (like 7.1, 7.2)?**
A: Digital TV allows multiple programs on one RF channel. 7.1 is the main channel, 7.2/7.3 are additional channels (weather, news, retro shows, etc.). All come from one RF frequency.

### Troubleshooting Questions

**Q: "ERROR: resource locked" - what does this mean?**
A: Another app is using that tuner (TV viewer, DVR, etc.). Solutions:
1. Close other apps using HDHomeRun
2. Try a different tuner (0, 1, 2, or 3)
3. Use AUTO mode - it tries all tuners automatically

**Q: Scan finds 0 channels. Why?**
A: Several possibilities:
1. **No antenna connected** → Connect antenna to HDHomeRun
2. **Antenna not pointed correctly** → Try rotating it
3. **Too far from towers** → Check FCC map: https://www.fcc.gov/media/engineering/dtvmaps
4. **Tuner locked** → Try different tuner or restart HDHomeRun

**Q: My channels have weak signal. How do I fix?**
A: The tool now shows automatic warnings and recommendations. Common fixes:
1. Reorient antenna (try all 4 directions)
2. Raise antenna higher
3. Move antenna away from metal/electronics
4. Switch to outdoor antenna
5. Check antenna is connected properly
6. Use amplifier if >50 miles from towers

**Q: Can I automate scans with cron?**
A: Yes! Use `--quiet` mode to suppress interactive prompts:
```bash
# Add to crontab
0 3 * * * cd /path/to/scanner && python3 main.py --device-id 12345678 --tuner 0 -q -o scan.csv
```

**Q: The welcome screen shows every time. How do I skip it?**
A: The welcome screen only shows once (marker file: `~/.hdhr_scan_welcomed`). If you want to skip it, use `--quiet` flag or delete the marker to see it again.

**Q: What's the --glossary flag for?**
A: It shows a comprehensive technical glossary explaining all terms:
```bash
python3 main.py --glossary
```
Explains: dBmV, SNQ, SEQ, 8vsb, TSID, subchannels, and more. Perfect for first-time users.

### Data Questions

**Q: Can I export results in JSON format?**
A: Yes! Use the `--json` flag or `--format json`:
```bash
# JSON output
python3 main.py --json -o scan.json

# Or explicitly specify format
python3 main.py --format json -o scan.json
```
JSON output includes scan metadata and cleaner program arrays.

**Q: How do I open the CSV file?**
A: Any spreadsheet app:
- **Excel**: File → Open → Select CSV
- **Google Sheets**: File → Import → Upload File
- **LibreOffice Calc**: Open directly
- **Command line**: `cat scan.csv` or `less scan.csv`

**Q: The CSV has 20 Program columns but I only have 3 programs. Why?**
A: The tool reserves space for up to 20 programs per frequency (the maximum possible). Empty columns just mean no program in that slot.

**Q: Can I diff two scans to see what changed?**
A: Yes!
```bash
diff scan1.csv scan2.csv
# Or for better readability:
diff -y scan1.csv scan2.csv | less
```

### Error Questions

**Q: "hdhomerun_config utility not found" - help!**
A: The tool now shows a comprehensive error message with What/Why/How format. Follow the installation steps:
1. Download from: https://www.silicondust.com/support/downloads/
2. Install for your OS
3. Verify: `hdhomerun_config discover`

**Q: "No HDHomeRun devices found" but my device is on!**
A: The tool now provides troubleshooting steps automatically. Check:
1. Device powered on (green LED solid)
2. Network cable connected
3. Same network as computer
4. Firewall allows UDP port 65001
5. Try: `hdhomerun_config discover` directly

**Q: I get a Python error about "openai module not found"**
A: OpenAI is optional. Either:
- Install it: `pip install openai`
- Or press 'N' when asked about OpenAI query
- Or use automation mode which skips OpenAI by default

**Q: File permission denied when saving CSV?**
A: The tool now offers a recovery menu with options:
1. Try different location
2. Display results on screen instead
3. Exit

Choose option 1 and provide a writable path, or use option 2 to see results without saving.

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

## DevOps & Production Deployment

### Quick Installation

The fastest way to install HDHomeRun Scanner in production:

```bash
# Download and run installation script
curl -fsSL https://raw.githubusercontent.com/yourusername/hdhr-scan-frequencies/main/install.sh | sudo bash

# Or clone and install
git clone https://github.com/yourusername/hdhr-scan-frequencies.git
cd hdhr-scan-frequencies
sudo bash install.sh

# Start using the scanner
hdhr-scan --help
```

The installation script automatically:
- Installs Python 3 and dependencies
- Downloads and compiles `hdhomerun_config` utility
- Creates service user and directories
- Sets up systemd service (Linux)
- Configures firewall rules
- Creates command-line wrapper

### Deployment Methods

#### 1. Docker Deployment (Recommended)

**Build and run with Docker:**
```bash
# Build image
docker build -t hdhr-scanner:3.0 .

# Run interactively
docker run --rm -it --network host \
  -v $(pwd)/output:/app/output \
  hdhr-scanner:3.0 python3 main.py

# Run automated scan
docker run --rm --network host \
  -v $(pwd)/output:/app/output \
  hdhr-scanner:3.0 python3 main.py \
  --device-id 12345678 --tuner 0 --quiet -o /app/output/scan.csv
```

**Using Docker Compose:**
```bash
# Start services
docker-compose up -d

# Run scan
docker-compose run --rm hdhr-scanner python3 main.py

# View configuration
docker-compose run --rm hdhr-scanner python3 main.py --show-config
```

#### 2. Native Installation

See `DEPLOYMENT.md` for comprehensive native installation instructions for:
- Ubuntu/Debian
- RHEL/CentOS/Fedora
- macOS
- Windows

#### 3. Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Production Features

#### Configuration Management
```bash
# View current configuration
hdhr-scan --show-config

# Edit configuration interactively
hdhr-scan --edit-config

# Reset to defaults
hdhr-scan --reset-config
```

Configuration file: `~/.hdhr_scanner_config.json`

#### Automation & Scheduling

**Cron job (daily at 3 AM):**
```bash
0 3 * * * hdhr-scan --device-id 12345678 --tuner 0 --quiet -o /var/hdhr/scans/scan_$(date +\%Y\%m\%d).csv
```

**systemd timer:**
```bash
# Enable timer
sudo systemctl enable hdhr-scanner.timer
sudo systemctl start hdhr-scanner.timer

# Check status
sudo systemctl status hdhr-scanner.timer
```

#### Monitoring & Logging

- **Log file:** `hdhr_scan.log`
- **Log rotation:** Automatic (5 MB × 5 files = 25 MB total)
- **Log levels:** INFO (default), DEBUG (`--debug` flag), WARNING, ERROR

**Monitor logs:**
```bash
# Tail logs
tail -f hdhr_scan.log

# Search for errors
grep ERROR hdhr_scan.log

# Today's activity
grep "$(date +%Y-%m-%d)" hdhr_scan.log
```

### Dependencies

#### Python Packages
See `requirements.txt`:
- **openai** (optional) - For AI-powered location identification

All other dependencies are Python standard library.

#### System Requirements
- **Python:** 3.7+ (3.11+ recommended)
- **hdhomerun_config:** Latest from [SiliconDust](https://www.silicondust.com/support/downloads/)
- **Network:** UDP port 65001 for device discovery

### CI/CD Pipeline

GitHub Actions workflow included (`.github/workflows/ci.yml`):
- **Linting:** flake8, black, mypy
- **Testing:** pytest on Python 3.7-3.11, Ubuntu & macOS
- **Security:** safety, bandit, Trivy
- **Docker:** Build, test, and publish images
- **Release:** Automatic artifact creation and Docker publishing

### Documentation

- **README.md** - User guide and feature documentation (this file)
- **ERROR_REFERENCE.md** - Comprehensive error reference
- **DEPLOYMENT.md** - Complete DevOps deployment guide
- **CHANGELOG.md** - Version history and changes

### Security

- Non-root user execution (Docker & systemd)
- Configuration file permissions (600)
- Firewall rules for HDHomeRun discovery
- API key management via environment variables
- No hardcoded credentials
- Security scanning in CI/CD pipeline

### Support Resources

**For production deployments, see:**
- [DEPLOYMENT.md](DEPLOYMENT.md) - Comprehensive deployment guide
- [ERROR_REFERENCE.md](ERROR_REFERENCE.md) - Error troubleshooting
- Production considerations, monitoring, automation, security best practices

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

