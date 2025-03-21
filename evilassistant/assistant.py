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
        sound.set_volume(1.0)
        channel = sound.play()
        while channel.get_busy():
            pygame.time.wait(100)
    else:
        os.system(f"aplay {audio_file}")

def record_audio(duration):
    print(f"Waiting for your next question ({duration} seconds)...")
    audio_data = sd.rec(int(duration * RATE), samplerate=RATE, channels=CHANNELS, dtype='int16')
    sd.wait()
    return audio_data

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

    print(f"Listening for wake-up phrases: {', '.join(WAKE_PHRASES)}...")

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
        
        if any(phrase in transcription for phrase in WAKE_PHRASES):
            detected_phrase = next(phrase for phrase in WAKE_PHRASES if phrase in transcription)
            print(f"Wake-up phrase '{detected_phrase}' detected!")
            
            while True:  # Inner loop for questions
                full_audio = record_until_silence()
                with wave.open("full_query.wav", "wb") as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)
                    wf.setframerate(RATE)
                    wf.writeframes(full_audio.tobytes())
                segments, _ = model.transcribe("full_query.wav", beam_size=5, language="en")
                full_transcription = " ".join([segment.text for segment in segments]).strip().lower()
                print(f"Question: {full_transcription}")
                os.remove("full_query.wav")
                
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

                # Prompt for another question
                follow_up_file = "follow_up.wav"
                speak_text(FOLLOW_UP_PROMPT, follow_up_file, voice)
                os.remove(follow_up_file)

                # Wait 3 seconds for a follow-up question
                follow_up_audio = record_audio(3)
                with wave.open("follow_up_query.wav", "wb") as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)
                    wf.setframerate(RATE)
                    wf.writeframes(follow_up_audio.tobytes())
                segments, _ = model.transcribe("follow_up_query.wav", beam_size=5, language="en")
                follow_up_transcription = " ".join([segment.text for segment in segments]).strip().lower()
                print(f"Follow-up: {follow_up_transcription}")
                os.remove("follow_up_query.wav")

                if follow_up_transcription:  # If there's a follow-up question
                    print("Processing follow-up question...")
                    with wave.open("full_query.wav", "wb") as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(2)
                        wf.setframerate(RATE)
                        wf.writeframes(follow_up_audio.tobytes())
                    continue  # Loop back with the follow-up as the new question
                else:
                    print("No follow-up detected, returning to wake-up mode...")
                    break  # Exit to wake-up mode if silent

            print(f"Listening for wake-up phrases: {', '.join(WAKE_PHRASES)}...")
