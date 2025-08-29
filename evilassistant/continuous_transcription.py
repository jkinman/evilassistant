#!/usr/bin/env python3
"""
Evil Assistant - Continuous Speech Transcription & Speaker Recognition
"I hear all whispers in your domain, mortal!"
"""

import os
import json
import time
import threading
import numpy as np
import wave
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from faster_whisper import WhisperModel
from cryptography.fernet import Fernet
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class TranscriptEntry:
    """A single transcript entry with metadata"""
    timestamp: float
    text: str
    confidence: float
    speaker_id: Optional[str] = None
    duration: float = 0.0
    audio_hash: Optional[str] = None

@dataclass
class SpeakerProfile:
    """Anonymous speaker profile"""
    speaker_id: str
    first_heard: float
    last_heard: float
    total_segments: int
    avg_confidence: float

class PrivacyProtectedStorage:
    """Encrypted local storage for transcripts"""
    
    def __init__(self, storage_dir: str = "transcripts", retention_days: int = 7):
        self.storage_dir = storage_dir
        self.retention_days = retention_days
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Create storage directory
        os.makedirs(self.storage_dir, exist_ok=True)
        
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = ".transcript_key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Make file read-only for owner
            os.chmod(key_file, 0o600)
            return key
    
    def _get_daily_file(self, timestamp: float) -> str:
        """Get filename for a given timestamp"""
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        return os.path.join(self.storage_dir, f"transcripts_{date_str}.enc")
    
    def store_transcript(self, entry: TranscriptEntry):
        """Store encrypted transcript entry"""
        try:
            daily_file = self._get_daily_file(entry.timestamp)
            
            # Read existing entries for the day
            entries = []
            if os.path.exists(daily_file):
                entries = self._read_daily_file(daily_file)
            
            # Add new entry
            entry_dict = {
                "timestamp": entry.timestamp,
                "text": entry.text,
                "confidence": entry.confidence,
                "speaker_id": entry.speaker_id,
                "duration": entry.duration,
                "audio_hash": entry.audio_hash
            }
            entries.append(entry_dict)
            
            # Encrypt and save
            data = json.dumps(entries).encode()
            encrypted_data = self.cipher.encrypt(data)
            
            with open(daily_file, 'wb') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            logger.error(f"Failed to store transcript: {e}")
    
    def _read_daily_file(self, filepath: str) -> List[Dict]:
        """Read and decrypt a daily transcript file"""
        try:
            with open(filepath, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
            
        except Exception as e:
            logger.error(f"Failed to read transcript file {filepath}: {e}")
            return []
    
    def search_transcripts(self, query: str, days_back: int = 7) -> List[TranscriptEntry]:
        """Search transcripts for a query"""
        results = []
        query_lower = query.lower()
        
        # Search through recent days
        for i in range(days_back):
            timestamp = time.time() - (i * 86400)  # Go back i days
            daily_file = self._get_daily_file(timestamp)
            
            if os.path.exists(daily_file):
                entries = self._read_daily_file(daily_file)
                
                for entry_dict in entries:
                    if query_lower in entry_dict.get("text", "").lower():
                        entry = TranscriptEntry(**entry_dict)
                        results.append(entry)
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results
    
    def get_recent_transcripts(self, hours_back: int = 1) -> List[TranscriptEntry]:
        """Get recent transcripts"""
        cutoff_time = time.time() - (hours_back * 3600)
        results = []
        
        # Check today and yesterday
        for i in range(2):
            timestamp = time.time() - (i * 86400)
            daily_file = self._get_daily_file(timestamp)
            
            if os.path.exists(daily_file):
                entries = self._read_daily_file(daily_file)
                
                for entry_dict in entries:
                    if entry_dict.get("timestamp", 0) >= cutoff_time:
                        entry = TranscriptEntry(**entry_dict)
                        results.append(entry)
        
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results
    
    def cleanup_old_files(self):
        """Remove files older than retention period"""
        cutoff_time = time.time() - (self.retention_days * 86400)
        
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.startswith("transcripts_") and filename.endswith(".enc"):
                    filepath = os.path.join(self.storage_dir, filename)
                    file_time = os.path.getctime(filepath)
                    
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        logger.info(f"Deleted old transcript file: {filename}")
                        
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")

class SimpleSpeakerIdentifier:
    """Basic speaker identification using voice characteristics"""
    
    def __init__(self):
        self.speakers: Dict[str, SpeakerProfile] = {}
        self.next_speaker_id = 1
        
    def _calculate_audio_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Calculate basic audio features for speaker identification"""
        # Simple features: pitch variance, energy, spectral characteristics
        features = {
            "mean_amplitude": float(np.mean(np.abs(audio_data))),
            "std_amplitude": float(np.std(np.abs(audio_data))),
            "zero_crossing_rate": float(np.mean(np.diff(np.signbit(audio_data)))),
            "energy": float(np.sum(audio_data ** 2)),
        }
        
        # Add spectral features if possible
        try:
            fft = np.fft.fft(audio_data)
            magnitude = np.abs(fft)
            features["spectral_centroid"] = float(np.mean(magnitude))
            features["spectral_variance"] = float(np.var(magnitude))
        except:
            features["spectral_centroid"] = 0.0
            features["spectral_variance"] = 0.0
            
        return features
    
    def _features_to_hash(self, features: Dict[str, float]) -> str:
        """Convert features to a hash for simple speaker matching"""
        # Create a simple speaker "fingerprint"
        feature_string = f"{features['mean_amplitude']:.3f}_{features['zero_crossing_rate']:.3f}"
        return hashlib.md5(feature_string.encode()).hexdigest()[:8]
    
    def identify_speaker(self, audio_data: np.ndarray, confidence: float) -> str:
        """Identify speaker from audio data (improved clustering)"""
        features = self._calculate_audio_features(audio_data)
        
        # More robust speaker matching with multiple features
        best_match = None
        best_similarity = float('inf')
        
        for speaker_id, profile in self.speakers.items():
            # Compare multiple audio characteristics
            if hasattr(profile, 'audio_features'):
                similarity = 0
                similarity += abs(features["mean_amplitude"] - profile.audio_features.get("mean_amplitude", 0))
                similarity += abs(features["zero_crossing_rate"] - profile.audio_features.get("zero_crossing_rate", 0)) * 0.5
                similarity += abs(features["spectral_centroid"] - profile.audio_features.get("spectral_centroid", 0)) * 0.0001
                
                # More lenient threshold for speaker matching
                if similarity < best_similarity and similarity < 0.15:  # Increased threshold
                    best_similarity = similarity
                    best_match = speaker_id
        
        if best_match:
            # Update existing speaker
            profile = self.speakers[best_match]
            profile.last_heard = time.time()
            profile.total_segments += 1
            return best_match
        
        # New speaker only if we have very few speakers already (max 3-4 realistic)
        if len(self.speakers) < 4:
            speaker_id = f"Speaker{self.next_speaker_id}"
            self.next_speaker_id += 1
            
            profile = SpeakerProfile(
                speaker_id=speaker_id,
                first_heard=time.time(),
                last_heard=time.time(),
                total_segments=1,
                avg_confidence=confidence
            )
            profile.audio_features = features  # Store features for comparison
            self.speakers[speaker_id] = profile
            
            logger.info(f"New speaker identified: {speaker_id}")
            return speaker_id
        else:
            # Too many speakers, assign to most recent
            most_recent = max(self.speakers.items(), key=lambda x: x[1].last_heard)
            return most_recent[0]

class ContinuousTranscriber:
    """Main continuous transcription system"""
    
    def __init__(self, 
                 model_name: str = "base",
                 chunk_duration: float = 10.0,
                 min_confidence: float = -0.8,
                 enable_speaker_id: bool = True):
        
        self.model_name = model_name
        self.chunk_duration = chunk_duration
        self.min_confidence = min_confidence
        self.enable_speaker_id = enable_speaker_id
        
        # Initialize components
        print("🎧 Loading Whisper model for continuous transcription...")
        self.whisper_model = WhisperModel(model_name, device="cpu", compute_type="int8")
        
        self.storage = PrivacyProtectedStorage()
        self.speaker_id = SimpleSpeakerIdentifier() if enable_speaker_id else None
        
        # State
        self.is_running = False
        self.transcription_thread = None
        self.total_transcripts = 0
        
        print("✅ Continuous transcription system initialized")
    
    def _calculate_audio_hash(self, audio_data: np.ndarray) -> str:
        """Calculate hash of audio data for deduplication"""
        audio_bytes = audio_data.tobytes()
        return hashlib.md5(audio_bytes).hexdigest()[:16]
    
    def transcribe_chunk(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Optional[TranscriptEntry]:
        """Transcribe a single audio chunk"""
        try:
            # Use proper resource management for temporary files
            from .audio_utils import temporary_wav_file
            
            with temporary_wav_file(audio_data, sample_rate) as wav_path:
                # Transcribe
                segments, info = self.whisper_model.transcribe(
                    wav_path,
                    beam_size=1,
                    language="en",
                    vad_filter=True
                )
                
                # Combine segments
                text_parts = []
                total_confidence = 0
                segment_count = 0
                
                for segment in segments:
                    if segment.text.strip():  # Skip empty segments
                        text_parts.append(segment.text.strip())
                        total_confidence += segment.avg_logprob
                        segment_count += 1
                
                if not text_parts:
                    return None
                
                full_text = " ".join(text_parts)
                avg_confidence = total_confidence / segment_count if segment_count > 0 else 0
                
                # Filter out very short or meaningless phrases
                if len(full_text) < 10:  # Too short
                    return None
                
                # Filter out common background noise phrases
                noise_phrases = [
                    "thank you", "okay", "yeah", "uh huh", "mm hmm", "alright",
                    "the", "and", "in", "to", "of", "a", "it", "is", "that"
                ]
                if full_text.lower().strip() in noise_phrases:
                    return None
                
                # Skip if confidence too low
                if avg_confidence < self.min_confidence:
                    logger.info(f"Skipping low confidence: {avg_confidence:.3f} < {self.min_confidence}")
                    return None
                
                logger.info(f"Storing transcript: '{full_text}' (confidence: {avg_confidence:.3f})")
                
                # Identify speaker if enabled
                speaker_id = None
                if self.speaker_id:
                    speaker_id = self.speaker_id.identify_speaker(audio_data, avg_confidence)
                
                # Create transcript entry
                entry = TranscriptEntry(
                    timestamp=time.time(),
                    text=full_text,
                    confidence=avg_confidence,
                    speaker_id=speaker_id,
                    duration=len(audio_data) / sample_rate,
                    audio_hash=self._calculate_audio_hash(audio_data)
                )
                
                return entry
                
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    def process_and_store(self, audio_data: np.ndarray):
        """Process audio chunk and store if valid"""
        entry = self.transcribe_chunk(audio_data)
        
        if entry and entry.text.strip():
            # Store the transcript
            self.storage.store_transcript(entry)
            self.total_transcripts += 1
            
            # Log for debugging (first few words only for privacy)
            preview = entry.text[:50] + "..." if len(entry.text) > 50 else entry.text
            speaker_info = f" [{entry.speaker_id}]" if entry.speaker_id else ""
            logger.info(f"📝 Transcript{speaker_info}: {preview}")
    
    def search_conversations(self, query: str, days_back: int = 7) -> List[TranscriptEntry]:
        """Search stored conversations"""
        return self.storage.search_transcripts(query, days_back)
    
    def get_recent_activity(self, hours_back: int = 1) -> List[TranscriptEntry]:
        """Get recent conversation activity"""
        return self.storage.get_recent_transcripts(hours_back)
    
    def get_speaker_summary(self) -> Dict[str, SpeakerProfile]:
        """Get summary of identified speakers"""
        if self.speaker_id:
            return self.speaker_id.speakers
        return {}
    
    def cleanup_old_data(self):
        """Clean up old transcript data"""
        self.storage.cleanup_old_files()
    
    def get_stats(self) -> Dict[str, any]:
        """Get transcription statistics"""
        stats = {
            "total_transcripts": self.total_transcripts,
            "is_running": self.is_running,
            "speakers_identified": len(self.speaker_id.speakers) if self.speaker_id else 0,
            "storage_directory": self.storage.storage_dir,
            "retention_days": self.storage.retention_days
        }
        
        if self.speaker_id:
            stats["speakers"] = {
                speaker_id: {
                    "total_segments": profile.total_segments,
                    "first_heard": datetime.fromtimestamp(profile.first_heard).strftime("%Y-%m-%d %H:%M"),
                    "last_heard": datetime.fromtimestamp(profile.last_heard).strftime("%Y-%m-%d %H:%M")
                }
                for speaker_id, profile in self.speaker_id.speakers.items()
            }
        
        return stats

# Global instance
_continuous_transcriber = None

def get_transcriber() -> ContinuousTranscriber:
    """Get singleton transcriber instance"""
    global _continuous_transcriber
    if _continuous_transcriber is None:
        _continuous_transcriber = ContinuousTranscriber()
    return _continuous_transcriber

def start_continuous_transcription():
    """Start continuous transcription service"""
    transcriber = get_transcriber()
    if not transcriber.is_running:
        transcriber.is_running = True
        logger.info("🎧 Continuous transcription started")
        return True
    return False

def stop_continuous_transcription():
    """Stop continuous transcription service"""
    transcriber = get_transcriber()
    if transcriber.is_running:
        transcriber.is_running = False
        logger.info("🔇 Continuous transcription stopped")
        return True
    return False

def process_audio_for_transcription(audio_data: np.ndarray):
    """Process audio data for transcription (called from main audio loop)"""
    transcriber = get_transcriber()
    if transcriber.is_running:
        # Process in background thread to avoid blocking main audio loop
        threading.Thread(
            target=transcriber.process_and_store,
            args=(audio_data,),
            daemon=True
        ).start()

async def search_transcription_logs(query: str, days_back: int = 7) -> List[TranscriptEntry]:
    """Search transcription logs (async for Evil Assistant integration)"""
    transcriber = get_transcriber()
    return transcriber.search_conversations(query, days_back)
