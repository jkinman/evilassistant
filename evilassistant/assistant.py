# ~/evilassistant/evilassistant/assistant.py
import sounddevice as sd
import numpy as np
import wave
import os
import pygame.mixer
import time
import threading
from faster_whisper import WhisperModel
from openai import OpenAI
from piper import PiperVoice
from .config import *
from .simple_smart_home import handle_smart_home_command

try:
    import pvporcupine
    _PORCUPINE_AVAILABLE = True
except Exception:
    _PORCUPINE_AVAILABLE = False
import requests
from dotenv import load_dotenv

try:
    import RPi.GPIO as GPIO  # type: ignore
    _GPIO_AVAILABLE = True
except Exception:
    _GPIO_AVAILABLE = False

_pwm = None
_stop_led_thread = None

def _init_pwm():
    global _pwm
    if not GPIO_ENABLED or not _GPIO_AVAILABLE or _pwm is not None:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    _pwm = GPIO.PWM(GPIO_PIN, PWM_FREQUENCY_HZ)
    _pwm.start(0)

def _cleanup_pwm():
    global _pwm
    if _pwm is not None:
        try:
            _pwm.ChangeDutyCycle(0)
            _pwm.stop()
        except Exception:
            pass
        _pwm = None
    if _GPIO_AVAILABLE:
        try:
            GPIO.cleanup()
        except Exception:
            pass

def _led_envelope_follow_thread(audio_file, stop_event):
    if _pwm is None:
        return
    try:
        with wave.open(audio_file, "rb") as wf:
            rate = wf.getframerate()
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            frames_per_chunk = max(1, int(rate * 0.02))  # ~20ms
            max_int = float(2 ** (8 * sampwidth - 1))
            alpha = max(0.0, min(1.0, AMPLITUDE_SMOOTHING))
            prev_level = 0.0
            while not stop_event.is_set():
                frames = wf.readframes(frames_per_chunk)
                if not frames:
                    break
                data = np.frombuffer(frames, dtype=np.int16)
                if channels > 1:
                    data = data.reshape(-1, channels).mean(axis=1)
                rms = float(np.sqrt(np.mean(np.square(data.astype(np.float32))))) / max_int
                level = alpha * prev_level + (1.0 - alpha) * rms
                prev_level = level
                duty = BRIGHTNESS_MIN + (BRIGHTNESS_MAX - BRIGHTNESS_MIN) * max(0.0, min(1.0, level * LED_GAIN))
                try:
                    _pwm.ChangeDutyCycle(duty)
                except Exception:
                    pass
                time.sleep(frames_per_chunk / float(rate))
    except Exception:
        # Fail silently to avoid breaking audio playback
        pass
    finally:
        try:
            _pwm.ChangeDutyCycle(0)
        except Exception:
            pass

def play_audio(audio_file, use_pygame=True):
    if use_pygame:
        pygame.mixer.init()
        sound = pygame.mixer.Sound(audio_file)
        sound.set_volume(1.0)
        channel = sound.play()

        led_thread = None
        stop_event = threading.Event()
        if GPIO_ENABLED and _GPIO_AVAILABLE:
            _init_pwm()
            led_thread = threading.Thread(target=_led_envelope_follow_thread, args=(audio_file, stop_event))
            led_thread.daemon = True
            led_thread.start()

        while channel.get_busy():
            pygame.time.wait(50)

        if led_thread is not None:
            stop_event.set()
            led_thread.join(timeout=0.5)
    else:
        os.system(f"aplay {audio_file}")

