#!/usr/bin/env python3
"""
Setup separate Python 3.11 environment for Coqui TTS
"""

import subprocess
import sys
import os

def check_pyenv():
    """Check if pyenv is available"""
    try:
        result = subprocess.run(['pyenv', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_python_311_pyenv():
    """Install Python 3.11 using pyenv"""
    print("🐍 Installing Python 3.11 with pyenv...")
    
    commands = [
        ['pyenv', 'install', '3.11.7'],
        ['pyenv', 'virtualenv', '3.11.7', 'coqui-tts'],
    ]
    
    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {result.stderr}")
            return False
        else:
            print(f"✅ Success: {cmd[1]}")
    
    return True

def create_coqui_script():
    """Create script to use Coqui TTS in Python 3.11 env"""
    script_content = '''#!/bin/bash
# Coqui TTS Runner Script

export PYENV_VERSION=coqui-tts

# Install Coqui TTS if not already installed
if ! python -c "import TTS" 2>/dev/null; then
    echo "📦 Installing Coqui TTS..."
    pip install coqui-tts[all]
fi

# Run Coqui TTS with provided arguments
python3 << 'EOF'
import sys
import json
from TTS.api import TTS
import tempfile
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: coqui_runner.sh <text> [model] [output_file]")
        sys.exit(1)
    
    text = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "tts_models/en/ljspeech/tacotron2-DDC"
    output_file = sys.argv[3] if len(sys.argv) > 3 else "coqui_output.wav"
    
    print(f"🎭 Loading model: {model}")
    tts = TTS(model_name=model)
    
    print(f"🔥 Synthesizing: '{text}'")
    tts.tts_to_file(text=text, file_path=output_file)
    
    print(f"✅ Audio saved to: {output_file}")

if __name__ == "__main__":
    main()
EOF
'''
    
    with open('coqui_runner.sh', 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod('coqui_runner.sh', 0o755)
    print("✅ Created coqui_runner.sh")

def setup_conda_env():
    """Alternative: Setup conda environment"""
    print("🅰️ Setting up Conda environment for Coqui TTS...")
    
    commands = [
        ['conda', 'create', '-n', 'coqui-tts', 'python=3.11', '-y'],
        ['conda', 'run', '-n', 'coqui-tts', 'pip', 'install', 'coqui-tts[all]'],
    ]
    
    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {result.stderr}")
            return False
        else:
            print(f"✅ Success")
    
    return True

def create_conda_script():
    """Create conda-based script"""
    script_content = '''#!/bin/bash
# Coqui TTS Conda Runner

conda run -n coqui-tts python3 << 'EOF'
import sys
from TTS.api import TTS

def main():
    if len(sys.argv) < 2:
        print("Usage: conda_coqui.sh <text> [output_file]")
        sys.exit(1)
    
    text = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "coqui_output.wav"
    
    # Use a fast model for testing
    print("🎭 Loading Coqui TTS...")
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
    
    print(f"🔥 Synthesizing: '{text}'")
    tts.tts_to_file(text=text, file_path=output_file)
    
    print(f"✅ Audio saved to: {output_file}")

if __name__ == "__main__":
    main()
EOF
'''
    
    with open('conda_coqui.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('conda_coqui.sh', 0o755)
    print("✅ Created conda_coqui.sh")

def main():
    """Main setup function"""
    print("🎯 Coqui TTS Python 3.11 Environment Setup")
    print("=" * 50)
    
    # Check available options
    has_pyenv = check_pyenv()
    has_conda = subprocess.run(['conda', '--version'], capture_output=True).returncode == 0
    
    print(f"🐍 pyenv available: {has_pyenv}")
    print(f"🅰️ conda available: {has_conda}")
    
    if has_pyenv:
        print("\\n🎯 Option 1: Using pyenv")
        if install_python_311_pyenv():
            create_coqui_script()
            print("\\n✅ Pyenv setup complete!")
            print("Usage: ./coqui_runner.sh 'Your text here'")
    
    elif has_conda:
        print("\\n🎯 Option 2: Using conda")
        if setup_conda_env():
            create_conda_script()
            print("\\n✅ Conda setup complete!")
            print("Usage: ./conda_coqui.sh 'Your text here'")
    
    else:
        print("\\n❌ Neither pyenv nor conda available.")
        print("\\nInstall options:")
        print("1. Install pyenv: https://github.com/pyenv/pyenv")
        print("2. Install conda: https://docs.conda.io/en/latest/miniconda.html")
        print("3. Use Docker approach instead")

if __name__ == "__main__":
    main()
