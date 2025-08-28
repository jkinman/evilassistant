#!/usr/bin/env python3
"""Test the final fixes - no clipping + no numbered responses"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('/Users/jkinman/dev/jk/evilassistant')

from evilassistant.assistant import _synthesize_with_elevenlabs, play_audio

def test_final_fixes():
    print("🎯 TESTING FINAL FIXES")
    print("=" * 50)
    print("🔇 Anti-clipping: norm -12 gain -6 (aggressive volume reduction)")
    print("🗣️  Natural speech: No numbered lists, flowing sentences")
    print("⚡ Speed: 1.2x for dynamic delivery")
    print()
    
    # Test natural flowing speech (how the new prompt should sound)
    test_phrases = [
        "Foolish mortal, your pathetic question amuses me. The weather outside matches the darkness in my realm.",
        "Insignificant human, you dare disturb my eternal slumber? I shall illuminate your dwelling at once.",
        "Wretched creature, your lights bend to my supernatural will as all things must.",
        "Miserable mortal, I await your next pitiful command from the depths of shadow."
    ]
    
    print("🎭 Testing natural flowing demonic speech...")
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n▶️  Test {i}: {phrase[:60]}...")
        output_file = f"final_fix_test_{i}.wav"
        
        success = _synthesize_with_elevenlabs(phrase, output_file)
        if success:
            print(f"✅ Generated: {output_file}")
            print("🎵 Playing... (listen for: no clipping + natural flow)")
            play_audio(output_file)
            
            print("Rate this sample:")
            print("  1. Any clipping? (should be none)")
            print("  2. Natural speech flow? (no numbers)")
            print("  3. Good demonic character?")
        else:
            print(f"❌ Failed to generate {output_file}")
    
    print("\n🎯 FINAL FIXES TEST COMPLETE!")
    print("The voice should now be:")
    print("✅ Completely clip-free")
    print("🗣️  Natural flowing speech")
    print("👹 Still demonic and intimidating")

if __name__ == "__main__":
    test_final_fixes()
