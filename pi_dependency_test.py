#!/usr/bin/env python3
"""
Raspberry Pi Specific Dependency Test
Run this script ON your Raspberry Pi to verify all dependencies work correctly.
"""

import subprocess
import sys
import platform
import os

def print_header(title):
    print(f"\n🔍 {title}")
    print("=" * (len(title) + 4))

def test_command(cmd, description):
    """Test a system command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {description}: OK")
            return True
        else:
            print(f"❌ {description}: Failed (exit {result.returncode})")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return False

def test_python_import(module, description):
    """Test Python module import"""
    try:
        __import__(module)
        print(f"✅ {description}: Import OK")
        return True
    except ImportError as e:
        print(f"❌ {description}: Import failed - {e}")
        return False

def check_pi_hardware():
    """Check Pi-specific hardware"""
    print_header("Raspberry Pi Hardware Detection")
    
    # Check if we're on a Pi
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
        print(f"✅ Hardware: {model}")
        is_pi = "Raspberry Pi" in model
    except:
        print("❌ Hardware: Not a Raspberry Pi")
        is_pi = False
    
    # Check architecture
    arch = platform.machine()
    print(f"✅ Architecture: {arch}")
    
    # Check memory
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if 'MemTotal:' in line:
                    mem_kb = int(line.split()[1])
                    mem_gb = mem_kb / (1024 * 1024)
                    print(f"✅ Memory: {mem_gb:.1f} GB")
                    break
    except:
        print("❌ Memory: Could not detect")
    
    # Check temperature
    try:
        temp_result = subprocess.run(['vcgencmd', 'measure_temp'], 
                                   capture_output=True, text=True)
        if temp_result.returncode == 0:
            temp = temp_result.stdout.strip()
            print(f"✅ Temperature: {temp}")
        else:
            print("⚠️  Temperature: vcgencmd not available")
    except:
        print("⚠️  Temperature: Cannot check")
    
    return is_pi

def check_audio_system():
    """Check Pi audio system"""
    print_header("Audio System Check")
    
    tests = [
        ("aplay -l", "Audio playback devices"),
        ("arecord -l", "Audio recording devices"),
        ("pulseaudio --check", "PulseAudio daemon"),
    ]
    
    success = 0
    for cmd, desc in tests:
        if test_command(cmd, desc):
            success += 1
    
    # Test actual audio functionality
    print("\n🎵 Testing Audio Functionality:")
    
    # Test espeak
    if test_command("espeak 'Pi audio test' 2>/dev/null", "espeak audio output"):
        success += 1
    
    # Test recording (brief)
    if test_command("timeout 1s arecord -f cd /tmp/test_rec.wav 2>/dev/null", "Audio recording"):
        success += 1
        # Cleanup
        subprocess.run(["rm", "-f", "/tmp/test_rec.wav"], capture_output=True)
    
    return success

def check_python_environment():
    """Check Python dependencies"""
    print_header("Python Environment Check")
    
    # Core dependencies
    deps = [
        ("faster_whisper", "Faster Whisper STT"),
        ("pygame", "Pygame audio"),
        ("numpy", "NumPy"),
        ("requests", "HTTP requests"),
        ("sounddevice", "Sound device"),
        ("piper", "Piper TTS"),
        ("phue", "Philips Hue"),
        ("dotenv", "Python dotenv"),
    ]
    
    success = 0
    for module, desc in deps:
        if test_python_import(module, desc):
            success += 1
    
    return success, len(deps)

def check_tts_system():
    """Check TTS functionality"""
    print_header("TTS System Check")
    
    # Test espeak
    espeak_ok = test_command("espeak 'Testing espeak TTS' 2>/dev/null", "espeak synthesis")
    
    # Test sox effects
    sox_ok = test_command("sox --version", "sox audio effects")
    
    # Test Piper (if available)
    piper_ok = False
    try:
        from evilassistant.tts import create_configured_engine
        engine = create_configured_engine('piper_ryan_demonic')
        success = engine.synthesize("Pi TTS test", "/tmp/pi_tts_test.wav")
        if success and os.path.exists("/tmp/pi_tts_test.wav"):
            print("✅ Piper TTS: Synthesis OK")
            piper_ok = True
            # Cleanup
            os.remove("/tmp/pi_tts_test.wav")
        else:
            print("❌ Piper TTS: Synthesis failed")
    except Exception as e:
        print(f"❌ Piper TTS: Error - {e}")
    
    return [espeak_ok, sox_ok, piper_ok]

def check_system_resources():
    """Check system resources and performance"""
    print_header("System Resources")
    
    # CPU info
    try:
        with open('/proc/cpuinfo', 'r') as f:
            lines = f.readlines()
        
        # Count CPU cores
        cores = len([line for line in lines if line.startswith('processor')])
        print(f"✅ CPU cores: {cores}")
        
        # Get CPU model
        for line in lines:
            if line.startswith('Model'):
                model = line.split(':')[1].strip()
                print(f"✅ CPU model: {model}")
                break
    except:
        print("⚠️  CPU info: Could not read")
    
    # Disk space
    if test_command("df -h .", "Disk space check"):
        pass
    
    # Load average
    try:
        load = os.getloadavg()
        print(f"✅ Load average: {load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}")
    except:
        print("⚠️  Load average: Not available")

def main():
    print("🍓 Raspberry Pi Evil Assistant Dependency Check")
    print("=" * 50)
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    
    # Run all checks
    is_pi = check_pi_hardware()
    audio_score = check_audio_system()
    py_success, py_total = check_python_environment()
    tts_results = check_tts_system()
    check_system_resources()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    
    print(f"🍓 Raspberry Pi detected: {'✅ YES' if is_pi else '❌ NO'}")
    print(f"🔊 Audio system: {audio_score}/5 tests passed")
    print(f"🐍 Python deps: {py_success}/{py_total} working")
    print(f"🎭 TTS engines: {sum(tts_results)}/3 working")
    
    total_possible = 5 + py_total + 3 + (1 if is_pi else 0)
    total_passed = audio_score + py_success + sum(tts_results) + (1 if is_pi else 0)
    
    percentage = (total_passed / total_possible) * 100
    
    print(f"\n🎯 Overall Score: {total_passed}/{total_possible} ({percentage:.1f}%)")
    
    if percentage >= 90:
        print("🎉 EXCELLENT! Evil Assistant should work perfectly on this Pi.")
    elif percentage >= 75:
        print("✅ GOOD! Minor issues but should work well.")
    elif percentage >= 60:
        print("⚠️  PARTIAL! Some features may not work correctly.")
    else:
        print("❌ POOR! Significant issues detected.")
    
    print("\n🚀 Ready to test the full Evil Assistant!")
    print("   Run: python -m evilassistant")

if __name__ == "__main__":
    main()
