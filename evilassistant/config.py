# ~/evilassistant/evilassistant/config.py
RATE = 44100
CHUNK_DURATION = 3
CHANNELS = 1
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1.5

WAKE_PHRASES = ["evil assistant", "i summon you", "dark one", "cthulhu", "amanda"]  # List of wake-up phrases
FOLLOW_UP_PROMPT = "What else do you seek, mortal?"
PIPER_MODEL = "en_US-lessac-low.onnx"
PIPER_CONFIG = "en_US-lessac-low.onnx.json"
SOX_EFFECTS = "tempo 0.85 pitch -600 gain -4 overdrive 6"
# SOX_EFFECTS = "tempo 0.7 pitch -500 reverb 60 overdrive 10 gain -5 tremolo 2 30"

