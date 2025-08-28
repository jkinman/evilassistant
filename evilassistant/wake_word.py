"""
Fast wake word detection for Evil Assistant
Uses OpenWakeWord for real-time performance (5x faster than Whisper)
"""

import numpy as np
import logging
from typing import List, Optional, Callable
import time
from dataclasses import dataclass

# Try importing OpenWakeWord (fastest option)
try:
    import openwakeword
    from openwakeword.model import Model as OpenWakeWordModel
    _OPENWAKEWORD_AVAILABLE = True
except ImportError:
    _OPENWAKEWORD_AVAILABLE = False

# Fallback to Porcupine if available
try:
    import pvporcupine
    _PORCUPINE_AVAILABLE = True
except ImportError:
    _PORCUPINE_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class WakeWordConfig:
    """Configuration for wake word detection"""
    method: str = "openwakeword"  # "openwakeword", "porcupine", "simple"
    confidence_threshold: float = 0.5
    confirmation_frames: int = 2  # Consecutive detections needed
    debounce_ms: int = 1000  # Prevent multiple triggers
    sample_rate: int = 16000
    
    # OpenWakeWord specific
    openwakeword_models: List[str] = None
    custom_model_path: Optional[str] = None
    
    # Porcupine specific
    porcupine_access_key: Optional[str] = None
    porcupine_keywords: List[str] = None
    
    # Simple threshold detection
    simple_phrases: List[str] = None
    amplitude_threshold: float = 0.05

    def __post_init__(self):
        if self.openwakeword_models is None:
            self.openwakeword_models = ["hey_jarvis"]  # Built-in model
        if self.simple_phrases is None:
            self.simple_phrases = ["evil assistant", "dark one", "cthulhu"]


class OpenWakeWordDetector:
    """OpenWakeWord implementation - fastest and most accurate"""
    
    def __init__(self, config: WakeWordConfig):
        if not _OPENWAKEWORD_AVAILABLE:
            raise ImportError("OpenWakeWord not available. Install with: pip install openwakeword")
        
        self.config = config
        self.models = {}
        self.frame_buffer = []
        self.required_samples = int(config.sample_rate * 1.5)  # 1.5 second buffer
        
        # Load wake word models
        self._load_models()
        
        logger.info(f"OpenWakeWord initialized with models: {list(self.models.keys())}")
    
    def _load_models(self):
        """Load OpenWakeWord models"""
        try:
            # Load built-in models
            for model_name in self.config.openwakeword_models:
                if model_name in openwakeword.get_pretrained_model_names():
                    self.models[model_name] = OpenWakeWordModel(
                        wakeword_models=[model_name],
                        inference_framework="onnx"  # Fastest framework
                    )
                    logger.info(f"Loaded built-in model: {model_name}")
            
            # Load custom model if specified
            if self.config.custom_model_path:
                custom_model = OpenWakeWordModel(
                    wakeword_models=[self.config.custom_model_path],
                    inference_framework="onnx"
                )
                self.models["custom"] = custom_model
                logger.info(f"Loaded custom model: {self.config.custom_model_path}")
                
        except Exception as e:
            logger.error(f"Failed to load OpenWakeWord models: {e}")
            raise
    
    def process_audio(self, audio_chunk: np.ndarray) -> dict:
        """Process audio chunk and return detection results"""
        # Convert to required format (int16)
        if audio_chunk.dtype != np.int16:
            audio_int16 = (audio_chunk * 32767).astype(np.int16)
        else:
            audio_int16 = audio_chunk
        
        # Add to frame buffer
        self.frame_buffer.extend(audio_int16.flatten())
        
        # Keep only required samples
        if len(self.frame_buffer) > self.required_samples:
            self.frame_buffer = self.frame_buffer[-self.required_samples:]
        
        # Need enough samples for detection
        if len(self.frame_buffer) < self.required_samples:
            return {}
        
        # Run detection on all models
        results = {}
        audio_for_detection = np.array(self.frame_buffer, dtype=np.int16)
        
        for model_name, model in self.models.items():
            try:
                prediction = model.predict(audio_for_detection)
                
                # Check if any wake word exceeded threshold
                for wake_word, confidence in prediction.items():
                    if confidence > self.config.confidence_threshold:
                        results[f"{model_name}_{wake_word}"] = confidence
                        logger.info(f"Wake word detected: {wake_word} (confidence: {confidence:.2f})")
                        
            except Exception as e:
                logger.warning(f"Error in {model_name} detection: {e}")
        
        return results


