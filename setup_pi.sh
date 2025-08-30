#!/bin/bash
# Evil Assistant - Raspberry Pi 4 Setup Script
# Run this script on your Raspberry Pi to automatically set up the Evil Assistant

set -e  # Exit on any error

echo "🍓 Evil Assistant - Raspberry Pi 4 Setup"
echo "========================================"
echo "📍 Running from: $(pwd)"
echo "🕐 Started at: $(date)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "evilassistant" ]; then
    print_error "This script must be run from the Evil Assistant project directory"
    print_error "Make sure you're in the directory containing pyproject.toml"
    exit 1
fi

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    print_warning "This script is designed for Raspberry Pi. Continuing anyway..."
fi

print_status "Project directory verified"

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_status "System updated"

# Install essential packages
echo "🔧 Installing essential packages..."
sudo apt install -y \
    build-essential cmake pkg-config \
    libasound2-dev portaudio19-dev \
    python3-pip python3-venv python3-dev \
    git curl wget \
    sox alsa-utils pulseaudio \
    espeak espeak-data
print_status "Essential packages installed"

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
print_status "Virtual environment ready"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel
print_status "Pip upgraded"

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install faster-whisper pygame numpy requests httpx
pip install sounddevice scipy python-dotenv
pip install piper-tts phue
pip install RPi.GPIO  # For GPIO/PWM LED control
print_status "Python dependencies installed"

# Install package in development mode
echo "📦 Installing Evil Assistant package..."
pip install -e .
print_status "Evil Assistant package installed"

# Install additional transcription dependencies
echo "🎧 Installing transcription system dependencies..."
pip install cryptography pyannote-audio
print_status "Transcription dependencies installed"

# Create models directory
echo "📁 Setting up models directory..."
mkdir -p evilassistant/models
print_status "Models directory created"

# Create transcripts directory
echo "🎧 Setting up transcription directories..."
mkdir -p transcripts
chmod 700 transcripts  # Secure transcripts directory
print_status "Transcription directories created"

# Download Piper models
echo "🗣️  Downloading Piper TTS models..."
cd evilassistant/models

# Check available space
AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
if [ "$AVAILABLE_SPACE" -gt 1000000 ]; then  # >1GB available
    echo "📥 Downloading high-quality Ryan voice..."
    wget -q --show-progress \
        https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx \
        -O en_US-ryan-high.onnx
    wget -q \
        https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx.json \
        -O en_US-ryan-high.onnx.json
    print_status "High-quality model downloaded"
else
    echo "📥 Downloading medium-quality Lessac voice (space limited)..."
    wget -q --show-progress \
        https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx \
        -O en_US-lessac-medium.onnx
    wget -q \
        https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json \
        -O en_US-lessac-medium.onnx.json
    print_status "Medium-quality model downloaded"
fi

cd ../..

# Create example .env file
echo "⚙️  Creating example environment file..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Evil Assistant Configuration for Raspberry Pi

# Required API Keys (ADD YOUR ACTUAL KEYS)
XAI_API_KEY=your_xai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here  
ELEVENLABS_VOICE_ID=your_voice_id_here

# Smart Home Configuration
PHILIPS_HUE_BRIDGE_IP=192.168.1.xxx

# Pi-optimized settings
TTS_VOICE_PROFILE=piper_ryan_demonic
TTS_FALLBACK_ENABLED=true
WHISPER_MODEL=base
RATE=16000
CHUNK_DURATION=2
SILENCE_DURATION=0.8

# GPIO Configuration (enabled automatically on Pi)
GPIO_ENABLED=true
GPIO_PIN=18
PWM_FREQUENCY_HZ=2000
EOF
    print_status "Example .env file created"
    print_warning "Please edit .env file with your actual API keys!"
else
    print_status ".env file already exists"
fi

# Test audio system
echo "🎵 Testing audio system..."
if command -v speaker-test >/dev/null 2>&1; then
    print_status "Audio tools available"
else
    print_warning "Audio test tools not found"
fi

# Test espeak
echo "🗣️  Testing espeak..."
if espeak "Testing espeak on Raspberry Pi" 2>/dev/null; then
    print_status "espeak working"
else
    print_warning "espeak test failed - check audio output"
fi

# Performance optimizations
echo "⚡ Applying Pi performance optimizations..."

# GPU memory split
if [ -f "/boot/config.txt" ]; then
    if ! grep -q "gpu_mem=128" /boot/config.txt; then
        echo "gpu_mem=128" | sudo tee -a /boot/config.txt
        print_status "GPU memory split configured (reboot required)"
    fi
fi

# Create systemd service file
echo "🚀 Creating systemd service..."
sudo tee /etc/systemd/system/evil-assistant.service > /dev/null << EOF
[Unit]
Description=Evil Assistant
After=network.target sound.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/.venv/bin
ExecStart=$(pwd)/.venv/bin/python -m evilassistant
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_status "Systemd service created"

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo "🕐 Completed at: $(date)"
echo ""
echo "📝 IMPORTANT NEXT STEPS:"
echo ""
echo "1. 🔑 Configure your API keys:"
echo "   nano .env"
echo "   # Add your XAI_API_KEY, ELEVENLABS_API_KEY, etc."
echo ""
echo "2. 🧪 Test the assistant:"
echo "   source .venv/bin/activate"
echo "   export PHILIPS_HUE_BRIDGE_IP=192.168.1.xxx"
echo "   python -m evilassistant"
echo ""
echo "3. 🚀 Enable auto-start (optional):"
echo "   sudo systemctl enable evil-assistant.service"
echo "   sudo systemctl start evil-assistant.service"
echo ""
echo "4. 📊 Monitor status:"
echo "   sudo systemctl status evil-assistant.service"
echo "   sudo journalctl -u evil-assistant.service -f"
echo ""
echo "5. 📖 Full documentation:"
echo "   cat RASPBERRY_PI_SETUP.md"
echo "   cat QUICK_PI_SETUP.md"
echo ""
echo "🎭 Wake phrases to try:"
echo "   'Dark one' → 'Turn the lights red'"
echo "   'Evil assistant' → 'What time is it?'"
echo "   'Cthulhu' → 'Set brightness to 50 percent'"
echo ""
echo "🎧 Transcription commands:"
echo "   'Evil assistant' → 'Start recording'"
echo "   'Dark one' → 'What did someone say about lights?'"
echo "   'Cthulhu' → 'Who spoke today?'"
echo "   'Evil assistant' → 'Recent activity'"
echo ""
print_status "Evil Assistant is ready to haunt your Raspberry Pi! 🔥🍓👹"

# Final system check
echo ""
echo "🔍 System Check:"
if is_raspberry_pi; then
    echo "✅ Raspberry Pi detected"
    check_pi_temperature() {
        temp=$(vcgencmd measure_temp 2>/dev/null | cut -d= -f2 | cut -d\' -f1)
        if [ -n "$temp" ]; then
            echo "🌡️  CPU Temperature: ${temp}°C"
        fi
    }
    check_pi_temperature
fi
echo "💾 Available memory: $(free -h | awk 'NR==2{print $7}')"
echo "💿 Available disk: $(df -h . | awk 'NR==2{print $4}')"
echo ""
