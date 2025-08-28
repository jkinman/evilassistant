#!/usr/bin/env python3
"""
Voice Activity Detection based audio processing for real-time speech chunking.
Uses webrtcvad for much faster and more accurate speech detection than static time blocks.
"""

import sounddevice as sd
import numpy as np
import webrtcvad
import collections
from typing import Optional, List, Tuple
from .config import RATE, CHANNELS

class VADAudioProcessor:
    """Real-time Voice Activity Detection audio processor."""
    
    def __init__(self, 
                 sample_rate: int = RATE,
                 frame_duration_ms: int = 30,  # 30ms frames for VAD
                 aggressiveness: int = 2,      # VAD sensitivity (0-3, 2=moderate)
                 speech_timeout: float = 0.8,  # Stop recording after 0.8s of silence
                 min_speech_duration: float = 0.3):  # Minimum speech duration to process
        """
        Initialize VAD audio processor.
        
        Args:
            sample_rate: Audio sample rate (must be 8000, 16000, 32000, or 48000)
            frame_duration_ms: Frame duration in milliseconds (10, 20, or 30)
            aggressiveness: VAD aggressiveness level (0-3)
            speech_timeout: Seconds of silence before stopping recording
            min_speech_duration: Minimum speech duration to consider valid
        """
        # Ensure sample rate is supported by webrtcvad
        if sample_rate not in [8000, 16000, 32000, 48000]:
            print(f"Warning: VAD requires sample rate of 8000, 16000, 32000, or 48000. Using 16000.")
            sample_rate = 16000
            
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.speech_timeout = speech_timeout
        self.min_speech_duration = min_speech_duration
        
        # Calculate frame size in samples
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)
        
        # Initialize VAD
        self.vad = webrtcvad.Vad(aggressiveness)
        
        # Audio buffers
        self.audio_buffer = collections.deque(maxlen=int(sample_rate * 10))  # 10 second buffer
        self.speech_frames = []
        
        print(f"VAD Audio Processor initialized:")
        print(f"  Sample rate: {sample_rate}Hz")
        print(f"  Frame duration: {frame_duration_ms}ms ({self.frame_size} samples)")
        print(f"  Aggressiveness: {aggressiveness}")
        print(f"  Speech timeout: {speech_timeout}s")
        
    def is_speech_frame(self, frame: np.ndarray) -> bool:
        """Check if a frame contains speech using VAD."""
        try:
            # Convert to int16 and ensure correct size
            frame_int16 = (frame * 32767).astype(np.int16)
            
            # Pad or trim frame to exact size needed
            if len(frame_int16) < self.frame_size:
                frame_int16 = np.pad(frame_int16, (0, self.frame_size - len(frame_int16)))
            elif len(frame_int16) > self.frame_size:
                frame_int16 = frame_int16[:self.frame_size]
                
            # Convert to bytes for VAD
            frame_bytes = frame_int16.tobytes()
            
            return self.vad.is_speech(frame_bytes, self.sample_rate)
        except Exception as e:
            # If VAD fails, fall back to simple energy detection
            rms = np.sqrt(np.mean(frame ** 2))
            return rms > 0.01  # Simple threshold fallback
            
    def record_speech_chunk(self) -> Optional[np.ndarray]:
        """
        Record a single speech chunk using VAD.
        Returns audio data when speech ends, or None if no speech detected.
        """
        print("Listening for speech...")
        
        speech_frames = []
        silence_frames = 0
        speech_started = False
        max_silence_frames = int(self.speech_timeout * 1000 / self.frame_duration_ms)
        
        while True:
            # Record one frame
            frame = sd.rec(self.frame_size, samplerate=self.sample_rate, 
                          channels=CHANNELS, dtype='float32')
            sd.wait()
            
            if CHANNELS == 1:
                frame = frame.flatten()
            else:
                frame = frame[:, 0]  # Take first channel if stereo
                
            # Check if this frame contains speech
            is_speech = self.is_speech_frame(frame)
            
            if is_speech:
                if not speech_started:
                    print("Speech detected!")
                    speech_started = True
                    
                speech_frames.append(frame)
                silence_frames = 0
            else:
                if speech_started:
                    silence_frames += 1
                    speech_frames.append(frame)  # Include some silence for natural endings
                    
                    if silence_frames >= max_silence_frames:
                        print("Speech ended.")
                        break
                        
            # Prevent infinite recording
            if len(speech_frames) > self.sample_rate * 10 / self.frame_size:  # 10 second max
                print("Maximum recording time reached.")
                break
                
        if not speech_started:
            return None
            
        # Check minimum duration
        total_duration = len(speech_frames) * self.frame_duration_ms / 1000
        if total_duration < self.min_speech_duration:
            print(f"Speech too short ({total_duration:.2f}s), ignoring.")
            return None
            
        # Concatenate frames
        audio_data = np.concatenate(speech_frames)
        print(f"Recorded {total_duration:.2f}s of speech")
        
        return audio_data
        
    def listen_for_wake_phrase(self, wake_phrases: List[str], model) -> Optional[str]:
        """
        Listen for wake phrases using speech-based chunking.
        
        Args:
            wake_phrases: List of wake phrases to detect
            model: Whisper model for transcription
            
        Returns:
            Detected wake phrase or None
        """
        while True:
            # Record a speech chunk
            audio_chunk = self.record_speech_chunk()
            
            if audio_chunk is None:
                continue  # No speech detected, keep listening
                
            # Save chunk for transcription
            import wave
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                with wave.open(tmp_file.name, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.sample_rate)
                    # Convert to int16 for saving
                    audio_int16 = (audio_chunk * 32767).astype(np.int16)
                    wf.writeframes(audio_int16.tobytes())
                
                # Transcribe
                try:
                    print(f"Transcribing audio file: {tmp_file.name}")
                    segments, _ = model.transcribe(tmp_file.name, beam_size=1, 
                                                 language="en", vad_filter=False)
                    transcription = " ".join([segment.text for segment in segments]).strip().lower()
                    
                    if transcription:
                        print(f"Heard: {transcription}")
                        
                        # Check for wake phrases with debug info
                        for phrase in wake_phrases:
                            print(f"Checking if '{phrase.lower()}' in '{transcription}'")
                            if phrase.lower() in transcription:
                                print(f"🔥 Wake phrase detected: '{phrase}'")
                                os.unlink(tmp_file.name)
                                return phrase
                        
                        print("No wake phrase found in transcription")
                    else:
                        print("Heard: (empty transcription)")
                                
                except Exception as e:
                    print(f"Transcription error: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_file.name):
                        os.unlink(tmp_file.name)
                        
    def record_question(self) -> Optional[np.ndarray]:
        """Record a question using speech-based chunking."""
        print("Ask your question...")
        
        # Give a moment for the user to start speaking
        import time
        time.sleep(0.2)
        
        audio_chunk = self.record_speech_chunk()
        
        if audio_chunk is None:
            print("No question detected.")
            return None
            
        return audio_chunk
