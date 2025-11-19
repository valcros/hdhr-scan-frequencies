#!/bin/bash
# HDHomeRun Scanner - Health Check Script
# Used for monitoring, Docker health checks, and K8s readiness probes

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
MAX_LOG_AGE_MINUTES=60
LOG_FILE="${LOG_FILE:-hdhr_scan.log}"
CRITICAL_ERRORS_THRESHOLD=10

# Exit codes
EXIT_OK=0
EXIT_WARNING=1
EXIT_CRITICAL=2

print_status() {
    local status=$1
    local message=$2
    case $status in
        "OK")
            echo -e "${GREEN}✓ OK${NC} - $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠ WARNING${NC} - $message"
            ;;
        "CRITICAL")
            echo -e "${RED}✗ CRITICAL${NC} - $message"
            ;;
    esac
}

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_status "OK" "Python 3 installed: $PYTHON_VERSION"
        return 0
    else
        print_status "CRITICAL" "Python 3 not found"
        return 1
    fi
}

check_hdhomerun_config() {
    if command -v hdhomerun_config &> /dev/null; then
        print_status "OK" "hdhomerun_config utility found"
        return 0
    else
        print_status "CRITICAL" "hdhomerun_config utility not found"
        return 1
    fi
}

check_main_py() {
    if [ -f "main.py" ]; then
        print_status "OK" "main.py exists"
        return 0
    else
        print_status "CRITICAL" "main.py not found"
        return 1
    fi
}

check_dependencies() {
    python3 -c "import sys, subprocess, csv, re, time, shutil, argparse, logging, datetime, pathlib, platform, typing" &> /dev/null
    if [ $? -eq 0 ]; then
        print_status "OK" "Core Python dependencies available"
        return 0
    else
        print_status "CRITICAL" "Missing core Python dependencies"
        return 1
    fi
}

check_openai() {
    python3 -c "import openai" &> /dev/null
    if [ $? -eq 0 ]; then
        print_status "OK" "OpenAI package installed (optional)"
        return 0
    else
        print_status "WARNING" "OpenAI package not installed (optional feature)"
        return 0  # Not critical
    fi
}

check_device_discovery() {
    if ! command -v hdhomerun_config &> /dev/null; then
        print_status "WARNING" "Cannot test device discovery (hdhomerun_config not found)"
        return 0
    fi

    # Test discovery (timeout after 5 seconds)
    timeout 5s hdhomerun_config discover &> /dev/null
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        print_status "OK" "HDHomeRun device discovery works"
        return 0
    elif [ $exit_code -eq 124 ]; then
        print_status "WARNING" "Device discovery timeout (no devices found, but that's OK)"
        return 0
    else
        print_status "WARNING" "Device discovery returned error (may be normal if no devices)"
        return 0
    fi
}

check_log_file() {
    if [ ! -f "$LOG_FILE" ]; then
        print_status "WARNING" "Log file not found (may not have run yet): $LOG_FILE"
        return 0
    fi

    # Check log age
    if [[ "$OSTYPE" == "darwin"* ]]; then
        LOG_AGE_SECONDS=$(( $(date +%s) - $(stat -f %m "$LOG_FILE") ))
    else
        LOG_AGE_SECONDS=$(( $(date +%s) - $(stat -c %Y "$LOG_FILE") ))
    fi

    LOG_AGE_MINUTES=$(( LOG_AGE_SECONDS / 60 ))

    if [ $LOG_AGE_MINUTES -gt $MAX_LOG_AGE_MINUTES ]; then
        print_status "WARNING" "Log file is $LOG_AGE_MINUTES minutes old (last activity > $MAX_LOG_AGE_MINUTES minutes ago)"
    else
        print_status "OK" "Log file is recent ($LOG_AGE_MINUTES minutes old)"
    fi

    # Check for critical errors
    if command -v grep &> /dev/null; then
        CRITICAL_COUNT=$(grep -c "CRITICAL" "$LOG_FILE" 2>/dev/null || echo 0)
        ERROR_COUNT=$(grep -c "ERROR" "$LOG_FILE" 2>/dev/null || echo 0)

        if [ "$CRITICAL_COUNT" -gt 0 ]; then
            print_status "WARNING" "Found $CRITICAL_COUNT CRITICAL errors in log"
        fi

        if [ "$ERROR_COUNT" -gt "$CRITICAL_ERRORS_THRESHOLD" ]; then
            print_status "WARNING" "Found $ERROR_COUNT errors in log (threshold: $CRITICAL_ERRORS_THRESHOLD)"
        else
            print_status "OK" "Error count within threshold: $ERROR_COUNT"
        fi
    fi

    return 0
}

check_disk_space() {
    DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')

    if [ "$DISK_USAGE" -gt 90 ]; then
        print_status "CRITICAL" "Disk usage critical: ${DISK_USAGE}%"
        return 1
    elif [ "$DISK_USAGE" -gt 80 ]; then
        print_status "WARNING" "Disk usage high: ${DISK_USAGE}%"
        return 0
    else
        print_status "OK" "Disk usage normal: ${DISK_USAGE}%"
        return 0
    fi
}

check_memory() {
    if command -v free &> /dev/null; then
        MEM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')

        if [ "$MEM_USAGE" -gt 90 ]; then
            print_status "WARNING" "Memory usage high: ${MEM_USAGE}%"
        else
            print_status "OK" "Memory usage normal: ${MEM_USAGE}%"
        fi
    else
        print_status "WARNING" "Cannot check memory (free command not available)"
    fi
    return 0
}

check_version() {
    if [ -f "main.py" ]; then
        VERSION=$(python3 main.py --version 2>&1 | head -1)
        print_status "OK" "Application version: $VERSION"
    fi
    return 0
}

# Main health check
main() {
    echo ""
    echo "======================================================================"
    echo "  HDHomeRun Scanner - Health Check"
    echo "  $(date)"
    echo "======================================================================"
    echo ""

    FAILED_CHECKS=0
    WARNING_CHECKS=0

    # Run all checks
    check_python || ((FAILED_CHECKS++))
    check_hdhomerun_config || ((FAILED_CHECKS++))
    check_main_py || ((FAILED_CHECKS++))
    check_dependencies || ((FAILED_CHECKS++))
    check_openai || ((WARNING_CHECKS++))
    check_device_discovery || ((WARNING_CHECKS++))
    check_log_file || ((WARNING_CHECKS++))
    check_disk_space || ((FAILED_CHECKS++))
    check_memory || ((WARNING_CHECKS++))
    check_version

    echo ""
    echo "======================================================================"

    if [ $FAILED_CHECKS -eq 0 ] && [ $WARNING_CHECKS -eq 0 ]; then
        echo -e "${GREEN}✓ HEALTH CHECK PASSED${NC} - All systems operational"
        echo "======================================================================"
        exit $EXIT_OK
    elif [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "${YELLOW}⚠ HEALTH CHECK PASSED WITH WARNINGS${NC} - $WARNING_CHECKS warning(s)"
        echo "======================================================================"
        exit $EXIT_WARNING
    else
        echo -e "${RED}✗ HEALTH CHECK FAILED${NC} - $FAILED_CHECKS critical failure(s), $WARNING_CHECKS warning(s)"
        echo "======================================================================"
        exit $EXIT_CRITICAL
    fi
}

# Run main function
main "$@"
