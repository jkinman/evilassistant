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
        # Use optimized Whisper settings from config
        self.model = WhisperModel(
            WHISPER_MODEL, 
            device="cpu", 
            compute_type=WHISPER_COMPUTE_TYPE,
            num_workers=WHISPER_NUM_WORKERS
        )
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
        self.home_assistant = None
        
        # Initialize Home Assistant integration
        try:
            from .home_assistant_integration import get_evil_home_assistant
            self.home_assistant = get_evil_home_assistant()
            if self.home_assistant.enabled:
                print("✅ Home Assistant integration enabled")
            else:
                print("⚠️  Home Assistant integration disabled (no token)")
        except ImportError as e:
            print(f"⚠️  Home Assistant integration not available: {e}")
        
        # Initialize direct Hue connection for synchronous control (fallback)
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
        return any(word in text_lower for word in ['light', 'lights', 'lamp', 'brightness', 'color', 'colour', 'red', 'blue', 'green', 'purple', 'yellow', 'orange', 'pink', 'white'])
    
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
            # Handle color changes first
            color_commands = {
                'red': (65535, 254, 254),      # Hue, Saturation, Brightness
                'blue': (46920, 254, 254),
                'green': (25500, 254, 254),
                'purple': (56100, 254, 254),
                'yellow': (12750, 254, 254),
                'orange': (8618, 254, 254),
                'pink': (56100, 76, 254),
                'white': (0, 0, 254),
            }
            
            for color_name, (hue, sat, bri) in color_commands.items():
                if color_name in text_lower:
                    for light in self.hue_bridge.lights:
                        light.on = True
                        light.hue = hue
                        light.saturation = sat
                        light.brightness = bri
                    return f"The lights blaze with {color_name} fire, mortal. My darkness adapts to all hues."
            
            # Handle brightness changes
            percentage = self.extract_brightness_percentage(text)
            if percentage and ('brightness' in text_lower or '%' in text_lower or 'percent' in text_lower):
                brightness = int(percentage * 2.54)  # Convert % to 0-254
                for light in self.hue_bridge.lights:
                    light.on = True
                    light.brightness = brightness
                return f"The lights bow to my will at {percentage}% brightness, mortal."
            
            # Handle on/off commands
            if 'off' in text_lower or 'turn off' in text_lower:
                for light in self.hue_bridge.lights:
                    light.on = False
                return "The lights have been extinguished, mortal. Darkness consumes you."
                    
            elif 'on' in text_lower or 'turn on' in text_lower:
                for light in self.hue_bridge.lights:
                    light.on = True
                    light.brightness = 254
                return "Let there be light, though it pales before my darkness."
            
            # Handle dim command (no specific percentage)
            elif 'dim' in text_lower:
                for light in self.hue_bridge.lights:
                    light.on = True
                    light.brightness = 127  # 50%
                return "The lights dim to half their strength, as befits your presence."
                        
        except Exception as e:
            print(f"Smart home error: {e}")
            return "My powers over the physical realm are temporarily weakened, mortal."
        
        return None
    
    async def process_command(self, text):
        """Process any smart home command."""
        # Try Home Assistant first (most comprehensive)
        if self.home_assistant and self.home_assistant.enabled:
            try:
                ha_response = await self.home_assistant.process_command(text)
                if ha_response:
                    return ha_response
            except Exception as e:
                print(f"Home Assistant command failed: {e}")
        
        # Fallback to direct integrations
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
                segments, _ = model.transcribe(
                    tmp_file.name, 
                    beam_size=WHISPER_BEAM_SIZE,
                    language=WHISPER_LANGUAGE, 
                    vad_filter=WHISPER_VAD_FILTER
                )
                transcription = " ".join([segment.text for segment in segments]).strip().lower()
                return transcription
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
    
    @staticmethod
    def synthesize_speech(text, output_file):
        """Generate speech using configurable TTS engine."""
        try:
            from .tts import create_configured_engine
            from .config import TTS_VOICE_PROFILE
            
            # Create configured TTS engine with fallback
            engine = create_configured_engine(TTS_VOICE_PROFILE)
            
            success = engine.synthesize(text, output_file)
            if success:
                provider = engine.get_current_provider()
                print(f"✅ TTS successful with {provider}")
                return True
            else:
                print("❌ All TTS providers failed")
                return False
                
        except Exception as e:
            print(f"TTS Engine error: {e}")
            return False
    
    @staticmethod
    def play_audio_file_with_interrupt(file_path, vad_processor, model):
        """Play audio file with interrupt capability for stop commands."""
        import threading
        import time
        
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Monitor for stop commands during playback
            while pygame.mixer.music.get_busy():
                # Quick check for stop command (non-blocking)
                try:
                    # Very short recording to check for "stop" 
                    import sounddevice as sd
                    import numpy as np
                    
                    chunk_size = int(vad_processor.sample_rate * 0.2)  # 200ms
                    chunk = sd.rec(chunk_size, samplerate=vad_processor.sample_rate, 
                                  channels=1, dtype='float32')
                    sd.wait()
                    
                    # Quick energy check
                    energy = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)) * 32767)
                    if energy > vad_processor.energy_threshold * 2:  # Higher threshold during playback
                        # Quick transcription check for stop words
                        import tempfile
                        import wave
                        
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                            with wave.open(tmp_file.name, 'wb') as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(vad_processor.sample_rate)
                                audio_int16 = (chunk * 32767).astype(np.int16)
                                wf.writeframes(audio_int16.tobytes())
                            
                            try:
                                segments, _ = model.transcribe(
                                    tmp_file.name, 
                                    beam_size=WHISPER_BEAM_SIZE,
                                    language=WHISPER_LANGUAGE,
                                    vad_filter=WHISPER_VAD_FILTER
                                )
                                transcription = " ".join([segment.text for segment in segments]).strip().lower()
                                
                                if any(word in transcription for word in ['stop', 'shut up', 'be silent', 'unsummon']):
                                    print("🛑 Stop command detected during playback!")
                                    pygame.mixer.music.stop()
                                    import os
                                    if os.path.exists(tmp_file.name):
                                        os.unlink(tmp_file.name)
                                    return True  # Interrupted
                            except:
                                pass  # Ignore transcription errors during playback
                            finally:
                                import os
                                if os.path.exists(tmp_file.name):
                                    os.unlink(tmp_file.name)
                    
                    pygame.time.wait(100)  # Small delay between checks
                    
                except Exception:
                    pygame.time.wait(100)  # Fallback delay
                    
        except Exception as e:
            print(f"Error playing audio: {e}")
        
        return False  # Completed normally
    
    @staticmethod
    def play_audio_file(file_path):
        """Simple audio playback without interruption."""
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
    
    def __init__(self, smart_home_handler, audio_handler, ai_handler, vad_processor=None, model=None):
        self.smart_home = smart_home_handler
        self.audio = audio_handler
        self.ai = ai_handler
        self.vad_processor = vad_processor
        self.model = model
    
    async def process_question(self, question):
        """Process a question through unified command processor."""
        print(f"Question: {question}")
        print("Processing question...")
        
        # Use unified command processor for all commands
        try:
            from .unified_command_processor import UnifiedCommandProcessor
            
            # Initialize transcription handler if available
            transcription_handler = None
            try:
                from .evil_transcription_commands import get_evil_transcription_handler
                transcription_handler = get_evil_transcription_handler()
            except ImportError:
                pass
            
            # Create unified processor
            processor = UnifiedCommandProcessor(
                smart_home_handler=self.smart_home,
                ai_handler=self.ai,
                transcription_handler=transcription_handler
            )
            
            # Process command through unified pipeline
            command_type, response = await processor.process_command(question)
            
            # Log what type of command was processed
            type_icons = {
                "transcription": "🎧",
                "smart_home": "🏠", 
                "ai_query": "🧠",
                "system": "⚙️"
            }
            icon = type_icons.get(command_type.value, "❓")
            print(f"{icon} {command_type.value.title()} command executed!")
            
            return response
            
        except ImportError as e:
            print(f"⚠️  Unified processor not available: {e}")
            # Fallback to old method if unified processor fails
            return self.ai.get_ai_response(question)
        except Exception as e:
            print(f"❌ Command processing failed: {e}")
            return "My dark powers are temporarily disrupted, mortal. Try again."
    
    def handle_response(self, response):
        """Handle response synthesis and playback with interrupt capability."""
        print(f"Evil Assistant says: {response}")
        print("🔥 Using ElevenLabs demon voice...")
        
        if self.audio.synthesize_speech(response, "response.wav"):
            # Use interruptible playback if VAD and model are available
            if self.vad_processor and self.model:
                interrupted = self.audio.play_audio_file_with_interrupt("response.wav", self.vad_processor, self.model)
                if interrupted:
                    print("🛑 Response interrupted by stop command")
            else:
                self.audio.play_audio_file("response.wav")
                
            if os.path.exists("response.wav"):
                os.remove("response.wav")

