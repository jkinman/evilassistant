#!/usr/bin/env python3
"""
ElevenLabs TTS Provider

Cloud-based premium text-to-speech using ElevenLabs API.
Provides high-quality voice synthesis with configurable voice settings.
Requires API key and internet connection.
"""

import os
import subprocess
import logging
from ..base import TTSProvider
from ..config import ElevenLabsConfig

logger = logging.getLogger(__name__)

class ElevenLabsProvider(TTSProvider):
    """ElevenLabs TTS provider with configurable settings"""
    
    def __init__(self, config: ElevenLabsConfig):
        super().__init__(config)
        self.elevenlabs_config = config
    
    def is_available(self) -> bool:
        """Check if ElevenLabs API key is configured"""
        api_key = os.getenv("ELEVENLABS_API_KEY")
        return bool(api_key and self.elevenlabs_config.voice_id)
    
    def synthesize(self, text: str, output_file: str) -> bool:
        """Synthesize using ElevenLabs API"""
        import requests
        
        if not self.is_available():
            logger.error("ElevenLabs not configured")
            return False
            
        api_key = os.getenv("ELEVENLABS_API_KEY")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_config.voice_id}"
        
        headers = {
            "xi-api-key": api_key,
            "accept": "audio/mpeg",
            "content-type": "application/json",
        }
        
        payload = {
            "text": text,
            "model_id": self.elevenlabs_config.model_id,
            "voice_settings": {
                "stability": self.elevenlabs_config.stability,
                "similarity_boost": self.elevenlabs_config.similarity_boost,
                "style": self.elevenlabs_config.style,
                "use_speaker_boost": self.elevenlabs_config.use_speaker_boost,
                "speed": self.elevenlabs_config.speed
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            # Save MP3 and convert to WAV with effects
            temp_mp3 = output_file.replace('.wav', '_temp.mp3')
            with open(temp_mp3, "wb") as f:
                f.write(response.content)
            
            # Apply effects during conversion
            if self.config.effects:
                success = self.apply_effects(temp_mp3, output_file)
            else:
                subprocess.run(['sox', temp_mp3, output_file], check=True)
                success = True
                
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
                
            return success
            
        except Exception as e:
            logger.error(f"ElevenLabs synthesis failed: {e}")
            return False
