"""
gTTS + Sox Demonic Voice Provider for Evil Assistant
Fast, free, and effective demonic voice synthesis
"""

import os
import tempfile
import subprocess
import logging
from typing import Optional, List

from ..base import TTSProvider
from ..config import TTSConfig

logger = logging.getLogger(__name__)

class GTTSDemonicProvider(TTSProvider):
    """Fast demonic TTS using Google TTS + Sox audio effects"""
    
    def __init__(self, config: TTSConfig):
        super().__init__(config)
        self.provider_name = "GTTSDemonic"
        
        # Check dependencies
        self._check_dependencies()
    
    def _check_dependencies(self) -> bool:
        """Check if gTTS and sox are available"""
        try:
            import gtts
            self.gtts_available = True
        except ImportError:
            logger.warning("gTTS not available. Install with: pip install gtts")
            self.gtts_available = False
        
        # Check sox
        try:
            result = subprocess.run(['sox', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            self.sox_available = result.returncode == 0
            if self.sox_available:
                logger.info("Sox available for audio effects")
            else:
                logger.warning("Sox not available. Install with: brew install sox")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.sox_available = False
            logger.warning("Sox not found - demonic effects will be limited")
        
        return self.gtts_available
    
    def is_available(self) -> bool:
        """Check if this provider can be used"""
        return self.gtts_available
    
    def synthesize(self, text: str, output_file: str) -> bool:
        """Synthesize demonic voice using gTTS + Sox effects"""
        if not self.gtts_available:
            logger.error("gTTS not available")
            return False
        
        try:
            from gtts import gTTS
            
            # Generate base TTS with masculine voice configuration
            # Use slow=False for speed, we'll handle depth with pitch effects
            # Try different TLD domains for voice variation (some sound more masculine)
            tts = gTTS(text=text, lang='en', slow=False, tld='com.au')  # Australian TLD often deeper
            
            # Save to temporary MP3 file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_mp3:
                base_file = tmp_mp3.name
            
            try:
                tts.save(base_file)
                logger.debug(f"Base TTS saved to {base_file}")
                
                # Apply demonic effects if sox is available
                if self.sox_available:
                    success = self._apply_demonic_effects(base_file, output_file)
                else:
                    # Fallback: convert MP3 to WAV without effects
                    success = self._convert_mp3_to_wav(base_file, output_file)
                
                return success
                
            finally:
                # Cleanup base file
                if os.path.exists(base_file):
                    os.unlink(base_file)
        
        except Exception as e:
            logger.error(f"gTTS synthesis failed: {e}")
            return False
    
    def _apply_demonic_effects(self, input_file: str, output_file: str) -> bool:
        """Apply demonic effects using sox with configurable profiles"""
        try:
            # Get effect profile from config or use default
            effect_profile = self._get_effect_profile()
            
            # Build sox command with selected profile
            sox_cmd = ['sox', input_file, output_file] + effect_profile
            
            result = subprocess.run(sox_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.debug("Demonic effects applied successfully")
                return True
            else:
                logger.error(f"Sox effects failed: {result.stderr}")
                # Fallback to basic conversion
                return self._convert_mp3_to_wav(input_file, output_file)
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.error(f"Sox processing error: {e}")
            return self._convert_mp3_to_wav(input_file, output_file)
    
    def _get_effect_profile(self) -> List[str]:
        """Get demonic effect profile based on configuration"""
        
        # Available demonic voice profiles - SPEED OPTIMIZED
        profiles = {
            "fast_demon": [
                'pitch', '-600',      # Single deep pitch for speed
                'bass', '+20',        # Moderate bass boost
                'vol', '0.9'          # Higher volume
            ],
            
            "balanced_demon": [
                'pitch', '-700',      # Deep pitch, single pass
                'bass', '+25',        # Strong bass boost
                'treble', '-10',      # Reduce treble for darker sound
                'vol', '0.85'         # Volume control
            ],
            
            "premium_demon": [
                'pitch', '-300',      # First moderate shift
                'pitch', '-300',      # Second shift (compound)
                'pitch', '-300',      # Third shift (triple effect)
                'reverb', '50',       # Heavy reverb
                'bass', '+30',        # Strong bass
                'treble', '-12',      # Dark sound
                'vol', '0.8',         # Volume control
                'overdrive', '3'      # Light distortion
            ],
            
            "nightmare_whisper": [
                'pitch', '-500',      # Deep masculine whisper
                'pitch', '-300',      # Additional depth
                'reverb', '80',       # Maximum reverb for otherworldly effect
                'bass', '+35',        # Extreme bass
                'treble', '-20',      # Very dark masculine tone
                'echo', '0.8', '0.88', '60', '0.3',  # Echo effect
                'vol', '0.7',         # Lower volume for whisper effect
                'overdrive', '5'      # Growl
            ],
            
            "ancient_evil": [
                'pitch', '-350',      # Moderate but clear depth
                'pitch', '-350',      # Double shift
                'reverb', '60',       # Cathedral reverb
                'bass', '+28',        # Heavy masculine bass
                'treble', '-10',      # Dark tone
                'chorus', '0.6', '0.9', '50', '0.25', '0.4', '2', '-s',  # Choir effect
                'vol', '0.8'          # Volume control
            ],
            
            "brutal_overlord": [   # Experimental: Maximum depth
                'pitch', '-600',      # Deep base
                'pitch', '-600',      # Double deep
                'reverb', '40',       # Moderate reverb for clarity
                'bass', '+40',        # Maximum bass
                'treble', '-25',      # Eliminate high frequencies
                'vol', '0.9',         # Compensate for deep pitch
                'overdrive', '8'      # Heavy distortion
            ],
            
            "demon_lord": [        # NEW: Balanced clarity and depth
                'pitch', '-350',      # Moderate depth
                'pitch', '-250',      # Additional depth
                'reverb', '30',       # Light reverb for clarity
                'bass', '+25',        # Strong bass
                'treble', '-8',       # Slightly darker tone
                'vol', '0.85'         # Good volume
            ],
            
            "experimental_deep": [ # SPEED OPTIMIZED: Single pass deep
                'pitch', '-800',      # Single deep pitch shift for speed
                'bass', '+30',        # Strong bass boost
                'vol', '0.9'          # Higher volume to compensate
            ],
            
            "lightning_demon": [   # NEW: Maximum speed, good depth
                'pitch', '-650',      # Deep but fast
                'bass', '+25',        # Bass boost
                'vol', '0.9'          # Volume
            ],
            
            "speed_overlord": [    # NEW: Optimized for real-time
                'pitch', '-750',      # Very deep, single pass
                'bass', '+30',        # Strong masculine bass
                'treble', '-15',      # Dark tone
                'vol', '0.9'          # Volume compensation
            ]
        }
        
        # Determine which profile to use
        # Check if custom effects are provided
        if self.config.effects and len(self.config.effects) > 1:
            # Custom effects provided
            return self.config.effects
        
        # Check for specific profile request in effects
        if self.config.effects and len(self.config.effects) == 1:
            profile_name = self.config.effects[0]
            if profile_name in profiles:
                logger.info(f"Using demonic profile: {profile_name}")
                return profiles[profile_name]
        
        # Default to balanced demon (good quality + speed)
        logger.info("Using default balanced_demon profile")
        return profiles["balanced_demon"]
    
    def _convert_mp3_to_wav(self, input_file: str, output_file: str) -> bool:
        """Fallback: simple MP3 to WAV conversion"""
        try:
            # Try sox for basic conversion
            if self.sox_available:
                sox_cmd = ['sox', input_file, output_file]
                result = subprocess.run(sox_cmd, capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    logger.debug("Basic MP3 to WAV conversion successful")
                    return True
            
            # Final fallback: use pygame/librosa if available
            try:
                import librosa
                import soundfile as sf
                
                audio, sr = librosa.load(input_file, sr=22050)
                sf.write(output_file, audio, sr)
                logger.debug("Conversion using librosa successful")
                return True
                
            except ImportError:
                logger.error("No audio conversion method available")
                return False
                
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            return False
    
    def get_voice_info(self) -> dict:
        """Get information about this voice provider"""
        return {
            "provider": self.provider_name,
            "type": "cloud_plus_effects",
            "language": "en",
            "voice_style": "demonic_deep",
            "effects": "pitch_shift, reverb, bass_boost, distortion",
            "latency": "medium",  # Network + processing time
            "quality": "good",
            "cost": "free",
            "dependencies": {
                "gtts": self.gtts_available,
                "sox": self.sox_available
            }
        }

# Provider factory function
def create_provider(config: TTSConfig) -> GTTSDemonicProvider:
    """Create and return a GTTSDemonic provider instance"""
    return GTTSDemonicProvider(config)