async def run_clean_assistant(enable_transcription=False):
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
    conversation_handler = ConversationHandler(smart_home_handler, audio_handler, ai_handler, vad, model)
    
    # Initialize transcription system (only if enabled)
    transcriber = None
    if enable_transcription:
        try:
            from .continuous_transcription import get_transcriber, start_continuous_transcription
            transcriber = get_transcriber()
            print("🎧 Continuous transcription system initialized")
            print("🔥 Say 'Evil assistant, start recording' to begin surveillance!")
        except ImportError as e:
            print(f"⚠️  Transcription system not available: {e}")
            transcriber = None
    else:
        print("🔇 Transcription disabled (use --transcription flag to enable)")
        print("ℹ️  Privacy mode: No conversation recording")
    
    print(f"Listening for wake-up phrases: {', '.join(WAKE_PHRASES)}...")
    
    try:
        logger.info("🚀 STARTING MAIN ASSISTANT LOOP")
        print("🚀 Evil Assistant ready - listening for commands...")
        
        while True:
            # Listen for wake phrase
            logger.info("👂 LISTENING FOR WAKE PHRASES")
            wake_phrase = vad.listen_for_wake_phrase(WAKE_PHRASES, model)
            
            if wake_phrase:
                logger.warning(f"⚡ WAKE PHRASE TRIGGERED: '{wake_phrase}'")
                print("🔥 Wake detected!")
                
                # Check if question was extracted from wake audio
                question = None
                if hasattr(vad, 'extracted_question') and vad.extracted_question:
                    question = vad.extracted_question
                    logger.info(f"💡 USING EXTRACTED QUESTION: '{question}'")
                    print(f"💡 Using extracted question: {question}")
                else:
                    # Record and process question normally
                    logger.info("🎤 RECORDING QUESTION AUDIO")
                    print("🎤 Recording your question...")
                    question_audio = vad.record_question()
                    if question_audio is not None:
                        logger.info("🔤 TRANSCRIBING QUESTION")
                        print("🔤 Transcribing question...")
                        question = audio_handler.transcribe_audio(question_audio, model, "question")
                        logger.info(f"📝 QUESTION TRANSCRIBED: '{question}'")
                
                if question and len(question.strip()) > 2:
                    logger.info(f"❓ PROCESSING QUESTION: '{question}'")
                    print(f"❓ Processing: '{question}'")
                    
                    response = await conversation_handler.process_question(question)
                    
                    if response:
                        logger.info(f"💬 RESPONSE GENERATED: '{response[:100]}...'")
                        print(f"💬 Response ready: '{response[:50]}...'")
                        conversation_handler.handle_response(response)
                    else:
                        logger.warning("❌ NO RESPONSE GENERATED")
                        print("❌ No response generated")
                    
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
                            response = await conversation_handler.process_question(follow_up)
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
