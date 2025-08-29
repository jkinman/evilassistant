#!/usr/bin/env python3
"""
Advanced demonic voice experiments - trying different approaches
"""

import tempfile
import os
import subprocess
import time
from gtts import gTTS

def test_experimental_techniques():
    """Test various advanced demonic voice techniques"""
    
    test_text = "I am your demonic overlord. Bow before my dark power!"
    
    # Experimental techniques to try
    experiments = {
        "method_1_speed_then_pitch": [
            'speed', '0.6',           # Slow down first (makes voice deeper naturally)
            'pitch', '-400',          # Then pitch shift
            'bass', '+25',
            'reverb', '50',
            'vol', '0.8'
        ],
        
        "method_2_formant_shift": [
            'pitch', '-600',
            'bend', '0.3,400,0.35,400',  # Formant bending for unnatural sound
            'bass', '+30',
            'reverb', '40',
            'vol', '0.75'
        ],
        
        "method_3_multiple_pitch": [
            'pitch', '-300',          # First pitch shift
            'pitch', '-300',          # Second pitch shift (compounds)
            'bass', '+20',
            'reverb', '30',
            'vol', '0.9'
        ],
        
        "method_4_octave_down": [
            'pitch', '-1200',         # Full octave down
            'speed', '0.8',           # Slightly slower
            'bass', '+35',
            'treble', '-20',
            'vol', '1.0'
        ],
        
        "method_5_vocal_tract": [
            'pitch', '-500',
            'allpass', '50',          # Vocal tract simulation
            'bass', '+25',
            'reverb', '60',
            'tremolo', '5',
            'vol', '0.8'
        ],
        
        "method_6_distortion_heavy": [
            'pitch', '-700',
            'overdrive', '15',        # Heavy overdrive
            'bass', '+40',
            'treble', '-25',
            'reverb', '30',
            'vol', '0.7'
        ],
        
        "method_7_chorus_demon": [
            'pitch', '-800',
            'chorus', '0.8', '0.9', '55', '0.4', '0.25', '2', '-s',  # Multiple voice effect
            'bass', '+30',
            'reverb', '70',
            'vol', '0.75'
        ],
        
        "method_8_flanger_evil": [
            'pitch', '-600',
            'flanger', '2', '5', '95', '75', '0.25', 'sin', '2', '0', '0',  # Whooshing effect
            'bass', '+25',
            'overdrive', '8',
            'vol', '0.8'
        ],
        
        "method_9_echo_chamber": [
            'pitch', '-750',
            'echo', '0.8', '0.88', '1000', '0.4',  # Long echo
            'echo', '0.6', '0.5', '1800', '0.2',   # Second echo
            'bass', '+35',
            'vol', '0.7'
        ],
        
        "method_10_robotic_demon": [
            'pitch', '-650',
            'vocoder', '40', '0.5',   # Robotic effect
            'bass', '+30',
            'overdrive', '10',
            'vol', '0.8'
        ]
    }
    
    print("🔥 ADVANCED DEMONIC VOICE EXPERIMENTS")
    print("=" * 60)
    print("Testing various audio processing techniques...")
    
    successful_methods = []
    
    for method_name, effects in experiments.items():
        print(f"\n🧪 Experiment: {method_name.upper()}")
        print(f"   Technique: {', '.join(effects[:6])}...")
        
        try:
            # Generate base gTTS
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as mp3_file:
                mp3_path = mp3_file.name
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                wav_path = wav_file.name
            
            # Create slower gTTS for better base
            start_time = time.time()
            tts = gTTS(text=test_text, lang='en', slow=True, tld='com.au')
            tts.save(mp3_path)
            
            # Apply experimental effects
            sox_cmd = ['sox', mp3_path, wav_path] + effects
            result = subprocess.run(sox_cmd, capture_output=True, text=True, timeout=30)
            
            generation_time = time.time() - start_time
            
            if result.returncode == 0:
                file_size = os.path.getsize(wav_path)
                print(f"   ✅ Success! ({generation_time:.2f}s, {file_size} bytes)")
                
                if input(f"   ▶️  Play {method_name}? (y/n): ").lower() == 'y':
                    play_audio(wav_path)
                    
                    # Rate the experiment
                    depth_rating = input("   🎚️  Depth (1-5): ")
                    demonic_rating = input("   😈 Demonic quality (1-5): ")
                    clarity_rating = input("   🗣️  Clarity (1-5): ")
                    coolness_rating = input("   🔥 Overall coolness (1-5): ")
                    
                    scores = {
                        'depth': depth_rating,
                        'demonic': demonic_rating, 
                        'clarity': clarity_rating,
                        'coolness': coolness_rating
                    }
                    
                    print(f"   📊 Scores: D:{depth_rating} E:{demonic_rating} C:{clarity_rating} O:{coolness_rating}")
                    
                    # Track successful methods
                    if int(coolness_rating) >= 4:
                        successful_methods.append((method_name, effects, scores))
                        print("   🌟 MARKED AS PROMISING!")
                    
            else:
                error_msg = result.stderr.split('\n')[0] if result.stderr else "Unknown error"
                print(f"   ❌ Failed: {error_msg}")
                
        except subprocess.TimeoutExpired:
            print("   ⏰ Timeout - too complex")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        finally:
            # Cleanup
            for file_path in [mp3_path, wav_path]:
                if os.path.exists(file_path):
                    os.unlink(file_path)
    
    return successful_methods

