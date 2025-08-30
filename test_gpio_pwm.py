#!/usr/bin/env python3
"""
Test script for GPIO PWM LED control with Evil Assistant
"""

import time
import logging
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_gpio_controller():
    """Test the GPIO controller functionality"""
    print("🧪 Testing GPIO PWM Controller")
    print("=" * 50)
    
    try:
        from evilassistant.gpio_controller import get_gpio_controller
        
        # Get GPIO controller
        gpio = get_gpio_controller()
        
        if not gpio:
            print("❌ Failed to initialize GPIO controller")
            return
        
        # Print status
        status = gpio.get_status()
        print("📋 GPIO Status:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        if not status['gpio_available']:
            print("⚠️  GPIO not available - test results limited")
            return
        
        print("\n🔆 Testing LED sequence...")
        gpio.test_led_sequence(duration=10.0)
        
        print("\n✅ GPIO PWM test completed!")
        
    except Exception as e:
        print(f"❌ GPIO test failed: {e}")
        import traceback
        traceback.print_exc()

def test_audio_manager():
    """Test the audio manager with GPIO integration"""
    print("\n🎵 Testing Audio Manager with GPIO Integration")
    print("=" * 60)
    
    try:
        from evilassistant.audio_manager import get_audio_manager
        
        # Get audio manager
        audio = get_audio_manager()
        
        # Print status
        status = audio.get_status()
        print("📋 Audio Manager Status:")
        print(f"   Audio initialized: {status['audio_initialized']}")
        print(f"   GPIO available: {status['gpio']['gpio_available']}")
        
        # Test LED functionality
        print("\n🧪 Testing LED functionality...")
        audio.test_led_functionality()
        
        # Test TTS synthesis (if possible)
        print("\n🎭 Testing TTS synthesis...")
        success = audio.synthesize_speech("Testing GPIO PWM LED control with demonic voice", "test_gpio.wav")
        
        if success:
            print("✅ TTS synthesis successful")
            
            # Test playback with LED control
            print("🔊 Testing audio playback with LED control...")
            audio.play_audio_file("test_gpio.wav", enable_led_control=True)
            
            # Clean up test file
            import os
            if os.path.exists("test_gpio.wav"):
                os.remove("test_gpio.wav")
        else:
            print("❌ TTS synthesis failed")
        
        print("\n✅ Audio manager test completed!")
        
    except Exception as e:
        print(f"❌ Audio manager test failed: {e}")
        import traceback
        traceback.print_exc()

def test_integrated_system():
    """Test the complete integrated system"""
    print("\n🔗 Testing Integrated Audio + GPIO System")
    print("=" * 50)
    
    try:
        from evilassistant.assistant_clean import AudioHandler
        
        # Initialize audio handler (which uses audio manager)
        audio_handler = AudioHandler()
        
        # Get status
        status = audio_handler.get_status()
        print("📋 Integrated System Status:")
        print(f"   Audio initialized: {status.get('audio_initialized', 'N/A')}")
        gpio_status = status.get('gpio', {})
        print(f"   GPIO available: {gpio_status.get('gpio_available', 'N/A')}")
        print(f"   PWM enabled: {gpio_status.get('pwm_enabled', 'N/A')}")
        
        # Test LED
        print("\n🧪 Testing LED through audio handler...")
        audio_handler.test_led_functionality()
        
        # Test synthesis
        print("\n🎭 Testing speech synthesis...")
        success = audio_handler.synthesize_speech(
            "The demonic LED panel responds to my dark voice", 
            "test_integrated.wav"
        )
        
        if success:
            print("✅ Speech synthesis successful")
            
            # Test playback
            print("🔊 Testing integrated playback with LED control...")
            audio_handler.play_audio_file("test_integrated.wav")
            
            # Clean up
            import os
            if os.path.exists("test_integrated.wav"):
                os.remove("test_integrated.wav")
        else:
            print("❌ Speech synthesis failed")
        
        # Clean up
        audio_handler.cleanup()
        
        print("\n✅ Integrated system test completed!")
        
    except Exception as e:
        print(f"❌ Integrated test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description='Test GPIO PWM functionality')
    parser.add_argument('--component', choices=['gpio', 'audio', 'integrated', 'all'], 
                       default='all', help='Which component to test')
    
    args = parser.parse_args()
    
    print("🔥 Evil Assistant GPIO PWM Test Suite")
    print("=" * 60)
    
    if args.component in ['gpio', 'all']:
        test_gpio_controller()
    
    if args.component in ['audio', 'all']:
        test_audio_manager()
    
    if args.component in ['integrated', 'all']:
        test_integrated_system()
    
    print("\n🎉 All tests completed!")
    print("\n💡 Usage Instructions:")
    print("   1. Connect your LED panel dimmer to GPIO pin 18")
    print("   2. Connect your PWM-to-10V module between Pi and dimmer")
    print("   3. Run Evil Assistant - LEDs should respond to voice output!")
    print("   4. Wire diagram: Pi GPIO18 -> PWM-to-10V module -> LED dimmer (1-10V input)")

if __name__ == "__main__":
    main()
