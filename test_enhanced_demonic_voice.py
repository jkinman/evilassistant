#!/usr/bin/env python3
"""
Test enhanced demonic voice effects for gTTS
Experiment with different sox effect combinations
"""

import subprocess
import tempfile
import os
import time
from gtts import gTTS

def test_demonic_variations():
    """Test different demonic voice effect combinations"""
    
    test_text = "Your soul belongs to me now, mortal. The darkness awaits your commands."
    
    # Effect variations to test
    effect_profiles = {
        "current": [
            'pitch', '-300',
            'reverb', '40', 
            'bass', '+15',
            'treble', '-8',
            'vol', '0.75',
            'overdrive', '5'
        ],
        
        "deeper_demon": [
            'pitch', '-450',          # Even deeper
            'reverb', '60', '50',     # More reverb with different settings
            'bass', '+20',            # More bass
            'treble', '-12',          # Less treble
            'chorus', '0.6', '0.9', '20', '0.25', '0.4', '3', '-s',  # Choir effect
            'vol', '0.7',
            'overdrive', '8'          # More distortion
        ],
        
        "hellish_echo": [
            'pitch', '-350',
            'echo', '0.8', '0.9', '1000', '0.3',  # Echo effect
            'reverb', '80',           # Heavy reverb
            'bass', '+18',
            'treble', '-10',
            'flanger', '0.6', '0.87', '3.0', '0.9', '0.5', 'sin', '2', '0', '0',  # Flanger
            'vol', '0.65'
        ],
        
        "otherworldly": [
            'pitch', '-400',
            'phaser', '0.8', '0.74', '3', '0.4', '0.5', 'sin',  # Phaser effect
            'reverb', '50', '50',
            'bass', '+22',
            'tremolo', '10',          # Tremolo for unnatural feeling
            'vol', '0.6',
            'overdrive', '10'
        ],
        
        "ancient_evil": [
            'pitch', '-375',
            'reverb', '90', '70',     # Cathedral-like reverb
            'bass', '+25',
            'treble', '-15',
            'delay', '0.5', '0.8',    # Delay effect
            'chorus', '0.5', '0.9', '50', '0.25', '0.4', '2', '-s',
            'vol', '0.55',
            'overdrive', '12'
        ],
        
        "nightmare_whisper": [
            'pitch', '-320',
            'reverb', '100', '80',    # Maximum reverb
            'bass', '+30',            # Maximum bass
            'treble', '-20',          # Minimal treble
            'flanger', '1', '0.5', '2', '0.8', '0.25', 'sin', '2', '0', '0',
            'echo', '0.8', '0.88', '60', '0.4',
            'vol', '0.5',
            'overdrive', '15'
        ]
    }
    
    print("🔥 Testing Enhanced Demonic Voice Effects")
    print("=" * 60)
    
    for profile_name, effects in effect_profiles.items():
        print(f"\n🎭 Testing profile: {profile_name.upper()}")
        print(f"   Effects: {' '.join(effects[:8])}...")  # Show first few effects
        
        try:
            # Generate base gTTS audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as mp3_file:
                mp3_path = mp3_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                wav_path = wav_file.name
            
            # Create gTTS audio
            start_time = time.time()
            tts = gTTS(text=test_text, lang='en', slow=False)
            tts.save(mp3_path)
            
            # Apply sox effects
            sox_cmd = ['sox', mp3_path, wav_path] + effects
            result = subprocess.run(sox_cmd, capture_output=True, text=True, timeout=30)
            
            generation_time = time.time() - start_time
            
            if result.returncode == 0:
                file_size = os.path.getsize(wav_path)
                print(f"   ✅ Generated successfully ({generation_time:.2f}s)")
                print(f"   📊 File size: {file_size} bytes")
                
                # Offer to play
                if input(f"   ▶️  Play {profile_name}? (y/n): ").lower() == 'y':
                    play_audio(wav_path)
                    
                    # Ask for rating
                    rating = input("   ⭐ Rate this voice (1-5): ")
                    print(f"   📝 Rated: {rating}/5")
                
            else:
                print(f"   ❌ Failed: {result.stderr}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        finally:
            # Cleanup
            for file_path in [mp3_path, wav_path]:
                if os.path.exists(file_path):
                    os.unlink(file_path)

def test_realtime_performance():
    """Test which effect profile has the best performance"""
    print("\n⚡ Performance Testing")
    print("-" * 40)
    
    quick_text = "Performance test"
    
    # Simplified profiles for speed testing
    performance_profiles = {
        "fast_demon": ['pitch', '-300', 'bass', '+15', 'vol', '0.75'],
        "balanced_demon": ['pitch', '-350', 'reverb', '40', 'bass', '+18', 'vol', '0.7'],
        "quality_demon": ['pitch', '-400', 'reverb', '60', 'bass', '+20', 'tremolo', '8', 'vol', '0.65']
    }
    
    for profile_name, effects in performance_profiles.items():
        times = []
        
        for i in range(3):  # Test 3 times
            try:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as mp3_file:
                    mp3_path = mp3_file.name
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                    wav_path = wav_file.name
                
                start_time = time.time()
                
                # Generate and process
                tts = gTTS(text=quick_text, lang='en', slow=False)
                tts.save(mp3_path)
                
                sox_cmd = ['sox', mp3_path, wav_path] + effects
                result = subprocess.run(sox_cmd, capture_output=True, timeout=15)
                
                if result.returncode == 0:
                    times.append(time.time() - start_time)
                
            except Exception:
                pass
            finally:
                for file_path in [mp3_path, wav_path]:
                    if os.path.exists(file_path):
                        os.unlink(file_path)
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"   {profile_name}: {avg_time:.3f}s avg")
        else:
            print(f"   {profile_name}: Failed")

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

def recommend_best_profile():
    """Provide recommendations for best demonic voice profile"""
    print("\n🎯 Recommendations")
    print("-" * 30)
    print("Based on testing, here are the recommended profiles:")
    print()
    print("🏃 FAST (Evil Assistant Real-time):")
    print("   ['pitch', '-300', 'bass', '+15', 'vol', '0.75']")
    print()
    print("⚖️  BALANCED (Good quality + speed):")
    print("   ['pitch', '-350', 'reverb', '40', 'bass', '+18', 'vol', '0.7']")
    print()
    print("👑 PREMIUM (Maximum demonic quality):")
    print("   ['pitch', '-400', 'reverb', '60', 'bass', '+20', 'tremolo', '8', 'vol', '0.65']")
    print()
    print("😈 NIGHTMARE (Ultimate evil, slower):")
    print("   ['pitch', '-450', 'reverb', '90', 'bass', '+25', 'chorus', '0.6', '0.9', '20', '0.25', '0.4', '3', '-s', 'vol', '0.6']")

if __name__ == "__main__":
    # Check if sox is available
    try:
        subprocess.run(['sox', '--version'], capture_output=True, check=True)
        print("✅ SoX is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ SoX not found. Install with: brew install sox")
        exit(1)
    
    test_demonic_variations()
    test_realtime_performance()
    recommend_best_profile()
    
    print("\n🔥 Test Complete!")
    print("Choose your favorite profile to implement in gTTS Demonic provider!")
