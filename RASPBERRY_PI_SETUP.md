# Evil Assistant - Raspberry Pi 4 Setup Guide

## 🍓 **Raspberry Pi 4 Deployment**

This guide covers deploying the Evil Assistant on a Raspberry Pi 4 with full functionality including GPIO LED control, audio processing, and smart home integration.

## 📋 **Prerequisites**

### **Hardware Requirements**
- **Raspberry Pi 4** (4GB+ RAM recommended)
- **microSD card** (32GB+ Class 10)
- **USB microphone** or USB sound card with mic input
- **Speakers/headphones** (USB, 3.5mm, or Bluetooth)
- **LED panel** + MOSFET for GPIO control (optional)
- **Reliable internet connection**

### **Recommended Pi 4 Setup**
- Raspberry Pi OS 64-bit (Bullseye or newer)
- Python 3.9+ (should be included)
- At least 2GB free space

## 🚀 **Step-by-Step Installation**

### **1. Prepare Raspberry Pi OS**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential development tools
sudo apt install -y build-essential cmake pkg-config
sudo apt install -y libasound2-dev portaudio19-dev
sudo apt install -y python3-pip python3-venv python3-dev
sudo apt install -y git curl wget

# Install audio tools
sudo apt install -y sox alsa-utils pulseaudio
```

### **2. Audio Setup**

```bash
# Test microphone
arecord -l  # List recording devices
aplay -l    # List playback devices

# Test recording (should create test.wav)
arecord -D plughw:1,0 -d 5 -f cd test.wav
aplay test.wav

# If using USB audio, you may need to set default device
# Edit ~/.asoundrc or /etc/asound.conf
```

### **3. Clone and Setup Evil Assistant**

```bash
# Clone repository
cd ~
git clone <your-repo-url> evilassistant
cd evilassistant

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install --upgrade pip setuptools wheel

# Install core dependencies
pip install faster-whisper pygame numpy requests httpx
pip install sounddevice scipy python-dotenv

# Install TTS dependencies
pip install piper-tts

# Install smart home dependencies  
pip install phue

# Install the package in development mode
pip install -e .
```

### **4. Download Piper Models**

```bash
# Create models directory
mkdir -p evilassistant/models

# Download Piper models (choose based on storage/performance needs)
cd evilassistant/models

# High quality (recommended if space allows)
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx.json

# Alternative: Medium quality (smaller files)
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

cd ../..
```

### **5. Install espeak (Fallback TTS)**

```bash
# Install espeak as fallback TTS
sudo apt install -y espeak espeak-data

# Test espeak
espeak "Hello from Raspberry Pi"
```

### **6. GPIO Setup (Optional)**

```bash
# Install GPIO libraries (usually pre-installed)
pip install RPi.GPIO

# Test GPIO (will be enabled automatically when running on Pi)
# The assistant will detect Pi hardware and enable GPIO features
```

### **7. Configure Environment**

```bash
# Create .env file
nano .env

# Add your API keys and configuration:
```

```env
# Required API Keys
XAI_API_KEY=your_xai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here

# Smart Home Configuration
PHILIPS_HUE_BRIDGE_IP=192.168.1.xxx

# Pi-specific optimizations
TTS_VOICE_PROFILE=piper_ryan_demonic
TTS_FALLBACK_ENABLED=true

# Audio settings for Pi
RATE=16000
CHUNK_DURATION=2
SILENCE_DURATION=0.8
```

## ⚡ **Pi 4 Performance Optimizations**

### **Memory Optimization**

```bash
# Increase GPU memory split for better performance
sudo raspi-config
# Advanced Options > Memory Split > Set to 128MB

# Enable memory overcommit
echo 'vm.overcommit_memory=1' | sudo tee -a /etc/sysctl.conf
```

### **CPU Optimization**

```bash
# Set CPU governor to performance
echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Or make permanent:
sudo nano /etc/rc.local
# Add before 'exit 0':
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### **Faster-Whisper Optimization**

The assistant uses faster-whisper which is optimized for ARM. For Pi 4:

```python
# In config.py, these settings are Pi-friendly:
WHISPER_MODEL = "base"  # Good balance of speed/accuracy on Pi
RATE = 16000           # Optimal for Pi audio processing
```

## 🧪 **Testing on Pi**

### **1. Basic Functionality Test**

