#!/usr/bin/env python3
"""
Audio Manager for Evil Assistant
Centralized audio handling with GPIO LED integration and better architecture
"""

import os
import threading
import time
import wave
import pygame
import numpy as np
import sounddevice as sd
import logging
from typing import Optional, Callable
from dataclasses import dataclass
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@dataclass
class AudioConfig:
    """Configuration for audio system"""
    sample_rate: int = 22050
    buffer_size: int = 512
    channels: int = 2
    bit_depth: int = -16  # 16-bit signed

class AudioManager:
    """
    Centralized audio management with GPIO LED integration
    Handles TTS synthesis, playback, and hardware control
    """
    
    def __init__(self, config: AudioConfig):
        self.config = config
        self.gpio_controller = None
        self._current_audio_data: Optional[np.ndarray] = None
        self._audio_lock = threading.Lock()
        self._is_playing = False
        
        # Initialize audio system
        self._initialize_audio()
        
        # Initialize GPIO controller
        self._initialize_gpio()
    
    def _initialize_audio(self):
        """Initialize pygame mixer for audio playback"""
        try:
            pygame.mixer.init(
                frequency=self.config.sample_rate,
                size=self.config.bit_depth,
                channels=self.config.channels,
                buffer=self.config.buffer_size
            )
            logger.info("✅ Audio system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize audio system: {e}")
            raise
    
    def _initialize_gpio(self):
        """Initialize GPIO controller for LED control"""
        try:
            from .gpio_controller import get_gpio_controller
            self.gpio_controller = get_gpio_controller()
            
            if self.gpio_controller and self.gpio_controller.gpio_available:
                logger.info("✅ GPIO LED control available")
            else:
                logger.info("ℹ️  GPIO LED control not available")
                
        except Exception as e:
            logger.warning(f"GPIO initialization failed: {e}")
    
    def synthesize_speech(self, text: str, output_file: str) -> bool:
        """
        Synthesize speech using the TTS engine
        
        Args:
            text: Text to synthesize
            output_file: Output file path
            
        Returns:
            True if synthesis was successful
        """
        try:
            from .tts.factory import create_configured_engine
            
            logger.info(f"🎭 Synthesizing speech: '{text[:50]}...'")
            
            tts_engine = create_configured_engine()
            success = tts_engine.synthesize(text, output_file)
            
            if success:
                logger.info(f"✅ Speech synthesis completed: {output_file}")
            else:
                logger.error("❌ Speech synthesis failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")
            return False
    
    def play_audio_file(self, file_path: str, enable_led_control: bool = True) -> bool:
        """
        Play an audio file with optional LED control
        
        Args:
            file_path: Path to audio file
            enable_led_control: Whether to enable LED brightness control
            
        Returns:
            True if playback completed successfully
        """
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return False
        
        try:
            logger.info(f"🔊 Playing audio: {file_path}")
            
            # Load and start playback with error handling
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
            except pygame.error as pygame_err:
                if "Unknown WAVE format" in str(pygame_err):
                    logger.warning(f"Pygame WAVE format issue: {pygame_err}")
                    # Try converting the file first
                    if self._convert_audio_for_pygame(file_path):
                        converted_path = file_path.replace('.wav', '_converted.wav')
                        pygame.mixer.music.load(converted_path)
                        pygame.mixer.music.play()
                        # Clean up converted file after playback
                        self._cleanup_converted_file = converted_path
                    else:
                        raise pygame_err
                else:
                    raise pygame_err
            
            # Start LED control if enabled and available
            led_started = False
            if enable_led_control and self.gpio_controller:
                self._start_led_control_for_file(file_path)
                led_started = True
            
            self._is_playing = True
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            self._is_playing = False
            
            # Stop LED control
            if led_started:
                self._stop_led_control()
            
            # Clean up any converted file
            if hasattr(self, '_cleanup_converted_file'):
                try:
                    if os.path.exists(self._cleanup_converted_file):
                        os.remove(self._cleanup_converted_file)
                        logger.debug(f"Cleaned up converted file: {self._cleanup_converted_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up converted file: {e}")
                finally:
                    delattr(self, '_cleanup_converted_file')
            
            logger.info("✅ Audio playback completed")
            return True
            
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            self._is_playing = False
            return False
    
    def play_audio_file_with_interrupt(self, file_path: str, vad_processor, model, 
                                     enable_led_control: bool = True) -> bool:
        """
        Play audio file with interrupt capability for stop commands
        
        Args:
            file_path: Path to audio file
            vad_processor: VAD processor for stop command detection
            model: Whisper model for transcription
            enable_led_control: Whether to enable LED brightness control
            
        Returns:
            True if interrupted, False if completed normally
        """
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return False
        
        try:
            logger.info(f"🔊 Playing audio with interrupt capability: {file_path}")
            
            # Load and start playback with error handling
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
            except pygame.error as pygame_err:
                if "Unknown WAVE format" in str(pygame_err):
                    logger.warning(f"Pygame WAVE format issue: {pygame_err}")
                    # Try converting the file first
                    if self._convert_audio_for_pygame(file_path):
                        converted_path = file_path.replace('.wav', '_converted.wav')
                        pygame.mixer.music.load(converted_path)
                        pygame.mixer.music.play()
                        # Clean up converted file after playback
                        self._cleanup_converted_file = converted_path
                    else:
                        raise pygame_err
                else:
                    raise pygame_err
            
            # Start LED control if enabled and available
            led_started = False
            if enable_led_control and self.gpio_controller:
                self._start_led_control_for_file(file_path)
                led_started = True
            
            self._is_playing = True
            
            # Monitor for stop commands during playback
            while pygame.mixer.music.get_busy():
                if self._check_for_stop_command(vad_processor, model):
                    pygame.mixer.music.stop()
                    logger.info("🛑 Audio playback interrupted by stop command")
                    self._is_playing = False
                    
                    # Stop LED control
                    if led_started:
                        self._stop_led_control()
                    
                    return True  # Interrupted
                
                pygame.time.wait(100)
            
            self._is_playing = False
            
            # Stop LED control
            if led_started:
                self._stop_led_control()
            
            # Clean up any converted file
            if hasattr(self, '_cleanup_converted_file'):
                try:
                    if os.path.exists(self._cleanup_converted_file):
                        os.remove(self._cleanup_converted_file)
                        logger.debug(f"Cleaned up converted file: {self._cleanup_converted_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up converted file: {e}")
                finally:
                    delattr(self, '_cleanup_converted_file')
            
            logger.info("✅ Audio playback completed normally")
            return False  # Not interrupted
            
        except Exception as e:
            logger.error(f"Audio playback with interrupt error: {e}")
            self._is_playing = False
            return False
    
    def _start_led_control_for_file(self, file_path: str):
        """Start LED control based on audio file playback"""
        if not self.gpio_controller or not self.gpio_controller.gpio_available:
            return
            
        try:
            # Load audio file for amplitude analysis
            self._load_audio_data(file_path)
            
            # Start envelope following
            self.gpio_controller.start_audio_envelope_following(self._get_current_audio_chunk)
            
            logger.debug("🎵 LED control started for audio playback")
            
        except Exception as e:
            logger.error(f"Failed to start LED control: {e}")
    
    def _stop_led_control(self):
        """Stop LED control"""
        if self.gpio_controller:
            self.gpio_controller.stop_audio_envelope_following()
            logger.debug("🔇 LED control stopped")
    
    def _load_audio_data(self, file_path: str):
        """Load audio file data for LED control"""
        try:
            # Try multiple methods to load audio data
            audio_data = None
            
            # Method 1: Try with wave module (most compatible)
            try:
                with wave.open(file_path, 'rb') as wf:
                    frames = wf.readframes(wf.getnframes())
                    if wf.getsampwidth() == 2:  # 16-bit
                        audio_data = np.frombuffer(frames, dtype=np.int16)
                    elif wf.getsampwidth() == 4:  # 32-bit
                        audio_data = np.frombuffer(frames, dtype=np.int32)
                        audio_data = audio_data.astype(np.int16)  # Convert to 16-bit
                    else:
                        raise ValueError(f"Unsupported sample width: {wf.getsampwidth()}")
                    
                    # Convert to float32 and normalize
                    audio_data = audio_data.astype(np.float32) / 32768.0
                    
                    # Handle stereo by taking left channel
                    if wf.getnchannels() == 2:
                        audio_data = audio_data[::2]
                        
                    logger.debug(f"Loaded audio data with wave module: {len(audio_data)} samples")
                    
            except Exception as wave_error:
                logger.debug(f"Wave module failed: {wave_error}, trying soundfile")
                
                # Method 2: Try with soundfile (if available)
                try:
                    import soundfile as sf
                    audio_data, sample_rate = sf.read(file_path)
                    
                    # Convert to mono if stereo
                    if len(audio_data.shape) > 1:
                        audio_data = audio_data[:, 0]
                    
                    logger.debug(f"Loaded audio data with soundfile: {len(audio_data)} samples")
                    
                except ImportError:
                    logger.debug("soundfile not available, trying pygame")
                except Exception as sf_error:
                    logger.debug(f"soundfile failed: {sf_error}, trying pygame")
                
                # Method 3: Fallback - generate silent data (prevents crashes)
                if audio_data is None:
                    logger.warning(f"Could not load audio data from {file_path}, using silent data")
                    audio_data = np.zeros(1024, dtype=np.float32)
            
            if audio_data is not None:
                with self._audio_lock:
                    self._current_audio_data = audio_data
                    
                logger.debug(f"Audio data loaded successfully: {len(audio_data)} samples")
            else:
                logger.error("Failed to load audio data with any method")
                
        except Exception as e:
            logger.error(f"Failed to load audio data: {e}")
            # Use silent fallback to prevent crashes
            with self._audio_lock:
                self._current_audio_data = np.zeros(1024, dtype=np.float32)
    
    def _get_current_audio_chunk(self) -> Optional[np.ndarray]:
        """Get current audio chunk for LED control with real-time tracking"""
        with self._audio_lock:
            if self._current_audio_data is None or not self._is_playing:
                return None
            
            # Calculate current playback position based on pygame mixer position
            try:
                # Get pygame mixer position (in milliseconds since start)
                pos_ms = pygame.mixer.music.get_pos()
                if pos_ms < 0:  # -1 means not playing
                    return None
                
                # Convert to sample position
                sample_rate = self.config.sample_rate
                pos_samples = int((pos_ms / 1000.0) * sample_rate)
                
                # Return current chunk around playback position
                chunk_size = 1024
                start_pos = max(0, pos_samples - chunk_size // 2)
                end_pos = min(len(self._current_audio_data), start_pos + chunk_size)
                
                if start_pos < len(self._current_audio_data):
                    current_chunk = self._current_audio_data[start_pos:end_pos]
                    logger.debug(f"LED: pos={pos_ms}ms, samples={pos_samples}, chunk_size={len(current_chunk)}")
                    return current_chunk
                    
            except Exception as e:
                logger.debug(f"Error getting playback position: {e}")
            
            # Fallback: return a chunk from the middle
            chunk_size = 1024
            if len(self._current_audio_data) > chunk_size:
                start_pos = len(self._current_audio_data) // 2
                return self._current_audio_data[start_pos:start_pos + chunk_size]
            
            return self._current_audio_data
    
    def _check_for_stop_command(self, vad_processor, model) -> bool:
        """Check for stop command during playback"""
        try:
            # Quick recording to check for stop command
            chunk_size = int(vad_processor.sample_rate * 0.2)  # 200ms
            chunk = sd.rec(chunk_size, samplerate=vad_processor.sample_rate, 
                          channels=1, dtype='float32')
            sd.wait()
            
            # Quick energy check
            energy = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)) * 32767)
            if energy > vad_processor.energy_threshold * 2:
                # Transcribe to check for stop command
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
                        segments, _ = model.transcribe(tmp_file.name, beam_size=1, 
                                                     language="en", vad_filter=False)
                        transcription = " ".join([segment.text for segment in segments]).strip().lower()
                        
                        # Check for stop phrases
                        from .config import STOP_PHRASES
                        for phrase in STOP_PHRASES:
                            if phrase.lower() in transcription:
                                logger.info(f"Stop command detected: '{phrase}' in '{transcription}'")
                                return True
                                
                    except Exception:
                        pass  # Ignore transcription errors during playback
                    finally:
                        if os.path.exists(tmp_file.name):
                            os.unlink(tmp_file.name)
            
            return False
            
        except Exception:
            return False  # Don't interrupt on errors
    
    def _convert_audio_for_pygame(self, file_path: str) -> bool:
        """Convert audio file to pygame-compatible format"""
        try:
            import subprocess
            
            converted_path = file_path.replace('.wav', '_converted.wav')
            
            # Use ffmpeg to convert to standard PCM WAV format
            cmd = [
                'ffmpeg', '-y', '-i', file_path,
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-ar', '22050',          # 22.05kHz sample rate  
                '-ac', '2',              # Stereo
                converted_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Audio converted successfully: {converted_path}")
                return True
            else:
                logger.error(f"Audio conversion failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Audio conversion timeout")
            return False
        except FileNotFoundError:
            logger.error("ffmpeg not found for audio conversion")
            return False
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return False
    
    def test_led_functionality(self):
        """Test LED functionality"""
        if not self.gpio_controller:
            logger.warning("GPIO controller not available for testing")
            return
            
        logger.info("🧪 Testing LED functionality...")
        self.gpio_controller.test_led_sequence(duration=5.0)
    
    def get_status(self) -> dict:
        """Get audio manager status"""
        gpio_status = {}
        if self.gpio_controller:
            gpio_status = self.gpio_controller.get_status()
        
        return {
            "audio_initialized": pygame.mixer.get_init() is not None,
            "is_playing": self._is_playing,
            "config": {
                "sample_rate": self.config.sample_rate,
                "channels": self.config.channels,
                "buffer_size": self.config.buffer_size
            },
            "gpio": gpio_status
        }
    
    def cleanup(self):
        """Clean up audio resources"""
        logger.info("🧹 Cleaning up audio manager...")
        
        # Stop any ongoing playback
        try:
            pygame.mixer.music.stop()
        except:
            pass
        
        # Clean up GPIO
        if self.gpio_controller:
            self.gpio_controller.cleanup()
        
        # Clean up pygame
        try:
            pygame.mixer.quit()
        except:
            pass
        
        logger.info("✅ Audio manager cleanup completed")

# Global audio manager instance
_audio_manager: Optional[AudioManager] = None

def get_audio_manager() -> AudioManager:
    """Get the global audio manager instance"""
    global _audio_manager
    
    if _audio_manager is None:
        config = AudioConfig()
        _audio_manager = AudioManager(config)
    
    return _audio_manager

def cleanup_audio_manager():
    """Clean up global audio manager"""
    global _audio_manager
    
    if _audio_manager:
        _audio_manager.cleanup()
        _audio_manager = None
