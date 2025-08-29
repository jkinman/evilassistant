#!/usr/bin/env python3
"""
Centralized Configuration Management for Evil Assistant
"""

import os
import logging
from typing import Dict, Any, Optional, TypeVar, Type
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class ConfigSection:
    """Base class for configuration sections"""
    pass

@dataclass
class AudioConfig(ConfigSection):
    """Audio configuration"""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1600
    chunk_duration: float = 0.1
    speech_timeout: float = 0.8
    energy_threshold: int = 1200
    noise_reduction: bool = True
    gain_normalization: bool = True
    auto_gain: bool = True

@dataclass
class STTConfig(ConfigSection):
    """Speech-to-Text configuration"""
    model: str = "base"
    compute_type: str = "int8"
    beam_size: int = 1
    num_workers: int = 2
    language: str = "en"
    vad_filter: bool = True
    silence_duration: float = 0.6
    min_confidence: float = -0.8

@dataclass
class TTSConfig(ConfigSection):
    """Text-to-Speech configuration"""
    provider: str = "piper"
    voice_profile: str = "piper_ryan_demonic"
    fallback_enabled: bool = True
    speed: float = 1.0
    
    # ElevenLabs specific
    elevenlabs_stability: float = 0.75
    elevenlabs_similarity_boost: float = 0.8
    elevenlabs_style: float = 0.0
    elevenlabs_speed: float = 1.0
    
    # Espeak specific
    espeak_voice: str = "en+m3"
    espeak_speed: int = 150
    espeak_pitch: int = 50
    espeak_volume: int = 100

@dataclass
class SmartHomeConfig(ConfigSection):
    """Smart home configuration"""
    hue_bridge_ip: Optional[str] = None
    home_assistant_url: str = "http://localhost:8123"
    home_assistant_token: Optional[str] = None
    auto_discovery: bool = True

@dataclass
class TranscriptionConfig(ConfigSection):
    """Transcription configuration"""
    enabled: bool = False
    min_confidence: float = -0.8
    chunk_duration: float = 10.0
    storage_dir: str = "transcripts"
    retention_days: int = 7
    enable_speaker_id: bool = True
    max_speakers: int = 4

@dataclass
class SystemConfig(ConfigSection):
    """System configuration"""
    log_level: str = "INFO"
    debug_mode: bool = False
    pi_optimizations: bool = False
    temp_dir: str = "temp"
    max_temp_files: int = 100

@dataclass
class EvilAssistantConfig:
    """Main configuration class"""
    audio: AudioConfig = field(default_factory=AudioConfig)
    stt: STTConfig = field(default_factory=STTConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    smart_home: SmartHomeConfig = field(default_factory=SmartHomeConfig)
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
    
    # Wake phrases
    wake_phrases: list[str] = field(default_factory=lambda: [
        "evil assistant", "evil assistance", "dark one", "dark 1", "cthulhu", "summon"
    ])
    
    # API Keys (loaded from environment)
    xai_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_voice_id: Optional[str] = None

class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_file: str = ".env"):
        self.config_file = config_file
        self._config: Optional[EvilAssistantConfig] = None
        self._load_dotenv()
    
    def _load_dotenv(self):
        """Load environment variables from .env file"""
        try:
            from dotenv import load_dotenv
            if os.path.exists(self.config_file):
                load_dotenv(self.config_file)
                logger.info(f"Loaded configuration from {self.config_file}")
        except ImportError:
            logger.warning("python-dotenv not available, using system environment only")
    
    def get_config(self) -> EvilAssistantConfig:
        """Get the current configuration"""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> EvilAssistantConfig:
        """Load configuration from environment variables"""
        config = EvilAssistantConfig()
        
        # Load API keys
        config.xai_api_key = os.getenv("XAI_API_KEY")
        config.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        config.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        
        # Smart home configuration
        config.smart_home.hue_bridge_ip = os.getenv("PHILIPS_HUE_BRIDGE_IP")
        config.smart_home.home_assistant_url = os.getenv("HOME_ASSISTANT_URL", config.smart_home.home_assistant_url)
        config.smart_home.home_assistant_token = os.getenv("HOME_ASSISTANT_TOKEN")
        
        # TTS configuration
        config.tts.provider = os.getenv("TTS_PROVIDER", config.tts.provider)
        config.tts.voice_profile = os.getenv("TTS_VOICE_PROFILE", config.tts.voice_profile)
        config.tts.fallback_enabled = os.getenv("TTS_FALLBACK_ENABLED", "true").lower() == "true"
        
        # STT configuration
        config.stt.model = os.getenv("WHISPER_MODEL", config.stt.model)
        config.stt.compute_type = os.getenv("WHISPER_COMPUTE_TYPE", config.stt.compute_type)
        
        # System configuration
        config.system.log_level = os.getenv("LOG_LEVEL", config.system.log_level)
        config.system.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        
        # Auto-detect Pi optimizations
        try:
            from .config_pi import is_raspberry_pi
            config.system.pi_optimizations = is_raspberry_pi()
        except ImportError:
            pass
        
        return config
    
    def validate_config(self) -> list[str]:
        """Validate configuration and return list of issues"""
        config = self.get_config()
        issues = []
        
        # Required API keys
        if not config.xai_api_key:
            issues.append("XAI_API_KEY is required for AI functionality")
        
        # Optional but recommended
        if not config.elevenlabs_api_key:
            issues.append("ELEVENLABS_API_KEY missing - using fallback TTS")
        
        if not config.smart_home.hue_bridge_ip:
            issues.append("PHILIPS_HUE_BRIDGE_IP missing - smart home features disabled")
        
        # Directory validation
        try:
            os.makedirs(config.system.temp_dir, exist_ok=True)
            os.makedirs(config.transcription.storage_dir, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create required directories: {e}")
        
        return issues
    
    def get_env_var(self, key: str, default: T = None, var_type: Type[T] = str) -> T:
        """Get environment variable with type conversion"""
        value = os.getenv(key, default)
        
        if value is None:
            return default
        
        if var_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            try:
                return int(value)
            except ValueError:
                logger.warning(f"Invalid integer value for {key}: {value}, using default")
                return default
        elif var_type == float:
            try:
                return float(value)
            except ValueError:
                logger.warning(f"Invalid float value for {key}: {value}, using default")
                return default
        else:
            return var_type(value)
    
    def update_config(self, **kwargs):
        """Update configuration values"""
        config = self.get_config()
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")
    
    def save_config_template(self, output_file: str = ".env.template"):
        """Save a configuration template file"""
        template = """# Evil Assistant Configuration Template

# Required API Keys
XAI_API_KEY=your_xai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here

# Smart Home (Optional)
PHILIPS_HUE_BRIDGE_IP=192.168.1.xxx
HOME_ASSISTANT_URL=http://localhost:8123
HOME_ASSISTANT_TOKEN=your_long_lived_access_token

# Voice Configuration
TTS_PROVIDER=piper
TTS_VOICE_PROFILE=piper_ryan_demonic
TTS_FALLBACK_ENABLED=true

# Speech Recognition
WHISPER_MODEL=base
WHISPER_COMPUTE_TYPE=int8

# System
LOG_LEVEL=INFO
DEBUG_MODE=false
"""
        
        with open(output_file, 'w') as f:
            f.write(template)
        
        logger.info(f"Configuration template saved to {output_file}")

# Global configuration manager
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config() -> EvilAssistantConfig:
    """Get current configuration"""
    return get_config_manager().get_config()
