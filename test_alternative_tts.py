#!/usr/bin/env python3
"""
Test multiple TTS alternatives for demonic voice synthesis
"""

import os
import tempfile
import time
import subprocess
from pathlib import Path

def test_gTTS_with_effects():
    """Test Google TTS (gTTS) with audio effects for demonic voice"""
    print("🔥 Testing gTTS + Audio Effects")
    print("-" * 40)
    
    try:
        from gtts import gTTS
        import pygame
        print("✅ gTTS available")
        
        # Test phrase
        text = "I am your Evil Assistant, mortal. What darkness do you seek?"
        
        # Generate base TTS
        tts = gTTS(text=text, lang='en', slow=False)
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            base_file = tmp_file.name
        
        start_time = time.time()
        tts.save(base_file)
        generation_time = time.time() - start_time
        
        print(f"⚡ Generation time: {generation_time:.3f}s")
        
        # Apply demonic effects with sox (if available)
        demonic_file = base_file.replace('.mp3', '_demonic.wav')
        
        try:
            # Convert to WAV and apply effects
            sox_cmd = [
                'sox', base_file, demonic_file,
                'pitch', '-300',      # Lower pitch significantly
                'reverb', '50',       # Add reverb
                'bass', '+10',        # Boost bass
                'vol', '0.8'          # Reduce volume to prevent clipping
            ]
            
            result = subprocess.run(sox_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Applied demonic effects with sox")
                print(f"💾 Demonic version: {demonic_file}")
                
                if input("▶️  Play demonic gTTS? (y/n): ").lower() == 'y':
                    play_audio(demonic_file)
            else:
                print(f"⚠️  Sox effects failed: {result.stderr}")
                
        except FileNotFoundError:
            print("⚠️  Sox not found - install with: brew install sox")
        
        # Cleanup
        os.unlink(base_file)
        if os.path.exists(demonic_file):
            os.unlink(demonic_file)
            
    except ImportError:
        print("❌ gTTS not available. Install with: pip install gTTS")
    except Exception as e:
        print(f"❌ gTTS test failed: {e}")

def test_edge_tts():
    """Test Microsoft Edge TTS (free, high quality)"""
    print("\n🔥 Testing Microsoft Edge TTS")
    print("-" * 40)
    
    try:
        import edge_tts
        import asyncio
        import pygame
        print("✅ Edge TTS available")
        
        async def generate_edge_voice():
            # Test different voices for demonic effect
            demonic_voices = [
                "en-US-ChristopherNeural",  # Deep male voice
                "en-GB-RyanNeural",         # British male
                "en-US-GuyNeural",          # Another deep male
            ]
            
            text = "Your soul belongs to me now, mortal. I am the Evil Assistant."
            
            for voice in demonic_voices:
                print(f"\n🎭 Testing voice: {voice}")
                
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    output_file = tmp_file.name
                
                start_time = time.time()
                
                # Generate with Edge TTS
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_file)
                
                generation_time = time.time() - start_time
                print(f"⚡ Generation time: {generation_time:.3f}s")
                print(f"💾 Saved: {output_file}")
                
                # Apply demonic effects
                demonic_file = apply_pitch_effects(output_file)
                
                if input(f"▶️  Play {voice}? (y/n): ").lower() == 'y':
                    play_audio(demonic_file if demonic_file else output_file)
                
                # Cleanup
                os.unlink(output_file)
                if demonic_file and os.path.exists(demonic_file):
                    os.unlink(demonic_file)
        
        # Run async function
        asyncio.run(generate_edge_voice())
        
    except ImportError:
        print("❌ Edge TTS not available. Install with: pip install edge-tts")
    except Exception as e:
        print(f"❌ Edge TTS test failed: {e}")

