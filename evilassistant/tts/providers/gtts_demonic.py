"""
gTTS + Sox Demonic Voice Provider for Evil Assistant
Fast, free, and effective demonic voice synthesis
"""

import os
import tempfile
import subprocess
import logging
from typing import Optional

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
            
            # Generate base TTS
            tts = gTTS(text=text, lang='en', slow=False)
            
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
        """Apply demonic effects using sox"""
        try:
            # Demonic effect chain
            sox_cmd = [
                'sox', input_file, output_file,
                'pitch', '-300',      # Much lower pitch
                'reverb', '40',       # Reverb for depth
                'bass', '+15',        # Heavy bass boost
                'treble', '-8',       # Reduce treble for darker sound
                'vol', '0.75',        # Prevent clipping
                'overdrive', '5'      # Slight distortion
            ]
            
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
