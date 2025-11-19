#!/bin/bash
# HDHomeRun Channel Scanner - Installation Script
# Version 3.0
# Supports: Ubuntu, Debian, CentOS, RHEL, Fedora, macOS

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/hdhr-scan-frequencies"
OUTPUT_DIR="/var/hdhr/scans"
LOG_DIR="/var/hdhr/logs"
SERVICE_USER="hdhr"

# Print with color
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
print_banner() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║         HDHomeRun Channel Scanner v3.0                     ║"
    echo "║         Installation Script                                ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
            OS_VERSION=$VERSION_ID
        else
            print_error "Cannot detect Linux distribution"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        OS_VERSION=$(sw_vers -productVersion)
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi

    print_info "Detected OS: $OS $OS_VERSION"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Install system dependencies
install_dependencies() {
    print_info "Installing system dependencies..."

    case $OS in
        ubuntu|debian)
            apt-get update
            apt-get install -y python3 python3-pip python3-venv curl wget git
            print_success "System dependencies installed"
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                dnf install -y python3 python3-pip curl wget git
            else
                yum install -y python3 python3-pip curl wget git
            fi
            print_success "System dependencies installed"
            ;;
        macos)
            if ! command -v brew &> /dev/null; then
                print_error "Homebrew not found. Please install from https://brew.sh"
                exit 1
            fi
            brew install python3
            print_success "System dependencies installed"
            ;;
        *)
            print_error "Unsupported OS: $OS"
            exit 1
            ;;
    esac
}

# Install hdhomerun_config utility
install_hdhomerun_config() {
    print_info "Installing hdhomerun_config utility..."

    case $OS in
        ubuntu|debian)
            if apt-cache search hdhomerun-config | grep -q hdhomerun-config; then
                apt-get install -y hdhomerun-config
                print_success "hdhomerun_config installed via package manager"
                return
            fi
            ;;
    esac

    # Manual installation for other systems
    print_info "Installing hdhomerun_config from source..."

    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"

    wget -q https://download.silicondust.com/hdhomerun/libhdhomerun_20210624.tgz
    tar -xzf libhdhomerun_20210624.tgz
    cd libhdhomerun

    make
    cp hdhomerun_config /usr/local/bin/
    chmod +x /usr/local/bin/hdhomerun_config

    cd /
    rm -rf "$TEMP_DIR"

    print_success "hdhomerun_config installed from source"
}

# Verify hdhomerun_config installation
verify_hdhomerun_config() {
    print_info "Verifying hdhomerun_config installation..."

    if command -v hdhomerun_config &> /dev/null; then
        print_success "hdhomerun_config found at: $(which hdhomerun_config)"

        # Test discovery
        print_info "Testing device discovery..."
        if hdhomerun_config discover &> /dev/null; then
            print_success "Device discovery test passed"
        else
            print_warning "Device discovery test failed (this is OK if no devices are connected)"
        fi
    else
        print_error "hdhomerun_config not found in PATH"
        exit 1
    fi
}

# Create service user
create_user() {
    print_info "Creating service user: $SERVICE_USER..."

    if id "$SERVICE_USER" &>/dev/null; then
        print_warning "User $SERVICE_USER already exists"
    else
        case $OS in
            macos)
                # macOS user creation is complex, skip it
                print_warning "Skipping user creation on macOS (run as current user)"
                SERVICE_USER=$(whoami)
                ;;
            *)
                useradd -r -s /bin/bash -m "$SERVICE_USER"
                print_success "User $SERVICE_USER created"
                ;;
        esac
    fi
}

# Create directories
create_directories() {
    print_info "Creating application directories..."

    # Installation directory
    mkdir -p "$INSTALL_DIR"
    print_success "Created: $INSTALL_DIR"

    # Output and log directories
    mkdir -p "$OUTPUT_DIR" "$LOG_DIR"
    print_success "Created: $OUTPUT_DIR"
    print_success "Created: $LOG_DIR"

    # Set ownership
    if [ "$OS" != "macos" ]; then
        chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR" "$OUTPUT_DIR" "$LOG_DIR"
    fi
}

