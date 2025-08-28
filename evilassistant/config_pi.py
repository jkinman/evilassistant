#!/usr/bin/env python3
"""
Raspberry Pi Optimized Configuration

This configuration file contains Pi-specific optimizations for performance
and compatibility on Raspberry Pi 4 hardware.
"""

import os
import platform

# Auto-detect if running on Raspberry Pi
def is_raspberry_pi():
    """Check if running on Raspberry Pi hardware"""
    try:
        with open('/proc/device-tree/model', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except:
        return False

# Base configuration (import from main config)
from .config import *

# Pi-specific optimizations
if is_raspberry_pi():
    print("🍓 Raspberry Pi detected - applying optimizations")
    
    # Audio optimizations for Pi
    RATE = 16000  # Optimal for Pi audio processing
    CHUNK_DURATION = 2  # Slightly larger chunks for stability
    SILENCE_DURATION = 0.8  # Good balance for Pi performance
    
    # Whisper model optimization for Pi
    WHISPER_MODEL = "base"  # Good balance of speed/accuracy on Pi
    
    # Memory-conscious settings
    MAX_RECORDING_DURATION = 30  # Prevent memory issues
    
    # GPIO settings (automatically enabled on Pi)
    GPIO_ENABLED = True
    
    # TTS optimizations for Pi
    TTS_VOICE_PROFILE = "piper_ryan_demonic"  # Use Piper for best local performance
    TTS_FALLBACK_ENABLED = True  # Important for Pi reliability
    
    # Performance monitoring
    ENABLE_PERFORMANCE_LOGGING = True
    
    print("✅ Pi optimizations applied")

# Pi 4 specific memory optimizations
def get_pi_memory():
    """Get available memory on Pi"""
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if 'MemAvailable:' in line:
                    # Return memory in MB
                    return int(line.split()[1]) // 1024
    except:
        return 4096  # Default to 4GB

if is_raspberry_pi():
    available_memory = get_pi_memory()
    
    if available_memory < 2048:  # Less than 2GB available
        print("⚠️  Low memory detected - applying memory optimizations")
        WHISPER_MODEL = "tiny"  # Use smallest model
        CHUNK_DURATION = 1.5  # Smaller chunks
        TTS_VOICE_PROFILE = "demonic_deep"  # Use espeak for less memory
    elif available_memory < 3072:  # Less than 3GB available  
        print("🔧 Medium memory detected - balanced optimizations")
        WHISPER_MODEL = "small"  # Medium model
    else:
        print("✅ Sufficient memory for full features")

# GPIO LED Configuration for Pi
LED_BRIGHTNESS_MIN = 5.0   # Minimum LED brightness %
LED_BRIGHTNESS_MAX = 85.0  # Maximum LED brightness %
LED_GAIN = 200.0          # Audio level to brightness gain
LED_SMOOTHING = 0.8       # LED brightness smoothing factor

# Pi-specific wake phrases (optimized for Pi processing)
PI_WAKE_PHRASES = [
    "evil assistant",
    "dark one", 
    "cthulhu",
    "summon"  # Shorter phrases work better on Pi
]

# Update wake phrases if on Pi
if is_raspberry_pi():
    WAKE_PHRASES = PI_WAKE_PHRASES
    print(f"🎤 Using Pi-optimized wake phrases: {', '.join(WAKE_PHRASES)}")

# Temperature monitoring for Pi
def check_pi_temperature():
    """Check Pi CPU temperature and warn if too hot"""
    try:
        temp = os.popen('vcgencmd measure_temp').readline()
        temp_value = float(temp.replace("temp=", "").replace("'C\n", ""))
        
        if temp_value > 80:
            print(f"🔥 WARNING: Pi temperature high ({temp_value}°C) - performance may be throttled")
            return temp_value
        elif temp_value > 70:
            print(f"🌡️  Pi temperature: {temp_value}°C (consider cooling)")
            return temp_value
        else:
            print(f"❄️  Pi temperature: {temp_value}°C (good)")
            return temp_value
    except:
        return None

# Performance monitoring
if is_raspberry_pi() and ENABLE_PERFORMANCE_LOGGING:
    import time
    import psutil
    
    def log_pi_performance():
        """Log Pi performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            temp = check_pi_temperature()
            
            print(f"📊 Pi Stats - CPU: {cpu_percent}%, RAM: {memory.percent}%, Temp: {temp}°C")
        except Exception as e:
            print(f"Performance logging error: {e}")

# Export Pi detection for other modules
__all__ = ['is_raspberry_pi', 'check_pi_temperature', 'get_pi_memory']

if __name__ == "__main__":
    # Test Pi detection and optimization
    print("🧪 Testing Pi configuration...")
    print(f"Platform: {platform.machine()}")
    print(f"Is Pi: {is_raspberry_pi()}")
    if is_raspberry_pi():
        print(f"Memory: {get_pi_memory()}MB")
        check_pi_temperature()
    print("✅ Pi configuration test complete")
