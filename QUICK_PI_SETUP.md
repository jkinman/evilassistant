# Evil Assistant - Quick Pi Setup (Git Clone Method)

## 🚀 **One-Command Pi Setup**

This is the fastest way to get Evil Assistant running on your Raspberry Pi 4 using git clone.

## 📋 **Prerequisites**
- Raspberry Pi 4 (4GB+ RAM recommended) 
- Raspberry Pi OS 64-bit installed
- Internet connection
- SSH access (if setting up remotely)

## ⚡ **Quick Setup Commands**

### **Step 1: SSH to your Pi** (if setting up remotely)
```bash
ssh pi@YOUR_PI_IP_ADDRESS
```

### **Step 2: Clone and Setup** (run on Pi)
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/evilassistant.git
cd evilassistant

# Run the automated setup script
chmod +x setup_pi.sh
./setup_pi.sh
```

That's it! The setup script will:
- ✅ Update system packages
- ✅ Install all dependencies 
- ✅ Set up Python virtual environment
- ✅ Install Evil Assistant package
- ✅ Download Piper TTS models
- ✅ Configure audio system
- ✅ Create systemd service
- ✅ Apply Pi optimizations

### **Step 3: Configure API Keys**
```bash
# Edit the environment file
nano .env

# Add your API keys:
XAI_API_KEY=your_xai_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here
PHILIPS_HUE_BRIDGE_IP=192.168.1.xxx
```

### **Step 4: Test the Assistant**
```bash
# Activate environment and test
source .venv/bin/activate
export PHILIPS_HUE_BRIDGE_IP=192.168.1.xxx
python -m evilassistant --vad --clean
```

### **Step 5: Enable Auto-Start** (Optional)
```bash
# Enable service to start on boot
sudo systemctl enable evil-assistant.service
sudo systemctl start evil-assistant.service

# Check status
sudo systemctl status evil-assistant.service
```

## 🔧 **Quick Tests**

### **Test TTS System**
```bash
source .venv/bin/activate
python -c "
from evilassistant.tts import create_configured_engine
engine = create_configured_engine('piper_ryan_demonic')
print('Testing demonic voice...')
engine.synthesize('Mortal, I have awakened on the Raspberry Pi!', '/tmp/test.wav')
"
```

### **Test Audio I/O**
```bash
# Test microphone (record 3 seconds)
arecord -D plughw:1,0 -d 3 -f cd test.wav

# Test speakers
aplay test.wav

# Clean up
rm test.wav
```

### **Check GPIO Detection**
```bash
python -c "
from evilassistant.config_pi import is_raspberry_pi, check_pi_temperature
print(f'Running on Pi: {is_raspberry_pi()}')
if is_raspberry_pi():
    check_pi_temperature()
"
```

## 🎯 **Expected Performance on Pi 4**

| Operation | Time |
|-----------|------|
| Wake phrase detection | ~100ms |
| Speech transcription | 2-5 seconds |
| AI response | 1-3 seconds |
| TTS synthesis | 1-2 seconds |
| **Total response** | **5-10 seconds** |

## 🔥 **Usage Examples**

Once running, try these commands:

```
"Dark one" → (wait for beep) → "Turn the lights red"
"Evil assistant" → "What's the weather like?"
"Cthulhu" → "Set brightness to 50 percent"
"Dark one" → "Turn off the lights"
```

## 🚨 **Troubleshooting**

### **Audio Issues**
```bash
# Check audio devices
aplay -l
arecord -l

# Configure audio
sudo raspi-config
# Advanced Options > Audio > Force 3.5mm or USB
```

### **Permission Issues**
```bash
# Add user to audio group
sudo usermod -a -G audio $USER

# Logout and login again
```

### **Memory Issues**
```bash
# Check memory
free -h

# The Pi config automatically adjusts based on available memory
```

### **Temperature Issues**
```bash
# Check temperature
vcgencmd measure_temp

# Ensure good cooling/ventilation if >70°C
```

## 📱 **Remote Management**

### **Check Status Remotely**
```bash
ssh pi@YOUR_PI_IP "sudo systemctl status evil-assistant.service"
```

### **View Logs Remotely**
```bash
ssh pi@YOUR_PI_IP "sudo journalctl -u evil-assistant.service -f"
```

### **Restart Service Remotely**
```bash
ssh pi@YOUR_PI_IP "sudo systemctl restart evil-assistant.service"
```

## 🔄 **Updates**

To update your Pi installation:
```bash
cd ~/evilassistant
git pull origin main
source .venv/bin/activate
pip install -e .
sudo systemctl restart evil-assistant.service
```

## 🌟 **Pro Tips**

1. **Use wired network** for best performance
2. **Good cooling** prevents throttling
3. **Quality SD card** improves performance
4. **Monitor temperature** during heavy use
5. **Set static IP** for consistent access

---

**Your Evil Assistant is now ready to haunt your Raspberry Pi!** 🔥🍓👹

Need the full detailed setup guide? See `RASPBERRY_PI_SETUP.md`
