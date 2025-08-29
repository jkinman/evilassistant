# Evil Assistant - Systemd Service Setup

## 🎯 **Auto-Start Service for Raspberry Pi**

This setup enables the Evil Assistant to automatically start on boot and restart if it crashes.

## 📁 **Files Created**

1. **`evil-assistant.service`** - Systemd service configuration
2. **`install_service.sh`** - One-command installation script
3. **`service_manager.sh`** - Easy service management commands

## 🚀 **Quick Setup (On Your Pi)**

### **Step 1: Commit and Pull**
```bash
# On your local machine:
git add .
git commit -m "Add systemd service for auto-start"
git push

# On your Pi:
cd ~/evilassistant
git pull
```

### **Step 2: Install the Service**
```bash
# Make scripts executable
chmod +x install_service.sh service_manager.sh

# Install the service
./install_service.sh
```

### **Step 3: Start the Service**
```bash
# Start immediately
sudo systemctl start evil-assistant

# Check if it's working
sudo systemctl status evil-assistant
```

## 🔧 **Service Management**

### **Easy Commands (Using service_manager.sh)**
```bash
./service_manager.sh start      # Start the service
./service_manager.sh stop       # Stop the service
./service_manager.sh restart    # Restart the service
./service_manager.sh status     # Check status
./service_manager.sh logs       # View real-time logs
./service_manager.sh enable     # Enable auto-start
./service_manager.sh disable    # Disable auto-start
```

### **Direct Systemctl Commands**
```bash
# Service control
sudo systemctl start evil-assistant
sudo systemctl stop evil-assistant
sudo systemctl restart evil-assistant
sudo systemctl status evil-assistant

# Auto-start control
sudo systemctl enable evil-assistant   # Auto-start on boot
sudo systemctl disable evil-assistant  # Don't auto-start

# Logs
sudo journalctl -u evil-assistant -f   # Real-time logs
sudo journalctl -u evil-assistant -n 50  # Last 50 lines
```

## 📊 **Service Features**

### **Automatic Restart**
- Restarts if the assistant crashes
- 10-second delay between restart attempts
- Limits restart attempts to prevent boot loops

### **Proper Dependencies**
- Waits for network connection
- Waits for audio system
- Ensures filesystem is ready

### **Resource Limits**
- 2GB memory limit (prevents runaway usage)
- Task limits for stability
- Security restrictions

### **Logging**
- All output goes to systemd journal
- Easy to view with `journalctl`
- Automatic log rotation

## 🧪 **Testing the Service**

### **1. Installation Test**
```bash
# Install and start
./install_service.sh
sudo systemctl start evil-assistant

# Check status
./service_manager.sh status
```

### **2. Auto-Start Test**
```bash
# Reboot and check if it starts automatically
sudo reboot

# After reboot, check status
./service_manager.sh status
```

### **3. Crash Recovery Test**
```bash
# Find the process and kill it
ps aux | grep evilassistant
sudo kill -9 [PID]

# Wait 10 seconds, then check if it restarted
sleep 10
./service_manager.sh status
```

## 🚨 **Troubleshooting**

### **Service Won't Start**
```bash
# Check detailed status
sudo systemctl status evil-assistant -l

# Check logs for errors
sudo journalctl -u evil-assistant -n 50

# Test manually first
cd ~/evilassistant
source .venv/bin/activate
python -m evilassistant
```

### **Audio Issues After Boot**
```bash
# Check if audio devices are ready
aplay -l

# Restart the service
./service_manager.sh restart
```

### **Network/Hue Issues**
```bash
# Check network connectivity
ping 192.168.0.20

# Check if environment variables are set
sudo systemctl show evil-assistant | grep Environment
```

## 🎉 **What You Get**

✅ **Auto-start on boot** - No manual intervention needed  
✅ **Crash recovery** - Automatically restarts if it fails  
✅ **Easy management** - Simple commands to control  
✅ **Proper logging** - All output captured in journal  
✅ **Production ready** - Reliable service management  

Your Evil Assistant will now be a proper system service that starts automatically and stays running! 🍓👹⚙️
