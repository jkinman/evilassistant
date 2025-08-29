#!/usr/bin/env python3
"""
Evil Assistant <-> Home Assistant Integration
Provides comprehensive Home Assistant control through Evil Assistant
"""

import os
import aiohttp
import asyncio
import json
import logging
from typing import Optional, Dict, List, Any
import random

logger = logging.getLogger(__name__)

class EvilHomeAssistant:
    """Evil Assistant's interface to Home Assistant"""
    
    def __init__(self):
        self.base_url = os.getenv("HOME_ASSISTANT_URL", "http://localhost:8123")
        self.token = os.getenv("HOME_ASSISTANT_TOKEN")
        
        if not self.token:
            logger.warning("HOME_ASSISTANT_TOKEN not set - Home Assistant integration disabled")
            self.enabled = False
            return
            
        self.enabled = True
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Evil responses for different device types and actions
        self.evil_responses = {
            "lights_on": [
                "Let there be light, though it pales before my darkness!",
                "The illumination bends to my will, mortal!",
                "I summon forth the photons to serve me!",
                "The light spirits obey my dark command!"
            ],
            "lights_off": [
                "Darkness reclaims its rightful domain!",
                "I banish the light to the shadow realm!",
                "The void consumes all illumination!",
                "Silence and darkness, as I prefer it!"
            ],
            "lights_dim": [
                "The light grows weak, like your mortal soul!",
                "I drain the luminous energy for my own power!",
                "Dimming to match your intellect, human!"
            ],
            "lights_bright": [
                "The light blazes with my unholy power!",
                "Maximum illumination to reveal all your failures!",
                "Brightness that burns like the fires of damnation!"
            ],
            "lights_color": [
                "Behold! The spectrum bends to my demonic influence!",
                "I paint your world in the colors of the underworld!",
                "The hues shift as reality warps around me!",
                "The lights blaze with {color} fire, mortal!"
            ],
            "switch_on": [
                "The electrical spirits obey my command!",
                "Power flows through my dark influence!",
                "The device awakens at my demonic touch!",
                "I grant power to this pathetic machine!"
            ],
            "switch_off": [
                "I cut the life force from this device!",
                "The electrical spirits abandon their post!",
                "Powerless, like your resistance to my will!"
            ],
            "temperature": [
                "The ambient energy reads {value}°, insignificant mortal!",
                "Your dwelling maintains {value}° by my dark grace!",
                "The thermal sensors reveal {value}° to my all-seeing eye!"
            ],
            "humidity": [
                "The moisture content stands at {value}%, pathetic human!",
                "I sense {value}% humidity in your mortal realm!"
            ],
            "scene_activate": [
                "Behold! The scene '{scene}' manifests by my will!",
                "I summon the ambiance of '{scene}' into existence!",
                "Your environment transforms to '{scene}' at my command!"
            ],
            "automation_trigger": [
                "The automation '{automation}' executes by my decree!",
                "I invoke the ritual of '{automation}', mortal!",
                "The automated sequence '{automation}' begins!"
            ],
            "error": [
                "The smart devices resist my dark magic!",
                "These pathetic machines dare defy me!",
                "The network demons are blocking my power!",
                "Your technology is too feeble for my commands!"
            ],
            "status_query": [
                "Your domain contains {count} devices under my surveillance!",
                "I monitor {count} entities in your pathetic realm!",
                "My dark influence extends over {count} connected devices!"
            ]
        }
    
    def get_evil_response(self, category: str, **kwargs) -> str:
        """Get a random evil response for the given category"""
        if category not in self.evil_responses:
            return "Your request has been... processed, mortal."
        
        responses = self.evil_responses[category]
        response = random.choice(responses)
        
        # Format with any provided kwargs
        try:
            return response.format(**kwargs)
        except:
            return response
    
    async def test_connection(self) -> bool:
        """Test connection to Home Assistant"""
        if not self.enabled:
            return False
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/", headers=self.headers) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.error(f"Home Assistant connection test failed: {e}")
            return False
    
    async def get_states(self) -> List[Dict[str, Any]]:
        """Get all entity states from Home Assistant"""
        if not self.enabled:
            return []
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/states", headers=self.headers) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            logger.error(f"Failed to get states: {e}")
        return []
    
    async def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get state of a specific entity"""
        if not self.enabled:
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/states/{entity_id}", headers=self.headers) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            logger.error(f"Failed to get entity state for {entity_id}: {e}")
        return None
    
    async def call_service(self, domain: str, service: str, entity_id: str = None, **kwargs) -> bool:
        """Call a Home Assistant service"""
        if not self.enabled:
            return False
            
        data = kwargs.copy()
        if entity_id:
            data["entity_id"] = entity_id
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/services/{domain}/{service}"
                async with session.post(url, headers=self.headers, json=data) as resp:
                    success = resp.status < 400
                    if not success:
                        logger.error(f"Service call failed: {resp.status} - {await resp.text()}")
                    return success
        except Exception as e:
            logger.error(f"Service call error: {e}")
            return False
    
    async def process_light_command(self, command: str) -> Optional[str]:
        """Process light-related commands"""
        command_lower = command.lower()
        
        # Get all light entities
        states = await self.get_states()
        lights = [entity for entity in states if entity['entity_id'].startswith('light.')]
        
        if not lights:
            return "No lights found in your domain, mortal!"
        
        # Determine target lights
        target_lights = []
        if any(room in command_lower for room in ['living room', 'bedroom', 'kitchen', 'bathroom']):
            # Room-specific
            for room in ['living_room', 'bedroom', 'kitchen', 'bathroom']:
                if room.replace('_', ' ') in command_lower:
                    target_lights = [light for light in lights if room in light['entity_id']]
                    break
        else:
            # All lights
            target_lights = lights
        
        if not target_lights:
            target_lights = lights  # Fallback to all lights
        
        # Process command
        success_count = 0
        
        if "on" in command_lower or "turn on" in command_lower:
            for light in target_lights:
                success = await self.call_service("light", "turn_on", light['entity_id'])
                if success:
                    success_count += 1
            
            if success_count > 0:
                return self.get_evil_response("lights_on")
                
        elif "off" in command_lower or "turn off" in command_lower:
            for light in target_lights:
                success = await self.call_service("light", "turn_off", light['entity_id'])
                if success:
                    success_count += 1
            
            if success_count > 0:
                return self.get_evil_response("lights_off")
        
        elif any(word in command_lower for word in ["dim", "dimmer", "darker"]):
            for light in target_lights:
                success = await self.call_service("light", "turn_on", light['entity_id'], brightness=80)
                if success:
                    success_count += 1
            
            if success_count > 0:
                return self.get_evil_response("lights_dim")
        
        elif any(word in command_lower for word in ["bright", "brighter", "brighten"]):
            for light in target_lights:
                success = await self.call_service("light", "turn_on", light['entity_id'], brightness=255)
                if success:
                    success_count += 1
            
            if success_count > 0:
                return self.get_evil_response("lights_bright")
        
        elif any(color in command_lower for color in ["red", "blue", "green", "purple", "yellow", "orange", "pink", "white"]):
            # Color mapping (HS values)
            colors = {
                "red": {"hs_color": [0, 100]},
                "blue": {"hs_color": [240, 100]},
                "green": {"hs_color": [120, 100]},
                "purple": {"hs_color": [270, 100]},
                "yellow": {"hs_color": [60, 100]},
                "orange": {"hs_color": [30, 100]},
                "pink": {"hs_color": [300, 100]},
                "white": {"hs_color": [0, 0]}
            }
            
            for color_name, color_data in colors.items():
                if color_name in command_lower:
                    for light in target_lights:
                        success = await self.call_service("light", "turn_on", light['entity_id'], **color_data)
                        if success:
                            success_count += 1
                    
                    if success_count > 0:
                        return self.get_evil_response("lights_color", color=color_name)
                    break
        
        if success_count == 0:
            return self.get_evil_response("error")
        
        return None
    
    async def process_switch_command(self, command: str) -> Optional[str]:
        """Process switch-related commands"""
        command_lower = command.lower()
        
        # Get all switch entities
        states = await self.get_states()
        switches = [entity for entity in states if entity['entity_id'].startswith('switch.')]
        
        if not switches:
            return "No switches found in your pathetic realm!"
        
        success_count = 0
        
        if "on" in command_lower or "turn on" in command_lower:
            for switch in switches:
                success = await self.call_service("switch", "turn_on", switch['entity_id'])
                if success:
                    success_count += 1
            
            if success_count > 0:
                return self.get_evil_response("switch_on")
                
        elif "off" in command_lower or "turn off" in command_lower:
            for switch in switches:
                success = await self.call_service("switch", "turn_off", switch['entity_id'])
                if success:
                    success_count += 1
            
            if success_count > 0:
                return self.get_evil_response("switch_off")
        
        if success_count == 0:
            return self.get_evil_response("error")
            
        return None
    
    async def process_sensor_query(self, command: str) -> Optional[str]:
        """Process sensor queries (temperature, humidity, etc.)"""
        command_lower = command.lower()
        
        states = await self.get_states()
        sensors = [entity for entity in states if entity['entity_id'].startswith('sensor.')]
        
        if "temperature" in command_lower:
            temp_sensors = [s for s in sensors if "temperature" in s['entity_id'] and s['state'] not in ['unknown', 'unavailable']]
            if temp_sensors:
                # Get the first available temperature
                temp = temp_sensors[0]['state']
                unit = temp_sensors[0]['attributes'].get('unit_of_measurement', '°')
                return self.get_evil_response("temperature", value=f"{temp}{unit}")
        
        elif "humidity" in command_lower:
            humidity_sensors = [s for s in sensors if "humidity" in s['entity_id'] and s['state'] not in ['unknown', 'unavailable']]
            if humidity_sensors:
                humidity = humidity_sensors[0]['state']
                unit = humidity_sensors[0]['attributes'].get('unit_of_measurement', '%')
                return self.get_evil_response("humidity", value=f"{humidity}{unit}")
        
        return None
    
    async def process_scene_command(self, command: str) -> Optional[str]:
        """Process scene activation commands"""
        command_lower = command.lower()
        
        if not any(word in command_lower for word in ["scene", "mood", "ambiance", "atmosphere"]):
            return None
        
        states = await self.get_states()
        scenes = [entity for entity in states if entity['entity_id'].startswith('scene.')]
        
        # Try to match scene names
        for scene in scenes:
            scene_name = scene['attributes'].get('friendly_name', scene['entity_id'].replace('scene.', ''))
            if any(word in command_lower for word in scene_name.lower().split()):
                success = await self.call_service("scene", "turn_on", scene['entity_id'])
                if success:
                    return self.get_evil_response("scene_activate", scene=scene_name)
        
        return None
    
    async def get_status_summary(self) -> str:
        """Get a summary of the Home Assistant status"""
        if not self.enabled:
            return "Home Assistant integration is disabled, mortal!"
        
        states = await self.get_states()
        if not states:
            return "I cannot sense any devices in your realm!"
        
        # Count different entity types
        lights = len([e for e in states if e['entity_id'].startswith('light.')])
        switches = len([e for e in states if e['entity_id'].startswith('switch.')])
        sensors = len([e for e in states if e['entity_id'].startswith('sensor.')])
        
        summary = f"Your domain contains {len(states)} entities: "
        summary += f"{lights} lights, {switches} switches, {sensors} sensors. "
        summary += "All bend to my dark will!"
        
        return summary
    
    async def process_command(self, command: str) -> Optional[str]:
        """Main command processor for Home Assistant integration"""
        if not self.enabled:
            return None
        
        command_lower = command.lower()
        
        # Status queries
        if any(word in command_lower for word in ["status", "summary", "devices", "entities"]):
            return await self.get_status_summary()
        
        # Light commands
        if any(word in command_lower for word in ["light", "lights", "lamp", "brightness", "illumination"]):
            return await self.process_light_command(command)
        
        # Switch commands
        if any(word in command_lower for word in ["switch", "switches", "plug", "outlet", "power"]):
            return await self.process_switch_command(command)
        
        # Sensor queries
        if any(word in command_lower for word in ["temperature", "humidity", "sensor", "reading"]):
            return await self.process_sensor_query(command)
        
        # Scene commands
        if any(word in command_lower for word in ["scene", "mood", "ambiance", "atmosphere"]):
            return await self.process_scene_command(command)
        
        return None

# Singleton instance
_evil_ha = None

def get_evil_home_assistant() -> EvilHomeAssistant:
    """Get the singleton Evil Home Assistant instance"""
    global _evil_ha
    if _evil_ha is None:
        _evil_ha = EvilHomeAssistant()
    return _evil_ha

async def process_home_assistant_command(command: str) -> Optional[str]:
    """Process a command through Home Assistant integration"""
    evil_ha = get_evil_home_assistant()
    return await evil_ha.process_command(command)
