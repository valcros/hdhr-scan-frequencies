# Part 2: User Journey Maps
## HDHomeRun Channel Scanner v3.0 - UX Audit

**Date**: 2025-11-19
**Status**: Complete journey analysis across all user paths

---

## Journey 1: Happy Path - Perfect Execution

### Overview
User successfully scans channels, saves to CSV, and identifies geographic region using OpenAI.

**Total Steps**: 9
**Estimated Duration**: 2-8 minutes (depending on scan time)
**Success Rate Target**: 95%

---

### Step 1: Application Launch
**User Action**: `python3 main.py`

**User Sees**:
```
2025-11-19 10:30:15 - __main__ - INFO - ============================================================
2025-11-19 10:30:15 - __main__ - INFO - HDHomeRun Channel Scanner v3.0 Starting
2025-11-19 10:30:15 - __main__ - INFO - ============================================================
```

**System State**:
- Logging initialized
- hdhomerun_config utility checked
- Ready to discover devices

**Duration**: < 1 second
**Friction Points**: None
**User Feeling**: Informed, ready to proceed

---

### Step 2: Device Discovery
**System Action**: Automatically searches for HDHomeRun devices

**User Sees**:
```
Select an HDHomeRun device:
1) hdhomerun device 12345678 found at 192.168.1.100
2) Rediscover devices
```

**User Input Required**: Select device number

**What User Thinks**:
- ✅ "Found my device"
- ✅ "Clear what to do next"
- ❓ "What if I have multiple devices?"

**Duration**: 2-5 seconds for discovery
**Friction Points**:
- No indication discovery is happening (appears instant or frozen)
- No explanation of what device number means

---

### Step 3: Device Selection
**User Action**: Types `1` and presses Enter

**User Sees**:
```
Enter the device number: 1

Select a tuner or Auto mode:
0) Tuner 0
1) Tuner 1
2) Tuner 2
3) Tuner 3
4) Auto mode (Try all tuners)
```

**User Input Required**: Select tuner (0-4)

**What User Thinks**:
- ✅ "Got multiple tuner options"
- ❓ "What's the difference between tuners?"
- ❓ "Which should I choose?"
- ✅ "Auto mode sounds safe"

**Duration**: User decision time (~5-10 seconds)
**Friction Points**:
- No explanation of tuner differences
- No recommendation for first-time users
- No indication which tuners are in use

---

### Step 4: Tuner Selection
**User Action**: Types `4` (Auto mode)

**User Sees**:
```
Enter the mode number: 4

Scanning tuner 0 on device 12345678...
```

**System State**: Begins 5-minute channel scan

**What User Thinks**:
- ✅ "System is working"
- ⏳ "How long will this take?"
- ❓ "Is it progressing or stuck?"

**Duration**: 2-5 minutes for scan
**Friction Points**:
- **CRITICAL**: No progress bar or percentage
- No time estimate
- No indication of how many frequencies scanned
- User may think it's frozen

---

### Step 5: Scan Completion
**User Sees**:
```
Scan completed for tuner 0.
Scanned 69 frequencies, successfully locked on 15 channels.

Parsing scan results...
Successfully parsed 69 frequency entries.
```

**System State**: Data ready, moving to save decision

**What User Thinks**:
- ✅ "Scan worked!"
- ✅ "Found 15 channels"
- ✅ "System is processing results"

**Duration**: 1-2 seconds
**Friction Points**: None - good feedback here!

---

### Step 6: CSV Save Decision
**User Sees**:
```
Save results to a CSV file? (1=yes / 2=no):
```

**User Action**: Types `1` or `yes`

**What User Thinks**:
- ✅ "Default should be yes"
- ❓ "Where will the file be saved?"
- ❓ "What will it be named?"

**User Sees Next**:
```
Writing data to 'hostname_20251119_10.csv'...
Data successfully written to 'hostname_20251119_10.csv'.
```

**What User Thinks**:
- ✅ "File saved successfully"
- ✅ "I can see the filename"
- ❓ "Where is this file located?"

