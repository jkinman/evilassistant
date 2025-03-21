# Evil Assistant

A demonic voice assistant powered by xAI's Grok API, using Piper TTS and Sox for a terrifying voice.

## Installation

1. Install system dependencies:
   ```bash
   sudo apt install sox# evilassistant
markdown

# Evil Assistant

A demonic voice assistant powered by xAI's Grok API, using Piper TTS and Sox for a terrifying voice.

## Installation

1. Install system dependencies:
   ```bash
   sudo apt install sox

Install the package:
bash

pip install .

Set the API key:
bash

export XAI_API_KEY="your_xai_api_key_here"

Run:
bash

evilassistant

Requirements
Piper voice model: Place en_US-lessac-low.onnx and en_US-lessac-low.onnx.json in the directory where you run the assistant.


#### 4. `evilassistant/config.py` (Configuration)
Separate constants for easy tweaking.

```python
# ~/cthulhu/evilassistant/evilassistant/config.py
RATE = 44100
CHUNK_DURATION = 3
CHANNELS = 1
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1.5

WAKE_PHRASE = "evil assistant"
WELCOME_PHRASE = "I am Evil Assistant, what dark query do you dare to ask?"

PIPER_MODEL = "en_US-lessac-low.onnx"
PIPER_CONFIG = "en_US-lessac-low.onnx.json"
SOX_EFFECTS = "tempo 0.8 pitch -300 reverb 50 overdrive 10"
