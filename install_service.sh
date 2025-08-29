#!/bin/bash
# Evil Assistant - Service Installation Script
# Run this script ON your Raspberry Pi to install the systemd service

set -e

echo "🍓 Installing Evil Assistant Systemd Service"
echo "==========================================="

# Check if we're in the right directory
if [ ! -f "evil-assistant.service" ] || [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Run this script from the evilassistant project directory"
    exit 1
fi

# Check if running as pi user
if [ "$USER" != "pi" ]; then
    echo "⚠️  Warning: This script should be run as the 'pi' user"
    echo "   Current user: $USER"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📋 Pre-installation checks..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run setup_pi.sh first."
    exit 1
fi

# Check if Evil Assistant is installed
if ! .venv/bin/python -c "import evilassistant" 2>/dev/null; then
    echo "❌ Evil Assistant not installed in virtual environment"
    echo "   Run: source .venv/bin/activate && pip install -e ."
    exit 1
fi

echo "✅ Pre-checks passed"

echo "🔧 Installing systemd service..."

# Copy service file to systemd directory
sudo cp evil-assistant.service /etc/systemd/system/

# Set proper permissions
sudo chmod 644 /etc/systemd/system/evil-assistant.service

# Reload systemd
sudo systemctl daemon-reload

echo "✅ Service file installed"

echo "🚀 Enabling auto-start on boot..."

# Enable the service
sudo systemctl enable evil-assistant.service

echo "✅ Auto-start enabled"

echo "📊 Service status:"
sudo systemctl status evil-assistant.service --no-pager || true

echo ""
echo "🎉 Installation Complete!"
echo "======================="
echo ""
echo "🔧 Service Management Commands:"
echo "  Start:    sudo systemctl start evil-assistant"
echo "  Stop:     sudo systemctl stop evil-assistant"
echo "  Restart:  sudo systemctl restart evil-assistant"
echo "  Status:   sudo systemctl status evil-assistant"
echo "  Logs:     sudo journalctl -u evil-assistant -f"
echo ""
echo "🚀 To start the service now:"
echo "  sudo systemctl start evil-assistant"
echo ""
echo "📋 To check if it's working:"
echo "  sudo systemctl status evil-assistant"
echo "  sudo journalctl -u evil-assistant -f"
echo ""
echo "👹 Your Evil Assistant will now start automatically on boot!"
