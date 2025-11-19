# HDHomeRun Channel Scanner - Deployment Guide

**Version:** 3.0
**Last Updated:** 2025-11-19

This comprehensive guide covers all deployment methods for the HDHomeRun Channel Scanner in production environments.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Deployment Methods](#deployment-methods)
   - [Docker Deployment](#docker-deployment)
   - [Native Installation](#native-installation)
   - [Virtual Environment](#virtual-environment)
3. [Configuration Management](#configuration-management)
4. [Production Considerations](#production-considerations)
5. [Monitoring & Logging](#monitoring--logging)
6. [Automation & Scheduling](#automation--scheduling)
7. [Troubleshooting](#troubleshooting)
8. [Security Best Practices](#security-best-practices)

---

## System Requirements

### Minimum Requirements
- **CPU:** 1 core (2 recommended)
- **RAM:** 256 MB (512 MB recommended)
- **Disk:** 100 MB free space (1 GB recommended for logs/output)
- **Network:** Same subnet as HDHomeRun device
- **OS:** Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+, CentOS 8+)
  - Also supports: macOS 10.14+, Windows 10+

### Software Dependencies
- **Python:** 3.7+ (3.11+ recommended)
- **hdhomerun_config:** Latest version from [SiliconDust](https://www.silicondust.com/support/downloads/)
- **Network Access:** UDP port 65001 for HDHomeRun discovery

### Optional Dependencies
- **OpenAI API Key:** For geographic location identification
- **Docker:** 20.10+ (if using containerized deployment)
- **Docker Compose:** 1.29+ (if using docker-compose)

---

## Deployment Methods

## Docker Deployment

Docker provides the easiest and most consistent deployment method across platforms.

### Prerequisites
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Build and Run

**1. Build the image:**
```bash
docker build -t hdhr-scanner:3.0 .
```

**2. Run interactively:**
```bash
docker run --rm -it \
  --network host \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  hdhr-scanner:3.0 \
  python3 main.py
```

**3. Run automated scan:**
```bash
docker run --rm \
  --network host \
  -v $(pwd)/output:/app/output \
  hdhr-scanner:3.0 \
  python3 main.py --device-id 12345678 --tuner 0 --quiet -o /app/output/scan.csv
```

### Using Docker Compose

**1. Create environment file:**
```bash
cat > .env <<EOF
OPENAI_API_KEY=your-key-here
TZ=America/New_York
EOF
```

**2. Start services:**
```bash
docker-compose up -d
```

**3. Run scan:**
```bash
docker-compose run --rm hdhr-scanner python3 main.py
```

**4. View logs:**
```bash
docker-compose logs -f
```

---

## Native Installation

For bare-metal or VM deployments without Docker.

### Linux (Ubuntu/Debian)

**1. Install system dependencies:**
```bash
# Update package list
sudo apt-get update

# Install Python 3
sudo apt-get install -y python3 python3-pip python3-venv

# Install hdhomerun_config
sudo apt-get install -y hdhomerun-config

# Or download from SiliconDust:
wget https://download.silicondust.com/hdhomerun/libhdhomerun_20210624.tgz
tar -xzf libhdhomerun_20210624.tgz
cd libhdhomerun && make
sudo cp hdhomerun_config /usr/local/bin/
```

**2. Clone repository:**
```bash
git clone https://github.com/yourusername/hdhr-scan-frequencies.git
cd hdhr-scan-frequencies
```

**3. Install Python dependencies:**
```bash
pip3 install -r requirements.txt
```

**4. Run scanner:**
```bash
python3 main.py
```

### Linux (RHEL/CentOS/Fedora)

**1. Install system dependencies:**
```bash
# Install Python 3
sudo dnf install -y python3 python3-pip

# Install hdhomerun_config (manual)
sudo dnf install -y gcc make
wget https://download.silicondust.com/hdhomerun/libhdhomerun_20210624.tgz
tar -xzf libhdhomerun_20210624.tgz
cd libhdhomerun && make
sudo cp hdhomerun_config /usr/local/bin/
```

**2-4. Same as Ubuntu/Debian steps above**

### macOS

**1. Install Homebrew (if not installed):**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**2. Install dependencies:**
```bash
brew install python3
brew install libhdhomerun
```

**3-4. Same as Linux steps above**

### Windows

**1. Install Python:**
- Download from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation

**2. Install hdhomerun_config:**
- Download from [SiliconDust](https://www.silicondust.com/support/downloads/)
- Extract to `C:\Program Files\HDHomeRun\`
- Add to PATH: System Properties → Environment Variables → PATH

**3. Clone and run:**
```powershell
git clone https://github.com/yourusername/hdhr-scan-frequencies.git
cd hdhr-scan-frequencies
pip install -r requirements.txt
python main.py
```

---

## Virtual Environment

Recommended for development and isolated production deployments.

### Create and Activate

**Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run scanner
python main.py

# Deactivate when done
deactivate
```

**Windows:**
```powershell
# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run scanner
python main.py

# Deactivate when done
deactivate
```

---

## Configuration Management

### Environment Variables

Set these in your environment or `.env` file:

```bash
# OpenAI API Key (optional)
export OPENAI_API_KEY="sk-..."

# Timezone (for Docker deployments)
export TZ="America/New_York"

# Custom config file location (optional)
export HDHR_CONFIG_FILE="$HOME/.hdhr_scanner_config.json"
```

### Configuration File

Located at: `~/.hdhr_scanner_config.json`

**Initialize configuration:**
```bash
python3 main.py --edit-config
```

**Example configuration:**
```json
{
    "device_id": "12345678",
    "tuner": 0,
    "output_directory": "/var/hdhr/scans",
    "auto_openai": false,
    "quiet": false,
    "debug": false,
    "save_csv": true,
    "last_device_id": "12345678",
    "last_tuner": 0
}
```

### View/Edit Configuration

```bash
# View current config
python3 main.py --show-config

# Edit interactively
python3 main.py --edit-config

# Reset to defaults
python3 main.py --reset-config
```

---

## Production Considerations

### File Permissions

Ensure the application has write access:

```bash
# Create output directories
sudo mkdir -p /var/hdhr/{scans,logs}

# Set ownership (if running as hdhr user)
sudo chown -R hdhr:hdhr /var/hdhr

# Set permissions
sudo chmod 755 /var/hdhr
sudo chmod 775 /var/hdhr/{scans,logs}
```

### Log Rotation

The application uses built-in log rotation:
- Log file: `hdhr_scan.log`
- Max size: 5 MB per file
- Backup count: 5 files
- Total storage: ~25 MB

**External log rotation (optional):**

Create `/etc/logrotate.d/hdhr-scanner`:
```
/var/hdhr/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 hdhr hdhr
}
```

### Resource Limits

**systemd service limits:**
```ini
[Service]
MemoryLimit=512M
CPUQuota=100%
TasksMax=10
```

**Docker resource limits:**
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
```

---

## Monitoring & Logging

### Application Logs

**Location:** `hdhr_scan.log` (or `/var/hdhr/logs/hdhr_scan.log`)

**Log Levels:**
- `ERROR`: Critical failures
- `WARNING`: Non-fatal issues
- `INFO`: Normal operations (default)
- `DEBUG`: Detailed debugging (use `--debug` flag)

**View logs:**
```bash
# Tail logs
tail -f hdhr_scan.log

# Search for errors
grep ERROR hdhr_scan.log

# View with timestamps
tail -f hdhr_scan.log | grep "$(date +%Y-%m-%d)"
```

### Health Checks

**Docker health check:**
```bash
docker inspect hdhr-scanner --format='{{.State.Health.Status}}'
```

**Manual health check:**
```bash
# Verify hdhomerun_config is accessible
hdhomerun_config discover

# Test Python environment
python3 -c "import openai; print('OK')"

# Check file permissions
touch /var/hdhr/scans/test.csv && rm /var/hdhr/scans/test.csv
```

### Monitoring Script

Create `monitor_hdhr.sh`:
```bash
#!/bin/bash
# HDHomeRun Scanner Health Monitor

LOG_FILE="/var/hdhr/logs/hdhr_scan.log"
MAX_AGE_MINUTES=60

# Check if log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "ERROR: Log file not found"
    exit 1
fi

# Check log file age
LOG_AGE=$(( $(date +%s) - $(stat -c %Y "$LOG_FILE") ))
if [ $LOG_AGE -gt $(($MAX_AGE_MINUTES * 60)) ]; then
    echo "WARNING: Log file hasn't been updated in ${LOG_AGE}s"
fi

# Check for recent errors
ERROR_COUNT=$(grep -c ERROR "$LOG_FILE" | tail -100)
if [ $ERROR_COUNT -gt 5 ]; then
    echo "WARNING: ${ERROR_COUNT} errors in recent logs"
fi

echo "OK: Health check passed"
```

---

## Automation & Scheduling

### Cron Jobs

**Daily scan at 3 AM:**
```bash
crontab -e

# Add this line:
0 3 * * * cd /opt/hdhr-scan-frequencies && /usr/bin/python3 main.py --device-id 12345678 --tuner 0 --quiet -o /var/hdhr/scans/scan_$(date +\%Y\%m\%d).csv >> /var/hdhr/logs/cron.log 2>&1
```

**Weekly scan with notification:**
```bash
0 2 * * 0 cd /opt/hdhr-scan-frequencies && /usr/bin/python3 main.py --device-id 12345678 --tuner 0 --quiet -o /var/hdhr/scans/weekly_$(date +\%Y\%m\%d).csv && echo "Scan complete" | mail -s "HDHomeRun Scan" admin@example.com
```

### systemd Timer

**1. Create service file** `/etc/systemd/system/hdhr-scanner.service`:
```ini
[Unit]
Description=HDHomeRun Channel Scanner
After=network.target

[Service]
Type=oneshot
User=hdhr
Group=hdhr
WorkingDirectory=/opt/hdhr-scan-frequencies
Environment="PATH=/usr/local/bin:/usr/bin"
ExecStart=/usr/bin/python3 main.py --device-id 12345678 --tuner 0 --quiet -o /var/hdhr/scans/scan_%%Y%%m%%d.csv
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**2. Create timer file** `/etc/systemd/system/hdhr-scanner.timer`:
```ini
[Unit]
Description=HDHomeRun Scanner Daily Timer
Requires=hdhr-scanner.service

[Timer]
OnCalendar=daily
OnCalendar=03:00
Persistent=true

[Install]
WantedBy=timers.target
```

**3. Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable hdhr-scanner.timer
sudo systemctl start hdhr-scanner.timer

# Check status
sudo systemctl status hdhr-scanner.timer
sudo systemctl list-timers hdhr-scanner.timer
```

### Docker Automation

**Using Docker Compose with cron:**
```bash
# Add to crontab
0 3 * * * cd /opt/hdhr-scan-frequencies && docker-compose run --rm hdhr-scanner python3 main.py --device-id 12345678 --tuner 0 --quiet -o /app/output/scan_$(date +\%Y\%m\%d).csv
```

---

## Troubleshooting

### Common Issues

**1. "hdhomerun_config utility not found"**
```bash
# Verify installation
which hdhomerun_config

# Test discovery
hdhomerun_config discover

# If not found, reinstall
sudo apt-get install --reinstall hdhomerun-config
```

**2. "No HDHomeRun devices found"**
```bash
# Check network connectivity
ping <hdhr-ip-address>

# Verify device is on network
hdhomerun_config discover

# Check firewall
sudo ufw allow 65001/udp
```

**3. "Permission denied" when saving CSV**
```bash
# Check directory permissions
ls -la /var/hdhr/scans

# Fix ownership
sudo chown -R hdhr:hdhr /var/hdhr

# Or use alternate location
python3 main.py -o ~/scans/output.csv
```

**4. Docker network issues**
```bash
# Ensure host network mode
docker run --network host ...

# Check Docker network
docker network ls
docker network inspect host
```

**5. OpenAI API errors**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API key
python3 -c "import openai; openai.api_key='$OPENAI_API_KEY'; print('OK')"

# Skip OpenAI if not needed
python3 main.py  # Just press 'N' when prompted
```

### Debug Mode

Enable verbose logging:
```bash
# With --debug flag
python3 main.py --debug

# With --verbose flag (implies --debug)
python3 main.py --verbose

# Check log file
tail -f hdhr_scan.log
```

### Network Debugging

**Verify HDHomeRun connectivity:**
```bash
# Discover devices
hdhomerun_config discover

# Get device info
hdhomerun_config <device-id> get /sys/hwmodel

# Check tuner status
hdhomerun_config <device-id> get /tuner0/status

# Test scan
hdhomerun_config <device-id> scan /tuner0
```

**Check network accessibility:**
```bash
# Test UDP broadcast (requires nmap)
sudo nmap -sU -p 65001 <subnet>/24

# Check routing
ip route | grep default

# Verify firewall
sudo iptables -L -n | grep 65001
```

---

## Security Best Practices

### Principle of Least Privilege

**1. Run as non-root user:**
```bash
# Create dedicated user
sudo useradd -r -s /bin/bash -m hdhr

# Set ownership
sudo chown -R hdhr:hdhr /opt/hdhr-scan-frequencies
```

**2. Restrict file permissions:**
```bash
# Application files (read-only)
chmod 755 /opt/hdhr-scan-frequencies
chmod 644 /opt/hdhr-scan-frequencies/*.py

# Output directories (write)
chmod 755 /var/hdhr/scans
chmod 755 /var/hdhr/logs
```

**3. Secure configuration file:**
```bash
# Config file (contains potential API keys)
chmod 600 ~/.hdhr_scanner_config.json
```

### Network Security

**1. Firewall rules:**
```bash
# Allow HDHomeRun discovery (UDP 65001)
sudo ufw allow from <hdhr-subnet>/24 to any port 65001 proto udp

# Deny all other inbound
sudo ufw default deny incoming
sudo ufw enable
```

**2. Network segmentation:**
- Place HDHomeRun devices on isolated VLAN
- Use firewall rules to restrict access
- Monitor network traffic for anomalies

### API Key Management

**1. Environment variables (preferred):**
```bash
# Set in shell profile
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc

# Or use .env file with Docker Compose
echo 'OPENAI_API_KEY=sk-...' > .env
chmod 600 .env
```

**2. Never commit API keys:**
```bash
# Add to .gitignore
echo '.env' >> .gitignore
echo '*.key' >> .gitignore
```

**3. Rotate keys regularly:**
- Set expiration on OpenAI API keys
- Rotate every 90 days minimum
- Revoke compromised keys immediately

### Container Security

**1. Use non-root user in Docker:**
```dockerfile
USER hdhr  # Already implemented in Dockerfile
```

**2. Read-only filesystem (optional):**
```bash
docker run --read-only \
  -v /app/output:/app/output \
  -v /app/logs:/app/logs \
  hdhr-scanner:3.0
```

**3. Security scanning:**
```bash
# Scan image for vulnerabilities
docker scan hdhr-scanner:3.0

# Use Trivy
trivy image hdhr-scanner:3.0
```

### Audit Logging

**Enable detailed logging for security audits:**
```bash
# Run with debug mode
python3 main.py --debug

# Monitor access logs
tail -f hdhr_scan.log | grep -E "(ERROR|WARNING|CRITICAL)"
```

---

## Support and Resources

### Documentation
- **README.md**: User guide and feature documentation
- **ERROR_REFERENCE.md**: Comprehensive error reference
- **DEPLOYMENT.md**: This file (deployment guide)

### External Resources
- [SiliconDust Support](https://www.silicondust.com/support/)
- [HDHomeRun Downloads](https://www.silicondust.com/support/downloads/)
- [Python Docker Images](https://hub.docker.com/_/python)

### Reporting Issues

When reporting issues, include:
1. Operating system and version
2. Python version (`python3 --version`)
3. hdhomerun_config version
4. Full error message from `hdhr_scan.log`
5. Command used to run the scanner
6. Network configuration (device subnet, firewall rules)

---

## Quick Reference

### Essential Commands

```bash
# Interactive scan
python3 main.py

# Automated scan
python3 main.py --device-id 12345678 --tuner 0 --quiet -o scan.csv

# Show version
python3 main.py --version

# Show help
python3 main.py --help

# View configuration
python3 main.py --show-config

# Edit configuration
python3 main.py --edit-config

# Technical glossary
python3 main.py --glossary

# Debug mode
python3 main.py --debug

# Docker interactive
docker-compose run --rm hdhr-scanner python3 main.py

# Docker automated
docker-compose run --rm hdhr-scanner python3 main.py --device-id 12345678 --tuner 0 --quiet -o /app/output/scan.csv
```

---

**End of Deployment Guide**
