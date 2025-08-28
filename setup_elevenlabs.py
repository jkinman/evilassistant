#!/usr/bin/env python3
"""
ElevenLabs Voice Setup for Evil Assistant
"""

import os
import requests

def test_elevenlabs_connection():
    """Test ElevenLabs API connection and show available voices"""
    
    # Check if API key exists
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key or api_key == "sk_your_key_here":
        print("🔥 ELEVENLABS SETUP GUIDE")
        print("=" * 50)
        print("1. Go to: https://elevenlabs.io/app/speech-synthesis")
        print("2. Sign up for a free account (10,000 characters/month)")
        print("3. Go to Profile → API Key")
        print("4. Copy your API key")
        print("5. Update your .env file:")
        print("   ELEVENLABS_API_KEY=sk_your_actual_key_here")
        print()
        print("👹 RECOMMENDED DEMON VOICES:")
        print("- Clone your own voice and adjust settings for demonic effect")
        print("- Use voice settings: Stability=0.15, Clarity=0.75, Style=0.9")
        print("- Try the 'Adam' or 'Antoni' voices for deeper tones")
        return False
    
    print(f"🔥 Testing ElevenLabs with API key: {api_key[:8]}...")
    
    # Test API connection
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    try:
        response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers)
        if response.status_code == 200:
            voices = response.json()["voices"]
            print(f"✅ Connected! Found {len(voices)} voices")
            
            print("\n🎭 AVAILABLE VOICES:")
            for voice in voices[:10]:  # Show first 10
                print(f"  - {voice['name']}: {voice['voice_id']}")
            
            print("\n👹 TO USE A VOICE:")
            print("Update evilassistant/config.py:")
            print("ELEVENLABS_VOICE_ID = 'voice_id_here'")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_voice_synthesis():
    """Test voice synthesis with a demon phrase"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key or api_key == "sk_your_key_here":
        print("❌ Set up your API key first!")
        return
    
    voice_id = "EXAVITQu4vr4xnSDxMaL"  # Sarah voice
    text = "Greetings, puny mortal. I am your evil assistant, ready to serve your dark commands!"
    
    print(f"🔥 Testing voice synthesis...")
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.15,  # Lower for more variation (demonic)
            "similarity_boost": 0.75,
            "style": 0.9,  # Higher for more expressive (evil)
            "use_speaker_boost": True
        }
    }
    
    try:
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            with open("test_demon_voice.mp3", "wb") as f:
                f.write(response.content)
            print("✅ Voice test saved as 'test_demon_voice.mp3'")
            print("🎵 Playing test...")
            os.system("afplay test_demon_voice.mp3")  # macOS
            return True
        else:
            print(f"❌ Synthesis failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Synthesis error: {e}")
        return False

if __name__ == "__main__":
    print("🔥 EVIL ASSISTANT - ELEVENLABS SETUP")
    print("=" * 40)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    if test_elevenlabs_connection():
        print("\n" + "=" * 40)
        test_voice_synthesis()
    
    print("\n👹 Ready to unleash demonic voice!")
