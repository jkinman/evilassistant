#!/usr/bin/env python3
"""Quick test of the new demonic voice"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append('/Users/jkinman/dev/jk/evilassistant')

from evilassistant.assistant import _synthesize_with_elevenlabs, play_audio

def test_demonic_voice():
    print("🔥 Testing DEMONIC voice with Clyde + effects...")
    
    test_text = "Greetings, mortal. I am your demonic assistant, risen from the depths of darkness!"
    output_file = "test_demonic_clyde.wav"
    
    success = _synthesize_with_elevenlabs(test_text, output_file)
    
    if success:
        print(f"✅ Demonic voice saved as {output_file}")
        print("🎵 Playing demonic voice...")
        play_audio(output_file)
        print("👹 How does that sound? Much more demonic?")
    else:
        print("❌ Failed to generate demonic voice")

if __name__ == "__main__":
    test_demonic_voice()
