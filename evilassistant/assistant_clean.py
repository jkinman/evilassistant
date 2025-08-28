#!/usr/bin/env python3
"""
Clean, refactored Evil Assistant with proper separation of concerns.
"""

import os
import wave
import tempfile
import pygame
import requests
from faster_whisper import WhisperModel
from .config import *
from .simple_vad import SimpleVADRecorder
import numpy as np

# Global components
vad_processor = None
smart_home_controller = None
model = None

class AssistantComponents:
    """Container for all assistant components with proper initialization."""
    
    def __init__(self):
        self.vad = None
        self.smart_home = None
        self.model = None
        self.initialized = False
    
    def initialize_environment(self):
        """Load and validate environment variables."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ Environment variables loaded")
        except ImportError:
            print("⚠️  python-dotenv not installed, using system environment variables")
        
        # Validate API keys
        xai_key = os.getenv("XAI_API_KEY")
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY") 
        elevenlabs_voice = os.getenv("ELEVENLABS_VOICE_ID")
        hue_ip = os.getenv("PHILIPS_HUE_BRIDGE_IP")
        
        print(f"XAI API Key: {'✅ Found' if xai_key else '❌ Missing'}")
        print(f"ElevenLabs API Key: {'✅ Found' if elevenlabs_key else '❌ Missing'}")
        print(f"ElevenLabs Voice ID: {'✅ Found' if elevenlabs_voice else '❌ Missing'}")
        print(f"Hue Bridge IP: {'✅ Found' if hue_ip else '❌ Missing'}")
        
        return xai_key, elevenlabs_key, elevenlabs_voice, hue_ip
    
    def initialize_audio(self):
        """Initialize pygame mixer for audio playback."""
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        print("✅ Audio system initialized")
    
    def initialize_vad(self):
        """Initialize VAD audio processor."""
        self.vad = SimpleVADRecorder(
            sample_rate=RATE,
            chunk_duration=0.1,
            speech_timeout=0.8,
            min_speech_duration=0.5,
            energy_threshold=SILENCE_THRESHOLD
        )
        print("✅ VAD processor initialized")
        return self.vad
    
    def initialize_smart_home(self, hue_ip):
        """Initialize smart home controller."""
        try:
            from .smart_home import SmartHomeController
            
            # Create config for SmartHomeController
            config = {
                'PHILIPS_HUE_BRIDGE_IP': hue_ip,
                'HOME_ASSISTANT_URL': None,
                'GOOGLE_HOME_DEVICES': None
            }
            
            self.smart_home = SmartHomeController(config)
            print("✅ Smart home controller initialized")
            
            if hue_ip:
                print("✅ Philips Hue IP configured")
            else:
                print("⚠️  PHILIPS_HUE_BRIDGE_IP not set - Hue integration disabled")
            
            return self.smart_home
        except Exception as e:
            print(f"❌ Smart home initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def initialize_whisper(self):
        """Initialize Whisper model for speech recognition."""
        print("Loading Whisper model...")
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8", num_workers=1)
        print("✅ Whisper model loaded")
        return self.model
    
    def initialize_all(self):
        """Initialize all components."""
        # Environment
        xai_key, elevenlabs_key, elevenlabs_voice, hue_ip = self.initialize_environment()
        
        # Audio
        self.initialize_audio()
        
        # VAD
        self.vad = self.initialize_vad()
        
        # Smart Home
        self.smart_home = self.initialize_smart_home(hue_ip)
        
        # Whisper
        self.model = self.initialize_whisper()
        
        self.initialized = True
        print("🔥 All components initialized successfully!")
        
        return self.vad, self.smart_home, self.model

class SmartHomeHandler:
    """Handles all smart home command processing."""
    
    def __init__(self, smart_home_controller):
        self.smart_home = smart_home_controller
        self.hue_bridge = None
        
        # Initialize direct Hue connection for synchronous control
        hue_ip = os.getenv("PHILIPS_HUE_BRIDGE_IP")
        if hue_ip:
            try:
                from phue import Bridge
                self.hue_bridge = Bridge(hue_ip)
                self.hue_bridge.connect()
                print("✅ Direct Hue bridge connection established")
            except Exception as e:
                print(f"⚠️  Direct Hue connection failed: {e}")
                self.hue_bridge = None
    
    def is_light_command(self, text):
        """Check if text contains light control commands."""
        text_lower = text.lower()
        return any(word in text_lower for word in ['light', 'lights', 'lamp', 'brightness'])
    
    def extract_brightness_percentage(self, text):
        """Extract brightness percentage from text."""
        import re
        brightness_match = re.search(r'(\d+)\s*%?', text.lower())
        if brightness_match:
            percentage = int(brightness_match.group(1))
            return max(1, min(100, percentage))
        return None
    
    def process_light_command(self, text):
        """Process light control commands."""
        if not self.hue_bridge:
            return "My powers over the physical realm are weakened, mortal."
        
        text_lower = text.lower()
        
        try:
            if 'off' in text_lower or 'turn off' in text_lower:
                # Turn off all lights
                for light in self.hue_bridge.lights:
                    light.on = False
                return "The lights have been extinguished, mortal. Darkness consumes you."
                    
            elif 'on' in text_lower or 'turn on' in text_lower:
                # Turn on all lights to full brightness
                for light in self.hue_bridge.lights:
                    light.on = True
                    light.brightness = 254
                return "Let there be light, though it pales before my darkness."
                    
            elif any(word in text_lower for word in ['dim', 'brightness', '%', 'percent']):
                percentage = self.extract_brightness_percentage(text)
                if percentage:
                    brightness = int(percentage * 2.54)  # Convert % to 0-254
                    for light in self.hue_bridge.lights:
                        light.on = True
                        light.brightness = brightness
                    return f"The lights bow to my will at {percentage}% brightness, mortal."
                else:
                    # Default dim to 50%
                    for light in self.hue_bridge.lights:
                        light.on = True
                        light.brightness = 127
                    return "The lights dim to half their strength, as befits your presence."
                        
        except Exception as e:
            print(f"Smart home error: {e}")
            return "My powers over the physical realm are temporarily weakened, mortal."
        
        return None
    
    def process_command(self, text):
        """Process any smart home command."""
        if self.is_light_command(text):
            return self.process_light_command(text)
        
        # Add other smart home commands here (thermostat, etc.)
        return None

class AudioHandler:
    """Handles all audio processing and playback."""
    
    @staticmethod
    def transcribe_audio(audio_data, model, file_suffix="temp"):
        """Transcribe audio data using Whisper."""
        with tempfile.NamedTemporaryFile(suffix=f'_{file_suffix}.wav', delete=False) as tmp_file:
            with wave.open(tmp_file.name, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(RATE)
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
    
    @staticmethod
    def synthesize_speech(text, output_file):
        """Generate speech using ElevenLabs."""
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key or not ELEVENLABS_VOICE_ID:
            print("ELEVENLABS_API_KEY or ELEVENLABS_VOICE_ID missing")
            return False
            
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        headers = {
            "xi-api-key": api_key,
            "accept": "audio/mpeg",
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
                "speed": 1.2           # Increase speech speed for more dynamic delivery
            }
        }
        
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            
            temp_mp3 = output_file.replace('.wav', '_temp.mp3')
            with open(temp_mp3, "wb") as f:
                f.write(r.content)
            
            # Convert MP3 to WAV with ultra-conservative anti-clipping processing + fade-in
            sox_effects = f"sox {temp_mp3} {output_file} fade 0.05 vol 0.1"
            os.system(sox_effects)
            
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
            
            return True
        except Exception as e:
            print(f"ElevenLabs TTS failed: {e}")
            return False
    
    @staticmethod
    def play_audio_file(file_path):
        """Play audio file using pygame."""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
        except Exception as e:
            print(f"Error playing audio: {e}")

class AIHandler:
    """Handles AI response generation."""
    
    @staticmethod
    def get_ai_response(question):
        """Get AI response from XAI Grok."""
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
                        "model": "grok-2-1212",
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

class ConversationHandler:
    """Handles conversation flow and question processing."""
    
    def __init__(self, smart_home_handler, audio_handler, ai_handler):
        self.smart_home = smart_home_handler
        self.audio = audio_handler
        self.ai = ai_handler
    
    def process_question(self, question):
        """Process a question through smart home then AI if needed."""
        print(f"Question: {question}")
        print("Processing question...")
        
        # Try smart home first
        smart_response = self.smart_home.process_command(question)
        if smart_response:
            print("🏠 Smart home command executed!")
            return smart_response
        
        # Fall back to AI
        return self.ai.get_ai_response(question)
    
    def handle_response(self, response):
        """Handle response synthesis and playback."""
        print(f"Evil Assistant says: {response}")
        print("🔥 Using ElevenLabs demon voice...")
        
        if self.audio.synthesize_speech(response, "response.wav"):
            self.audio.play_audio_file("response.wav")
            if os.path.exists("response.wav"):
                os.remove("response.wav")

def run_clean_assistant():
    """Run the clean, refactored Evil Assistant."""
    print("🔥 Starting Clean Evil Assistant")
    
    # Initialize all components
    components = AssistantComponents()
    vad, smart_home_ctrl, model = components.initialize_all()
    
    if not components.initialized:
        print("❌ Failed to initialize components")
        return
    
    # Initialize handlers
    smart_home_handler = SmartHomeHandler(smart_home_ctrl)
    audio_handler = AudioHandler()
    ai_handler = AIHandler()
    conversation_handler = ConversationHandler(smart_home_handler, audio_handler, ai_handler)
    
    print(f"Listening for wake-up phrases: {', '.join(WAKE_PHRASES)}...")
    
    try:
        while True:
            # Listen for wake phrase
            wake_phrase = vad.listen_for_wake_phrase(WAKE_PHRASES, model)
            
            if wake_phrase:
                print("🔥 Wake detected!")
                
                # Check if question was extracted from wake audio
                question = None
                if hasattr(vad, 'extracted_question') and vad.extracted_question:
                    question = vad.extracted_question
                    print(f"💡 Using extracted question: {question}")
                else:
                    # Record and process question normally
                    question_audio = vad.record_question()
                    if question_audio is not None:
                        question = audio_handler.transcribe_audio(question_audio, model, "question")
                
                if question and len(question.strip()) > 2:
                    response = conversation_handler.process_question(question)
                    conversation_handler.handle_response(response)
                    
                    # Clear extracted question after use
                    if hasattr(vad, 'extracted_question'):
                        vad.extracted_question = None
                        
                        # Handle follow-up questions
                        while True:
                            print("Ask another question or say 'stop' to return to wake mode...")
                            
                            follow_up_audio = vad.record_question()
                            if follow_up_audio is None:
                                print("No follow-up detected, returning to wake mode...")
                                break
                                
                            follow_up = audio_handler.transcribe_audio(follow_up_audio, model, "followup")
                            if not follow_up or len(follow_up.strip()) <= 2:
                                print("No clear follow-up, returning to wake mode...")
                                break
                                
                            if any(phrase in follow_up for phrase in STOP_PHRASES):
                                print(f"Stop phrase detected: '{follow_up}', returning to wake mode...")
                                break
                                
                            print(f"Follow-up: {follow_up}")
                            response = conversation_handler.process_question(follow_up)
                            conversation_handler.handle_response(response)
                    
                    else:
                        print("No clear question detected, prompting...")
                        conversation_handler.handle_response(FOLLOW_UP_PROMPT)
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
    run_clean_assistant()
