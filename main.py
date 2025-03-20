import pyaudio
import wave
import subprocess
import requests
import os
import pygame.mixer

# Audio setup
RATE = 44100  # Matches your working arecord command
CHUNK = 1024
audio = pyaudio.PyAudio()
try:
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
except Exception as e:
    print(f"Error opening audio stream: {e}")
    audio.terminate()
    exit(1)

# xAI API setup
API_KEY = os.getenv("XAI_API_KEY")  # Fetch from environment variable
if not API_KEY:
    print("Error: XAI_API_KEY environment variable not set")
    audio.terminate()
    exit(1)
URL = "https://api.xai.com/v1/grok"
headers = {"Authorization": f"Bearer {API_KEY}"}

# Wake-up phrase
WAKE_PHRASE = "evil assistant"

# Initialize pygame mixer for playback
pygame.mixer.init()

def play_audio(audio_file):
    """Play WAV file without LED dimming."""
    sound = pygame.mixer.Sound(audio_file)
    sound.play()
    # Wait for playback to finish (approximate duration)
    duration = sound.get_length()
    time.sleep(duration)

print(f"Listening for wake-up phrase: '{WAKE_PHRASE}'...")

try:
    while True:
        print("Listening...")

        frames = []
        for _ in range(int(RATE / CHUNK * 2)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

        wf = wave.open("temp.wav", "wb")
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
        wf.close()

        result = subprocess.run(["../whisper.cpp/build/bin/whisper-cli", "-m", "../../whisper.cpp/models/ggml-tiny.en.bin", "-f", "temp.wav"], capture_output=True, text=True)
        transcription = result.stdout.strip().lower()
        print(f"Heard: {transcription}")

        if WAKE_PHRASE in transcription:
            print(f"Wake-up phrase '{WAKE_PHRASE}' detected!")
            data = {"prompt": f"Respond to this in a deep, demonic tone: {transcription}"}
            response = requests.post(URL, headers=headers, json=data)
            ai_response = response.json()["response"]
            print(f"Demon Grok says: {ai_response}")

            output_file = "demon_output.wav"
            os.system(f'espeak -v en-us -p 10 -s 100 -w {output_file} "{ai_response}"')
            play_audio(output_file)
            os.remove(output_file)

except KeyboardInterrupt:
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print("Stopped")
