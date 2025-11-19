# HDHomeRun Channel Scanner - Error Reference

Complete reference for all errors, warnings, and status messages you may encounter while using the HDHomeRun Channel Scanner.

## Table of Contents

- [Critical Errors](#critical-errors)
- [Warning Messages](#warning-messages)
- [Information Messages](#information-messages)
- [Exit Codes](#exit-codes)
- [Error Recovery Procedures](#error-recovery-procedures)

---

## Critical Errors

### E001: HDHomeRun Utility Not Found

**Error Message:**
```
❌ ERROR: HDHomeRun Utility Not Found

WHAT HAPPENED:
  The 'hdhomerun_config' command-line utility is not installed or not
  in your system PATH.
```

**Cause:** The `hdhomerun_config` utility is not installed or cannot be found in your system PATH.

**Impact:** The scanner cannot communicate with HDHomeRun devices. The program will exit immediately.

**Resolution:**
1. Download the HDHomeRun software package from: https://www.silicondust.com/support/downloads/
2. Install the package for your operating system:
   - **Linux**: `sudo apt-get install hdhomerun-config`
   - **macOS**: Install from DMG file
   - **Windows**: Run the installer
3. Verify installation: `hdhomerun_config discover`
4. Ensure the utility is in your PATH
5. Rerun the scanner

**Exit Code:** 1

**Log Reference:** Check `hdhr_scan.log` for:
```
ERROR - hdhomerun_config utility not found in system PATH
```

---

### E002: No HDHomeRun Devices Found

**Error Message:**
```
❌ ERROR: No HDHomeRun Devices Found

WHAT HAPPENED:
  The scan could not find any HDHomeRun devices on your network.

WHY THIS HAPPENS:
  • Device is not powered on
  • Device not connected to same network as this computer
  • Network firewall blocking device discovery
  • Device has network configuration issues
```

**Cause:** Device discovery failed to find any HDHomeRun devices on the local network.

**Impact:** Cannot proceed with scanning. The program will exit.

**Resolution:**
1. **Check Device Power**
   - Verify device is plugged in
   - Look for solid green LED on front of device
   - If LED is off, device has no power
   - If LED is blinking, device is booting (wait 30 seconds)

2. **Check Network Connection**
   - Verify ethernet cable is securely connected
   - Check router shows device is connected
   - Try different ethernet cable
   - Try different router port

3. **Verify Same Network**
   - Computer and HDHomeRun must be on same subnet
   - Check computer IP: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
   - Device should be on same 192.168.x.x or 10.x.x.x network

4. **Test Device Connectivity**
   - Run: `hdhomerun_config discover`
   - Visit: http://my.hdhomerun.com (shows all devices on account)
   - Ping device IP if known: `ping 192.168.1.100`

5. **Check Firewall Settings**
   - Allow UDP port 65001 for device discovery
   - Temporarily disable firewall to test
   - Add exception for hdhomerun_config utility

6. **Try Direct Device ID**
   - If you know device ID, bypass discovery:
   - `python3 main.py --device-id 12345678`

7. **Restart Device**
   - Unplug device for 10 seconds
   - Plug back in and wait for solid green LED
   - Retry scan

**Exit Code:** 1

**Log Reference:**
```
ERROR - Device discovery failed with return code X
ERROR - Device discovery timed out after 10 seconds
```

---

### E003: Device ID Not Found

**Error Message:**
```
❌ Error: Device 12345678 not found
   Available devices: 2
   - hdhomerun device AAAA1111 found at 192.168.1.100
   - hdhomerun device BBBB2222 found at 192.168.1.101
```

**Cause:** The device ID specified with `--device-id` flag does not exist on the network.

**Impact:** Cannot proceed with scanning the specified device.

**Resolution:**
1. Check the device ID you entered
2. Run discovery to see all available devices:
   ```bash
   hdhomerun_config discover
   ```
3. Use correct device ID from the list:
   ```bash
   python3 main.py --device-id AAAA1111
   ```
4. Or run in interactive mode (no --device-id flag) to select from menu

**Exit Code:** 1

**Log Reference:**
```
ERROR - Device 12345678 not found on network
```

---

### E004: Tuner Resource Locked

**Error Message:**
```
⚠️  Tuner 0 is locked by another resource. Skipping to next tuner.
```

**Cause:** The specified tuner is currently in use by another application (TV viewer, DVR, recording software, etc.).

**Impact:** Scanner skips this tuner and tries the next one. If all tuners are locked, scan fails.

**Resolution:**
1. **Close Other Applications**
   - Stop any TV viewing apps
   - Cancel any ongoing recordings
   - Close DVR software
   - Check for background recording schedules

2. **Try Different Tuner**
   - Use different tuner: `--tuner 1` (try 0, 1, 2, or 3)

3. **Use AUTO Mode**
   - Scanner will try all tuners automatically
   - Runs without `--tuner` flag in interactive mode
   - Select option 4 "AUTO" from tuner menu

4. **Wait and Retry**
   - If recording is in progress, wait for it to finish
   - Retry scan after other apps are closed

5. **Restart Device**
   - As last resort, power cycle the HDHomeRun
   - Wait for solid green LED before retrying

**Severity:** Warning (not fatal if other tuners available)

**Log Reference:**
```
WARNING - Tuner 0 is locked by another resource
```

---

### E005: No Tuner Locks Found

**Error Message:**
```
⚠️  Tuner 0 failed to lock on any frequency.
```

**Cause:** The tuner scanned all frequencies but could not lock onto any signals.

**Impact:** Scanner tries next tuner. If all tuners fail, no data is captured.

**Resolution:**
1. **Check Antenna Connection**
   - Verify antenna is connected to "ANTENNA" port
   - Check cable is not loose
   - Inspect cable for damage

2. **Check Antenna Placement**
   - Move antenna near window
   - Point antenna toward broadcast towers
   - Raise antenna height
   - Remove obstacles (metal, electronics)

3. **Verify Coverage Area**
   - Check FCC coverage map: https://www.fcc.gov/media/engineering/dtvmaps
   - Enter your address to see expected channels
   - If you're >50 miles from towers, you may need outdoor antenna

4. **Try Different Tuner**
   - One tuner may be faulty
   - Try each tuner (0, 1, 2, 3) individually

5. **Check External Factors**
   - Weather (heavy storms can block signals)
   - Time of day (atmospheric conditions affect UHF)
   - Nearby construction/interference

6. **Test Antenna**
   - Try different antenna if available
   - Test antenna with TV directly to verify it works
   - Consider amplified antenna if signal is weak

**Severity:** Warning (may be normal if no broadcasts in area)

**Log Reference:**
```
WARNING - Tuner 0 failed to lock on any frequency
```

---

### E006: Scan Timeout

**Error Message:**
```
⏱️  Error: Tuner 0 scan timed out. Trying next tuner.
```

**Cause:** The scan took longer than 5 minutes (300 seconds) to complete.

**Impact:** Scanner aborts current tuner and tries next one.

**Resolution:**
1. **Network Issues**
   - Check network connection is stable
   - Verify no packet loss: `ping <device_ip>`
   - Check router isn't overloaded

2. **Device Issues**
   - Device may be malfunctioning
   - Try power cycle (unplug/replug)
   - Update device firmware if available

3. **Try Different Tuner**
   - Timeout may be specific to one tuner
   - Use --tuner flag to try each individually

4. **Check Device Temperature**
   - Ensure device has adequate ventilation
   - Device may throttle if overheating

**Severity:** Error (causes tuner to be skipped)

**Log Reference:**
```
ERROR - Tuner 0 scan timed out after 5 minutes
```

---

### E007: No Scan Results

**Error Message:**
```
Error: Could not obtain scan results from tuner.
```

**Cause:** After trying all specified tuners, no scan data was captured.

**Impact:** Program exits without any data. No CSV file created.

**Resolution:**
1. See resolutions for E005 (No Tuner Locks)
2. Verify antenna is working with TV directly
3. Check device functionality with official HDHomeRun app
4. Contact HDHomeRun support if device appears faulty

**Exit Code:** 1

**Log Reference:**
```
ERROR - No scan results obtained from tuner
```

---

### E008: File Permission Denied

**Error Message:**
```
❌ Cannot write to file: scan.csv
   Directory: /path/to/directory

📋 Your scan data is ready but cannot be saved to this location.
   What would you like to do?

   1) Try a different file location
   2) Display results on screen instead
   3) Exit (lose the data)
```

**Cause:** No write permission for the output file or directory.

**Impact:** Cannot save scan data. Recovery menu is shown with options.

**Resolution:**
1. **Choose Option 1: Try Different Location**
   - Enter a path where you have write permissions
   - Example: `/tmp/scan.csv` or `~/scan.csv`
   - Scan data is preserved

2. **Choose Option 2: Display Results**
   - View formatted results on screen
   - Copy data manually if needed
   - No file is created

3. **Choose Option 3: Exit**
   - Confirms data loss
   - Only use if you want to abort

**Prevention:**
- Run scanner from directory you own
- Use --output flag to specify writable path
- Check permissions before scanning: `ls -la`
- Use --no-save flag if you only want to view results

**Exit Code:** 1 (if option 3 chosen)

**Log Reference:**
```
ERROR - Cannot write to file: scan.csv
INFO - User provided alternate path: /tmp/scan.csv (if option 1)
INFO - User chose to display results instead (if option 2)
WARNING - User chose to exit, losing scan data (if option 3)
```

---

### E009: Filename Too Long

**Error Message:**
```
❌ Error: Filename is too long (300 characters)
   Maximum allowed: 255 characters
   Please use a shorter filename with --output
```

**Cause:** The filename specified with --output exceeds filesystem limit (255 characters).

**Impact:** Program exits immediately before scanning.

**Resolution:**
- Use shorter filename: `--output scan.csv`
- Use shorter path: `--output ~/s.csv`
- Filesystem limit is 255 chars total (path + filename)

**Exit Code:** 1

**Log Reference:**
```
ERROR - User-provided filename too long: 300 chars (max 255)
```

---

### E010: Hostname Too Long

**Warning Message:**
```
⚠️  Note: Hostname too long, truncated to 239 characters
```

**Cause:** System hostname exceeds safe filename length. Auto-generated CSV filename would be too long.

**Impact:** Hostname is automatically truncated. Scan continues normally.

**Resolution:**
- No action required (handled automatically)
- Consider using --output flag to specify custom short filename
- Not an error, just informational warning

**Severity:** Warning (non-fatal)

**Log Reference:**
```
WARNING - System name truncated from 250 to 239 chars
```

---

### E011: OpenAI Token Limit

**Warning Message:**
```
⚠️  Note: Station list truncated (too many channels for OpenAI)
```

**Cause:** Too many channels detected (>2000 characters of station data). OpenAI has 4096 token limit.

**Impact:** Only first 2000 characters of stations sent to OpenAI. Location detection may be less accurate but will still work.

**Resolution:**
- No action required (handled automatically)
- OpenAI still receives enough data for region identification
- Consider this normal for areas with many channels

**Severity:** Warning (non-fatal)

**Log Reference:**
```
WARNING - Station list truncated from 2500 to 2000 chars
```

---

## Warning Messages

### W001: Signal Quality Out of Range

**Warning Message:** (in logs only)
```
WARNING - Signal to Noise Quality value 150 outside expected range [0-100]
```

**Cause:** Signal quality value from device is outside expected 0-100 range.

**Impact:** Data is still recorded. May indicate device malfunction or parsing issue.

**Resolution:**
- Check device firmware is up to date
- Data is preserved as-is in CSV
- Contact support if values are consistently wrong
- Report issue with sample log file

**Severity:** Warning (data preserved)

---

### W002: Weak Signal Detected

**Warning Message:**
```
⚠️  Weak signal - Consider antenna adjustment
```

**Cause:** Channel has signal strength between -10 and 0 dBmV (weak but usable).

**Impact:** Channel may work but could have occasional dropouts.

**Resolution:**
1. Reorient antenna (try different directions)
2. Raise antenna height
3. Move antenna away from electronics/metal
4. See full improvement guide in displayed warnings section

**Severity:** Warning (channel usable but suboptimal)

---

### W003: Very Weak Signal

**Warning Message:**
```
❌ Signal too weak - May not work reliably
```

**Cause:** Channel has signal strength below -10 dBmV (very weak, unreliable).

**Impact:** Channel may not work at all or have frequent dropouts.

**Resolution:**
1. Same as W002 but more urgent
2. Consider outdoor antenna
3. Consider signal amplifier
4. Channel may not be receivable from your location

**Severity:** Warning (channel likely unusable)

---

### W004: Poor Signal Quality (SNQ)

**Warning Message:**
```
⚠️  Poor signal quality (low SNQ)
```

**Cause:** Signal to Noise Quality <50%. Too much interference/noise.

**Impact:** Channel may have pixelation, stuttering, or dropouts.

**Resolution:**
1. Move antenna away from electronics
2. Check for sources of RF interference (computers, motors, LED lights)
3. Try different antenna location
4. Consider shielded coax cable

**Severity:** Warning (channel may be problematic)

---

### W005: Symbol Errors Detected (SEQ)

**Warning Message:**
```
⚠️  Symbol errors detected (low SEQ)
```

**Cause:** Symbol Error Quality <90%. Digital data corruption.

**Impact:** May cause pixelation, audio dropouts, or channel freezing.

**Resolution:**
1. Check for multipath interference (signal bouncing off buildings)
2. Adjust antenna direction
3. Move antenna to different location
4. Try indoor antenna in different room

**Severity:** Warning (channel may have issues)

---

## Information Messages

### I001: First-Time Welcome

**Message:**
```
🎉 WELCOME TO HDHomeRun CHANNEL SCANNER

This tool scans Over-The-Air (OTA) TV channels...
```

**When:** First time running the tool (or after deleting `~/.hdhr_scan_welcomed`)

**Purpose:** Helps new users understand the tool, requirements, and tips.

**To Skip:** Use `--quiet` flag or file is created after first run.

---

### I002: Device Discovery

**Message:**
```
🔍 Searching for HDHomeRun devices on your network...
   (This may take up to 10 seconds)

   → Found 2 devices
```

**When:** During device discovery phase.

**Purpose:** Provides feedback during 1-10 second wait.

**To Skip:** Use `--quiet` flag.

---

### I003: Scan Progress

**Message:**
```
📡 Scanning tuner 0 on device 12345678...
   This will take 3-5 minutes. Progress shown below:

   Scanning: Channel 7 (25 frequencies) | ETA: 2m 30s (45%)
   ✅ Locked: Channel 7 (Total locks: 3)
```

**When:** During channel scan (every frequency).

**Purpose:** Shows real-time progress, ETA, and lock notifications.

**To Skip:** Use `--quiet` flag (only available in automation mode).

---

### I004: Scan Complete

**Message:**
```
✅ Scan completed for tuner 0!
📊 Results: 65 frequencies scanned, 15 channels found
⏱️  Duration: 3m 45s
```

**When:** After successful scan completion.

**Purpose:** Summarizes scan results and duration.

---

### I005: Signal Warnings Summary

**Message:**
```
⚠️  SIGNAL WARNINGS:
   • Problem channels: Ch 2, Ch 45
     → May experience dropouts or fail to tune
   • Weak channels: Ch 7, Ch 13
     → Consider repositioning antenna

   HOW TO IMPROVE:
   1. Reorient antenna (try different directions)
   2. Raise antenna height if possible
   ...
```

**When:** After displaying scan results (if weak signals detected).

**Purpose:** Provides actionable guidance for improving reception.

---

## Exit Codes

The scanner returns standard POSIX exit codes:

| Code | Meaning | When |
|------|---------|------|
| 0 | Success | Scan completed successfully |
| 1 | General Error | Any error condition (see logs) |
| 130 | Interrupted | User pressed Ctrl+C |

**Usage in Scripts:**
```bash
python3 main.py
if [ $? -eq 0 ]; then
    echo "Scan successful"
else
    echo "Scan failed - check logs"
fi
```

---

## Error Recovery Procedures

### Procedure 1: Complete Reset

If encountering persistent errors:

1. **Stop All HDHomeRun Apps**
   ```bash
   # Kill any apps using device
   pkill -f hdhomerun
   ```

2. **Power Cycle Device**
   - Unplug HDHomeRun for 30 seconds
   - Plug back in
   - Wait for solid green LED (30-60 seconds)

3. **Verify Device Works**
   ```bash
   hdhomerun_config discover
   hdhomerun_config <device_id> get /sys/model
   ```

4. **Test Connection**
   ```bash
   ping <device_ip>
   ```

5. **Retry Scan**
   ```bash
   python3 main.py --debug
   ```

6. **Check Logs**
   ```bash
   cat hdhr_scan.log | grep ERROR
   ```

---

### Procedure 2: Network Troubleshooting

If device discovery fails repeatedly:

1. **Check Network Connection**
   ```bash
   # Linux/Mac
   ifconfig
   ip addr show

   # Windows
   ipconfig
   ```

2. **Verify Same Subnet**
   - Computer: 192.168.1.100
   - Device should be: 192.168.1.x (same subnet)

3. **Test Direct Communication**
   ```bash
   # If you know device IP
   hdhomerun_config <device_ip> get /sys/model
   ```

4. **Check Firewall**
   ```bash
   # Linux - temporarily disable to test
   sudo ufw disable

   # Mac - System Preferences → Security → Firewall
   # Windows - Control Panel → Windows Defender Firewall
   ```

5. **Try Different Network**
   - Connect computer directly to router (not WiFi)
   - Use wired connection for both computer and device
   - Try different ethernet cables

---

### Procedure 3: Antenna Troubleshooting

If scan finds 0 channels or all weak:

1. **Verify Antenna Connection**
   - Cable connected to "ANTENNA" port (not "CABLE")
   - Cable finger-tight, not loose
   - No damage to cable

2. **Check Antenna Orientation**
   - Point toward broadcast towers
   - Use FCC map to find tower locations
   - Try all 4 cardinal directions (N, E, S, W)
   - Compare signal strengths

3. **Test Antenna Height**
   - Scan at floor level
   - Scan at table height
   - Scan at ceiling height
   - Scan at window
   - Compare results

4. **Eliminate Interference**
   - Move antenna away from computers
   - Move away from LED lights
   - Move away from metal objects
   - Move away from motors/appliances

5. **Try Different Location**
   - Different room
   - Different side of building
   - Near window vs. interior room

6. **Consider Upgrade**
   - Amplified antenna if >30 miles from towers
   - Outdoor antenna if >50 miles
   - Directional antenna if towers in one direction

---

### Procedure 4: Log Analysis

When reporting issues, include relevant log sections:

```bash
# View recent errors
tail -50 hdhr_scan.log | grep ERROR

# View full session
tail -200 hdhr_scan.log

# Search for specific issue
grep "Device discovery" hdhr_scan.log
```

**What to Include in Bug Reports:**
1. Full error message from screen
2. Relevant log excerpts (last 50-100 lines)
3. Command used to run scanner
4. OS and Python version: `python3 --version`
5. hdhomerun_config version: `hdhomerun_config version`
6. Device model and firmware version

---

## Getting Help

If this reference doesn't solve your issue:

1. **Check Logs:** `hdhr_scan.log` has detailed diagnostic information
2. **Run with --debug:** Provides maximum detail
3. **Use --glossary:** Explains all technical terms
4. **Check FAQ:** README.md has 30+ common questions answered
5. **Official Support:** https://www.silicondust.com/support/
6. **Report Bug:** Include error reference code (E001, etc.) and log excerpts

---

**Last Updated:** 2025-11-19 (Version 3.0)
