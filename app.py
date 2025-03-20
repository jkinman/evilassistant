import sounddevice as sd
import numpy as np
import wave
import os
import pygame.mixer
import time
import whisper
from openai import OpenAI
from piper import PiperVoice

# Audio setup
RATE = 44100
CHUNK_DURATION = 3  # 3-second chunks for wake-up
CHANNELS = 1
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1.5

# Load Whisper model
model = whisper.load_model("tiny")

# Load Piper TTS model (adjust path if needed)
voice = PiperVoice.load("en_US-lessac-low.onnx", config_path="en_US-lessac-low.onnx.json")

# xAI Grok API setup using OpenAI client
API_KEY = os.getenv("XAI_API_KEY")
if not API_KEY:
    print("Error: XAI_API_KEY environment variable not set")
    exit(1)
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.x.ai/v1",
)

# Wake-up phrase
WAKE_PHRASE = "evil assistant"
WELCOME_PHRASE = "I am Evil Assistant, what dark query do you dare to ask?"

# Initialize pygame mixer for playback
pygame.mixer.init()

def play_audio(audio_file):
    sound = pygame.mixer.Sound(audio_file)
    sound.play()
    duration = sound.get_length()
    time.sleep(duration)

def record_until_silence():
    print("Ask your question... (stops on silence)")
    audio_chunks = []
    silence_counter = 0
    chunk_size = int(RATE * CHUNK_DURATION)

    while True:
        chunk = sd.rec(chunk_size, samplerate=RATE, channels=CHANNELS, dtype='int16')
        sd.wait()
        audio_chunks.append(chunk)
        rms = np.sqrt(np.mean(chunk.astype(float) ** 2))
        if rms < SILENCE_THRESHOLD:
            silence_counter += CHUNK_DURATION
            if silence_counter >= SILENCE_DURATION:
                break
        else:
            silence_counter = 0

    full_audio = np.concatenate(audio_chunks, axis=0)
    return full_audio

def speak_text(text, output_file):
    temp_file = "temp.wav"
    with wave.open(temp_file, "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(RATE)
        voice.synthesize(text, wav_file)
    os.system(f"sox {temp_file} {output_file} tempo 0.8 pitch -300 reverb 50 overdrive 10")
    play_audio(output_file)
    os.remove(temp_file)

print(f"Listening for wake-up phrase: '{WAKE_PHRASE}'...")

try:
    while True:
        print("Listening...")
        audio_data = sd.rec(int(CHUNK_DURATION * RATE), samplerate=RATE, channels=CHANNELS, dtype='int16')
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
            # Speak welcome phrase
            welcome_file = "welcome.wav"
            speak_text(WELCOME_PHRASE, welcome_file)
            os.remove(welcome_file)
            
            # Record user's question
            full_audio = record_until_silence()
            with wave.open("full_query.wav", "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(RATE)
                wf.writeframes(full_audio.tobytes())
            result = model.transcribe("full_query.wav", language="en")
            full_transcription = result["text"].strip().lower()
            print(f"Question: {full_transcription}")
            
            # Get and speak Grok's answer
            response = client.chat.completions.create(
                model="grok-2-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Evil Assistant, a chatbot with a deep, demonic tone."
                    },
                    {
                        "role": "user",
                        "content": f"Respond to this in English: {full_transcription}"
                    },
                ],
                max_tokens=100
            )
            ai_response = response.choices[0].message.content
            print(f"Evil Assistant says: {ai_response}")
            output_file = "evil_output.wav"
            speak_text(ai_response, output_file)
            os.remove(output_file)
            os.remove("full_query.wav")

except KeyboardInterrupt:
    print("Stopped")
