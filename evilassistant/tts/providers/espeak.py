#!/usr/bin/env python3
"""
espeak TTS Provider

Local text-to-speech using espeak - lightweight and always available fallback.
Supports configurable voice parameters and audio effects via sox.
"""

import os
import subprocess
import tempfile
import logging
from ..base import TTSProvider
from ..config import EspeakConfig

logger = logging.getLogger(__name__)

class EspeakProvider(TTSProvider):
    """espeak TTS provider with configurable voice settings"""
    
    def __init__(self, config: EspeakConfig):
        super().__init__(config)
        self.espeak_config = config
    
    def is_available(self) -> bool:
        """Check if espeak is installed"""
        try:
            subprocess.run(['espeak', '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def synthesize(self, text: str, output_file: str) -> bool:
        """Synthesize using espeak with configuration"""
        if not self.is_available():
            logger.error("espeak not available")
            return False
            
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_raw:
            try:
                # Build espeak command from config
                espeak_cmd = [
                    'espeak',
                    '-v', self.espeak_config.voice_id,
                    '-s', str(self.espeak_config.speed),
                    '-p', str(self.espeak_config.pitch),
                    '-a', str(self.espeak_config.amplitude),
                    '-g', str(self.espeak_config.word_gap),
                    '-z',  # No final sentence pause
                    '-w', tmp_raw.name,
                    text
                ]
                
                logger.debug(f"espeak command: {' '.join(espeak_cmd)}")
                subprocess.run(espeak_cmd, check=True, capture_output=True)
                
                # Apply effects
                if self.config.effects:
                    return self.apply_effects(tmp_raw.name, output_file)
                else:
                    subprocess.run(['cp', tmp_raw.name, output_file], check=True)
                    return True
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"espeak synthesis failed: {e}")
                return False
            finally:
                if os.path.exists(tmp_raw.name):
                    os.unlink(tmp_raw.name)
