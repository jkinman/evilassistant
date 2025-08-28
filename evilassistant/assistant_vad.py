#!/usr/bin/env python3
"""
Evil Assistant with VAD-based speech chunking for real-time responsiveness.
"""

import os
import wave
import tempfile
import pygame
import requests
from faster_whisper import WhisperModel
from .config import *
from .simple_vad import SimpleVADRecorder
from .smart_home import SmartHomeController
import numpy as np

# Initialize VAD audio processor
vad_processor = None

def initialize_vad():
    """Initialize the VAD audio processor."""
    global vad_processor
    if vad_processor is None:
        vad_processor = SimpleVADRecorder(
            sample_rate=RATE,
            chunk_duration=0.1,        # 100ms chunks for smooth recording
            speech_timeout=0.8,        # Stop after 0.8s of silence
            min_speech_duration=0.5,   # Minimum 0.5s of speech
            energy_threshold=SILENCE_THRESHOLD  # Use config threshold
        )
    return vad_processor

def _synthesize_with_elevenlabs(text, output_file):
    """Generate speech using ElevenLabs with anti-clipping."""
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
        
        # Convert MP3 to WAV with maximum anti-clipping processing
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

def play_audio_file(file_path):
    """Play audio file using pygame."""
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
    except Exception as e:
        print(f"Error playing audio: {e}")

def transcribe_audio(audio_data, model, file_suffix="temp"):
    """Transcribe audio data using Whisper."""
    with tempfile.NamedTemporaryFile(suffix=f'_{file_suffix}.wav', delete=False) as tmp_file:
        with wave.open(tmp_file.name, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(RATE)
            # Convert to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wf.writeframes(audio_int16.tobytes())
        
        try:
            segments, _ = model.transcribe(tmp_file.name, beam_size=3, 
                                         language="en", vad_filter=True)
            transcription = " ".join([segment.text for segment in segments]).strip().lower()
            return transcription
        finally:
            if os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)

def process_smart_home_command(question: str, smart_home: SmartHomeController) -> Optional[str]:
    """Process smart home commands and return a response if handled."""
    question_lower = question.lower()
    
    # Light control commands
    if any(word in question_lower for word in ['light', 'lights', 'lamp', 'brightness']):
        try:
            if 'off' in question_lower or 'turn off' in question_lower:
                result = smart_home.control_philips_hue("living_room", on=False)
                if result:
                    return "The lights have been extinguished, mortal. Darkness consumes you."
                else:
                    return "The light spirits resist my command, mortal."
                    
            elif 'on' in question_lower or 'turn on' in question_lower:
                result = smart_home.control_philips_hue("living_room", on=True, brightness=254)
                if result:
                    return "Let there be light, though it pales before my darkness."
                else:
                    return "The light spirits resist my command, mortal."
                    
            elif any(word in question_lower for word in ['dim', 'brightness', '%', 'percent']):
                # Extract brightness percentage
                import re
                brightness_match = re.search(r'(\d+)\s*%?', question_lower)
                if brightness_match:
                    percentage = int(brightness_match.group(1))
                    brightness = max(1, min(254, int(percentage * 2.54)))  # Convert % to 0-254
                    result = smart_home.control_philips_hue("living_room", on=True, brightness=brightness)
                    if result:
                        return f"The lights bow to my will at {percentage}% brightness, mortal."
                    else:
                        return "The light spirits resist my command, mortal."
                else:
                    # Default dim
                    result = smart_home.control_philips_hue("living_room", on=True, brightness=127)
                    if result:
                        return "The lights dim to half their strength, as befits your presence."
                    else:
                        return "The light spirits resist my command, mortal."
        except Exception as e:
            print(f"Smart home error: {e}")
            return "My powers over the physical realm are temporarily weakened, mortal."
    
    return None  # Not a smart home command

def get_ai_response(question):
    """Get AI response from XAI."""
    import httpx
    
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        return "API key not configured, mortal."
    
    try:
        with httpx.Client() as client:
            response = client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-2-1212",  # Updated to current Grok model
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": question}
                    ],
                    "max_tokens": 150,
                    "temperature": 0.8
                },
                timeout=15.0
            )
            
            print(f"XAI API Response: {response.status_code}")
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"XAI API Error: {response.status_code} - {response.text}")
                return f"The dark forces are silent, mortal. Error {response.status_code}."
                
    except Exception as e:
        print(f"AI request failed: {e}")
        return "My powers are weakened, mortal. Try again later."

