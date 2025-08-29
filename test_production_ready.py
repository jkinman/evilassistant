#!/usr/bin/env python3
"""
Comprehensive test for production-ready Evil Assistant
"""

import asyncio
import numpy as np
from evilassistant.audio_utils import temporary_wav_file, get_audio_manager
from evilassistant.error_handling import evil_error_handler, validate_environment
from evilassistant.config_manager import get_config_manager
from evilassistant.privacy_manager import get_privacy_manager
from evilassistant.unified_command_processor import UnifiedCommandProcessor

@evil_error_handler("Test failed with evil error!")
def test_resource_management():
    """Test proper resource management"""
    print("🧪 Testing Resource Management...")
    
    # Create test audio data
    audio_data = np.random.normal(0, 0.1, 16000)  # 1 second of audio
    
    # Test context manager
    with temporary_wav_file(audio_data) as wav_path:
        print(f"✅ Created temporary file: {wav_path}")
        assert wav_path.endswith('.wav')
        import os
        assert os.path.exists(wav_path)
    
    # File should be cleaned up
    assert not os.path.exists(wav_path)
    print("✅ Resource cleanup verified")

@evil_error_handler("Configuration test failed!")
def test_configuration():
    """Test configuration management"""
    print("🧪 Testing Configuration Management...")
    
    config_manager = get_config_manager()
    config = config_manager.get_config()
    
    print(f"✅ Audio sample rate: {config.audio.sample_rate}")
    print(f"✅ TTS provider: {config.tts.provider}")
    print(f"✅ Wake phrases: {len(config.wake_phrases)}")
    
    # Test validation
    issues = config_manager.validate_config()
    print(f"📋 Configuration issues: {len(issues)}")
    for issue in issues:
        print(f"   ⚠️  {issue}")

@evil_error_handler("Privacy test failed!")
def test_privacy_manager():
    """Test privacy management"""
    print("🧪 Testing Privacy Manager...")
    
    privacy_manager = get_privacy_manager()
    
    # Test status
    status = privacy_manager.get_privacy_status()
    print(f"✅ Privacy status:\n{status}")

def test_environment_validation():
    """Test environment validation"""
    print("🧪 Testing Environment Validation...")
    
    issues = validate_environment()
    print(f"📋 Environment issues: {len(issues)}")
    for issue in issues:
        print(f"   ⚠️  {issue}")

async def test_unified_commands():
    """Test unified command processor"""
    print("🧪 Testing Unified Command Processor...")
    
    # Mock handlers for testing
    class MockSmartHome:
        async def process_command(self, text):
            if 'light' in text.lower():
                return "Mock: Lights controlled!"
            return None
    
    class MockAI:
        def get_ai_response(self, text):
            return f"Mock AI: {text}"
    
    processor = UnifiedCommandProcessor(
        smart_home_handler=MockSmartHome(),
        ai_handler=MockAI(),
        transcription_handler=None  # Will test without transcription
    )
    
    test_commands = [
        "turn on the lights",
        "what's the weather",
        "stop"
    ]
    
    for command in test_commands:
        command_type, response = await processor.process_command(command)
        print(f"✅ '{command}' → {command_type.value}: {response}")

async def main():
    """Run comprehensive production tests"""
    print("🔥 EVIL ASSISTANT PRODUCTION READINESS TEST")
    print("=" * 60)
    
    # Test 1: Resource Management
    test_resource_management()
    print()
    
    # Test 2: Configuration
    test_configuration()
    print()
    
    # Test 3: Privacy Manager
    test_privacy_manager()
    print()
    
    # Test 4: Environment Validation
    test_environment_validation()
    print()
    
    # Test 5: Unified Commands
    await test_unified_commands()
    print()
    
    print("🎯 PRODUCTION TESTS COMPLETE!")
    print("🔥 Evil Assistant is ready to dominate the digital realm!")

if __name__ == "__main__":
    asyncio.run(main())
