#!/usr/bin/env python3
"""
GPIO Controller for Evil Assistant
Handles all GPIO operations including PWM LED control based on audio output
"""

import threading
import time
import numpy as np
import logging
from typing import Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PWMConfig:
    """Configuration for PWM LED control"""
    pin: int = 18
    frequency: int = 1000
    brightness_min: float = 5.0
    brightness_max: float = 85.0
    gain: float = 120.0
    smoothing: float = 0.85
    enabled: bool = True

class GPIOController:
    """
    Centralized GPIO control for Evil Assistant
    Handles PWM LED control with audio envelope following
    """
    
    def __init__(self, config: PWMConfig):
        self.config = config
        self.pwm = None
        self.gpio_available = False
        self._running = False
        self._smoothed_brightness = 0.0
        self._audio_callback: Optional[Callable] = None
        self._pwm_thread: Optional[threading.Thread] = None
        
        # Initialize GPIO if available
        self._initialize_gpio()
    
    def _initialize_gpio(self):
        """Initialize GPIO and PWM if running on Raspberry Pi"""
        if not self.config.enabled:
            logger.info("GPIO PWM disabled in configuration")
            return
            
        try:
            # Check if we're on a Raspberry Pi - try multiple detection methods
            is_pi = False
            
            # Method 1: Check /proc/device-tree/model (most reliable)
            try:
                with open('/proc/device-tree/model', 'r') as f:
                    model = f.read().strip()
                    if 'Raspberry Pi' in model:
                        is_pi = True
                        logger.info(f"Detected Pi model: {model}")
            except:
                pass
            
            # Method 2: Check /proc/cpuinfo as fallback
            if not is_pi:
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        cpuinfo = f.read()
                        if any(indicator in cpuinfo for indicator in ['BCM', 'Raspberry Pi', 'ARM']):
                            is_pi = True
                            logger.info("Detected Pi from /proc/cpuinfo")
                except:
                    pass
            
            if not is_pi:
                logger.info("Not running on Raspberry Pi - GPIO disabled")
                return
                
        except Exception as e:
            logger.warning(f"Could not detect Pi hardware: {e} - GPIO disabled")
            return
            
        try:
            # Try gpiozero first (better Pi 4/5 support, handles SOC issues better)
            try:
                from gpiozero import PWMOutputDevice
                
                # Create PWM device with error handling for SOC issues
                self.pwm = PWMOutputDevice(self.config.pin, frequency=self.config.frequency)
                self.pwm.value = 0.0  # Start with 0% duty cycle
                
                self.gpio_available = True
                self._use_gpiozero = True
                logger.info(f"✅ GPIO PWM initialized with gpiozero on pin {self.config.pin} at {self.config.frequency}Hz")
                
            except ImportError:
                logger.debug("gpiozero not available, trying RPi.GPIO")
                self._try_rpi_gpio()
                
            except Exception as gpio_err:
                logger.warning(f"gpiozero failed ({gpio_err}), trying RPi.GPIO fallback")
                self._try_rpi_gpio()
            
        except Exception as e:
            logger.error(f"All GPIO initialization methods failed: {e}")
    
    def _try_rpi_gpio(self):
        """Try to initialize GPIO using RPi.GPIO as fallback"""
        try:
            import RPi.GPIO as GPIO
            
            # Setup GPIO with better error handling
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)  # Suppress warnings for already configured pins
            GPIO.setup(self.config.pin, GPIO.OUT)
            
            # Create PWM instance
            self.pwm = GPIO.PWM(self.config.pin, self.config.frequency)
            self.pwm.start(0)  # Start with 0% duty cycle
            
            self.gpio_available = True
            self._use_gpiozero = False
            logger.info(f"✅ GPIO PWM initialized with RPi.GPIO on pin {self.config.pin} at {self.config.frequency}Hz")
            
        except ImportError:
            logger.warning("RPi.GPIO not available - GPIO PWM disabled")
        except Exception as e:
            logger.error(f"RPi.GPIO initialization failed: {e} - GPIO PWM disabled")
    
    def start_audio_envelope_following(self, audio_data_callback: Callable[[], Optional[np.ndarray]]):
        """
        Start following audio envelope for LED brightness control
        
        Args:
            audio_data_callback: Function that returns current audio data or None
        """
        if not self.gpio_available:
            logger.debug("GPIO not available - skipping envelope following")
            return
            
        if self._running:
            logger.warning("Audio envelope following already running")
            return
            
        self._audio_callback = audio_data_callback
        self._running = True
        
        # Start PWM update thread
        self._pwm_thread = threading.Thread(target=self._pwm_update_loop, daemon=True)
        self._pwm_thread.start()
        
        logger.info("🎵 Started audio envelope following for LED control")
    
    def stop_audio_envelope_following(self):
        """Stop audio envelope following"""
        if not self._running:
            return
            
        self._running = False
        
        if self._pwm_thread:
            self._pwm_thread.join(timeout=1.0)
            self._pwm_thread = None
            
        # Reset LED to minimum brightness
        if self.gpio_available and self.pwm:
            if hasattr(self, '_use_gpiozero') and self._use_gpiozero:
                self.pwm.value = self.config.brightness_min / 100.0
            else:
                self.pwm.ChangeDutyCycle(self.config.brightness_min)
            
        logger.info("🔇 Stopped audio envelope following")
    
    def _pwm_update_loop(self):
        """Main loop for updating PWM based on audio amplitude"""
        logger.debug("PWM update loop started")
        
        while self._running:
            try:
                # Get current audio data
                if self._audio_callback:
                    audio_data = self._audio_callback()
                    
                    if audio_data is not None and len(audio_data) > 0:
                        # Calculate RMS amplitude
                        rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
                        
                        # Scale to brightness (0-100%) with better scaling
                        # Normalize RMS to a more reasonable range (0-1)
                        normalized_rms = min(1.0, rms * self.config.gain)
                        
                        target_brightness = (
                            self.config.brightness_min + 
                            (self.config.brightness_max - self.config.brightness_min) * normalized_rms
                        )
                        
                        # Apply smoothing to prevent flickering
                        self._smoothed_brightness = (
                            self.config.smoothing * self._smoothed_brightness +
                            (1 - self.config.smoothing) * target_brightness
                        )
                        
                        # Update PWM duty cycle
                        if self.pwm:
                            if hasattr(self, '_use_gpiozero') and self._use_gpiozero:
                                # gpiozero uses 0.0-1.0 range
                                self.pwm.value = self._smoothed_brightness / 100.0
                            else:
                                # RPi.GPIO uses 0-100 range
                                self.pwm.ChangeDutyCycle(self._smoothed_brightness)
                        
                        # More frequent logging for debugging
                        if hasattr(self, '_debug_counter'):
                            self._debug_counter += 1
                        else:
                            self._debug_counter = 0
                            
                        if self._debug_counter % 10 == 0:  # Log every 10th update
                            logger.info(f"🔆 LED: {self._smoothed_brightness:.1f}% (RMS: {rms:.4f}, norm: {normalized_rms:.4f})")
                    
                    else:
                        # No audio - fade to minimum
                        self._smoothed_brightness = (
                            self.config.smoothing * self._smoothed_brightness +
                            (1 - self.config.smoothing) * self.config.brightness_min
                        )
                        
                        if self.pwm:
                            if hasattr(self, '_use_gpiozero') and self._use_gpiozero:
                                # gpiozero uses 0.0-1.0 range
                                self.pwm.value = self._smoothed_brightness / 100.0
                            else:
                                # RPi.GPIO uses 0-100 range
                                self.pwm.ChangeDutyCycle(self._smoothed_brightness)
                
                # Update rate (100Hz for smooth LED response)
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in PWM update loop: {e}")
                time.sleep(0.1)  # Slower retry on error
    
    def set_manual_brightness(self, brightness: float):
        """
        Manually set LED brightness (bypasses audio following)
        
        Args:
            brightness: Brightness percentage (0-100)
        """
        if not self.gpio_available or not self.pwm:
            return
            
        brightness = max(0.0, min(100.0, brightness))
        
        if hasattr(self, '_use_gpiozero') and self._use_gpiozero:
            # gpiozero uses 0.0-1.0 range
            self.pwm.value = brightness / 100.0
        else:
            # RPi.GPIO uses 0-100 range
            self.pwm.ChangeDutyCycle(brightness)
            
        logger.info(f"Manual LED brightness set to {brightness:.1f}%")
    
    def test_led_sequence(self, duration: float = 5.0):
        """
        Test LED with a brightness sequence
        
        Args:
            duration: Total test duration in seconds
        """
        if not self.gpio_available or not self.pwm:
            logger.warning("GPIO not available for LED test")
            return
            
        logger.info("🧪 Starting LED test sequence...")
        
        try:
            steps = 50
            for i in range(steps):
                # Create a sine wave brightness pattern
                brightness = (
                    self.config.brightness_min + 
                    (self.config.brightness_max - self.config.brightness_min) *
                    (0.5 + 0.5 * np.sin(2 * np.pi * i / steps))
                )
                
                if hasattr(self, '_use_gpiozero') and self._use_gpiozero:
                    # gpiozero uses 0.0-1.0 range
                    self.pwm.value = brightness / 100.0
                else:
                    # RPi.GPIO uses 0-100 range
                    self.pwm.ChangeDutyCycle(brightness)
                    
                time.sleep(duration / steps)
                
            # Return to minimum
            if hasattr(self, '_use_gpiozero') and self._use_gpiozero:
                self.pwm.value = self.config.brightness_min / 100.0
            else:
                self.pwm.ChangeDutyCycle(self.config.brightness_min)
            logger.info("✅ LED test sequence completed")
            
        except Exception as e:
            logger.error(f"LED test failed: {e}")
    
    def cleanup(self):
        """Clean up GPIO resources"""
        logger.info("🧹 Cleaning up GPIO resources...")
        
        # Stop envelope following
        self.stop_audio_envelope_following()
        
        # Clean up PWM
        if self.pwm:
            try:
                if hasattr(self, '_use_gpiozero') and self._use_gpiozero:
                    # gpiozero cleanup
                    self.pwm.close()
                else:
                    # RPi.GPIO cleanup
                    self.pwm.stop()
            except:
                pass
                
        # Clean up GPIO
        if self.gpio_available:
            try:
                if not (hasattr(self, '_use_gpiozero') and self._use_gpiozero):
                    # Only cleanup RPi.GPIO if we used it
                    import RPi.GPIO as GPIO
                    GPIO.cleanup()
                logger.info("✅ GPIO cleanup completed")
            except:
                pass
    
    def get_status(self) -> dict:
        """Get current GPIO/PWM status"""
        return {
            "gpio_available": self.gpio_available,
            "pwm_enabled": self.config.enabled,
            "pin": self.config.pin,
            "frequency": self.config.frequency,
            "running": self._running,
            "current_brightness": self._smoothed_brightness,
            "config": {
                "brightness_min": self.config.brightness_min,
                "brightness_max": self.config.brightness_max,
                "gain": self.config.gain,
                "smoothing": self.config.smoothing
            }
        }

