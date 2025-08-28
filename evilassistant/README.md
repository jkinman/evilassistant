# Evil Assistant

A demonic voice assistant powered by xAI's Grok API, using Piper TTS and Sox for a terrifying voice.

## Installation

1. Install system dependencies:
   ```bash
   sudo apt install sox rubberband-cli
   ```
2. Install the package:
   ```bash
   pip install .
   ```
3. Set the API key:
   ```bash
   export XAI_API_KEY="your_xai_api_key_here"
   ```
4. Run:
   ```bash
   evilassistant
   ```


## Run on Raspberry Pi

Options to Keep It Running
1. Run in Background with nohup (Simple)
How It Works: nohup (no hangup) detaches the process from your terminal, letting it run after logout.

Steps:
Start the app with nohup:
   ```bash
   cd ~/evilassistant
   nohup evilassistant &
   ```
& puts it in the background; nohup prevents termination on logout.

Check it’s running:
   ```bash
   ps aux | grep evilassistant
   ```
Look for the process (e.g., python3 ... evilassistant).

Exit SSH: exit—it’ll keep running.

Stop It Later:
   ```bash
   pkill -f evilassistant
   ```
Output: Logs go to nohup.out in ~/evilassistant/—check with cat nohup.out.

Pros: Quick, no setup needed.

Cons: No auto-restart on crash or reboot.

## Hardware: LED Light Box via GPIO PWM

- Use a 3.3V logic-level MOSFET or a PWM LED driver between Raspberry Pi `GPIO18` (BCM) and the LED light box dimmer input. Do not drive the LED directly from the GPIO.
- Configure the dimmer to accept a 3.3V PWM signal (or use level shifting/driver as needed). Frequency used: 1 kHz.
- The code modulates brightness proportional to output audio loudness using an envelope follower.

### Wiring (typical MOSFET low-side)
- Gate: Raspberry Pi `GPIO18` through a small resistor (e.g., 150 Ω)
- Source: GND
- Drain: LED negative terminal; LED positive to 12V/appropriate supply via current-limited driver
- Add a flyback diode if driving inductive loads (not needed for pure LEDs with proper driver)

### Configurable settings in `evilassistant/config.py`
- `GPIO_ENABLED`: set `True` to enable PWM dimming
- `GPIO_PIN`: default `18` (supports hardware PWM)
- `PWM_FREQUENCY_HZ`: default `1000`
- `BRIGHTNESS_MIN` / `BRIGHTNESS_MAX`: duty-cycle limits (percent)
- `LED_GAIN`: maps audio amplitude to brightness
- `AMPLITUDE_SMOOTHING`: 0..1 smoothing factor for brightness changes

## Better Wake Word Reliability

- The assistant now requires `WAKE_CONFIRM_WINDOWS` consecutive detection windows containing a wake phrase to trigger, reducing false wakes.
- Whisper VAD is enabled during transcription.

Tune in `evilassistant/config.py`:
- `CHUNK_DURATION`: length (s) of wake-listen windows
- `WAKE_CONFIRM_WINDOWS`: consecutive hits required
- Adjust/add `WAKE_PHRASES` as desired

## Demon Voice Improvements

- Enhanced SoX chain for darker timbre: bass boost, pitch drop, slight slowdown, saturation, and reverb. Tweak `SOX_EFFECTS` if needed.

Example values:
```text
SOX_EFFECTS = "norm -3 bass +6 treble -3 pitch -700 tempo 0.88 overdrive 12:12 reverb 20 50 100 100 0 -t"
```

If Piper output is too bright or thin, try different voices (e.g., male voices) and layer effects. You can also cascade formant shifts using `sox mcompand` and `stretch` if CPU allows.

## Wake Word with Porcupine (optional)

- Set `USE_PORCUPINE = True` in `evilassistant/config.py`.
- Set env var with your access key:
```bash
export PORCUPINE_ACCESS_KEY="..."
```
- Use built-in keywords via `PORCUPINE_KEYWORDS = ["jarvis"]` or point to custom `.ppn` files with `PORCUPINE_KEYWORD_PATHS`.

## Cloud Demon Voice (optional)

- Set `TTS_PROVIDER = "elevenlabs"` and configure `ELEVENLABS_VOICE_ID` and model.
- Prefer streaming APIs for lower latency; PWM brightness will follow playback in real time.
