#!/usr/bin/env python3
"""
Piper TTS Provider

Local neural text-to-speech using Piper models.
Provides high-quality voice synthesis with configurable speed and effects.
Requires Piper models to be downloaded locally.
"""

import os
import subprocess
import tempfile
import logging
from ..base import TTSProvider
from ..config import PiperConfig

logger = logging.getLogger(__name__)

class PiperProvider(TTSProvider):
    """Piper TTS provider with high-quality neural voices"""
    
    def __init__(self, config: PiperConfig):
        super().__init__(config)
        self.piper_config = config
    
    def is_available(self) -> bool:
        """Check if Piper and models are available"""
        try:
            import piper
            import os
            return (os.path.exists(self.piper_config.model_path) and 
                   os.path.exists(self.piper_config.config_path))
        except ImportError:
            return False
    
    def synthesize(self, text: str, output_file: str) -> bool:
        """Synthesize using Piper TTS"""
        if not self.is_available():
            logger.error("Piper TTS not available or models missing")
            return False
            
        try:
            from piper import PiperVoice
            from piper.config import SynthesisConfig
            import wave
            import tempfile
            
            # Load voice model
            voice = PiperVoice.load(
                self.piper_config.model_path,
                config_path=self.piper_config.config_path,
                use_cuda=False  # Use CPU for compatibility
            )
            
            # Create synthesis config with speed adjustment
            syn_config = SynthesisConfig(
                length_scale=1.0 / self.piper_config.speed,
                speaker_id=self.piper_config.speaker_id
            )
            
            # Generate audio to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_raw:
                with wave.open(tmp_raw.name, 'wb') as wav_file:
                    voice.synthesize_wav(text, wav_file, syn_config)
                
                # Apply effects if specified
                if self.config.effects:
                    success = self.apply_effects(tmp_raw.name, output_file)
                else:
                    subprocess.run(['cp', tmp_raw.name, output_file], check=True)
                    success = True
                
                # Cleanup
                if os.path.exists(tmp_raw.name):
                    os.unlink(tmp_raw.name)
                
                return success
                
        except Exception as e:
            logger.error(f"Piper synthesis failed: {e}")
            return False
