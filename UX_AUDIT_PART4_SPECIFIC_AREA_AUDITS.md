# User Journey Audit - Part 4: Specific Area Deep Dives
## HDHomeRun Channel Scanner v3.0

**Date:** 2025-11-19
**Auditor:** Claude Code
**Session:** Comprehensive UX Audit (Part 4 of 10)

---

## Executive Summary

This document provides detailed audits of five specific areas of the HDHomeRun Channel Scanner application:
1. Prompt and message quality
2. Progress and feedback mechanisms
3. Error recovery paths
4. Command-line argument UX
5. Output quality (screen, CSV, log)

Each section includes current behavior analysis, UX issues identified, and specific recommendations for improvement.

---

## Table of Contents

- [4.1 Prompt and Message Quality Audit](#41-prompt-and-message-quality-audit)
- [4.2 Progress and Feedback Audit](#42-progress-and-feedback-audit)
- [4.3 Error Recovery Path Audit](#43-error-recovery-path-audit)
- [4.4 Command-Line Arguments UX Audit](#44-command-line-arguments-ux-audit)
- [4.5 Output Quality Audit](#45-output-quality-audit)
- [Summary of Findings](#summary-of-findings)

---

## 4.1 Prompt and Message Quality Audit

### 4.1.1 Device Selection Prompt

**Location:** `main.py:217`

**Current Implementation:**
```python
user_input = input("\nEnter the device number: ").strip()
```

**Context Provided:**
```
Select an HDHomeRun device:
1) hdhomerun device 12345678 found at 192.168.1.100
2) hdhomerun device 98765432 found at 192.168.1.101
3) Rediscover devices

Enter the device number:
```

#### Analysis

**✅ Strengths:**
- Clear numbered list format
- "Rediscover devices" option clearly labeled
- Menu structure is easy to scan

**❌ Weaknesses:**
1. **Ambiguous valid range**: Prompt doesn't indicate valid numbers (1-3 in this example)
2. **No cancellation hint**: Users don't know they can press Ctrl+C to exit
3. **Term ambiguity**: "device number" could mean the 8-digit ID vs menu position
4. **No help available**: No way to get more information about devices

**Error Message Quality (line 229):**
```python
print(f"Invalid choice. Please enter a number between 1 and {len(discovered_devices) + 1}")
```
- ✅ Good: Dynamically shows valid range
- ❌ Issue: Only shown AFTER error, not upfront

#### Recommendations

**Improved Prompt:**
```python
print(f"\nEnter the device number (1-{len(discovered_devices) + 1}) or press Ctrl+C to cancel: ")
user_input = input("> ").strip()
```

**Better Context:**
```python
print("\nSelect an HDHomeRun device:")
for i, device in enumerate(discovered_devices):
    print(f"  {i + 1}) {device}")
print(f"  {len(discovered_devices) + 1}) Rediscover devices")
print(f"\nEnter your choice (1-{len(discovered_devices) + 1}, or Ctrl+C to cancel)")
user_input = input("> ").strip()
```

**Effort:** 15 minutes
**Impact:** Medium - Reduces confusion and errors

---

### 4.1.2 Tuner Selection Prompt

**Location:** `main.py:287`

**Current Implementation:**
```python
user_input = input("\nEnter the mode number: ").strip()
```

**Context Provided:**
```
Select a tuner or Auto mode:
0) Tuner 0
1) Tuner 1
2) Tuner 2
3) Tuner 3
4) Auto mode (Try all tuners)

Enter the mode number:
```

#### Analysis

**✅ Strengths:**
- Auto mode has helpful description "(Try all tuners)"
- Range is clear from menu (0-4)
- Consistent formatting

**❌ Weaknesses:**
1. **Inconsistent terminology**: Says "mode number" but shows "Tuner X"
2. **No guidance on selection**: Users don't know which tuner to pick
3. **No status information**: Doesn't show which tuners might be busy
4. **Missing expected range in prompt**: Have to count menu items
5. **No explanation**: What IS a tuner? Why would I pick one vs auto?

**Error Message (line 295):**
```python
print(f"Invalid choice. Please enter a number between 0 and 4.")
```
- ✅ Good: Clear range
- ❌ Issue: Hardcoded "4" instead of dynamic

#### Recommendations

**Better Terminology:**
Change "Enter the mode number" to "Enter the tuner number" for consistency.

**Add Guidance:**
```python
print("\nSelect a tuner or Auto mode:")
print("  0) Tuner 0")
print("  1) Tuner 1")
print("  2) Tuner 2")
print("  3) Tuner 3")
print("  4) Auto mode (Try all tuners sequentially until one works)")
print("\nℹ️  Tip: Choose 'Auto mode' (4) if you're unsure or if a tuner might be in use.")
print(f"\nEnter tuner number (0-4, or Ctrl+C to cancel)")
user_input = input("> ").strip()
```

**Add Default:**
```python
user_input = input("> ").strip() or "4"  # Default to auto mode
```

**Effort:** 20 minutes
**Impact:** High - Auto mode is almost always the right choice for users

---

### 4.1.3 Yes/No Prompts

**Location:** `main.py:830` (get_yes_no_input function)

**Current Implementation:**
```python
user_input = input(f"{prompt} (1=yes / 2=no): ").strip().lower()
```

**Example Usage:**
```
Save results to a CSV file? (1=yes / 2=no):
Send results to OpenAI to determine the city/region? (1=yes / 2=no):
```

#### Analysis

**✅ Strengths:**
- Function accepts multiple formats: '1', 'y', 'yes', '2', 'n', 'no' (lines 825-826)
- Has default value support (unused in current calls)
- Handles KeyboardInterrupt gracefully

**❌ Weaknesses:**
1. **Non-standard format**: Most CLIs use 'y/n' or 'Y/n', not '1/2'
2. **Hidden flexibility**: Accepts 'yes'/'no' but prompt doesn't say so
3. **No default indication**: Format like '[Y/n]' is standard to show default
4. **Inconsistent with rediscovery prompt**: Line 248 uses 'y/n' format directly
5. **Doesn't show what user typed**: If they type '1', feedback shows they chose yes

**Example of Inconsistency:**
```python
# Line 248 - Direct input, uses y/n
retry_input = input("Would you like to discover devices again? (y/n): ").strip().lower()

# Line 830 - Helper function, uses 1/2
user_input = input(f"{prompt} (1=yes / 2=no): ").strip().lower()
```

#### Recommendations

**Standardize on y/n:**
```python
def get_yes_no_input(prompt: str, default: str = 'n') -> bool:
    """
    Get validated yes/no input from user.

    Args:
        prompt: The prompt to display to the user.
        default: Default value if user just presses enter ('y' or 'n').

    Returns:
        bool: True for yes, False for no.
    """
    valid_yes = ['y', 'yes']
    valid_no = ['n', 'no', '']

    # Show default in prompt
    if default == 'y':
        prompt_suffix = "[Y/n]"
        default_bool = True
    else:
        prompt_suffix = "[y/N]"
        default_bool = False

    while True:
        try:
            user_input = input(f"{prompt} {prompt_suffix}: ").strip().lower()

            if not user_input:
                return default_bool

            if user_input in valid_yes:
                return True
            elif user_input in valid_no:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")

        except KeyboardInterrupt:
            logger.info("User cancelled input")
            print("\nOperation cancelled.")
            return False
```

**Updated Call Sites:**
```python
# Line 984
save_to_csv = get_yes_no_input("Save results to a CSV file?", default='y')

# Line 1047
if args.auto_openai or get_yes_no_input("Send results to OpenAI to determine the city/region?", default='n'):
```

**Effort:** 30 minutes
**Impact:** High - Aligns with CLI conventions, reduces cognitive load

---

### 4.1.4 Error Message Quality Review

#### 4.1.4.1 Invalid Input Error (Device Selection)

**Location:** `main.py:232`

**Current:**
```python
print("Invalid input. Please enter a number.")
```

**Analysis:**
- ❌ Generic - doesn't specify which numbers are valid
- ❌ No context about what the number represents

**Recommended:**
```python
print(f"❌ Invalid input. Please enter a device number between 1 and {len(discovered_devices) + 1}.")
```

---

#### 4.1.4.2 No Devices Found Error

**Location:** `main.py:241`

**Current:**
```python
print("No HDHomeRun devices found. Retrying in 3 seconds...")
```

**Analysis:**
- ✅ Good: Tells user what's happening next
- ❌ Doesn't explain WHY (common causes)
- ❌ No troubleshooting hints

**Recommended:**
```python
print("⚠️  No HDHomeRun devices found on the network.")
print("   Common causes:")
print("   - Device is powered off")
print("   - Device is on a different network/VLAN")
print("   - Firewall is blocking discovery")
print("\nRetrying in 3 seconds...")
```

**After Retry Failure (line 247):**
```python
print("\n⚠️  No HDHomeRun devices found after retry.")
print("   For troubleshooting help, run: python3 main.py --debug")
retry_input = input("\nWould you like to try again? [y/N]: ").strip().lower()
```

---

#### 4.1.4.3 Tuner Locked Error

**Location:** `main.py:604`

**Current:**
```python
print(f"Tuner {tuner} is locked by another resource. Skipping to next tuner.")
```

**Analysis:**
- ✅ Good: Explains what's happening
- ✅ Good: Tells user next action
- ❌ Doesn't suggest solutions
- ❌ Doesn't identify what might be locking it

**Recommended:**
```python
print(f"⚠️  Tuner {tuner} is locked by another application.")
print(f"   (Could be: TV software, recording in progress, or another scan)")
if tuner < len(tuners) - 1:
    print(f"   → Trying tuner {tuners[tuners.index(tuner) + 1]} instead...")
else:
    print(f"   → No more tuners available to try.")
```

---

#### 4.1.4.4 Permission Denied Error

**Location:** `main.py:989`

**Current:**
```python
print(f"Error: Cannot write to file '{filename}'. Check permissions.")
```

**Analysis:**
- ✅ Good: Identifies the file
- ❌ Doesn't suggest alternatives
- ❌ Doesn't offer to display instead

**Recommended:**
```python
print(f"❌ Error: Cannot write to file '{filename}'")
print(f"   Directory: {os.path.dirname(os.path.abspath(filename)) or 'current directory'}")
print(f"   Reason: No write permission")
print(f"\n   Solutions:")
print(f"   1. Run with different output path: --output /tmp/scan.csv")
print(f"   2. Run with --no-save to display results instead")
print(f"   3. Fix permissions: chmod +w {os.path.dirname(filename) or '.'}")
```

---

#### 4.1.4.5 OpenAI API Key Missing

**Location:** `main.py:732`

**Current:**
```python
print("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
```

**Analysis:**
- ✅ Good: Clear problem statement
- ❌ Doesn't show how to set it
- ❌ Doesn't offer to continue without it

**Recommended:**
```python
print("⚠️  OpenAI API key not found.")
print("   To enable geographic identification, set your API key:")
print("   export OPENAI_API_KEY='your-key-here'")
print("\n   Get a key at: https://platform.openai.com/api-keys")
print("   → Continuing without OpenAI integration...")
```

---

### 4.1.5 Success Message Quality

#### 4.1.5.1 Scan Completion

**Location:** `main.py:1071`

**Current:**
```python
print("\nScan completed successfully!")
```

**Analysis:**
- ✅ Simple and clear
- ❌ Doesn't summarize what was accomplished
- ❌ Doesn't tell user what to do next
- ❌ Doesn't mention where files are

**Recommended:**
```python
print("\n" + "="*60)
print("✅ Scan completed successfully!")
print("="*60)
if saved_file:
    print(f"📄 Results saved to: {os.path.abspath(saved_file)}")
    print(f"   ({os.path.getsize(saved_file)} bytes, {len(parsed_data)} channels)")
if openai_response:
    print(f"📍 Location: {openai_response}")
print(f"📋 Log file: {os.path.abspath('hdhr_scan.log')}")
print("\nThank you for using HDHomeRun Channel Scanner!")
```

---

#### 4.1.5.2 CSV File Write Success

**Location:** `main.py:1029`

**Current:**
```python
print(f"Data successfully written to '{filename}'.")
```

**Analysis:**
- ✅ Confirms action
- ❌ Doesn't show full path
- ❌ Doesn't show record count
- ❌ Doesn't confirm what's in the file

**Recommended:**
```python
full_path = os.path.abspath(filename)
record_count = len(parsed_data)
file_size = os.path.getsize(filename)
print(f"\n✅ Data successfully written to CSV file:")
print(f"   📄 File: {full_path}")
print(f"   📊 Records: {record_count} frequency entries")
print(f"   💾 Size: {file_size:,} bytes")
```

---

## 4.2 Progress and Feedback Audit

### 4.2.1 Device Discovery Feedback

**Location:** `main.py:143-162`

**Current Behavior:**
```python
# Line 143: No feedback before starting
result = subprocess.run(["hdhomerun_config", "discover", "-4"], ...)
# Line 162: First feedback after discovery completes
logger.info(f"Discovered {len(devices)} HDHomeRun device(s)")
```

**Timeline:**
1. User selects device (implied, no message)
2. **[SILENCE - 0-10 seconds]**
3. Device list appears

#### Analysis

**❌ Issues:**
1. **Silent operation**: No indication that discovery is starting
2. **Unknown duration**: Can take 1-10 seconds, user doesn't know if it's working
3. **No timeout indication**: Times out at 10 seconds, but user isn't warned

**User Experience:**
- User doesn't know if the program hung or is working
- On slow networks, appears frozen

#### Recommendations

**Add Immediate Feedback:**
```python
# Before line 143
print("🔍 Searching for HDHomeRun devices on your network...")
print("   (This may take up to 10 seconds)")

logger.debug("Attempting to discover HDHomeRun devices")
result = subprocess.run(...)

# After successful discovery
if len(devices) == 0:
    print("   → No devices found")
elif len(devices) == 1:
    print(f"   → Found 1 device")
else:
    print(f"   → Found {len(devices)} devices")
```

**Effort:** 10 minutes
**Impact:** High - Eliminates confusion about whether program is working

---

### 4.2.2 Channel Scanning Feedback

**Location:** `main.py:586-622`

**Current Behavior:**
```python
# Line 589: Initial message
print(f"\nScanning tuner {tuner} on device {device_id}...")

# Line 591-596: Silent scan for up to 5 MINUTES
result = subprocess.run([...], timeout=300)

# Line 615: First feedback after scan completes
print(f"Scan completed for tuner {tuner}.")

# Line 621: Summary stats
print(f"Scanned {scan_count} frequencies, successfully locked on {lock_count} channels.")
```

**Timeline:**
1. "Scanning tuner X..." message
2. **[SILENCE - UP TO 5 MINUTES]** ⚠️ CRITICAL ISSUE
3. "Scan completed..."
4. Stats summary

#### Analysis

**❌ CRITICAL ISSUES:**
1. **5-minute black hole**: User has NO idea if scan is working or hung
2. **No progress indication**: Can't estimate completion time
3. **No incremental feedback**: Real-time data available but not shown
4. **No way to tell if scanning vs analyzing**: User doesn't know what's happening
5. **Cancellation unclear**: Can user press Ctrl+C? Will data be lost?

**User Experience:**
- User stares at terminal for 5 minutes wondering if it's broken
- This was identified as **CF-2 (Critical Friction)** in Part 3

#### Recommendations

**Option 1: Real-Time Progress (Best UX)**
```python
import threading
import sys

def scan_with_progress(device_id: str, tuner: int) -> List[str]:
    """Scan tuner with real-time progress feedback."""

    print(f"\n📡 Scanning tuner {tuner} on device {device_id}...")
    print("   Progress will be shown in real-time (this takes 3-5 minutes)")
    print("   Press Ctrl+C to cancel\n")

    # Use Popen for real-time output
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

    try:
        for line in process.stdout:
            lines.append(line.strip())

            # Show progress for each frequency scanned
            if line.startswith('SCANNING:'):
                scan_count += 1
                # Extract frequency and channel
                match = re.search(r'(\d+) \(us-bcast:(\d+)\)', line)
                if match:
                    freq = match.group(1)
                    channel = match.group(2)
                    # Update same line
                    print(f"\r   Scanning: Channel {channel} ({scan_count} frequencies checked)     ", end='', flush=True)

            elif line.startswith('LOCK:') and 'none' not in line:
                lock_count += 1
                print(f"\r   ✅ Locked: Channel {channel} (Total locks: {lock_count})             ")

        process.wait()
        print(f"\n\n✅ Scan completed!")
        print(f"   📊 Scanned {scan_count} frequencies")
        print(f"   🔒 Successfully locked on {lock_count} channels\n")

        return lines

    except KeyboardInterrupt:
        process.terminate()
        print("\n\n⚠️  Scan cancelled by user.")
        print(f"   Partial results available: {scan_count} frequencies scanned, {lock_count} locked")
        raise
```

**Option 2: Periodic Updates (Simpler)**
```python
# Before scan
print(f"\n📡 Scanning tuner {tuner}...")
print("   This will take 3-5 minutes. Progress updates every 30 seconds.")
print("   Press Ctrl+C to cancel\n")

# Add progress thread
def show_progress(stop_event, start_time):
    while not stop_event.is_set():
        elapsed = int(time.time() - start_time)
        print(f"   ... still scanning ... ({elapsed}s elapsed)", flush=True)
        time.sleep(30)

stop_event = threading.Event()
start_time = time.time()
progress_thread = threading.Thread(target=show_progress, args=(stop_event, start_time))
progress_thread.start()

try:
    result = subprocess.run([...], timeout=300)
finally:
    stop_event.set()
    progress_thread.join()
```

**Option 3: Spinner (Minimal Change)**
```python
import itertools
import threading

def spinner_task(message, stop_event):
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    while not stop_event.is_set():
        sys.stdout.write(f'\r{message} {next(spinner)}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * (len(message) + 2) + '\r')

stop_event = threading.Event()
spinner_thread = threading.Thread(target=spinner_task, args=("Scanning tuner (this may take 5 minutes)...", stop_event))
spinner_thread.start()

try:
    result = subprocess.run([...], timeout=300)
finally:
    stop_event.set()
    spinner_thread.join()
    print("Scan completed!")
```

**Effort:**
- Option 1: 2-3 hours (best UX)
- Option 2: 1 hour (good compromise)
- Option 3: 30 minutes (minimal improvement)

**Impact:** CRITICAL - Fixes the #1 UX problem in the application

---

### 4.2.3 Parsing Feedback

**Location:** `main.py:970-980`

**Current Behavior:**
```python
# Line 971: Before parsing
print("\nParsing scan results...")

# Line 972: Immediate parsing (fast operation)
parsed_data = parse_results_info(results)

# Line 980: After parsing
print(f"Successfully parsed {len(parsed_data)} frequency entries.")
```

**Timeline:**
- "Parsing..." message
- **[< 1 second typically]**
- "Successfully parsed X entries"

#### Analysis

**✅ Strengths:**
- Feedback before and after
- Shows count of parsed entries
- Operation is fast enough that progress isn't critical

**❌ Minor Issues:**
1. For large scans (100+ channels), parsing can take 2-3 seconds with no feedback
2. No validation feedback (signal quality warnings are only in logs)

#### Recommendations

**For Large Datasets:**
```python
print("\nParsing scan results...")
if len(results) > 500:
    print("   (Large dataset detected, this may take a moment...)")

parsed_data = parse_results_info(results)

# Show validation warnings to user, not just logs
warning_count = sum(1 for data in parsed_data
                   if int(data.get('Signal to Noise Quality', '0')) > 100
                   or int(data.get('Symbol Error Quality', '0')) > 100)

print(f"✅ Successfully parsed {len(parsed_data)} frequency entries")
if warning_count > 0:
    print(f"   ⚠️  {warning_count} entries have unusual signal quality values (see log for details)")
```

**Effort:** 15 minutes
**Impact:** Low - Operation is already fast

---

### 4.2.4 File Writing Feedback

**Location:** `main.py:993-1029`

**Current Behavior:**
```python
# Line 995: Before writing
print(f"\nWriting data to '{filename}'...")

# Line 997-1026: Write operation (silent)
with open(filename, 'w', newline='') as output_file:
    # ... writing happens ...

# Line 1029: After writing
print(f"Data successfully written to '{filename}'.")
```

#### Analysis

**✅ Strengths:**
- Feedback before and after
- Operation is typically fast (<1 second)

**❌ Issues:**
1. Doesn't show WHERE file was written (relative vs absolute path)
2. Doesn't show file SIZE or record COUNT
3. Doesn't confirm file is openable/readable

#### Recommendations

**Enhanced Feedback:**
```python
print(f"\n💾 Writing data to CSV file...")

with open(filename, 'w', newline='') as output_file:
    # ... writing logic ...

# Verify and report
full_path = os.path.abspath(filename)
file_size = os.path.getsize(filename)
record_count = len(parsed_data)

print(f"✅ Data successfully written!")
print(f"   📄 File: {full_path}")
print(f"   📊 Records: {record_count} frequency entries")
print(f"   💾 Size: {file_size:,} bytes")
print(f"\n   To open: open {filename}  # macOS")
print(f"            xdg-open {filename}  # Linux")
```

**Effort:** 20 minutes
**Impact:** Medium - Helps users locate and verify their files

---

### 4.2.5 OpenAI Query Feedback

**Location:** `main.py:1049-1068`

**Current Behavior:**
```python
# Line 1050: Before query
print("\nQuerying OpenAI to identify geographic region...")

# Line 1056: Silent API call (1-5 seconds)
openai_response = get_openai_response(full_text)

# Line 1060: After response
print(f"\nThe broadcast region is: {openai_response}")
```

#### Analysis

**✅ Strengths:**
- Feedback before query
- Clean result display

**❌ Issues:**
1. No indication of wait time (can be 1-10 seconds)
2. No feedback during API call
3. Doesn't show what was sent (useful for debugging)

#### Recommendations

**Add Spinner:**
```python
print("\n🤖 Querying OpenAI to identify geographic region...")
print("   (This may take 5-10 seconds)")

# Show what we're sending (in debug mode)
if logger.level == logging.DEBUG:
    print(f"   Sending {len(stations_list)} station call signs...")

openai_response = get_openai_response(full_text)

if openai_response:
    print(f"\n✅ The broadcast region is: {openai_response}")
else:
    print("\n⚠️  Could not determine region from OpenAI.")
```

**Effort:** 10 minutes
**Impact:** Low - Operation is reasonably fast

---

## 4.3 Error Recovery Path Audit

### 4.3.1 Invalid Input Recovery (Device Selection)

**Location:** `main.py:215-236`

**Current Implementation:**
```python
while True:  # Infinite loop
    try:
        user_input = input("\nEnter the device number: ").strip()
        choice = int(user_input) - 1

        if 0 <= choice < len(discovered_devices):
            # Valid choice - return
            return selected
        elif choice == len(discovered_devices):
            # Rediscover - break inner loop
            break
        else:
            # Invalid range
            print(f"Invalid choice. Please enter a number between 1 and {len(discovered_devices) + 1}")
    except ValueError:
        # Non-numeric input
        print("Invalid input. Please enter a number.")
    except KeyboardInterrupt:
        # User cancellation
        return ""
```

#### Analysis

**✅ Strengths:**
- Infinite retries allowed
- Separate handling for ValueError vs range error
- KeyboardInterrupt handled gracefully

**❌ Weaknesses:**
1. **No retry limit**: User could be stuck forever on wrong input
2. **No help escalation**: After 2-3 failures, should offer help
3. **No example**: Doesn't show "Example: enter 1 for first device"
4. **No context retention**: Redisplays same menu without learning

#### Recommendations

**Add Retry Limit with Help Escalation:**
```python
retry_count = 0
MAX_RETRIES = 5

while retry_count < MAX_RETRIES:
    try:
        user_input = input("\nEnter the device number: ").strip()

        # Show help after 2 failures
        if retry_count == 2:
            print("\n💡 Tip: Enter the number shown before the device (e.g., '1' for the first device)")
            print("   Or press Ctrl+C to exit\n")

        choice = int(user_input) - 1

        if 0 <= choice < len(discovered_devices):
            return discovered_devices[choice]
        elif choice == len(discovered_devices):
            logger.info("User requested device rediscovery")
            break
        else:
            retry_count += 1
            print(f"❌ Invalid choice. Please enter a number between 1 and {len(discovered_devices) + 1}")

    except ValueError:
        retry_count += 1
        print("❌ Invalid input. Please enter a number (not text).")
        if retry_count == 1:
            print("   Example: Enter '1' to select the first device")

    except KeyboardInterrupt:
        logger.info("User cancelled device selection")
        print("\n✋ Operation cancelled.")
        return ""

# Hit retry limit
print(f"\n⚠️  Too many invalid attempts ({MAX_RETRIES}). Exiting.")
logger.warning(f"User exceeded retry limit on device selection")
return ""
```

**Effort:** 30 minutes
**Impact:** Medium - Prevents infinite loops and helps confused users

---

### 4.3.2 Invalid Input Recovery (Tuner Selection)

**Location:** `main.py:284-307`

**Current Implementation:**
```python
max_attempts = 3
for attempt in range(max_attempts):
    try:
        user_input = input("\nEnter the mode number: ").strip()
        choice = int(user_input)

        if 0 <= choice <= 4:
            return choice
        else:
            print(f"Invalid choice. Please enter a number between 0 and 4.")

    except ValueError:
        print("Invalid input. Please enter a number.")
    except KeyboardInterrupt:
        return -1

# After 3 attempts
print(f"Too many invalid attempts. Exiting.")
return -1
```

#### Analysis

**✅ Strengths:**
- Has retry limit (3 attempts)
- Clean error messages
- Returns error code (-1) after failures

**❌ Weaknesses:**
1. **No help escalation**: Same error message each time
2. **Retry count not shown**: User doesn't know how many chances left
3. **No suggestion**: Doesn't recommend auto mode (4) as safe default
4. **Inconsistent with device selection**: Different retry limits (3 vs infinite)

#### Recommendations

**Add Help and Attempt Counter:**
```python
MAX_ATTEMPTS = 5  # More generous
for attempt in range(MAX_ATTEMPTS):
    try:
        if attempt > 0:
            remaining = MAX_ATTEMPTS - attempt
            print(f"   ({remaining} attempt{'s' if remaining != 1 else ''} remaining)")

        user_input = input("\nEnter tuner number: ").strip()

        # Provide help after 2 failures
        if attempt == 2:
            print("\n💡 Tip: If you're unsure which tuner to use, select '4' for Auto mode")
            print("   Auto mode will try each tuner until it finds one that works.\n")
            continue

        choice = int(user_input)

        if 0 <= choice <= 4:
            logger.info(f"User selected tuner mode: {choice}")
            return choice
        else:
            print(f"❌ Invalid choice. Please enter a number between 0 and 4.")
            print("   Example: Enter '4' for Auto mode (recommended)")

    except ValueError:
        print("❌ Invalid input. Please enter a number (not text).")
        if attempt == 0:
            print("   Example: Enter '4' for Auto mode")

    except KeyboardInterrupt:
        logger.info("User cancelled tuner selection")
        print("\n✋ Operation cancelled.")
        return -1

# After max attempts
print(f"\n⚠️  Too many invalid attempts. Exiting.")
logger.error(f"User exceeded retry limit ({MAX_ATTEMPTS}) on tuner selection")
return -1
```

**Effort:** 30 minutes
**Impact:** Medium - Helps users understand auto mode

---

### 4.3.3 Device Discovery Failure Recovery

**Location:** `main.py:238-254`

**Current Implementation:**
```python
else:  # No devices found
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
```

#### Analysis

**✅ Strengths:**
- Automatic retry (1 time)
- Manual retry option
- Clear messaging

**❌ Weaknesses:**
1. **No troubleshooting guidance**: Doesn't explain why devices might not be found
2. **No diagnostic commands**: Could suggest running with --debug
3. **No network check**: Could verify network connectivity
4. **Timer interruption**: 3-second wait not cancellable

#### Recommendations

**Enhanced Troubleshooting:**
```python
else:  # No devices found
    if retry_count < 1:  # First failure - automatic retry
        print("\n⚠️  No HDHomeRun devices found on initial scan.")
        print("   Retrying in 3 seconds...")
        time.sleep(3)
        retry_count += 1
        continue
    else:  # Second failure - offer help
        print("\n❌ No HDHomeRun devices found after retry.\n")
        print("Troubleshooting checklist:")
        print("  ☐ Is your HDHomeRun device powered on?")
        print("  ☐ Is it connected to the same network as this computer?")
        print("  ☐ Is your firewall allowing device discovery?")
        print("  ☐ Can you ping the device's IP address?")
        print("\nFor detailed diagnostics, run: python3 main.py --debug")

        retry_input = input("\nWould you like to try again? [y/N]: ").strip().lower()

        if retry_input == 'y':
            logger.info("User requested manual retry after troubleshooting")
            retry_count = 0  # Reset counter
            continue
        else:
            logger.info("User chose to exit after device discovery failure")
            print("\n💡 Tip: You can also test with sample data using: --test-file flag")
            return ""
```

**Effort:** 20 minutes
**Impact:** High - Helps users diagnose common problems

---

### 4.3.4 Tuner Lock Failure Recovery

**Location:** `main.py:601-646`

**Current Implementation:**
```python
# Check for resource locked
if any("ERROR: resource locked" in line for line in lines):
    logger.warning(f"Tuner {tuner} is locked")
    print(f"Tuner {tuner} is locked by another resource. Skipping to next tuner.")
    continue

# Check for lock failure
lock_success = any(line.startswith('LOCK:') and 'none' not in line for line in lines)
if not lock_success:
    logger.warning(f"Tuner {tuner} failed to lock")
    print(f"Tuner {tuner} failed to lock on any frequency.")
    continue

# ... tries next tuner ...

# After all tuners fail (line 644)
logger.warning("All tuners are either locked or failed to lock")
print("\nAll tuners are either locked or failed to lock.")
return []
```

#### Analysis

**✅ Strengths:**
- Automatically tries next tuner
- Distinguishes between "locked" and "failed to lock"
- Logs all attempts

**❌ Weaknesses:**
1. **No explanation WHY lock failed**: Signal issues? Antenna disconnected?
2. **No troubleshooting for "all tuners locked"**: What should user do?
3. **No partial results offered**: If one tuner got partial data, should offer it
4. **No retry option**: After all fail, just exits

#### Recommendations

**Enhanced Error Recovery:**
```python
# After individual tuner lock failure
if not lock_success:
    logger.warning(f"Tuner {tuner} failed to lock on any frequency")
    print(f"\n⚠️  Tuner {tuner} failed to lock on any frequency.")

    # Check if this is signal vs config issue
    if scan_count > 0:
        print(f"   Tuner scanned {scan_count} frequencies but couldn't lock.")
        print(f"   Possible causes:")
        print(f"   • Weak antenna signal")
        print(f"   • Antenna not connected")
        print(f"   • Wrong tuner mode (should be 8VSB for ATSC)")
    else:
        print(f"   Tuner didn't scan any frequencies.")
        print(f"   Possible causes:")
        print(f"   • Tuner hardware issue")
        print(f"   • Device firmware needs update")

    if tuner < len(tuners) - 1:
        print(f"\n   → Trying next tuner...")
    continue

# After ALL tuners fail
logger.warning("All tuners are either locked or failed to lock")
print("\n❌ All tuners are either locked or failed to lock.\n")
print("Troubleshooting steps:")
print("  1. Check antenna connection to HDHomeRun device")
print("  2. Verify antenna signal strength (try TV directly)")
print("  3. Check if another application is using the tuners:")
print("     • DVR recording software")
print("     • HDHomeRun app")
print("     • Another scan in progress")
print("  4. Restart the HDHomeRun device")
print("\nFor detailed diagnostics: python3 main.py --debug")

retry = input("\nWould you like to try again? [y/N]: ").strip().lower()
if retry == 'y':
    return query_tuner(device_id, tuners)  # Recursive retry
else:
    return []
```

**Effort:** 45 minutes
**Impact:** High - Lock failures are common, guidance is critical

---

### 4.3.5 File Permission Error Recovery

**Location:** `main.py:986-991`

**Current Implementation:**
```python
# Check file permissions
if not check_file_writable(filename):
    print(f"Error: Cannot write to file '{filename}'. Check permissions.")
    logger.error(f"Cannot write to file: {filename}")
    return 1  # EXIT THE ENTIRE PROGRAM ❌
```

#### Analysis

**❌ CRITICAL ISSUES:**
1. **DATA LOSS**: Exits program, losing all scan data (5+ minutes of work)
2. **No alternatives offered**: Could display instead, try different path, etc.
3. **No recovery path**: Should loop back and ask for different filename
4. **Inconsistent with "no-save" mode**: That mode displays data, this should too

**This is CF-1 (Critical Friction) from Part 3**

#### Recommendations

**Offer Recovery Options:**
```python
# Check file permissions
if not check_file_writable(filename):
    print(f"\n❌ Cannot write to file: {filename}")
    print(f"   Directory: {os.path.dirname(os.path.abspath(filename)) or '.'}")
    logger.error(f"File not writable: {filename}")

    print("\n📋 Your scan data is ready but cannot be saved to this location.")
    print("   What would you like to do?\n")
    print("   1) Display results on screen instead")
    print("   2) Try a different file location")
    print("   3) Exit and lose the data")

    while True:
        choice = input("\nEnter choice (1-3): ").strip()

        if choice == '1':
            # Display results
            logger.info("User chose to display results instead of saving")
            print("\n📊 Scan Results:")
            print("="*80)
            for idx, data in enumerate(parsed_data, 1):
                print(f"\n[{idx}] Frequency: {data.get('Frequency', 'N/A')}")
                print(f"    Channel: {data.get('US-Bcast Channel', 'N/A')}")
                print(f"    Lock: {data.get('Lock', 'N/A')}")
                print(f"    Signal Strength: {data.get('Signal Strength (dBmV)', 'N/A')} dBmV")
                # ... show more fields ...
            print("="*80)
            break  # Continue to OpenAI prompt

        elif choice == '2':
            # Try different location
            new_filename = input("\nEnter new file path: ").strip()
            if check_file_writable(new_filename):
                filename = new_filename
                logger.info(f"User provided alternate path: {filename}")
                break  # Continue with new filename
            else:
                print(f"❌ Still cannot write to: {new_filename}")
                print("   Try again or choose option 1 or 3.")

        elif choice == '3':
            # Exit
            logger.warning("User chose to exit after permission error")
            print("\n⚠️  Exiting without saving. Scan data will be lost.")
            return 1

        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
```

**Effort:** 45 minutes
**Impact:** CRITICAL - Prevents data loss after 5-minute scan

---

### 4.3.6 OpenAI Error Recovery

**Location:** `main.py:755-783`

**Current Implementation:**
Multiple specific exception handlers that all print error and return empty string:

```python
except openai.error.AuthenticationError:
    print("Error: Invalid OpenAI API key...")
    return ""

except openai.error.RateLimitError:
    print("Error: OpenAI rate limit exceeded...")
    return ""

# ... etc ...
```

**Caller handling (line 1058-1068):**
```python
if openai_response:
    print(f"\nThe broadcast region is: {openai_response}")
else:
    print("Could not get a response from OpenAI.")
# ... continues program ...
```

#### Analysis

**✅ Strengths:**
- Specific exception handling
- Program continues without OpenAI
- Doesn't lose data on OpenAI failure

**❌ Weaknesses:**
1. **No retry option**: Rate limits or network blips could be retried
2. **Generic failure message**: "Could not get response" doesn't explain why
3. **No manual fallback**: Could ask user to enter their city manually

#### Recommendations

**Add Retry and Manual Fallback:**
```python
# In get_openai_response function
def get_openai_response(prompt: str, retry_count: int = 0) -> str:
    """Get OpenAI response with retry logic."""

    MAX_RETRIES = 2

    # ... existing code ...

    except openai.error.RateLimitError:
        logger.error("OpenAI rate limit exceeded")
        if retry_count < MAX_RETRIES:
            wait_time = 2 ** retry_count  # Exponential backoff
            print(f"⚠️  OpenAI rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            return get_openai_response(prompt, retry_count + 1)
        else:
            print("❌ OpenAI rate limit exceeded after retries.")
            return ""

    except openai.error.APIConnectionError:
        if retry_count < MAX_RETRIES:
            print(f"⚠️  Connection error. Retrying...")
            time.sleep(2)
            return get_openai_response(prompt, retry_count + 1)
        else:
            print("❌ Unable to connect to OpenAI API after retries.")
            return ""

# In main() after OpenAI call
if openai_response:
    print(f"\n📍 The broadcast region is: {openai_response}")
else:
    print("\n⚠️  Could not determine region from OpenAI.")
    manual_entry = input("Would you like to manually enter your city/region? [y/N]: ").strip().lower()
    if manual_entry == 'y':
        location = input("Enter city and state: ").strip()
        logger.info(f"User manually entered location: {location}")
        print(f"✅ Location recorded as: {location}")
```

**Effort:** 30 minutes
**Impact:** Low - OpenAI is optional feature

---

## 4.4 Command-Line Arguments UX Audit

### 4.4.1 Help Text Quality

**Location:** `main.py:864-875`

**Current Implementation:**
```python
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
```

**Output of `--help`:**
```
usage: main.py [-h] [--debug] [--test-file] [--no-save] [--auto-openai] [--output OUTPUT]

HDHomeRun Channel Scanner - Scan and analyze OTA TV channels

optional arguments:
  -h, --help            show this help message and exit
  --debug               Enable debug logging
  --test-file           Use local ScanData.txt file for testing
  --no-save             Do not save results to CSV file
  --auto-openai         Automatically query OpenAI without prompting
  --output OUTPUT, -o OUTPUT
                        Specify output CSV filename

Examples:
  main.py                    # Interactive mode
  main.py --debug            # Enable debug logging
  main.py --test-file        # Use local test file
  main.py --no-save          # Don't save to CSV
  main.py --auto-openai      # Automatically query OpenAI
```

#### Analysis

**✅ Strengths:**
- All flags documented
- Examples provided
- Clean description
- Short form provided for --output

**❌ Weaknesses:**
1. **No version flag**: Standard CLIs have `--version`
2. **Examples don't show combinations**: Real usage often combines flags
3. **No explanation of requirements**: Doesn't mention hdhomerun_config needed
4. **No explanation of defaults**: What happens in interactive mode?
5. **Missing important examples**:
   - Complete automation example
   - --debug for troubleshooting
   - Test mode for offline use

#### Recommendations

**Enhanced Help Text:**
```python
parser = argparse.ArgumentParser(
    description='HDHomeRun Channel Scanner - Scan and analyze OTA TV channels',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''
Description:
  Discovers HDHomeRun devices on your network, scans for OTA TV channels,
  and exports results to CSV. Optionally uses OpenAI to identify your
  broadcast region based on detected station call signs.

Requirements:
  • HDHomeRun device on your local network
  • hdhomerun_config utility (https://www.silicondust.com/support/downloads/)
  • Python 3.7+
  • Optional: OpenAI API key for geographic identification

Examples:
  # Basic interactive mode (recommended for first-time users)
  %(prog)s

  # Enable detailed logging for troubleshooting
  %(prog)s --debug

  # Test mode using sample data (no device needed)
  %(prog)s --test-file

  # Quick scan without saving (display only)
  %(prog)s --no-save

  # Fully automated scan with custom output
  %(prog)s --output my_channels.csv --auto-openai --debug

  # Automated scan for scripting (quiet mode)
  %(prog)s --output scan.csv --auto-openai 2>/dev/null

Exit Codes:
  0   Success
  1   Error occurred (check logs)
  130 User cancelled (Ctrl+C)

Log Files:
  Detailed logs written to: hdhr_scan.log
  Use --debug for verbose logging

More Information:
  GitHub: https://github.com/yourusername/hdhr-scan-frequencies
  HDHomeRun Support: https://www.silicondust.com/support/
    '''
)

# Add version flag
parser.add_argument('--version', action='version', version='%(prog)s 3.0')
```

**Effort:** 30 minutes
**Impact:** Medium - Better first-time user experience

---

### 4.4.2 Flag Naming Evaluation

**Current Flags:**
- `--debug` ✅ Standard
- `--test-file` ⚠️ Could be clearer
- `--no-save` ✅ Clear negative flag
- `--auto-openai` ⚠️ Specific to implementation
- `--output` / `-o` ✅ Standard

#### Analysis

**Issues:**
1. **`--test-file`**: Implies you provide a file path, but actually looks for hardcoded 'ScanData.txt'
2. **`--auto-openai`**: Exposes implementation detail (OpenAI), not user goal
3. **No short forms**: Only -o has short form, others don't
4. **No verbose flag**: `--debug` affects logs, but no `--verbose` for screen output

#### Recommendations

**Improved Flag Names:**

```python
# Better: --test-mode or --offline
parser.add_argument('--test-mode', '--test-file', dest='use_test_file',
                   action='store_true',
                   help='Use local ScanData.txt file for testing (no device needed)')

# Better: --identify-region or --auto-locate
parser.add_argument('--identify-region', '--auto-openai', dest='auto_identify',
                   action='store_true',
                   help='Automatically identify broadcast region (requires OpenAI API key)')

# Add verbose flag
parser.add_argument('--verbose', '-v', action='store_true',
                   help='Show detailed progress during operations')

# Add quiet flag
parser.add_argument('--quiet', '-q', action='store_true',
                   help='Minimize output (errors only)')

# Add short forms for common flags
parser.add_argument('--debug', '-d', action='store_true',
                   help='Enable debug logging')
```

**Backward Compatibility:**
Keep old flag names as hidden aliases for existing scripts.

**Effort:** 45 minutes (includes testing)
**Impact:** Medium - Better aligns with CLI conventions

---

### 4.4.3 Flag Interaction Validation

**Current State:** No validation of conflicting flags

#### Test Cases

**Test 1: `--no-save` + `--output`**
```bash
python3 main.py --no-save --output scan.csv
```
**Current Behavior:**
- Both flags set
- Skips save prompt (due to --no-save)
- Output filename is generated but never used
- Confusing!

**Expected Behavior:**
```
⚠️  Warning: --output specified but --no-save flag will prevent file creation.
   Remove --no-save flag if you want to save results.
```

---

**Test 2: `--test-file` + device selection**
```bash
python3 main.py --test-file
```
**Current Behavior:**
- Skips device discovery (correct)
- Goes straight to parsing ScanData.txt (correct)
- If file missing, errors out (correct)

**Issue:** Still prompts for save/OpenAI even though test data is fake

**Expected Behavior:**
```
📋 Test Mode: Using sample data from ScanData.txt
   Note: Results will not reflect your actual location.

[... scanning ...]

Save results to CSV? [y/N]: y
⚠️  Note: This is test data. Results may not be meaningful.
```

---

**Test 3: `--auto-openai` without API key**
```bash
unset OPENAI_API_KEY
python3 main.py --auto-openai
```
**Current Behavior:**
- Runs scan
- Attempts OpenAI query
- Fails with "API key not found"
- Continues and exits

**Expected Behavior:**
Pre-flight check at startup:
```
❌ Error: --auto-openai flag requires OPENAI_API_KEY environment variable

   Set your API key: export OPENAI_API_KEY='your-key-here'
   Or run without --auto-openai flag for interactive mode.

Exiting.
```

---

#### Recommendations

**Add Flag Validation:**
```python
# In main(), after parsing args
args = parser.parse_args()

# Validate flag combinations
if args.no_save and args.output:
    print("⚠️  Warning: --output ignored because --no-save flag is set.")
    print("   Remove --no-save if you want to save results to a file.\n")
    args.output = None

if args.auto_openai and not os.environ.get("OPENAI_API_KEY"):
    print("❌ Error: --auto-openai requires OPENAI_API_KEY environment variable")
    print("\n   Set your API key:")
    print("   export OPENAI_API_KEY='your-key-here'")
    print("\n   Or run without --auto-openai for interactive mode.")
    return 1

if args.quiet and args.verbose:
    print("❌ Error: Cannot use --quiet and --verbose together")
    return 1

if args.use_test_file:
    if not os.path.exists('ScanData.txt'):
        print("❌ Error: Test file 'ScanData.txt' not found")
        print("   Test mode requires a ScanData.txt file in the current directory.")
        return 1
    print("📋 Test Mode: Using sample data from ScanData.txt\n")
```

**Effort:** 30 minutes
**Impact:** Medium - Prevents user confusion

---

### 4.4.4 Missing Useful Flags

#### Suggested Additions

**1. `--list-devices`** - Just list devices and exit
```python
parser.add_argument('--list-devices', action='store_true',
                   help='List available HDHomeRun devices and exit')

# In main()
if args.list_devices:
    devices = discover_devices()
    if devices:
        print("Found HDHomeRun devices:")
        for i, device in enumerate(devices, 1):
            print(f"  {i}) {device}")
        return 0
    else:
        print("No devices found.")
        return 1
```

**2. `--device-id`** - Skip device selection
```python
parser.add_argument('--device-id', type=str,
                   help='Specify device ID to skip selection (e.g., 12345678)')

# In main()
if args.device_id:
    device_number = args.device_id
else:
    selected_device = select_device()
    device_number = selected_device.split()[2]
```

**3. `--tuner`** - Skip tuner selection
```python
parser.add_argument('--tuner', type=int, choices=[0,1,2,3,4],
                   help='Specify tuner (0-3) or 4 for auto mode')

# In main()
if args.tuner is not None:
    mode = args.tuner
else:
    mode = select_tuner_mode()
```

**4. `--timeout`** - Configure scan timeout
```python
parser.add_argument('--timeout', type=int, default=300,
                   help='Scan timeout in seconds (default: 300)')
```

**5. `--format`** - Output format options
```python
parser.add_argument('--format', choices=['csv', 'json', 'text'], default='csv',
                   help='Output format (default: csv)')
```

**Full Automation Example:**
```bash
python3 main.py --device-id 12345678 --tuner 4 --output scan.csv --auto-openai --quiet
```

**Effort:** 2-3 hours for all additions
**Impact:** High - Enables scripting and automation

---

## 4.5 Output Quality Audit

### 4.5.1 Screen Display Output

#### Current Console Output

**Typical Run:**
```
Select an HDHomeRun device:
1) hdhomerun device 12345678 found at 192.168.1.100
2) Rediscover devices

Enter the device number: 1

Select a tuner or Auto mode:
0) Tuner 0
1) Tuner 1
2) Tuner 2
3) Tuner 3
4) Auto mode (Try all tuners)

Enter the mode number: 4

Scanning tuner 0 on device 192.168.1.100...
Scan completed for tuner 0.
Scanned 69 frequencies, successfully locked on 23 channels.

Parsing scan results...
Successfully parsed 23 frequency entries.

Save results to a CSV file? (1=yes / 2=no): 1

Writing data to 'hostname_20251119_14.csv'...
Data successfully written to 'hostname_20251119_14.csv'.

Send results to OpenAI to determine the city/region? (1=yes / 2=no): 1

Querying OpenAI to identify geographic region...

The broadcast region is: Los Angeles, California

Scan completed successfully!
```

#### Analysis

**✅ Strengths:**
- Clean, step-by-step flow
- Clear prompts
- Confirmation messages

**❌ Weaknesses:**
1. **No visual hierarchy**: Everything same importance
2. **No use of formatting**: No colors, bold, or emphasis
3. **Too much scrollback**: Long scans scroll off screen
4. **No summary table**: Doesn't show key info at a glance
5. **Missing context**: Doesn't show what you scanned when you're done
6. **Filename generated silently**: User doesn't know filename until save prompt

#### Recommendations

**Enhanced Console Output:**

```python
# At startup
print("\n" + "="*80)
print("  📡 HDHomeRun Channel Scanner v3.0")
print("="*80 + "\n")

# After device selection
print(f"\n✅ Selected: {selected_device}")
print(f"   Device ID: {device_number}\n")

# After tuner selection
if mode == 4:
    print(f"\n✅ Selected: Auto mode (will try tuners 0-3 sequentially)\n")
else:
    print(f"\n✅ Selected: Tuner {mode}\n")

# During scan - add visual separator
print("\n" + "─"*80)
print(f"📡 Scanning tuner {tuner} on device {device_id}...")
print("─"*80)

# After scan - enhanced summary
print("\n" + "─"*80)
print("✅ Scan completed!")
print("─"*80)
print(f"   📊 Scanned: {scan_count} frequencies")
print(f"   🔒 Locked: {lock_count} channels")
print(f"   ⏱️  Duration: {elapsed_time:.1f} seconds")
print("─"*80 + "\n")

# Parsing results
print("⚙️  Parsing scan results...\n")

# Parse results summary
print(f"✅ Successfully parsed {len(parsed_data)} frequency entries")
if len(parsed_data) > 0:
    # Show sample
    print(f"\n   Sample channels found:")
    for data in parsed_data[:3]:  # Show first 3
        channel = data.get('US-Bcast Channel', '?')
        freq = data.get('Frequency', '?')
        programs = [v for k,v in data.items() if k.startswith('Program') and v]
        print(f"   • Channel {channel} ({freq} Hz): {len(programs)} program(s)")
    if len(parsed_data) > 3:
        print(f"   ... and {len(parsed_data) - 3} more\n")

# Before save prompt - show what will be saved
print(f"\n💾 Ready to save results")
print(f"   Proposed filename: {filename}")
print(f"   Location: {os.path.abspath('.')}")
print(f"   Size: ~{len(parsed_data) * 200} bytes\n")

# Final summary
print("\n" + "="*80)
print("✅ SCAN COMPLETED SUCCESSFULLY")
print("="*80)
if saved_file:
    print(f"📄 Results saved: {os.path.abspath(saved_file)}")
print(f"📊 Total channels: {len(parsed_data)}")
if openai_response:
    print(f"📍 Location: {openai_response}")
print(f"📋 Log file: hdhr_scan.log")
print("="*80 + "\n")
```

**Effort:** 1 hour
**Impact:** High - Much better UX and professionalism

---

### 4.5.2 CSV File Output Quality

**Location:** `main.py:997-1026`

#### Current CSV Format

**Header Row:**
```
Frequency,US-Bcast Channel,Lock,Signal Strength (dBmV),Signal to Noise Quality,Symbol Error Quality,TSID,Program1,Program2,...,Program20
```

**Sample Data Row:**
```
569000000,23,8vsb,10,100,100,0x1234,KABC-HD,KABC-SD,KABC-3,...,,,,,
```

#### Analysis

**✅ Strengths:**
- Standard CSV format
- Clear header names
- All important fields included
- Up to 20 programs per frequency

**❌ Weaknesses:**
1. **Sparse matrix**: Most Program columns are empty (wasted space)
2. **No metadata**: Missing scan date, device info, location
3. **No validation**: Doesn't mark questionable data
4. **Frequency format**: Raw Hz value (569000000) vs readable (569 MHz)
5. **No channel sorting**: Random order, hard to find specific channel

#### Recommendations

**Option 1: Improved Current Format**
```python
# Add metadata rows at top
output_writer.writerow(['# HDHomeRun Channel Scanner v3.0'])
output_writer.writerow(['# Scan Date:', current_datetime.strftime('%Y-%m-%d %H:%M:%S')])
output_writer.writerow(['# Device:', device_number])
output_writer.writerow(['# System:', system_name])
if openai_response:
    output_writer.writerow(['# Location:', openai_response])
output_writer.writerow([])  # Blank line

# Enhanced header
header = [
    'Frequency (Hz)',
    'Frequency (MHz)',  # Add human-readable
    'US-Bcast Channel',
    'Lock Status',
    'Signal Strength (dBmV)',
    'SNQ (%)',
    'SEQ (%)',
    'TSID',
    'Program Count',
    'Programs (comma-separated)'
]

# Write data
for data in sorted(parsed_data, key=lambda x: int(x.get('US-Bcast Channel', '0'))):
    freq_hz = data.get('Frequency', '')
    freq_mhz = f"{int(freq_hz)/1000000:.3f}" if freq_hz else ''

    # Collect all programs
    programs = [v for k,v in data.items() if k.startswith('Program') and v]
    program_str = ', '.join(programs)

    row = [
        freq_hz,
        freq_mhz,
        data.get('US-Bcast Channel', ''),
        data.get('Lock', ''),
        data.get('Signal Strength (dBmV)', ''),
        data.get('Signal to Noise Quality', ''),
        data.get('Symbol Error Quality', ''),
        data.get('TSID', ''),
        len(programs),
        program_str
    ]
    output_writer.writerow(row)
```

**Option 2: Normalized Format (Better for large datasets)**

Two CSV files:
- `scan_frequencies.csv` - One row per frequency
- `scan_programs.csv` - One row per program

**frequencies.csv:**
```
Channel,Frequency_Hz,Frequency_MHz,Lock,Signal_Strength,SNQ,SEQ,TSID,Program_Count
23,569000000,569.000,8vsb,10,100,100,0x1234,3
```

**programs.csv:**
```
Channel,Frequency_Hz,Program_Number,Program_Name
23,569000000,1,KABC-HD
23,569000000,2,KABC-SD
23,569000000,3,KABC-3
```

**Effort:**
- Option 1: 45 minutes
- Option 2: 2 hours

**Impact:** Medium - Better data usability

---

### 4.5.3 Display Mode Output (--no-save)

**Location:** `main.py:1040-1044`

**Current Implementation:**
```python
else:
    logger.info("User chose not to save to CSV, displaying data")
    print("\nDisplaying parsed data:")
    for data in parsed_data:
        print(data)
```

**Current Output:**
```
Displaying parsed data:
{'Frequency': '569000000', 'US-Bcast Channel': '23', 'Lock': '8vsb', 'Signal Strength (dBmV)': '10', 'Signal to Noise Quality': '100', 'Symbol Error Quality': '100', 'TSID': '0x1234', 'Program1': 'KABC-HD', 'Program2': 'KABC-SD', 'Program3': 'KABC-3'}
{'Frequency': '575000000', 'US-Bcast Channel': '24', 'Lock': '8vsb', 'Signal Strength (dBmV)': '8', 'Signal to Noise Quality': '95', 'Symbol Error Quality': '98', 'TSID': '0x5678', 'Program1': 'KNBC-HD', 'Program2': 'KNBC-SD'}
...
```

#### Analysis

**❌ CRITICAL ISSUE - This is CF-3 (Critical Friction)**
- **Completely unreadable**: Raw Python dict representation
- **No formatting**: Horizontal scroll required
- **Mixed data**: Important and unimportant fields mixed
- **Not user-friendly**: Only developers can parse this
- **No structure**: Can't scan for specific channel

This is broken functionality that needs immediate fix.

#### Recommendations

**Formatted Table Display:**
```python
else:
    logger.info("User chose not to save to CSV, displaying data")
    print("\n" + "="*100)
    print("📊 SCAN RESULTS")
    print("="*100)

    # Sort by channel number
    sorted_data = sorted(parsed_data, key=lambda x: int(x.get('US-Bcast Channel', '0')))

    for idx, data in enumerate(sorted_data, 1):
        channel = data.get('US-Bcast Channel', '?')
        freq_hz = data.get('Frequency', '?')
        freq_mhz = f"{int(freq_hz)/1000000:.3f} MHz" if freq_hz != '?' else '?'
        lock = data.get('Lock', '?')
        signal = data.get('Signal Strength (dBmV)', '?')
        snq = data.get('Signal to Noise Quality', '?')
        seq = data.get('Symbol Error Quality', '?')

        # Collect programs
        programs = [v for k,v in data.items() if k.startswith('Program') and v]

        # Quality indicator
        if lock == 'none':
            status = '❌ No Lock'
        elif int(signal) < 0:
            status = '⚠️  Weak'
        else:
            status = '✅ Good'

        print(f"\n[{idx}] Channel {channel} ({freq_mhz}) {status}")
        print(f"    Frequency: {freq_hz} Hz")
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

    print("\n" + "="*100)
    print(f"Total: {len(parsed_data)} frequency entries")
    locked_count = sum(1 for d in parsed_data if d.get('Lock') != 'none')
    print(f"Locked: {locked_count} channels")
    print("="*100 + "\n")
```

**Alternative: Compact Table**
```python
# Use tabulate library for clean tables
from tabulate import tabulate

# Prepare table data
table_data = []
for data in sorted_data:
    channel = data.get('US-Bcast Channel', '')
    freq = f"{int(data.get('Frequency', '0'))/1000000:.1f}"
    lock = '✅' if data.get('Lock') != 'none' else '❌'
    signal = data.get('Signal Strength (dBmV)', '')
    programs = ', '.join([v for k,v in data.items() if k.startswith('Program') and v])
    if len(programs) > 50:
        programs = programs[:47] + '...'

    table_data.append([channel, freq, lock, signal, programs])

headers = ['Ch', 'Freq (MHz)', 'Lock', 'Signal', 'Programs']
print(tabulate(table_data, headers=headers, tablefmt='grid'))
```

**Effort:** 1 hour
**Impact:** CRITICAL - Fixes completely broken display mode

---

### 4.5.4 Log File Output

**Location:** `main.py:68` (file handler setup)

**Current Behavior:**
- Log file: `hdhr_scan.log` in current directory
- Appends to existing file (never rotates)
- Contains all DEBUG/INFO/WARNING/ERROR messages

#### Analysis

**✅ Strengths:**
- Comprehensive logging
- Timestamps on all entries
- Separate file from console output
- Includes stack traces for errors

**❌ Weaknesses:**
1. **No log rotation**: File grows indefinitely
2. **Fixed location**: Always current directory (might not be writable)
3. **Not mentioned at end**: Users don't know it exists
4. **No way to disable**: Some users might want no log file
5. **Not structured**: Plain text, hard to parse programmatically

#### Recommendations

**Add Log Rotation:**
```python
from logging.handlers import RotatingFileHandler

# In setup_logging()
file_handler = RotatingFileHandler(
    'hdhr_scan.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5  # Keep 5 old logs
)
```

**Make Location Configurable:**
```python
parser.add_argument('--log-file', type=str, default='hdhr_scan.log',
                   help='Log file location (default: hdhr_scan.log)')
parser.add_argument('--no-log-file', action='store_true',
                   help='Disable file logging')

# In setup_logging()
if args.no_log_file:
    handlers = [console_handler]
else:
    handlers = [console_handler, file_handler]
```

**Mention Log at End:**
```python
# In success summary
print(f"📋 Detailed log: {os.path.abspath('hdhr_scan.log')}")
```

**Effort:** 30 minutes
**Impact:** Low - Nice to have

---

## Summary of Findings

### Critical Issues Found (Fix Immediately)

1. **CF-2: 5-Minute Scan Black Hole** (Section 4.2.2)
   - No progress during 5-minute scan
   - **Impact:** Users think program is frozen
   - **Fix:** Add real-time progress or periodic updates
   - **Effort:** 2-3 hours

2. **CF-1: Data Loss on Permission Error** (Section 4.3.5)
   - Program exits, losing 5+ minutes of scan data
   - **Impact:** Extremely frustrating, wastes user time
   - **Fix:** Offer display or alternate path options
   - **Effort:** 45 minutes

3. **CF-3: Broken Display Mode** (Section 4.5.3)
   - Prints raw Python dicts, completely unreadable
   - **Impact:** --no-save mode is unusable
   - **Fix:** Format as readable table
   - **Effort:** 1 hour

### High Priority Issues (Fix This Sprint)

4. **Device Discovery Silent Operation** (Section 4.2.1)
   - No feedback during 1-10 second discovery
   - **Fix:** Add "Searching..." message
   - **Effort:** 10 minutes

5. **Non-Standard Yes/No Prompts** (Section 4.1.3)
   - Uses 1/2 instead of y/n
   - **Fix:** Standardize on y/n format
   - **Effort:** 30 minutes

6. **Inconsistent Error Messages** (Section 4.1.4)
   - Generic, don't offer solutions
   - **Fix:** Add troubleshooting to all errors
   - **Effort:** 1-2 hours

7. **Poor Lock Failure Recovery** (Section 4.3.4)
   - No guidance when all tuners fail
   - **Fix:** Add troubleshooting checklist
   - **Effort:** 45 minutes

8. **Missing CLI Automation Flags** (Section 4.4.4)
   - Can't fully automate in scripts
   - **Fix:** Add --device-id, --tuner flags
   - **Effort:** 2-3 hours

### Medium Priority Issues

9. **Ambiguous Prompts** (Sections 4.1.1, 4.1.2)
   - Don't show valid ranges upfront
   - **Effort:** 30 minutes total

10. **No Help Escalation** (Sections 4.3.1, 4.3.2)
    - Same error message on repeated failures
    - **Effort:** 1 hour

11. **Flag Interaction Issues** (Section 4.4.3)
    - --no-save + --output causes confusion
    - **Effort:** 30 minutes

12. **Sparse CSV Format** (Section 4.5.2)
    - 20 mostly-empty Program columns
    - **Effort:** 45 minutes

13. **No Visual Hierarchy** (Section 4.5.1)
    - All text same importance
    - **Effort:** 1 hour

### Low Priority Issues

14. **Help Text Completeness** (Section 4.4.1)
15. **Log File Rotation** (Section 4.5.4)
16. **Minor Message Improvements** (Various)

---

## Quick Wins (High ROI, Low Effort)

These 6 issues can be fixed in ~2 hours total with high user impact:

1. ✅ Add "Searching for devices..." message (10 min)
2. ✅ Fix broken display mode formatting (1 hour)
3. ✅ Show file path in save success message (15 min)
4. ✅ Add examples to invalid input errors (15 min)
5. ✅ Standardize y/n prompts (30 min)
6. ✅ Add visual separators to output (20 min)

---

## Effort Summary

**Critical Fixes:** 4-5 hours
**High Priority:** 5-7 hours
**Medium Priority:** 4-5 hours
**Low Priority:** 2-3 hours

**Total Estimated Effort:** 15-20 hours

---

## Next Steps

1. Review this audit with stakeholders
2. Prioritize which fixes to implement
3. Create detailed implementation tickets
4. Begin with quick wins for immediate impact
5. Continue to Parts 5-10 of comprehensive audit

---

**End of Part 4**

Continue to [Part 5: Accessibility and Inclusivity Audit](#) (To be created)
