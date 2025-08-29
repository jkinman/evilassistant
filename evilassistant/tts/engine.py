#!/usr/bin/env python3
"""
Main TTS Engine with fallback strategy
"""

import logging
from typing import List, Optional, Tuple
from .base import TTSProvider
from .providers import EspeakProvider, ElevenLabsProvider, PiperProvider
from .providers.gtts_demonic import GTTSDemonicProvider
from .config import EspeakConfig, ElevenLabsConfig, PiperConfig, TTSConfig

logger = logging.getLogger(__name__)

class TTSEngine:
    """Main TTS engine with fallback strategy"""
    
    def __init__(self):
        self.providers: List[Tuple[int, TTSProvider]] = []
        self.current_provider: Optional[TTSProvider] = None
    
    def add_provider(self, provider_name: str, config: TTSConfig, priority: int = 0):
        """Add a TTS provider by name with priority (lower = higher priority)"""
        if provider_name == "gtts_demonic":
            provider = GTTSDemonicProvider(config)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        self.providers.append((priority, provider))
        self.providers.sort(key=lambda x: x[0])  # Sort by priority
    
    def add_provider_instance(self, provider: TTSProvider, priority: int = 0):
        """Add a TTS provider instance with priority (lower = higher priority)"""
        self.providers.append((priority, provider))
        self.providers.sort(key=lambda x: x[0])  # Sort by priority
    
    def configure_espeak(self, config: EspeakConfig) -> 'TTSEngine':
        """Configure espeak provider"""
        self.add_provider_instance(EspeakProvider(config), priority=2)
        return self
    
    def configure_edge_demonic(self, config: TTSConfig) -> 'TTSEngine':
        """Configure Edge TTS + demonic effects provider"""
        from .providers.edge_demonic import EdgeDemonicProvider
        self.add_provider_instance(EdgeDemonicProvider(config), priority=0)
        return self
    
    def configure_elevenlabs(self, config: ElevenLabsConfig) -> 'TTSEngine':
        """Configure ElevenLabs provider"""  
        self.add_provider_instance(ElevenLabsProvider(config), priority=0)
        return self
    
    def configure_piper(self, config: PiperConfig) -> 'TTSEngine':
        """Configure Piper TTS provider"""
        self.add_provider_instance(PiperProvider(config), priority=1)
        return self
    
    def synthesize(self, text: str, output_file: str) -> bool:
        """Synthesize text using available providers with fallback"""
        logger.info(f"🎭 TTS SYNTHESIS REQUEST: '{text[:50]}...' -> {output_file}")
        print(f"🎭 Synthesizing: '{text[:50]}...'")
        
        for priority, provider in self.providers:
            provider_name = provider.__class__.__name__
            if provider.is_available():
                logger.info(f"🔄 TRYING PROVIDER: {provider_name} (Priority {priority})")
                print(f"🔄 Trying TTS provider: {provider_name}")
                
                if provider.synthesize(text, output_file):
                    self.current_provider = provider
                    logger.info(f"✅ TTS SUCCESS: {provider_name} completed synthesis")
                    print(f"✅ TTS completed by: {provider_name}")
                    return True
                else:
                    logger.warning(f"❌ TTS FAILED: {provider_name} failed, trying next...")
                    print(f"❌ TTS failed: {provider_name}, trying next...")
            else:
                logger.debug(f"⏭️  SKIPPING: {provider_name} not available")
        
        logger.error("💥 ALL TTS PROVIDERS FAILED")
        print("💥 All TTS providers failed!")
        return False
    
    def get_current_provider(self) -> Optional[str]:
        """Get name of currently used provider"""
        if self.current_provider:
            return self.current_provider.__class__.__name__
        return None
