#!/usr/bin/env python3
"""
Setup Coqui TTS using Docker with Python 3.11
"""

import subprocess
import tempfile
import os

def create_coqui_dockerfile():
    """Create Dockerfile for Coqui TTS service"""
    dockerfile_content = '''
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    build-essential \\
    libsndfile1 \\
    ffmpeg \\
    && rm -rf /var/lib/apt/lists/*

# Install Coqui TTS
RUN pip install --no-cache-dir coqui-tts[all]

# Create app directory
WORKDIR /app

# Copy TTS service script
COPY coqui_service.py /app/

# Expose port
EXPOSE 5000

# Run the service
CMD ["python", "coqui_service.py"]
'''
    
    with open('Dockerfile.coqui', 'w') as f:
        f.write(dockerfile_content)
    print("✅ Created Dockerfile.coqui")

def create_coqui_service():
    """Create Flask service for Coqui TTS"""
    service_content = '''
#!/usr/bin/env python3
"""
Coqui TTS Microservice
"""

from flask import Flask, request, send_file
from TTS.api import TTS
import tempfile
import os
import json

app = Flask(__name__)

# Initialize TTS models
print("🎭 Loading Coqui TTS models...")
tts_models = {
    "tacotron2": TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC"),
    "vits": TTS(model_name="tts_models/en/ljspeech/vits"),
    # Add more models as needed
}
print("✅ Models loaded!")

@app.route('/synthesize', methods=['POST'])
def synthesize():
    """Synthesize text to speech"""
    try:
        data = request.json
        text = data.get('text', '')
        model = data.get('model', 'tacotron2')
        effects = data.get('effects', [])
        
        if model not in tts_models:
            return {"error": f"Model {model} not available"}, 400
        
        # Generate audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        # Synthesize
        tts_models[model].tts_to_file(text=text, file_path=output_path)
        
        # Apply effects if requested (would need sox in container)
        if effects:
            # Apply effects here
            pass
        
        return send_file(output_path, as_attachment=True, download_name='speech.wav')
        
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/models', methods=['GET'])
def list_models():
    """List available models"""
    return {"models": list(tts_models.keys())}

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return {"status": "healthy", "models_loaded": len(tts_models)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
'''
    
    with open('coqui_service.py', 'w') as f:
        f.write(service_content)
    print("✅ Created coqui_service.py")

def create_docker_compose():
    """Create docker-compose for easy management"""
    compose_content = '''
version: '3.8'

services:
  coqui-tts:
    build:
      context: .
      dockerfile: Dockerfile.coqui
    ports:
      - "5000:5000"
    volumes:
      - ./models:/app/models  # Cache models locally
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    container_name: evil-coqui-tts
'''
    
    with open('docker-compose.coqui.yml', 'w') as f:
        f.write(compose_content)
    print("✅ Created docker-compose.coqui.yml")

def setup_coqui_docker():
    """Set up complete Coqui TTS Docker solution"""
    print("🐳 Setting up Coqui TTS Docker solution...")
    
    # Create files
    create_coqui_dockerfile()
    create_coqui_service()
    create_docker_compose()
    
    print("\\n🎯 Next steps:")
    print("1. Build the Docker image:")
    print("   docker-compose -f docker-compose.coqui.yml build")
    print("\\n2. Start the service:")
    print("   docker-compose -f docker-compose.coqui.yml up -d")
    print("\\n3. Test the service:")
    print("   curl -X POST http://localhost:5000/synthesize \\\\")
    print("        -H 'Content-Type: application/json' \\\\")
    print("        -d '{\"text\":\"I am your evil assistant\"}' \\\\")
    print("        --output test.wav")

if __name__ == "__main__":
    setup_coqui_docker()