**Duration**: < 1 second
**Friction Points**:
- No indication of file location (current directory assumed)
- Filename format might be surprising
- No preview of what "hostname" will be

---

### Step 7: OpenAI Query Decision
**User Sees**:
```
Send results to OpenAI to determine the city/region? (1=yes / 2=no):
```

**User Action**: Types `1` or `yes`

**What User Thinks**:
- ✅ "This sounds cool"
- ❓ "Do I need an API key?"
- ❓ "Will this cost money?"
- ❓ "How does it work?"

**User Sees Next**:
```
Querying OpenAI to identify geographic region...

The broadcast region is: Los Angeles, California
```

**What User Thinks**:
- ✅ "Wow, that's accurate!"
- ✅ "Nice feature"

**Duration**: 2-5 seconds (API call)
**Friction Points**:
- No indication API key is needed before prompt
- No cost warning
- No progress during API call

---

### Step 8: Completion
**User Sees**:
```
Scan completed successfully!
```

**System State**: Program exits with code 0

**What User Thinks**:
- ✅ "All done!"
- ✅ "Clear success message"
- ❓ "What do I do with the CSV now?"

**Duration**: Immediate
**Friction Points**:
- No next steps suggested
- No indication of where to find output files
- No summary of what was accomplished

---

## Journey 2: Alternative Path - CLI Power User

### Overview
Expert user uses command-line flags to automate entire workflow.

**Command**:
```bash
python3 main.py --debug --output my_scan.csv --auto-openai
```

**Journey Changes**:
1. **No device prompt** - Automated discovery still happens
2. **No tuner prompt** - Must still select (⚠️ inconsistency!)
3. **No save prompt** - Auto-saves to my_scan.csv
4. **No OpenAI prompt** - Automatically queries
5. **Debug output** - Verbose logging to console

**Friction Points Discovered**:
- ❌ **INCONSISTENCY**: Flags skip some prompts but not all
- ❌ Cannot fully automate (still requires device & tuner selection)
- ❌ No `--auto-select` or `--device-id` flags
- ❌ No `--tuner` flag to specify tuner programmatically

**User Expectation vs Reality**:
- Expected: Fully automated scan
- Reality: Still requires 2 interactive prompts
- **Gap**: Partial automation disappoints power users

---

## Journey 3: Alternative Path - Test Mode

### Overview
Developer testing with local file instead of real device.

**Command**: `python3 main.py --test-file`

**Journey Changes**:
1. **Skips**: hdhomerun_config check
2. **Skips**: Device discovery
3. **Skips**: Device selection
4. **Skips**: Tuner selection
5. **Loads**: ScanData.txt instead

**User Sees**:
```
Loading data from local test file: ScanData.txt
Parsing scan results...
Successfully parsed 69 frequency entries.
```

**Then**: Same save and OpenAI prompts as normal flow

**Friction Points**:
- ✅ **GOOD**: Clean bypass of hardware dependencies
- ✅ **GOOD**: Clear messaging about test mode
- ❌ File location hardcoded (always ./ScanData.txt)
- ❌ No option to specify test file path

---

## Journey 4: Alternative Path - Display Only (No Save)

### Overview
User wants to see results without saving file.

**Command**: `python3 main.py --no-save`

**Journey Executes**: Normal discovery, selection, scanning

**At Save Decision**: Automatically skipped

**User Sees**:
```
Displaying parsed data:
{'Frequency': '605000000', 'US-Bcast Channel': '36', 'Lock': '8vsb', 'Signal Strength (dBmV)': '100', 'Signal to Noise Quality': '100', 'Symbol Error Quality': '100', 'TSID': '0x0123', 'Program3': '4.1 NBC4-LA', 'Program4': '4.2 COZI-TV'}
{'Frequency': '599000000', 'US-Bcast Channel': '35', 'Lock': '8vsb', ...}
...
```

