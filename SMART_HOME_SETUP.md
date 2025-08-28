# 🏠 Smart Home Integration Guide for Evil Assistant

## Supported Devices

Your Evil Assistant can control:
- **Philips Hue** lights and bridges
- **Google Home** devices and Chromecasts
- **Home Assistant** (any devices connected to HA)

## 📱 Quick Setup for Each Platform

### 1. Philips Hue Setup

#### Step 1: Find Your Hue Bridge IP
```bash
# Auto-discover Hue bridges on your network
python3 -c "
import requests
response = requests.get('https://discovery.meethue.com/')
bridges = response.json()
for bridge in bridges:
    print(f'Hue Bridge found: {bridge[\"internalipaddress\"]}')
"
```

Or check your router's device list for "Philips Hue".

#### Step 2: Get Bridge Access
```python
# Run this script to get authenticated with your bridge
from phue import Bridge

# Replace with your bridge IP
BRIDGE_IP = "192.168.1.100"  # Your actual bridge IP

# This will prompt you to press the bridge button
bridge = Bridge(BRIDGE_IP)
bridge.connect()

print("✅ Connected to Hue bridge!")
print(f"Available lights: {[light.name for light in bridge.lights]}")
```

#### Step 3: Update Your Config
```python
# Add to your .env file:
PHILIPS_HUE_BRIDGE_IP=192.168.1.100  # Your bridge IP
```

### 2. Google Home / Chromecast Setup

#### Step 1: Install Dependencies
```bash
pip install pychromecast
```

#### Step 2: Discover Your Devices
```python
# Run this to find your Google devices
import pychromecast

chromecasts, browser = pychromecast.get_chromecasts()
print("Found Google devices:")
for cast in chromecasts:
    print(f"- {cast.device.friendly_name} ({cast.device.model_name})")
```

#### Step 3: Update Your Config
```python
# Add to your .env file:
GOOGLE_HOME_DEVICES=["Living Room Speaker", "Kitchen Display", "Bedroom Mini"]
```

### 3. Home Assistant Setup

#### Step 1: Get Your HA Details
- **URL**: Usually `http://homeassistant.local:8123` or your Pi's IP
- **Token**: Go to HA → Profile → Long-Lived Access Tokens → Create Token

#### Step 2: Test Connection
```python
import aiohttp
import asyncio

async def test_ha_connection():
    url = "http://homeassistant.local:8123"
    token = "your_long_lived_token_here"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/api/", headers=headers) as response:
            if response.status == 200:
                print("✅ Home Assistant connection successful!")
            else:
                print(f"❌ Connection failed: {response.status}")

# Run the test
asyncio.run(test_ha_connection())
```

#### Step 3: Update Your Config
```python
# Add to your .env file:
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=your_long_lived_token_here
```

## 🗣️ Voice Commands You Can Use

### Philips Hue Commands
```
"Evil assistant, turn on the living room lights"
"Dark one, make all lights red"
"Cthulhu, dim the bedroom lights"
"Evil assistant, turn off everything"
"Make the kitchen lights purple"
"Brighten the lights 50%"
```

### Google Home Commands
```
"Play music in the living room"
"Stop the kitchen speaker"
"Set volume to 50% on bedroom speaker"
```

### Home Assistant Commands
```
"Turn on the coffee maker"
"Set the thermostat to 72 degrees"
"Lock the front door"
"Check if garage door is open"
```

## 🛠️ Complete Setup Script

Create a file called `setup_smart_home.py`:

```python
#!/usr/bin/env python3
"""
Smart Home Setup for Evil Assistant
"""

import os
import sys

def setup_hue():
    """Setup Philips Hue integration"""
    print("🔍 Setting up Philips Hue...")
    
    try:
        from phue import Bridge
        import requests
        
        # Discover bridges
        print("Discovering Hue bridges...")
        response = requests.get('https://discovery.meethue.com/')
        bridges = response.json()
        
        if not bridges:
            print("❌ No Hue bridges found on network")
            return
        
        bridge_ip = bridges[0]["internalipaddress"]
        print(f"Found bridge at: {bridge_ip}")
        
        # Test connection
        print("Press the button on your Hue bridge now...")
        input("Press Enter when ready...")
        
        bridge = Bridge(bridge_ip)
        bridge.connect()
        
        print("✅ Hue bridge connected!")
        print(f"Available lights: {[light.name for light in bridge.lights]}")
        
        # Add to .env
        env_line = f"PHILIPS_HUE_BRIDGE_IP={bridge_ip}\n"
        with open(".env", "a") as f:
            f.write(env_line)
        
    except Exception as e:
        print(f"❌ Hue setup failed: {e}")

def setup_google_home():
    """Setup Google Home integration"""
    print("🔍 Setting up Google Home...")
    
    try:
        import pychromecast
        
        print("Discovering Google devices...")
        chromecasts, browser = pychromecast.get_chromecasts()
        
        if not chromecasts:
            print("❌ No Google devices found")
            return
        
        device_names = []
        print("Found devices:")
        for cast in chromecasts:
            name = cast.device.friendly_name
            print(f"- {name}")
            device_names.append(name)
        
        # Add to .env
        devices_str = '["' + '", "'.join(device_names) + '"]'
        env_line = f"GOOGLE_HOME_DEVICES={devices_str}\n"
        with open(".env", "a") as f:
            f.write(env_line)
        
        print("✅ Google Home setup complete!")
        
    except Exception as e:
        print(f"❌ Google Home setup failed: {e}")

def setup_home_assistant():
    """Setup Home Assistant integration"""
    print("🔍 Setting up Home Assistant...")
    
    ha_url = input("Enter Home Assistant URL (e.g., http://homeassistant.local:8123): ")
    ha_token = input("Enter your long-lived access token: ")
    
    if not ha_url or not ha_token:
        print("❌ URL and token required")
        return
    
    # Test connection
    try:
        import aiohttp
        import asyncio
        
        async def test():
            headers = {
                "Authorization": f"Bearer {ha_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{ha_url}/api/", headers=headers) as response:
                    if response.status == 200:
                        print("✅ Home Assistant connection successful!")
                        
                        # Add to .env
                        with open(".env", "a") as f:
                            f.write(f"HOME_ASSISTANT_URL={ha_url}\n")
                            f.write(f"HOME_ASSISTANT_TOKEN={ha_token}\n")
                        
                        return True
                    else:
                        print(f"❌ Connection failed: {response.status}")
                        return False
        
        asyncio.run(test())
        
    except Exception as e:
        print(f"❌ Home Assistant setup failed: {e}")

def main():
    print("🏠 Evil Assistant Smart Home Setup")
    print("=" * 40)
    
    # Create .env if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("# Smart Home Configuration\n")
    
    # Setup each platform
    platforms = {
        "1": ("Philips Hue", setup_hue),
        "2": ("Google Home", setup_google_home), 
        "3": ("Home Assistant", setup_home_assistant)
    }
    
    print("Which platforms do you want to setup?")
    for key, (name, _) in platforms.items():
        print(f"{key}. {name}")
    
    choices = input("Enter choices (e.g., 1,2,3): ").split(",")
    
    for choice in choices:
        choice = choice.strip()
        if choice in platforms:
            name, setup_func = platforms[choice]
            print(f"\n--- Setting up {name} ---")
            setup_func()
    
    print("\n🎉 Smart home setup complete!")
    print("Your .env file has been updated with the configuration.")

if __name__ == "__main__":
    main()
```

## 🔧 Enable Smart Home in Your Assistant

### Option 1: Update Your Current Config
Edit your `evilassistant/config.py`:

```python
# Add these lines
SMART_HOME_ENABLED = True
PHILIPS_HUE_BRIDGE_IP = os.getenv("PHILIPS_HUE_BRIDGE_IP", "")
HOME_ASSISTANT_URL = os.getenv("HOME_ASSISTANT_URL", "")
HOME_ASSISTANT_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN", "")
GOOGLE_HOME_DEVICES = eval(os.getenv("GOOGLE_HOME_DEVICES", "[]"))
```

### Option 2: Use the Optimized Assistant
The new async assistant has smart home built-in:

```python
# In async_assistant.py, set:
config = AssistantConfig(
    smart_home_enabled=True,  # Enable smart home
    # ... other settings
)
```

## 🧪 Test Your Integration

Create `test_smart_home.py`:

```python
import asyncio
from evilassistant.smart_home import SmartHomeController

async def test_integration():
    config = {
        'PHILIPS_HUE_BRIDGE_IP': 'your_bridge_ip',
        'HOME_ASSISTANT_URL': 'your_ha_url',
        'HOME_ASSISTANT_TOKEN': 'your_token',
        'GOOGLE_HOME_DEVICES': ['Living Room Speaker']
    }
    
    controller = SmartHomeController(config)
    await controller.initialize()
    
    # Test commands
    test_commands = [
        "turn on the living room lights",
        "make all lights red", 
        "dim the bedroom",
        "turn off everything"
    ]
    
    for cmd in test_commands:
        print(f"\nTesting: '{cmd}'")
        command = controller.parse_command(cmd)
        if command:
            response = await controller.execute_command(command)
            print(f"Response: {response}")
        else:
            print("Command not recognized")

if __name__ == "__main__":
    asyncio.run(test_integration())
```

## 🎯 Quick Start Summary

1. **Install dependencies**: `pip install phue pychromecast aiohttp`
2. **Run setup script**: `python setup_smart_home.py`
3. **Test integration**: `python test_smart_home.py`
4. **Enable in assistant**: Set `smart_home_enabled=True`
5. **Try voice commands**: "Evil assistant, turn on the lights!"

Your Evil Assistant will now respond with demonic flair to smart home commands like:

> *"The photons bend to my will, mortal! Your living room lights obey!"*

> *"Darkness consumes the light, as it should be! All lights are banished!"*

> *"Behold! The spectrum bends to my demonic influence! Red light fills your domain!"*

🔥 Your smart home is now under the control of the dark forces! 👹
