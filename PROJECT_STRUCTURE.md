# Evil Assistant - Project Structure

## 🏗️ **Current Architecture (Post-Cleanup)**

### **Main Entry Points**
- `python -m evilassistant` - Single entry point with modern architecture

### **Core Components**

#### **Primary Assistant**
- `evilassistant/assistant_clean.py` - Main production assistant (modular, clean)
- `evilassistant/assistant_vad.py` - VAD-based speech detection version
- `evilassistant/config.py` - Configuration settings

#### **TTS Engine (Fully Modular)**
```
evilassistant/tts/
├── __init__.py          # Package exports
├── base.py              # Abstract TTS provider base class
├── config.py            # Voice configurations and profiles  
├── engine.py            # Main TTS engine with fallback
├── factory.py           # Engine factory functions
└── providers/           # 📁 Individual provider implementations
    ├── __init__.py      #   Provider exports
    ├── espeak.py        #   EspeakProvider (local fallback)
    ├── elevenlabs.py    #   ElevenLabsProvider (premium cloud)
    └── piper.py         #   PiperProvider (neural local)
```

#### **Supporting Modules**
- `evilassistant/simple_vad.py` - Voice activity detection
- `evilassistant/smart_home.py` - Smart home controller
- `evilassistant/simple_smart_home.py` - Simplified smart home integration

#### **Model Files**
```
evilassistant/models/
├── en_US-ryan-high.onnx         # Piper neural voice model (deep male)
├── en_US-ryan-high.onnx.json    # Model configuration
├── en_US-lessac-medium.onnx     # Piper neural voice model (versatile)
└── en_US-lessac-medium.onnx.json # Model configuration
```

### **Project Organization**

#### **Archive** (Preserved but unused)
- `archive/` - Contains old/broken components for reference
  - Legacy assistants (assistant.py, async_assistant.py)
  - Broken optimized components (audio_stream.py, wake_word.py, etc.)
  - Old setup scripts and documentation
  - Original monolithic TTS engine

#### **Temporary Files**
- `temp/` - All test files and temporary audio files
  - Automatically ignored by git
  - Safe to delete entire folder
  - Contains old test scripts and audio samples

### **Configuration**

#### **Voice Profiles Available**
- `piper_ryan_demonic` - Deep male neural voice with enhanced demonic effects
- `piper_ryan_dark_gritty` - Alternative with overdrive distortion  
- `piper_lessac_evil` - Versatile neural voice with lighter effects
- `elevenlabs_premium` - High-quality cloud TTS (when API available)
- Various espeak fallbacks

#### **TTS Priority System**
1. **ElevenLabs** (Priority 0) - Premium quality, costs money
2. **Piper** (Priority 1) - High-quality neural voices, free
3. **espeak** (Priority 2) - Basic fallback, always available

### **Smart Home Integration**
- **Philips Hue** - Color changing, brightness control, on/off
- **Future**: Google Home, Home Assistant support planned

### **Key Features**
- ✅ **Modular Architecture** - Clean separation of concerns
- ✅ **Automatic Fallback** - TTS providers with intelligent switching  
- ✅ **Enhanced Demonic Voice** - Pitch-shifted neural TTS with effects
- ✅ **Interrupt Support** - Stop commands during playback
- ✅ **Smart Home Control** - Philips Hue integration
- ✅ **Voice Activity Detection** - Speech-based audio chunking
- ✅ **Question Extraction** - Salvage questions spoken with wake phrase

### **Dependencies**
- **Core**: faster-whisper, pygame, requests, numpy
- **TTS**: piper-tts, sox (for audio effects)
- **Smart Home**: phue (Philips Hue)
- **LLM**: httpx (for xAI Grok API)
- **Optional**: python-dotenv (for .env files)

### **Environment Variables**
```bash
XAI_API_KEY=your_xai_key
ELEVENLABS_API_KEY=your_elevenlabs_key  
ELEVENLABS_VOICE_ID=your_voice_id
PHILIPS_HUE_BRIDGE_IP=192.168.x.x
```

### **Usage Examples**
```bash
# Start with enhanced demonic voice
python -m evilassistant

# Test voice quality
python -c "from evilassistant.tts import create_configured_engine; engine = create_configured_engine('piper_ryan_demonic'); engine.synthesize('Test voice', 'test.wav')"

# Smart home commands
"Dark one, turn the lights red"
"Set brightness to 50 percent"  
"Turn off the lights"
```

### **Future Improvements**
- Voice caching system
- Ollama local LLM integration  
- Coqui TTS for voice cloning
- Performance monitoring
- Async processing pipeline

### **Easy TTS Provider Extension**
Adding new TTS providers is now trivial thanks to the modular structure:

```python
# Add providers/azure.py
class AzureProvider(TTSProvider):
    def is_available(self) -> bool:
        return os.getenv("AZURE_SPEECH_KEY") is not None
    
    def synthesize(self, text: str, output_file: str) -> bool:
        # Azure implementation here
        pass

# Add providers/aws_polly.py  
class PollyProvider(TTSProvider):
    def is_available(self) -> bool:
        return boto3.Session().get_credentials() is not None
    
    def synthesize(self, text: str, output_file: str) -> bool:
        # AWS Polly implementation here
        pass

# Add providers/coqui.py
class CoquiProvider(TTSProvider):
    def is_available(self) -> bool:
        return self.model_path and os.path.exists(self.model_path)
    
    def synthesize(self, text: str, output_file: str) -> bool:
        # Coqui voice cloning implementation here
        pass
```

Then simply update `providers/__init__.py` and configure in `engine.py`!

---

## 🧹 **Cleanup Summary**

### **What Was Moved to Archive**
- Old broken async components
- Legacy assistant implementations  
- Experimental/incomplete features
- Old setup scripts and documentation

### **What Was Moved to Temp**
- All test files and scripts
- Audio samples and experiments
- Development artifacts

### **What Was Refactored**
- Monolithic `tts_engine.py` → Modular `tts/` package
- Hard-coded voice settings → Configurable profiles
- Tight coupling → Proper separation of concerns

### **What Was Simplified**
- Entry points (removed broken options)
- Dependencies (archived unused components)
- File structure (cleaner, more maintainable)

The project is now much cleaner, more maintainable, and easier to extend! 🎉
