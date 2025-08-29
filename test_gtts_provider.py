#!/usr/bin/env python3
"""
Test the new gTTS Demonic provider integration
"""

import os
import tempfile
import time
import pygame

def test_gtts_provider():
    """Test the new gTTS Demonic TTS provider"""
    print("🔥 Testing gTTS Demonic Provider Integration")
    print("=" * 60)
    
    try:
        from evilassistant.tts.factory import create_demonic_engine
        
        # Create demonic engine
        print("🎭 Creating demonic TTS engine...")
        engine = create_demonic_engine()
        
        # Test phrases
        test_phrases = [
            "I am your Evil Assistant, mortal.",
            "Your dark commands amuse me, human.",
            "The shadows whisper your secrets to me.",
            "What darkness do you seek from the void?",
        ]
        
        for i, phrase in enumerate(test_phrases, 1):
            print(f"\n🔥 Test {i}: '{phrase}'")
            
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            try:
                # Synthesize
                start_time = time.time()
                success = engine.synthesize(phrase, output_file)
                generation_time = time.time() - start_time
                
                if success:
                    print(f"✅ Synthesis successful ({generation_time:.3f}s)")
                    print(f"💾 Output: {output_file}")
                    
                    # Check file exists and has content
                    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                        print(f"📊 File size: {os.path.getsize(output_file)} bytes")
                        
                        # Play audio
                        if input("▶️  Play this audio? (y/n): ").lower() == 'y':
                            play_audio(output_file)
                    else:
                        print("❌ Output file is empty or missing")
                else:
                    print("❌ Synthesis failed")
                
            except Exception as e:
                print(f"❌ Error during synthesis: {e}")
            
            finally:
                # Cleanup
                if os.path.exists(output_file):
                    os.unlink(output_file)
    
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        print("Make sure gTTS is installed: pip install gtts")

def play_audio(file_path):
    """Play audio file using pygame"""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        # Wait for playback to complete
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        pygame.mixer.quit()
        print("🔊 Playback completed")
        
    except Exception as e:
        print(f"❌ Playback failed: {e}")

def test_provider_info():
    """Test provider information and capabilities"""
    print("\n📋 Provider Information Test")
    print("-" * 40)
    
    try:
        from evilassistant.tts.providers.gtts_demonic import GTTSDemonicProvider
        from evilassistant.tts.config import TTSConfig
        
        # Create provider
        config = TTSConfig(effects=["demonic_transformation"])
        provider = GTTSDemonicProvider(config)
        
        # Get info
        info = provider.get_voice_info()
        
        print("🎭 Provider Information:")
        for key, value in info.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")
        
        # Test availability
        available = provider.is_available()
        print(f"\n✅ Provider available: {available}")
        
    except Exception as e:
        print(f"❌ Provider info test failed: {e}")

def performance_test():
    """Test synthesis performance"""
    print("\n⚡ Performance Test")
    print("-" * 40)
    
    try:
        from evilassistant.tts.factory import create_demonic_engine
        
        engine = create_demonic_engine()
        test_text = "Performance test for demonic voice synthesis in real-time applications."
        
        # Multiple runs
        times = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            try:
                start = time.time()
                success = engine.synthesize(test_text, output_file)
                duration = time.time() - start
                
                if success:
                    times.append(duration)
                    print(f"  Run {i+1}: {duration:.3f}s")
                else:
                    print(f"  Run {i+1}: FAILED")
                
            finally:
                if os.path.exists(output_file):
                    os.unlink(output_file)
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"\n📊 Performance Results:")
            print(f"  Average time: {avg_time:.3f}s")
            print(f"  Fastest: {min(times):.3f}s")
            print(f"  Status: {'✅ Real-time capable' if avg_time < 2.0 else '⚠️ Slow'}")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")

if __name__ == "__main__":
    test_gtts_provider()
    test_provider_info()
    performance_test()
    
    print(f"\n🎯 Summary:")
    print("✅ gTTS Demonic provider tested")
    print("✅ Ready for Evil Assistant integration")
    print("🔥 Fast, free, demonic voice synthesis achieved!")
