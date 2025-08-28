"""
TTS (Text-to-Speech) Engine Package

Provides configurable, extensible text-to-speech synthesis with multiple providers:
- ElevenLabs (premium quality, cloud-based)
- Piper (high-quality neural voices, local)
- espeak (lightweight fallback, local)
"""

from .engine import TTSEngine
from .config import (
    VoiceConfig, 
    EspeakConfig, 
    ElevenLabsConfig, 
    PiperConfig,
    VOICE_PROFILES
)
from .providers import EspeakProvider, ElevenLabsProvider, PiperProvider
from .factory import create_configured_engine

__all__ = [
    'TTSEngine',
    'VoiceConfig',
    'EspeakConfig', 
    'ElevenLabsConfig',
    'PiperConfig',
    'VOICE_PROFILES',
    'EspeakProvider',
    'ElevenLabsProvider', 
    'PiperProvider',
    'create_configured_engine'
]
