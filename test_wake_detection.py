#!/usr/bin/env python3
"""Test wake phrase detection specifically"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('/Users/jkinman/dev/jk/evilassistant')

from evilassistant.config import WAKE_PHRASES

def test_wake_detection():
    print("🧪 TESTING WAKE PHRASE DETECTION")
    print("=" * 50)
    print(f"Wake phrases: {WAKE_PHRASES}")
    print()
    
    # Test transcriptions that we saw in the logs
    test_transcriptions = [
        "thank you",
        "done", 
        "okay",
        "bye-bye",
        "good",
        "are calling thanks",
        "on",
        "dark one",  # This should match
        "evil assistance",  # This should match
        "evil assistant",  # This should match
        "dark one turn on lights",  # This should match
        "i summon you"  # This should match
    ]
    
    print("Testing wake phrase detection logic:")
    for transcription in test_transcriptions:
        transcription_lower = transcription.lower()
        matches = [phrase for phrase in WAKE_PHRASES if phrase in transcription_lower]
        
        if matches:
            print(f"✅ '{transcription}' → MATCHES: {matches}")
        else:
            print(f"❌ '{transcription}' → No matches")
    
    print("\n🔍 Wake detection should work if:")
    print("1. Transcription contains any wake phrase")
    print("2. Case is handled correctly (converted to lowercase)")
    print("3. 2-second chunks capture complete phrases")

if __name__ == "__main__":
    test_wake_detection()
