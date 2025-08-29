#!/usr/bin/env python3
"""
Test Chatterbox TTS for demonic voice synthesis
"""

import os
import tempfile
import time
from pathlib import Path

try:
    from chatterbox import ChatterboxTTS
    import pygame
    import numpy as np
    import librosa
    import soundfile as sf
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install chatterbox-tts pygame librosa soundfile")
    exit(1)

def test_demonic_voice():
    """Test Chatterbox TTS with demonic voice synthesis"""
    print("🔥 Testing Chatterbox TTS for Demonic Voice Synthesis")
    print("=" * 60)
    
    # Initialize Chatterbox TTS
    print("🎭 Initializing Chatterbox TTS...")
    try:
        tts = ChatterboxTTS()
        print("✅ Chatterbox TTS initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize Chatterbox TTS: {e}")
        return
    
    # Test phrases for demonic voice
    demonic_phrases = [
        "I am your Evil Assistant, mortal.",
        "Your dark commands please me, human.",
        "The shadows whisper your secrets to me.",
        "What darkness do you seek from the void?",
        "I shall grant your twisted desires."
    ]
    
    # Test different emotion settings for demonic effect
    emotion_settings = [
        {"emotion": "angry", "intensity": 0.8, "name": "Angry Demon"},
        {"emotion": "fearful", "intensity": 0.9, "name": "Fearful Terror"},
        {"emotion": "neutral", "intensity": 0.5, "name": "Cold Evil"},
        # Custom settings for demonic effect
        {"emotion": "angry", "intensity": 1.0, "name": "Pure Rage"},
    ]
    
    print(f"\n🎤 Testing {len(emotion_settings)} demonic voice variations...")
    
    for i, setting in enumerate(emotion_settings):
        print(f"\n🔥 Test {i+1}: {setting['name']}")
        print(f"   Emotion: {setting['emotion']} | Intensity: {setting['intensity']}")
        
        test_phrase = demonic_phrases[i % len(demonic_phrases)]
        print(f"   Text: '{test_phrase}'")
        
        try:
            # Generate audio with emotion control
            start_time = time.time()
            
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_path = tmp_file.name
            
            # Synthesize with emotion control
            audio = tts.generate(
                text=test_phrase,
                emotion=setting["emotion"],
                emotion_intensity=setting["intensity"],
                sample_rate=22050
            )
            
            generation_time = time.time() - start_time
            print(f"   ⚡ Generation time: {generation_time:.3f}s")
            
            # Save audio
            sf.write(output_path, audio, 22050)
            print(f"   💾 Saved to: {output_path}")
            
            # Apply additional demonic effects with librosa
            enhanced_audio = apply_demonic_effects(audio, 22050)
            enhanced_path = output_path.replace('.wav', '_demonic.wav')
            sf.write(enhanced_path, enhanced_audio, 22050)
            print(f"   👹 Enhanced version: {enhanced_path}")
            
            # Play audio (optional)
            if input("   ▶️  Play this audio? (y/n): ").lower() == 'y':
                play_audio(enhanced_path)
            
            print(f"   ✅ Test {i+1} completed successfully!")
            
        except Exception as e:
            print(f"   ❌ Test {i+1} failed: {e}")
            continue
    
    print(f"\n🎯 Chatterbox TTS Demonic Voice Test Complete!")
    print("🔥 Files saved in current directory")

def apply_demonic_effects(audio, sample_rate):
    """Apply additional demonic effects to the audio"""
    try:
        # Convert to numpy array if needed
        if hasattr(audio, 'numpy'):
            audio = audio.numpy()
        elif hasattr(audio, 'detach'):
            audio = audio.detach().cpu().numpy()
        
        # Ensure audio is 1D
        if len(audio.shape) > 1:
            audio = audio.squeeze()
        
        # 1. Pitch shift down for deeper voice
        audio_deep = librosa.effects.pitch_shift(
            y=audio, 
            sr=sample_rate, 
            n_steps=-6  # Lower by 6 semitones
        )
        
        # 2. Add slight reverb effect (simple delay)
        delay_samples = int(0.1 * sample_rate)  # 100ms delay
        reverb_audio = np.zeros(len(audio_deep) + delay_samples)
        reverb_audio[:len(audio_deep)] += audio_deep
        reverb_audio[delay_samples:] += audio_deep * 0.3  # Echo at 30% volume
        
        # 3. Normalize to prevent clipping
        if np.max(np.abs(reverb_audio)) > 0:
            reverb_audio = reverb_audio / np.max(np.abs(reverb_audio)) * 0.9
        
        return reverb_audio[:len(audio_deep)]  # Trim to original length
        
    except Exception as e:
        print(f"   ⚠️  Effects processing failed: {e}")
        return audio

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
        print("   🔊 Playback completed")
        
    except Exception as e:
        print(f"   ❌ Playback failed: {e}")

def test_performance():
    """Test Chatterbox TTS performance metrics"""
    print("\n⚡ Performance Test")
    print("-" * 30)
    
    try:
        tts = ChatterboxTTS()
        test_text = "Performance test for real-time demonic voice synthesis."
        
        # Multiple runs for average
        times = []
        for i in range(5):
            start = time.time()
            audio = tts.generate(
                text=test_text,
                emotion="angry",
                emotion_intensity=0.8
            )
            duration = time.time() - start
            times.append(duration)
            print(f"   Run {i+1}: {duration:.3f}s")
        
        avg_time = sum(times) / len(times)
        text_duration = len(test_text.split()) * 0.6  # Rough estimate
        realtime_factor = avg_time / text_duration if text_duration > 0 else avg_time
        
        print(f"\n📊 Performance Results:")
        print(f"   Average generation time: {avg_time:.3f}s")
        print(f"   Real-time factor: {realtime_factor:.2f}x")
        print(f"   Status: {'✅ Real-time capable' if realtime_factor < 1.0 else '⚠️ Slower than real-time'}")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")

if __name__ == "__main__":
    test_demonic_voice()
    test_performance()
    
    print(f"\n🎭 Next Steps:")
    print("1. Try different emotion combinations")
    print("2. Experiment with custom voice cloning")
    print("3. Integrate into Evil Assistant TTS system")
    print("4. Test on Raspberry Pi for performance")
