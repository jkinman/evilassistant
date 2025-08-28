# 🏠 Quick Smart Home Integration Guide

## 🚀 Super Fast Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip install phue requests aiohttp
```

### Step 2: Run Auto-Setup
```bash
python setup_smart_home.py
```
This will:
- Auto-discover your Philips Hue bridge
- Find Google Home devices  
- Help you configure Home Assistant
- Update your `.env` file automatically

### Step 3: Add Smart Home to Your Current Assistant

Edit your `evilassistant/assistant.py` and add this code after line 337 (where you get `full_transcription`):

```python
# Add this import at the top of the file
from .simple_smart_home import handle_smart_home_command

# Add this code right after you get full_transcription and before the LLM call:
# Check for smart home commands first
smart_home_response = handle_smart_home_command(full_transcription)
if smart_home_response:
    print(f"Evil Assistant says: {smart_home_response}")
    output_file = "evil_output.wav"
    speak_text(smart_home_response, output_file, voice)
    os.remove(output_file)
    continue  # Skip LLM processing for smart home commands
```

That's it! Your assistant now controls smart devices with demonic flair! 👹

## 🗣️ Voice Commands That Work

### Philips Hue
```
"Evil assistant, turn on the living room lights"
"Dark one, make all lights red" 
"Cthulhu, turn off the lights"
"Evil assistant, dim the bedroom lights"
"Make the lights purple"
"Turn on the kitchen lights"
```

### Responses You'll Get
> *"Let there be light! The illumination obeys my command!"*

> *"Behold! The spectrum bends to my will! Red light fills your domain!"*

> *"Darkness consumes the light, as it should be!"*

## 🔧 Manual Device Setup (if auto-setup doesn't work)

### Philips Hue
1. Find your bridge IP:
   - Check your router's connected devices
   - Look for "Philips Hue" 
   - Usually something like `192.168.1.100`

2. Add to `.env` file:
   ```
   PHILIPS_HUE_BRIDGE_IP=192.168.1.100
   ```

3. Test connection:
   ```python
   from phue import Bridge
   bridge = Bridge("192.168.1.100")  # Your IP
   bridge.connect()  # Press bridge button when prompted
   print("Connected!")
   ```

### Home Assistant
1. Get your HA URL (usually `http://homeassistant.local:8123`)
2. Create a long-lived access token:
   - Go to your HA profile
   - Scroll to "Long-lived access tokens"
   - Create token and copy it

3. Add to `.env` file:
   ```
   HOME_ASSISTANT_URL=http://homeassistant.local:8123
   HOME_ASSISTANT_TOKEN=your_token_here
   ```

## 🧪 Test Your Setup

```bash
python -c "from evilassistant.simple_smart_home import test_smart_home; test_smart_home()"
```

## 🎯 What Each Platform Controls

### Philips Hue
- ✅ Turn lights on/off
- ✅ Change colors (red, blue, green, purple, orange, pink, yellow, white)
- ✅ Dim/brighten lights
- ✅ Room-specific control (if your lights are named by room)

### Home Assistant  
- ✅ Any light entities
- ✅ Basic on/off control
- ✅ Color control
- 🔄 Can be extended for switches, sensors, etc.

### Google Home (via optimized assistant)
- ✅ Media playback control
- ✅ Volume control
- ✅ Multi-room audio

## 🔥 Advanced: Full Optimized Assistant

For the ultimate experience, use the optimized assistant:

```bash
# Enable smart home in optimized mode
evilassistant --optimized
```

This gives you:
- Faster response times
- Better command parsing
- More device types supported
- Async processing
- Better error handling

## 🛟 Troubleshooting

### "Bridge not found"
- Make sure Hue bridge is powered on
- Check your network connection
- Try manual IP entry

### "Authentication failed"  
- Press the bridge button when prompted
- You have 30 seconds after pressing
- Try again if you missed the window

### "No response from devices"
- Check `.env` file has correct settings
- Test devices work from their native apps
- Verify network connectivity

### "Import errors"
- Install missing packages: `pip install phue requests`
- Check Python version (3.11+ recommended)

## 🎉 Success!

Once working, you can say things like:

> **You**: "Evil assistant, turn on red lights in the living room"
> 
> **Evil Assistant**: *"Behold! The spectrum bends to my demonic influence! Red light fills your domain, mortal!"*

Your smart home is now under the control of dark forces! 🔥👹

For more advanced features, check out `SMART_HOME_SETUP.md` for the complete integration guide.
