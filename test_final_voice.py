#!/usr/bin/env python3
"""Test the final optimized voice - no clipping + faster speech"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('/Users/jkinman/dev/jk/evilassistant')

from evilassistant.assistant import _synthesize_with_elevenlabs, play_audio

def test_final_voice():
    print("🎯 TESTING FINAL OPTIMIZED DEMONIC VOICE")
    print("=" * 50)
    print("✅ Anti-clipping: norm + compression + limiter + gain reduction")
    print("⚡ Speed: 1.2x for dynamic delivery")
    print("👹 Settings: stability=0.3, similarity=0.2, style=0.6")
    print()
    
    # Test with challenging phrases that previously caused clipping
    test_phrases = [
        "Greetings, mortal! Your demonic assistant commands the darkness!",
        "I summon the shadows to bend reality to my supernatural will!",
        "The lights obey my every whisper and command, foolish human!",
        "What else do you seek, mortal? I await your next dark command!"
    ]
    
    print("🎭 Testing phrases that previously caused clipping...")
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n▶️  Test {i}: {phrase}")
        output_file = f"final_optimized_test_{i}.wav"
        
        success = _synthesize_with_elevenlabs(phrase, output_file)
        if success:
            print(f"✅ Generated: {output_file}")
            print("🎵 Playing optimized voice...")
            play_audio(output_file)
            print("   - Listen for: No clipping + faster, more dynamic speech")
        else:
            print(f"❌ Failed to generate {output_file}")
    
    print("\n🎯 FINAL VOICE TEST COMPLETE!")
    print("How does it sound now?")
    print("✅ No clipping?")
    print("⚡ Good speech speed?")
    print("👹 Still demonic enough?")

if __name__ == "__main__":
    test_final_voice()