# Global GPIO controller instance
_gpio_controller: Optional[GPIOController] = None

def get_gpio_controller() -> Optional[GPIOController]:
    """Get the global GPIO controller instance"""
    global _gpio_controller
    
    if _gpio_controller is None:
        # Import config here to avoid circular imports
        try:
            from .config import (
                GPIO_ENABLED, GPIO_PIN, PWM_FREQUENCY_HZ,
                BRIGHTNESS_MIN, BRIGHTNESS_MAX, LED_GAIN, AMPLITUDE_SMOOTHING
            )
            
            config = PWMConfig(
                pin=GPIO_PIN,
                frequency=PWM_FREQUENCY_HZ,
                brightness_min=BRIGHTNESS_MIN,
                brightness_max=BRIGHTNESS_MAX,
                gain=LED_GAIN,
                smoothing=AMPLITUDE_SMOOTHING,
                enabled=GPIO_ENABLED
            )
            
            _gpio_controller = GPIOController(config)
            
        except ImportError as e:
            logger.error(f"Failed to import GPIO configuration: {e}")
            
    return _gpio_controller

def cleanup_gpio():
    """Clean up global GPIO controller"""
    global _gpio_controller
    
    if _gpio_controller:
        _gpio_controller.cleanup()
        _gpio_controller = None
