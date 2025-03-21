import sounddevice as sd
import numpy as np
import wave
import os
import pygame.mixer
import time
import whisper
from openai import OpenAI
from piper import PiperVoice
from .config import *

def play_audio(audio_file):
    pygame.mixer.init()
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

    return np.concatenate(audio_chunks, axis=0)

def speak_text(text, output_file, voice):
    temp_file = "temp.wav"
    with wave.open(temp_file, "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(RATE)
        voice.synthesize(text, wav_file)
    os.system(f"sox {temp_file} {output_file} {SOX_EFFECTS}")
    play_audio(output_file)
    os.remove(temp_file)

def run_assistant():
    model = whisper.load_model("tiny")
    voice = PiperVoice.load(PIPER_MODEL, config_path=PIPER_CONFIG)

    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("Error: XAI_API_KEY environment variable not set")
        return
    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

    print(f"Listening for wake-up phrase: '{WAKE_PHRASE}'...")

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
            welcome_file = "welcome.wav"
            speak_text(WELCOME_PHRASE, welcome_file, voice)
            os.remove(welcome_file)
            
            full_audio = record_until_silence()
            with wave.open("full_query.wav", "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(RATE)
                wf.writeframes(full_audio.tobytes())
            result = model.transcribe("full_query.wav", language="en")
            full_transcription = result["text"].strip().lower()
            print(f"Question: {full_transcription}")
            
            response = client.chat.completions.create(
                model="grok-2-latest",
                messages=[
                    {"role": "system", "content": "You are Evil Assistant, a chatbot with a deep, demonic tone."},
                    {"role": "user", "content": f"Respond to this in English: {full_transcription}"},
                ],
                max_tokens=100
            )
            ai_response = response.choices[0].message.content
            print(f"Evil Assistant says: {ai_response}")
            output_file = "evil_output.wav"
            speak_text(ai_response, output_file, voice)
            os.remove(output_file)
            os.remove("full_query.wav")
