# DevOps Quick Start Guide

**HDHomeRun Channel Scanner v3.0**

This guide provides streamlined instructions for DevOps teams to deploy, test, and monitor the HDHomeRun Channel Scanner in production environments.

---

## 🚀 Quick Deploy (30 seconds)

```bash
# Clone and deploy
git clone https://github.com/yourusername/hdhr-scan-frequencies.git
cd hdhr-scan-frequencies

# Option 1: Docker (Fastest)
make docker-build
make docker-run

# Option 2: Native (Production)
sudo make install

# Option 3: Kubernetes (Scale)
make k8s-deploy
```

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [File Structure](#file-structure)
3. [Quick Deploy Methods](#quick-deploy-methods)
4. [Configuration](#configuration)
5. [Testing & Validation](#testing--validation)
6. [Monitoring & Health Checks](#monitoring--health-checks)
7. [Automation](#automation)
8. [Troubleshooting](#troubleshooting)
9. [Security Checklist](#security-checklist)

---

## Prerequisites

### Required
- **Python:** 3.7+ (3.11+ recommended)
- **hdhomerun_config:** From [SiliconDust](https://www.silicondust.com/support/downloads/)
- **Network:** UDP port 65001 for device discovery
- **Permissions:** Root/sudo for system-wide installation

### Optional
- **Docker:** 20.10+ (for containerized deployment)
- **Docker Compose:** 1.29+ (for orchestration)
- **Kubernetes:** 1.20+ (for cluster deployment)
- **OpenAI API Key:** For AI-powered location identification

### Quick Verification
```bash
python3 --version          # Should be 3.7+
hdhomerun_config discover  # Should find devices (if connected)
docker --version           # Optional, for Docker deployment
kubectl version            # Optional, for K8s deployment
```

---

## File Structure

```
hdhr-scan-frequencies/
├── main.py                      # Main application
├── test_main.py                 # Unit tests
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── Makefile                     # DevOps automation commands
├── .env.example                 # Environment variables template
├── Dockerfile                   # Container definition
├── docker-compose.yml           # Docker orchestration
├── .dockerignore               # Docker build exclusions
├── install.sh                   # Automated installation script
├── .pre-commit-config.yaml     # Pre-commit hooks
├── .gitignore                   # Git exclusions
├── README.md                    # User documentation
├── ERROR_REFERENCE.md           # Error troubleshooting
├── DEPLOYMENT.md                # Comprehensive deployment guide
├── DEVOPS_QUICKSTART.md         # This file
├── scripts/
│   └── health-check.sh         # Health check script
├── k8s/
│   ├── configmap.yaml          # Configuration
│   ├── secret.yaml.example     # Secrets template
│   ├── pvc.yaml                # Persistent volumes
│   └── cronjob.yaml            # Scheduled scans
└── .github/
    └── workflows/
        └── ci.yml               # CI/CD pipeline
```

---

## Quick Deploy Methods

### Method 1: Docker (Recommended for Testing)

**Build:**
```bash
make docker-build
# Or manually:
docker build -t hdhr-scanner:3.0 .
```

**Run Interactively:**
```bash
make docker-run
# Or manually:
docker run --rm -it --network host \
  -v $(pwd)/output:/app/output \
  hdhr-scanner:3.0 python3 main.py
```

**Run Automated Scan:**
```bash
docker run --rm --network host \
  -v $(pwd)/output:/app/output \
  hdhr-scanner:3.0 python3 main.py \
  --device-id 12345678 --tuner 0 --quiet -o /app/output/scan.csv
```

**Verify:**
```bash
make docker-test
# Checks: version, help, dependencies
```

### Method 2: Docker Compose (Recommended for Development)

**Setup:**
```bash
# 1. Create environment file
cp .env.example .env
nano .env  # Edit with your values

# 2. Start services
make docker-compose-up
# Or: docker-compose up -d

# 3. Run scan
docker-compose run --rm hdhr-scanner python3 main.py

# 4. Stop services
make docker-compose-down
```

### Method 3: Native Installation (Recommended for Production)

**Automated:**
```bash
sudo bash install.sh
# Installs: Python, hdhomerun_config, creates user, sets up systemd

# Use the scanner:
hdhr-scan --help
```

**Manual:**
```bash
# Install dependencies
sudo apt-get install python3 python3-pip hdhomerun-config

# Install Python packages
pip3 install -r requirements.txt

# Run scanner
python3 main.py
```

### Method 4: Kubernetes (Recommended for Scale)

**Setup:**
```bash
# 1. Create namespace (optional)
kubectl create namespace hdhr-scanner

# 2. Create configuration
kubectl apply -f k8s/configmap.yaml

# 3. Create secrets (copy and edit first)
cp k8s/secret.yaml.example k8s/secret.yaml
nano k8s/secret.yaml
kubectl apply -f k8s/secret.yaml

# 4. Create storage
kubectl apply -f k8s/pvc.yaml

# 5. Deploy CronJobs
kubectl apply -f k8s/cronjob.yaml

# Or use Makefile:
make k8s-deploy
```

**Verify:**
```bash
make k8s-status
# Or manually:
kubectl get pods -l app=hdhr-scanner
kubectl get cronjobs
```

---

## Configuration

### Environment Variables

**Create configuration:**
```bash
cp .env.example .env
```

**Key variables:**
```bash
# Optional: OpenAI API key
OPENAI_API_KEY=sk-your-key-here

# Optional: Default device ID
HDHR_DEVICE_ID=12345678

# Optional: Default tuner
HDHR_TUNER=0

# Optional: Output directory
OUTPUT_DIR=/var/hdhr/scans
```

### Application Configuration

**Interactive editor:**
```bash
python3 main.py --edit-config
# Or with Makefile:
make config-edit
```

**View current config:**
```bash
make config-show
```

**Reset to defaults:**
```bash
make config-reset
```

**Configuration file:** `~/.hdhr_scanner_config.json`

---

## Testing & Validation

### Unit Tests

```bash
# Run tests
make test

# With coverage
make test-coverage

# View coverage report
open htmlcov/index.html
```

### Integration Tests

```bash
# Test Docker image
make docker-test

# Health check
make health-check
# Or: bash scripts/health-check.sh
```

### CI/CD Tests (Local)

```bash
# Run full CI suite
make ci-test

# Full CI build (includes Docker)
make ci-build
```

### Manual Testing

```bash
# Test with sample data
python3 main.py --test-file

# Test device discovery
hdhomerun_config discover

# Test version
python3 main.py --version

# Test help
python3 main.py --help
```

---

## Monitoring & Health Checks

### Health Check Script

**Run manually:**
```bash
make health-check
```

**Health check verifies:**
- Python 3 installation
- hdhomerun_config utility
- Core dependencies
- OpenAI package (optional)
- Device discovery
- Log file status
- Disk space
- Memory usage

**Exit codes:**
- `0`: All checks passed
- `1`: Warnings present (non-critical)
- `2`: Critical failures

### Application Logs

**Location:** `hdhr_scan.log`

**View logs:**
```bash
# Tail logs
make logs-tail

# Show errors only
make logs-errors

# Today's activity
make logs-today
```

**Log levels:**
- `DEBUG`: Detailed diagnostic info (`--debug` flag)
- `INFO`: Normal operations (default)
- `WARNING`: Non-critical issues
- `ERROR`: Critical errors

**Log rotation:**
- Automatic rotation at 5 MB
- Keeps 5 backup files
- Total storage: ~25 MB

### Metrics & Monitoring

**Docker health check:**
```bash
docker inspect hdhr-scanner --format='{{.State.Health.Status}}'
```

**Kubernetes probes:**
```yaml
livenessProbe:
  exec:
    command:
    - bash
    - /app/scripts/health-check.sh
  initialDelaySeconds: 30
  periodSeconds: 60
```

### Alerting

**Monitor for:**
- Failed scans (exit code != 0)
- Log errors (grep ERROR hdhr_scan.log)
- Disk space (> 80%)
- Memory usage (> 90%)

---

## Automation

### Cron Jobs (Native)

**Add to crontab:**
```bash
crontab -e

# Daily scan at 3 AM
0 3 * * * cd /opt/hdhr-scan-frequencies && python3 main.py --device-id 12345678 --tuner 0 --quiet -o /var/hdhr/scans/scan_$(date +\%Y\%m\%d).csv

# Weekly scan on Sundays at 2 AM
0 2 * * 0 cd /opt/hdhr-scan-frequencies && python3 main.py --device-id 12345678 --tuner 0 --quiet -o /var/hdhr/scans/weekly_$(date +\%Y\%m\%d).csv
```

### systemd Timer (Linux)

**Enable and start:**
```bash
sudo systemctl enable hdhr-scanner.timer
sudo systemctl start hdhr-scanner.timer

# Check status
sudo systemctl status hdhr-scanner.timer

# View next run time
sudo systemctl list-timers hdhr-scanner.timer
```

### Kubernetes CronJobs

**Deployed automatically with k8s manifests:**
- Daily scan: 3:00 AM UTC
- Weekly scan: 2:00 AM UTC (Sundays)

**Trigger manually:**
```bash
kubectl create job --from=cronjob/hdhr-scanner-daily manual-scan-$(date +%s)
```

### Docker Automation

**With cron:**
```bash
# Add to crontab
0 3 * * * docker-compose -f /path/to/docker-compose.yml run --rm hdhr-scanner python3 main.py --device-id 12345678 --tuner 0 --quiet -o /app/output/scan_$(date +\%Y\%m\%d).csv
```

---

## Troubleshooting

### Common Issues

**1. "hdhomerun_config utility not found"**
```bash
# Verify installation
which hdhomerun_config

# Install (Ubuntu/Debian)
sudo apt-get install hdhomerun-config

# Or download from SiliconDust
wget https://download.silicondust.com/hdhomerun/libhdhomerun_20210624.tgz
tar -xzf libhdhomerun_20210624.tgz
cd libhdhomerun && make
sudo cp hdhomerun_config /usr/local/bin/
```

**2. "No HDHomeRun devices found"**
```bash
# Test discovery directly
hdhomerun_config discover

# Check network
ping <hdhr-ip-address>

# Verify firewall
sudo ufw allow 65001/udp
# Or: sudo firewall-cmd --add-port=65001/udp --permanent
```

**3. Docker network issues**
```bash
# Ensure host networking
docker run --network host ...

# Check Docker network
docker network ls
docker network inspect host
```

**4. Permission denied (file writes)**
```bash
# Check directory permissions
ls -la /var/hdhr/scans

# Fix ownership
sudo chown -R $USER:$USER /var/hdhr

# Or use alternative directory
python3 main.py -o ~/scans/output.csv
```

**5. Kubernetes pod failures**
```bash
# Check pod status
kubectl get pods -l app=hdhr-scanner

# View logs
kubectl logs -l app=hdhr-scanner

# Describe pod for events
kubectl describe pod <pod-name>

# Check secrets
kubectl get secrets hdhr-scanner-secrets
```

### Debug Mode

**Enable verbose logging:**
```bash
# Native
python3 main.py --debug

# Docker
docker run ... --debug

# Kubernetes (edit cronjob)
kubectl edit cronjob hdhr-scanner-daily
# Add --debug flag to command
```

### Health Check

**Run comprehensive health check:**
```bash
make health-check
# Exit codes: 0=OK, 1=Warning, 2=Critical
```

---

## Security Checklist

### ✅ Pre-Deployment

- [ ] Review `.env.example` and create `.env` with secure values
- [ ] **Never commit `.env`, `secret.yaml`, or files with API keys**
- [ ] Set file permissions: `chmod 600 .env ~/.hdhr_scanner_config.json`
- [ ] Use non-root user for execution (Docker/systemd configured)
- [ ] Enable firewall rules: `sudo ufw allow 65001/udp`
- [ ] Rotate OpenAI API keys regularly (90 days)
- [ ] Run security scans: `make security-scan`
- [ ] Review Dockerfile for vulnerabilities: `docker scan hdhr-scanner:3.0`

### ✅ Post-Deployment

- [ ] Verify non-root execution: `ps aux | grep main.py`
- [ ] Check file permissions: `ls -la ~/.hdhr_scanner_config.json`
- [ ] Monitor logs for security events: `grep -i security hdhr_scan.log`
- [ ] Enable log rotation (automatic, verify: `ls -lh hdhr_scan.log*`)
- [ ] Set up alerts for failed scans
- [ ] Regular dependency updates: `pip list --outdated`
- [ ] Keep hdhomerun_config updated

### ✅ Kubernetes Specific

- [ ] Use NetworkPolicies to restrict traffic
- [ ] Enable Pod Security Standards
- [ ] Use separate namespace: `kubectl create namespace hdhr-scanner`
- [ ] Set resource limits (configured in cronjob.yaml)
- [ ] Use read-only file system where possible
- [ ] Scan container images: `trivy image hdhr-scanner:3.0`

---

## Quick Reference

### Essential Commands

```bash
# Makefile commands (run 'make help' for full list)
make install              # Install dependencies
make test                 # Run tests
make docker-build         # Build Docker image
make docker-run           # Run Docker container
make k8s-deploy           # Deploy to Kubernetes
make health-check         # Run health check
make logs-tail            # Tail logs
make clean                # Clean generated files

# Direct Python commands
python3 main.py                    # Interactive scan
python3 main.py --help             # Show help
python3 main.py --version          # Show version
python3 main.py --show-config      # View configuration
python3 main.py --debug            # Debug mode

# Docker commands
docker-compose up -d               # Start services
docker-compose run --rm hdhr-scanner python3 main.py
docker-compose down                # Stop services

# Kubernetes commands
kubectl apply -f k8s/              # Deploy all
kubectl get pods -l app=hdhr-scanner
kubectl logs -f <pod-name>
kubectl delete -f k8s/             # Remove all
```

### File Locations

```
Configuration:    ~/.hdhr_scanner_config.json
Logs:             hdhr_scan.log (or /var/hdhr/logs/)
Output:           ./ (or /var/hdhr/scans/)
Install dir:      /opt/hdhr-scan-frequencies
systemd service:  /etc/systemd/system/hdhr-scanner.service
```

### Support Resources

- **Documentation:** README.md, DEPLOYMENT.md, ERROR_REFERENCE.md
- **Issues:** GitHub Issues with debug logs
- **SiliconDust:** https://www.silicondust.com/support/

---

## CI/CD Integration

### GitHub Actions

**Pipeline runs on:**
- Push to main/develop branches
- Pull requests
- Releases

**Pipeline includes:**
- Linting (flake8, black, mypy)
- Testing (Python 3.7-3.11, Ubuntu & macOS)
- Security scanning (safety, bandit, Trivy)
- Docker build and test
- Release artifacts (on tags)

**Workflow file:** `.github/workflows/ci.yml`

### Local CI Testing

```bash
# Run full CI suite
make ci-test

# Run full CI build
make ci-build
```

---

## Next Steps

1. **Deploy to staging:**
   ```bash
   ENVIRONMENT=staging make deploy-local
   ```

2. **Run smoke tests:**
   ```bash
   make test
   make health-check
   ```

3. **Deploy to production:**
   ```bash
   ENVIRONMENT=production make deploy-prod
   ```

4. **Set up monitoring:**
   - Configure log aggregation
   - Set up alerting for failures
   - Monitor resource usage

5. **Schedule scans:**
   - Configure cron/systemd timers
   - Or use Kubernetes CronJobs

---

**Need more details?** See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide.

**Questions or issues?** Open a GitHub issue with debug logs attached.
