# Evil Assistant

A demonic voice assistant powered by xAI's Grok API, using Piper TTS and Sox for a terrifying voice.

## Installation

1. Install system dependencies:
   ```bash
   sudo apt install sox
2. Install the package:
   ```bash
   pip install .

3. Set the API key:
   ```bash
   export XAI_API_KEY="your_xai_api_key_here"

4. Run:
   ```bash
   evilassistant


## Run on Raspberry Pi

Options to Keep It Running
1. Run in Background with nohup (Simple)
How It Works: nohup (no hangup) detaches the process from your terminal, letting it run after logout.

Steps:
Start the app with nohup:
   ```bash
cd ~/evilassistant
nohup evilassistant &

& puts it in the background; nohup prevents termination on logout.

Check it’s running:
   ```bash

ps aux | grep evilassistant

Look for the process (e.g., python3 ... evilassistant).

Exit SSH: exit—it’ll keep running.

Stop It Later:
   ```bash
pkill -f evilassistant

Output: Logs go to nohup.out in ~/evilassistant/—check with cat nohup.out.

Pros: Quick, no setup needed.

Cons: No auto-restart on crash or reboot.