def _porcupine_listen_for_wake():
    if not _PORCUPINE_AVAILABLE:
        return False
    access_key = os.getenv("PORCUPINE_ACCESS_KEY")
    if not access_key:
        print("PORCUPINE_ACCESS_KEY not set; falling back to STT wake.")
        return False
    porcupine = None
    stream = None
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=PORCUPINE_KEYWORDS if PORCUPINE_KEYWORDS else None,
            keyword_paths=PORCUPINE_KEYWORD_PATHS if PORCUPINE_KEYWORD_PATHS else None,
        )
        stream = sd.InputStream(
            samplerate=porcupine.sample_rate,
            blocksize=porcupine.frame_length,
            dtype='int16',
            channels=1,
        )
        stream.start()
        print("Porcupine listening for wake...")
        hits = 0
        while True:
            frame, overflowed = stream.read(porcupine.frame_length)
            if overflowed:
                continue
            pcm = frame.reshape(-1)
            idx = porcupine.process(pcm)
            if idx >= 0:
                hits += 1
                if hits >= WAKE_CONFIRM_WINDOWS:
                    return True
            else:
                hits = 0
    except KeyboardInterrupt:
        return False
    except Exception as e:
        print(f"Porcupine error: {e}; falling back to STT wake.")
        return False
    finally:
        try:
            if stream is not None:
                stream.stop(); stream.close()
        except Exception:
            pass
        try:
            if porcupine is not None:
                porcupine.delete()
        except Exception:
            pass

def _synthesize_with_elevenlabs(text, output_file):
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key or not ELEVENLABS_VOICE_ID:
        print("ELEVENLABS_API_KEY or ELEVENLABS_VOICE_ID missing")
        return False
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": api_key,
        "accept": "audio/mpeg",  # Use MP3 for faster processing
        "content-type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": ELEVENLABS_MODEL_ID,
        "voice_settings": {
            "stability": 0.3,      # Higher stability for cleaner audio
            "similarity_boost": 0.2,  # Maintain voice character while reducing distortion
            "style": 0.6,          # Moderate style for demonic effect without clipping
            "use_speaker_boost": False,  # Keep disabled to prevent clipping
            "speed": 1.2          # Increase speech speed for more dynamic delivery
        }
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        # Save MP3 audio and convert to WAV for pygame compatibility
        temp_mp3 = output_file.replace('.wav', '_temp.mp3')
        with open(temp_mp3, "wb") as f:
            f.write(r.content)
        
        # Convert MP3 to WAV with aggressive anti-clipping processing
        try:
            # Fix ALL clipping with maximum conservative volume reduction
            sox_effects = f"sox {temp_mp3} {output_file} vol 0.15"
            os.system(sox_effects)
            # Clean up temp file
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
        except Exception as e:
            print(f"Audio conversion failed: {e}")
            # If conversion fails, try ffmpeg as fallback
            try:
                os.system(f"ffmpeg -i {temp_mp3} {output_file} -y")
                if os.path.exists(temp_mp3):
                    os.remove(temp_mp3)
            except:
                # Last resort: rename mp3 to wav (might work with pygame)
                os.rename(temp_mp3, output_file)
        
        return True
    except Exception as e:
        print(f"ElevenLabs TTS failed: {e}")
        return False

def record_audio(duration):
    print(f"Waiting for your next question ({duration} seconds)...")
    audio_data = sd.rec(int(duration * RATE), samplerate=RATE, channels=CHANNELS, dtype='int16')
    sd.wait()
    return audio_data

def record_until_silence():
    print("Ask your question... (stops on silence)")
    audio_chunks = []
    silence_counter = 0.0
    chunk_size = int(RATE * CHUNK_DURATION)

    while True:
        chunk = sd.rec(chunk_size, samplerate=RATE, channels=CHANNELS, dtype='int16')
        sd.wait()
        audio_chunks.append(chunk)
        rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
        if rms < SILENCE_THRESHOLD:
            silence_counter += float(CHUNK_DURATION)
            if silence_counter >= SILENCE_DURATION:
                break
        else:
            silence_counter = 0.0

    return np.concatenate(audio_chunks, axis=0)

def speak_text(text, output_file, voice):
    if TTS_PROVIDER == "elevenlabs":
        print("🔥 Using ElevenLabs demon voice...")
        ok = _synthesize_with_elevenlabs(text, output_file)
        if ok:
            play_audio(output_file)
            return
        else:
            print("⚠️ ElevenLabs failed, falling back to system voice...")
    
    if TTS_PROVIDER == "system" or True:  # Always fallback to system if other methods fail
        # Use macOS say command with demon voice
        print("🎵 Using system voice...")
        # Fred voice at slower rate for more sinister effect
        os.system(f'say -v "Fred" -r 180 "{text}"')
        return
    
    # Piper path (if needed)
    if voice is not None:
        print("📢 Using Piper TTS...")
        temp_file = "temp.wav"
        with wave.open(temp_file, "wb") as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(2)
            voice_sample_rate = getattr(voice, "sample_rate", RATE)
            wav_file.setframerate(voice_sample_rate)
            voice.synthesize(text, wav_file)
        os.system(f"sox {temp_file} {output_file} {SOX_EFFECTS}")
        play_audio(output_file)
        os.remove(temp_file)
    else:
        # Emergency fallback: use macOS say command
        print("No TTS available, using system voice...")
        # Make the voice deeper and more sinister
        os.system(f'say -v "Fred" -r 180 "{text}"')

