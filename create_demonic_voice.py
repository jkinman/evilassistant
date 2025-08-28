#!/usr/bin/env python3
"""
Create a custom demonic voice using ElevenLabs Voice Design API
This is the BEST approach - no post-processing needed!
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def create_demonic_voice():
    """
    Create a custom demonic voice using ElevenLabs Voice Design API
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found")
        return None
    
    url = "https://api.elevenlabs.io/v1/voice-generation/generate-voice"
    
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Demonic voice parameters
    payload = {
        "text": "I am your demonic assistant, risen from the depths of darkness to serve your every command, mortal.",
        "voice_description": "Deep, menacing, demonic voice with low pitch, gravelly texture, and otherworldly resonance. Dark, intimidating tone suitable for a supernatural entity.",
        "gender": "male",
        "age": "old",
        "accent": "american",
        "accent_strength": 1.0
    }
    
    try:
        print("🔥 Creating custom demonic voice...")
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        
        if "voice_id" in result:
            voice_id = result["voice_id"]
            print(f"✅ Demonic voice created! Voice ID: {voice_id}")
            print(f"📝 Add this to your .env file:")
            print(f"ELEVENLABS_DEMONIC_VOICE_ID={voice_id}")
            
            # Test the new voice
            test_demonic_voice(voice_id)
            return voice_id
        else:
            print("❌ Failed to create voice:", result)
            return None
            
    except Exception as e:
        print(f"❌ Voice creation failed: {e}")
        return None

def test_demonic_voice(voice_id):
    """Test the newly created demonic voice"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "xi-api-key": api_key,
        "accept": "audio/mpeg",
        "content-type": "application/json"
    }
    
    payload = {
        "text": "Greetings, mortal. Your demonic assistant has awakened. What darkness shall we unleash today?",
        "model_id": "eleven_multilingual_v2"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        with open("test_custom_demon.mp3", "wb") as f:
            f.write(response.content)
        
        print("✅ Test voice saved as test_custom_demon.mp3")
        print("🎵 Play this file to hear your custom demonic voice!")
        
    except Exception as e:
        print(f"❌ Voice test failed: {e}")

if __name__ == "__main__":
    create_demonic_voice()
