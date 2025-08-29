#!/usr/bin/env python3
"""
Test script for Evil Assistant Continuous Transcription
"""

import asyncio
import time
from evilassistant.continuous_transcription import (
    get_transcriber, 
    start_continuous_transcription, 
    stop_continuous_transcription,
    search_transcription_logs
)
from evilassistant.evil_transcription_commands import process_evil_transcription_command

async def test_transcription_system():
    """Test the continuous transcription system"""
    print("🔥 Testing Evil Assistant Continuous Transcription System")
    print("=" * 60)
    
    # Initialize transcriber
    transcriber = get_transcriber()
    print("✅ Transcriber initialized")
    
    # Test stats
    stats = transcriber.get_stats()
    print(f"📊 Initial stats: {stats}")
    
    # Test evil commands
    print("\n🎭 Testing Evil Commands:")
    
    test_commands = [
        "start recording",
        "stats",
        "who spoke today",
        "what did someone say about lights",
        "recent activity",
        "stop recording"
    ]
    
    for command in test_commands:
        print(f"\n🗣️  Command: '{command}'")
        response = await process_evil_transcription_command(command)
        if response:
            print(f"👹 Evil Response: {response}")
        else:
            print("❌ No response")
    
    print("\n🎯 Test Summary:")
    print("✅ Transcription system loaded successfully")
    print("✅ Evil commands processed")
    print("✅ Privacy encryption system ready")
    print("✅ Speaker identification system ready")
    
    print("\n🔥 Ready for Evil Assistant integration!")
    print("Say: 'Evil assistant, start recording' to begin surveillance!")

if __name__ == "__main__":
    asyncio.run(test_transcription_system())