**Friction Points**:
- ❌ **CRITICAL UX ISSUE**: Raw dictionary output is unreadable
- ❌ No formatting or table structure
- ❌ Scrolls off screen quickly
- ❌ No way to navigate or search
- ❌ No summary at end

**User Feeling**: Frustrated - this is not usable

**Recommendation**: Need formatted table output for screen display

---

## Journey 5: Error Recovery - No Devices Found

### Trigger: HDHomeRun device not on network

**User Experience**:

```
Select an HDHomeRun device:
[wait 3 seconds...]

No HDHomeRun devices found. Retrying in 3 seconds...
[automatic 3-second wait]

No HDHomeRun devices found after retry.
Would you like to discover devices again? (y/n):
```

**User Action 1**: Types `y`
**Result**: Rediscovers (loops back)

**User Action 2**: Types `n`
**Result**: Program exits

**Friction Analysis**:

| Aspect | Rating | Notes |
|--------|--------|-------|
| Clear error message | ✅ Good | "No devices found" is clear |
| Automatic retry | ✅ Good | Saves user from manual retry |
| Wait time indication | ✅ Good | "Retrying in 3 seconds" |
| Recovery options | ✅ Good | Manual retry offered |
| Troubleshooting help | ❌ **Missing** | No guidance on WHY or HOW TO FIX |
| Exit path | ✅ Good | Clean exit option |

**Improvement Opportunity**:
```
No HDHomeRun devices found after retry.

Troubleshooting tips:
1. Ensure your HDHomeRun device is powered on
2. Check that device is on the same network
3. Check firewall settings
4. For detailed logs, run with --debug flag

Would you like to discover devices again? (y/n):
```

---

## Journey 6: Error Recovery - Invalid Input (Device Selection)

### Trigger: User types non-numeric input

**Scenario 1**: User types "first" instead of "1"

```
Select an HDHomeRun device:
1) hdhomerun device 12345678 found at 192.168.1.100
2) Rediscover devices

Enter the device number: first
Invalid input. Please enter a number.

Enter the device number:
```

**Friction Points**:
- ✅ **GOOD**: Immediate feedback
- ✅ **GOOD**: Infinite retries
- ❌ Message doesn't restate valid range
- ❌ Doesn't show menu again (user has to scroll up)

**Improvement**:
```
Invalid input. Please enter a number between 1 and 2.

Enter the device number:
```

**Scenario 2**: User types "99" (out of range)

```
Enter the device number: 99
Invalid choice. Please enter a number between 1 and 2.

Enter the device number:
```

**Friction Points**:
- ✅ **GOOD**: Shows valid range
- ✅ **GOOD**: Different message for different errors (good!)
- ✅ **GOOD**: Allows retry

---

## Journey 7: Error Recovery - All Tuners Locked

### Trigger: All tuners in use by another application

**User Experience**:

```
Select a tuner or Auto mode:
0) Tuner 0
1) Tuner 1
2) Tuner 2
3) Tuner 3
4) Auto mode (Try all tuners)

Enter the mode number: 4

Scanning tuner 0 on device 12345678...
Tuner 0 is locked by another resource. Skipping to next tuner.

Scanning tuner 1 on device 12345678...
Tuner 1 is locked by another resource. Skipping to next tuner.

Scanning tuner 2 on device 12345678...
Tuner 2 is locked by another resource. Skipping to next tuner.

Scanning tuner 3 on device 12345678...
Tuner 3 is locked by another resource. Skipping to next tuner.

All tuners are either locked or failed to lock.
Error: Could not obtain scan results from tuner.
```

**Program exits with code 1**

**Friction Analysis**:

| Aspect | Rating | Notes |
|--------|--------|-------|
| Clear error | ✅ Good | Explains each tuner is locked |
| Progressive feedback | ✅ Good | Shows trying each tuner |
| Root cause identified | ✅ Good | "resource locked" is clear |
| Recovery option | ❌ **MISSING** | No option to retry later |
| Troubleshooting help | ❌ **MISSING** | Doesn't say HOW to fix |
| Exit gracefully | ⚠️ Partial | Exits, but no guidance |

