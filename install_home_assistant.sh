#!/bin/bash

# Evil Assistant - Home Assistant Integration Setup
# Installs Home Assistant via Docker alongside Evil Assistant

set -e

echo "🔥 Evil Assistant - Home Assistant Integration Setup"
echo "=================================================="
echo "This will install Home Assistant on your Pi alongside Evil Assistant"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running on Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check available space
print_step "Checking available disk space..."
AVAILABLE_SPACE=$(df / | tail -1 | awk '{print $4}')
REQUIRED_SPACE=2000000  # 2GB in KB

if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
    print_error "Insufficient disk space. Need at least 2GB free."
    echo "Available: $(( AVAILABLE_SPACE / 1024 ))MB"
    echo "Required: $(( REQUIRED_SPACE / 1024 ))MB"
    exit 1
fi

print_success "Sufficient disk space available: $(( AVAILABLE_SPACE / 1024 ))MB"

# Update system
print_step "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Docker if not present
print_step "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_success "Docker installed successfully"
else
    print_success "Docker already installed"
fi

# Install Docker Compose
print_step "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo apt install -y docker-compose
    print_success "Docker Compose installed"
else
    print_success "Docker Compose already installed"
fi

# Create Home Assistant directory
print_step "Creating Home Assistant directory..."
HA_DIR="/home/$USER/homeassistant"
sudo mkdir -p "$HA_DIR"
sudo chown $USER:$USER "$HA_DIR"
print_success "Home Assistant directory created: $HA_DIR"

# Create docker-compose.yml for Home Assistant
print_step "Creating Home Assistant Docker configuration..."
cat > "$HA_DIR/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  homeassistant:
    container_name: homeassistant
    image: ghcr.io/home-assistant/home-assistant:stable
    volumes:
      - ./config:/config
      - /etc/localtime:/etc/localtime:ro
      - /run/dbus:/run/dbus:ro
    restart: unless-stopped
    privileged: true
    network_mode: host
    environment:
      - TZ=America/New_York
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8123"]
      interval: 30s
      timeout: 10s
      retries: 5
EOF

print_success "Docker Compose configuration created"

# Create initial Home Assistant configuration
print_step "Creating initial Home Assistant configuration..."
mkdir -p "$HA_DIR/config"

cat > "$HA_DIR/config/configuration.yaml" << 'EOF'
# Home Assistant Configuration for Evil Assistant Integration

# Configure a default setup of Home Assistant (frontend, api, etc)
default_config:

# Enable the HTTP integration for API access
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 127.0.0.1
    - ::1

# Enable API
api:

# Enable automation UI
automation: !include automations.yaml

# Enable script UI  
script: !include scripts.yaml

# Enable scene UI
scene: !include scenes.yaml

# Text to speech
tts:
  - platform: google_translate

# Evil Assistant Integration
# This allows Evil Assistant to control devices
homeassistant:
  # Customize entity names to be more evil
  customize:
    light.living_room:
      friendly_name: "Mortal's Illumination"
    switch.coffee_maker:
      friendly_name: "Caffeine Summoner"

# Enable discovery to find devices automatically
discovery:

# Enable mobile app support
mobile_app:

# Enable Philips Hue (if detected)
# Will be auto-configured during setup

# Enable TP-Link Kasa integration
# Will be auto-configured during setup

# Evil Assistant webhook for advanced integration
webhook:

# Enable frontend themes
frontend:
  themes: !include_dir_merge_named themes

# Logger configuration
logger:
  default: info
  logs:
    homeassistant.core: debug
EOF

# Create empty automation files
touch "$HA_DIR/config/automations.yaml"
touch "$HA_DIR/config/scripts.yaml"
touch "$HA_DIR/config/scenes.yaml"

print_success "Initial configuration created"

# Start Home Assistant
print_step "Starting Home Assistant..."
cd "$HA_DIR"
docker-compose up -d

print_success "Home Assistant container started"

# Wait for Home Assistant to start
print_step "Waiting for Home Assistant to initialize..."
echo "This may take 2-5 minutes for first startup..."

