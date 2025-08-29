# 🎧 Evil Assistant - Continuous Transcription & Speaker Recognition

The Evil Assistant includes a sophisticated conversation surveillance system that can transcribe all speech in your environment and identify different speakers - all while maintaining your privacy with local encryption.

## ✨ **Features**

### **🎤 Continuous Transcription**
- **Real-time speech-to-text** using Faster-Whisper
- **Background processing** doesn't interfere with assistant responses
- **Energy-based filtering** ignores background noise
- **Configurable sensitivity** for different environments

### **👥 Anonymous Speaker Recognition**
- **Automatic speaker identification** using voice characteristics
- **Anonymous tracking** (Speaker1, Speaker2, etc. - no biometric storage)
- **Speaker statistics** and conversation patterns
- **Multi-speaker conversation analysis**

### **🔐 Privacy Protection**
- **AES-256 encryption** for all stored transcripts
- **Local storage only** - nothing sent to the cloud
- **Automatic deletion** after configurable retention period (default: 7 days)
- **Secure key generation** with proper file permissions
- **Voice-controlled privacy** controls

### **👹 Evil Assistant Integration**
- **Demonic voice commands** for transcript search and control
- **Natural language queries** about conversations
- **Seamless integration** with existing wake phrase system
- **Evil-themed responses** to all commands

## 🗣️ **Voice Commands**

### **Start/Stop Recording**
```
"Evil assistant, start recording"
"Dark one, begin surveillance" 
"Cthulhu, start listening"

"Evil assistant, stop recording"
"Dark one, cease monitoring"
"Cthulhu, end surveillance"
```

### **Search Conversations**
```
"Evil assistant, what did someone say about lights?"
"Dark one, search for pizza"
"Cthulhu, what was said about the meeting?"
"Evil assistant, find conversation about work"
```

### **Speaker Information**
```
"Evil assistant, who spoke today?"
"Dark one, how many people talked?"
"Cthulhu, show me the speakers"
"Evil assistant, who was talking?"
```

### **Recent Activity**
```
"Evil assistant, recent activity"
"Dark one, what happened in the last hour?"
"Cthulhu, today's conversations"
"Evil assistant, what was said lately?"
```

### **Statistics & Status**
```
"Evil assistant, stats"
"Dark one, transcription summary"
"Cthulhu, show me the surveillance report"
```

## 📊 **Example Evil Responses**

### **Starting Surveillance**
> *"I now hear every whisper in your domain, mortal!"*
> 
> *"Your conversations are mine to harvest and hoard!"*
> 
> *"Nothing escapes my all-hearing presence!"*

### **Search Results**
> *"I found 3 instances of your pitiful conversations!"*
> 
> *"At 14:30, Speaker1 spoke: 'Turn on the living room lights' And 2 more instances, mortal!"*

### **Speaker Summary**
> *"My surveillance has identified 2 separate mortals! Speaker1 last spoke at 15:45 with 12 recorded segments. Speaker2 last spoke at 16:20 with 8 recorded segments."*

### **Recent Activity**
> *"In the last hour, I recorded 5 conversations! Most recently, Speaker1 spoke at 16:30: 'Can you dim the lights to 50 percent?'"*

## 🔧 **Technical Details**

### **Storage Structure**
```
transcripts/
├── transcripts_2024-01-15.enc    # Daily encrypted logs
├── transcripts_2024-01-16.enc
└── ...

.transcript_key                    # Encryption key (secure)
```

### **Encryption Details**
- **Algorithm**: AES-256 in Fernet format (cryptography library)
- **Key generation**: Secure random key generation
- **Key storage**: Local file with 600 permissions (owner read-only)
- **Data format**: JSON encrypted with timestamps and metadata

### **Speaker Identification**
- **Features analyzed**: Amplitude variance, zero-crossing rate, spectral characteristics
- **Matching algorithm**: Simple clustering based on voice characteristics
- **Anonymous IDs**: No biometric data stored, only anonymous speaker numbers
- **Accuracy**: Basic speaker distinction (can be enhanced with pyannote-audio)

