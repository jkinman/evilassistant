#!/usr/bin/env python3
"""
Quick voice profile tester for Evil Assistant
Easily compare different demonic voice profiles
"""

import tempfile
import os
from evilassistant.tts.config import TTSConfig
from evilassistant.tts.engine import TTSEngine

def test_voice_profiles():
    """Quick tester for different voice profiles"""
    
    # All available profiles
    profiles = [
        "fast_demon",
        "balanced_demon", 
        "experimental_deep",
        "demon_lord",
        "premium_demon",
        "nightmare_whisper",
        "ancient_evil",
        "brutal_overlord"
    ]
    
    test_phrase = "I am your demonic overlord testing voice profiles."
    
    print("🎭 EVIL ASSISTANT VOICE PROFILE TESTER")
    print("=" * 60)
    print(f"Test phrase: '{test_phrase}'")
    print()
    
    for i, profile in enumerate(profiles, 1):
        print(f"{i}. {profile}")
    
    while True:
        try:
            choice = input(f"\nChoose profile to test (1-{len(profiles)}) or 'q' to quit: ")
            
            if choice.lower() == 'q':
                break
                
            profile_idx = int(choice) - 1
            if 0 <= profile_idx < len(profiles):
                profile_name = profiles[profile_idx]
                test_profile(profile_name, test_phrase)
            else:
                print("Invalid choice!")
                
        except (ValueError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

def test_profile(profile_name, text):
    """Test a specific profile"""
    print(f"\n🎯 Testing: {profile_name.upper()}")
    
    try:
        # Create engine with specific profile
        engine = TTSEngine()
        gtts_config = TTSConfig(effects=[profile_name])
        engine.add_provider("gtts_demonic", gtts_config)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_file = tmp_file.name
        
        try:
            import time
            start_time = time.time()
            success = engine.synthesize(text, output_file)
            gen_time = time.time() - start_time
            
            if success:
                file_size = os.path.getsize(output_file)
                print(f"   ✅ Generated in {gen_time:.2f}s ({file_size} bytes)")
                
                play_choice = input("   ▶️  Play this profile? (y/n): ")
                if play_choice.lower() == 'y':
                    play_audio(output_file)
                    
                    # Quick rating
                    rating = input("   ⭐ Rate this profile (1-5): ")
                    if rating.isdigit():
                        print(f"   📊 {profile_name}: {rating}/5")
                        
                        if int(rating) >= 4:
                            print(f"   🏆 {profile_name} is a winner!")
                            
                            set_default = input("   🎯 Set as new default? (y/n): ")
                            if set_default.lower() == 'y':
                                update_default_profile(profile_name)
            else:
                print("   ❌ Generation failed")
                
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
                
    except Exception as e:
        print(f"   ❌ Error: {e}")

def play_audio(file_path):
    """Play audio file"""
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            import time
            time.sleep(0.1)
        pygame.mixer.quit()
        print("   🔊 Playback completed")
        
    except Exception as e:
        print(f"   ❌ Playback failed: {e}")

def update_default_profile(profile_name):
    """Update the default profile in factory.py"""
    try:
        factory_file = "evilassistant/tts/factory.py"
        
        with open(factory_file, 'r') as f:
            content = f.read()
        
        # Update the profile
        import re
        pattern = r'TTSConfig\(effects=\["[^"]+"\]\)'
        replacement = f'TTSConfig(effects=["{profile_name}"])'
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            with open(factory_file, 'w') as f:
                f.write(new_content)
            print(f"   ✅ Updated default profile to: {profile_name}")
            print("   🔄 Restart Evil Assistant to use new default")
        else:
            print("   ⚠️  Could not update default profile")
            
    except Exception as e:
        print(f"   ❌ Failed to update default: {e}")

def show_profile_info():
    """Show information about each profile"""
    info = {
        "fast_demon": "Moderate depth, optimized for speed",
        "balanced_demon": "Double pitch shift, good balance", 
        "experimental_deep": "Based on our experiments, double -400 pitch",
        "demon_lord": "Balanced clarity and depth",
        "premium_demon": "Triple pitch shift, maximum effects",
        "nightmare_whisper": "Deep whisper with echo",
        "ancient_evil": "Cathedral reverb with choir effect",
        "brutal_overlord": "Maximum depth and distortion"
    }
    
    print("\n📋 VOICE PROFILE INFORMATION")
    print("-" * 50)
    for profile, description in info.items():
        print(f"• {profile}: {description}")

if __name__ == "__main__":
    show_profile_info()
    test_voice_profiles()
    print("\n🔥 Voice testing complete!")
