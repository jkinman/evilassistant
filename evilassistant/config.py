# ~/evilassistant/evilassistant/config.py
RATE = 44100
CHUNK_DURATION = 3
CHANNELS = 1
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1.5

WAKE_PHRASE = "evil assistant"
PIPER_MODEL = "en_US-lessac-low.onnx"
PIPER_CONFIG = "en_US-lessac-low.onnx.json"
SOX_EFFECTS = "tempo 0.7 pitch -800 reverb 60 overdrive 20 tremolo 2 30"
