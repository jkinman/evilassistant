#!/usr/bin/env python3
"""
Test script to verify LED brightness follows audio output correctly
"""

import sys
import os
import time
import logging

# Add parent directory to path to import evilassistant modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_led_audio_sync():
    """Test LED brightness synchronization with audio playback"""
    print("\n🧪 Testing LED-Audio Synchronization")
    print("=" * 50)
    
    try:
        from evilassistant.audio_manager import get_audio_manager
        from evilassistant.tts.factory import create_configured_engine
        import tempfile
        
        # Get audio manager
        audio_manager = get_audio_manager()
        
        print("📋 Audio Manager Status:")
        status = audio_manager.get_status()
        for key, value in status.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for k, v in value.items():
                    print(f"     {k}: {v}")
            else:
                print(f"   {key}: {value}")
        
        if not status.get('gpio', {}).get('gpio_available', False):
            print("⚠️  GPIO not available - LED test will be limited")
            return
        
        # Test 1: Manual LED brightness test
        print("\n🔆 Test 1: Manual LED Brightness Control")
        if audio_manager.gpio_controller:
            print("   Testing brightness levels...")
            for brightness in [10, 30, 50, 70, 90, 50, 10]:
                print(f"   Setting brightness to {brightness}%")
                audio_manager.gpio_controller.set_manual_brightness(brightness)
                time.sleep(1)
            
            print("   ✅ Manual brightness test completed")
        
        # Test 2: TTS with LED sync
        print("\n🎭 Test 2: TTS Audio with LED Synchronization")
        
        # Create a test phrase with varying volume
        test_text = "Testing LED brightness synchronization. LOUD WORDS and quiet words should show different brightness levels!"
        
        # Generate TTS
        tts_engine = create_configured_engine()
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            print(f"   Synthesizing: '{test_text[:50]}...'")
            
            if tts_engine.synthesize(test_text, tmp_file.name):
                print(f"   ✅ TTS generated: {tmp_file.name}")
                
                # Play with LED control
                print("   🔊 Playing audio with LED control...")
                print("   📊 Watch for LED brightness changes in the logs!")
                
                success = audio_manager.play_audio_file(tmp_file.name, enable_led_control=True)
                
                if success:
                    print("   ✅ Audio playback with LED control completed")
                else:
                    print("   ❌ Audio playback failed")
                    
            else:
                print("   ❌ TTS synthesis failed")
            
            # Clean up
            try:
                os.unlink(tmp_file.name)
            except:
                pass
        
        # Test 3: LED sequence test
        print("\n🌈 Test 3: LED Sequence Test")
        if audio_manager.gpio_controller:
            print("   Running LED sequence test...")
            audio_manager.gpio_controller.test_led_sequence(duration=3.0)
            print("   ✅ LED sequence test completed")
        
        print("\n✅ All LED-Audio sync tests completed!")
        print("\n📋 Expected Results:")
        print("   - Manual brightness should show smooth transitions")
        print("   - TTS playback should show LED brightness changes")
        print("   - LED sequence should show smooth sine wave pattern")
        print("   - Check logs for detailed brightness values")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            from evilassistant.audio_manager import cleanup_audio_manager
            cleanup_audio_manager()
        except:
            pass

if __name__ == "__main__":
    test_led_audio_sync()
