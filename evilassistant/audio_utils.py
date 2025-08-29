#!/usr/bin/env python3
"""
Centralized audio utilities with proper resource management
"""

import os
import wave
import tempfile
import numpy as np
from contextlib import contextmanager
from typing import Generator
import logging

logger = logging.getLogger(__name__)

@contextmanager
def temporary_wav_file(audio_data: np.ndarray, sample_rate: int = 16000) -> Generator[str, None, None]:
    """
    Context manager for creating temporary WAV files with guaranteed cleanup
    
    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate (default 16000)
        
    Yields:
        str: Path to temporary WAV file
        
    Example:
        with temporary_wav_file(audio_data) as wav_path:
            result = some_audio_function(wav_path)
            # File automatically cleaned up here
    """
    tmp_file = None
    try:
        # Create temporary file
        tmp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmp_path = tmp_file.name
        tmp_file.close()  # Close handle but keep file
        
        # Write audio data to WAV
        with wave.open(tmp_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            # Convert to int16 for WAV format
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wf.writeframes(audio_int16.tobytes())
        
        logger.debug(f"Created temporary WAV file: {tmp_path}")
        yield tmp_path
        
    except Exception as e:
        logger.error(f"Error creating temporary WAV file: {e}")
        raise
    finally:
        # Guaranteed cleanup
        if tmp_file and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
                logger.debug(f"Cleaned up temporary WAV file: {tmp_path}")
            except OSError as e:
                logger.warning(f"Failed to cleanup temporary file {tmp_path}: {e}")

def numpy_to_wav_bytes(audio_data: np.ndarray, sample_rate: int = 16000) -> bytes:
    """
    Convert numpy audio data directly to WAV bytes without temp files
    
    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate (default 16000)
        
    Returns:
        bytes: WAV file data
    """
    import io
    
    # Create in-memory WAV file
    wav_buffer = io.BytesIO()
    
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        # Convert to int16 for WAV format
        audio_int16 = (audio_data * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())
    
    wav_buffer.seek(0)
    return wav_buffer.getvalue()

class AudioFileManager:
    """Manages audio file lifecycle with proper cleanup"""
    
    def __init__(self):
        self._temp_files = set()
    
    def create_temp_wav(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """Create temporary WAV file and track it for cleanup"""
        tmp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmp_path = tmp_file.name
        tmp_file.close()
        
        # Write audio data
        with wave.open(tmp_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wf.writeframes(audio_int16.tobytes())
        
        self._temp_files.add(tmp_path)
        logger.debug(f"Created tracked temporary file: {tmp_path}")
        return tmp_path
    
    def cleanup_file(self, file_path: str):
        """Clean up a specific file"""
        if file_path in self._temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                self._temp_files.remove(file_path)
                logger.debug(f"Cleaned up file: {file_path}")
            except OSError as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
    
    def cleanup_all(self):
        """Clean up all tracked temporary files"""
        for file_path in list(self._temp_files):
            self.cleanup_file(file_path)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_all()

# Global instance for simple usage
_audio_manager = AudioFileManager()

def get_audio_manager() -> AudioFileManager:
    """Get global audio file manager"""
    return _audio_manager
