#!/usr/bin/env python3
"""
Find the best existing demonic voice from ElevenLabs voice library
and test different voice settings for maximum demonic effect
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_all_voices():
    """Get all available ElevenLabs voices"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found")
        return []
    
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("voices", [])
    except Exception as e:
        print(f"❌ Failed to get voices: {e}")
        return []

def test_demonic_settings(voice_id, voice_name):
    """Test extreme demonic voice settings"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "accept": "audio/mpeg",
        "content-type": "application/json"
    }
    
    # Extreme demonic settings
    payload = {
        "text": "I am your demonic assistant, risen from the depths of hell to serve your darkest commands, mortal.",
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.1,           # Very low for unnatural variation
            "similarity_boost": 0.0,    # Minimum for most unnatural sound
            "style": 1.0,               # Maximum style for dramatic effect
            "use_speaker_boost": True
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        filename = f"test_demonic_{voice_name.lower().replace(' ', '_')}.mp3"
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"✅ {voice_name} demonic test saved as {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ {voice_name} test failed: {e}")
        return None

def find_best_demonic_voice():
    """Find and test the best voices for demonic effect"""
    print("🔥 FINDING THE PERFECT DEMONIC VOICE...")
    print("=" * 50)
    
    voices = get_all_voices()
    if not voices:
        print("❌ No voices found")
        return
    
    # Look for voices that might work well for demonic effects
    deep_voice_keywords = ['male', 'deep', 'dark', 'low', 'bass', 'narrator', 'serious']
    potential_voices = []
    
    print("🎭 Available voices:")
    for voice in voices:
        name = voice.get("name", "Unknown")
        voice_id = voice.get("voice_id", "")
        labels = voice.get("labels", {})
        description = labels.get("description", "").lower()
        gender = labels.get("gender", "").lower()
        age = labels.get("age", "").lower()
        
        print(f"  - {name}: {voice_id}")
        if gender == "male":
            print(f"    Gender: {gender}, Age: {age}")
            print(f"    Description: {description[:100]}...")
        
        # Score voices for demonic potential
        score = 0
        if gender == "male":
            score += 2
        if age in ["middle aged", "old"]:
            score += 2
        for keyword in deep_voice_keywords:
            if keyword in description:
                score += 1
        
        if score >= 3:  # Good candidates
            potential_voices.append((name, voice_id, score))
    
    # Sort by score and test top candidates
    potential_voices.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n🎯 TESTING TOP {min(5, len(potential_voices))} DEMONIC CANDIDATES:")
    print("=" * 50)
    
    tested_files = []
    for name, voice_id, score in potential_voices[:5]:
        print(f"\n🔥 Testing {name} (Score: {score})")
        filename = test_demonic_settings(voice_id, name)
        if filename:
            tested_files.append((name, voice_id, filename))
    
    print(f"\n👹 DEMONIC VOICE TESTS COMPLETE!")
    print("=" * 50)
    print("🎵 Test files created:")
    for name, voice_id, filename in tested_files:
        print(f"  - {filename} ({name}: {voice_id})")
    
    print(f"\n🔥 NEXT STEPS:")
    print("1. Listen to each test file")
    print("2. Pick the most demonic sounding one")
    print("3. Update your config with the voice_id")
    
    if tested_files:
        best_name, best_id, best_file = tested_files[0]
        print(f"\n⭐ RECOMMENDED (highest scoring): {best_name}")
        print(f"   Voice ID: {best_id}")
        print(f"   Add to .env: ELEVENLABS_DEMONIC_VOICE_ID={best_id}")

if __name__ == "__main__":
    find_best_demonic_voice()
