#!/usr/bin/env python3
"""
Evil Assistant - Smart Home Device Discovery
Scans network for controllable devices and protocols
"""

import socket
import threading
import json
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
import subprocess
import re
from typing import List, Dict, Any

class EvilDeviceDiscovery:
    """Discover smart home devices on the local network"""
    
    def __init__(self):
        self.discovered_devices = []
        self.local_ip = self.get_local_ip()
        self.network_base = ".".join(self.local_ip.split(".")[:-1]) + "."
        
    def get_local_ip(self) -> str:
        """Get the local IP address"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "192.168.1.100"  # fallback
    
    def scan_port(self, ip: str, port: int, timeout: float = 0.5) -> bool:
        """Check if a port is open on an IP"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                return result == 0
        except:
            return False
    
    def discover_philips_hue(self) -> List[Dict]:
        """Discover Philips Hue bridges"""
        devices = []
        
        # Method 1: Official discovery service
        try:
            response = requests.get("https://discovery.meethue.com/", timeout=5)
            hue_bridges = response.json()
            for bridge in hue_bridges:
                devices.append({
                    "type": "philips_hue_bridge",
                    "name": "Philips Hue Bridge",
                    "ip": bridge["internalipaddress"],
                    "id": bridge["id"],
                    "protocol": "HTTP REST API",
                    "controllable": "✅ Direct API",
                    "integration": "Already supported!"
                })
        except:
            pass
            
        # Method 2: Local network scan for port 80 (Hue bridges)
        print("🔍 Scanning for Hue bridges on local network...")
        for i in range(1, 255):
            ip = f"{self.network_base}{i}"
            if self.scan_port(ip, 80):
                try:
                    # Check if it's a Hue bridge
                    response = requests.get(f"http://{ip}/api/config", timeout=2)
                    if "bridgeid" in response.text.lower():
                        devices.append({
                            "type": "philips_hue_bridge",
                            "name": "Philips Hue Bridge (Local)",
                            "ip": ip,
                            "protocol": "HTTP REST API",
                            "controllable": "✅ Direct API",
                            "integration": "Already supported!"
                        })
                except:
                    pass
                    
        return devices
    
    def discover_tplink_kasa(self) -> List[Dict]:
        """Discover TP-Link Kasa devices"""
        devices = []
        print("🔍 Scanning for TP-Link Kasa devices...")
        
        # Kasa devices use port 9999
        for i in range(1, 255):
            ip = f"{self.network_base}{i}"
            if self.scan_port(ip, 9999):
                devices.append({
                    "type": "tplink_kasa",
                    "name": "TP-Link Kasa Device",
                    "ip": ip,
                    "protocol": "TCP Socket (Port 9999)",
                    "controllable": "✅ python-kasa library",
                    "integration": "🔄 Can be added to Evil Assistant"
                })
                
        return devices
    
    def discover_lifx(self) -> List[Dict]:
        """Discover LIFX bulbs"""
        devices = []
        print("🔍 Scanning for LIFX devices...")
        
        # LIFX uses port 56700
        for i in range(1, 255):
            ip = f"{self.network_base}{i}"
            if self.scan_port(ip, 56700):
                devices.append({
                    "type": "lifx",
                    "name": "LIFX Smart Bulb",
                    "ip": ip,
                    "protocol": "UDP (Port 56700)",
                    "controllable": "✅ lifxlan library",
                    "integration": "🔄 Can be added to Evil Assistant"
                })
                
        return devices
    
    def discover_chromecasts(self) -> List[Dict]:
        """Discover Chromecast/Google Home devices"""
        devices = []
        print("🔍 Scanning for Chromecast/Google devices...")
        
        try:
            import pychromecast
            chromecasts, browser = pychromecast.get_chromecasts(timeout=10)
            
            for cast in chromecasts:
                device_type = "google_home" if "Google" in cast.device.model_name else "chromecast"
                devices.append({
                    "type": device_type,
                    "name": cast.device.friendly_name,
                    "ip": cast.host,
                    "model": cast.device.model_name,
                    "protocol": "Google Cast Protocol",
                    "controllable": "✅ pychromecast library",
                    "integration": "Partially supported, can be enhanced"
                })
                
            browser.stop_discovery()
        except ImportError:
            print("⚠️  pychromecast not installed, skipping Chromecast discovery")
        except Exception as e:
            print(f"⚠️  Chromecast discovery failed: {e}")
            
        return devices
    
    def discover_upnp_devices(self) -> List[Dict]:
        """Discover UPnP devices (many smart devices use this)"""
        devices = []
        print("🔍 Scanning for UPnP devices...")
        
        try:
            import requests
            # Simple UPnP discovery
            upnp_broadcast = '''M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nST: upnp:rootdevice\r\nMX: 3\r\n\r\n'''
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.settimeout(5)
            sock.sendto(upnp_broadcast.encode(), ('239.255.255.250', 1900))
            
            try:
                while True:
                    data, addr = sock.recvfrom(1024)
                    response = data.decode('utf-8')
                    if 'LOCATION:' in response:
                        # Extract device info
                        location_match = re.search(r'LOCATION:\s*(.+)', response)
                        if location_match:
                            location = location_match.group(1).strip()
                            devices.append({
                                "type": "upnp_device",
                                "name": "UPnP Device",
                                "ip": addr[0],
                                "location": location,
                                "protocol": "UPnP/SSDP",
                                "controllable": "🔄 Depends on device type",
                                "integration": "🔄 May be controllable"
                            })
            except socket.timeout:
                pass
            finally:
                sock.close()
                
        except Exception as e:
            print(f"⚠️  UPnP discovery failed: {e}")
            
        return devices
    
    def discover_home_assistant(self) -> List[Dict]:
        """Discover Home Assistant instances"""
        devices = []
        print("🔍 Scanning for Home Assistant instances...")
        
        # Common HA ports
        ha_ports = [8123, 8124]
        
        for i in range(1, 255):
            ip = f"{self.network_base}{i}"
            for port in ha_ports:
                if self.scan_port(ip, port):
                    try:
                        response = requests.get(f"http://{ip}:{port}/", timeout=2)
                        if "Home Assistant" in response.text:
                            devices.append({
                                "type": "home_assistant",
                                "name": "Home Assistant",
                                "ip": ip,
                                "port": port,
                                "url": f"http://{ip}:{port}",
                                "protocol": "HTTP REST API + WebSocket",
                                "controllable": "✅ Full integration possible",
                                "integration": "🔥 RECOMMENDED - Ultimate smart home hub!"
                            })
                    except:
                        pass
                        
        return devices
    
    def run_discovery(self) -> Dict[str, List]:
        """Run comprehensive device discovery"""
        print("🔥 Evil Assistant - Smart Home Device Discovery")
        print("=" * 60)
        print(f"🏠 Scanning network: {self.network_base}0/24")
        print(f"📍 Your IP: {self.local_ip}")
        print()
        
        all_devices = {}
        
        # Run all discovery methods
        discovery_methods = [
            ("Philips Hue", self.discover_philips_hue),
            ("TP-Link Kasa", self.discover_tplink_kasa),
            ("LIFX", self.discover_lifx),
            ("Chromecast/Google", self.discover_chromecasts),
            ("Home Assistant", self.discover_home_assistant),
            ("UPnP Devices", self.discover_upnp_devices),
        ]
        
        for name, method in discovery_methods:
            print(f"\n🔍 Discovering {name} devices...")
            try:
                devices = method()
                if devices:
                    all_devices[name] = devices
                    print(f"✅ Found {len(devices)} {name} devices")
                else:
                    print(f"❌ No {name} devices found")
            except Exception as e:
                print(f"⚠️  {name} discovery failed: {e}")
        
        return all_devices
    
    def print_results(self, devices: Dict[str, List]):
        """Print discovery results in a nice format"""
        print("\n" + "=" * 80)
        print("🎯 DISCOVERY RESULTS")
        print("=" * 80)
        
        total_devices = sum(len(device_list) for device_list in devices.values())
        
        if total_devices == 0:
            print("😈 No devices found, mortal! Your smart home hides from my power!")
            print("\n💡 Try these troubleshooting steps:")
            print("   • Make sure devices are powered on and connected to WiFi")
            print("   • Check that you're on the same network as your devices")
            print("   • Some devices may use different protocols or be hidden")
            print("   • Run with sudo for more complete network scanning")
            return
        
        print(f"📊 Found {total_devices} controllable devices across {len(devices)} categories:")
        print()
        
        for category, device_list in devices.items():
            if device_list:
                print(f"🔥 {category.upper()}:")
                print("-" * 40)
                
                for device in device_list:
                    print(f"   📱 {device['name']}")
                    print(f"      IP: {device['ip']}")
                    print(f"      Protocol: {device['protocol']}")
                    print(f"      Control: {device['controllable']}")
                    print(f"      Status: {device['integration']}")
                    if 'model' in device:
                        print(f"      Model: {device['model']}")
                    if 'url' in device:
                        print(f"      URL: {device['url']}")
                    print()
        
        print("🎯 NEXT STEPS:")
        print("-" * 40)
        
        # Provide specific next steps based on what was found
        for category, device_list in devices.items():
            if device_list:
                if category == "Home Assistant":
                    print("🏠 Home Assistant found! This is your golden ticket:")
                    print("   1. Open the HA web interface")
                    print("   2. Set up long-lived access token")
                    print("   3. Integrate with Evil Assistant for ULTIMATE control")
                    print()
                elif category == "Philips Hue":
                    print("💡 Hue bridges found! Already supported:")
                    print("   1. Add PHILIPS_HUE_BRIDGE_IP to your .env file")
                    print("   2. Test with: 'evil assistant, turn on the lights'")
                    print()
                elif category == "TP-Link Kasa":
                    print("🔌 Kasa devices found! Can be integrated:")
                    print("   1. Install: pip install python-kasa")
                    print("   2. Add Kasa support to Evil Assistant")
                    print()
                elif category == "LIFX":
                    print("💡 LIFX bulbs found! Can be integrated:")
                    print("   1. Install: pip install lifxlan")
                    print("   2. Add LIFX support to Evil Assistant")
                    print()
                elif category == "Chromecast/Google":
                    print("📺 Google devices found! Enhance current support:")
                    print("   1. Already partially working with pychromecast")
                    print("   2. Can add media control commands")
                    print()

def main():
    """Main discovery function"""
    discovery = EvilDeviceDiscovery()
    devices = discovery.run_discovery()
    discovery.print_results(devices)
    
    # Save results to file
    with open("discovered_devices.json", "w") as f:
        json.dump(devices, f, indent=2)
    print(f"\n💾 Results saved to: discovered_devices.json")

if __name__ == "__main__":
    main()