**Improvement Opportunity**:
```
All tuners are locked by another resource.

This usually means another application is using your HDHomeRun:
• Plex, Kodi, or other media software
• Another scan in progress
• Live TV viewing application

Close other HDHomeRun applications and try again.

Would you like to retry? (y/n):
```

---

## Journey 8: Error Recovery - File Permission Denied

### Trigger: User doesn't have write permission in current directory

**User Experience**:

```
Save results to a CSV file? (1=yes / 2=no): 1
Error: Cannot write to file 'hostname_20251119_10.csv'. Check permissions.
```

**Program exits with code 1**

**Friction Analysis**:

| Aspect | Rating | Notes |
|--------|--------|-------|
| Error detected | ✅ Good | Pre-flight check works |
| Error message | ⚠️ Partial | Says WHAT but not HOW TO FIX |
| Recovery option | ❌ **MISSING** | Can't specify alternate path |
| Data lost | ❌ **CRITICAL** | Scan data lost on exit |
| Alternative offered | ❌ **MISSING** | Could offer display mode |

**Current Behavior**: All scan work lost!

**Improvement Opportunity**:
```
Error: Cannot write to file 'hostname_20251119_10.csv'.
Reason: No write permission in current directory (/readonly/path)

Options:
1) Display results on screen instead
2) Specify a different output path
3) Exit and fix permissions

Choose an option (1-3):
```

---

## Journey 9: Error Recovery - OpenAI API Key Missing

### Trigger: User selects OpenAI query but no API key set

**User Experience**:

```
Send results to OpenAI to determine the city/region? (1=yes / 2=no): 1

Querying OpenAI to identify geographic region...
OpenAI API key not found. Please set OPENAI_API_KEY environment variable.
Could not get a response from OpenAI.

Scan completed successfully!
```

**Friction Analysis**:

| Aspect | Rating | Notes |
|--------|--------|-------|
| Early detection | ❌ **MISSING** | Should check BEFORE prompting |
| Error message | ✅ Good | Explains how to fix |
| Program continues | ✅ Good | Doesn't crash |
| User informed upfront | ❌ **MISSING** | Shouldn't ask if key missing |

**Improvement**: Check for API key before prompting:

```python
# Before prompting
if results and os.environ.get("OPENAI_API_KEY"):
    if get_yes_no_input("Send results to OpenAI..."):
        # Query API
else:
    # Don't even ask
```

---

## Journey 10: Error Recovery - Scan Timeout

### Trigger: Tuner scan takes > 5 minutes

**User Experience**:

```
Scanning tuner 0 on device 12345678...
[5 minutes pass with no feedback...]

Error: Tuner 0 scan timed out. Trying next tuner.

Scanning tuner 1 on device 12345678...
```

**Friction Analysis**:

| Aspect | Rating | Notes |
|--------|--------|-------|
| Timeout is reasonable | ✅ Good | 5 min is appropriate |
| User knows timeout occurred | ✅ Good | Clear message |
| Automatic recovery | ✅ Good | Tries next tuner |
| Progress during scan | ❌ **CRITICAL** | 5 min with NO feedback is terrible |
| User knows it's working | ❌ **CRITICAL** | Appears frozen |

**Critical UX Issue**: 5-minute black hole

**Improvement**: Add streaming progress:
```
Scanning tuner 0 on device 12345678...
Scanning frequency 1/69: 695000000 (us-bcast:51) - no lock
Scanning frequency 2/69: 689000000 (us-bcast:50) - no lock
Scanning frequency 15/69: 605000000 (us-bcast:36) - LOCKED ✓
...
Scan completed for tuner 0 (4m 32s)
```

---

## Journey 11: Interruption Path - Ctrl+C at Device Selection

### Trigger: User presses Ctrl+C during device selection

**User Experience**:

