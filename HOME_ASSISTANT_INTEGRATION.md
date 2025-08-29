# 🏠 Home Assistant Integration Guide for Evil Assistant

## 🎯 What is Home Assistant?

Home Assistant (HA) is the **ultimate smart home hub** that can control virtually ANY smart device. Think of it as your own personal Google Home replacement that runs locally and gives you complete control.

### **🔥 Why Home Assistant + Evil Assistant = PERFECTION:**

1. **Device Discovery**: HA finds devices Google Home can't even see
2. **Local Control**: Everything runs on your network (no cloud dependencies)
3. **1000+ Integrations**: Support for almost every smart device brand
4. **Custom Automations**: Way more powerful than Google routines
5. **Privacy**: Your data never leaves your network
6. **Evil Assistant Integration**: Perfect API for demonic control! 👹

---

## 🚀 Quick Start Options

### **Option 1: Dedicated Hardware (EASIEST)**
- **Home Assistant Green** ($99) - Plug and play
- **Home Assistant Yellow** ($150) - With Zigbee/Thread radio

### **Option 2: Existing Pi (BUDGET FRIENDLY)**
- Install HA on your current Pi (alongside Evil Assistant)
- Or use a second Pi if you have one

### **Option 3: Docker/Virtual Machine**
- Run on any existing server/computer
- Great for testing

---

## 📋 Installation Guide

### **Method 1: Raspberry Pi Installation (Recommended)**

#### **Step 1: Download Home Assistant OS**
```bash
# Download the latest image for Pi 4
wget https://github.com/home-assistant/operating-system/releases/download/10.5/haos_rpi4-64-10.5.img.xz

# Flash to SD card (use different SD card than your Evil Assistant Pi)
# Use Raspberry Pi Imager or balenaEtcher
```

#### **Step 2: Initial Setup**
1. Insert SD card and boot Pi
2. Wait 10-15 minutes for initial setup
3. Open web browser: `http://homeassistant.local:8123`
4. Follow setup wizard
5. Create admin account

#### **Step 3: Device Discovery**
Home Assistant will automatically start discovering devices on your network!

### **Method 2: Docker Installation (Same Pi)**
```bash
# Install Docker if not already installed
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Run Home Assistant in Docker
sudo docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -e TZ=America/New_York \
  -v /home/pi/homeassistant:/config \
  -p 8123:8123 \
  ghcr.io/home-assistant/home-assistant:stable
```

---

## 🔗 Evil Assistant Integration

### **Step 1: Get Home Assistant API Token**

1. Open Home Assistant web interface
2. Go to your **Profile** (bottom left)
3. Scroll to **Long-lived access tokens**
4. Click **Create Token**
5. Name it "Evil Assistant"
6. Copy the token (save it securely!)

### **Step 2: Configure Evil Assistant**

Add to your `.env` file:
```bash
# Home Assistant Integration
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=your_long_lived_token_here

# Or if using IP address:
HOME_ASSISTANT_URL=http://192.168.1.100:8123
```

### **Step 3: Test Integration**

Create a test script:
```python
# test_ha_integration.py
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_ha_connection():
    url = os.getenv("HOME_ASSISTANT_URL")
    token = os.getenv("HOME_ASSISTANT_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Get all entities
        async with session.get(f"{url}/api/states", headers=headers) as resp:
            if resp.status == 200:
                entities = await resp.json()
                print(f"✅ Connected! Found {len(entities)} entities:")
                
                # Show lights
                lights = [e for e in entities if e['entity_id'].startswith('light.')]
                print(f"💡 Lights: {len(lights)}")
                for light in lights[:5]:  # Show first 5
                    print(f"   - {light['entity_id']}: {light['state']}")
                
                # Show switches  
                switches = [e for e in entities if e['entity_id'].startswith('switch.')]
                print(f"🔌 Switches: {len(switches)}")
                
                # Show sensors
                sensors = [e for e in entities if e['entity_id'].startswith('sensor.')]
                print(f"📊 Sensors: {len(sensors)}")
                
            else:
                print(f"❌ Failed to connect: {resp.status}")

if __name__ == "__main__":
    asyncio.run(test_ha_connection())
```

Run the test:
```bash
python test_ha_integration.py
```

---

## 🎭 Evil Assistant Voice Commands

### **Enhanced Smart Home Commands**

With Home Assistant, your Evil Assistant can control:

#### **Lights (WAY more than just Hue!)**
```
"Evil assistant, turn on all the lights"
"Dark one, make the living room lights purple"  
"Cthulhu, dim the bedroom lights to 20%"
"Set kitchen lights to warm white"
```

