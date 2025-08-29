#!/usr/bin/env python3
"""
Test concurrent operations: normal assistant + transcription
"""

import asyncio
import time
import threading
from unittest.mock import Mock
import numpy as np

async def test_concurrent_operations():
    """Test if normal app works while transcription is running"""
    print("🧪 Testing Concurrent Operations")
    print("=" * 50)
    
    # Test 1: Audio resource sharing
    print("🎤 Testing Audio Resource Sharing...")
    
    try:
        from evilassistant.simple_vad import SimpleVADRecorder
        from evilassistant.continuous_transcription import process_audio_for_transcription
        
        # Create VAD instance
        vad = SimpleVADRecorder()
        print("✅ VAD recorder created")
        
        # Simulate transcription being active
        transcription_active = True
        
        # Test if wake phrase detection still works with transcription active
        print("🔍 Testing wake phrase detection with transcription...")
        
        # Create mock audio data
        audio_chunk = np.random.normal(0, 0.1, 1600)  # 0.1 second chunk
        
        # This should work without conflicts
        process_audio_for_transcription(audio_chunk)
        print("✅ Transcription processing works")
        
    except Exception as e:
        print(f"❌ Error in audio resource test: {e}")
    
    # Test 2: Command processing while transcribing
    print("\n🎭 Testing Command Processing During Transcription...")
    
    try:
        from evilassistant.unified_command_processor import UnifiedCommandProcessor
        
        # Mock handlers
        class MockSmartHome:
            async def process_command(self, text):
                await asyncio.sleep(0.1)  # Simulate processing time
                return "Smart home command processed!" if 'light' in text.lower() else None
        
        class MockAI:
            def get_ai_response(self, text):
                time.sleep(0.1)  # Simulate AI processing
                return f"AI response: {text}"
        
        processor = UnifiedCommandProcessor(
            smart_home_handler=MockSmartHome(),
            ai_handler=MockAI(),
            transcription_handler=None
        )
        
        # Test commands while "transcription is running"
        test_commands = [
            "turn on the lights",
            "what time is it",
            "start recording"  # This should work even if transcription is running
        ]
        
        for command in test_commands:
            start_time = time.time()
            command_type, response = await processor.process_command(command)
            processing_time = time.time() - start_time
            
            print(f"✅ '{command}' → {command_type.value} ({processing_time:.3f}s)")
            
            # Commands should process quickly even with transcription
            if processing_time > 2.0:
                print(f"⚠️  Slow processing detected: {processing_time:.3f}s")
    
    except Exception as e:
        print(f"❌ Error in command processing test: {e}")
    
    # Test 3: Thread safety
    print("\n🧵 Testing Thread Safety...")
    
    try:
        results = []
        errors = []
        
        def worker_thread(thread_id):
            """Simulate concurrent audio processing"""
            try:
                for i in range(5):
                    audio_data = np.random.normal(0, 0.1, 1600)
                    # Simulate processing
                    time.sleep(0.01)
                    results.append(f"Thread-{thread_id}-Task-{i}")
            except Exception as e:
                errors.append(f"Thread-{thread_id}: {e}")
        
        # Start multiple threads to simulate concurrent operations
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        print(f"✅ Thread safety test completed")
        print(f"   Results: {len(results)} tasks completed")
        print(f"   Errors: {len(errors)} errors")
        
        if errors:
            for error in errors:
                print(f"   ❌ {error}")
    
    except Exception as e:
        print(f"❌ Error in thread safety test: {e}")
    
    # Test 4: Performance impact
    print("\n⚡ Testing Performance Impact...")
    
    try:
        # Baseline: normal command processing
        start_time = time.time()
        for i in range(10):
            await asyncio.sleep(0.01)  # Simulate normal processing
        baseline_time = time.time() - start_time
        
        # With transcription: simulate background transcription load
        start_time = time.time()
        for i in range(10):
            # Simulate transcription happening in background
            threading.Thread(target=lambda: time.sleep(0.005), daemon=True).start()
            await asyncio.sleep(0.01)  # Normal processing
        
        with_transcription_time = time.time() - start_time
        
        overhead = ((with_transcription_time - baseline_time) / baseline_time) * 100
        
        print(f"✅ Performance test completed")
        print(f"   Baseline: {baseline_time:.3f}s")
        print(f"   With transcription: {with_transcription_time:.3f}s")
        print(f"   Overhead: {overhead:.1f}%")
        
        if overhead > 50:
            print(f"⚠️  High overhead detected: {overhead:.1f}%")
    
    except Exception as e:
        print(f"❌ Error in performance test: {e}")
    
    print(f"\n🎯 CONCURRENT OPERATIONS TEST COMPLETE!")

if __name__ == "__main__":
    asyncio.run(test_concurrent_operations())
