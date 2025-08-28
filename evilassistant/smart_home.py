"""
Smart Home Integration for Evil Assistant
Supports Philips Hue, Google Home, and Home Assistant
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass

try:
    from phue import Bridge
    _PHUE_AVAILABLE = True
except ImportError:
    _PHUE_AVAILABLE = False

try:
    import pychromecast
    _CHROMECAST_AVAILABLE = True
except ImportError:
    _CHROMECAST_AVAILABLE = False


@dataclass
class SmartHomeCommand:
    """Represents a parsed smart home command"""
    action: str  # "turn_on", "turn_off", "dim", "brighten", "color", "scene"
    target: str  # "lights", "living_room", "bedroom", "all"
    value: Optional[Any] = None  # brightness, color, scene name
    room: Optional[str] = None


class SmartHomeController:
    """Unified controller for smart home devices"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize integrations
        self.hue_bridge = None
        self.home_assistant = None
        self.chromecasts = {}
        
        # Command patterns for demonic responses
        self.evil_responses = {
            "lights_on": [
                "Let there be darkness... wait, that's backwards. The lights obey!",
                "I summon the illumination, mortal!",
                "The photons bend to my will!"
            ],
            "lights_off": [
                "Darkness consumes the light, as it should be!",
                "I banish the illumination to the void!",
                "The shadows reclaim their domain!"
            ],
            "dim": [
                "The light grows weak, like your mortal soul!",
                "I drain the luminous energy for my own power!",
                "Dimming to match your intellect, human!"
            ],
            "color_change": [
                "Behold! The spectrum bends to my demonic influence!",
                "I paint your world in the colors of the underworld!",
                "The hues shift as reality warps around me!"
            ],
            "error": [
                "The smart devices resist my dark magic!",
                "These pathetic machines dare defy me!",
                "The network demons are blocking my power!"
            ]
        }
    
    async def initialize(self):
        """Initialize all smart home connections"""
        tasks = []
        
        if self.config.get('PHILIPS_HUE_BRIDGE_IP'):
            tasks.append(self._init_hue())
        
        if self.config.get('HOME_ASSISTANT_URL'):
            tasks.append(self._init_home_assistant())
        
        if self.config.get('GOOGLE_HOME_DEVICES'):
            tasks.append(self._init_chromecasts())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _init_hue(self):
        """Initialize Philips Hue bridge connection"""
        if not _PHUE_AVAILABLE:
            self.logger.warning("phue library not available")
            return
        
        try:
            bridge_ip = self.config['PHILIPS_HUE_BRIDGE_IP']
            self.hue_bridge = Bridge(bridge_ip)
            self.hue_bridge.connect()
            self.logger.info(f"Connected to Hue bridge at {bridge_ip}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Hue bridge: {e}")
    
    async def _init_home_assistant(self):
        """Initialize Home Assistant connection"""
        self.home_assistant = {
            'url': self.config['HOME_ASSISTANT_URL'],
            'token': self.config.get('HOME_ASSISTANT_TOKEN', ''),
            'headers': {
                'Authorization': f"Bearer {self.config.get('HOME_ASSISTANT_TOKEN', '')}",
                'Content-Type': 'application/json'
            }
        }
        
        # Test connection
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.home_assistant['url']}/api/",
                    headers=self.home_assistant['headers']
                ) as response:
                    if response.status == 200:
                        self.logger.info("Connected to Home Assistant")
                    else:
                        self.logger.error(f"Home Assistant connection failed: {response.status}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Home Assistant: {e}")
    
    async def _init_chromecasts(self):
        """Initialize Google Home/Chromecast connections"""
        if not _CHROMECAST_AVAILABLE:
            self.logger.warning("pychromecast library not available")
            return
        
        try:
            chromecasts, browser = pychromecast.get_chromecasts()
            for cast in chromecasts:
                if cast.device.friendly_name in self.config['GOOGLE_HOME_DEVICES']:
                    self.chromecasts[cast.device.friendly_name] = cast
                    self.logger.info(f"Found Chromecast: {cast.device.friendly_name}")
        except Exception as e:
            self.logger.error(f"Failed to discover Chromecasts: {e}")
    
    def parse_command(self, text: str) -> Optional[SmartHomeCommand]:
        """Parse natural language into smart home commands"""
        text = text.lower().strip()
        
        # Action detection
        action = None
        if any(word in text for word in ["turn on", "on", "enable", "activate"]):
            action = "turn_on"
        elif any(word in text for word in ["turn off", "off", "disable", "deactivate"]):
            action = "turn_off"
        elif any(word in text for word in ["dim", "darker", "dimmer"]):
            action = "dim"
        elif any(word in text for word in ["bright", "brighter", "brighten"]):
            action = "brighten"
        elif any(word in text for word in ["color", "colour", "red", "blue", "green", "purple"]):
            action = "color"
        elif any(word in text for word in ["scene", "mood", "ambiance"]):
            action = "scene"
        
        if not action:
            return None
        
        # Target detection
        target = "all"  # default
        room = None
        
        if any(word in text for word in ["living room", "lounge"]):
            target = room = "living_room"
        elif any(word in text for word in ["bedroom", "bed room"]):
            target = room = "bedroom"
        elif any(word in text for word in ["kitchen"]):
            target = room = "kitchen"
        elif any(word in text for word in ["bathroom", "bath"]):
            target = room = "bathroom"
        elif any(word in text for word in ["lights", "lighting"]):
            target = "lights"
        
        # Value extraction
        value = None
        if action == "color":
            colors = {"red": [255, 0, 0], "blue": [0, 0, 255], "green": [0, 255, 0], 
                     "purple": [128, 0, 128], "orange": [255, 165, 0], "pink": [255, 192, 203]}
            for color_name, rgb in colors.items():
                if color_name in text:
                    value = rgb
                    break
        elif action in ["dim", "brighten"]:
            # Extract percentage if mentioned
            import re
            percent_match = re.search(r'(\d+)\s*%', text)
            if percent_match:
                value = int(percent_match.group(1))
        
        return SmartHomeCommand(action=action, target=target, value=value, room=room)
    
    async def execute_command(self, command: SmartHomeCommand) -> str:
        """Execute a smart home command and return demonic response"""
        try:
            success = False
            
            # Try different integrations
            if self.hue_bridge:
                success = await self._execute_hue_command(command)
            
            if not success and self.home_assistant:
                success = await self._execute_ha_command(command)
            
            if success:
                return self._get_evil_response(command.action)
            else:
                return self._get_evil_response("error")
                
        except Exception as e:
            self.logger.error(f"Smart home command failed: {e}")
            return self._get_evil_response("error")
    
    async def _execute_hue_command(self, command: SmartHomeCommand) -> bool:
        """Execute command via Philips Hue"""
        if not self.hue_bridge:
            return False
        
        try:
            lights = self.hue_bridge.lights
            
            if command.room:
                # Filter lights by room (requires Hue room setup)
                target_lights = [light for light in lights if command.room in light.name.lower()]
            else:
                target_lights = lights
            
            for light in target_lights:
                if command.action == "turn_on":
                    light.on = True
                elif command.action == "turn_off":
                    light.on = False
                elif command.action == "dim":
                    light.brightness = max(1, light.brightness - (command.value or 50))
                elif command.action == "brighten":
                    light.brightness = min(254, light.brightness + (command.value or 50))
                elif command.action == "color" and command.value:
                    light.colortemp_k = None  # Allow color mode
                    light.hue = int(command.value[0] * 182)  # Convert to Hue range
                    light.saturation = 254
            
            return True
            
        except Exception as e:
            self.logger.error(f"Hue command failed: {e}")
            return False
    
    async def _execute_ha_command(self, command: SmartHomeCommand) -> bool:
        """Execute command via Home Assistant"""
        if not self.home_assistant:
            return False
        
        try:
            # Map command to Home Assistant service calls
            service_data = {}
            domain = "light"
            service = None
            
            if command.action == "turn_on":
                service = "turn_on"
            elif command.action == "turn_off":
                service = "turn_off"
            elif command.action in ["dim", "brighten"]:
                service = "turn_on"
                # Get current brightness and adjust
                if command.value:
                    service_data["brightness_pct"] = command.value
            elif command.action == "color" and command.value:
                service = "turn_on"
                service_data["rgb_color"] = command.value
            
            if command.room:
                service_data["entity_id"] = f"light.{command.room}"
            else:
                service_data["entity_id"] = "all"
            
            url = f"{self.home_assistant['url']}/api/services/{domain}/{service}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=self.home_assistant['headers'],
                    json=service_data
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.error(f"Home Assistant command failed: {e}")
            return False
    
    def _get_evil_response(self, action: str) -> str:
        """Get a random evil response for the action"""
        import random
        responses = self.evil_responses.get(action, self.evil_responses["error"])
        return random.choice(responses)


