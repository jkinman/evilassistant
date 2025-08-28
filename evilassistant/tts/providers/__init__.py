"""
TTS Provider Implementations

Individual provider classes for different TTS engines:
- EspeakProvider: Local espeak synthesis (always available fallback)
- ElevenLabsProvider: Cloud-based premium TTS (requires API key)  
- PiperProvider: Local neural TTS (high quality, free)
"""

from .espeak import EspeakProvider
from .elevenlabs import ElevenLabsProvider
from .piper import PiperProvider

__all__ = [
    'EspeakProvider',
    'ElevenLabsProvider', 
    'PiperProvider'
]
