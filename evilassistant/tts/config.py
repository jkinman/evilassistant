#!/usr/bin/env python3
"""
TTS Configuration Classes and Voice Profiles
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class TTSConfig:
    """Generic TTS configuration"""
    effects: List[str] = field(default_factory=list)
    extra_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VoiceConfig:
    """Base configuration for voice synthesis"""
    voice_id: str = "en"
    speed: int = 120
    pitch: int = 15
    volume: float = 0.8
    effects: List[str] = field(default_factory=list)
    extra_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EspeakConfig(VoiceConfig):
    """espeak-specific configuration"""
    voice_id: str = "en"
    speed: int = 120  # words per minute
    pitch: int = 15   # 0-99, lower = deeper
    volume: float = 0.8
    effects: List[str] = field(default_factory=lambda: ["pitch -600", "bass +8"])
    
    # espeak-specific
    amplitude: int = 100  # 0-200
    word_gap: int = 0     # milliseconds between words
    sentence_gap: int = 0 # milliseconds between sentences

@dataclass
class ElevenLabsConfig(VoiceConfig):
    """ElevenLabs-specific configuration"""
    voice_id: str = "cPoqAvGWCPfCfyPMwe4z"
    model_id: str = "eleven_multilingual_v2"
    stability: float = 0.3
    similarity_boost: float = 0.2
    style: float = 0.6
    use_speaker_boost: bool = False
    speed: float = 1.2
    effects: List[str] = field(default_factory=lambda: ["vol 0.1", "fade 0.05"])

@dataclass
class PiperConfig(VoiceConfig):
    """Piper TTS-specific configuration"""
    model_path: str = "models/en_US-ryan-high.onnx"
    config_path: str = "models/en_US-ryan-high.onnx.json"
    speaker_id: Optional[int] = None
    speed: float = 1.0
    effects: List[str] = field(default_factory=lambda: ["pitch -400", "bass +6", "vol 0.8"])

# Predefined voice profiles
VOICE_PROFILES = {
    # Piper TTS (High Quality Neural Voices)
    "piper_ryan_demonic": PiperConfig(
        model_path=os.path.join(os.path.dirname(__file__), "../models/en_US-ryan-high.onnx"),
        config_path=os.path.join(os.path.dirname(__file__), "../models/en_US-ryan-high.onnx.json"),
        speed=0.9,  # Slightly slower for ominous effect
        effects=["pitch -550", "bass +10", "vol 0.75"]  # Enhanced demonic: deeper pitch, more bass
    ),
    "piper_lessac_evil": PiperConfig(
        model_path=os.path.join(os.path.dirname(__file__), "../models/en_US-lessac-medium.onnx"), 
        config_path=os.path.join(os.path.dirname(__file__), "../models/en_US-lessac-medium.onnx.json"),
        speed=0.85,
        effects=["pitch -350", "bass +5", "vol 0.8"]
    ),
    "piper_ryan_dark_gritty": PiperConfig(
        model_path=os.path.join(os.path.dirname(__file__), "../models/en_US-ryan-high.onnx"),
        config_path=os.path.join(os.path.dirname(__file__), "../models/en_US-ryan-high.onnx.json"), 
        speed=0.9,
        effects=["pitch -580", "bass +11", "overdrive 6", "vol 0.75"]  # Alternative: dark & gritty
    ),
    
    # espeak fallbacks  
    "demonic_deep": EspeakConfig(
        voice_id="en",
        speed=110,
        pitch=12,
        effects=["pitch -700", "bass +10", "vol 0.7"]
    ),
    "demonic_aristocrat": EspeakConfig(
        voice_id="en-uk-rp", 
        speed=125,
        pitch=18,
        effects=["pitch -500", "bass +6", "vol 0.8"]
    ),
    "demonic_harsh": EspeakConfig(
        voice_id="de",
        speed=140,
        pitch=10,
        effects=["pitch -800", "bass +12", "vol 0.6"]
    ),
    
    # ElevenLabs premium
    "elevenlabs_premium": ElevenLabsConfig(
        voice_id="cPoqAvGWCPfCfyPMwe4z",
        stability=0.3,
        similarity_boost=0.2,
        style=0.6,
        speed=1.2,
        effects=["vol 0.1", "fade 0.05"]
    )
}
