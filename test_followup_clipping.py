#!/usr/bin/env python3
"""Test the specific follow-up prompt for clipping"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('/Users/jkinman/dev/jk/evilassistant')

from evilassistant.assistant import _synthesize_with_elevenlabs, play_audio

def test_followup_clipping():
    print("🔍 TESTING FOLLOW-UP PROMPT CLIPPING")
    print('Testing exact phrase: "What else do you seek, mortal? I await your next command!"')
    print('Focus on: "else do" part where clipping occurred')
    print()

    follow_up_text = "What else do you seek, mortal? I await your next command!"
    print(f"Generating: {follow_up_text}")

    success = _synthesize_with_elevenlabs(follow_up_text, "followup_test.wav")
    if success:
        print("✅ Generated follow-up prompt")
        print('🎵 Playing... Listen specifically to "else do" for clipping')
        play_audio("followup_test.wav")
        print()
        clip_response = input('Any clipping on "else do"? (y/n): ').lower()
        if clip_response == 'y':
            print("⚠️  Follow-up prompt still clipping - same processing should apply")
            print("   The vol 0.3 reduction should affect all audio equally")
        else:
            print("✅ No clipping detected in isolated test")
            print("   May be a different issue in the full assistant flow")
    else:
        print("❌ Failed to generate follow-up test")

    print("\n🔧 If clipping persists, we may need to reduce volume further to vol 0.2")

if __name__ == "__main__":
    test_followup_clipping()