```
Select an HDHomeRun device:
1) hdhomerun device 12345678 found at 192.168.1.100
2) Rediscover devices

Enter the device number: ^C
Operation cancelled by user.
```

**Program exits cleanly**

**Friction Analysis**:

| Aspect | Rating | Notes |
|--------|--------|-------|
| Interrupt handled | ✅ Good | Doesn't crash |
| Clear message | ✅ Good | User knows why |
| Exit code | ✅ Good | Returns 130 (Ctrl+C) |
| Cleanup | ✅ Good | No temp files left |

**No issues identified** - this works well!

---

## Journey 12: Interruption Path - Ctrl+C During Scan

### Trigger: User presses Ctrl+C during 5-minute scan

**Expected Behavior**: Graceful exit

**Actual Behavior**:
- Ctrl+C caught by main() handler
- Scan subprocess may continue briefly
- Program exits with code 130

**Friction Analysis**:

| Aspect | Rating | Notes |
|--------|--------|-------|
| Interrupt handled | ✅ Good | Doesn't crash |
| Subprocess cleanup | ⚠️ Unknown | subprocess.run() should handle |
| Partial data | ❌ **LOST** | Any scanned data is discarded |
| User informed | ✅ Good | "Program interrupted by user. Exiting." |

**Improvement Opportunity**: Offer to save partial results:
```
Program interrupted by user.

Partial scan data available (23 frequencies scanned).
Save partial results? (y/n):
```

---

## Journey Comparison Matrix

| Journey | Steps | Duration | Prompts | Friction Level | Success Rate |
|---------|-------|----------|---------|----------------|--------------|
| Happy Path | 9 | 2-8 min | 4 | Low | 95% |
| CLI Power User | 7 | 2-8 min | 2 | Medium (expectations) | 85% |
| Test Mode | 5 | < 10 sec | 2 | Low | 99% |
| No-Save Display | 8 | 2-8 min | 3 | **HIGH** (output) | 40% |
| No Devices | 3 | 10-20 sec | 2 | Medium | 70% |
| Invalid Input | Varies | +5-15 sec | +1-3 | Low | 90% |
| All Tuners Locked | 6 | 30-60 sec | 2 | High | 20% |
| Permission Denied | 8 | 2-8 min | 3 | **CRITICAL** | 0% (data lost) |
| Missing API Key | 9 | 2-8 min | 4 | Medium | 80% |
| Scan Timeout | 6-8 | 5+ min | 2 | **CRITICAL** (wait time) | 60% |
| Ctrl+C (any point) | Varies | Immediate | 0 | Low | 100% |

---

## Critical Findings

### 🔴 Critical UX Issues

1. **Permission Denied = Data Loss**
   - Journey 8: All scan work lost when can't write file
   - Impact: HIGH - wastes 5+ minutes of user time
   - Fix Priority: P0

2. **5-Minute Black Hole**
   - Journey 4, 10: No progress during scan
   - Impact: HIGH - users think app is frozen
   - Fix Priority: P0

3. **Display Mode Unusable**
   - Journey 4: Raw dictionary output
   - Impact: HIGH - feature is broken
   - Fix Priority: P0

### 🟡 High-Priority Issues

4. **Incomplete Automation**
   - Journey 2: CLI flags don't skip all prompts
   - Impact: Medium - disappoints power users
   - Fix Priority: P1

5. **No Troubleshooting Help**
   - Journeys 5, 7: Errors don't explain solutions
   - Impact: Medium - users stuck without guidance
   - Fix Priority: P1

6. **API Key Check Timing**
   - Journey 9: Prompts for OpenAI without checking key first
   - Impact: Low - minor annoyance
   - Fix Priority: P2

### ✅ What Works Well

1. **Ctrl+C Handling**: Clean interruption at all points
2. **Input Validation**: Clear, specific error messages
3. **Auto-retry**: Device discovery retries automatically
4. **Multi-tuner Fallback**: Automatically tries next tuner
5. **Progress Messages**: Good feedback at key transitions

---

**Next**: Part 3 - Friction Point Analysis
