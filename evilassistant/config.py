# ~/evilassistant/evilassistant/config.py
RATE = 16000  # Lower sample rate for faster processing
CHUNK_DURATION = 2  # Optimal 2-second chunks for wake detection balance
CHANNELS = 1
SILENCE_THRESHOLD = 800
SILENCE_DURATION = 0.8  # Much faster response - 0.8 seconds instead of 1.5

WAKE_PHRASES = ["evil assistant", "evil assistance", "i summon you", "dark one", "dark 1", "cthulhu", "summon"]
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

# TTS provider selection: "piper" (offline), "elevenlabs" (cloud), or "system" (fallback)
TTS_PROVIDER = "elevenlabs"  # Use ElevenLabs for best quality
ELEVENLABS_MODEL_ID = "eleven_multilingual_v2"  # Latest model
ELEVENLABS_VOICE_ID = "cPoqAvGWCPfCfyPMwe4z"  # Custom demonic voice created in ElevenLabs dashboard
