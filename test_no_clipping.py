#!/usr/bin/env python3
"""Test the anti-clipping voice settings"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('/Users/jkinman/dev/jk/evilassistant')

from evilassistant.assistant import _synthesize_with_elevenlabs, play_audio

def test_no_clipping():
    print("🔧 TESTING ANTI-CLIPPING VOICE SETTINGS")
    print("=" * 50)
    print("Settings: stability=0.2, similarity=0.1, style=0.8, no speaker boost")
    print("Processing: Sox companding to reduce clipping")
    print()
    
    # Test phrases that commonly cause clipping
    test_phrases = [
        "Greetings, mortal. Your demonic assistant has awakened from the depths.",
        "I command the darkness to obey my every word and whisper.",
        "The lights bend to my supernatural will, foolish human.",
        "What else do you seek, mortal? I await your next command!"
    ]
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"🎭 Testing phrase {i}: {phrase[:50]}...")
        output_file = f"no_clipping_test_{i}.wav"
        
        success = _synthesize_with_elevenlabs(phrase, output_file)
        if success:
            print(f"✅ Generated: {output_file}")
            print("🎵 Playing... (listen for clipping)")
            play_audio(output_file)
            
            response = input("Any clipping detected? (y/n): ").lower()
            if response == 'y':
                print("⚠️  Clipping detected - may need further adjustment")
            else:
                print("✅ No clipping - sounds clean!")
            print()
        else:
            print(f"❌ Failed to generate {output_file}")
    
    print("🔧 Anti-clipping test complete!")
    print("If clipping persists, we can adjust settings further.")

if __name__ == "__main__":
    test_no_clipping()
