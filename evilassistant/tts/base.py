#!/usr/bin/env python3
"""
Base classes and interfaces for TTS providers
"""

import os
import subprocess
import logging
from abc import ABC, abstractmethod
from .config import VoiceConfig

logger = logging.getLogger(__name__)

class TTSProvider(ABC):
    """Abstract base class for TTS providers"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        
    @abstractmethod
    def synthesize(self, text: str, output_file: str) -> bool:
        """Synthesize text to audio file"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available/configured"""
        pass
    
    def apply_effects(self, input_file: str, output_file: str) -> bool:
        """Apply audio effects using sox"""
        if not self.config.effects:
            # Just copy file if no effects
            subprocess.run(['cp', input_file, output_file], check=True)
            return True
            
        try:
            # Build sox command properly from effects list
            effects_flat = []
            for effect in self.config.effects:
                effects_flat.extend(effect.split())
            
            sox_cmd = ['sox', input_file, output_file] + effects_flat
            subprocess.run(sox_cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Sox effects failed: {e}")
            return False
