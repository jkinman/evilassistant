"""
Real-time audio effects for Evil Assistant
Replaces Sox with fast scipy.signal DSP for demonic voice transformation
"""

import numpy as np
from scipy import signal
from scipy.interpolate import interp1d
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class EffectConfig:
    """Configuration for a single audio effect"""
    name: str
    enabled: bool = True
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class EffectsChainConfig:
    """Configuration for the complete effects chain"""
    sample_rate: int = 16000
    buffer_size: int = 1024
    effects: List[EffectConfig] = None
    
    def __post_init__(self):
        if self.effects is None:
            # Default demonic voice effects chain
            self.effects = [
                EffectConfig("normalize", True, {"target_level": -3}),
                EffectConfig("bass_boost", True, {"frequency": 100, "gain": 6}),
                EffectConfig("treble_cut", True, {"frequency": 4000, "gain": -3}),
                EffectConfig("pitch_shift", True, {"semitones": -12}),
                EffectConfig("formant_shift", True, {"factor": 0.8}),
                EffectConfig("tempo_change", True, {"factor": 0.88}),
                EffectConfig("distortion", True, {"gain": 1.5, "mix": 0.3}),
                EffectConfig("reverb", True, {"room_size": 0.8, "damping": 0.3, "wet": 0.2}),
            ]