# Install application
install_application() {
    print_info "Installing HDHomeRun Channel Scanner..."

    # Copy files
    cp main.py "$INSTALL_DIR/"
    cp README.md "$INSTALL_DIR/"
    cp ERROR_REFERENCE.md "$INSTALL_DIR/" 2>/dev/null || true
    cp requirements.txt "$INSTALL_DIR/"

    # Install Python dependencies
    print_info "Installing Python dependencies..."
    pip3 install -r "$INSTALL_DIR/requirements.txt" --quiet

    print_success "Application installed to $INSTALL_DIR"
}

# Create systemd service (Linux only)
create_systemd_service() {
    if [ "$OS" = "macos" ]; then
        print_info "Skipping systemd service creation on macOS"
        return
    fi

    print_info "Creating systemd service..."

    cat > /etc/systemd/system/hdhr-scanner.service <<EOF
[Unit]
Description=HDHomeRun Channel Scanner
After=network.target

[Service]
Type=oneshot
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=/usr/local/bin:/usr/bin"
ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py --help

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    print_success "systemd service created"
    print_info "Enable with: systemctl enable hdhr-scanner.service"
}

# Create command-line wrapper
create_wrapper() {
    print_info "Creating command-line wrapper..."

    cat > /usr/local/bin/hdhr-scan <<'EOF'
#!/bin/bash
# HDHomeRun Scanner wrapper script
INSTALL_DIR="/opt/hdhr-scan-frequencies"
exec python3 "$INSTALL_DIR/main.py" "$@"
EOF

    chmod +x /usr/local/bin/hdhr-scan
    print_success "Command-line wrapper created: hdhr-scan"
}

# Configure firewall
configure_firewall() {
    print_info "Configuring firewall..."

    if command -v ufw &> /dev/null; then
        ufw allow 65001/udp comment "HDHomeRun discovery" 2>/dev/null || true
        print_success "UFW firewall rule added"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=65001/udp 2>/dev/null || true
        firewall-cmd --reload 2>/dev/null || true
        print_success "firewalld rule added"
    else
        print_warning "No firewall detected, skipping firewall configuration"
    fi
}

# Print post-installation instructions
print_instructions() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║         Installation Complete!                             ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    print_success "HDHomeRun Channel Scanner v3.0 installed successfully"
    echo ""
    echo "📁 Installation directory: $INSTALL_DIR"
    echo "📁 Output directory: $OUTPUT_DIR"
    echo "📁 Log directory: $LOG_DIR"
    echo ""
    echo "🔧 Quick Start:"
    echo "   Run scanner:              hdhr-scan"
    echo "   View help:                hdhr-scan --help"
    echo "   Show version:             hdhr-scan --version"
    echo "   Edit configuration:       hdhr-scan --edit-config"
    echo ""
    echo "📖 Documentation:"
    echo "   User guide:               $INSTALL_DIR/README.md"
    echo "   Error reference:          $INSTALL_DIR/ERROR_REFERENCE.md"
    echo "   Deployment guide:         $INSTALL_DIR/DEPLOYMENT.md"
    echo ""
    echo "🔐 Optional Setup:"
    echo "   Configure OpenAI:         export OPENAI_API_KEY='your-key'"
    echo "   Create config:            hdhr-scan --edit-config"
    echo ""
    if [ "$OS" != "macos" ]; then
        echo "⚙️  Systemd Service:"
        echo "   Enable service:           sudo systemctl enable hdhr-scanner.service"
        echo "   Start service:            sudo systemctl start hdhr-scanner.service"
        echo ""
    fi
    echo "📚 For automation examples, see $INSTALL_DIR/README.md"
    echo ""
}

# Main installation process
main() {
    print_banner

    detect_os
    check_root

    print_info "Starting installation..."
    echo ""

    install_dependencies
    install_hdhomerun_config
    verify_hdhomerun_config
    create_user
    create_directories
    install_application
    create_systemd_service
    create_wrapper
    configure_firewall

    print_instructions
}

# Run main installation
main

exit 0
