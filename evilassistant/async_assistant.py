"""
Async Evil Assistant - High-performance real-time voice assistant
Integrates all optimized components for minimal latency
"""

import asyncio
import logging
import time
import numpy as np
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading

# Import our optimized components
from .audio_stream import StreamingAudioProcessor, AudioConfig, CircularAudioBuffer
from .wake_word import WakeWordDetector, WakeWordConfig
from .speech_recognition import HybridSTT, STTConfig
from .audio_effects import RealtimeEffectsProcessor, create_demonic_voice_config
from .smart_home import SmartHomeController

# GPIO for LED control
try:
    import RPi.GPIO as GPIO
    _GPIO_AVAILABLE = True
except ImportError:
    _GPIO_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AssistantConfig:
    """Configuration for the complete assistant"""
    # Audio settings
    sample_rate: int = 16000
    audio_buffer_duration: float = 2.0
    
    # Performance settings
    max_concurrent_tasks: int = 4
    response_timeout: float = 10.0
    
    # Component configs
    audio_config: Optional[AudioConfig] = None
    wake_config: Optional[WakeWordConfig] = None
    stt_config: Optional[STTConfig] = None
    
    # GPIO LED settings
    gpio_enabled: bool = True
    gpio_pin: int = 18
    pwm_frequency: int = 2000
    led_brightness_min: float = 5.0
    led_brightness_max: float = 85.0
    led_gain: float = 200.0
    led_smoothing: float = 0.8
    
    # LLM settings
    llm_provider: str = "ollama"  # "ollama", "cloud"
    ollama_model: str = "llama3.2:3b"
    ollama_url: str = "http://localhost:11434"
    cloud_model: str = "grok-2-latest"
    
    # TTS settings
    tts_provider: str = "piper"  # "piper", "coqui", "elevenlabs"
    
    # Smart home
    smart_home_enabled: bool = False
    
    def __post_init__(self):
        if self.audio_config is None:
            self.audio_config = AudioConfig(
                sample_rate=self.sample_rate,
                buffer_duration=self.audio_buffer_duration
            )
        
        if self.wake_config is None:
            self.wake_config = WakeWordConfig(
                sample_rate=self.sample_rate,
                method="openwakeword",
                confidence_threshold=0.5
            )
        
        if self.stt_config is None:
            self.stt_config = STTConfig(
                sample_rate=self.sample_rate,
                primary_engine="vosk",
                fallback_engine="whisper"
            )


