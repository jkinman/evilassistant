# ~/evilassistant/evilassistant/assistant.py
import sounddevice as sd
import numpy as np
import wave
import os
import pygame.mixer
import time
from faster_whisper import WhisperModel
from openai import OpenAI
from piper import PiperVoice
from .config import *

def play_audio(audio_file, use_pygame=True):
    if use_pygame:
        pygame.mixer.init()
        sound = pygame.mixer.Sound(audio_file)
        channel = sound.play()
        while channel.get_busy():  # Wait until playback completes
            pygame.time.wait(100)
    else:
        # Fallback to aplay for debugging
        print(f"Playing {audio_file} with aplay...")
        os.system(f"aplay {audio_file}")

def get_wav_duration(file_path):
    with wave.open(file_path, "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)

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

def speak_text(text, output_file, voice, debug=False):
    temp_file = "temp.wav"
    with wave.open(temp_file, "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(RATE)
        voice.synthesize(text, wav_file)
    
    if debug:
        temp_duration = get_wav_duration(temp_file)
        print(f"Piper output duration: {temp_duration:.2f} seconds")
        print("Testing Piper output with aplay...")
        os.system(f"aplay {temp_file}")
    
    # Use -t wav to ensure Sox preserves full length
    os.system(f"sox {temp_file} -t wav {output_file} {SOX_EFFECTS}")
    
    if debug:
        out_duration = get_wav_duration(output_file)
        print(f"Sox output duration: {out_duration:.2f} seconds")
        print("Testing Sox output with aplay...")
        os.system(f"aplay {output_file}")
    
    play_audio(output_file, use_pygame=True)
    os.remove(temp_file)

def get_random_greeting(client):
    response = client.chat.completions.create(
        model="grok-2-latest",
        messages=[
            {"role": "system", "content": "You are Evil Assistant, a chatbot with a deep, demonic tone."},
            {"role": "user", "content": "Provide a short, unique, sinister greeting in English to welcome a mortal who has summoned me. Make it dark and varied each time."},
        ],
        max_tokens=50
    )
    return response.choices[0].message.content

def run_assistant(debug=False):
    model = WhisperModel("tiny", device="cpu", compute_type="int8")

    piper_model = os.path.join(os.getcwd(), "en_US-lessac-low.onnx")
    piper_config = os.path.join(os.getcwd(), "en_US-lessac-low.onnx.json")
    
    if not os.path.exists(piper_model) or not os.path.exists(piper_config):
        print(f"Error: Piper model files not found at {piper_model} or {piper_config}")
        print("Please download en_US-lessac-low.onnx and en_US-lessac-low.onnx.json to your working directory.")
        return
    
    voice = PiperVoice.load(piper_model, config_path=piper_config)

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
        segments, _ = model.transcribe("temp.wav", beam_size=5, language="en")
        transcription = " ".join([segment.text for segment in segments]).strip().lower()
        print(f"Heard: {transcription}")
        
        if WAKE_PHRASE in transcription:
            print(f"Wake-up phrase '{WAKE_PHRASE}' detected!")
            welcome_message = get_random_greeting(client)
            print(f"Welcome message: {welcome_message}")
            welcome_file = "welcome.wav"
            speak_text(welcome_message, welcome_file, voice, debug=debug)
            os.remove(welcome_file)
            
            full_audio = record_until_silence()
            with wave.open("full_query.wav", "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(RATE)
                wf.writeframes(full_audio.tobytes())
            segments, _ = model.transcribe("full_query.wav", beam_size=5, language="en")
            full_transcription = " ".join([segment.text for segment in segments]).strip().lower()
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
            speak_text(ai_response, output_file, voice, debug=debug)
            os.remove(output_file)
            os.remove("full_query.wav")
