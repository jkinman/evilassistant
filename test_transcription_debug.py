#!/usr/bin/env python3
"""
Debug the transcription confidence issue
"""

import asyncio
import numpy as np
from evilassistant.continuous_transcription import ContinuousTranscriber

async def test_confidence_issue():
    """Test with lower confidence threshold"""
    print("🔍 Testing Transcription Confidence Issues")
    print("=" * 50)
    
    # Create transcriber with VERY low confidence threshold
    transcriber = ContinuousTranscriber(
        model_name="base",
        min_confidence=-2.0,  # Very low threshold to catch everything
        enable_speaker_id=True
    )
    
    print(f"📊 Minimum confidence threshold: {transcriber.min_confidence}")
    print("🧪 This should catch even low-confidence transcriptions")
    
    # Create fake audio data to test storage
    print("\n🎧 Creating test audio data...")
    sample_rate = 16000
    duration = 2.0  # 2 seconds
    audio_data = np.random.normal(0, 0.1, int(sample_rate * duration))
    
    # Test the transcription process
    print("🔍 Testing transcription process...")
    entry = transcriber.transcribe_chunk(audio_data, sample_rate)
    
    if entry:
        print(f"✅ Transcription successful!")
        print(f"   Text: {entry.text}")
        print(f"   Confidence: {entry.confidence}")
        print(f"   Speaker: {entry.speaker_id}")
        print(f"   Duration: {entry.duration}s")
        
        # Test storage
        transcriber.process_and_store(audio_data)
        stats = transcriber.get_stats()
        print(f"📊 Storage stats: {stats}")
    else:
        print("❌ No transcription result")
    
    print("\n💡 Try saying longer, clearer sentences for better confidence!")
    print("💡 Or we can lower the confidence threshold in the config")

if __name__ == "__main__":
    asyncio.run(test_confidence_issue())