def test_best_combinations(successful_methods):
    """Create hybrid combinations of the best techniques"""
    if not successful_methods:
        print("\n⚠️  No successful methods to combine")
        return
    
    print(f"\n🔬 CREATING HYBRID COMBINATIONS")
    print("=" * 50)
    print("Combining the best elements from successful experiments...")
    
    # Create hybrid combinations
    hybrids = {
        "ultra_hybrid_v1": [
            'speed', '0.7',           # From method_1
            'pitch', '-800',          # Deep pitch
            'chorus', '0.7', '0.85', '45', '0.3', '0.2', '2', '-s',  # From method_7
            'bass', '+35',
            'reverb', '50',
            'vol', '0.8'
        ],
        
        "ultra_hybrid_v2": [
            'pitch', '-1000',         # From method_4
            'overdrive', '12',        # From method_6
            'echo', '0.8', '0.9', '800', '0.3',  # From method_9
            'bass', '+40',
            'treble', '-20',
            'vol', '0.75'
        ],
        
        "balanced_hybrid": [
            'speed', '0.8',
            'pitch', '-600',
            'bass', '+30',
            'reverb', '40',
            'tremolo', '6',
            'overdrive', '8',
            'vol', '0.8'
        ]
    }
    
    test_text = "Behold the ultimate demonic voice synthesis!"
    
    for hybrid_name, effects in hybrids.items():
        print(f"\n🧬 Hybrid: {hybrid_name.upper()}")
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as mp3_file:
                mp3_path = mp3_file.name
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                wav_path = wav_file.name
            
            # Generate base
            tts = gTTS(text=test_text, lang='en', slow=True, tld='com.au')
            tts.save(mp3_path)
            
            # Apply hybrid effects
            sox_cmd = ['sox', mp3_path, wav_path] + effects
            result = subprocess.run(sox_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"   ✅ Hybrid generated successfully!")
                
                if input(f"   ▶️  Play {hybrid_name}? (y/n): ").lower() == 'y':
                    play_audio(wav_path)
                    
                    final_rating = input("   ⭐ Final rating (1-5): ")
                    print(f"   🏆 {hybrid_name}: {final_rating}/5")
            else:
                print(f"   ❌ Hybrid failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        finally:
            for file_path in [mp3_path, wav_path]:
                if os.path.exists(file_path):
                    os.unlink(file_path)

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

def summarize_findings():
    """Summarize what we learned"""
    print("\n📋 EXPERIMENT SUMMARY")
    print("=" * 40)
    print("🔬 Techniques tested:")
    print("   • Speed adjustment before pitch")
    print("   • Formant bending")
    print("   • Multiple pitch shifts")
    print("   • Full octave drops")
    print("   • Vocal tract simulation")
    print("   • Heavy distortion")
    print("   • Chorus effects")
    print("   • Flanger effects")
    print("   • Echo chambers")
    print("   • Robotic effects")
    print()
    print("🎯 Best findings will be integrated into gTTS provider!")

if __name__ == "__main__":
    # Check sox availability
    try:
        subprocess.run(['sox', '--version'], capture_output=True, check=True)
        print("✅ SoX available for experiments")
    except:
        print("❌ SoX required for experiments")
        exit(1)
    
    successful_methods = test_experimental_techniques()
    test_best_combinations(successful_methods)
    summarize_findings()
    
    print("\n🔥 Choose your favorite techniques for the Evil Assistant!")
