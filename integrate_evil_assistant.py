#!/usr/bin/env python3
"""
Evil Assistant <-> Home Assistant Integration Setup
Run this after Home Assistant initial setup is complete
"""

import os
import requests
import json

def main():
    print("🔥 Evil Assistant <-> Home Assistant Integration Setup")
    print("=" * 60)
    
    # Check if HA is running
    try:
        response = requests.get("http://localhost:8123", timeout=5)
        print("✅ Home Assistant is running")
    except:
        print("❌ Home Assistant not accessible at http://localhost:8123")
        print("Make sure Home Assistant is running and setup is complete")
        return
    
    print("\n📋 Integration Steps:")
    print("1. Open Home Assistant: http://192.168.0.50:8123")
    print("2. Complete initial setup if not done")
    print("3. Go to Profile → Long-lived access tokens")
    print("4. Create token named 'Evil Assistant'")
    print("5. Copy the token and paste it here")
    print()
    
    token = input("🔑 Paste your Home Assistant token: ").strip()
    
    if not token:
        print("❌ No token provided")
        return
    
    # Test the token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("http://localhost:8123/api/states", headers=headers)
        if response.status_code == 200:
            entities = response.json()
            print(f"✅ Token works! Found {len(entities)} entities")
            
            # Show some entities
            lights = [e for e in entities if e['entity_id'].startswith('light.')]
            switches = [e for e in entities if e['entity_id'].startswith('switch.')]
            sensors = [e for e in entities if e['entity_id'].startswith('sensor.')]
            
            print(f"💡 Lights: {len(lights)}")
            print(f"🔌 Switches: {len(switches)}")
            print(f"📊 Sensors: {len(sensors)}")
            
            # Show first few lights if any
            if lights:
                print("\n🔍 Found these lights:")
                for light in lights[:5]:  # Show first 5
                    name = light['attributes'].get('friendly_name', light['entity_id'])
                    state = light['state']
                    print(f"   - {name}: {state}")
                if len(lights) > 5:
                    print(f"   ... and {len(lights) - 5} more")
            
        else:
            print(f"❌ Token test failed: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return
    
    # Update .env file
    env_file = ".env"
    env_lines = []
    
    # Read existing .env
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    # Remove existing HA entries
    env_lines = [line for line in env_lines if not line.startswith(('HOME_ASSISTANT_URL=', 'HOME_ASSISTANT_TOKEN='))]
    
    # Add new HA configuration
    env_lines.append(f"\n# Home Assistant Integration\n")
    env_lines.append(f"HOME_ASSISTANT_URL=http://localhost:8123\n")
    env_lines.append(f"HOME_ASSISTANT_TOKEN={token}\n")
    
    # Write updated .env
    with open(env_file, 'w') as f:
        f.writelines(env_lines)
    
    print(f"✅ Configuration saved to {env_file}")
    
    print("\n🎯 Integration Complete!")
    print("=" * 30)
    print("Your Evil Assistant can now control:")
    print("• All Home Assistant discovered devices")
    print("• Lights, switches, sensors, and more")
    print("• Custom automations and scenes")
    print()
    print("🗣️  Try these commands:")
    print("• 'Evil assistant, turn on all lights'")
    print("• 'Dark one, what's the temperature?'")
    print("• 'Cthulhu, turn off all switches'")
    print("• 'Evil assistant, what devices do you control?'")
    print()
    print("🔧 Start Evil Assistant:")
    print("   source .venv/bin/activate")
    print("   python -m evilassistant")
    print()
    print("🏠 Manage Home Assistant:")
    print("   Start: ./ha_manager.sh start")
    print("   Stop: ./ha_manager.sh stop")
    print("   Logs: ./ha_manager.sh logs")

if __name__ == "__main__":
    main()
