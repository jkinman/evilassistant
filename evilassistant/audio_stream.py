"""
Real-time streaming audio pipeline for Evil Assistant
Replaces file-based processing with in-memory circular buffers
"""

import numpy as np
import sounddevice as sd
import threading
import time
import queue
from typing import Callable, Optional, List
import logging
from dataclasses import dataclass
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Audio configuration optimized for real-time processing"""
    sample_rate: int = 16000  # Reduced from 44100 for speed
    channels: int = 1
    dtype: str = 'int16'
    chunk_size: int = 1024  # 64ms chunks at 16kHz
    buffer_duration: float = 2.0  # 2 seconds of audio buffer
    vad_frame_ms: int = 30  # Voice activity detection frame size


class CircularAudioBuffer:
    """Thread-safe circular buffer for continuous audio processing"""
    
    def __init__(self, duration_seconds: float, sample_rate: int, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.size = int(duration_seconds * sample_rate * channels)
        self.buffer = np.zeros(self.size, dtype=np.float32)
        self.write_pos = 0
        self.lock = threading.Lock()
        
    def write(self, data: np.ndarray):
        """Write audio data to buffer (thread-safe)"""
        with self.lock:
            data_flat = data.flatten().astype(np.float32)
            data_len = len(data_flat)
            
            # Handle buffer wraparound
            if self.write_pos + data_len <= self.size:
                self.buffer[self.write_pos:self.write_pos + data_len] = data_flat
            else:
                # Split write across buffer boundary
                first_part = self.size - self.write_pos
                self.buffer[self.write_pos:] = data_flat[:first_part]
                self.buffer[:data_len - first_part] = data_flat[first_part:]
            
            self.write_pos = (self.write_pos + data_len) % self.size
    
    def read_latest(self, duration_seconds: float) -> np.ndarray:
        """Read the most recent audio data (thread-safe)"""
        with self.lock:
            samples = int(duration_seconds * self.sample_rate)
            samples = min(samples, self.size)
            
            # Calculate read position
            read_start = (self.write_pos - samples) % self.size
            
            if read_start + samples <= self.size:
                return self.buffer[read_start:read_start + samples].copy()
            else:
                # Handle wraparound
                first_part = self.size - read_start
                result = np.zeros(samples, dtype=np.float32)
                result[:first_part] = self.buffer[read_start:]
                result[first_part:] = self.buffer[:samples - first_part]
                return result
    
    def get_rms_level(self, duration_seconds: float = 0.1) -> float:
        """Get RMS level of recent audio for LED control"""
        recent_audio = self.read_latest(duration_seconds)
        return float(np.sqrt(np.mean(recent_audio ** 2)))


class VoiceActivityDetector:
    """Simple but effective voice activity detection"""
    
    def __init__(self, config: AudioConfig):
        self.config = config
        self.frame_size = int(config.vad_frame_ms * config.sample_rate / 1000)
        self.silence_threshold = 0.01  # Adjust based on environment
        self.speech_threshold = 0.02
        self.min_speech_frames = 3
        self.min_silence_frames = 20
        
        self.speech_frame_count = 0
        self.silence_frame_count = 0
        self.is_speech = False
        
    def process_frame(self, audio_frame: np.ndarray) -> bool:
        """Process audio frame and return True if speech is detected"""
        rms = np.sqrt(np.mean(audio_frame ** 2))
        
        if rms > self.speech_threshold:
            self.speech_frame_count += 1
            self.silence_frame_count = 0
            
            if self.speech_frame_count >= self.min_speech_frames:
                self.is_speech = True
        else:
            self.silence_frame_count += 1
            self.speech_frame_count = 0
            
            if self.silence_frame_count >= self.min_silence_frames:
                self.is_speech = False
        
        return self.is_speech


class StreamingAudioProcessor:
    """Main audio processing pipeline for real-time operation"""
    
    def __init__(self, config: AudioConfig):
        self.config = config
        self.audio_buffer = CircularAudioBuffer(
            config.buffer_duration, config.sample_rate, config.channels
        )
        self.vad = VoiceActivityDetector(config)
        
        # Event callbacks
        self.wake_word_callback: Optional[Callable[[np.ndarray], bool]] = None
        self.speech_start_callback: Optional[Callable[[], None]] = None
        self.speech_end_callback: Optional[Callable[[np.ndarray], None]] = None
        self.led_update_callback: Optional[Callable[[float], None]] = None
        
        # State
        self.is_listening = False
        self.is_recording = False
        self.speech_buffer = deque()
        self.stream = None
        
        # Performance tracking
        self.stats = {
            'chunks_processed': 0,
            'avg_processing_time': 0,
            'max_processing_time': 0
        }
    
    def start_stream(self):
        """Start the audio input stream"""
        logger.info(f"Starting audio stream at {self.config.sample_rate}Hz")
        
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio callback status: {status}")
            
            start_time = time.time()
            self._process_audio_chunk(indata)
            
            # Update performance stats
            processing_time = time.time() - start_time
            self.stats['chunks_processed'] += 1
            self.stats['avg_processing_time'] = (
                (self.stats['avg_processing_time'] * (self.stats['chunks_processed'] - 1) + processing_time) /
                self.stats['chunks_processed']
            )
            self.stats['max_processing_time'] = max(self.stats['max_processing_time'], processing_time)
            
            # Warn if processing is too slow
            if processing_time > self.config.chunk_size / self.config.sample_rate * 0.8:
                logger.warning(f"Audio processing too slow: {processing_time*1000:.1f}ms")
        
        self.stream = sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype=self.config.dtype,
            blocksize=self.config.chunk_size,
            callback=audio_callback
        )
        
        self.stream.start()
        self.is_listening = True
    
    def stop_stream(self):
        """Stop the audio input stream"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.is_listening = False
        logger.info("Audio stream stopped")
    
    def _process_audio_chunk(self, audio_chunk: np.ndarray):
        """Process each audio chunk in real-time"""
        # Convert to float32 and normalize
        audio_float = audio_chunk.flatten().astype(np.float32) / 32768.0
        
        # Add to circular buffer
        self.audio_buffer.write(audio_float)
        
        # Update LED brightness based on audio level
        if self.led_update_callback:
            rms_level = self.audio_buffer.get_rms_level(0.05)  # 50ms window
            self.led_update_callback(rms_level)
        
        # Voice activity detection
        is_speech = self.vad.process_frame(audio_float)
        
        if not self.is_recording:
            # Looking for wake word
            if self.wake_word_callback:
                # Get recent audio for wake word detection
                recent_audio = self.audio_buffer.read_latest(1.0)  # 1 second
                if self.wake_word_callback(recent_audio):
                    self._start_speech_recording()
        else:
            # Recording user speech
            self.speech_buffer.append(audio_float)
            
            # Check for end of speech
            if not is_speech and len(self.speech_buffer) > 0:
                self._end_speech_recording()
    
    def _start_speech_recording(self):
        """Start recording user speech after wake word detection"""
        logger.info("Wake word detected - starting speech recording")
        self.is_recording = True
        self.speech_buffer.clear()
        
        # Include some pre-speech audio
        pre_speech_duration = 0.3  # 300ms
        pre_speech_audio = self.audio_buffer.read_latest(pre_speech_duration)
        
        # Convert back to chunks for buffer
        chunk_size = self.config.chunk_size
        for i in range(0, len(pre_speech_audio), chunk_size):
            chunk = pre_speech_audio[i:i + chunk_size]
            if len(chunk) == chunk_size:
                self.speech_buffer.append(chunk)
        
        if self.speech_start_callback:
            self.speech_start_callback()
    
    def _end_speech_recording(self):
        """End speech recording and process the collected audio"""
        if not self.speech_buffer:
            return
        
        logger.info("Speech ended - processing recording")
        
        # Combine all speech chunks
        speech_audio = np.concatenate(list(self.speech_buffer))
        
        # Reset state
        self.is_recording = False
        self.speech_buffer.clear()
        
        # Process the speech
        if self.speech_end_callback:
            self.speech_end_callback(speech_audio)
    
    def force_stop_recording(self):
        """Force stop current recording (for stop commands)"""
        if self.is_recording:
            logger.info("Forcing stop of speech recording")
            self.is_recording = False
            self.speech_buffer.clear()
    
    def get_performance_stats(self) -> dict:
        """Get processing performance statistics"""
        return {
            **self.stats,
            'avg_processing_ms': self.stats['avg_processing_time'] * 1000,
            'max_processing_ms': self.stats['max_processing_time'] * 1000,
            'real_time_factor': self.stats['avg_processing_time'] / (self.config.chunk_size / self.config.sample_rate)
        }


