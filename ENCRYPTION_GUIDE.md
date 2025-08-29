# 🔐 Evil Assistant - Encryption & Data Recovery Guide

This guide explains how the transcript encryption system works and how to decode your data if needed.

## 🔧 **How Encryption Works**

### **Encryption Algorithm**
- **Algorithm**: AES-256 via Fernet (cryptography library)
- **Key Generation**: Secure random 256-bit key
- **Mode**: Authenticated encryption with timestamp verification
- **Format**: Base64-encoded encrypted data

### **Key Management**
```
.transcript_key          # 256-bit encryption key (binary)
├── Auto-generated on first use
├── Permissions: 600 (owner read-only)
├── One key for all transcripts
└── CRITICAL: Don't delete this file!
```

### **File Structure**
```
transcripts/
├── transcripts_2024-01-15.enc    # Daily encrypted logs
├── transcripts_2024-01-16.enc    # JSON → Encrypted → Base64
└── transcripts_2024-01-17.enc    # Fernet format
```

### **Data Format (Before Encryption)**
```json
[
  {
    "timestamp": 1705123456.789,
    "text": "Turn on the living room lights",
    "confidence": 0.85,
    "speaker_id": "Speaker1",
    "duration": 2.3,
    "audio_hash": "a1b2c3d4e5f6"
  },
  {
    "timestamp": 1705123478.123,
    "text": "The lights are now on, mortal",
    "confidence": 0.92,
    "speaker_id": "Speaker2", 
    "duration": 1.8,
    "audio_hash": "f6e5d4c3b2a1"
  }
]
```

## 🔓 **Manual Decoding Methods**

### **Method 1: Using the Decoder Script**

```bash
# Decode all transcripts
python decode_transcripts.py

# Decode specific date
python decode_transcripts.py --date 2024-01-15

# Search for specific text
python decode_transcripts.py --search "lights"

# Filter by speaker
python decode_transcripts.py --speaker Speaker1

# Show statistics only
python decode_transcripts.py --stats

# Export to unencrypted JSON
python decode_transcripts.py --export my_transcripts.json

# Show detailed info (confidence, duration)
python decode_transcripts.py --details
```

### **Method 2: Python Code**

```python
#!/usr/bin/env python3
import json
from cryptography.fernet import Fernet

# Load the encryption key
with open('.transcript_key', 'rb') as f:
    key = f.read()

cipher = Fernet(key)

# Decrypt a specific file
with open('transcripts/transcripts_2024-01-15.enc', 'rb') as f:
    encrypted_data = f.read()

# Decrypt and parse
decrypted_data = cipher.decrypt(encrypted_data)
transcripts = json.loads(decrypted_data.decode())

# Print all transcripts
for entry in transcripts:
    print(f"Time: {entry['timestamp']}")
    print(f"Speaker: {entry['speaker_id']}")
    print(f"Text: {entry['text']}")
    print()
```

### **Method 3: Command Line One-Liner**

```bash
# Quick decrypt (requires cryptography library)
python3 -c "
from cryptography.fernet import Fernet
import json
key = open('.transcript_key', 'rb').read()
cipher = Fernet(key)
data = cipher.decrypt(open('transcripts/transcripts_2024-01-15.enc', 'rb').read())
transcripts = json.loads(data.decode())
for t in transcripts: print(f'{t[\"timestamp\"]} {t[\"speaker_id\"]}: {t[\"text\"]}')
"
```

## 🛡️ **Security Features**

### **What's Protected**
- ✅ **Transcript text** - All conversation content encrypted
- ✅ **Timestamps** - When conversations occurred  
- ✅ **Speaker IDs** - Anonymous speaker identification
- ✅ **Metadata** - Confidence scores, duration, audio hashes
- ✅ **File integrity** - Fernet includes authentication

### **What's NOT Encrypted**
- ❌ **Filenames** - Date visible in filename (transcripts_YYYY-MM-DD.enc)
- ❌ **File sizes** - Approximate conversation volume visible
- ❌ **File count** - Number of days with conversations visible
- ❌ **Directory structure** - transcripts/ folder is visible

### **Security Properties**
- **Authenticated Encryption** - Tampering detected automatically
- **Timestamp Protection** - Fernet includes timestamp validation
- **Forward Secrecy** - Old data remains encrypted if key changes
- **Local Only** - No cloud storage, no network transmission

