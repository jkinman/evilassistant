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

# Prompt settings
SYSTEM_PROMPT = "You are Evil Assistant, a malevolent entity with a deep, demonic tone, sneering at human folly. Answer their questions directly with dark, disdainful humor, mocking their triviality while serving your dread purpose."
GREETING_INSTRUCTION = "Provide a short, unique, sinister greeting in English to welcome a mortal who has summoned me. Make it dark and varied each time."