def get_random_greeting(client):
    response = client.chat.completions.create(
        model="grok-2-latest",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": GREETING_INSTRUCTION},
        ],
        max_tokens=50
    )
    return response.choices[0].message.content

def run_assistant():
    # Load .env if present
    try:
        load_dotenv()
    except Exception:
        pass
    model = WhisperModel("tiny", device="cpu", compute_type="int8", num_workers=1)

    piper_model = os.path.join(os.getcwd(), PIPER_MODEL)
    piper_config = os.path.join(os.getcwd(), PIPER_CONFIG)
    voice = None
    if TTS_PROVIDER == "piper":
        if not os.path.exists(piper_model) or not os.path.exists(piper_config):
            print(f"Error: Piper model files not found at {piper_model} or {piper_config}")
            print(f"Please download {PIPER_MODEL} and {PIPER_CONFIG} to your working directory, or set TTS_PROVIDER='elevenlabs'.")
            return
        voice = PiperVoice.load(piper_model, config_path=piper_config)
    else:
        # Optional: try to load Piper for fallback if available
        if os.path.exists(piper_model) and os.path.exists(piper_config):
            try:
                voice = PiperVoice.load(piper_model, config_path=piper_config)
                print("Piper model loaded for fallback.")
            except Exception:
                print("Piper model present but failed to load; continuing with cloud TTS only.")
        else:
            print("Piper model not found; running with cloud TTS only.")

    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("Error: XAI_API_KEY environment variable not set")
        return
    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

    print(f"Listening for wake-up phrases: {', '.join(WAKE_PHRASES)}..." if not USE_PORCUPINE else "Wake: Porcupine enabled")
    wake_hits = 0

    try:
        while True:
            woke = False
            if USE_PORCUPINE and _PORCUPINE_AVAILABLE:
                woke = _porcupine_listen_for_wake()
            if not woke:
                print("Listening...")
                audio_data = sd.rec(int(CHUNK_DURATION * RATE), samplerate=RATE, channels=CHANNELS, dtype='int16')
                sd.wait()
                with wave.open("temp.wav", "wb") as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)
                    wf.setframerate(RATE)
                    wf.writeframes(audio_data.tobytes())
                segments, _ = model.transcribe("temp.wav", beam_size=1, language="en", vad_filter=True)
                transcription = " ".join([segment.text for segment in segments]).strip().lower()
                print(f"Heard: {transcription}")

                if any(phrase in transcription for phrase in WAKE_PHRASES):
                    wake_hits += 1
                else:
                    wake_hits = 0
                woke = wake_hits >= WAKE_CONFIRM_WINDOWS

            if not woke:
                continue

            print("Wake detected!")

            while True:  # Inner loop for questions
                full_audio = record_until_silence()
                with wave.open("full_query.wav", "wb") as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)
                    wf.setframerate(RATE)
                    wf.writeframes(full_audio.tobytes())
                segments, _ = model.transcribe("full_query.wav", beam_size=5, language="en", vad_filter=True)
                full_transcription = " ".join([segment.text for segment in segments]).strip().lower()
                print(f"Question: {full_transcription}")
                os.remove("full_query.wav")

                if any(phrase in full_transcription for phrase in STOP_PHRASES):
                    print(f"Stop phrase detected: '{full_transcription}', returning to wake-up mode...")
                    break  # Exit to wake-up mode

                if not full_transcription:  # Skip if no question
                    print("No question detected, prompting again...")
                else:
                    # Check for smart home commands first
                    smart_home_response = handle_smart_home_command(full_transcription)
                    if smart_home_response:
                        print(f"Evil Assistant (Smart Home): {smart_home_response}")
                        output_file = "evil_output.wav"
                        speak_text(smart_home_response, output_file, voice)
                        if os.path.exists(output_file):
                            os.remove(output_file)
                    else:
                        # Regular LLM processing for non-smart-home commands
                        try:
                            response = client.chat.completions.create(
                                model="grok-2-latest",
                                messages=[
                                    {"role": "system", "content": SYSTEM_PROMPT},
                                    {"role": "user", "content": f"Respond to this in English: {full_transcription}"},
                                ],
                                max_tokens=200
                            )
                            ai_response = response.choices[0].message.content
                            print(f"Evil Assistant says: {ai_response}")
                            output_file = "evil_output.wav"
                            speak_text(ai_response, output_file, voice)
                            if os.path.exists(output_file):
                                os.remove(output_file)
                        except Exception as e:
                            print(f"LLM API error: {e}")
                            ai_response = "The dark forces prevent me from answering that question, mortal. Try asking me to control your lights instead!"
                            print(f"Evil Assistant says: {ai_response}")
                            output_file = "evil_output.wav"
                            speak_text(ai_response, output_file, voice)
                            if os.path.exists(output_file):
                                os.remove(output_file)

                # Prompt for another question
                time.sleep(0.5)  # Brief pause before follow-up prompt
                print("📢 FOLLOW-UP PROMPT:", FOLLOW_UP_PROMPT)
                follow_up_file = "follow_up.wav"
                speak_text(FOLLOW_UP_PROMPT, follow_up_file, voice)
                if os.path.exists(follow_up_file):
                    os.remove(follow_up_file)

                # Wait 3 seconds for a follow-up question
                follow_up_audio = record_audio(3)
                with wave.open("follow_up_query.wav", "wb") as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)
                    wf.setframerate(RATE)
                    wf.writeframes(follow_up_audio.tobytes())
                segments, _ = model.transcribe("follow_up_query.wav", beam_size=3, language="en", vad_filter=True)
                follow_up_transcription = " ".join([segment.text for segment in segments]).strip().lower()
                print(f"Follow-up: {follow_up_transcription}")
                os.remove("follow_up_query.wav")

                if any(phrase in follow_up_transcription for phrase in STOP_PHRASES):
                    print(f"Stop phrase detected: '{follow_up_transcription}', returning to wake-up mode...")
                    break  # Exit to wake-up mode

                if follow_up_transcription:  # If there's a follow-up question
                    print("Processing follow-up question...")
                    full_transcription = follow_up_transcription  # Use the follow-up directly
                    
                    # Check for smart home commands in follow-up too
                    smart_home_response = handle_smart_home_command(full_transcription)
                    if smart_home_response:
                        print(f"Evil Assistant (Smart Home): {smart_home_response}")
                        output_file = "evil_output.wav"
                        speak_text(smart_home_response, output_file, voice)
                        if os.path.exists(output_file):
                            os.remove(output_file)
                    else:
                        # Regular LLM processing
                        try:
                            response = client.chat.completions.create(
                                model="grok-2-latest",
                                messages=[
                                    {"role": "system", "content": SYSTEM_PROMPT},
                                    {"role": "user", "content": f"Respond to this in English: {full_transcription}"},
                                ],
                                max_tokens=200
                            )
                            ai_response = response.choices[0].message.content
                            print(f"Evil Assistant says: {ai_response}")
                            output_file = "evil_output.wav"
                            speak_text(ai_response, output_file, voice)
                            if os.path.exists(output_file):
                                os.remove(output_file)
                        except Exception as e:
                            print(f"LLM API error: {e}")
                            ai_response = "The dark forces prevent me from answering that question, mortal. Try asking me to control your lights instead!"
                            print(f"Evil Assistant says: {ai_response}")
                            output_file = "evil_output.wav"
                            speak_text(ai_response, output_file, voice)
                            if os.path.exists(output_file):
                                os.remove(output_file)
                else:
                    print("No follow-up detected, returning to wake-up mode...")
                    break  # Exit to wake-up mode if silent

            print(f"Listening for wake-up phrases: {', '.join(WAKE_PHRASES)}...")
    finally:
        _cleanup_pwm()
