# Part 1: User Interaction Point Inventory
## HDHomeRun Channel Scanner v3.0 - Complete UX Audit

**Date**: 2025-11-19
**Auditor**: Comprehensive User Journey Analysis
**Application Version**: 3.0

---

## A. Command-Line Interface (CLI) Touchpoints

### Argument Parser (main.py:649-672)

| Argument | Type | Line | Description | Required |
|----------|------|------|-------------|----------|
| `--debug` | flag | 662 | Enable debug logging | No |
| `--test-file` | flag | 664 | Use local ScanData.txt | No |
| `--no-save` | flag | 666 | Skip CSV file creation | No |
| `--auto-openai` | flag | 668 | Auto-query OpenAI | No |
| `--output`, `-o` | string | 670 | Custom CSV filename | No |
| `--help`, `-h` | flag | built-in | Show help text | No |

**Help Text** (main.py:650-659):
- Description: "HDHomeRun Channel Scanner - Scan and analyze OTA TV channels"
- Epilog: Contains 5 usage examples
- Format: RawDescriptionHelpFormatter

**Exit Codes** (throughout main.py):
- `0`: Success (main.py:857)
- `1`: General error (main.py:713, 723, 735, 748, 752, 762, 776, 823, 862, 867, 880)
- `130`: Keyboard interrupt (main.py:872)

---

## B. Interactive Prompts

### B.1 Device Selection (main.py:177-263)

**Primary Prompt** (main.py:217):
```
"\nEnter the device number: "
```
- **Location**: select_device() function
- **Input Type**: Numeric
- **Valid Range**: 1 to (num_devices + 1)
- **Validation**: Lines 218-229
- **Error Handling**: ValueError (231), KeyboardInterrupt (233-236)
- **Retry Logic**: Infinite loop with manual exit

**Device List Display** (main.py:210-213):
```
"\nSelect an HDHomeRun device:"
"1) [device info]"
"2) [device info]"
"N+1) Rediscover devices"
```

**Rediscovery Prompt** (main.py:248):
```
"Would you like to discover devices again? (y/n): "
```
- **Input Type**: Single character (y/n)
- **Validation**: Lowercase conversion, exact match
- **Default**: None (explicit input required)

### B.2 Tuner Selection (main.py:150-191)

**Menu Display** (main.py:161-166):
```
"\nSelect a tuner or Auto mode:"
"0) Tuner 0"
"1) Tuner 1"
"2) Tuner 2"
"3) Tuner 3"
"4) Auto mode (Try all tuners)"
```

**Primary Prompt** (main.py:171):
```
"\nEnter the mode number: "
```
- **Location**: select_tuner_mode() function
- **Input Type**: Numeric
- **Valid Range**: 0 to 4
- **Validation**: Lines 172-179
- **Error Handling**: ValueError (181-183), KeyboardInterrupt (184-187)
- **Retry Logic**: 3 attempts maximum (main.py:168-189)
- **Failure Action**: Returns -1, program exits

### B.3 CSV Save Confirmation (main.py:769)

**Prompt** (via get_yes_no_input):
```
"\nSave results to a CSV file? (1=yes / 2=no): "
```
- **Location**: main() function
- **Input Type**: String (1/2, y/n, yes/no)
- **Valid Inputs**: ['1', 'y', 'yes'] or ['2', 'n', 'no']
- **Default**: 'y' (main.py:769)
- **Validation**: Lines 610-625
- **Error Handling**: KeyboardInterrupt (627-630)
- **Retry Logic**: Infinite loop until valid input or interrupt

### B.4 OpenAI Query Confirmation (main.py:832)

**Prompt** (via get_yes_no_input):
```
"\nSend results to OpenAI to determine the city/region? (1=yes / 2=no): "
```
- **Location**: main() function
- **Input Type**: String (1/2, y/n, yes/no)
- **Valid Inputs**: ['1', 'y', 'yes'] or ['2', 'n', 'no']
- **Default**: 'n' (main.py:832)
- **Validation**: Lines 610-625
- **Error Handling**: KeyboardInterrupt (627-630)
- **Retry Logic**: Infinite loop until valid input or interrupt

---

## C. Status and Progress Messages

### C.1 Startup Messages

