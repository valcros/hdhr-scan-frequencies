# Changelog

All notable changes to the HDHomeRun Channel Scanner project will be documented in this file.

## [3.0.0] - 2025-11-19

### 🐛 Critical Bug Fixes

#### Parse Lock Regex Fix (HIGH PRIORITY)
- **Fixed**: Critical bug in `parse_lock()` function that failed to capture negative signal strength values
- **Location**: main.py:395
- **Impact**: Previously, signal strength values like `ss=-20` were not parsed, causing data loss
- **Solution**: Updated regex pattern from `(\d+)` to `(-?\d+)` to handle negative values
- **Test Coverage**: Added comprehensive tests including edge cases for very negative values

#### Input Validation Crashes (HIGH PRIORITY)
- **Fixed**: Application crashes on non-numeric user input in multiple locations
- **Locations**:
  - Device selection (line 217)
  - Tuner mode selection (line 287)
  - CSV save prompt (line 830)
  - OpenAI query prompt (line 830)
- **Impact**: Any non-numeric input would crash the application with `ValueError`
- **Solution**: Added try-except blocks with proper validation and retry logic
- **Enhancement**: Users now get helpful error messages and can retry invalid inputs

#### Fragile Lock Detection (MEDIUM PRIORITY)
- **Fixed**: Fragile string matching for "LOCK: none" in query_tuner()
- **Location**: main.py:608
- **Impact**: Could incorrectly identify lock failures
- **Solution**: Replaced simple string search with robust check for successful locks
- **New Logic**: Actively searches for successful lock indicators rather than failure strings

### 🔒 Security Enhancements

#### Deprecated os.popen() Replacement
- **Replaced**: All uses of deprecated `os.popen()` with secure `subprocess.run()`
- **Locations**:
  - `discover_devices()`: main.py:144
  - `query_tuner()`: main.py:591
- **Benefits**:
  - Eliminates potential command injection vulnerabilities
  - Better error handling and timeout support
  - Future-proof compatibility
  - Proper signal handling

### ✨ Major New Features

#### Structured Logging System
- **Added**: Professional logging infrastructure using Python's logging module
- **Features**:
  - Log file output to `hdhr_scan.log`
  - Configurable log levels (DEBUG, INFO, WARNING, ERROR)
  - Timestamp and module information on all log entries
  - Console and file handlers
  - Debug mode via `--debug` flag
- **Location**: main.py:52-76, throughout codebase

#### Command-Line Interface
- **Added**: Full argparse integration with comprehensive options
- **Options**:
  - `--debug`: Enable debug logging
  - `--test-file`: Use local test file for development
  - `--no-save`: Skip CSV file creation
  - `--auto-openai`: Automatically query OpenAI
  - `--output FILE`: Custom output filename
  - `--help`: Display help message
- **Location**: main.py:864-886
- **Examples**: See README.md Usage section

#### Progress Indicators
- **Added**: Real-time progress feedback during scanning
- **Features**:
  - Frequency scan count
  - Successful lock count
  - Per-tuner status updates
  - Clear success/failure messaging
- **Location**: main.py:617-621

#### Pre-flight Checks
- **Added**: Validation before operations begin
- **Checks**:
  - hdhomerun_config utility existence
  - File write permissions
  - Directory access
- **Functions**:
  - `check_hdhomerun_config()`: main.py:79-96
  - `check_file_writable()`: main.py:786-811
- **Impact**: Fail fast with clear error messages

#### Data Validation
- **Added**: Signal quality range validation
- **Function**: `validate_signal_quality()`: main.py:99-114
- **Validation**:
  - SNQ (Signal-to-Noise Quality): 0-100 range
  - SEQ (Symbol Error Quality): 0-100 range
  - Warning logs for out-of-range values
- **Location**: Integrated into `parse_lock()`

### 🔄 API Updates

#### OpenAI Integration Modernization
- **Upgraded**: From deprecated Completion API to ChatCompletion API
- **Location**: main.py:708-783
- **Changes**:
  - Replaced `openai.Completion.create()` with `openai.ChatCompletion.create()`
  - Updated to use message-based format with system and user roles
  - Added model parameter: `gpt-3.5-turbo`
  - Improved context with system message
- **Error Handling**: Specific exception handling for:
  - `AuthenticationError`: Invalid API key
  - `RateLimitError`: Quota exceeded
  - `APIConnectionError`: Network issues
  - `Timeout`: Request timeout
  - `InvalidRequestError`: Malformed requests

### 🏗️ Architecture Improvements

#### Custom Exception Classes
- **Added**: Domain-specific exception hierarchy
- **Classes**:
  - `HDHRConfigNotFoundError`: Utility not found
  - `DeviceDiscoveryError`: Device discovery failed
  - `TunerLockError`: Tuner lock failure
  - `InvalidInputError`: Invalid user input
- **Location**: main.py:31-49
- **Benefit**: Better error categorization and handling

#### Enhanced Error Handling
- **Replaced**: Generic `except Exception` with specific exception types
- **Updated Functions**:
  - `discover_devices()`: Specific exceptions for timeout, file not found, etc.
  - `query_tuner()`: Timeout, file not found, value errors
  - `get_openai_response()`: All OpenAI-specific errors
  - `main()`: Comprehensive exception handling with proper exit codes
- **Features**:
  - Detailed error logging with stack traces
  - User-friendly error messages
  - Proper exit codes (0=success, 1=error, 130=interrupted)

#### Input Validation Helper
- **Added**: `get_yes_no_input()` function for validated yes/no prompts
- **Location**: main.py:814-845
- **Features**:
  - Accepts multiple formats: 1/2, y/n, yes/no
  - Default value support
  - Keyboard interrupt handling
  - Clear error messages

### 🧪 Testing