# Example usage patterns for voice commands:
COMMAND_EXAMPLES = {
    "turn on living room lights": SmartHomeCommand("turn_on", "lights", room="living_room"),
    "turn off all lights": SmartHomeCommand("turn_off", "all"),
    "dim the bedroom lights": SmartHomeCommand("dim", "lights", room="bedroom"),
    "make the lights red": SmartHomeCommand("color", "lights", value=[255, 0, 0]),
    "brighten the kitchen 50%": SmartHomeCommand("brighten", "lights", value=50, room="kitchen"),
}


async def test_smart_home():
    """Test function for smart home integration"""
    config = {
        'PHILIPS_HUE_BRIDGE_IP': '192.168.1.100',  # Replace with your bridge IP
        'HOME_ASSISTANT_URL': 'http://homeassistant.local:8123',
        'HOME_ASSISTANT_TOKEN': 'your_token_here',
        'GOOGLE_HOME_DEVICES': ['Living Room Speaker', 'Kitchen Display']
    }
    
    controller = SmartHomeController(config)
    await controller.initialize()
    
    # Test command parsing and execution
    test_commands = [
        "turn on the living room lights",
        "make all lights red",
        "dim the bedroom lights",
        "turn off everything"
    ]
    
    for cmd_text in test_commands:
        command = controller.parse_command(cmd_text)
        if command:
            response = await controller.execute_command(command)
            print(f"Command: {cmd_text}")
            print(f"Response: {response}")
            print()


if __name__ == "__main__":
    asyncio.run(test_smart_home())
