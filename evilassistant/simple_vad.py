#!/usr/bin/env python3
"""
Simple and reliable VAD-based audio recording using continuous recording.
"""

import sounddevice as sd
import numpy as np
import collections
import time
from typing import Optional
from .config import RATE, CHANNELS, SILENCE_THRESHOLD

class SimpleVADRecorder:
    """Simple VAD recorder using continuous audio stream and energy-based detection."""
    
    def __init__(self, 
                 sample_rate: int = RATE,
                 chunk_duration: float = 0.1,  # 100ms chunks for smooth recording
                 speech_timeout: float = 0.8,  # Stop after 0.8s of silence
                 min_speech_duration: float = 0.5,  # Minimum 0.5s of speech
                 energy_threshold: float = 800):  # Energy threshold for speech detection
        
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.speech_timeout = speech_timeout
        self.min_speech_duration = min_speech_duration
        self.energy_threshold = energy_threshold
        self.extracted_question = None  # Store question extracted from wake audio
        
        print(f"Simple VAD Recorder initialized:")
        print(f"  Sample rate: {sample_rate}Hz")
        print(f"  Chunk duration: {chunk_duration}s ({self.chunk_size} samples)")
        print(f"  Speech timeout: {speech_timeout}s")
        print(f"  Energy threshold: {energy_threshold}")
        
    def get_audio_energy(self, audio_chunk: np.ndarray) -> float:
        """Calculate RMS energy of audio chunk."""
        return float(np.sqrt(np.mean(audio_chunk.astype(np.float32) ** 2)) * 32767)
        
    def record_speech_chunk(self) -> Optional[np.ndarray]:
        """
        Record a speech chunk using simple energy-based VAD.
        More reliable than WebRTC VAD for this use case.
        """
        print("Listening for speech...")
        
        speech_chunks = []
        silence_duration = 0.0
        speech_started = False
        start_time = time.time()
        
        # Use a simple continuous recording approach
        with sd.InputStream(samplerate=self.sample_rate, channels=CHANNELS, 
                           dtype='float32', blocksize=self.chunk_size) as stream:
            
            while True:
                # Read one chunk
                chunk, overflowed = stream.read(self.chunk_size)
                
                if overflowed:
                    print("Audio buffer overflow detected")
                
                if CHANNELS == 1:
                    chunk = chunk.flatten()
                else:
                    chunk = chunk[:, 0]  # Take first channel
                
                # Calculate energy
                energy = self.get_audio_energy(chunk)
                
                if energy > self.energy_threshold:
                    if not speech_started:
                        print("Speech detected!")
                        speech_started = True
                        
                    speech_chunks.append(chunk)
                    silence_duration = 0.0
                else:
                    if speech_started:
                        # Include some silence for natural endings
                        speech_chunks.append(chunk)
                        silence_duration += self.chunk_duration
                        
                        if silence_duration >= self.speech_timeout:
                            print("Speech ended.")
                            break
                            
                # Prevent infinite recording
                if time.time() - start_time > 10.0:  # 10 second max
                    print("Maximum recording time reached.")
                    break
                    
        if not speech_started:
            return None
            
        # Check minimum duration
        total_duration = len(speech_chunks) * self.chunk_duration
        if total_duration < self.min_speech_duration:
            print(f"Speech too short ({total_duration:.2f}s), ignoring.")
            return None
            
        # Concatenate chunks
        audio_data = np.concatenate(speech_chunks)
        print(f"Recorded {total_duration:.2f}s of speech")
        
        return audio_data
    
    def extract_question_from_wake_audio(self, transcription: str, detected_phrase: str) -> Optional[str]:
        """Extract question from audio that contains both wake phrase and question."""
        try:
            # Find where the wake phrase ends in the transcription
            phrase_lower = detected_phrase.lower()
            transcription_lower = transcription.lower()
            
            # Find the position after the wake phrase
            phrase_end = transcription_lower.find(phrase_lower) + len(phrase_lower)
            
            if phrase_end < len(transcription):
                # Extract everything after the wake phrase
                question_part = transcription[phrase_end:].strip()
                
                # Remove common filler words at the beginning
                filler_words = ['um', 'uh', 'er', 'ah', 'well', 'so', 'now', 'can', 'could', 'would']
                words = question_part.split()
                
                # Remove leading filler words and punctuation
                while words and (words[0].lower().strip('.,!?:;') in filler_words or words[0].strip('.,!?:;') == ''):
                    words.pop(0)
                
                question_part = ' '.join(words).strip()
                
                # Check if there's a meaningful question (at least 3 words)
                if len(question_part.split()) >= 3:
                    return question_part
                    
        except Exception as e:
            print(f"Error extracting question from wake audio: {e}")
            
        return None
        
    def listen_for_wake_phrase(self, wake_phrases, model) -> Optional[str]:
        """Listen for wake phrases using simple VAD."""
        while True:
            # Record a speech chunk
            audio_chunk = self.record_speech_chunk()
            
            if audio_chunk is None:
                continue  # No speech detected, keep listening
            
            # Process audio for continuous transcription (if enabled)
            try:
                from .continuous_transcription import process_audio_for_transcription
                process_audio_for_transcription(audio_chunk)
            except ImportError:
                pass  # Transcription not available
                
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
                    print(f"Transcribing audio...")
                    segments, _ = model.transcribe(tmp_file.name, beam_size=1, 
                                                 language="en", vad_filter=False)
                    transcription = " ".join([segment.text for segment in segments]).strip().lower()
                    
                    if transcription:
                        print(f"Heard: '{transcription}'")
                        
                        # Check for wake phrases
                        for phrase in wake_phrases:
                            if phrase.lower() in transcription:
                                print(f"🔥 Wake phrase detected: '{phrase}'")
                                
                                # Check if there's a question in the same audio
                                question_part = self.extract_question_from_wake_audio(transcription, phrase)
                                if question_part:
                                    print(f"💡 Question extracted from wake audio: '{question_part}'")
                                    # Store the question for the assistant to use
                                    self.extracted_question = question_part
                                else:
                                    self.extracted_question = None
                                
                                os.unlink(tmp_file.name)
                                return phrase
                        
                        print("No wake phrase found")
                    else:
                        print("No transcription result")
                                
                except Exception as e:
                    print(f"Transcription error: {e}")
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_file.name):
                        os.unlink(tmp_file.name)
                        
    def record_question(self) -> Optional[np.ndarray]:
        """Record a question using simple VAD."""
        print("Ask your question...")
        
        # Brief pause to let user start speaking
        time.sleep(0.3)
        
        audio_chunk = self.record_speech_chunk()
        
        if audio_chunk is None:
            print("No question detected.")
            return None
            
        return audio_chunk
