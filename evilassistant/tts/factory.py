#!/usr/bin/env python3
"""
Factory functions for creating configured TTS engines
"""

import os
from .engine import TTSEngine
from .config import VOICE_PROFILES, EspeakConfig, PiperConfig

def create_configured_engine(profile_name: str = "piper_ryan_demonic") -> TTSEngine:
    """Create a pre-configured TTS engine with quality prioritization"""
    engine = TTSEngine()
    
    # Priority 0: ElevenLabs (best quality, but costs money)
    if "ELEVENLABS_API_KEY" in os.environ:
        engine.configure_elevenlabs(VOICE_PROFILES["elevenlabs_premium"])
    
    # Priority 1: Piper (high quality neural voices, free)
    if profile_name in VOICE_PROFILES:
        config = VOICE_PROFILES[profile_name]
        if isinstance(config, PiperConfig):
            engine.configure_piper(config)
    
    # Priority 2: espeak (fallback, always available)
    # Add a basic espeak fallback for any profile
    fallback_espeak = EspeakConfig(
        voice_id="en",
        speed=110,
        pitch=12,
        effects=["pitch -600", "bass +8", "vol 0.7"]
    )
    engine.configure_espeak(fallback_espeak)
    
    return engine