```bash
cd ~/evilassistant
source .venv/bin/activate

# Test TTS system
python -c "
from evilassistant.tts import create_configured_engine
engine = create_configured_engine('piper_ryan_demonic')
if engine.synthesize('Testing on Raspberry Pi', '/tmp/test.wav'):
    print('✅ TTS working')
    import pygame; pygame.mixer.init()
    pygame.mixer.music.load('/tmp/test.wav')
    pygame.mixer.music.play()
    import time; time.sleep(3)
else:
    print('❌ TTS failed')
"
```

### **2. Audio Test**

```bash
# Test microphone and speaker
python -c "
import sounddevice as sd
import numpy as np
print('🎤 Recording 3 seconds...')
audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1)
sd.wait()
print('🔊 Playing back...')
sd.play(audio, 16000)
sd.wait()
print('✅ Audio test complete')
"
```

### **3. Full Assistant Test**

```bash
# Set Hue bridge IP
export PHILIPS_HUE_BRIDGE_IP=192.168.1.xxx

# Test transcription system
python test_transcription.py

# Start the assistant
python -m evilassistant
```

### **4. Transcription Features Test**

Once the assistant is running:

```bash
# Say these commands:
"Evil assistant, start recording"      # Begin transcription
"Dark one, who spoke today?"          # Check speakers
"Cthulhu, recent activity"           # Recent conversations  
"Evil assistant, stats"              # Transcription stats
```

## 🔧 **Pi-Specific Configuration**

### **Auto-start on Boot**

Create a systemd service:

```bash
sudo nano /etc/systemd/system/evil-assistant.service
```

```ini
[Unit]
Description=Evil Assistant
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/evilassistant
Environment=PATH=/home/pi/evilassistant/.venv/bin
Environment=PHILIPS_HUE_BRIDGE_IP=192.168.1.xxx
ExecStart=/home/pi/evilassistant/.venv/bin/python -m evilassistant
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable the service
sudo systemctl enable evil-assistant.service
sudo systemctl start evil-assistant.service

# Check status
sudo systemctl status evil-assistant.service
```

### **GPIO LED Configuration**

The assistant automatically detects Pi hardware. Configure in your `.env`:

```env
# GPIO settings
GPIO_ENABLED=true
GPIO_PIN=18
PWM_FREQUENCY_HZ=2000
```

## 🚨 **Troubleshooting**

### **Common Pi Issues**

1. **Audio Not Working**
   ```bash
   # Check audio devices
   aplay -l
   arecord -l
   
   # Set default audio device
   sudo raspi-config
   # Advanced Options > Audio > Force 3.5mm/USB
   ```

2. **Memory Issues**
   ```bash
   # Check memory usage
   free -h
   
   # Reduce model size in config.py:
   WHISPER_MODEL = "tiny"  # Smallest model
   ```

3. **Slow Performance**
   ```bash
   # Check CPU temperature
   vcgencmd measure_temp
   
   # Ensure good cooling and ventilation
   ```

4. **TTS Not Working**
   ```bash
   # Test espeak fallback
   espeak "Test message"
   
   # Check Piper models
   ls -la evilassistant/models/
   ```

5. **Network Issues**
   ```bash
   # Test internet connectivity
   ping -c 3 api.x.ai
   ping -c 3 api.elevenlabs.io
   ```

## 📊 **Expected Performance**

### **Raspberry Pi 4 Benchmarks**
- **Wake phrase detection**: ~100ms
- **Speech transcription**: 2-5 seconds (base model)
- **AI response**: 1-3 seconds (network dependent)  
- **TTS synthesis**: 1-2 seconds (Piper)
- **Total response time**: 5-10 seconds

### **Resource Usage**
- **RAM**: 1-2GB (with base model)
- **CPU**: 50-80% during processing
- **Storage**: ~2GB for models and dependencies

## 🎯 **Optimization Tips**

1. **Use smaller Whisper model** for faster transcription
2. **Enable swap** if RAM is limited (2GB+)
3. **Use wired network** instead of Wi-Fi for stability
4. **Good cooling** prevents thermal throttling
5. **Quality SD card** improves I/O performance

## 🔮 **Next Steps After Setup**

1. Test wake phrase detection accuracy
2. Verify smart home device control
3. Optimize voice quality settings
4. Set up auto-start service
5. Configure LED panel if desired
6. Fine-tune for your environment

---
**Ready to unleash the Evil Assistant on your Raspberry Pi!** 🔥🍓👹
