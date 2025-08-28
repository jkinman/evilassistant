#!/usr/bin/env python3
"""
Setup script for optimized Evil Assistant
Downloads models and sets up dependencies
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_python_version():
    """Ensure Python 3.11+"""
    if sys.version_info < (3, 11):
        logger.error("Python 3.11+ required")
        return False
    logger.info(f"✅ Python {sys.version}")
    return True


def install_system_dependencies():
    """Install system-level dependencies"""
    logger.info("📦 Installing system dependencies...")
    
    # For Raspberry Pi
    if os.path.exists("/etc/rpi-issue"):
        commands = [
            "sudo apt update",
            "sudo apt install -y portaudio19-dev python3-dev",
            "sudo apt install -y alsa-utils pulseaudio",
            "sudo apt install -y build-essential cmake",
        ]
        
        for cmd in commands:
            logger.info(f"Running: {cmd}")
            subprocess.run(cmd.split(), check=False)
    
    logger.info("✅ System dependencies installed")


def download_vosk_models():
    """Download Vosk models for fast STT"""
    logger.info("📥 Downloading Vosk models...")
    
    os.makedirs("models", exist_ok=True)
    
    models = {
        "vosk-model-small-en-us-0.15": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
            "size": "40MB"
        }
    }
    
    for model_name, info in models.items():
        model_path = f"models/{model_name}"
        
        if os.path.exists(model_path):
            logger.info(f"✅ Model exists: {model_name}")
            continue
        
        logger.info(f"📥 Downloading {model_name} ({info['size']})...")
        zip_path = f"models/{model_name}.zip"
        
        try:
            urllib.request.urlretrieve(info["url"], zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("models/")
            
            os.remove(zip_path)
            logger.info(f"✅ Downloaded: {model_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to download {model_name}: {e}")


def setup_ollama():
    """Setup Ollama for local LLM"""
    logger.info("🦙 Setting up Ollama...")
    
    # Check if Ollama is installed
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ Ollama already installed")
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        logger.info("📥 Installing Ollama...")
        # Install Ollama
        subprocess.run([
            "curl", "-fsSL", "https://ollama.ai/install.sh"
        ], check=False, stdout=subprocess.PIPE)
    
    # Pull recommended model
    try:
        logger.info("📥 Pulling llama3.2:3b model...")
        subprocess.run(["ollama", "pull", "llama3.2:3b"], check=False)
        logger.info("✅ Ollama model ready")
    except Exception as e:
        logger.warning(f"⚠️ Failed to pull model: {e}")
        logger.info("You can manually run: ollama pull llama3.2:3b")


def create_env_template():
    """Create environment template"""
    env_template = """# Evil Assistant Environment Variables

# API Keys
XAI_API_KEY=your_xai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here
PORCUPINE_ACCESS_KEY=your_porcupine_key_here

# Ollama settings (if using local LLM)
OLLAMA_BASE_URL=http://localhost:11434

# Home Assistant (if using smart home)
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=your_ha_token_here

# Philips Hue (if using smart home)
PHILIPS_HUE_BRIDGE_IP=192.168.1.100
"""
    
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_template)
        logger.info("✅ Created .env template - please fill in your API keys")
    else:
        logger.info("✅ .env file already exists")


def create_test_script():
    """Create a simple test script"""
    test_script = """#!/usr/bin/env python3
'''
Test script for optimized Evil Assistant components
'''

import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def test_components():
    print("🔥 Testing Evil Assistant Components")
    
    # Test 1: Audio stream
    try:
        from evilassistant.audio_stream import StreamingAudioProcessor, AudioConfig
        config = AudioConfig()
        processor = StreamingAudioProcessor(config)
        print("✅ Audio streaming: OK")
    except Exception as e:
        print(f"❌ Audio streaming: {e}")
    
    # Test 2: Wake word detection
    try:
        from evilassistant.wake_word import WakeWordDetector, WakeWordConfig
        config = WakeWordConfig()
        detector = WakeWordDetector(config)
        print("✅ Wake word detection: OK")
    except Exception as e:
        print(f"❌ Wake word detection: {e}")
    
    # Test 3: Speech recognition
    try:
        from evilassistant.speech_recognition import HybridSTT, STTConfig
        config = STTConfig()
        stt = HybridSTT(config)
        print("✅ Speech recognition: OK")
    except Exception as e:
        print(f"❌ Speech recognition: {e}")
    
    # Test 4: Audio effects
    try:
        from evilassistant.audio_effects import RealtimeEffectsProcessor, create_demonic_voice_config
        config = create_demonic_voice_config()
        processor = RealtimeEffectsProcessor(config)
        print("✅ Audio effects: OK")
    except Exception as e:
        print(f"❌ Audio effects: {e}")
    
    # Test 5: Async assistant
    try:
        from evilassistant.async_assistant import AsyncEvilAssistant, AssistantConfig
        config = AssistantConfig()
        assistant = AsyncEvilAssistant(config)
        print("✅ Async assistant: OK")
    except Exception as e:
        print(f"❌ Async assistant: {e}")
    
    print("🎉 Component testing complete!")

if __name__ == "__main__":
    asyncio.run(test_components())
"""
    
    with open("test_components.py", "w") as f:
        f.write(test_script)
    
    os.chmod("test_components.py", 0o755)
    logger.info("✅ Created test_components.py")


def main():
    """Main setup function"""
    logger.info("🔥 Evil Assistant Optimization Setup")
    logger.info("=" * 50)
    
    if not check_python_version():
        return
    
    # Step 1: System dependencies
    install_system_dependencies()
    
    # Step 2: Download models
    download_vosk_models()
    
    # Step 3: Setup Ollama (optional)
    setup_choice = input("Setup Ollama for local LLM? (y/n): ").lower()
    if setup_choice == 'y':
        setup_ollama()
    
    # Step 4: Create config files
    create_env_template()
    create_test_script()
    
    logger.info("🎉 Setup complete!")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Fill in your API keys in .env file")
    logger.info("2. Install Python dependencies: pip install -e .")
    logger.info("3. Test components: python test_components.py")
    logger.info("4. Run optimized assistant: python -m evilassistant.async_assistant")
    

if __name__ == "__main__":
    main()
"""