| Message | Line | Condition | Purpose |
|---------|------|-----------|---------|
| "=" * 60 | 677 | Always | Visual separator |
| "HDHomeRun Channel Scanner v3.0 Starting" | 678 | Always | Application banner |
| "=" * 60 | 679 | Always | Visual separator |

### C.2 Device Discovery Messages

| Message | Line | Trigger | Type |
|---------|------|---------|------|
| "\nSelect an HDHomeRun device:" | 210 | Devices found | Info |
| "No HDHomeRun devices found. Retrying in 3 seconds..." | 241 | No devices, first try | Warning |
| "No HDHomeRun devices found after retry." | 247 | No devices, after retry | Warning |

### C.3 Scanning Progress Messages

| Message | Line | Trigger | Type |
|---------|------|---------|------|
| "\nScanning tuner {tuner} on device {device_id}..." | 401 | Scan start | Info |
| "Tuner {tuner} is locked by another resource. Skipping to next tuner." | 416 | Resource locked | Warning |
| "Tuner {tuner} failed to lock on any frequency." | 423 | No lock success | Warning |
| "Scan completed for tuner {tuner}." | 427 | Scan complete | Success |
| "Scanned {scan_count} frequencies, successfully locked on {lock_count} channels." | 433 | After scan | Info |

### C.4 Data Processing Messages

| Message | Line | Trigger | Type |
|---------|------|---------|------|
| "Loading data from local test file: ScanData.txt" | 740 | --test-file flag | Info |
| "\nParsing scan results..." | 756 | Always | Info |
| "Successfully parsed {len(parsed_data)} frequency entries." | 765 | Parsing success | Success |

### C.5 File Writing Messages

| Message | Line | Trigger | Type |
|---------|------|---------|------|
| "\nWriting data to '{filename}'..." | 780 | CSV write start | Info |
| "Data successfully written to '{filename}'." | 814 | CSV write success | Success |

### C.6 OpenAI Messages

| Message | Line | Trigger | Type |
|---------|------|---------|------|
| "\nQuerying OpenAI to identify geographic region..." | 835 | OpenAI query start | Info |
| "\nThe broadcast region is: {openai_response}" | 845 | OpenAI success | Success |
| "Could not get a response from OpenAI." | 847 | OpenAI failure | Warning |
| "No station data available to send to OpenAI." | 850 | No stations found | Warning |
| "No results available to send to OpenAI." | 853 | No scan results | Warning |

### C.7 Completion Messages

| Message | Line | Trigger | Type |
|---------|------|---------|------|
| "\nScan completed successfully!" | 856 | Normal completion | Success |
| "No device selected. Exiting the program." | 712 | No device selection | Exit |
| "\n\nProgram interrupted by user. Exiting." | 871 | Ctrl+C interrupt | Exit |

---

## D. Error Messages

### D.1 Device Discovery Errors

| Error Message | Line | Condition | Severity | Recovery |
|---------------|------|-----------|----------|----------|
| "Error during device discovery: {e}" | 258 | DeviceDiscoveryError | High | Exit select_device |
| "\nOperation cancelled by user." | 235, 262 | KeyboardInterrupt | Info | Exit program |
| "hdhomerun_config utility is required but not found. Please install from https://..." | 91-93 | HDHRConfigNotFoundError | Critical | Exit program |

### D.2 Input Validation Errors

| Error Message | Line | Condition | Severity | Recovery |
|---------------|------|-----------|----------|----------|
| "Invalid input. Please enter a number." | 232, 299 | Non-numeric input | Low | Retry prompt |
| "Invalid choice. Please enter a number between 1 and {max}" | 229 | Out of range | Low | Retry prompt |
| "Invalid choice. Please enter a number between 0 and 4." | 295 | Out of range tuner | Low | Retry prompt |
| "Too many invalid attempts. Exiting." | 306 | 3 failed attempts | Medium | Exit program |
| "Invalid input. Please enter '1' or 'yes' for yes, '2' or 'no' for no." | 625 | Invalid yes/no | Low | Retry prompt |

### D.3 Scanning Errors

