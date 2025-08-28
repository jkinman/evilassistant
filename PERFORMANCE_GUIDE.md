# Evil Assistant Performance Optimization Guide

## Target Performance Metrics

- **Total Latency**: < 500ms (wake detection to response start)
- **Wake Word Detection**: < 100ms
- **Speech Recognition**: < 200ms 
- **LLM Response**: < 300ms (local) / < 800ms (cloud fallback)
- **TTS Generation**: < 200ms (cached) / < 600ms (fresh)
- **Audio Effects**: Real-time (< 20ms buffer)

## Raspberry Pi Optimization

### Hardware Requirements
- **Minimum**: Raspberry Pi 4B (4GB RAM)
- **Recommended**: Raspberry Pi 4B (8GB RAM) or Pi 5
- **Storage**: Fast microSD (Class 10, U3) or USB 3.0 SSD
- **Audio**: USB audio interface for better quality than built-in

### System-Level Optimizations

```bash
# 1. Increase GPU memory split for better performance
echo "gpu_mem=128" >> /boot/config.txt

# 2. Optimize audio settings
echo "dtparam=audio=on" >> /boot/config.txt
echo "audio_pwm_mode=2" >> /boot/config.txt

# 3. Increase USB current limit
echo "max_usb_current=1" >> /boot/config.txt

# 4. Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable cups
sudo systemctl disable avahi-daemon

# 5. Set CPU governor to performance
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
sudo systemctl enable cpufrequtils

# 6. Optimize swap for real-time performance
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# 7. Increase audio buffer sizes
echo "snd-usb-audio index=-2" >> /etc/modprobe.d/alsa-base.conf
```

### Python Optimizations

```python
# Use these imports for better performance
import sys
sys.dont_write_bytecode = True  # Skip .pyc files

# Set environment variables before importing heavy modules
import os
os.environ['OMP_NUM_THREADS'] = '4'  # Limit OpenMP threads
os.environ['OPENBLAS_NUM_THREADS'] = '4'
os.environ['MKL_NUM_THREADS'] = '4'
os.environ['NUMEXPR_NUM_THREADS'] = '4'

# Memory optimization
import gc
gc.set_threshold(700, 10, 10)  # More aggressive garbage collection
```

## Model Selection and Optimization

### Wake Word Detection
```python
# Best options ranked by performance:
# 1. OpenWakeWord (fastest, Python-native)
# 2. Porcupine (commercial, very reliable)
# 3. Custom Whisper (slowest but most flexible)

# OpenWakeWord optimization
OPENWAKEWORD_INFERENCE_FRAMEWORK = "onnx"  # Fastest
OPENWAKEWORD_VAD_THRESHOLD = 0.5  # Balance sensitivity vs false positives
```

### Speech Recognition
```python
# Vosk Models (fastest):
VOSK_MODEL_SMALL = "vosk-model-small-en-us-0.15"  # 40MB, fastest
VOSK_MODEL_LARGE = "vosk-model-en-us-0.22"        # 1.8GB, most accurate

# Faster-Whisper optimization
WHISPER_MODEL = "base"  # Best balance of speed/accuracy
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"  # 4x faster than float32
WHISPER_BEAM_SIZE = 1  # Fastest decoding
```

### LLM Selection
```python
# Local models ranked by performance on Pi 4:
MODELS_BY_SPEED = [
    "llama3.2:1b",      # Fastest, basic responses
    "llama3.2:3b",      # Good balance
    "phi3:mini",        # Microsoft, efficient
    "gemma2:2b",        # Google, compact
]

# Ollama optimization
OLLAMA_CONFIG = {
    "num_ctx": 1024,           # Shorter context = faster
    "num_predict": 100,        # Limit response length
    "temperature": 0.7,        # Slightly reduce for consistency
    "num_thread": 4,           # Match CPU cores
}
```

### TTS Optimization
```python
# Coqui-TTS models by speed:
TTS_MODELS = {
    "fastest": "tts_models/en/ljspeech/tacotron2-DDC",
    "balanced": "tts_models/en/ljspeech/glow-tts",
    "quality": "tts_models/en/ljspeech/vits",
}

# Pre-generate common responses
CACHED_RESPONSES = {
    "greeting": "greetings.wav",
    "acknowledgment": "yes_mortal.wav", 
    "error": "error_response.wav",
    "goodbye": "begone.wav",
}
```

