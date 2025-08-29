#!/usr/bin/env python3
"""
Test the enhanced masculine demonic voice
"""

import tempfile
import os
import time

def test_masculine_profiles():
    """Test different masculine demonic voice profiles"""
    
    test_phrases = [
        "Your soul is mine, mortal fool.",
        "I am the ancient evil that haunts your dreams.",
        "Bow before your dark overlord.",
        "The abyss calls your name, human.",
        "Your pathetic existence amuses me."
    ]
    
    # Test profiles optimized for masculine sound
    profiles = ["fast_demon", "balanced_demon", "premium_demon", "nightmare_whisper", "brutal_overlord"]
    
    print("🔥 Testing Masculine Demonic Voice Profiles")
    print("=" * 60)
    
    for profile in profiles:
        print(f"\n👹 Testing Profile: {profile.upper()}")
        print("-" * 40)
        
        try:
            from evilassistant.tts.factory import create_configured_engine
            from evilassistant.tts.config import TTSConfig
            
            # Create engine with specific profile
            engine = create_configured_engine()
            
            # Override the gTTS config to use this specific profile
            gtts_config = TTSConfig(effects=[profile])
            engine.providers = []  # Clear existing
            engine.add_provider("gtts_demonic", gtts_config)
            
            # Test synthesis
            test_text = f"I am testing the {profile.replace('_', ' ')} voice profile."
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            try:
                start_time = time.time()
                success = engine.synthesize(test_text, output_file)
                generation_time = time.time() - start_time
                
                if success:
                    file_size = os.path.getsize(output_file)
                    print(f"   ✅ Generated successfully ({generation_time:.2f}s)")
                    print(f"   📊 File size: {file_size} bytes")
                    print(f"   📝 Text: '{test_text}'")
                    
                    # Offer to play
                    if input(f"   ▶️  Play {profile}? (y/n): ").lower() == 'y':
                        play_audio(output_file)
                        
                        # Rate masculinity
                        masculinity = input("   💪 Rate masculinity (1-5, 5=very masculine): ")
                        demon_quality = input("   😈 Rate demonic quality (1-5, 5=very demonic): ")
                        print(f"   📊 Masculinity: {masculinity}/5, Demonic: {demon_quality}/5")
                else:
                    print("   ❌ Generation failed")
                    
            finally:
                if os.path.exists(output_file):
                    os.unlink(output_file)
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_evil_assistant_integration():
    """Test with actual Evil Assistant phrases"""
    print("\n🎭 Testing Evil Assistant Integration")
    print("-" * 50)
    
    evil_phrases = [
        "Your dark commands please me, mortal.",
        "I have turned your lights to the color of hellfire!",
        "The shadows whisper your secrets to me.",
        "What darkness do you seek from the void, human?",
        "My surveillance is now active. All shall be recorded."
    ]
    
    try:
        from evilassistant.assistant_clean import AudioHandler
        
        audio_handler = AudioHandler()
        
        for i, phrase in enumerate(evil_phrases, 1):
            print(f"\n🔥 Evil Assistant Test {i}")
            print(f"   Text: '{phrase}'")
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            try:
                start_time = time.time()
                success = audio_handler.synthesize_speech(phrase, output_file)
                generation_time = time.time() - start_time
                
                if success:
                    print(f"   ✅ Evil Assistant TTS successful ({generation_time:.2f}s)")
                    
                    if input(f"   ▶️  Play Evil response {i}? (y/n): ").lower() == 'y':
                        play_audio(output_file)
                else:
                    print("   ❌ Evil Assistant TTS failed")
                    
            finally:
                if os.path.exists(output_file):
                    os.unlink(output_file)
                    
    except Exception as e:
        print(f"❌ Evil Assistant integration test failed: {e}")

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

def summarize_improvements():
    """Summarize the masculine voice improvements"""
    print("\n🎯 Masculine Voice Improvements")
    print("=" * 50)
    print("✅ Base Voice Changes:")
    print("   • gTTS slow=True for deeper base voice")
    print("   • Australian TLD (com.au) for voice variation")
    print("   • Slower speech pattern for more menacing effect")
    print()
    print("✅ Pitch Adjustments:")
    print("   • Increased pitch drop: -500 to -650 cents")
    print("   • Much deeper than original -300 cents")
    print("   • Counteracts feminine gTTS voice")
    print()
    print("✅ Audio Effects:")
    print("   • Increased bass boost: +20 to +40")
    print("   • Reduced treble: -10 to -25")
    print("   • Added overdrive for masculine growl")
    print("   • Optimized volume levels")
    print()
    print("✅ New Profiles:")
    print("   • brutal_overlord: Maximum masculinity")
    print("   • premium_demon: Default balanced masculine")
    print("   • nightmare_whisper: Deep masculine whisper")
    print()
    print("🔥 Result: Deep, masculine, demonic voice!")

if __name__ == "__main__":
    test_masculine_profiles()
    test_evil_assistant_integration()
    summarize_improvements()
    
    print("\n💀 The feminine voice has been banished to the depths!")
    print("🔥 Behold the masculine demon overlord voice!")
