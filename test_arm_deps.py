#!/usr/bin/env python3
"""
ARM Dependency Verification Script
Run this to verify packages work correctly before Pi deployment.
"""

import subprocess
import sys
import platform
import importlib.util

def test_import(package_name, import_name=None):
    """Test if a package can be imported"""
    if import_name is None:
        import_name = package_name
    
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            print(f"❌ {package_name}: Module not found")
            return False
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Get version if available
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name}: Import successful (v{version})")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: Import failed - {e}")
        return False
    except Exception as e:
        print(f"⚠️  {package_name}: Import warning - {e}")
        return False

def test_system_command(command, package_name):
    """Test if a system command is available"""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0] if result.stdout else result.stderr.split('\n')[0]
            print(f"✅ {package_name}: {version_line}")
            return True
        else:
            print(f"❌ {package_name}: Command failed (exit {result.returncode})")
            return False
    except FileNotFoundError:
        print(f"❌ {package_name}: Command not found")
        return False
    except subprocess.TimeoutExpired:
        print(f"⚠️  {package_name}: Command timeout")
        return False

def test_audio_devices():
    """Test audio device availability"""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        output_devices = [d for d in devices if d['max_output_channels'] > 0]
        
        print(f"🎤 Input devices found: {len(input_devices)}")
        print(f"🔊 Output devices found: {len(output_devices)}")
        
        if len(input_devices) > 0 and len(output_devices) > 0:
            print("✅ Audio devices: Available")
            return True
        else:
            print("⚠️  Audio devices: Limited availability")
            return False
    except Exception as e:
        print(f"❌ Audio devices: Error - {e}")
        return False

def test_tts_functionality():
    """Test TTS system functionality"""
    try:
        # Test if we can create a TTS engine
        from evilassistant.tts import create_configured_engine
        engine = create_configured_engine('piper_ryan_demonic')
        
        # Test synthesis to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as tmp:
            success = engine.synthesize("ARM compatibility test", tmp.name)
            if success:
                provider = engine.get_current_provider()
                print(f"✅ TTS System: Working with {provider}")
                return True
            else:
                print("❌ TTS System: Synthesis failed")
                return False
    except Exception as e:
        print(f"❌ TTS System: Error - {e}")
        return False

def main():
    print("🔍 ARM Dependency Verification for Evil Assistant")
    print("=" * 50)
    print(f"Platform: {platform.machine()}")
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print()
    
    # Test Python packages
    python_deps = [
        ("faster-whisper", "faster_whisper"),
        ("pygame", "pygame"),
        ("numpy", "numpy"),
        ("requests", "requests"),
        ("httpx", "httpx"),
        ("sounddevice", "sounddevice"),
        ("scipy", "scipy"),
        ("python-dotenv", "dotenv"),
        ("piper-tts", "piper"),
        ("phue", "phue"),
    ]
    
    print("📚 Testing Python Dependencies:")
    print("-" * 30)
    py_success = 0
    for pkg, imp in python_deps:
        if test_import(pkg, imp):
            py_success += 1
    
    print()
    
    # Test system commands
    system_deps = [
        ("espeak", "espeak"),
        ("sox", "sox"),
        ("aplay", "alsa-utils"),
    ]
    
    print("🖥️  Testing System Dependencies:")
    print("-" * 30)
    sys_success = 0
    for cmd, pkg in system_deps:
        if test_system_command(cmd, pkg):
            sys_success += 1
    
    print()
    
    # Test audio system
    print("🎵 Testing Audio System:")
    print("-" * 30)
    audio_ok = test_audio_devices()
    
    print()
    
    # Test TTS system if available
    print("🎭 Testing TTS System:")
    print("-" * 30)
    tts_ok = test_tts_functionality()
    
    print()
    print("📊 RESULTS SUMMARY:")
    print("=" * 20)
    print(f"Python packages: {py_success}/{len(python_deps)} working")
    print(f"System commands: {sys_success}/{len(system_deps)} working")
    print(f"Audio system: {'✅ OK' if audio_ok else '❌ Issues'}")
    print(f"TTS system: {'✅ OK' if tts_ok else '❌ Issues'}")
    
    total_tests = len(python_deps) + len(system_deps) + 2  # +2 for audio and TTS
    total_passed = py_success + sys_success + (1 if audio_ok else 0) + (1 if tts_ok else 0)
    
    print()
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Ready for Raspberry Pi deployment.")
        print("🍓 The Evil Assistant should work perfectly on ARM architecture.")
    elif total_passed >= total_tests - 2:
        print("⚠️  MOSTLY READY. Minor issues detected but should still work.")
        print("🍓 Consider testing on Pi for final verification.")
    else:
        print("❌ ISSUES DETECTED. Some dependencies may not work on ARM.")
        print("🔧 Check the ARM_DEPENDENCY_CHECK.md guide for solutions.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