## Real-time Audio Processing

### Buffer Management
```python
# Optimal buffer sizes for Pi 4
AUDIO_CONFIG = {
    "sample_rate": 16000,      # Lower = faster processing
    "chunk_size": 1024,        # 64ms chunks
    "buffer_count": 4,         # Ring buffer
    "channels": 1,             # Mono for speed
    "dtype": "int16",          # Sufficient quality
}

# Circular buffer implementation
class CircularAudioBuffer:
    def __init__(self, size, dtype=np.int16):
        self.buffer = np.zeros(size, dtype=dtype)
        self.write_pos = 0
        self.read_pos = 0
        self.size = size
    
    def write(self, data):
        # Write with automatic wraparound
        end_pos = (self.write_pos + len(data)) % self.size
        if end_pos > self.write_pos:
            self.buffer[self.write_pos:end_pos] = data
        else:
            # Handle wraparound
            split = self.size - self.write_pos
            self.buffer[self.write_pos:] = data[:split]
            self.buffer[:end_pos] = data[split:]
        self.write_pos = end_pos
```

### Real-time Effects Chain
```python
# Replace Sox with real-time DSP
from scipy import signal
import numpy as np

class RealtimeEffects:
    def __init__(self, sample_rate=16000):
        self.sr = sample_rate
        self.setup_filters()
    
    def setup_filters(self):
        # Pre-compute filter coefficients
        nyquist = self.sr / 2
        
        # Bass boost filter
        self.bass_b, self.bass_a = signal.butter(
            2, 200/nyquist, btype='low'
        )
        
        # Pitch shift (simplified)
        self.pitch_shift_factor = 0.8
    
    def process_chunk(self, audio_chunk):
        # Apply effects in real-time
        processed = audio_chunk.astype(np.float32)
        
        # Bass boost
        processed = signal.filtfilt(self.bass_b, self.bass_a, processed)
        
        # Simple pitch shift via resampling
        indices = np.arange(0, len(processed), self.pitch_shift_factor)
        processed = np.interp(indices, np.arange(len(processed)), processed)
        
        # Distortion
        processed = np.tanh(processed * 1.5)
        
        # Normalize
        processed = processed / np.max(np.abs(processed))
        
        return (processed * 32767).astype(np.int16)
```

## Memory Optimization

### Model Loading Strategy
```python
class ModelManager:
    def __init__(self):
        self.models = {}
        self.model_locks = {}
    
    def load_on_demand(self, model_name):
        """Load models only when needed"""
        if model_name not in self.models:
            if model_name == "wake_word":
                self.models[model_name] = self._load_wake_word_model()
            elif model_name == "stt":
                self.models[model_name] = self._load_stt_model()
            # etc.
        return self.models[model_name]
    
    def unload_unused(self):
        """Free memory from unused models"""
        # Implement LRU eviction
        pass
```

