#!/usr/bin/env python3
"""Test the initial clipping fix"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('/Users/jkinman/dev/jk/evilassistant')

from evilassistant.assistant import _synthesize_with_elevenlabs, play_audio

def test_initial_clipping():
    print("🔧 TESTING INITIAL CLIPPING FIX")
    print("=" * 50)
    print("🎵 Fix: fade 0.01 (10ms fade-in) + norm -9 + gain -4")
    print("👂 Focus: Listen specifically to the FIRST WORD for clipping")
    print()
    
    # Test phrases that start with hard consonants (most likely to clip)
    test_phrases = [
        "Greetings, pathetic mortal!",
        "Darkness consumes all light!",
        "Foolish human, you dare disturb me!",
        "Welcome to your doom, wretched creature!",
        "Bow before my supernatural power!"
    ]
    
    print("🎭 Testing initial audio onset...")
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n▶️  Test {i}: '{phrase}'")
        print(f"    Focus on: Does '{phrase.split()[0]}' clip at the start?")
        
        output_file = f"initial_clip_test_{i}.wav"
        
        success = _synthesize_with_elevenlabs(phrase, output_file)
        if success:
            print(f"✅ Generated: {output_file}")
            print("🎵 Playing... LISTEN TO THE FIRST WORD CAREFULLY")
            play_audio(output_file)
            
            clip_detected = input("   Any clipping at the start? (y/n): ").lower()
            if clip_detected == 'y':
                print("   ⚠️  Still clipping - may need stronger fade-in")
            else:
                print("   ✅ Clean start - no clipping!")
        else:
            print(f"❌ Failed to generate {output_file}")
    
    print("\n🔧 INITIAL CLIPPING TEST COMPLETE!")
    print("If any clipping remains, we can increase the fade-in time.")

if __name__ == "__main__":
    test_initial_clipping()