class PorcupineDetector:
    """Porcupine wake word detection (commercial, very reliable)"""
    
    def __init__(self, config: WakeWordConfig):
        if not _PORCUPINE_AVAILABLE:
            raise ImportError("Porcupine not available. Install with: pip install pvporcupine")
        
        self.config = config
        self.porcupine = None
        self.frame_buffer = []
        
        if not config.porcupine_access_key:
            raise ValueError("Porcupine access key required")
        
        self._initialize_porcupine()
    
    def _initialize_porcupine(self):
        """Initialize Porcupine with keywords"""
        try:
            self.porcupine = pvporcupine.create(
                access_key=self.config.porcupine_access_key,
                keywords=self.config.porcupine_keywords or ["jarvis"]
            )
            
            self.frame_length = self.porcupine.frame_length
            logger.info(f"Porcupine initialized with frame length: {self.frame_length}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Porcupine: {e}")
            raise
    
    def process_audio(self, audio_chunk: np.ndarray) -> dict:
        """Process audio chunk with Porcupine"""
        if not self.porcupine:
            return {}
        
        # Convert to int16 if needed
        if audio_chunk.dtype != np.int16:
            audio_int16 = (audio_chunk * 32767).astype(np.int16)
        else:
            audio_int16 = audio_chunk
        
        # Add to buffer
        self.frame_buffer.extend(audio_int16.flatten())
        
        results = {}
        
        # Process complete frames
        while len(self.frame_buffer) >= self.frame_length:
            frame = np.array(self.frame_buffer[:self.frame_length], dtype=np.int16)
            self.frame_buffer = self.frame_buffer[self.frame_length:]
            
            try:
                keyword_index = self.porcupine.process(frame)
                if keyword_index >= 0:
                    keyword = self.config.porcupine_keywords[keyword_index]
                    results[f"porcupine_{keyword}"] = 0.9  # Porcupine doesn't provide confidence
                    logger.info(f"Porcupine detected: {keyword}")
            except Exception as e:
                logger.warning(f"Porcupine processing error: {e}")
        
        return results
    
    def __del__(self):
        """Cleanup Porcupine resources"""
        if self.porcupine:
            try:
                self.porcupine.delete()
            except:
                pass


class SimpleThresholdDetector:
    """Simple amplitude-based detection as fallback"""
    
    def __init__(self, config: WakeWordConfig):
        self.config = config
        self.recent_audio = []
        self.buffer_duration = 3.0  # seconds
        self.max_samples = int(config.sample_rate * self.buffer_duration)
    
    def process_audio(self, audio_chunk: np.ndarray) -> dict:
        """Simple RMS threshold detection"""
        # Add to recent audio buffer
        self.recent_audio.extend(audio_chunk.flatten())
        if len(self.recent_audio) > self.max_samples:
            self.recent_audio = self.recent_audio[-self.max_samples:]
        
        # Calculate RMS
        if len(self.recent_audio) > self.config.sample_rate:  # At least 1 second
            rms = np.sqrt(np.mean(np.array(self.recent_audio) ** 2))
            
            if rms > self.config.amplitude_threshold:
                return {"simple_amplitude": rms}
        
        return {}


