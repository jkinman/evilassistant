#!/usr/bin/env python3
"""
Evil Assistant - Transcript Decoder
Manual decoding tool for encrypted transcript logs
"""

import os
import json
import argparse
from datetime import datetime
from cryptography.fernet import Fernet
from typing import List, Dict

def load_encryption_key() -> bytes:
    """Load the encryption key from .transcript_key file"""
    key_file = ".transcript_key"
    
    if not os.path.exists(key_file):
        print("❌ No encryption key found (.transcript_key)")
        print("   Transcripts have never been created or key was deleted")
        return None
    
    try:
        with open(key_file, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Failed to read encryption key: {e}")
        return None

def decrypt_transcript_file(filepath: str, cipher: Fernet) -> List[Dict]:
    """Decrypt a single transcript file"""
    try:
        with open(filepath, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = cipher.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
        
    except Exception as e:
        print(f"❌ Failed to decrypt {filepath}: {e}")
        return []

def format_timestamp(timestamp: float) -> str:
    """Format timestamp for human reading"""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def print_transcript_entry(entry: Dict, show_details: bool = True):
    """Print a single transcript entry"""
    timestamp = format_timestamp(entry.get('timestamp', 0))
    speaker = entry.get('speaker_id', 'Unknown')
    text = entry.get('text', '')
    confidence = entry.get('confidence', 0)
    duration = entry.get('duration', 0)
    
    print(f"📅 {timestamp}")
    print(f"🗣️  {speaker}: {text}")
    
    if show_details:
        print(f"   📊 Confidence: {confidence:.2f}, Duration: {duration:.1f}s")
    
    print()

def main():
    parser = argparse.ArgumentParser(description='Decode Evil Assistant encrypted transcripts')
    parser.add_argument('--date', 
                       help='Decode specific date (YYYY-MM-DD), default: all dates')
    parser.add_argument('--search', 
                       help='Search for specific text in transcripts')
    parser.add_argument('--speaker',
                       help='Filter by specific speaker ID')
    parser.add_argument('--export',
                       help='Export to JSON file (unencrypted)')
    parser.add_argument('--details', 
                       action='store_true',
                       help='Show detailed information (confidence, duration)')
    parser.add_argument('--stats', 
                       action='store_true',
                       help='Show statistics only')
    
    args = parser.parse_args()
    
    print("🔓 Evil Assistant Transcript Decoder")
    print("=" * 50)
    
    # Load encryption key
    key = load_encryption_key()
    if not key:
        return
    
    cipher = Fernet(key)
    print("✅ Encryption key loaded")
    
    # Find transcript files
    transcript_dir = "transcripts"
    if not os.path.exists(transcript_dir):
        print("❌ No transcripts directory found")
        return
    
    transcript_files = [f for f in os.listdir(transcript_dir) if f.endswith('.enc')]
    
    if not transcript_files:
        print("📭 No encrypted transcript files found")
        return
    
    print(f"📁 Found {len(transcript_files)} transcript files")
    print()
    
    # Filter by date if specified
    if args.date:
        target_file = f"transcripts_{args.date}.enc"
        transcript_files = [f for f in transcript_files if f == target_file]
        if not transcript_files:
            print(f"❌ No transcripts found for date {args.date}")
            return
    
    # Decode all matching files
    all_entries = []
    total_speakers = set()
    
    for filename in sorted(transcript_files):
        filepath = os.path.join(transcript_dir, filename)
        print(f"🔓 Decoding {filename}...")
        
        entries = decrypt_transcript_file(filepath, cipher)
        if entries:
            all_entries.extend(entries)
            
            # Track speakers
            for entry in entries:
                if entry.get('speaker_id'):
                    total_speakers.add(entry['speaker_id'])
    
    # Filter entries
    filtered_entries = all_entries
    
    if args.search:
        search_term = args.search.lower()
        filtered_entries = [e for e in filtered_entries 
                          if search_term in e.get('text', '').lower()]
    
    if args.speaker:
        filtered_entries = [e for e in filtered_entries 
                          if e.get('speaker_id') == args.speaker]
    
    # Sort by timestamp
    filtered_entries.sort(key=lambda x: x.get('timestamp', 0))
    
    # Show statistics
    if args.stats or len(filtered_entries) > 50:
        print("📊 STATISTICS:")
        print(f"   Total conversations: {len(all_entries)}")
        print(f"   Unique speakers: {len(total_speakers)}")
        print(f"   Date range: {transcript_files[0].split('_')[1].split('.')[0]} to {transcript_files[-1].split('_')[1].split('.')[0]}")
        
        if args.search:
            print(f"   Matches for '{args.search}': {len(filtered_entries)}")
        
        print(f"   Speakers identified: {', '.join(sorted(total_speakers))}")
        print()
    
    if args.stats:
        return
    
    # Export to file
    if args.export:
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_entries": len(filtered_entries),
            "speakers": list(total_speakers),
            "entries": filtered_entries
        }
        
        with open(args.export, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📤 Exported {len(filtered_entries)} entries to {args.export}")
        return
    
    # Display entries
    if not filtered_entries:
        print("📭 No matching transcript entries found")
        return
    
    print(f"📝 TRANSCRIPTS ({len(filtered_entries)} entries):")
    print("=" * 50)
    
    for entry in filtered_entries:
        print_transcript_entry(entry, args.details)
    
    print(f"📊 Total: {len(filtered_entries)} conversations")

if __name__ == "__main__":
    main()