#### Comprehensive Test Suite
- **Added**: test_main.py with 27 unit tests
- **Coverage**:
  - Parse lock with positive/negative/zero signal strength
  - Frequency and channel parsing
  - TSID parsing
  - Program extraction
  - Signal quality validation
  - File permission checks
  - Edge cases and malformed data
- **All Tests**: ✅ PASSING
- **Run**: `python3 test_main.py`

#### Test Classes
1. `TestParseLock`: 5 tests - lock data parsing
2. `TestParseFrequency`: 2 tests - frequency parsing
3. `TestParseTsid`: 3 tests - TSID parsing
4. `TestParseProgram`: 3 tests - program parsing
5. `TestExtractPrograms`: 2 tests - program extraction
6. `TestParseResultsInfo`: 1 test - comprehensive parsing
7. `TestValidateSignalQuality`: 2 tests - validation logic
8. `TestCheckFileWritable`: 2 tests - permission checks
9. `TestPrepareOpenAIPrompt`: 1 test - prompt generation
10. `TestGetUSBcast`: 2 tests - channel extraction
11. `TestUpdateLockInfo`: 1 test - dictionary updates
12. `TestEdgeCases`: 3 tests - edge cases

### 📚 Documentation

#### README.md Complete Rewrite
- **Enhanced**: Comprehensive documentation with professional formatting
- **New Sections**:
  - Version highlights and what's new
  - Detailed installation instructions
  - Command-line options table
  - Multiple usage examples
  - Logging documentation
  - Testing documentation
  - Troubleshooting guide with common issues
  - Architecture overview
  - Error code reference
  - Version history
  - Contributing guidelines

#### Code Documentation
- **Improved**: All function docstrings enhanced
- **Added**: Type hints throughout codebase
- **Updated**: Examples in docstrings to reflect current behavior
- **Added**: This CHANGELOG.md

### 🔧 Code Quality

#### Type Hints
- **Added**: Python type annotations to all function signatures
- **Types Used**: List, Dict, Optional, Tuple, str, int, bool
- **Benefit**: Better IDE support and type checking

#### Better Separation of Concerns
- **Refactored**: Main function decomposed into smaller, focused functions
- **New Functions**:
  - `setup_logging()`: Logging configuration
  - `check_hdhomerun_config()`: Utility validation
  - `validate_signal_quality()`: Data validation
  - `check_file_writable()`: Permission checks
  - `get_yes_no_input()`: Input validation helper
- **Benefit**: Improved testability and maintainability

#### Removed Dead Code
- **Removed**: Commented-out check for hdhomerun_config (now properly implemented)
- **Removed**: Commented-out debug prints
- **Cleaned**: Removed TODO comments (issues resolved)

### 📊 Statistics

- **Lines of Code**: ~1,100 (from ~680)
- **Functions**: 18 (from 13)
- **Test Cases**: 27 (new)
- **Custom Exceptions**: 4 (new)
- **Command-Line Options**: 5 (new)
- **Exit Codes**: 3 (standardized)

### 🎯 Fixes Summary by Severity

#### Critical (3 issues fixed)
1. ✅ Negative signal strength regex bug
2. ✅ Input validation crashes in device selection
3. ✅ Input validation crashes in tuner selection

#### High (9 issues fixed)
4. ✅ Input validation in CSV prompt
5. ✅ Input validation in OpenAI prompt
6. ✅ Deprecated os.popen() in discover_devices()
7. ✅ Deprecated os.popen() in query_tuner()
8. ✅ Fragile lock detection logic
9. ✅ Generic exception handling in discover_devices()
10. ✅ Generic exception handling in query_tuner()
11. ✅ Generic exception handling in get_openai_response()
12. ✅ Generic exception handling in main()

#### Medium (9 improvements)
13. ✅ Structured logging system
14. ✅ Progress indicators
15. ✅ OpenAI API upgrade
16. ✅ Command-line argument parsing
17. ✅ Signal quality validation
18. ✅ Pre-execution checks
19. ✅ File permission checks
20. ✅ Test suite creation
21. ✅ Documentation updates

### 🚀 Migration Guide

#### For Users
- **Command Line**: The script now supports flags. Use `--help` to see options.
- **Logging**: A log file `hdhr_scan.log` is now created automatically.
- **Interruption**: Ctrl+C is now handled gracefully.
- **No Breaking Changes**: Interactive mode works exactly as before.

#### For Developers
- **OpenAI**: If using the OpenAI integration, install: `pip install openai`
- **Testing**: Run tests before committing: `python3 test_main.py`
- **Imports**: New imports added: subprocess, argparse, logging, shutil, sys
- **Exceptions**: Catch specific custom exceptions instead of generic Exception

### 🔮 Future Enhancements (Not in this release)
- Configuration file support (.ini or .yaml)
- Support for multiple output formats (JSON, XML)
- Web interface for remote scanning
- Email notifications on scan completion
- Database storage option
- Scan scheduling/automation
- Support for ATSC 3.0

---

## [2.4.0] - 2023-09-25

### Added
- OpenAI integration for geographic identification
- Documentation improvements
- Refactored code for better modularity

## [2.2.0] - 2023-09-25

### Added
- Initial OpenAI integration
- Improved code organization

## [2.1.0] - Earlier

### Added
- Sample test file support
- Variable renaming for clarity

### Fixed
- Comment corrections
- Bug fixes

---

**Legend:**
- ✅ Completed
- 🐛 Bug Fix
- ✨ New Feature
- 🔒 Security
- 🔄 Update
- 🏗️ Architecture
- 🧪 Testing
- 📚 Documentation
- 🔧 Code Quality
- 📊 Statistics
- 🎯 Summary
- 🚀 Migration
- 🔮 Future
