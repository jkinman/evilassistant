#!/usr/bin/env python3
"""
Test the unified command processor
"""

import asyncio
from evilassistant.unified_command_processor import UnifiedCommandProcessor, CommandType

class MockSmartHome:
    async def process_command(self, text):
        if any(word in text.lower() for word in ['light', 'lights', 'brightness']):
            return "Mock smart home response: Lights controlled!"
        return None

class MockAI:
    def get_ai_response(self, text):
        return f"Mock AI response to: {text}"

class MockTranscription:
    pass

async def test_unified_commands():
    """Test the unified command processor"""
    print("🧪 Testing Unified Command Processor")
    print("=" * 50)
    
    # Create mock handlers
    smart_home = MockSmartHome()
    ai = MockAI()
    transcription = MockTranscription()
    
    # Create unified processor
    processor = UnifiedCommandProcessor(
        smart_home_handler=smart_home,
        ai_handler=ai,
        transcription_handler=transcription
    )
    
    # Test commands
    test_commands = [
        # Transcription commands
        "dark one start recording",
        "evil assistant begin surveillance", 
        "start recording",
        "stop transcription",
        "who spoke today",
        "stats",
        
        # Smart home commands
        "dark one turn on the lights",
        "turn off lights",
        "set brightness to 50 percent",
        "make the lights red",
        
        # AI queries
        "what is the weather",
        "tell me a joke",
        "how are you",
        
        # System commands
        "stop"
    ]
    
    for command in test_commands:
        print(f"\n🗣️  Command: '{command}'")
        try:
            command_type, response = await processor.process_command(command)
            print(f"   Type: {command_type.value}")
            print(f"   Response: {response}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📋 Command Help:")
    print(processor.get_command_help())

if __name__ == "__main__":
    asyncio.run(test_unified_commands())