class BaseEffect:
    """Base class for audio effects"""
    
    def __init__(self, sample_rate: int, config: EffectConfig):
        self.sample_rate = sample_rate
        self.config = config
        self.initialized = False
        self.state = {}  # For stateful effects
        
    def initialize(self):
        """Initialize effect parameters"""
        self.initialized = True
        
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process audio through this effect"""
        if not self.initialized:
            self.initialize()
            
        if not self.config.enabled:
            return audio
            
        return self._process_impl(audio)
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        """Implement the actual effect processing"""
        raise NotImplementedError
    
    def reset(self):
        """Reset effect state"""
        self.state = {}


class NormalizeEffect(BaseEffect):
    """Normalize audio to target level"""
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        target_db = self.config.parameters.get("target_level", -3)
        target_linear = 10 ** (target_db / 20)
        
        # RMS normalization
        rms = np.sqrt(np.mean(audio ** 2))
        if rms > 0:
            gain = target_linear / rms
            # Prevent excessive amplification
            gain = min(gain, 10.0)
            return audio * gain
        return audio


class BassBoostEffect(BaseEffect):
    """Boost low frequencies"""
    
    def initialize(self):
        freq = self.config.parameters.get("frequency", 100)
        gain_db = self.config.parameters.get("gain", 6)
        
        # Design low-shelf filter
        nyquist = self.sample_rate / 2
        self.b, self.a = signal.iirfilter(
            2, freq / nyquist, btype='low', ftype='butter'
        )
        
        # Convert gain to linear
        self.gain = 10 ** (gain_db / 20)
        self.initialized = True
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        # Apply low-pass filter and boost
        filtered = signal.filtfilt(self.b, self.a, audio)
        return audio + (filtered * (self.gain - 1))


class TrebleCutEffect(BaseEffect):
    """Cut high frequencies"""
    
    def initialize(self):
        freq = self.config.parameters.get("frequency", 4000)
        gain_db = self.config.parameters.get("gain", -3)
        
        # Design high-shelf filter
        nyquist = self.sample_rate / 2
        self.b, self.a = signal.iirfilter(
            2, freq / nyquist, btype='high', ftype='butter'
        )
        
        self.gain = 10 ** (gain_db / 20)
        self.initialized = True
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        # Apply high-pass filter and attenuate
        filtered = signal.filtfilt(self.b, self.a, audio)
        return audio + (filtered * (self.gain - 1))


class PitchShiftEffect(BaseEffect):
    """Pitch shifting using phase vocoder technique"""
    
    def initialize(self):
        self.semitones = self.config.parameters.get("semitones", -12)
        self.shift_factor = 2 ** (self.semitones / 12)
        self.frame_size = 2048
        self.hop_size = self.frame_size // 4
        
        # Initialize phase vocoder state
        self.phase_advance = np.linspace(0, np.pi * self.hop_size, self.frame_size // 2 + 1)
        self.last_phase = np.zeros(self.frame_size // 2 + 1)
        self.sum_phase = np.zeros(self.frame_size // 2 + 1)
        
        self.initialized = True
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        # Simple pitch shifting via resampling (faster but lower quality)
        # For better quality, implement PSOLA or phase vocoder
        
        if self.shift_factor == 1.0:
            return audio
        
        # Resample for pitch shift
        original_length = len(audio)
        indices = np.arange(0, original_length, self.shift_factor)
        
        if len(indices) < 2:
            return audio
        
        # Interpolate
        f = interp1d(np.arange(original_length), audio, kind='linear', 
                    bounds_error=False, fill_value=0)
        shifted = f(indices)
        
        # Resize to original length
        if len(shifted) != original_length:
            f2 = interp1d(np.arange(len(shifted)), shifted, kind='linear',
                         bounds_error=False, fill_value=0)
            shifted = f2(np.linspace(0, len(shifted) - 1, original_length))
        
        return shifted


class FormantShiftEffect(BaseEffect):
    """Shift formants to change vocal tract characteristics"""
    
    def initialize(self):
        self.factor = self.config.parameters.get("factor", 0.8)
        
        # Simple formant shifting using spectral envelope manipulation
        # Create formant filter banks
        formant_freqs = [800, 1200, 2600]  # Typical formant frequencies
        self.filters = []
        
        for freq in formant_freqs:
            nyquist = self.sample_rate / 2
            normalized_freq = freq / nyquist
            if normalized_freq < 1.0:
                b, a = signal.iirfilter(4, normalized_freq, btype='band', ftype='butter')
                self.filters.append((b, a))
        
        self.initialized = True
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        # Simple formant shifting by frequency domain manipulation
        # For production, use proper formant analysis/synthesis
        
        if self.factor == 1.0:
            return audio
        
        # Apply bandpass filters and frequency shift
        processed = audio.copy()
        
        for b, a in self.filters:
            formant_component = signal.filtfilt(b, a, audio)
            # Simple frequency shifting by resampling
            if self.factor != 1.0:
                length = len(formant_component)
                indices = np.arange(0, length, 1.0 / self.factor)
                if len(indices) > 1:
                    f = interp1d(np.arange(length), formant_component, 
                               kind='linear', bounds_error=False, fill_value=0)
                    shifted_formant = f(indices[:length])
                    processed += (shifted_formant - formant_component) * 0.3
        
        return processed


class TempoChangeEffect(BaseEffect):
    """Change tempo without affecting pitch"""
    
    def initialize(self):
        self.factor = self.config.parameters.get("factor", 0.88)
        self.initialized = True
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        if self.factor == 1.0:
            return audio
        
        # Time-domain stretching
        target_length = int(len(audio) / self.factor)
        indices = np.linspace(0, len(audio) - 1, target_length)
        
        f = interp1d(np.arange(len(audio)), audio, kind='cubic',
                    bounds_error=False, fill_value=0)
        stretched = f(indices)
        
        # Pad or truncate to original length
        if len(stretched) > len(audio):
            return stretched[:len(audio)]
        else:
            padded = np.zeros(len(audio))
            padded[:len(stretched)] = stretched
            return padded


class DistortionEffect(BaseEffect):
    """Add harmonic distortion for demonic character"""
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        gain = self.config.parameters.get("gain", 1.5)
        mix = self.config.parameters.get("mix", 0.3)
        
        # Soft clipping distortion
        driven = audio * gain
        distorted = np.tanh(driven)
        
        # Mix with original
        return audio * (1 - mix) + distorted * mix


class ReverbEffect(BaseEffect):
    """Simple reverb using delay lines"""
    
    def initialize(self):
        self.room_size = self.config.parameters.get("room_size", 0.8)
        self.damping = self.config.parameters.get("damping", 0.3)
        self.wet = self.config.parameters.get("wet", 0.2)
        
        # Create delay lines for simple reverb
        delay_times = [0.03, 0.05, 0.07, 0.09]  # seconds
        self.delays = []
        
        for delay_time in delay_times:
            delay_samples = int(delay_time * self.sample_rate)
            self.delays.append(np.zeros(delay_samples))
        
        self.delay_indices = [0] * len(self.delays)
        self.initialized = True
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        output = audio.copy()
        reverb_sum = np.zeros(len(audio))
        
        for i, sample in enumerate(audio):
            # Process each delay line
            for j, delay_line in enumerate(self.delays):
                # Get delayed sample
                delayed = delay_line[self.delay_indices[j]]
                reverb_sum[i] += delayed * (1 - j * 0.1)  # Decrease level for longer delays
                
                # Add current sample to delay line with damping
                delay_line[self.delay_indices[j]] = sample * self.room_size + delayed * self.damping
                
                # Advance delay index
                self.delay_indices[j] = (self.delay_indices[j] + 1) % len(delay_line)
        
        # Mix reverb with dry signal
        return output * (1 - self.wet) + reverb_sum * self.wet


class RealtimeEffectsProcessor:
    """Real-time effects processing chain"""
    
    def __init__(self, config: EffectsChainConfig):
        self.config = config
        self.effects = []
        self.stats = {
            'total_processed': 0,
            'avg_processing_time': 0,
            'max_processing_time': 0
        }
        
        self._create_effects_chain()
        logger.info(f"Initialized effects chain with {len(self.effects)} effects")
    
    def _create_effects_chain(self):
        """Create the effects processing chain"""
        effect_classes = {
            'normalize': NormalizeEffect,
            'bass_boost': BassBoostEffect,
            'treble_cut': TrebleCutEffect,
            'pitch_shift': PitchShiftEffect,
            'formant_shift': FormantShiftEffect,
            'tempo_change': TempoChangeEffect,
            'distortion': DistortionEffect,
            'reverb': ReverbEffect,
        }
        
        for effect_config in self.config.effects:
            if effect_config.name in effect_classes:
                effect_class = effect_classes[effect_config.name]
                effect = effect_class(self.config.sample_rate, effect_config)
                self.effects.append(effect)
                logger.debug(f"Added effect: {effect_config.name}")
            else:
                logger.warning(f"Unknown effect: {effect_config.name}")
    
    def process_audio(self, audio: np.ndarray) -> np.ndarray:
        """Process audio through the complete effects chain"""
        start_time = time.time()
        
        processed = audio.copy()
        
        # Apply each effect in sequence
        for effect in self.effects:
            try:
                processed = effect.process(processed)
            except Exception as e:
                logger.error(f"Error in effect {effect.config.name}: {e}")
                # Continue with unprocessed audio
        
        # Update performance stats
        processing_time = time.time() - start_time
        self.stats['total_processed'] += 1
        self.stats['avg_processing_time'] = (
            (self.stats['avg_processing_time'] * (self.stats['total_processed'] - 1) + processing_time) /
            self.stats['total_processed']
        )
        self.stats['max_processing_time'] = max(self.stats['max_processing_time'], processing_time)
        
        # Warn if processing is too slow
        max_allowed_time = len(audio) / self.config.sample_rate * 0.5  # 50% of real-time
        if processing_time > max_allowed_time:
            logger.warning(f"Effects processing too slow: {processing_time*1000:.1f}ms "
                          f"for {len(audio)/self.config.sample_rate*1000:.1f}ms audio")
        
        return processed
    
    def get_stats(self) -> dict:
        """Get processing performance statistics"""
        return {
            **self.stats,
            'avg_processing_ms': self.stats['avg_processing_time'] * 1000,
            'max_processing_ms': self.stats['max_processing_time'] * 1000,
            'total_effects': len(self.effects),
            'enabled_effects': sum(1 for e in self.effects if e.config.enabled)
        }
    
    def enable_effect(self, effect_name: str, enabled: bool = True):
        """Enable or disable a specific effect"""
        for effect in self.effects:
            if effect.config.name == effect_name:
                effect.config.enabled = enabled
                logger.info(f"Effect {effect_name} {'enabled' if enabled else 'disabled'}")
                return
        logger.warning(f"Effect not found: {effect_name}")
    
    def reset_all_effects(self):
        """Reset state of all effects"""
        for effect in self.effects:
            effect.reset()


def create_demonic_voice_config(sample_rate: int = 16000) -> EffectsChainConfig:
    """Create optimized configuration for demonic voice"""
    return EffectsChainConfig(
        sample_rate=sample_rate,
        effects=[
            EffectConfig("normalize", True, {"target_level": -6}),
            EffectConfig("bass_boost", True, {"frequency": 80, "gain": 8}),
            EffectConfig("treble_cut", True, {"frequency": 3000, "gain": -4}),
            EffectConfig("pitch_shift", True, {"semitones": -15}),  # More demonic
            EffectConfig("formant_shift", True, {"factor": 0.7}),   # Larger vocal tract
            EffectConfig("distortion", True, {"gain": 2.0, "mix": 0.4}),  # More grit
            EffectConfig("reverb", True, {"room_size": 0.9, "damping": 0.2, "wet": 0.3}),  # Cavernous
        ]
    )


def test_effects_chain():
    """Test the effects processing chain"""
    import sounddevice as sd
    import time
    
    # Create test configuration
    config = create_demonic_voice_config()
    processor = RealtimeEffectsProcessor(config)
    
    print("🔥 Testing real-time effects chain")
    print("Speak into the microphone to hear the demonic transformation...")
    print("Press Ctrl+C to stop")
    
    # Audio callback for real-time processing
    def audio_callback(indata, outdata, frames, time, status):
        if status:
            print(f"Audio status: {status}")
        
        # Process input through effects chain
        input_audio = indata.flatten()
        processed_audio = processor.process_audio(input_audio)
        
        # Output processed audio
        outdata[:] = processed_audio.reshape(-1, 1)
    
    try:
        # Start real-time audio processing
        with sd.Stream(
            samplerate=config.sample_rate,
            channels=1,
            dtype='float32',
            blocksize=config.buffer_size,
            callback=audio_callback
        ):
            print("🎤 Real-time effects active!")
            while True:
                time.sleep(1)
                stats = processor.get_stats()
                if stats['total_processed'] > 0:
                    print(f"Processed: {stats['total_processed']} chunks, "
                          f"avg: {stats['avg_processing_ms']:.1f}ms, "
                          f"max: {stats['max_processing_ms']:.1f}ms")
    
    except KeyboardInterrupt:
        print("\nStopping effects test...")
        final_stats = processor.get_stats()
        print(f"Final stats: {final_stats}")


if __name__ == "__main__":
    test_effects_chain()