TIMEOUT=300  # 5 minutes
COUNTER=0
while ! curl -f http://localhost:8123 >/dev/null 2>&1; do
    sleep 10
    COUNTER=$((COUNTER + 10))
    if [ $COUNTER -ge $TIMEOUT ]; then
        print_error "Home Assistant failed to start within 5 minutes"
        echo "Check logs with: docker-compose logs homeassistant"
        exit 1
    fi
    echo "Waiting... ($COUNTER/$TIMEOUT seconds)"
done

print_success "Home Assistant is running!"

# Get Pi IP address
PI_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "🎉 HOME ASSISTANT INSTALLATION COMPLETE!"
echo "========================================"
echo ""
echo "📱 Access Home Assistant:"
echo "   URL: http://$PI_IP:8123"
echo "   Local: http://localhost:8123"
echo ""
echo "🔧 Next Steps:"
echo "1. Open Home Assistant in your browser"
echo "2. Complete the onboarding wizard"
echo "3. Create your admin user"
echo "4. Let HA discover your devices (may take a few minutes)"
echo "5. Create a long-lived access token for Evil Assistant"
echo ""
echo "🔥 Evil Assistant Integration:"
echo "After setup, run: python integrate_evil_assistant.py"
echo ""
echo "📊 Management Commands:"
echo "   Start:   cd $HA_DIR && docker-compose up -d"
echo "   Stop:    cd $HA_DIR && docker-compose down"
echo "   Logs:    cd $HA_DIR && docker-compose logs -f homeassistant"
echo "   Update:  cd $HA_DIR && docker-compose pull && docker-compose up -d"
echo ""

# Create management script
print_step "Creating Home Assistant management script..."
cat > "/home/$USER/ha_manager.sh" << 'EOF'
#!/bin/bash

# Home Assistant Management Script

HA_DIR="/home/$USER/homeassistant"
cd "$HA_DIR"

case "$1" in
    start)
        echo "🚀 Starting Home Assistant..."
        docker-compose up -d
        echo "✅ Home Assistant started"
        ;;
    stop)
        echo "🛑 Stopping Home Assistant..."
        docker-compose down
        echo "✅ Home Assistant stopped"
        ;;
    restart)
        echo "🔄 Restarting Home Assistant..."
        docker-compose restart
        echo "✅ Home Assistant restarted"
        ;;
    logs)
        echo "📋 Home Assistant logs (Ctrl+C to exit):"
        docker-compose logs -f homeassistant
        ;;
    status)
        echo "📊 Home Assistant status:"
        docker-compose ps
        ;;
    update)
        echo "⬆️  Updating Home Assistant..."
        docker-compose pull
        docker-compose up -d
        echo "✅ Home Assistant updated"
        ;;
    backup)
        echo "💾 Creating backup..."
        tar -czf "ha_backup_$(date +%Y%m%d_%H%M%S).tar.gz" config/
        echo "✅ Backup created"
        ;;
    *)
        echo "Home Assistant Manager"
        echo "Usage: $0 {start|stop|restart|logs|status|update|backup}"
        echo ""
        echo "Commands:"
        echo "  start   - Start Home Assistant"
        echo "  stop    - Stop Home Assistant"
        echo "  restart - Restart Home Assistant"
        echo "  logs    - View live logs"
        echo "  status  - Show container status"
        echo "  update  - Update to latest version"
        echo "  backup  - Create configuration backup"
        exit 1
        ;;
esac
EOF

chmod +x "/home/$USER/ha_manager.sh"
print_success "Management script created: /home/$USER/ha_manager.sh"

# Create Evil Assistant integration script
print_step "Creating Evil Assistant integration helper..."
cat > "integrate_evil_assistant.py" << 'EOF'
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
    print("1. Open Home Assistant: http://localhost:8123")
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
    print()
    print("🔧 Manage Home Assistant:")
    print("• Start: ./ha_manager.sh start")
    print("• Stop: ./ha_manager.sh stop")
    print("• Logs: ./ha_manager.sh logs")

if __name__ == "__main__":
    main()
EOF

chmod +x "integrate_evil_assistant.py"
print_success "Integration script created: integrate_evil_assistant.py"

print_warning "IMPORTANT: After Home Assistant completes setup, run:"
print_warning "python integrate_evil_assistant.py"

echo ""
print_success "Setup complete! Home Assistant is installing in the background."
print_warning "Open http://$PI_IP:8123 in your browser to complete setup!"