# Example usage with callbacks
class AudioCallbacks:
    """Example callback implementations"""
    
    def __init__(self):
        self.wake_word_detector = None  # Will be set up later
        self.stt_engine = None
        self.led_controller = None
    
    def wake_word_callback(self, audio: np.ndarray) -> bool:
        """Check if wake word is present in audio"""
        # This will be replaced with actual wake word detection
        # For now, simple amplitude threshold
        rms = np.sqrt(np.mean(audio ** 2))
        return rms > 0.05  # Placeholder
    
    def speech_start_callback(self):
        """Called when speech recording starts"""
        print("👹 I'm listening, mortal...")
    
    def speech_end_callback(self, speech_audio: np.ndarray):
        """Process recorded speech"""
        print(f"Processing {len(speech_audio)/16000:.1f}s of speech")
        # This will be connected to STT processing
    
    def led_update_callback(self, rms_level: float):
        """Update LED brightness based on audio level"""
        # This will be connected to GPIO PWM
        brightness = min(100, rms_level * 1000)  # Scale to 0-100%
        # print(f"LED brightness: {brightness:.1f}%")  # Uncomment for debugging


def main():
    """Test the streaming audio pipeline"""
    config = AudioConfig()
    processor = StreamingAudioProcessor(config)
    callbacks = AudioCallbacks()
    
    # Connect callbacks
    processor.wake_word_callback = callbacks.wake_word_callback
    processor.speech_start_callback = callbacks.speech_start_callback
    processor.speech_end_callback = callbacks.speech_end_callback
    processor.led_update_callback = callbacks.led_update_callback
    
    try:
        processor.start_stream()
        print("🎤 Streaming audio pipeline started. Press Ctrl+C to stop.")
        print("Speak loudly to trigger wake word detection...")
        
        while True:
            time.sleep(1)
            stats = processor.get_performance_stats()
            if stats['chunks_processed'] > 0:
                print(f"Stats: {stats['chunks_processed']} chunks, "
                      f"avg: {stats['avg_processing_ms']:.1f}ms, "
                      f"max: {stats['max_processing_ms']:.1f}ms")
    
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        processor.stop_stream()


if __name__ == "__main__":
    main()