#### **Switches & Outlets**
```
"Evil assistant, turn on the coffee maker"
"Dark one, turn off all switches"
"Power on the TV outlet"
```

#### **Climate Control**
```
"Evil assistant, set temperature to 72 degrees"
"Dark one, turn on the fan"
"Make it warmer in here"
```

#### **Sensors & Status**
```
"Evil assistant, what's the temperature?"
"Dark one, are any lights on?"
"What's the humidity level?"
```

#### **Scenes & Automations**
```
"Evil assistant, activate movie mode"
"Dark one, run bedtime routine"
"Set dramatic lighting"
```

---

## 🔧 Advanced Integration

### **Custom Evil Assistant - HA Bridge**

Create an enhanced smart home handler:

```python
# enhanced_smart_home.py
import aiohttp
import asyncio
import os
from typing import Optional, Dict, Any

class EvilHomeAssistant:
    """Enhanced Home Assistant integration for Evil Assistant"""
    
    def __init__(self):
        self.base_url = os.getenv("HOME_ASSISTANT_URL")
        self.token = os.getenv("HOME_ASSISTANT_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Evil responses for different actions
        self.evil_responses = {
            "lights_on": [
                "Let there be light, though it pales before my darkness!",
                "The illumination bends to my will, mortal!",
                "I summon forth the photons to serve me!"
            ],
            "lights_off": [
                "Darkness reclaims its domain, as it should be!",
                "I banish the light to the shadow realm!",
                "The void consumes all illumination!"
            ],
            "switch_on": [
                "The electrical spirits obey my command!",
                "Power flows through my dark influence!",
                "The device awakens at my demonic touch!"
            ],
            "temperature": [
                "The ambient energy reads {value} degrees, insignificant mortal!",
                "Your dwelling maintains {value} degrees by my dark grace!",
                "The thermal sensors reveal {value} degrees to my all-seeing eye!"
            ]
        }
    
    async def call_service(self, domain: str, service: str, entity_id: str, **kwargs) -> bool:
        """Call a Home Assistant service"""
        data = {
            "entity_id": entity_id,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/services/{domain}/{service}"
            async with session.post(url, headers=self.headers, json=data) as resp:
                return resp.status < 400
    
    async def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of an entity"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/states/{entity_id}"
            async with session.get(url, headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
        return None
    
    async def process_command(self, command: str) -> Optional[str]:
        """Process voice command and return evil response"""
        command = command.lower()
        
        # Light controls
        if "light" in command:
            if "on" in command:
                await self.call_service("light", "turn_on", "all")
                return self.evil_responses["lights_on"][0]
            elif "off" in command:
                await self.call_service("light", "turn_off", "all")
                return self.evil_responses["lights_off"][0]
        
        # Temperature queries
        elif "temperature" in command:
            temp_sensors = await self.get_entities_by_domain("sensor")
            for sensor in temp_sensors:
                if "temperature" in sensor["entity_id"]:
                    state = await self.get_state(sensor["entity_id"])
                    if state:
                        temp = state["state"]
                        return self.evil_responses["temperature"][0].format(value=temp)
        
        return None
```

### **Integration with Current Evil Assistant**

Add to your `assistant_clean.py`:

```python
# Add this to your SmartHomeHandler class
from .enhanced_smart_home import EvilHomeAssistant

class SmartHomeHandler:
    def __init__(self, smart_home_controller):
        self.smart_home = smart_home_controller
        self.hue_bridge = None
        
        # Add Home Assistant support
        if os.getenv("HOME_ASSISTANT_URL"):
            self.ha = EvilHomeAssistant()
            print("✅ Home Assistant integration enabled")
        else:
            self.ha = None
```

---

## 🎯 Benefits You'll Get

### **Immediate Benefits:**
- **10x more devices** than Google Home can control
- **Local control** - works even without internet
- **Custom automations** - way more powerful than Google routines
- **Privacy** - your data stays local
- **Integration** - perfect API for Evil Assistant

### **Advanced Benefits:**
- **Zigbee/Z-Wave support** (with USB dongle)
- **Matter/Thread support** (cutting edge protocols)
- **Custom dashboards** - beautiful web interface
- **Mobile app** - control from anywhere
- **Add-ons** - extend functionality infinitely

### **Evil Assistant Benefits:**
- **More demonic responses** - control ANY device type
- **Better discovery** - find hidden devices
- **Faster responses** - local network speed
- **Unlimited expansion** - add any device type

---

## 🚀 Quick Start Command

Want to test device discovery first? Run this:

```bash
python device_discovery.py
```

This will scan your network and tell you exactly what devices you have and how to control them!

**Ready to set up Home Assistant and become the master of your smart home domain?** 👹🏠
