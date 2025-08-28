#!/usr/bin/env python3
"""
Smart Home Setup for Evil Assistant
Auto-discovers and configures your smart home devices
"""

import os
import sys
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def install_dependencies():
    """Install required smart home libraries"""
    import subprocess
    
    dependencies = [
        "phue",           # Philips Hue
        "pychromecast",   # Google Home/Chromecast
        "aiohttp",        # Async HTTP for Home Assistant
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            logger.info(f"✅ {dep} already installed")
        except ImportError:
            logger.info(f"📥 Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)


def setup_hue():
    """Setup Philips Hue integration"""
    logger.info("🔍 Setting up Philips Hue...")
    
    try:
        from phue import Bridge
        import requests
        
        # Discover bridges
        logger.info("Discovering Hue bridges...")
        response = requests.get('https://discovery.meethue.com/', timeout=10)
        bridges = response.json()
        
        if not bridges:
            logger.warning("❌ No Hue bridges found on network")
            # Try manual IP entry
            manual_ip = input("Enter your Hue bridge IP manually (or press Enter to skip): ")
            if not manual_ip:
                return False
            bridges = [{"internalipaddress": manual_ip}]
        
        bridge_ip = bridges[0]["internalipaddress"]
        logger.info(f"Found bridge at: {bridge_ip}")
        
        # Test connection
        print("\n🔵 IMPORTANT: Press the button on your Hue bridge NOW!")
        print("You have 30 seconds after pressing the button...")
        input("Press Enter when you've pressed the bridge button...")
        
        bridge = Bridge(bridge_ip)
        bridge.connect()
        
        logger.info("✅ Hue bridge connected!")
        lights = [light.name for light in bridge.lights]
        logger.info(f"Available lights: {lights}")
        
        # Update .env file
        update_env_file("PHILIPS_HUE_BRIDGE_IP", bridge_ip)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Hue setup failed: {e}")
        return False


def setup_google_home():
    """Setup Google Home integration"""
    logger.info("🔍 Setting up Google Home...")
    
    try:
        import pychromecast
        import time
        
        logger.info("Discovering Google devices (this may take 10-15 seconds)...")
        chromecasts, browser = pychromecast.get_chromecasts(timeout=15)
        
        if not chromecasts:
            logger.warning("❌ No Google devices found")
            return False
        
        device_names = []
        logger.info("Found devices:")
        for cast in chromecasts:
            name = cast.device.friendly_name
            model = cast.device.model_name
            logger.info(f"- {name} ({model})")
            device_names.append(name)
        
        # Clean up discovery
        browser.stop_discovery()
        
        # Save to config
        devices_str = str(device_names).replace("'", '"')
        update_env_file("GOOGLE_HOME_DEVICES", devices_str)
        
        logger.info("✅ Google Home setup complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Google Home setup failed: {e}")
        return False


def setup_home_assistant():
    """Setup Home Assistant integration"""
    logger.info("🔍 Setting up Home Assistant...")
    
    print("\nHome Assistant Setup:")
    print("1. Go to your Home Assistant web interface")
    print("2. Click on your profile (bottom left)")
    print("3. Scroll down to 'Long-lived access tokens'")
    print("4. Click 'Create Token' and copy the token")
    print()
    
    ha_url = input("Enter Home Assistant URL (e.g., http://homeassistant.local:8123): ").strip()
    if not ha_url:
        logger.info("Skipping Home Assistant setup")
        return False
    
    # Ensure URL has protocol
    if not ha_url.startswith(('http://', 'https://')):
        ha_url = 'http://' + ha_url
    
    ha_token = input("Enter your long-lived access token: ").strip()
    if not ha_token:
        logger.warning("❌ Token required for Home Assistant")
        return False
    
    # Test connection
    try:
        import aiohttp
        
        async def test_connection():
            headers = {
                "Authorization": f"Bearer {ha_token}",
                "Content-Type": "application/json"
            }
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{ha_url}/api/", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("✅ Home Assistant connection successful!")
                        logger.info(f"HA Version: {data.get('version', 'Unknown')}")
                        
                        # Get some entities to show it's working
                        async with session.get(f"{ha_url}/api/states", headers=headers) as entities_response:
                            if entities_response.status == 200:
                                entities = await entities_response.json()
                                light_entities = [e for e in entities if e['entity_id'].startswith('light.')]
                                logger.info(f"Found {len(light_entities)} light entities")
                        
                        return True
                    else:
                        logger.error(f"❌ Connection failed: HTTP {response.status}")
                        return False
        
        success = asyncio.run(test_connection())
        if success:
            update_env_file("HOME_ASSISTANT_URL", ha_url)
            update_env_file("HOME_ASSISTANT_TOKEN", ha_token)
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"❌ Home Assistant setup failed: {e}")
        return False


def update_env_file(key, value):
    """Update or add a key-value pair in .env file"""
    env_path = ".env"
    
    # Read existing .env
    env_lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_lines = f.readlines()
    
    # Update or add the key
    key_found = False
    for i, line in enumerate(env_lines):
        if line.startswith(f"{key}="):
            env_lines[i] = f"{key}={value}\n"
            key_found = True
            break
    
    if not key_found:
        env_lines.append(f"{key}={value}\n")
    
    # Write back to .env
    with open(env_path, 'w') as f:
        f.writelines(env_lines)
    
    logger.info(f"Updated .env: {key}={value}")


def test_smart_home_integration():
    """Test the smart home integration"""
    logger.info("🧪 Testing smart home integration...")
    
    try:
        from evilassistant.smart_home import SmartHomeController
        
        # Load config from .env
        config = {}
        if os.path.exists(".env"):
            with open(".env", 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value
        
        async def test():
            controller = SmartHomeController(config)
            await controller.initialize()
            
            # Test command parsing
            test_commands = [
                "turn on the living room lights",
                "make all lights red",
                "dim the bedroom lights",
                "turn off everything"
            ]
            
            logger.info("Testing command parsing:")
            for cmd in test_commands:
                command = controller.parse_command(cmd)
                if command:
                    logger.info(f"✅ '{cmd}' -> {command.action} {command.target}")
                else:
                    logger.warning(f"❌ '{cmd}' -> Not recognized")
        
        asyncio.run(test())
        logger.info("✅ Smart home integration test complete!")
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")


def main():
    """Main setup function"""
    print("🏠 Evil Assistant Smart Home Setup")
    print("=" * 50)
    
    # Install dependencies first
    logger.info("Installing dependencies...")
    install_dependencies()
    
    # Create .env if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("# Evil Assistant Smart Home Configuration\n")
        logger.info("Created .env file")
    
    # Setup platforms
    platforms = {
        "1": ("Philips Hue", setup_hue),
        "2": ("Google Home/Chromecast", setup_google_home),
        "3": ("Home Assistant", setup_home_assistant)
    }
    
    print("\nWhich smart home platforms do you want to setup?")
    for key, (name, _) in platforms.items():
        print(f"{key}. {name}")
    print("a. All platforms")
    print("s. Skip setup")
    
    choice = input("\nEnter your choice (1,2,3,a,s): ").strip().lower()
    
    if choice == 's':
        logger.info("Skipping smart home setup")
        return
    
    if choice == 'a':
        choices = ['1', '2', '3']
    else:
        choices = [c.strip() for c in choice.split(',')]
    
    success_count = 0
    for choice_num in choices:
        if choice_num in platforms:
            name, setup_func = platforms[choice_num]
            print(f"\n--- Setting up {name} ---")
            if setup_func():
                success_count += 1
    
    print(f"\n🎉 Setup complete! Successfully configured {success_count} platform(s)")
    
    if success_count > 0:
        print("\nYour .env file has been updated with smart home configuration.")
        
        # Test integration
        test_choice = input("\nWould you like to test the integration? (y/n): ").lower()
        if test_choice == 'y':
            test_smart_home_integration()
        
        print("\n🔥 Smart home integration ready!")
        print("\nTo use with your assistant:")
        print("1. Run: evilassistant --optimized")
        print("2. Say: 'Evil assistant, turn on the lights!'")
        print("3. Enjoy your demonic smart home control! 👹")
    else:
        print("\nNo platforms were successfully configured.")
        print("Check the error messages above and try again.")


if __name__ == "__main__":
    main()
