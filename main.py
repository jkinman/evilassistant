import sounddevice as sd
import numpy as np
import wave
import os
import pygame.mixer
import time
import whisper
from openai import OpenAI

# Audio setup
RATE = 44100
DURATION = 2
CHANNELS = 1

# Load Whisper model
model = whisper.load_model("tiny")

# xAI Grok API setup using OpenAI client
API_KEY = os.getenv("XAI_API_KEY")
if not API_KEY:
    print("Error: XAI_API_KEY environment variable not set")
    exit(1)
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.x.ai/v1",  # Custom base URL for xAI
)

# Wake-up phrase
WAKE_PHRASE = "evil assistant"

# Initialize pygame mixer for playback
pygame.mixer.init()

def play_audio(audio_file):
    sound = pygame.mixer.Sound(audio_file)
    sound.play()
    duration = sound.get_length()
    time.sleep(duration)

print(f"Listening for wake-up phrase: '{WAKE_PHRASE}'...")

try:
    while True:
        print("Listening...")
        audio_data = sd.rec(int(DURATION * RATE), samplerate=RATE, channels=CHANNELS, dtype='int16')
        sd.wait()
        with wave.open("temp.wav", "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(RATE)
            wf.writeframes(audio_data.tobytes())
        result = model.transcribe("temp.wav", language="en")
        transcription = result["text"].strip().lower()
        print(f"Heard: {transcription}")
        if WAKE_PHRASE in transcription:
            print(f"Wake-up phrase '{WAKE_PHRASE}' detected!")
            # Grok API request via OpenAI client
            response = client.chat.completions.create(
                model="grok-2-latest",  # From Grok docs example
                messages=[
                    {
                        "role": "system",
                        "content": "You are Evil Assistant, a chatbot with a deep, demonic tone."
                    },
                    {
                        "role": "user",
                        "content": f"Respond to this in English: {transcription}"
                    },
                ],
                max_tokens=100
            )
            # Extract response from Grok
            ai_response = response.choices[0].message.content
            print(f"Evil Assistant says: {ai_response}")
            output_file = "evil_output.wav"
            os.system(f'espeak -v en-us -p 10 -s 100 -w {output_file} "{ai_response}"')
            play_audio(output_file)
            os.remove(output_file)

except KeyboardInterrupt:
    print("Stopped")