def run_vad_assistant():
    """Run the Evil Assistant with VAD-based speech detection."""
    print("🔥 Starting Simple VAD-powered Evil Assistant")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment variables")
    
    # Debug API keys
    xai_key = os.getenv("XAI_API_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY") 
    elevenlabs_voice = os.getenv("ELEVENLABS_VOICE_ID")
    
    print(f"XAI API Key: {'✅ Found' if xai_key else '❌ Missing'}")
    print(f"ElevenLabs API Key: {'✅ Found' if elevenlabs_key else '❌ Missing'}")
    print(f"ElevenLabs Voice ID: {'✅ Found' if elevenlabs_voice else '❌ Missing'}")
    
    # Initialize pygame mixer
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    
    # Initialize VAD processor
    vad = initialize_vad()
    
    # Initialize Smart Home Controller
    print("Initializing smart home integration...")
    smart_home = SmartHomeController()
    if os.getenv("PHILIPS_HUE_BRIDGE_IP"):
        smart_home.setup_philips_hue(os.getenv("PHILIPS_HUE_BRIDGE_IP"))
        print("✅ Philips Hue integration ready")
    else:
        print("⚠️  PHILIPS_HUE_BRIDGE_IP not set - Hue integration disabled")
    
    # Initialize Whisper model (optimized for speed)
    print("Loading Whisper model...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8", num_workers=1)
    
    print(f"Listening for wake-up phrases: {', '.join(WAKE_PHRASES)}...")
    
    try:
        while True:
            # Listen for wake phrase using VAD
            wake_phrase = vad.listen_for_wake_phrase(WAKE_PHRASES, model)
            
            if wake_phrase:
                print("🔥 Wake detected!")
                
                # Record question using VAD
                question_audio = vad.record_question()
                
                if question_audio is not None:
                    # Transcribe question
                    question = transcribe_audio(question_audio, model, "question")
                    
                    if question and len(question.strip()) > 2:
                        print(f"Question: {question}")
                        
                        # Check for smart home commands first
                        print("Processing question...")
                        smart_home_response = process_smart_home_command(question, smart_home)
                        
                        if smart_home_response:
                            print("🏠 Smart home command executed!")
                            response = smart_home_response
                        else:
                            # Get AI response for non-smart-home questions
                            response = get_ai_response(question)
                            
                        print(f"Evil Assistant says: {response}")
                        
                        # Synthesize and play response
                        print("🔥 Using ElevenLabs demon voice...")
                        if _synthesize_with_elevenlabs(response, "response.wav"):
                            play_audio_file("response.wav")
                            if os.path.exists("response.wav"):
                                os.remove("response.wav")
                        
                        # Continue listening for follow-up questions
                        while True:
                            print("Ask another question or say 'stop' to return to wake mode...")
                            
                            follow_up_audio = vad.record_question()
                            
                            if follow_up_audio is None:
                                print("No follow-up detected, returning to wake mode...")
                                break
                                
                            follow_up = transcribe_audio(follow_up_audio, model, "followup")
                            
                            if not follow_up or len(follow_up.strip()) <= 2:
                                print("No clear follow-up, returning to wake mode...")
                                break
                                
                            # Check for stop phrases
                            if any(phrase in follow_up for phrase in STOP_PHRASES):
                                print(f"Stop phrase detected: '{follow_up}', returning to wake mode...")
                                break
                                
                            print(f"Follow-up: {follow_up}")
                            
                            # Check for smart home commands in follow-up
                            smart_home_response = process_smart_home_command(follow_up, smart_home)
                            
                            if smart_home_response:
                                print("🏠 Smart home command executed!")
                                response = smart_home_response
                            else:
                                # Get AI response for non-smart-home follow-ups
                                response = get_ai_response(follow_up)
                                
                            print(f"Evil Assistant says: {response}")
                            
                            # Synthesize and play response
                            print("🔥 Using ElevenLabs demon voice...")
                            if _synthesize_with_elevenlabs(response, "followup_response.wav"):
                                play_audio_file("followup_response.wav")
                                if os.path.exists("followup_response.wav"):
                                    os.remove("followup_response.wav")
                    
                    else:
                        print("No clear question detected, prompting...")
                        # Play follow-up prompt
                        print(f"📢 FOLLOW-UP PROMPT: {FOLLOW_UP_PROMPT}")
                        print("🔥 Using ElevenLabs demon voice...")
                        if _synthesize_with_elevenlabs(FOLLOW_UP_PROMPT, "prompt.wav"):
                            play_audio_file("prompt.wav")
                            if os.path.exists("prompt.wav"):
                                os.remove("prompt.wav")
                else:
                    print("No question audio detected, returning to wake mode...")
                    
            print(f"Listening for wake-up phrases: {', '.join(WAKE_PHRASES)}...")
            
    except KeyboardInterrupt:
        print("\n🔥 Evil Assistant shutting down...")
    except Exception as e:
        print(f"Error in assistant: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_vad_assistant()
