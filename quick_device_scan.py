#!/usr/bin/env python3
"""
Quick Smart Device Discovery - Fast version
Focused scan for immediate results
"""

import socket
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

class QuickDeviceScanner:
    def __init__(self):
        self.discovered = []
        self.local_ip = self.get_local_ip()
        self.network_base = ".".join(self.local_ip.split(".")[:-1]) + "."
        
    def get_local_ip(self):
        """Get local IP address"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "192.168.1.100"
    
    def check_hue_bridge(self, ip):
        """Quick check if IP is a Hue bridge"""
        try:
            response = requests.get(f"http://{ip}/api/config", timeout=1)
            data = response.json()
            if "bridgeid" in data:
                return {
                    "type": "Philips Hue Bridge",
                    "ip": ip,
                    "name": data.get("name", "Hue Bridge"),
                    "id": data.get("bridgeid", "unknown")
                }
        except:
            pass
        return None
    
    def check_common_ports(self, ip):
        """Check for common smart device ports"""
        devices = []
        common_checks = [
            (80, "web", "Web Interface"),
            (8123, "homeassistant", "Home Assistant"),
            (9999, "kasa", "TP-Link Kasa"),
            (56700, "lifx", "LIFX")
        ]
        
        for port, device_type, name in common_checks:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.5)
                    if sock.connect_ex((ip, port)) == 0:
                        # Special check for Hue on port 80
                        if port == 80:
                            hue_check = self.check_hue_bridge(ip)
                            if hue_check:
                                devices.append(hue_check)
                        # Special check for Home Assistant
                        elif port == 8123:
                            try:
                                resp = requests.get(f"http://{ip}:{port}/", timeout=1)
                                if "Home Assistant" in resp.text:
                                    devices.append({
                                        "type": "Home Assistant",
                                        "ip": ip,
                                        "port": port,
                                        "url": f"http://{ip}:{port}"
                                    })
                            except:
                                pass
                        else:
                            devices.append({
                                "type": name,
                                "ip": ip,
                                "port": port
                            })
            except:
                pass
        return devices
    
    def scan_ip_range(self, start_ip, end_ip):
        """Scan a range of IPs concurrently"""
        devices = []
        
        def scan_single_ip(i):
            ip = f"{self.network_base}{i}"
            return self.check_common_ports(ip)
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(scan_single_ip, i): i for i in range(start_ip, end_ip)}
            
            for future in as_completed(futures, timeout=10):
                try:
                    result = future.result(timeout=1)
                    if result:
                        devices.extend(result)
                        print(f"✅ Found device at {self.network_base}{futures[future]}")
                except:
                    pass
        
        return devices
    
    def discover_chromecasts(self):
        """Quick Chromecast discovery"""
        devices = []
        try:
            import pychromecast
            print("🔍 Scanning for Chromecast/Google devices...")
            chromecasts, browser = pychromecast.get_chromecasts(timeout=5)
            
            for cast in chromecasts:
                devices.append({
                    "type": "Chromecast/Google Home",
                    "name": cast.device.friendly_name,
                    "ip": cast.host,
                    "model": cast.device.model_name
                })
            
            browser.stop_discovery()
            
        except ImportError:
            print("⚠️  pychromecast not installed - skipping Chromecast scan")
        except Exception as e:
            print(f"⚠️  Chromecast scan failed: {e}")
            
        return devices
    
    def discover_hue_official(self):
        """Use official Hue discovery service"""
        devices = []
        try:
            print("🔍 Checking Philips Hue discovery service...")
            response = requests.get("https://discovery.meethue.com/", timeout=5)
            bridges = response.json()
            
            for bridge in bridges:
                devices.append({
                    "type": "Philips Hue Bridge (Official)",
                    "ip": bridge["internalipaddress"],
                    "id": bridge["id"]
                })
                
        except Exception as e:
            print(f"⚠️  Official Hue discovery failed: {e}")
            
        return devices
    
    def run_quick_scan(self):
        """Run a quick, focused scan"""
        print("🔥 Evil Assistant - Quick Device Discovery")
        print("=" * 50)
        print(f"🏠 Network: {self.network_base}0/24")
        print(f"📍 Your IP: {self.local_ip}")
        print()
        
        all_devices = []
        
        # Official Hue discovery (fast)
        hue_devices = self.discover_hue_official()
        if hue_devices:
            all_devices.extend(hue_devices)
            print(f"✅ Found {len(hue_devices)} Hue bridges via official discovery")
        
        # Chromecast discovery
        cast_devices = self.discover_chromecasts()
        if cast_devices:
            all_devices.extend(cast_devices)
            print(f"✅ Found {len(cast_devices)} Chromecast/Google devices")
        
        # Quick network scan (most common IPs first)
        print("🔍 Quick network scan for other devices...")
        
        # Scan common router IP ranges first
        priority_ranges = [
            (1, 20),    # Router, common static IPs
            (100, 150), # Common DHCP range
            (20, 50),   # More static IPs
        ]
        
        for start, end in priority_ranges:
            print(f"   Scanning {self.network_base}{start}-{end}...")
            range_devices = self.scan_ip_range(start, end)
            if range_devices:
                all_devices.extend(range_devices)
                print(f"   ✅ Found {len(range_devices)} devices in this range")
            
            # Stop early if we found some devices and user wants quick results
            if len(all_devices) > 5:
                print("   (Found several devices, stopping early scan for speed)")
                break
        
        return all_devices
    
    def print_results(self, devices):
        """Print results nicely"""
        print("\n" + "=" * 60)
        print("🎯 QUICK SCAN RESULTS")
        print("=" * 60)
        
        if not devices:
            print("😈 No devices found in quick scan, mortal!")
            print("\n💡 Try these options:")
            print("   • Run full discovery: python device_discovery.py")
            print("   • Check devices are on and connected to WiFi")
            print("   • Try manual IP configuration")
            return
        
        print(f"📊 Found {len(devices)} smart devices:")
        print()
        
        # Group by type
        device_types = {}
        for device in devices:
            device_type = device["type"]
            if device_type not in device_types:
                device_types[device_type] = []
            device_types[device_type].append(device)
        
        for device_type, device_list in device_types.items():
            print(f"🔥 {device_type.upper()}:")
            for device in device_list:
                print(f"   📱 {device.get('name', 'Unknown Device')}")
                print(f"      IP: {device['ip']}")
                if 'port' in device:
                    print(f"      Port: {device['port']}")
                if 'url' in device:
                    print(f"      URL: {device['url']}")
                if 'model' in device:
                    print(f"      Model: {device['model']}")
                if 'id' in device:
                    print(f"      ID: {device['id']}")
                print()
        
        # Provide next steps
        print("🎯 NEXT STEPS:")
        print("-" * 30)
        
        if any("Hue" in d["type"] for d in devices):
            print("💡 Philips Hue found!")
            print("   Add to .env: PHILIPS_HUE_BRIDGE_IP=<ip_address>")
            print("   Test: 'evil assistant, turn on the lights'")
            print()
        
        if any("Home Assistant" in d["type"] for d in devices):
            print("🏠 Home Assistant found!")
            print("   1. Open web interface")
            print("   2. Create long-lived access token")
            print("   3. Add to Evil Assistant configuration")
            print()
        
        if any("Chromecast" in d["type"] or "Google" in d["type"] for d in devices):
            print("📺 Google devices found!")
            print("   Already supported via pychromecast")
            print("   Can enhance media control commands")
            print()
        
        if any("Kasa" in d["type"] for d in devices):
            print("🔌 TP-Link Kasa found!")
            print("   Install: pip install python-kasa")
            print("   Can add direct control to Evil Assistant")
            print()

def main():
    scanner = QuickDeviceScanner()
    devices = scanner.run_quick_scan()
    scanner.print_results(devices)
    
    # Save results
    with open("quick_scan_results.json", "w") as f:
        json.dump(devices, f, indent=2)
    print(f"\n💾 Results saved to: quick_scan_results.json")

if __name__ == "__main__":
    main()
