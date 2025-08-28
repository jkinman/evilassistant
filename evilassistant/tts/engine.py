#!/usr/bin/env python3
"""
Main TTS Engine with fallback strategy
"""

import logging
from typing import List, Optional, Tuple
from .base import TTSProvider
from .providers import EspeakProvider, ElevenLabsProvider, PiperProvider
from .config import EspeakConfig, ElevenLabsConfig, PiperConfig

logger = logging.getLogger(__name__)

class TTSEngine:
    """Main TTS engine with fallback strategy"""
    
    def __init__(self):
        self.providers: List[Tuple[int, TTSProvider]] = []
        self.current_provider: Optional[TTSProvider] = None
    
    def add_provider(self, provider: TTSProvider, priority: int = 0):
        """Add a TTS provider with priority (lower = higher priority)"""
        self.providers.append((priority, provider))
        self.providers.sort(key=lambda x: x[0])  # Sort by priority
    
    def configure_espeak(self, config: EspeakConfig) -> 'TTSEngine':
        """Configure espeak provider"""
        self.add_provider(EspeakProvider(config), priority=2)
        return self
    
    def configure_elevenlabs(self, config: ElevenLabsConfig) -> 'TTSEngine':
        """Configure ElevenLabs provider"""  
        self.add_provider(ElevenLabsProvider(config), priority=0)
        return self
    
    def configure_piper(self, config: PiperConfig) -> 'TTSEngine':
        """Configure Piper TTS provider"""
        self.add_provider(PiperProvider(config), priority=1)
        return self
    
    def synthesize(self, text: str, output_file: str) -> bool:
        """Synthesize text using available providers with fallback"""
        for priority, provider in self.providers:
            if provider.is_available():
                logger.info(f"Trying {provider.__class__.__name__}")
                if provider.synthesize(text, output_file):
                    self.current_provider = provider
                    return True
                else:
                    logger.warning(f"{provider.__class__.__name__} failed, trying next...")
        
        logger.error("All TTS providers failed")
        return False
    
    def get_current_provider(self) -> Optional[str]:
        """Get name of currently used provider"""
        if self.current_provider:
            return self.current_provider.__class__.__name__
        return None
