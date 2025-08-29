#!/usr/bin/env python3
"""
Factory functions for creating configured TTS engines
"""

import os
from .engine import TTSEngine
from .config import VOICE_PROFILES, EspeakConfig, PiperConfig, TTSConfig

def create_configured_engine(profile_name: str = "piper_ryan_demonic") -> TTSEngine:
    """Create a pre-configured TTS engine with quality prioritization"""
    engine = TTSEngine()
    
    # Priority 0: ElevenLabs (best quality, but costs money)
    if "ELEVENLABS_API_KEY" in os.environ:
        engine.configure_elevenlabs(VOICE_PROFILES["elevenlabs_premium"])
    
    # Priority 1: gTTS Demonic (fast, free, proven demonic voice)
    gtts_config = TTSConfig(effects=["demonic_transformation"])
    engine.add_provider("gtts_demonic", gtts_config)
    
    # Priority 2: Piper (high quality neural voices, free)
    if profile_name in VOICE_PROFILES:
        config = VOICE_PROFILES[profile_name]
        if isinstance(config, PiperConfig):
            engine.configure_piper(config)
    
    # Priority 3: espeak (fallback, always available)
    # Add a basic espeak fallback for any profile
    fallback_espeak = EspeakConfig(
        voice_id="en",
        speed=110,
        pitch=12,
        effects=["pitch -600", "bass +8", "vol 0.7"]
    )
    engine.configure_espeak(fallback_espeak)
    
    return engine

def create_demonic_engine() -> TTSEngine:
    """Create a TTS engine optimized for demonic voice synthesis"""
    engine = TTSEngine()
    
    # Add gTTS Demonic as primary provider
    gtts_config = TTSConfig(effects=["demonic_transformation"])
    engine.add_provider("gtts_demonic", gtts_config)
    
    # Add fallback espeak with heavy demonic effects
    demonic_espeak = EspeakConfig(
        voice_id="en",
        speed=90,
        pitch=8,
        effects=["pitch -800", "bass +20", "overdrive 8", "vol 0.6"]
    )
    engine.configure_espeak(demonic_espeak)
    
    return engine