def test_coqui_tts():
    """Test Coqui TTS (open source, high quality)"""
    print("\n🔥 Testing Coqui TTS")
    print("-" * 40)
    
    try:
        from TTS.api import TTS
        print("✅ Coqui TTS available")
        
        # Initialize TTS with a good model
        # Using a fast, English model
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
        
        text = "Darkness rises, and your Evil Assistant awakens from the void."
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_file = tmp_file.name
        
        start_time = time.time()
        tts.tts_to_file(text=text, file_path=output_file)
        generation_time = time.time() - start_time
        
        print(f"⚡ Generation time: {generation_time:.3f}s")
        print(f"💾 Saved: {output_file}")
        
        # Apply demonic effects
        demonic_file = apply_pitch_effects(output_file)
        
        if input("▶️  Play Coqui TTS? (y/n): ").lower() == 'y':
            play_audio(demonic_file if demonic_file else output_file)
        
        # Cleanup
        os.unlink(output_file)
        if demonic_file and os.path.exists(demonic_file):
            os.unlink(demonic_file)
            
    except ImportError:
        print("❌ Coqui TTS not available. Install with: pip install TTS")
    except Exception as e:
        print(f"❌ Coqui TTS test failed: {e}")

def apply_pitch_effects(input_file):
    """Apply pitch-shifting and other demonic effects"""
    try:
        output_file = input_file.replace('.wav', '_demonic.wav')
        
        sox_cmd = [
            'sox', input_file, output_file,
            'pitch', '-400',      # Much lower pitch
            'reverb', '40',       # Reverb
            'bass', '+15',        # Heavy bass boost
            'treble', '-5',       # Reduce treble
            'vol', '0.7'          # Prevent clipping
        ]
        
        result = subprocess.run(sox_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"👹 Applied demonic effects: {output_file}")
            return output_file
        else:
            print(f"⚠️  Effects failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"⚠️  Effects error: {e}")
        return None

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
        print("🔊 Playback completed")
        
    except Exception as e:
        print(f"❌ Playback failed: {e}")

def performance_comparison():
    """Compare performance of different TTS engines"""
    print("\n📊 Performance Comparison")
    print("=" * 50)
    
    test_text = "Performance test for real-time synthesis"
    
    results = []
    
    # Test each engine and record performance
    engines = [
        ("gTTS", test_gtts_performance),
        ("Edge TTS", test_edge_performance),
        # ("Coqui TTS", test_coqui_performance),  # Skip due to Python 3.13 issues
    ]
    
    for name, test_func in engines:
        try:
            duration = test_func(test_text)
            if duration:
                results.append((name, duration))
                realtime_factor = duration / 2.0  # Rough estimate
                status = "✅ Real-time" if realtime_factor < 1.0 else "⚠️ Slow"
                print(f"{name:12} | {duration:6.3f}s | {status}")
        except Exception as e:
            print(f"{name:12} | ERROR   | {e}")
    
    if results:
        fastest = min(results, key=lambda x: x[1])
        print(f"\n🏆 Fastest: {fastest[0]} ({fastest[1]:.3f}s)")

def test_gtts_performance(text):
    """Test gTTS performance"""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            start = time.time()
            tts.save(tmp_file.name)
            duration = time.time() - start
            os.unlink(tmp_file.name)
            return duration
    except:
        return None

def test_edge_performance(text):
    """Test Edge TTS performance"""
    try:
        import edge_tts
        import asyncio
        
        async def generate():
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                start = time.time()
                communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
                await communicate.save(tmp_file.name)
                duration = time.time() - start
                os.unlink(tmp_file.name)
                return duration
        
        return asyncio.run(generate())
    except:
        return None

def test_coqui_performance(text):
    """Test Coqui TTS performance"""
    try:
        from TTS.api import TTS
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            start = time.time()
            tts.tts_to_file(text=text, file_path=tmp_file.name)
            duration = time.time() - start
            os.unlink(tmp_file.name)
            return duration
    except:
        return None

if __name__ == "__main__":
    print("🎭 Testing Multiple TTS Engines for Demonic Voice")
    print("=" * 60)
    
    # Test available TTS engines  
    test_gTTS_with_effects()
    test_edge_tts()
    # Skip Coqui TTS (Python 3.13 compatibility issues)
    # test_coqui_tts()
    
    # Performance comparison (limited to available engines)
    performance_comparison()
    
    print(f"\n🎯 Recommendations:")
    print("1. 🏆 Edge TTS: Fastest, free, high quality, great for real-time")
    print("2. 🎨 Coqui TTS: Open source, customizable, good quality")
    print("3. 🌐 gTTS: Simple, reliable, requires internet")
    print("4. 🔥 Apply sox effects for demonic transformation")
    print("\n💡 Next: Integrate best option into Evil Assistant!")