class LEDController:
    """Real-time LED brightness control"""
    
    def __init__(self, config: AssistantConfig):
        self.config = config
        self.pwm = None
        self.current_brightness = 0.0
        self.smoothed_level = 0.0
        
        if config.gpio_enabled and _GPIO_AVAILABLE:
            self._init_gpio()
    
    def _init_gpio(self):
        """Initialize GPIO PWM"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.config.gpio_pin, GPIO.OUT)
            self.pwm = GPIO.PWM(self.config.gpio_pin, self.config.pwm_frequency)
            self.pwm.start(0)
            logger.info(f"LED controller initialized on GPIO {self.config.gpio_pin}")
        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")
            self.pwm = None
    
    def update_brightness(self, rms_level: float):
        """Update LED brightness based on audio RMS level"""
        if not self.pwm:
            return
        
        # Apply smoothing
        alpha = self.config.led_smoothing
        self.smoothed_level = alpha * self.smoothed_level + (1 - alpha) * rms_level
        
        # Scale to brightness range
        scaled = self.smoothed_level * self.config.led_gain
        brightness = np.clip(
            self.config.led_brightness_min + 
            (self.config.led_brightness_max - self.config.led_brightness_min) * scaled,
            self.config.led_brightness_min,
            self.config.led_brightness_max
        )
        
        # Update PWM
        try:
            self.pwm.ChangeDutyCycle(brightness)
            self.current_brightness = brightness
        except Exception as e:
            logger.warning(f"Failed to update LED: {e}")
    
    def set_brightness(self, brightness: float):
        """Set LED to specific brightness"""
        if self.pwm:
            try:
                clamped = np.clip(brightness, 0, 100)
                self.pwm.ChangeDutyCycle(clamped)
                self.current_brightness = clamped
            except Exception as e:
                logger.warning(f"Failed to set LED brightness: {e}")
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        if self.pwm:
            try:
                self.pwm.ChangeDutyCycle(0)
                self.pwm.stop()
                GPIO.cleanup()
            except:
                pass
            self.pwm = None


class AsyncEvilAssistant:
    """High-performance async voice assistant"""
    
    def __init__(self, config: AssistantConfig):
        self.config = config
        
        # Core components
        self.audio_processor = StreamingAudioProcessor(config.audio_config)
        self.wake_detector = WakeWordDetector(config.wake_config)
        self.stt_engine = HybridSTT(config.stt_config)
        self.effects_processor = RealtimeEffectsProcessor(
            create_demonic_voice_config(config.sample_rate)
        )
        self.led_controller = LEDController(config)
        
        # Smart home (optional)
        self.smart_home = None
        if config.smart_home_enabled:
            self.smart_home = SmartHomeController({})
        
        # Async processing
        self.executor = ThreadPoolExecutor(max_workers=config.max_concurrent_tasks)
        self.loop = None
        
        # State management
        self.is_running = False
        self.is_processing = False
        self.conversation_active = False
        
        # Performance tracking
        self.performance_stats = {
            'total_interactions': 0,
            'wake_detections': 0,
            'successful_transcriptions': 0,
            'response_times': [],
            'avg_response_time': 0
        }
        
        # Connect audio callbacks
        self._setup_audio_callbacks()
        
        logger.info("Async Evil Assistant initialized")
    
    def _setup_audio_callbacks(self):
        """Connect audio processing callbacks"""
        self.audio_processor.wake_word_callback = self._wake_word_callback
        self.audio_processor.speech_start_callback = self._speech_start_callback
        self.audio_processor.speech_end_callback = self._speech_end_callback
        self.audio_processor.led_update_callback = self._led_update_callback
    
    def _wake_word_callback(self, audio: np.ndarray) -> bool:
        """Check for wake word in audio"""
        return self.wake_detector.process_audio(audio)
    
    def _speech_start_callback(self):
        """Called when speech recording starts"""
        logger.info("👹 Listening for your command, mortal...")
        self.conversation_active = True
        
        # Set LED to listening mode
        self.led_controller.set_brightness(50)
    
    def _speech_end_callback(self, speech_audio: np.ndarray):
        """Process recorded speech"""
        if not self.conversation_active:
            return
        
        # Process speech asynchronously
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self._process_speech_async(speech_audio),
                self.loop
            )
    
    def _led_update_callback(self, rms_level: float):
        """Update LED brightness"""
        self.led_controller.update_brightness(rms_level)
    
    async def _process_speech_async(self, speech_audio: np.ndarray):
        """Async speech processing pipeline"""
        interaction_start = time.time()
        
        try:
            self.is_processing = True
            self.performance_stats['total_interactions'] += 1
            
            # Step 1: Speech Recognition
            logger.info("🔄 Transcribing speech...")
            stt_result = await self.stt_engine.transcribe_async(speech_audio)
            
            if not stt_result.get('text'):
                logger.warning("No speech detected")
                await self._speak_error("I heard nothing but silence, mortal.")
                return
            
            transcription = stt_result['text'].strip().lower()
            logger.info(f"📝 Transcribed: '{transcription}'")
            self.performance_stats['successful_transcriptions'] += 1
            
            # Check for stop commands
            stop_phrases = ["shut up", "stop", "quiet", "be silent", "unsummon"]
            if any(phrase in transcription for phrase in stop_phrases):
                logger.info("Stop command detected")
                await self._speak_response("Very well, I return to the shadows...")
                self.conversation_active = False
                return
            
            # Step 2: Check for smart home commands
            if self.smart_home:
                smart_command = self.smart_home.parse_command(transcription)
                if smart_command:
                    logger.info(f"Smart home command: {smart_command}")
                    response = await self.smart_home.execute_command(smart_command)
                    await self._speak_response(response)
                    return
            
            # Step 3: Generate LLM response
            logger.info("🧠 Generating response...")
            response = await self._generate_llm_response(transcription)
            
            # Step 4: Speak response
            await self._speak_response(response)
            
            # Update performance stats
            total_time = time.time() - interaction_start
            self.performance_stats['response_times'].append(total_time)
            self.performance_stats['avg_response_time'] = (
                sum(self.performance_stats['response_times']) / 
                len(self.performance_stats['response_times'])
            )
            
            logger.info(f"⚡ Total interaction time: {total_time*1000:.1f}ms")
            
        except Exception as e:
            logger.error(f"Error processing speech: {e}")
            await self._speak_error("The dark forces interfere with my power!")
            
        finally:
            self.is_processing = False
    
    async def _generate_llm_response(self, text: str) -> str:
        """Generate LLM response (local or cloud)"""
        system_prompt = (
            "You are Evil Assistant, a malevolent entity who resents puny mortals. "
            "Always respond in exactly two parts: "
            "1) a single-sentence demonic welcome/taunt addressing the mortal, "
            "2) a concise, direct answer in 1–2 short sentences. "
            "Keep it dark, disdainful, and to the point."
        )
        
        try:
            if self.config.llm_provider == "ollama":
                response = await self._query_ollama(system_prompt, text)
            else:
                response = await self._query_cloud_llm(system_prompt, text)
            
            return response
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "The void consumes my words, ask again mortal."
    
    async def _query_ollama(self, system_prompt: str, user_text: str) -> str:
        """Query local Ollama LLM"""
        import aiohttp
        
        payload = {
            "model": self.config.ollama_model,
            "prompt": f"System: {system_prompt}\n\nUser: {user_text}\n\nAssistant:",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 150,
                "top_p": 0.9
            }
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.post(f"{self.config.ollama_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '').strip()
                    else:
                        raise Exception(f"Ollama error: {response.status}")
        except Exception as e:
            logger.warning(f"Ollama request failed: {e}")
            raise
    
    async def _query_cloud_llm(self, system_prompt: str, user_text: str) -> str:
        """Query cloud LLM as fallback"""
        # This would integrate with your existing OpenAI/XAI setup
        # For now, return a placeholder
        return "Cloud LLM integration needed, foolish mortal!"
    
    async def _speak_response(self, text: str):
        """Generate and play TTS response"""
        logger.info(f"🗣️ Speaking: '{text}'")
        
        # Set LED to speaking mode
        self.led_controller.set_brightness(80)
        
        try:
            # Generate TTS (this should be made async too)
            audio_data = await self._generate_tts_async(text)
            
            if audio_data is not None:
                # Apply real-time effects
                processed_audio = self.effects_processor.process_audio(audio_data)
                
                # Play audio (this should also be async)
                await self._play_audio_async(processed_audio)
            
        except Exception as e:
            logger.error(f"TTS/playback failed: {e}")
        
        finally:
            # Return LED to idle
            self.led_controller.set_brightness(10)
    
    async def _speak_error(self, message: str):
        """Speak error message"""
        await self._speak_response(message)
    
    async def _generate_tts_async(self, text: str) -> Optional[np.ndarray]:
        """Generate TTS audio asynchronously"""
        # This should integrate with your TTS system
        # For now, return silence
        duration = len(text) * 0.1  # Rough estimate
        samples = int(duration * self.config.sample_rate)
        return np.zeros(samples, dtype=np.float32)
    
    async def _play_audio_async(self, audio: np.ndarray):
        """Play audio asynchronously"""
        # This should integrate with your audio playback
        # For now, just simulate playback time
        duration = len(audio) / self.config.sample_rate
        await asyncio.sleep(duration)
    
    async def start(self):
        """Start the assistant"""
        logger.info("🔥 Starting Evil Assistant...")
        
        self.loop = asyncio.get_event_loop()
        self.is_running = True
        
        # Initialize smart home if enabled
        if self.smart_home:
            await self.smart_home.initialize()
        
        # Start audio processing
        self.audio_processor.start_stream()
        
        # Set LED to idle
        self.led_controller.set_brightness(10)
        
        logger.info("👹 Evil Assistant is active and listening...")
        
        try:
            # Main loop
            while self.is_running:
                await asyncio.sleep(1)
                
                # Periodic stats logging
                if self.performance_stats['total_interactions'] > 0:
                    stats = self.get_performance_stats()
                    if stats['total_interactions'] % 10 == 0:  # Every 10 interactions
                        logger.info(f"Performance: {stats}")
        
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the assistant"""
        logger.info("🛑 Stopping Evil Assistant...")
        
        self.is_running = False
        
        # Stop audio processing
        self.audio_processor.stop_stream()
        
        # Cleanup GPIO
        self.led_controller.cleanup()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Evil Assistant stopped")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        base_stats = self.performance_stats.copy()
        
        # Add component stats
        base_stats['audio'] = self.audio_processor.get_performance_stats()
        base_stats['wake_detection'] = self.wake_detector.get_stats()
        base_stats['stt'] = self.stt_engine.get_comprehensive_stats()
        base_stats['effects'] = self.effects_processor.get_stats()
        
        return base_stats
    
    def force_wake(self):
        """Force wake the assistant (for testing)"""
        logger.info("🔥 Force wake triggered")
        self.audio_processor._start_speech_recording()


async def main():
    """Main entry point for async assistant"""
    # Create configuration
    config = AssistantConfig(
        gpio_enabled=True,
        smart_home_enabled=False,  # Enable when ready
        llm_provider="ollama"  # Change to "cloud" if Ollama not available
    )
    
    # Create and start assistant
    assistant = AsyncEvilAssistant(config)
    
    try:
        await assistant.start()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    finally:
        await assistant.stop()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run assistant
    asyncio.run(main())
