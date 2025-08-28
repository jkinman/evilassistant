"""
Fast speech recognition for Evil Assistant
Primary: Vosk (real-time, local)
Fallback: Faster-Whisper (better accuracy)
"""

import json
import logging
import numpy as np
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Vosk for real-time STT
try:
    import vosk
    _VOSK_AVAILABLE = True
except ImportError:
    _VOSK_AVAILABLE = False

# Faster-Whisper for fallback
try:
    from faster_whisper import WhisperModel
    _WHISPER_AVAILABLE = True
except ImportError:
    _WHISPER_AVAILABLE = False

# For temporary file handling
import tempfile
import wave
import os

logger = logging.getLogger(__name__)


@dataclass
class STTConfig:
    """Configuration for speech-to-text processing"""
    primary_engine: str = "vosk"  # "vosk", "whisper", "simple"
    fallback_engine: str = "whisper"
    sample_rate: int = 16000
    
    # Vosk settings
    vosk_model_path: str = "models/vosk-model-small-en-us-0.15"
    vosk_large_model_path: str = "models/vosk-model-en-us-0.22"
    vosk_confidence_threshold: float = 0.8
    
    # Whisper settings
    whisper_model_size: str = "base"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    whisper_beam_size: int = 1  # Fastest
    
    # Performance settings
    max_audio_duration: float = 30.0  # seconds
    chunk_timeout: float = 5.0  # seconds
    enable_vad: bool = True
    language: str = "en"