| Error Message | Line | Condition | Severity | Recovery |
|---------------|------|-----------|----------|----------|
| "Error: Tuner {tuner} scan timed out. Trying next tuner." | 439 | Timeout (5 min) | High | Try next tuner |
| "Error: Invalid tuner number: {tuner}" | 448 | ValueError | Medium | Try next tuner |
| "Unexpected error with tuner {tuner}: {query_error}" | 453 | General exception | High | Try next tuner |
| "\nAll tuners are either locked or failed to lock." | 457 | All tuners failed | Critical | Return empty |
| "Error: Could not obtain scan results from tuner." | 734 | Empty results | Critical | Exit program |

### D.4 File Operation Errors

| Error Message | Line | Condition | Severity | Recovery |
|---------------|------|-----------|----------|----------|
| "Error: Test file 'ScanData.txt' not found." | 747 | FileNotFoundError | Critical | Exit program |
| "Error reading test file: {e}" | 751 | IOError | Critical | Exit program |
| "Error: Cannot write to file '{filename}'. Check permissions." | 774 | Permission denied | Critical | Exit program |
| "Error writing to file: {e}" | 818 | IOError | Critical | Exit program |
| "Error writing CSV data: {e}" | 822 | csv.Error | Critical | Exit program |

### D.5 Data Parsing Errors

| Error Message | Line | Condition | Severity | Recovery |
|---------------|------|-----------|----------|----------|
| "No valid data parsed from scan results." | 761 | Empty parsed_data | Critical | Exit program |

### D.6 OpenAI API Errors

| Error Message | Line | Condition | Severity | Recovery |
|---------------|------|-----------|----------|----------|
| "OpenAI API key not found. Please set OPENAI_API_KEY environment variable." | 517 | Missing API key | Medium | Continue without AI |
| "Error: Invalid OpenAI API key. Please check your OPENAI_API_KEY environment variable." | 542 | AuthenticationError | Medium | Continue without AI |
| "Error: OpenAI rate limit exceeded. Please try again later." | 547 | RateLimitError | Medium | Continue without AI |
| "Error: Unable to connect to OpenAI API. Please check your internet connection." | 552 | APIConnectionError | Medium | Continue without AI |
| "Error: OpenAI API request timed out. Please try again." | 557 | Timeout | Medium | Continue without AI |
| "Error: Invalid request to OpenAI API: {e}" | 562 | InvalidRequestError | Medium | Continue without AI |
| "An unexpected error occurred with OpenAI: {error}" | 567 | General exception | Medium | Continue without AI |

### D.7 General Errors

| Error Message | Line | Condition | Severity | Recovery |
|---------------|------|-----------|----------|----------|
| "Error: {e}" | 861, 866 | Custom exceptions | Critical | Exit program |
| "An unexpected error occurred: {e}" | 876 | General exception | Critical | Exit program |

---

## E. Output Displays

### E.1 Screen Output (Display Mode)

**Location**: main.py:827-829

**Trigger**: User selects "no" to CSV save

**Format**:
```python
for data in parsed_data:
    print(data)
```

**Output Type**: Raw dictionary display

**Example**:
```
{'Frequency': '605000000', 'US-Bcast Channel': '36', 'Lock': '8vsb', ...}
```

### E.2 CSV File Output

**Location**: main.py:782-812

**Header Row** (main.py:786-790):
```
['Frequency', 'US-Bcast Channel', 'Lock', 'Signal Strength (dBmV)',
 'Signal to Noise Quality', 'Symbol Error Quality', 'TSID',
 'Program1', 'Program2', ..., 'Program20']
```

**Filename Format** (main.py:698):
- Default: `{hostname}_{YYYYMMDD}_{HH}.csv`
- Custom: User-specified via `--output`

**File Location**: Current working directory

### E.3 Log File Output

**Location**: `hdhr_scan.log` (main.py:68)

