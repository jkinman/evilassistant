"""
Simple smart home integration for the original Evil Assistant
Lightweight version that can be easily added to your existing assistant.py
"""

import os
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


def is_smart_home_command(text: str) -> bool:
    """Check if the text contains smart home commands"""
    smart_home_keywords = [
        "turn on", "turn off", "dim", "brighten", "lights", "light",
        "red", "blue", "green", "purple", "orange", "color", "colour",
        "living room", "bedroom", "kitchen", "bathroom"
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in smart_home_keywords)


def parse_simple_command(text: str) -> dict:
    """Parse basic smart home commands"""
    text = text.lower().strip()
    
    command = {
        "action": None,
        "target": "all",
        "color": None,
        "room": None
    }
    
    # Detect action
    if any(phrase in text for phrase in ["turn on", "on", "activate"]):
        command["action"] = "turn_on"
    elif any(phrase in text for phrase in ["turn off", "off", "deactivate"]):
        command["action"] = "turn_off"
    elif any(phrase in text for phrase in ["dim", "darker"]):
        command["action"] = "dim"
    elif any(phrase in text for phrase in ["bright", "brighter"]):
        command["action"] = "brighten"
    
    # Detect color
    colors = {
        "red": [255, 0, 0],
        "blue": [0, 0, 255], 
        "green": [0, 255, 0],
        "purple": [128, 0, 128],
        "orange": [255, 165, 0],
        "pink": [255, 192, 203],
        "yellow": [255, 255, 0],
        "white": [255, 255, 255]
    }
    
    for color_name in colors:
        if color_name in text:
            command["action"] = "color"
            command["color"] = colors[color_name]
            break
    
    # Detect room
    if "living room" in text:
        command["room"] = "living_room"
    elif "bedroom" in text:
        command["room"] = "bedroom"
    elif "kitchen" in text:
        command["room"] = "kitchen"
    elif "bathroom" in text:
        command["room"] = "bathroom"
    
    return command


def execute_hue_command(command: dict) -> str:
    """Execute Philips Hue command"""
    try:
        from phue import Bridge
        
        bridge_ip = os.getenv("PHILIPS_HUE_BRIDGE_IP")
        if not bridge_ip:
            return "The Hue bridge remains hidden from my dark sight, mortal!"
        
        bridge = Bridge(bridge_ip)
        bridge.connect()
        
        # Get lights
        if command["room"]:
            # Filter by room (this is simplified - real implementation would need room mapping)
            lights = [light for light in bridge.lights if command["room"].replace("_", " ") in light.name.lower()]
            if not lights:
                lights = bridge.lights  # Fallback to all lights
        else:
            lights = bridge.lights
        
        # Execute command
        if command["action"] == "turn_on":
            for light in lights:
                light.on = True
            return "Let there be light! The illumination obeys my command!"
        
        elif command["action"] == "turn_off":
            for light in lights:
                light.on = False
            return "Darkness consumes the light, as it should be!"
        
        elif command["action"] == "dim":
            for light in lights:
                light.brightness = max(1, light.brightness - 100)
            return "The light grows weak, like your mortal soul!"
        
        elif command["action"] == "brighten":
            for light in lights:
                light.brightness = min(254, light.brightness + 100)
            return "Blinding brilliance at my command, foolish human!"
        
        elif command["action"] == "color" and command["color"]:
            for light in lights:
                try:
                    # Convert RGB to Hue color space (simplified)
                    light.colortemp = None  # Disable color temperature mode
                    light.hue = int(command["color"][0] * 182)  # Scale to Hue range
                    light.saturation = 254
                    light.on = True  # Make sure light is on for color
                except Exception as e:
                    # If color not supported, just turn on the light
                    light.on = True
            
            color_name = next((name for name, rgb in {
                "red": [255, 0, 0], "blue": [0, 0, 255], "green": [0, 255, 0],
                "purple": [128, 0, 128], "orange": [255, 165, 0]
            }.items() if rgb == command["color"]), "unknown")
            
            return f"Behold! The spectrum bends to my will! {color_name.title()} light fills your domain!"
        
        return "The lights acknowledge my presence, mortal."
        
    except ImportError:
        return "The Hue libraries are not installed. Install with: pip install phue"
    except Exception as e:
        logger.error(f"Hue command failed: {e}")
        return "The smart devices resist my dark magic!"