class VoskSTT:
    """Vosk speech recognition - fastest for real-time"""
    
    def __init__(self, config: STTConfig):
        if not _VOSK_AVAILABLE:
            raise ImportError("Vosk not available. Install with: pip install vosk")
        
        self.config = config
        self.model = None
        self.recognizer = None
        
        # Performance tracking
        self.stats = {
            'recognitions': 0,
            'total_time': 0,
            'avg_confidence': 0,
            'failed_recognitions': 0
        }
        
        self._load_model()
    
    def _load_model(self):
        """Load Vosk model"""
        try:
            # Try small model first (faster)
            if os.path.exists(self.config.vosk_model_path):
                model_path = self.config.vosk_model_path
            else:
                # Fallback to large model
                model_path = self.config.vosk_large_model_path
                if not os.path.exists(model_path):
                    raise FileNotFoundError(f"No Vosk model found at {model_path}")
            
            logger.info(f"Loading Vosk model from: {model_path}")
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.config.sample_rate)
            
            # Enable word-level timestamps
            self.recognizer.SetWords(True)
            
            logger.info("Vosk model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            raise
    
    def transcribe_audio(self, audio: np.ndarray) -> Dict[str, Any]:
        """Transcribe audio using Vosk"""
        start_time = time.time()
        
        try:
            # Convert audio to bytes (Vosk expects int16)
            if audio.dtype != np.int16:
                audio_int16 = (audio * 32767).astype(np.int16)
            else:
                audio_int16 = audio
            
            audio_bytes = audio_int16.tobytes()
            
            # Process audio through Vosk
            if self.recognizer.AcceptWaveform(audio_bytes):
                result = json.loads(self.recognizer.Result())
            else:
                result = json.loads(self.recognizer.PartialResult())
            
            # Calculate confidence from word-level data
            confidence = self._calculate_confidence(result)
            
            # Update stats
            processing_time = time.time() - start_time
            self.stats['recognitions'] += 1
            self.stats['total_time'] += processing_time
            self.stats['avg_confidence'] = (
                (self.stats['avg_confidence'] * (self.stats['recognitions'] - 1) + confidence) /
                self.stats['recognitions']
            )
            
            # Check confidence threshold
            if confidence < self.config.vosk_confidence_threshold:
                self.stats['failed_recognitions'] += 1
                logger.warning(f"Low confidence recognition: {confidence:.2f}")
            
            return {
                'text': result.get('text', '').strip(),
                'confidence': confidence,
                'words': result.get('result', []),
                'processing_time': processing_time,
                'engine': 'vosk'
            }
            
        except Exception as e:
            logger.error(f"Vosk transcription failed: {e}")
            self.stats['failed_recognitions'] += 1
            return {
                'text': '',
                'confidence': 0.0,
                'error': str(e),
                'engine': 'vosk'
            }
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate average confidence from word-level results"""
        if 'result' in result and result['result']:
            confidences = [word.get('conf', 0.0) for word in result['result']]
            return sum(confidences) / len(confidences) if confidences else 0.0
        return 0.5  # Default confidence for partial results
    
    def reset(self):
        """Reset recognizer state"""
        if self.recognizer:
            # Create new recognizer instance
            self.recognizer = vosk.KaldiRecognizer(self.model, self.config.sample_rate)
            self.recognizer.SetWords(True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if self.stats['recognitions'] > 0:
            avg_time = self.stats['total_time'] / self.stats['recognitions']
            success_rate = 1 - (self.stats['failed_recognitions'] / self.stats['recognitions'])
        else:
            avg_time = 0
            success_rate = 0
        
        return {
            **self.stats,
            'avg_processing_time': avg_time,
            'avg_processing_ms': avg_time * 1000,
            'success_rate': success_rate,
            'engine': 'vosk'
        }


class WhisperSTT:
    """Faster-Whisper for fallback when accuracy is critical"""
    
    def __init__(self, config: STTConfig):
        if not _WHISPER_AVAILABLE:
            raise ImportError("Faster-Whisper not available. Install with: pip install faster-whisper")
        
        self.config = config
        self.model = None
        self.stats = {
            'recognitions': 0,
            'total_time': 0,
            'avg_confidence': 0
        }
        
        self._load_model()
    
    def _load_model(self):
        """Load Faster-Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.config.whisper_model_size}")
            self.model = WhisperModel(
                self.config.whisper_model_size,
                device=self.config.whisper_device,
                compute_type=self.config.whisper_compute_type
            )
            logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe_audio(self, audio: np.ndarray) -> Dict[str, Any]:
        """Transcribe audio using Faster-Whisper"""
        start_time = time.time()
        
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                
                # Convert and save audio
                with wave.open(temp_path, "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(self.config.sample_rate)
                    
                    if audio.dtype != np.int16:
                        audio_int16 = (audio * 32767).astype(np.int16)
                    else:
                        audio_int16 = audio
                    
                    wav_file.writeframes(audio_int16.tobytes())
            
            # Transcribe with Whisper
            segments, info = self.model.transcribe(
                temp_path,
                beam_size=self.config.whisper_beam_size,
                language=self.config.language,
                vad_filter=self.config.enable_vad
            )
            
            # Combine segments
            text_parts = []
            confidences = []
            
            for segment in segments:
                text_parts.append(segment.text)
                # Faster-Whisper doesn't provide confidence, estimate from probability
                confidences.append(getattr(segment, 'avg_logprob', -0.5))
            
            text = " ".join(text_parts).strip()
            
            # Convert log probability to confidence (rough estimate)
            if confidences:
                avg_logprob = sum(confidences) / len(confidences)
                confidence = min(1.0, max(0.0, (avg_logprob + 1.0)))  # Normalize roughly
            else:
                confidence = 0.0
            
            # Cleanup temp file
            try:
                os.unlink(temp_path)
            except:
                pass
            
            # Update stats
            processing_time = time.time() - start_time
            self.stats['recognitions'] += 1
            self.stats['total_time'] += processing_time
            self.stats['avg_confidence'] = (
                (self.stats['avg_confidence'] * (self.stats['recognitions'] - 1) + confidence) /
                self.stats['recognitions']
            )
            
            return {
                'text': text,
                'confidence': confidence,
                'language': info.language,
                'language_probability': info.language_probability,
                'processing_time': processing_time,
                'engine': 'whisper'
            }
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'error': str(e),
                'engine': 'whisper'
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if self.stats['recognitions'] > 0:
            avg_time = self.stats['total_time'] / self.stats['recognitions']
        else:
            avg_time = 0
        
        return {
            **self.stats,
            'avg_processing_time': avg_time,
            'avg_processing_ms': avg_time * 1000,
            'engine': 'whisper'
        }


class HybridSTT:
    """Hybrid STT system with primary and fallback engines"""
    
    def __init__(self, config: STTConfig):
        self.config = config
        self.primary_engine = None
        self.fallback_engine = None
        
        # Thread pool for async processing
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        self.stats = {
            'primary_used': 0,
            'fallback_used': 0,
            'total_requests': 0,
            'avg_latency': 0
        }
        
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize STT engines based on config"""
        try:
            # Initialize primary engine
            if self.config.primary_engine == "vosk" and _VOSK_AVAILABLE:
                self.primary_engine = VoskSTT(self.config)
                logger.info("Primary engine: Vosk")
            elif self.config.primary_engine == "whisper" and _WHISPER_AVAILABLE:
                self.primary_engine = WhisperSTT(self.config)
                logger.info("Primary engine: Whisper")
            
            # Initialize fallback engine
            if self.config.fallback_engine == "whisper" and _WHISPER_AVAILABLE:
                self.fallback_engine = WhisperSTT(self.config)
                logger.info("Fallback engine: Whisper")
            elif self.config.fallback_engine == "vosk" and _VOSK_AVAILABLE:
                self.fallback_engine = VoskSTT(self.config)
                logger.info("Fallback engine: Vosk")
            
            if not self.primary_engine:
                raise RuntimeError("No STT engine available")
            
        except Exception as e:
            logger.error(f"Failed to initialize STT engines: {e}")
            raise
    
    def transcribe(self, audio: np.ndarray, use_fallback_if_needed: bool = True) -> Dict[str, Any]:
        """Transcribe audio with automatic fallback"""
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        # Try primary engine first
        if self.primary_engine:
            result = self.primary_engine.transcribe_audio(audio)
            
            # Check if result is good enough
            if result.get('text') and result.get('confidence', 0) > 0.5:
                self.stats['primary_used'] += 1
                self._update_latency_stats(start_time)
                return result
            
            logger.info(f"Primary engine gave low confidence result: {result.get('confidence', 0):.2f}")
        
        # Fall back to secondary engine if needed and available
        if use_fallback_if_needed and self.fallback_engine:
            logger.info("Using fallback STT engine")
            result = self.fallback_engine.transcribe_audio(audio)
            self.stats['fallback_used'] += 1
            self._update_latency_stats(start_time)
            return result
        
        # Return primary result even if low confidence
        self.stats['primary_used'] += 1
        self._update_latency_stats(start_time)
        return result if self.primary_engine else {
            'text': '',
            'confidence': 0.0,
            'error': 'No STT engine available',
            'engine': 'none'
        }
    
    async def transcribe_async(self, audio: np.ndarray) -> Dict[str, Any]:
        """Asynchronous transcription"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.transcribe, audio)
    
    def _update_latency_stats(self, start_time: float):
        """Update latency statistics"""
        latency = time.time() - start_time
        self.stats['avg_latency'] = (
            (self.stats['avg_latency'] * (self.stats['total_requests'] - 1) + latency) /
            self.stats['total_requests']
        )
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get stats from all engines"""
        stats = {
            'hybrid': {
                **self.stats,
                'avg_latency_ms': self.stats['avg_latency'] * 1000,
                'primary_success_rate': self.stats['primary_used'] / max(1, self.stats['total_requests']),
                'fallback_usage_rate': self.stats['fallback_used'] / max(1, self.stats['total_requests'])
            }
        }
        
        if self.primary_engine:
            stats['primary'] = self.primary_engine.get_stats()
        
        if self.fallback_engine:
            stats['fallback'] = self.fallback_engine.get_stats()
        
        return stats
    
    def reset_all(self):
        """Reset all engines"""
        if self.primary_engine and hasattr(self.primary_engine, 'reset'):
            self.primary_engine.reset()
        if self.fallback_engine and hasattr(self.fallback_engine, 'reset'):
            self.fallback_engine.reset()


def download_vosk_models():
    """Download recommended Vosk models"""
    import urllib.request
    import zipfile
    
    models = {
        "vosk-model-small-en-us-0.15": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "vosk-model-en-us-0.22": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
    }
    
    os.makedirs("models", exist_ok=True)
    
    for model_name, url in models.items():
        model_path = f"models/{model_name}"
        
        if os.path.exists(model_path):
            print(f"✅ Model already exists: {model_name}")
            continue
        
        print(f"📥 Downloading {model_name}...")
        zip_path = f"models/{model_name}.zip"
        
        try:
            urllib.request.urlretrieve(url, zip_path)
            
            print(f"📦 Extracting {model_name}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("models/")
            
            os.remove(zip_path)
            print(f"✅ Downloaded: {model_name}")
            
        except Exception as e:
            print(f"❌ Failed to download {model_name}: {e}")


def test_stt_performance():
    """Test STT engine performance"""
    import sounddevice as sd
    
    config = STTConfig()
    stt = HybridSTT(config)
    
    print("🎤 Testing speech recognition performance")
    print("Speak clearly for 3-5 seconds when prompted...")
    
    try:
        # Record test audio
        duration = 5  # seconds
        print(f"🔴 Recording for {duration} seconds... Speak now!")
        
        audio = sd.rec(
            int(duration * config.sample_rate),
            samplerate=config.sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        print("🔄 Processing...")
        
        # Test transcription
        result = stt.transcribe(audio.flatten())
        
        print(f"\n📝 Transcription: '{result['text']}'")
        print(f"🎯 Confidence: {result['confidence']:.2f}")
        print(f"⚡ Engine: {result['engine']}")
        print(f"⏱️  Processing time: {result.get('processing_time', 0)*1000:.1f}ms")
        
        # Show comprehensive stats
        print("\n📊 Performance Stats:")
        stats = stt.get_comprehensive_stats()
        for engine, engine_stats in stats.items():
            print(f"{engine}: {engine_stats}")
    
    except KeyboardInterrupt:
        print("\nTest cancelled")
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    # Download models if needed
    if _VOSK_AVAILABLE:
        download_vosk_models()
    
    # Test performance
    test_stt_performance()