**Format** (main.py:60):
```
'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

**Log Levels**:
- DEBUG: With `--debug` flag
- INFO: Default
- WARNING: Signal validation, non-critical issues
- ERROR: Critical failures

**Example**:
```
2025-11-19 10:30:15 - __main__ - INFO - HDHomeRun Channel Scanner v3.0 Starting
```

---

## F. User Interruption Points

### F.1 Keyboard Interrupt (Ctrl+C) Handling

| Location | Line | Handler | Message | Exit Code |
|----------|------|---------|---------|-----------|
| Device selection | 233-236 | try/except | "Operation cancelled by user." | Returns "" |
| Device selection (outer) | 260-263 | try/except | "Operation cancelled by user." | Returns "" |
| Tuner selection | 184-187 | try/except | "Operation cancelled by user." | Returns -1 |
| Yes/No input | 627-630 | try/except | "Operation cancelled by user." | Returns False |
| Main function | 869-872 | try/except | "Program interrupted by user. Exiting." | Exit 130 |

---

## G. Progress Indicators and Feedback

### G.1 Real-Time Progress

| Indicator | Line | Information Provided | Update Frequency |
|-----------|------|---------------------|------------------|
| Scan start | 401 | Tuner number, device ID | Per tuner |
| Scan complete | 427 | Tuner number | Per tuner |
| Frequency count | 433 | Total scanned, successful locks | Per tuner |
| Parsing status | 756 | "Parsing..." | Once |
| Parse result | 765 | Number of entries | Once |
| File write status | 780 | Filename | Once |
| File write complete | 814 | Filename | Once |
| OpenAI query | 835 | "Querying..." | Once |

### G.2 Wait States (No Visual Feedback)

| Operation | Duration | Line | Feedback Status |
|-----------|----------|------|-----------------|
| Device discovery | Up to 10 sec | 144-157 | ❌ No progress |
| Channel scanning | Up to 5 min | 403-409 | ❌ No progress |
| OpenAI API call | Variable | 526-534 | ❌ No progress |
| Automatic retry wait | 3 seconds | 242 | ✅ "Retrying in 3 seconds..." |

---

## H. Contextual Help and Documentation

### H.1 In-Application Help

| Type | Access Method | Location | Content |
|------|---------------|----------|---------|
| Argument help | `--help` | Built-in | Full argparse help text |
| Usage examples | `--help` | main.py:652-659 | 5 command examples |

### H.2 External Documentation

| Document | Coverage | Completeness |
|----------|----------|--------------|
| README.md | Full usage, troubleshooting, examples | ✅ Comprehensive |
| CHANGELOG.md | Version history, changes | ✅ Detailed |
| Test documentation | Test coverage, running tests | ✅ Complete |

### H.3 Error Message Documentation Links

**Current State**: ❌ No error messages link to documentation

**Opportunity**: Error messages could reference specific README sections

---

## Summary Statistics

### Interaction Point Counts

| Category | Count |
|----------|-------|
| CLI Arguments | 6 (5 custom + help) |
| Interactive Prompts | 4 main prompts |
| Status Messages | 15 |
| Error Messages | 28 |
| Progress Indicators | 8 |
| Output Formats | 3 (screen, CSV, log) |
| Interrupt Points | 5 |
| **TOTAL TOUCHPOINTS** | **69** |

### Message Type Distribution

| Type | Count | Percentage |
|------|-------|------------|
| Informational | 20 | 29% |
| Success | 7 | 10% |
| Warning | 8 | 12% |
| Error | 28 | 41% |
| Prompt | 6 | 9% |

### Critical Interaction Density

| Function | Interaction Points | Complexity |
|----------|-------------------|------------|
| main() | 45+ | Very High |
| select_device() | 12 | High |
| select_tuner_mode() | 8 | Medium |
| query_tuner() | 10 | High |
| get_yes_no_input() | 4 | Medium |

---

## Key Findings

### ✅ Strengths

1. **Comprehensive Error Coverage**: 28 distinct error messages
2. **Flexible Input**: Supports multiple input formats (1/2, y/n, yes/no)
3. **Graceful Interrupts**: Ctrl+C handled at all major points
4. **Progress Feedback**: Key operations provide status updates
5. **Detailed Logging**: All operations logged to file

### ⚠️ Concerns

1. **Long Wait States**: 5-minute scans with no progress updates
2. **Inconsistent Prompts**: Mix of numeric (1/2) and letter (y/n) inputs
3. **No Timeout Indicators**: User doesn't know if operation is frozen
4. **Error Message Variability**: Some errors very detailed, others generic
5. **No Help During Prompts**: No way to get help without restarting
6. **Display Mode Poor UX**: Raw dictionary output not user-friendly

---

**Next**: Part 2 - User Journey Mapping
