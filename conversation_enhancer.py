#!/usr/bin/env python3
"""
Enhanced conversation analysis for Evil Assistant transcripts
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from cryptography.fernet import Fernet

def load_and_analyze_conversations(date: str = None) -> Dict:
    """Load transcripts and group into actual conversations"""
    
    # Load encryption key
    with open('.transcript_key', 'rb') as f:
        key = f.read()
    cipher = Fernet(key)
    
    # Load transcript file
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    filepath = f"transcripts/transcripts_{date}.enc"
    
    try:
        with open(filepath, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = cipher.decrypt(encrypted_data)
        entries = json.loads(decrypted_data.decode())
    except Exception as e:
        print(f"Error loading transcripts: {e}")
        return {}
    
    # Group entries into conversations (within 2 minutes = same conversation)
    conversations = []
    current_conversation = []
    last_timestamp = 0
    
    for entry in sorted(entries, key=lambda x: x['timestamp']):
        timestamp = entry['timestamp']
        
        # If more than 2 minutes gap, start new conversation
        if timestamp - last_timestamp > 120:  # 2 minutes
            if current_conversation:
                conversations.append(current_conversation)
            current_conversation = [entry]
        else:
            current_conversation.append(entry)
        
        last_timestamp = timestamp
    
    # Add the last conversation
    if current_conversation:
        conversations.append(current_conversation)
    
    # Analyze conversations
    analyzed = {
        "total_conversations": len(conversations),
        "conversations": [],
        "speaker_stats": {},
        "topics": []
    }
    
    for i, conv in enumerate(conversations):
        if len(conv) < 2:  # Skip single-utterance "conversations"
            continue
            
        conv_analysis = {
            "id": i + 1,
            "start_time": datetime.fromtimestamp(conv[0]['timestamp']).strftime("%H:%M:%S"),
            "duration": conv[-1]['timestamp'] - conv[0]['timestamp'],
            "speakers": list(set(entry['speaker_id'] for entry in conv)),
            "utterances": len(conv),
            "content": []
        }
        
        for entry in conv:
            conv_analysis["content"].append({
                "time": datetime.fromtimestamp(entry['timestamp']).strftime("%H:%M:%S"),
                "speaker": entry['speaker_id'],
                "text": entry['text'],
                "confidence": entry['confidence']
            })
        
        analyzed["conversations"].append(conv_analysis)
    
    # Speaker statistics
    all_speakers = set()
    for conv in conversations:
        for entry in conv:
            speaker = entry['speaker_id']
            all_speakers.add(speaker)
            
            if speaker not in analyzed["speaker_stats"]:
                analyzed["speaker_stats"][speaker] = {
                    "total_utterances": 0,
                    "total_words": 0,
                    "conversations_participated": 0,
                    "avg_confidence": 0
                }
            
            stats = analyzed["speaker_stats"][speaker]
            stats["total_utterances"] += 1
            stats["total_words"] += len(entry['text'].split())
            stats["avg_confidence"] += entry['confidence']
    
    # Calculate averages
    for speaker, stats in analyzed["speaker_stats"].items():
        if stats["total_utterances"] > 0:
            stats["avg_confidence"] /= stats["total_utterances"]
            stats["conversations_participated"] = len([c for c in analyzed["conversations"] 
                                                     if speaker in c["speakers"]])
    
    return analyzed

def print_conversation_summary(analysis: Dict):
    """Print a nice summary of conversations"""
    print("📊 CONVERSATION ANALYSIS")
    print("=" * 50)
    
    print(f"Total meaningful conversations: {len(analysis['conversations'])}")
    print(f"Total speakers: {len(analysis['speaker_stats'])}")
    print()
    
    # Speaker summary
    print("👥 SPEAKER SUMMARY:")
    for speaker, stats in analysis['speaker_stats'].items():
        print(f"  {speaker}:")
        print(f"    • {stats['total_utterances']} utterances")
        print(f"    • {stats['total_words']} total words")
        print(f"    • {stats['conversations_participated']} conversations")
        print(f"    • {stats['avg_confidence']:.2f} avg confidence")
        print()
    
    # Conversation details
    print("💬 CONVERSATIONS:")
    for conv in analysis['conversations']:
        duration_str = f"{conv['duration']:.0f}s" if conv['duration'] < 60 else f"{conv['duration']/60:.1f}m"
        print(f"\n🔸 Conversation {conv['id']} at {conv['start_time']} ({duration_str})")
        print(f"   Speakers: {', '.join(conv['speakers'])}")
        print(f"   Utterances: {conv['utterances']}")
        
        for utterance in conv['content']:
            print(f"   {utterance['time']} {utterance['speaker']}: {utterance['text']}")

if __name__ == "__main__":
    import sys
    
    date = sys.argv[1] if len(sys.argv) > 1 else None
    analysis = load_and_analyze_conversations(date)
    
    if analysis.get('conversations'):
        print_conversation_summary(analysis)
    else:
        print("📭 No meaningful conversations found")
        print("💡 Try having longer conversations (multiple exchanges) for better analysis")
