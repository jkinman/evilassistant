# Improved Real-time Configuration for Evil Assistant
# Optimized for Raspberry Pi 4+ with focus on minimal latency

# Audio Settings - Optimized for real-time processing
RATE = 16000  # Reduced from 44100 for faster processing
CHUNK_SIZE = 1024  # Streaming chunk size (64ms at 16kHz)
CHANNELS = 1
DTYPE = 'int16'

# Voice Activity Detection
VAD_FRAME_DURATION_MS = 30  # WebRTCVAD frame duration
VAD_AGGRESSIVENESS = 3  # 0-3, higher = more aggressive silence detection
SILENCE_TIMEOUT_SEC = 1.5  # Stop recording after this much silence
PRE_SPEECH_BUFFER_MS = 300  # Keep this much audio before speech starts

# Wake Word Detection - Multi-tier approach
WAKE_DETECTION_METHOD = "openwakeword"  # "openwakeword", "porcupine", "whisper"
WAKE_PHRASES = ["evil assistant", "dark one", "cthulhu"]
WAKE_THRESHOLD = 0.5  # OpenWakeWord confidence threshold
WAKE_DEBOUNCE_MS = 500  # Prevent multiple triggers

# OpenWakeWord settings (fastest, most reliable)
OPENWAKEWORD_MODEL_PATH = "models/hey_jarvis_v0.1.pkl"  # Download from OpenWakeWord
CUSTOM_WAKE_MODELS = []  # Train custom models for your phrases

# Speech Recognition - Tiered approach for speed
STT_PRIMARY = "vosk"  # "vosk", "faster-whisper", "whisper-cpp"
STT_FALLBACK = "faster-whisper"
VOSK_MODEL_PATH = "models/vosk-model-small-en-us-0.15"  # Lightweight model
WHISPER_MODEL_SIZE = "base"  # Only for fallback
STT_LANGUAGE = "en"

# LLM Processing - Local-first approach
LLM_PRIMARY = "ollama"  # "ollama", "llamafile", "cloud"
LLM_FALLBACK = "cloud"
OLLAMA_MODEL = "llama3.2:3b"  # Fast, capable model for Pi
OLLAMA_BASE_URL = "http://localhost:11434"
CLOUD_MODEL = "grok-2-latest"  # Your current cloud option
MAX_RESPONSE_TOKENS = 150  # Keep responses concise for speed

# TTS - Enhanced options
TTS_PRIMARY = "coqui"  # "coqui", "piper", "elevenlabs"
TTS_FALLBACK = "piper"
COQUI_MODEL = "tts_models/en/ljspeech/tacotron2-DDC"  # Fast, good quality
VOICE_CLONING_ENABLED = True  # Clone a demonic voice sample
DEMON_VOICE_SAMPLE = "samples/demon_voice.wav"  # Train from this

# Audio Effects - Real-time DSP instead of Sox
REALTIME_EFFECTS = True
EFFECT_CHAIN = [
    {"type": "pitch_shift", "semitones": -12},  # Deeper voice
    {"type": "formant_shift", "factor": 0.8},   # More menacing
    {"type": "distortion", "gain": 1.5},        # Gritty texture
    {"type": "reverb", "room_size": 0.8, "damping": 0.3},
    {"type": "bass_boost", "frequency": 100, "gain": 6},
]

# GPIO and LED Control - Optimized
GPIO_ENABLED = True
GPIO_PIN = 18
PWM_FREQUENCY_HZ = 2000  # Higher frequency for smoother dimming
LED_UPDATE_RATE_MS = 20  # 50 Hz updates for smooth response
BRIGHTNESS_CURVE = "logarithmic"  # More natural brightness perception
LED_FADE_TIME_MS = 100  # Smooth transitions

# Smart Home Integration
SMART_HOME_ENABLED = True
HOME_ASSISTANT_URL = "http://homeassistant.local:8123"
HOME_ASSISTANT_TOKEN = ""  # Set in environment
PHILIPS_HUE_BRIDGE_IP = ""  # Auto-discover or set manually
GOOGLE_HOME_DEVICES = []  # Device names for control

# Performance Optimizations
ENABLE_GPU_ACCELERATION = False  # Set True if you have GPU
THREAD_POOL_SIZE = 4  # Parallel processing threads
MEMORY_OPTIMIZATION = True  # Aggressive memory management
CACHE_COMMON_RESPONSES = True  # Pre-generate frequent responses
PRELOAD_MODELS = True  # Load models at startup for faster response

# Buffer Management
AUDIO_BUFFER_SIZE_MS = 500  # Circular buffer for continuous processing
PROCESSING_OVERLAP_MS = 100  # Overlap between processing windows

# Monitoring and Debugging
PERFORMANCE_MONITORING = True
LOG_TIMING_INFO = True
TARGET_LATENCY_MS = 500  # Goal: wake to response start
LATENCY_WARNING_MS = 1000  # Warn if processing takes longer

# Advanced Features
INTERRUPT_CURRENT_RESPONSE = True  # Stop speaking when new wake word detected
CONTEXT_AWARENESS = True  # Remember conversation context
ADAPTIVE_VOLUME = True  # Adjust output volume based on ambient noise
GESTURE_RECOGNITION = False  # Future: camera-based gestures

# Fallback Behavior
OFFLINE_MODE_RESPONSES = [
    "The connection to the dark realm is severed, mortal.",
    "My powers are diminished without the network, foolish human.",
    "The digital void has consumed my voice... try again later."
]

STOP_PHRASES = ["shut up", "be silent", "stop", "unsummon", "quiet"]