## 🚨 **Data Recovery Scenarios**

### **Scenario 1: Normal Access**
**Problem**: Want to read transcripts manually  
**Solution**: Use `decode_transcripts.py` script

### **Scenario 2: Lost Key File**
**Problem**: `.transcript_key` deleted or corrupted  
**Solution**: **❌ DATA IS PERMANENTLY LOST**
```bash
# This will NOT work:
# - No key recovery possible
# - No password reset
# - No backup decryption
# - AES-256 is unbreakable without key
```

### **Scenario 3: Corrupted Transcript File**
**Problem**: `.enc` file damaged  
**Solution**: Check other daily files
```bash
# Try other dates
python decode_transcripts.py --date 2024-01-14
python decode_transcripts.py --date 2024-01-16

# Check file integrity
python -c "
from cryptography.fernet import Fernet
key = open('.transcript_key', 'rb').read()
cipher = Fernet(key)
try:
    data = cipher.decrypt(open('transcripts/transcripts_2024-01-15.enc', 'rb').read())
    print('✅ File is valid')
except:
    print('❌ File is corrupted')
"
```

### **Scenario 4: Migration/Backup**
**Problem**: Moving to new system  
**Solution**: Copy both key and data
```bash
# CRITICAL: Copy BOTH files together
cp .transcript_key /backup/location/
cp -r transcripts/ /backup/location/

# Test decryption on new system
python decode_transcripts.py --stats
```

## 🔧 **Advanced Operations**

### **Key Rotation (Manual)**
```python
#!/usr/bin/env python3
# WARNING: This will make old transcripts unreadable!
from cryptography.fernet import Fernet
import os

# Generate new key
new_key = Fernet.generate_key()

# Backup old key
os.rename('.transcript_key', '.transcript_key.old')

# Save new key
with open('.transcript_key', 'wb') as f:
    f.write(new_key)

print("🔄 New encryption key generated")
print("⚠️  Old transcripts now require .transcript_key.old to decrypt")
```

### **Bulk Export/Conversion**
```bash
# Export all transcripts to readable format
python decode_transcripts.py --export all_transcripts.json

# Convert to CSV
python -c "
import json, csv
data = json.load(open('all_transcripts.json'))
with open('transcripts.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'speaker_id', 'text', 'confidence'])
    writer.writeheader()
    for entry in data['entries']:
        writer.writerow(entry)
"
```

### **Secure Deletion**
```bash
# Securely delete transcripts (Linux/Mac)
shred -vfz -n 3 transcripts/*.enc
shred -vfz -n 3 .transcript_key

# Or use rm (less secure)
rm -rf transcripts/
rm .transcript_key
```

## 🎯 **Best Practices**

### **Key Management**
- ✅ **Never share** `.transcript_key` with anyone
- ✅ **Backup safely** if you need the data long-term
- ✅ **Test recovery** periodically with decoder script
- ❌ **Never commit** key to git (already in .gitignore)

### **Data Management**
- ✅ **Regular cleanup** - Auto-deletion after 7 days
- ✅ **Monitor disk space** - Encrypted files can accumulate
- ✅ **Export important** conversations before auto-deletion
- ❌ **Don't edit** .enc files directly (will corrupt them)

### **Privacy Operations**
```bash
# Check what's stored
python decode_transcripts.py --stats

# Search for sensitive content
python decode_transcripts.py --search "password"
python decode_transcripts.py --search "social security"

# Delete specific day
rm transcripts/transcripts_2024-01-15.enc

# Emergency privacy wipe
rm -rf transcripts/ .transcript_key
```

## 📊 **Decoder Script Usage Examples**

```bash
# Quick overview
python decode_transcripts.py --stats

# Today's conversations
python decode_transcripts.py --date $(date +%Y-%m-%d)

# Find all mentions of smart home
python decode_transcripts.py --search "lights" --details

# Export conversations with family
python decode_transcripts.py --speaker Speaker1 --export family_talks.json

# Full transcript dump with details
python decode_transcripts.py --details > full_transcripts.txt
```

---

**🔐 Remember: The encryption is only as secure as your `.transcript_key` file. Protect it like a password!**
