#!/bin/bash
"""
Quick install script for missing dependencies on Raspberry Pi
Run this on the Pi to install sox and fix audio issues
"""

echo "🔧 Installing missing dependencies for Evil Assistant..."

# Install sox with all format support
echo "📦 Installing sox with format support..."
sudo apt update
sudo apt install -y sox libsox-fmt-all

# Install optional audio libraries for better compatibility
echo "📦 Installing optional audio libraries..."
sudo apt install -y libsndfile1-dev

# Install Python audio libraries in virtual environment
echo "🐍 Installing Python audio libraries..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip install soundfile  # For better audio file handling
    echo "✅ soundfile installed in virtual environment"
else
    echo "⚠️  Virtual environment not found. Run from Evil Assistant directory."
fi

# Test sox installation
echo "🧪 Testing sox installation..."
if command -v sox &> /dev/null; then
    echo "✅ sox is installed"
    sox --version
else
    echo "❌ sox installation failed"
fi

# Test if we can create audio effects
echo "🧪 Testing sox audio effects..."
if sox --help effects &> /dev/null; then
    echo "✅ sox effects are available"
else
    echo "❌ sox effects not available"
fi

echo ""
echo "✅ Dependencies installation completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Restart Evil Assistant service: sudo systemctl restart evil-assistant"
echo "   2. Check logs: sudo journalctl -u evil-assistant -f"
echo "   3. Test GPIO: python test_gpio_pwm.py"
