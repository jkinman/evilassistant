# ~/evilassistant/evilassistant/config.py
RATE = 44100
CHUNK_DURATION = 3
CHANNELS = 1
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1.5

WAKE_PHRASES = ["evil assistant", "i summon you", "dark one", "cthulhu", "durans dick"]
STOP_PHRASES = ["shut up", "be silent", "stop", "unsummon"]
FOLLOW_UP_PROMPT = "What else do you seek, mortal?"
PIPER_MODEL = "en_US-lessac-low.onnx"
PIPER_CONFIG = "en_US-lessac-low.onnx.json"
SOX_EFFECTS = "tempo 0.85 pitch -600 gain -4 overdrive 6"
