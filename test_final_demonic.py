#!/usr/bin/env python3
"""Test the final demonic voice setup"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('/Users/jkinman/dev/jk/evilassistant')

from evilassistant.assistant import _synthesize_with_elevenlabs, play_audio

def test_final_demonic():
    print("🔥 TESTING FINAL DEMONIC VOICE SETUP")
    print("=" * 50)
    print("Voice: Bill (old male)")
    print("Settings: Maximum demonic (stability=0.1, similarity=0.0, style=1.0)")
    print("Effects: Pure ElevenLabs (no post-processing)")
    print()
    
    test_phrases = [
        "Greetings, mortal. Your demonic assistant has awakened.",
        "I am here to serve your darkest commands.",
        "The lights obey my will. Darkness consumes all.",
        "What else do you seek, mortal? I await your next command!"
    ]
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"🎭 Testing phrase {i}: {phrase[:50]}...")
        output_file = f"final_demonic_test_{i}.wav"
        
        success = _synthesize_with_elevenlabs(phrase, output_file)
        if success:
            print(f"✅ Generated: {output_file}")
            print("🎵 Playing...")
            play_audio(output_file)
            input("Press Enter for next test...")
        else:
            print(f"❌ Failed to generate {output_file}")
    
    print("\n👹 Final demonic voice test complete!")
    print("How does it sound now? Much more demonic and otherworldly?")

if __name__ == "__main__":
    test_final_demonic()