### Async Processing Pipeline
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncPipeline:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.audio_queue = asyncio.Queue(maxsize=10)
    
    async def process_audio_stream(self):
        """Non-blocking audio processing"""
        while True:
            audio_chunk = await self.audio_queue.get()
            
            # Process in parallel
            tasks = [
                self.run_in_executor(self.detect_wake_word, audio_chunk),
                self.run_in_executor(self.update_led_brightness, audio_chunk),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
    async def run_in_executor(self, func, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)
```

## Monitoring and Profiling

### Performance Metrics
```python
import time
import psutil
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    wake_detection_time: float = 0
    stt_time: float = 0
    llm_time: float = 0
    tts_time: float = 0
    total_time: float = 0
    memory_usage: float = 0
    cpu_usage: float = 0

class PerformanceMonitor:
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self.start_time = None
    
    def start_timing(self, phase: str):
        self.start_time = time.perf_counter()
    
    def end_timing(self, phase: str):
        if self.start_time:
            duration = time.perf_counter() - self.start_time
            setattr(self.metrics, f"{phase}_time", duration)
            
            # Log if too slow
            if duration > self.get_target_time(phase):
                logging.warning(f"{phase} took {duration:.2f}ms (target: {self.get_target_time(phase):.2f}ms)")
    
    def get_system_metrics(self):
        self.metrics.memory_usage = psutil.virtual_memory().percent
        self.metrics.cpu_usage = psutil.cpu_percent(interval=0.1)
```

### Profiling Commands
```bash
# Profile Python performance
python -m cProfile -o profile.stats evilassistant
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

# Monitor system resources
htop
iotop
sudo perf top

# Audio latency testing
aplay -D plughw:1,0 test_tone.wav  # Test audio output latency
arecord -D plughw:1,0 -d 5 test.wav  # Test input latency
```

## Benchmarking Script

```python
#!/usr/bin/env python3
"""
Performance benchmark for Evil Assistant
Run this to test your optimization results
"""

import time
import asyncio
import numpy as np
from evilassistant.config_improved import *

async def benchmark_pipeline():
    """Benchmark the complete pipeline"""
    print("🔥 Evil Assistant Performance Benchmark 🔥")
    print("=" * 50)
    
    # Simulate audio input
    test_audio = np.random.randint(-32768, 32767, int(RATE * 3), dtype=np.int16)
    
    start_total = time.perf_counter()
    
    # 1. Wake word detection
    start = time.perf_counter()
    # ... wake word processing
    wake_time = (time.perf_counter() - start) * 1000
    
    # 2. Speech recognition
    start = time.perf_counter()
    # ... STT processing
    stt_time = (time.perf_counter() - start) * 1000
    
    # 3. LLM processing
    start = time.perf_counter()
    # ... LLM processing
    llm_time = (time.perf_counter() - start) * 1000
    
    # 4. TTS generation
    start = time.perf_counter()
    # ... TTS processing
    tts_time = (time.perf_counter() - start) * 1000
    
    total_time = (time.perf_counter() - start_total) * 1000
    
    # Results
    print(f"Wake Detection: {wake_time:.1f}ms (target: <100ms)")
    print(f"Speech Recognition: {stt_time:.1f}ms (target: <200ms)")
    print(f"LLM Response: {llm_time:.1f}ms (target: <300ms)")
    print(f"TTS Generation: {tts_time:.1f}ms (target: <200ms)")
    print(f"Total Pipeline: {total_time:.1f}ms (target: <500ms)")
    
    # Performance rating
    if total_time < 500:
        print("🎉 EXCELLENT: Real-time performance achieved!")
    elif total_time < 1000:
        print("✅ GOOD: Acceptable performance")
    else:
        print("⚠️  NEEDS OPTIMIZATION: Too slow for real-time")

if __name__ == "__main__":
    asyncio.run(benchmark_pipeline())
```

## Deployment Optimization

### Systemd Service
```ini
# /etc/systemd/system/evilassistant.service
[Unit]
Description=Evil Assistant Voice Assistant
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/evilassistant
Environment=PATH=/home/pi/.local/bin
ExecStart=/home/pi/.local/bin/evilassistant
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Performance optimizations
Nice=-10
IOSchedulingClass=1
IOSchedulingPriority=4
LimitRTPRIO=95
LimitMEMLOCK=infinity

[Install]
WantedBy=multi-user.target
```

### Auto-optimization Script
```bash
#!/bin/bash
# optimize_pi.sh - Automatic Raspberry Pi optimization for Evil Assistant

echo "🔥 Optimizing Raspberry Pi for Evil Assistant..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install performance tools
sudo apt install -y htop iotop cpufrequtils

# Audio optimization
sudo apt install -y pulseaudio-module-jack jackd2

# Python optimization
pip install --upgrade pip
pip install numba  # JIT compilation

# Set real-time audio permissions
sudo usermod -a -G audio $USER
echo "@audio - rtprio 95" | sudo tee -a /etc/security/limits.conf
echo "@audio - memlock unlimited" | sudo tee -a /etc/security/limits.conf

# Optimize boot config
echo "# Evil Assistant optimizations" | sudo tee -a /boot/config.txt
echo "gpu_mem=128" | sudo tee -a /boot/config.txt
echo "audio_pwm_mode=2" | sudo tee -a /boot/config.txt
echo "max_usb_current=1" | sudo tee -a /boot/config.txt

echo "✅ Optimization complete! Reboot recommended."
```

This guide should help you achieve the target real-time performance. The key is aggressive optimization at every level - from hardware configuration to algorithm selection to memory management.
