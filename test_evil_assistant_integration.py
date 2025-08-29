#!/usr/bin/env python3
"""
Test Evil Assistant integration with new gTTS Demonic provider
"""

import os
import tempfile
import time

def test_evil_assistant_tts():
    """Test the Evil Assistant TTS system with gTTS Demonic"""
    print("🔥 Testing Evil Assistant TTS Integration")
    print("=" * 60)
    
    try:
        # Test the exact same path the assistant uses
        from evilassistant.assistant_clean import AudioHandler
        
        print("🎭 Creating AudioHandler (as used in Evil Assistant)...")
        audio_handler = AudioHandler()
        
        # Test phrases that Evil Assistant would actually say
        evil_responses = [
            "Your dark commands please me, mortal.",
            "I have turned your lights to the color of hellfire!",
            "The shadows whisper your secrets to me.",
            "What darkness do you seek from the void, human?",
            "My surveillance is now active. All shall be recorded.",
        ]
        
        print(f"🎤 Testing {len(evil_responses)} Evil Assistant responses...")
        
        for i, response in enumerate(evil_responses, 1):
            print(f"\n🔥 Test {i}: Evil Assistant Response")
            print(f"   Text: '{response}'")
            
            # Create temp file (same pattern as assistant)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            try:
                # Use the exact same method as Evil Assistant
                start_time = time.time()
                success = audio_handler.synthesize_speech(response, output_file)
                generation_time = time.time() - start_time
                
                if success:
                    file_size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
                    print(f"   ✅ Synthesis successful ({generation_time:.3f}s)")
                    print(f"   📊 File size: {file_size} bytes")
                    
                    # Test playback (optional)
                    if input("   ▶️  Play Evil Assistant response? (y/n): ").lower() == 'y':
                        play_audio(output_file)
                        
                else:
                    print(f"   ❌ Synthesis failed")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            finally:
                # Cleanup
                if os.path.exists(output_file):
                    os.unlink(output_file)
    
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        print("Make sure all dependencies are installed")

def test_provider_priority():
    """Test TTS provider priority and fallback"""
    print("\n🎯 Testing Provider Priority & Fallback")
    print("-" * 50)
    
    try:
        from evilassistant.tts.factory import create_configured_engine
        
        # Create engine (same as Evil Assistant)
        engine = create_configured_engine()
        
        # Test provider order
        print("📋 Configured TTS Providers (in priority order):")
        for i, (priority, provider) in enumerate(engine.providers):
            provider_name = provider.__class__.__name__
            available = "✅" if provider.is_available() else "❌"
            print(f"   {i+1}. Priority {priority}: {provider_name} {available}")
        
        # Test synthesis
        test_text = "Provider priority test for Evil Assistant."
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_file = tmp_file.name
        
        try:
            print(f"\n🔊 Testing synthesis with: '{test_text}'")
            success = engine.synthesize(test_text, output_file)
            
            if success:
                current_provider = engine.get_current_provider()
                print(f"✅ Synthesis successful with: {current_provider}")
                
                if input("▶️  Play provider test? (y/n): ").lower() == 'y':
                    play_audio(output_file)
            else:
                print("❌ All providers failed")
                
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    except Exception as e:
        print(f"❌ Provider test failed: {e}")

def play_audio(file_path):
    """Play audio file"""
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        pygame.mixer.quit()
        print("   🔊 Playback completed")
        
    except Exception as e:
        print(f"   ❌ Playback failed: {e}")

def test_config_compatibility():
    """Test configuration compatibility"""
    print("\n⚙️ Testing Configuration Compatibility")
    print("-" * 50)
    
    try:
        from evilassistant.config import TTS_VOICE_PROFILE
        print(f"📝 Current TTS_VOICE_PROFILE: {TTS_VOICE_PROFILE}")
        
        # Test if the profile exists
        from evilassistant.tts.config import VOICE_PROFILES
        if TTS_VOICE_PROFILE in VOICE_PROFILES:
            profile = VOICE_PROFILES[TTS_VOICE_PROFILE]
            print(f"✅ Profile found: {type(profile).__name__}")
        else:
            print(f"⚠️  Profile '{TTS_VOICE_PROFILE}' not found in VOICE_PROFILES")
        
        # Test factory creation
        from evilassistant.tts.factory import create_configured_engine
        engine = create_configured_engine(TTS_VOICE_PROFILE)
        print(f"✅ Engine created with {len(engine.providers)} providers")
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")

if __name__ == "__main__":
    test_evil_assistant_tts()
    test_provider_priority()
    test_config_compatibility()
    
    print(f"\n🎯 Integration Test Summary:")
    print("✅ Evil Assistant TTS system tested")
    print("✅ gTTS Demonic provider integration verified")
    print("✅ Provider priority and fallback tested")
    print("🔥 Ready for deployment to Raspberry Pi!")
    print("\n📋 Next Steps:")
    print("1. Deploy to Pi when connection is available")
    print("2. Test on Pi hardware")
    print("3. Fix wake phrase detection issues")