class WakeWordDetector:
    """Unified wake word detector with multiple methods"""
    
    def __init__(self, config: WakeWordConfig):
        self.config = config
        self.detector = None
        self.confirmation_buffer = []
        self.last_detection_time = 0
        
        # Performance tracking
        self.stats = {
            'total_detections': 0,
            'false_positives': 0,
            'avg_processing_time': 0,
            'processing_count': 0
        }
        
        self._initialize_detector()
    
    def _initialize_detector(self):
        """Initialize the appropriate detector based on config"""
        try:
            if self.config.method == "openwakeword" and _OPENWAKEWORD_AVAILABLE:
                self.detector = OpenWakeWordDetector(self.config)
                logger.info("Using OpenWakeWord detector")
                
            elif self.config.method == "porcupine" and _PORCUPINE_AVAILABLE:
                self.detector = PorcupineDetector(self.config)
                logger.info("Using Porcupine detector")
                
            else:
                logger.warning(f"Requested method '{self.config.method}' not available, using simple detector")
                self.detector = SimpleThresholdDetector(self.config)
                
        except Exception as e:
            logger.error(f"Failed to initialize {self.config.method} detector: {e}")
            logger.info("Falling back to simple detector")
            self.detector = SimpleThresholdDetector(self.config)
    
    def process_audio(self, audio_chunk: np.ndarray) -> bool:
        """Process audio and return True if wake word detected"""
        start_time = time.time()
        
        # Check debounce
        current_time = time.time() * 1000  # milliseconds
        if current_time - self.last_detection_time < self.config.debounce_ms:
            return False
        
        # Process with current detector
        results = self.detector.process_audio(audio_chunk)
        
        # Update performance stats
        processing_time = time.time() - start_time
        self.stats['processing_count'] += 1
        self.stats['avg_processing_time'] = (
            (self.stats['avg_processing_time'] * (self.stats['processing_count'] - 1) + processing_time) /
            self.stats['processing_count']
        )
        
        # Check for detections
        detected = len(results) > 0
        
        if detected:
            self.confirmation_buffer.append(1)
            logger.debug(f"Wake word candidates: {results}")
        else:
            self.confirmation_buffer.append(0)
        
        # Keep only recent confirmations
        if len(self.confirmation_buffer) > self.config.confirmation_frames * 2:
            self.confirmation_buffer = self.confirmation_buffer[-self.config.confirmation_frames * 2:]
        
        # Check if we have enough consecutive confirmations
        if len(self.confirmation_buffer) >= self.config.confirmation_frames:
            recent_confirmations = sum(self.confirmation_buffer[-self.config.confirmation_frames:])
            
            if recent_confirmations >= self.config.confirmation_frames:
                self.last_detection_time = current_time
                self.stats['total_detections'] += 1
                self.confirmation_buffer.clear()
                
                logger.info("✅ Wake word confirmed!")
                return True
        
        return False
    
    def get_stats(self) -> dict:
        """Get detection performance statistics"""
        return {
            **self.stats,
            'avg_processing_ms': self.stats['avg_processing_time'] * 1000,
            'method': self.config.method,
            'detector_type': type(self.detector).__name__
        }
    
    def reset(self):
        """Reset detection state"""
        self.confirmation_buffer.clear()
        self.last_detection_time = 0


def download_openwakeword_models():
    """Download recommended OpenWakeWord models"""
    if not _OPENWAKEWORD_AVAILABLE:
        print("OpenWakeWord not installed. Install with: pip install openwakeword")
        return
    
    print("📥 Downloading OpenWakeWord models...")
    
    # Download pre-trained models
    recommended_models = ["hey_jarvis", "alexa", "hey_mycroft"]
    
    for model_name in recommended_models:
        try:
            # This will download the model if not already present
            model = OpenWakeWordModel(wakeword_models=[model_name])
            print(f"✅ Downloaded: {model_name}")
        except Exception as e:
            print(f"❌ Failed to download {model_name}: {e}")
    
    print("🎉 Model download complete!")


def test_wake_word_detection():
    """Test wake word detection performance"""
    import sounddevice as sd
    
    config = WakeWordConfig(
        method="openwakeword",
        confidence_threshold=0.5,
        confirmation_frames=2
    )
    
    detector = WakeWordDetector(config)
    
    print(f"🎤 Testing wake word detection with {detector.detector.__class__.__name__}")
    print("Say 'Hey Jarvis' or speak loudly to test...")
    print("Press Ctrl+C to stop")
    
    try:
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            
            # Convert to the format expected by detector
            audio_data = indata.flatten()
            
            # Test detection
            if detector.process_audio(audio_data):
                print("🔥 WAKE WORD DETECTED! 🔥")
        
        # Start audio stream
        with sd.InputStream(
            samplerate=config.sample_rate,
            channels=1,
            dtype='float32',
            blocksize=1024,
            callback=audio_callback
        ):
            while True:
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nStopping test...")
        stats = detector.get_stats()
        print(f"Stats: {stats}")


if __name__ == "__main__":
    # Download models first
    download_openwakeword_models()
    
    # Test detection
    test_wake_word_detection()