def execute_home_assistant_command(command: dict) -> str:
    """Execute Home Assistant command (simplified)"""
    try:
        import requests
        
        ha_url = os.getenv("HOME_ASSISTANT_URL")
        ha_token = os.getenv("HOME_ASSISTANT_TOKEN")
        
        if not ha_url or not ha_token:
            return "Home Assistant remains beyond my reach, mortal!"
        
        headers = {
            "Authorization": f"Bearer {ha_token}",
            "Content-Type": "application/json"
        }
        
        # Simple light control
        if command["action"] in ["turn_on", "turn_off"]:
            service = command["action"]
            domain = "light"
            
            service_data = {}
            if command["room"]:
                service_data["entity_id"] = f"light.{command['room']}"
            
            if command["color"] and command["action"] == "turn_on":
                service_data["rgb_color"] = command["color"]
            
            url = f"{ha_url}/api/services/{domain}/{service}"
            response = requests.post(url, headers=headers, json=service_data, timeout=5)
            
            if response.status_code == 200:
                if command["action"] == "turn_on":
                    return "The Home Assistant spirits obey my commands!"
                else:
                    return "Darkness falls as I command the automated realm!"
            else:
                return "The Home Assistant defies my power!"
        
        return "Home Assistant acknowledges my presence."
        
    except ImportError:
        return "Install requests library for Home Assistant control: pip install requests"
    except Exception as e:
        logger.error(f"Home Assistant command failed: {e}")
        return "The automation spirits are in chaos!"


def handle_smart_home_command(text: str) -> Optional[str]:
    """Main function to handle smart home commands
    
    Returns a demonic response if a smart home command was executed,
    or None if this wasn't a smart home command.
    """
    
    if not is_smart_home_command(text):
        return None
    
    command = parse_simple_command(text)
    
    if not command["action"]:
        return "I sense your intent to control the smart realm, but your words are unclear, mortal!"
    
    logger.info(f"Smart home command: {command}")
    
    # Try Philips Hue first
    if os.getenv("PHILIPS_HUE_BRIDGE_IP"):
        response = execute_hue_command(command)
        if "not installed" not in response.lower() and "resist" not in response.lower():
            return response
    
    # Try Home Assistant
    if os.getenv("HOME_ASSISTANT_URL"):
        response = execute_home_assistant_command(command)
        if "beyond my reach" not in response.lower():
            return response
    
    return "No smart home devices are configured for my dark magic, foolish mortal!"


# Example integration into your existing assistant.py:
"""
Add this to your assistant.py in the question processing section:

# After getting full_transcription, before the LLM call:
smart_home_response = handle_smart_home_command(full_transcription)
if smart_home_response:
    print(f"Evil Assistant says: {smart_home_response}")
    output_file = "evil_output.wav"
    speak_text(smart_home_response, output_file, voice)
    os.remove(output_file)
    continue  # Skip LLM processing for smart home commands
"""


def test_smart_home():
    """Test the smart home integration"""
    test_commands = [
        "turn on the living room lights",
        "make all lights red", 
        "turn off the lights",
        "dim the bedroom lights",
        "turn on purple lights in the kitchen"
    ]
    
    print("🏠 Testing Smart Home Integration")
    print("=" * 40)
    
    for cmd in test_commands:
        print(f"\nCommand: '{cmd}'")
        response = handle_smart_home_command(cmd)
        if response:
            print(f"Response: {response}")
        else:
            print("Not a smart home command")


if __name__ == "__main__":
    test_smart_home()