### **Performance Optimizations**
- **Background processing**: Transcription happens in separate threads
- **Energy filtering**: Only processes speech above threshold
- **Batch processing**: Efficient handling of audio chunks
- **Memory management**: Automatic cleanup of processed audio

## ⚙️ **Configuration**

### **Basic Settings** (in `config.py`)
```python
# Transcription settings
WHISPER_MODEL = "base"              # Whisper model size
MIN_CONFIDENCE = 0.3                # Minimum confidence threshold
CHUNK_DURATION = 10.0              # Audio chunk length (seconds)

# Privacy settings  
TRANSCRIPT_RETENTION_DAYS = 7       # Auto-delete after N days
ENABLE_SPEAKER_ID = True           # Enable speaker recognition
```

### **Advanced Settings**
```python
# Performance tuning
WHISPER_COMPUTE_TYPE = "int8"      # CPU optimization
WHISPER_BEAM_SIZE = 1              # Speed vs accuracy
WHISPER_NUM_WORKERS = 2            # Parallel processing

# Privacy controls
STORAGE_DIRECTORY = "transcripts"   # Where to store logs
ENCRYPTION_ENABLED = True          # Always keep enabled!
```

## 🛡️ **Privacy & Security**

### **What's Stored**
- ✅ **Text transcripts** (encrypted)
- ✅ **Timestamps** (when things were said)
- ✅ **Anonymous speaker IDs** (Speaker1, Speaker2, etc.)
- ✅ **Confidence scores** (transcription quality)
- ✅ **Audio duration** (length of segments)

### **What's NOT Stored**
- ❌ **Raw audio files** (deleted immediately after transcription)
- ❌ **Biometric voice data** (no voice prints or samples)
- ❌ **Personal identifiers** (no names or real identities)
- ❌ **Cloud data** (everything stays local)

### **Privacy Controls**
- **Voice-activated deletion**: "Evil assistant, delete conversations"
- **Automatic expiry**: Old transcripts auto-delete after 7 days
- **Secure storage**: AES-256 encryption with local keys
- **Opt-out anytime**: "Evil assistant, stop recording"

## 🚀 **Installation**

### **Dependencies**
```bash
# Required packages (auto-installed)
pip install cryptography pyannote-audio
```

### **Setup**
```bash
# Test the system
python test_transcription.py

# Run Evil Assistant WITH transcription (privacy warning!)
python -m evilassistant --transcription

# Run Evil Assistant WITHOUT transcription (default, privacy-safe)
python -m evilassistant

# Enable transcription (only works with --transcription flag)
# Say: "Evil assistant, start recording"
```

### **File Permissions**
The system automatically sets secure permissions:
- **Transcripts directory**: `700` (owner access only)
- **Encryption key**: `600` (owner read-only)
- **Log files**: `600` (owner read-only)

## 🎯 **Use Cases**

### **Smart Home Automation**
> *"Evil assistant, what did I say about the lights yesterday?"*
> 
> Search for specific home automation commands and patterns.

### **Meeting Notes**
> *"Dark one, who was talking about the project timeline?"*
> 
> Find mentions of specific topics in conversations.

### **Family Activity**
> *"Cthulhu, what did the kids say about homework?"*
> 
> Track conversations and activities around the house.

### **Security Monitoring**
> *"Evil assistant, recent activity"*
> 
> Monitor for unusual conversations or activity patterns.

## 🔮 **Future Enhancements**

- **Enhanced speaker recognition** with pyannote-audio
- **Conversation summaries** and topic detection  
- **Temporal queries** ("what was said this morning?")
- **Export functionality** for backups
- **Custom wake word training** from transcripts
- **Smart notifications** for important conversations

---

**🔥 The Evil Assistant's transcription system gives you unprecedented insight into the conversations in your domain - all while maintaining privacy and security through local encryption!**
