#!/usr/bin/env python3
"""
Edge TTS + Demonic Effects Provider for Evil Assistant
Combines Microsoft's high-quality Edge TTS with demonic audio processing
"""

import asyncio
import os
import tempfile
import subprocess
import logging
from typing import Optional, List

from ..base import TTSProvider
from ..config import TTSConfig

logger = logging.getLogger(__name__)

class EdgeDemonicProvider(TTSProvider):
    """High-quality demonic TTS using Microsoft Edge TTS + SoX effects"""
    
    def __init__(self, config: TTSConfig):
        super().__init__(config)
        self.provider_name = "EdgeDemonic"
        
        # Default to best masculine voice
        self.voice_name = "en-GB-RyanNeural"  # Deep British voice
        
        # Check dependencies
        self._check_dependencies()
    
    def _check_dependencies(self) -> bool:
        """Check if Edge TTS and SoX are available"""
        try:
            import edge_tts
            self.edge_available = True
            logger.info("Edge TTS available for high-quality synthesis")
        except ImportError:
            logger.warning("Edge TTS not available. Install with: pip install edge-tts")
            self.edge_available = False
        
        # Check SoX for demonic effects
        try:
            result = subprocess.run(['sox', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            self.sox_available = result.returncode == 0
            if self.sox_available:
                logger.info("SoX available for demonic effects")
            else:
                logger.warning("SoX not available. Install with: brew install sox")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.sox_available = False
            logger.warning("SoX not found - demonic effects will be limited")
        
        return self.edge_available

    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.edge_available

    def synthesize(self, text: str, output_file: str) -> bool:
        """Synthesize text using Edge TTS with demonic effects"""
        if not self.is_available():
            logger.error("Edge TTS not available")
            return False
        
        try:
            # Handle asyncio event loop properly
            try:
                # Try to get existing loop
                loop = asyncio.get_running_loop()
                # If we're in an existing loop, create a new thread
                import concurrent.futures
                import threading
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self._synthesize_async(text, output_file))
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result(timeout=30)
                    
            except RuntimeError:
                # No running loop, can use asyncio.run
                return asyncio.run(self._synthesize_async(text, output_file))
                
        except Exception as e:
            logger.error(f"Edge TTS synthesis failed: {e}")
            return False

    async def _synthesize_async(self, text: str, output_file: str) -> bool:
        """Async synthesis with Edge TTS"""
        try:
            import edge_tts
            
            # Generate high-quality base voice
            communicate = edge_tts.Communicate(text, self.voice_name)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_mp3:
                base_file = tmp_mp3.name
            
            try:
                await communicate.save(base_file)
                logger.debug(f"Edge TTS saved to {base_file}")
                
                # Apply demonic effects if SoX is available
                if self.sox_available:
                    success = self._apply_demonic_effects(base_file, output_file)
                else:
                    # Fallback: basic conversion without effects
                    success = self._convert_to_wav(base_file, output_file)
                
                return success
                
            finally:
                # Cleanup temp file
                if os.path.exists(base_file):
                    os.unlink(base_file)
                    
        except Exception as e:
            logger.error(f"Edge TTS async synthesis failed: {e}")
            return False

    def _apply_demonic_effects(self, input_file: str, output_file: str) -> bool:
        """Apply demonic effects using SoX"""
        try:
            # Get effect profile based on configuration
            effect_profile = self._get_effect_profile()
            
            # Check if input is MP3 and SoX doesn't support it
            if input_file.endswith('.mp3'):
                # First convert MP3 to WAV, then apply effects
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_wav:
                    intermediate_wav = tmp_wav.name
                
                try:
                    # Convert MP3 to WAV first using basic method
                    if not self._convert_mp3_to_wav_basic(input_file, intermediate_wav):
                        return self._convert_to_wav(input_file, output_file)
                    
                    # Now apply effects to the WAV file
                    sox_cmd = ['sox', intermediate_wav, output_file] + effect_profile
                    result = subprocess.run(sox_cmd, capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        logger.debug("Demonic effects applied successfully to Edge TTS voice")
                        return True
                    else:
                        logger.error(f"SoX effects failed: {result.stderr}")
                        # Fallback to basic conversion
                        return self._convert_to_wav(input_file, output_file)
                
                finally:
                    # Cleanup intermediate file
                    if os.path.exists(intermediate_wav):
                        os.unlink(intermediate_wav)
            else:
                # Direct SoX processing for WAV files
                sox_cmd = ['sox', input_file, output_file] + effect_profile
                result = subprocess.run(sox_cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    logger.debug("Demonic effects applied successfully to Edge TTS voice")
                    return True
                else:
                    logger.error(f"SoX effects failed: {result.stderr}")
                    return self._convert_to_wav(input_file, output_file)
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.error(f"SoX processing error: {e}")
            return self._convert_to_wav(input_file, output_file)

    def _get_effect_profile(self) -> List[str]:
        """Get demonic effect profile optimized for Edge TTS quality"""
        
        # Demonic profiles optimized for high-quality Edge TTS base
        profiles = {
            "natural_demon": [
                'pitch', '-400',      # Deep masculine pitch
                'bass', '+20',        # Enhanced bass
                'treble', '-8',       # Darker tone
                'vol', '0.9'          # Volume compensation
            ],
            
            "deep_overlord": [
                'pitch', '-500',      # Very deep pitch
                'bass', '+25',        # Strong bass
                'treble', '-12',      # Dark tone
                'reverb', '30',       # Light reverb to maintain clarity
                'vol', '0.85'         # Volume control
            ],
            
            "ancient_evil": [
                'pitch', '-450',      # Deep but clear
                'bass', '+22',        # Heavy bass
                'treble', '-10',      # Darker sound
                'reverb', '40',       # Moderate reverb
                'chorus', '0.6', '0.9', '40', '0.25', '0.4', '2', '-s',  # Choir effect
                'vol', '0.8'          # Volume control
            ],
            
            "nightmare_whisper": [
                'pitch', '-550',      # Ultra deep
                'bass', '+30',        # Maximum bass
                'treble', '-15',      # Very dark
                'reverb', '60',       # Heavy reverb
                'echo', '0.8', '0.88', '50', '0.3',  # Echo effect
                'vol', '0.75'         # Lower volume for whisper
            ],
            
            "balanced_demon": [   # Default: best balance
                'pitch', '-450',      # Good depth
                'bass', '+20',        # Strong bass
                'treble', '-8',       # Slightly darker
                'reverb', '25',       # Light reverb for naturalness
                'vol', '0.9'          # Good volume
            ],
            
            "clarity_beast": [     # WINNER: 4/5 overall, 4/5 clarity, 3/5 monster
                'pitch', '-480',      # Optimal depth for monstrosity + clarity
                'bass', '+26',        # Enhanced bass without muddiness
                'treble', '-8',       # Darkened tone
                'overdrive', '6',     # Controlled growl for monster factor
                'vol', '0.92'         # High volume compensation
            ],
            
            "articulate_demon": [ # RUNNER-UP: 4/5 overall, 4/5 clarity, 3/5 monster
                'pitch', '-450',      # Moderate depth for articulation
                'bass', '+24',        # Good bass
                'treble', '-4',       # Minimal treble reduction
                'overdrive', '5',     # Light overdrive
                'tremolo', '8',       # Unnatural tremolo for demon effect
                'vol', '0.9'          # Good volume
            ]
        }
        
        # Determine which profile to use
        if self.config.effects and len(self.config.effects) > 1:
            # Custom effects provided
            return self.config.effects
        
        # Check for specific profile request
        if self.config.effects and len(self.config.effects) == 1:
            profile_name = self.config.effects[0]
            if profile_name in profiles:
                logger.info(f"Using Edge demonic profile: {profile_name}")
                return profiles[profile_name]
        
        # Default to balanced demon (maintains Edge TTS quality while adding depth)
        logger.info("Using default balanced_demon profile for Edge TTS")
        return profiles["balanced_demon"]

    def _convert_mp3_to_wav_basic(self, input_file: str, output_file: str) -> bool:
        """Convert MP3 to WAV using available tools"""
        try:
            # Try ffmpeg first (most reliable)
            try:
                ffmpeg_cmd = ['ffmpeg', '-i', input_file, '-acodec', 'pcm_s16le', '-ar', '22050', '-y', output_file]
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    logger.debug("MP3 to WAV conversion successful with ffmpeg")
                    return True
            except FileNotFoundError:
                pass
            
            # Try pygame for MP3 conversion
            try:
                import pygame
                pygame.mixer.init()
                sound = pygame.mixer.Sound(input_file)
                pygame.sndarray.array(sound)  # Convert to array
                # This is basic but may work for simple conversion
                import shutil
                shutil.copy2(input_file, output_file)
                logger.debug("MP3 conversion attempted with pygame fallback")
                return True
            except Exception:
                pass
            
            # Final fallback: direct copy (Edge TTS MP3 might be compatible)
            import shutil
            shutil.copy2(input_file, output_file)
            logger.warning("Using direct file copy for MP3 conversion")
            return True
            
        except Exception as e:
            logger.error(f"MP3 to WAV conversion failed: {e}")
            return False

    def _convert_to_wav(self, input_file: str, output_file: str) -> bool:
        """Fallback: basic MP3 to WAV conversion"""
        try:
            if self.sox_available:
                sox_cmd = ['sox', input_file, output_file]
                result = subprocess.run(sox_cmd, capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    logger.debug("Basic MP3 to WAV conversion successful")
                    return True
            
            # Use the basic MP3 converter
            return self._convert_mp3_to_wav_basic(input_file, output_file)
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return False

    def get_voice_info(self) -> dict:
        """Get information about the current voice"""
        return {
            "provider": "EdgeDemonic",
            "voice_name": self.voice_name,
            "quality": "High (Microsoft Edge TTS)",
            "naturalness": "Excellent",
            "demonic_effects": "Yes (SoX processing)",
            "cost": "Free",
            "speed": "Fast"
        }

    def set_voice(self, voice_name: str) -> bool:
        """Set the Edge TTS voice to use"""
        # List of good masculine voices for demonic character
        masculine_voices = [
            "en-GB-RyanNeural",           # Deep British (default)
            "en-US-GuyNeural",            # American masculine
            "en-US-DavisNeural",          # Deep American
            "en-US-EricNeural",           # Strong American
            "en-AU-WilliamNeural",        # Australian masculine
            "en-CA-LiamNeural"            # Canadian masculine
        ]
        
        if voice_name in masculine_voices:
            self.voice_name = voice_name
            logger.info(f"Edge TTS voice set to: {voice_name}")
            return True
        else:
            logger.warning(f"Voice {voice_name} not in masculine voice list")
            return False
