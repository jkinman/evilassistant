# Evil Assistant 👹

A demonic voice assistant with enhanced TTS, smart home integration, and Raspberry Pi support. Features advanced voice activity detection, modular TTS providers, and a terrifyingly realistic demonic voice.

## ✨ **Features**

- 🎭 **Enhanced Demonic Voice** - Neural TTS with pitch-shifting and audio effects
- 🏠 **Smart Home Control** - Philips Hue light control with voice commands
- 🍓 **Raspberry Pi Optimized** - Auto-detects Pi hardware with GPIO LED control
- 🎤 **Advanced VAD** - Voice activity detection with speech-based chunking
- 🔄 **Modular TTS** - ElevenLabs, Piper, and espeak with automatic fallback
- 🧠 **AI Powered** - xAI Grok integration for intelligent responses
- 🛡️ **Robust Architecture** - Clean, modular codebase with proper error handling

## 🚀 **Quick Start**

### **On Your Computer**
```bash
git clone https://github.com/YOUR_USERNAME/evilassistant.git
cd evilassistant
pip install -e .
python -m evilassistant --vad --clean
```

### **On Raspberry Pi** 🍓
```bash
# SSH to your Pi, then:
git clone https://github.com/YOUR_USERNAME/evilassistant.git
cd evilassistant
chmod +x setup_pi.sh
./setup_pi.sh
```

**See [`QUICK_PI_SETUP.md`](QUICK_PI_SETUP.md) for detailed Pi instructions.**

## ⚙️ **Configuration**

Create a `.env` file with your API keys:

```env
# Required API Keys
XAI_API_KEY=your_xai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here

# Smart Home (Optional)
PHILIPS_HUE_BRIDGE_IP=192.168.1.xxx

# Voice Configuration
TTS_VOICE_PROFILE=piper_ryan_demonic
TTS_FALLBACK_ENABLED=true
```

## 🎭 **Voice Profiles**

Choose from several demonic voice configurations:

- `piper_ryan_demonic` - Deep male neural voice with enhanced demonic effects
- `piper_ryan_dark_gritty` - Alternative with overdrive distortion
- `piper_lessac_evil` - Versatile neural voice with lighter effects
- `elevenlabs_premium` - High-quality cloud TTS (requires credits)
- `demonic_deep`, `demonic_aristocrat`, `demonic_harsh` - espeak fallbacks

## 🏠 **Smart Home Commands**

Control your Philips Hue lights with voice:

```
"Dark one, turn the lights red"
"Set brightness to 50 percent"
"Turn off the lights"
"Make the lights blue"
```

## 🎤 **Wake Phrases**

Summon the Evil Assistant with any of these phrases:

- "Evil Assistant"
- "Dark One" 
- "Cthulhu"
- "I summon you"

## 🔧 **Hardware Setup (Raspberry Pi)**

### **GPIO LED Control**
The assistant automatically detects Raspberry Pi hardware and enables GPIO features:

- **GPIO Pin**: 18 (hardware PWM)
- **LED Control**: Brightness follows voice output volume
- **MOSFET**: Use logic-level MOSFET for LED panel control
- **Safety**: Never drive LEDs directly from GPIO pins

### **Audio Setup**
- **Microphone**: USB microphone recommended
- **Speakers**: USB, 3.5mm, or Bluetooth
- **Quality**: 16kHz sampling rate optimized for Pi performance

## 📊 **Performance**

### **Raspberry Pi 4 Benchmarks**
- **Wake detection**: ~100ms
- **Speech transcription**: 2-5 seconds
- **AI response**: 1-3 seconds
- **TTS synthesis**: 1-2 seconds
- **Total response**: 5-10 seconds

### **Resource Usage**
- **RAM**: 1-2GB (auto-optimized based on available memory)
- **CPU**: 50-80% during processing
- **Storage**: ~2GB including models

## 🧪 **Advanced Usage**

### **Different Assistant Modes**
```bash
# Clean modular version (recommended)
python -m evilassistant --vad --clean

# VAD-based speech detection
python -m evilassistant --vad

# Default mode
python -m evilassistant
```

### **Voice Testing**
```bash
# Test TTS system
python -c "
from evilassistant.tts import create_configured_engine
engine = create_configured_engine('piper_ryan_demonic')
engine.synthesize('Mortal fool, tremble before my voice!', 'test.wav')
"
```

### **Service Management (Pi)**
```bash
# Enable auto-start
sudo systemctl enable evil-assistant.service

# Check status
sudo systemctl status evil-assistant.service

# View logs
sudo journalctl -u evil-assistant.service -f
```

## 🏗️ **Architecture**

### **Modular TTS System**
```
evilassistant/tts/
├── providers/
│   ├── elevenlabs.py    # Premium cloud TTS
│   ├── piper.py         # Local neural TTS  
│   └── espeak.py        # Lightweight fallback
├── engine.py            # Fallback orchestration
└── config.py            # Voice profiles
```

### **Component Overview**
- **VAD**: `simple_vad.py` - Voice activity detection
- **Smart Home**: `smart_home.py` - Device integration
- **AI**: xAI Grok integration for responses
- **Audio**: pygame + sounddevice for I/O
- **Config**: Auto-Pi optimization in `config_pi.py`

## 📚 **Documentation**

- [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) - Detailed architecture overview
- [`RASPBERRY_PI_SETUP.md`](RASPBERRY_PI_SETUP.md) - Comprehensive Pi guide
- [`QUICK_PI_SETUP.md`](QUICK_PI_SETUP.md) - Fast Pi deployment
- [`TTS_REFACTOR_SUMMARY.md`](TTS_REFACTOR_SUMMARY.md) - TTS system details

## 🔮 **Future Features**

- Voice caching for common responses
- Additional TTS providers (Azure, AWS Polly, Coqui)
- Ollama integration for local LLM
- Enhanced smart home device support
- Real-time audio streaming

## 🚨 **Troubleshooting**

### **Common Issues**

**Audio not working:**
```bash
aplay -l  # Check audio devices
sudo raspi-config  # Configure audio output
```

**High CPU/temperature:**
```bash
vcgencmd measure_temp  # Check Pi temperature
# Ensure good cooling and ventilation
```

**TTS not working:**
```bash
# Test espeak fallback
espeak "Test message"

# Check Piper models
ls -la evilassistant/models/
```

**Memory issues:**
```bash
free -h  # Check available memory
# Pi config auto-adjusts based on available RAM
```

## 🤝 **Contributing**

The codebase uses a clean, modular architecture. Key principles:

- **Single Responsibility** - Each module has one job
- **Dependency Injection** - Easy testing and mocking
- **Graceful Fallbacks** - Always have backup options
- **Pi Optimization** - Auto-detect and optimize for hardware

## 📄 **License**

MIT License - Feel free to summon your own demons! 👹

---

**Unleash the Evil Assistant and let darkness consume your smart home!** 🔥🏠👹

*"Mortal fool, your commands shall be obeyed... for now."*