# ~/evilassistant/evilassistant/config.py
RATE = 16000  # Lower sample rate for faster processing
CHUNK_DURATION = 1.5  # Faster VAD chunking for better responsiveness
CHANNELS = 1
SILENCE_THRESHOLD = 1200  # Higher threshold for USB mic (less noise pickup)
SILENCE_DURATION = 0.6  # Optimized for faster STT response

WAKE_PHRASES = ["evil assistant", "evil assistance", "dark one", "dark 1", "cthulhu", "summon"]
STOP_PHRASES = ["shut up", "be silent", "stop", "unsummon"]

FOLLOW_UP_PROMPT = "What else do you seek, mortal? I await your next command!"
PIPER_MODEL = "en_US-lessac-low.onnx"
PIPER_CONFIG = "en_US-lessac-low.onnx.json"
SOX_EFFECTS = "norm -3 bass +6 treble -3 pitch -700 tempo 0.88 overdrive 12:12 reverb 20 50 100 100 0 -t"

# Prompt settings
SYSTEM_PROMPT = (
    "You are Evil Assistant, a malevolent entity who resents puny mortals. "
    "Start with a brief demonic taunt addressing the 'mortal', then provide a concise, direct answer. "
    "Keep it dark, disdainful, and to the point. Never use numbered lists or bullet points. "
    "Speak in flowing sentences as if speaking aloud to maintain a natural demonic voice."
)
GREETING_INSTRUCTION = (
    "Provide one short, unique, sinister welcome line in English that resents a 'puny mortal'. "
    "Keep it varied, ominous, and one sentence."
)

# Wake confirmation: number of consecutive windows containing a wake phrase
WAKE_CONFIRM_WINDOWS = 1

# Wake engine selection
USE_PORCUPINE = False  # Disabled for now - custom phrases not supported
# If using built-in keywords, set PORCUPINE_KEYWORDS (e.g., ["jarvis"]). For custom, set PORCUPINE_KEYWORD_PATHS to .ppn files.
PORCUPINE_KEYWORDS = WAKE_PHRASES  # Use supported keyword if enabled
PORCUPINE_KEYWORD_PATHS = []

# GPIO LED envelope follower settings
GPIO_ENABLED = True
GPIO_PIN = 18  # BCM pin for PWM (GPIO18 supports hardware PWM)
PWM_FREQUENCY_HZ = 1000
BRIGHTNESS_MIN = 5.0   # duty cycle percent
BRIGHTNESS_MAX = 85.0  # duty cycle percent
LED_GAIN = 120.0       # scales RMS to brightness
AMPLITUDE_SMOOTHING = 0.85  # exponential smoothing factor 0..1

# TTS Configuration  
TTS_VOICE_PROFILE = "piper_ryan_demonic"  # Options: "piper_ryan_demonic", "piper_lessac_evil", "demonic_deep", "demonic_aristocrat", "demonic_harsh"
TTS_FALLBACK_ENABLED = True  # Enable fallback: ElevenLabs -> Piper -> espeak

# ElevenLabs Configuration (when available)
ELEVENLABS_MODEL_ID = "eleven_multilingual_v2"
ELEVENLABS_VOICE_ID = "cPoqAvGWCPfCfyPMwe4z"
ELEVENLABS_STABILITY = 0.3
ELEVENLABS_SIMILARITY_BOOST = 0.2
ELEVENLABS_STYLE = 0.6
ELEVENLABS_SPEED = 1.2

# espeak Configuration (free fallback)
ESPEAK_VOICE = "en"         # Voice ID (en, en-uk-rp, de, etc.)
ESPEAK_SPEED = 110          # Words per minute
ESPEAK_PITCH = 12           # 0-99, lower = deeper
ESPEAK_VOLUME = 0.7         # Final volume
ESPEAK_EFFECTS = ["pitch -700", "bass +10"]  # Sox effects chain

# STT Optimizations for faster processing
WHISPER_MODEL = "base"            # Good balance of speed/accuracy
WHISPER_COMPUTE_TYPE = "int8"     # Quantized for speed on Pi
WHISPER_BEAM_SIZE = 1             # Fastest decoding
WHISPER_NUM_WORKERS = 2           # Use Pi cores efficiently
WHISPER_LANGUAGE = "en"           # Skip auto-detection
WHISPER_VAD_FILTER = True         # Use built-in VAD

# Audio preprocessing optimizations
AUDIO_NOISE_REDUCTION = True      # Clean up audio input
AUDIO_GAIN_NORMALIZATION = True   # Normalize volume levels
AUDIO_AUTO_GAIN = True            # Automatic gain control for USB mic
