#!/usr/bin/env python3
"""
Evil Assistant - Transcription Commands
"Your conversations are mine to catalog and command!"
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Optional
from .continuous_transcription import get_transcriber, start_continuous_transcription, stop_continuous_transcription, search_transcription_logs

class EvilTranscriptionHandler:
    """Handles all transcription-related voice commands with demonic flair"""
    
    def __init__(self):
        self.evil_responses = {
            "transcription_started": [
                "I now hear every whisper in your domain, mortal!",
                "Your conversations are mine to harvest and hoard!",
                "Nothing escapes my all-hearing presence!",
                "The voices in your realm shall be catalogued!"
            ],
            "transcription_stopped": [
                "I cease my surveillance... for now, mortal.",
                "Your privacy returns, though my memory remains!",
                "The listening shadows retreat to the digital void.",
                "I grant you temporary silence from my gaze."
            ],
            "search_results_found": [
                "I found {count} instances of your pitiful conversations!",
                "Your words echo through my digital realm, mortal!",
                "The conversations you seek are revealed: {count} found!",
                "My archives yield {count} records of your chatter!"
            ],
            "search_no_results": [
                "Your query yields nothing from my vast surveillance!",
                "Those words were never spoken in my presence!",
                "The void contains no such conversations, mortal!",
                "My omniscient ears heard no such words!"
            ],
            "speaker_summary": [
                "I have catalogued {count} distinct voices in your domain!",
                "My surveillance has identified {count} separate mortals!",
                "The speakers under my watch number {count}!",
                "{count} unique vocal patterns are in my possession!"
            ],
            "recent_activity": [
                "In the last hour, I recorded {count} conversations!",
                "Recent chatter reveals {count} exchanges, mortal!",
                "Your domain buzzed with {count} spoken words recently!",
                "The voices spoke {count} times in the recent past!"
            ],
            "transcript_preview": [
                "At {time}, {speaker} spoke: '{text}'",
                "{speaker} whispered at {time}: '{text}'",
                "The voice of {speaker} echoed at {time}: '{text}'"
            ],
            "privacy_deletion": [
                "The requested memories have been purged from my realm!",
                "Your words vanish into the digital abyss!",
                "The conversations are erased from my dark archives!",
                "Your secrets are consumed by the void!"
            ],
            "stats_report": [
                "I have collected {total} transcripts from {speakers} speakers!",
                "My surveillance encompasses {total} recorded utterances!",
                "The archive contains {total} conversations across {speakers} voices!"
            ]
        }
    
    def get_evil_response(self, category: str, **kwargs) -> str:
        """Get a random evil response for the given category"""
        if category not in self.evil_responses:
            return "Your request has been... processed, mortal."
        
        responses = self.evil_responses[category]
        response = random.choice(responses)
        
        try:
            return response.format(**kwargs)
        except:
            return response
    
    def is_transcription_command(self, text: str) -> bool:
        """Check if text contains transcription-related commands"""
        text_lower = text.lower()
        
        transcription_keywords = [
            'conversation', 'conversations', 'transcript', 'transcripts',
            'record', 'recording', 'listen', 'listening', 'heard', 'said',
            'spoke', 'talking', 'voice', 'voices', 'speaker', 'speakers',
            'log', 'logs', 'surveillance', 'monitor', 'monitoring'
        ]
        
        command_patterns = [
            'what did', 'who said', 'who was talking', 'what was said',
            'search for', 'find conversation', 'show me', 'tell me about',
            'start recording', 'stop recording', 'start listening', 'stop listening',
            'delete conversation', 'clear logs', 'recent activity', 'who spoke',
            'stats', 'statistics', 'summary', 'report'
        ]
        
        return (any(keyword in text_lower for keyword in transcription_keywords) or
                any(pattern in text_lower for pattern in command_patterns))
    
    async def process_transcription_command(self, text: str) -> Optional[str]:
        """Process transcription-related commands"""
        text_lower = text.lower()
        transcriber = get_transcriber()
        
        # Start/Stop commands - Flexible semantic parsing like smart home
        if self._is_start_command(text_lower):
            success = start_continuous_transcription()
            if success:
                return self.get_evil_response("transcription_started")
            else:
                return "My surveillance is already active, mortal!"
        
        if self._is_stop_command(text_lower):
            success = stop_continuous_transcription()
            if success:
                return self.get_evil_response("transcription_stopped")
            else:
                return "My surveillance was not active, foolish mortal!"
        
        # Search commands
        if any(phrase in text_lower for phrase in ['what did', 'who said', 'search for', 'find conversation']):
            search_query = self._extract_search_query(text)
            if search_query:
                results = await search_transcription_logs(search_query, days_back=7)
                
                if results:
                    response = self.get_evil_response("search_results_found", count=len(results))
                    
                    # Add preview of first few results
                    preview_count = min(3, len(results))
                    for i, result in enumerate(results[:preview_count]):
                        time_str = datetime.fromtimestamp(result.timestamp).strftime("%H:%M")
                        speaker = result.speaker_id or "Unknown Voice"
                        text_preview = result.text[:100] + "..." if len(result.text) > 100 else result.text
                        
                        preview = self.get_evil_response("transcript_preview", 
                                                       time=time_str, 
                                                       speaker=speaker, 
                                                       text=text_preview)
                        response += f" {preview}"
                    
                    if len(results) > 3:
                        response += f" And {len(results) - 3} more instances, mortal!"
                    
                    return response
                else:
                    return self.get_evil_response("search_no_results")
        
        # Speaker summary
        if any(phrase in text_lower for phrase in ['who spoke', 'speakers', 'voices', 'how many people']):
            speakers = transcriber.get_speaker_summary()
            count = len(speakers)
            
            if count > 0:
                response = self.get_evil_response("speaker_summary", count=count)
                
                # Add details about each speaker
                for speaker_id, profile in speakers.items():
                    last_heard = datetime.fromtimestamp(profile.last_heard).strftime("%H:%M")
                    response += f" {speaker_id} last spoke at {last_heard} with {profile.total_segments} recorded segments."
                
                return response
            else:
                return "No speakers have been catalogued in my surveillance, mortal!"
        
        # Recent activity
        if any(phrase in text_lower for phrase in ['recent', 'lately', 'today', 'this hour', 'last hour']):
            hours_back = 1
            if 'today' in text_lower:
                hours_back = 24
            elif 'this hour' in text_lower or 'last hour' in text_lower:
                hours_back = 1
            
            recent = transcriber.get_recent_activity(hours_back)
            count = len(recent)
            
            if count > 0:
                response = self.get_evil_response("recent_activity", count=count)
                
                # Add preview of most recent
                if recent:
                    latest = recent[0]
                    time_str = datetime.fromtimestamp(latest.timestamp).strftime("%H:%M")
                    speaker = latest.speaker_id or "Unknown Voice"
                    text_preview = latest.text[:80] + "..." if len(latest.text) > 80 else latest.text
                    
                    response += f" Most recently, {speaker} spoke at {time_str}: '{text_preview}'"
                
                return response
            else:
                return f"Silence has reigned in your domain for the past {hours_back} hour(s), mortal!"
        
        # Statistics
        if any(phrase in text_lower for phrase in ['stats', 'statistics', 'summary', 'report', 'total']):
            stats = transcriber.get_stats()
            
            return self.get_evil_response("stats_report", 
                                        total=stats['total_transcripts'],
                                        speakers=stats['speakers_identified'])
        
        # Privacy/deletion commands
        if any(phrase in text_lower for phrase in ['delete', 'clear', 'erase', 'purge', 'remove']):
            return await self._handle_privacy_command(text_lower)
        
        return None
    
    async def _handle_privacy_command(self, text: str) -> str:
        """Handle privacy and deletion commands"""
        try:
            from .privacy_manager import get_privacy_manager
            privacy_manager = get_privacy_manager()
            
            # Specific deletion commands
            if "all" in text or "everything" in text:
                return privacy_manager.delete_all_transcripts()
            elif "today" in text:
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")
                return privacy_manager.delete_transcripts_by_date(today)
            elif "yesterday" in text:
                from datetime import datetime, timedelta
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                return privacy_manager.delete_transcripts_by_date(yesterday)
            elif "old" in text or "older" in text:
                # Delete transcripts older than 7 days
                return privacy_manager.delete_transcripts_older_than(7)
            elif "key" in text or "encryption" in text:
                return privacy_manager.delete_encryption_key()
            else:
                # Default: show privacy status
                return privacy_manager.get_privacy_status()
                
        except ImportError:
            return "Privacy controls are not available, mortal!"
        except Exception as e:
            logger.error(f"Privacy command failed: {e}")
            return "The dark forces resist your privacy command!"
    
    def _is_start_command(self, text: str) -> bool:
        """Flexible detection for start recording commands"""
        start_indicators = ['start', 'begin', 'enable', 'activate', 'turn on']
        recording_indicators = ['recording', 'transcription', 'surveillance', 'monitoring', 'listening']
        
        # Check if text contains both a start indicator and recording indicator
        has_start = any(indicator in text for indicator in start_indicators)
        has_recording = any(indicator in text for indicator in recording_indicators)
        
        return has_start and has_recording
    
    def _is_stop_command(self, text: str) -> bool:
        """Flexible detection for stop recording commands"""
        stop_indicators = ['stop', 'end', 'disable', 'deactivate', 'turn off', 'cease']
        recording_indicators = ['recording', 'transcription', 'surveillance', 'monitoring', 'listening']
        
        # Check if text contains both a stop indicator and recording indicator
        has_stop = any(indicator in text for indicator in stop_indicators)
        has_recording = any(indicator in text for indicator in recording_indicators)
        
        return has_stop and has_recording
    
    def _extract_search_query(self, text: str) -> Optional[str]:
        """Extract search query from natural language"""
        text_lower = text.lower()
        
        # Pattern: "what did [someone] say about [topic]"
        patterns = [
            ('what did', 'say about'),
            ('who said', 'about'),
            ('search for', ''),
            ('find conversation about', ''),
            ('what was said about', ''),
        ]
        
        for start_phrase, end_phrase in patterns:
            if start_phrase in text_lower:
                start_idx = text_lower.find(start_phrase) + len(start_phrase)
                
                if end_phrase and end_phrase in text_lower:
                    end_idx = text_lower.find(end_phrase, start_idx)
                    if end_idx > start_idx:
                        # Extract the topic after "about"
                        topic_start = end_idx + len(end_phrase)
                        query = text[topic_start:].strip()
                        return query if len(query) > 2 else None
                else:
                    # Extract everything after the start phrase
                    query = text[start_idx:].strip()
                    return query if len(query) > 2 else None
        
        # Fallback: extract quoted text or key words
        words = text.split()
        if len(words) > 2:
            # Return last few words as search query
            return ' '.join(words[-3:])
        
        return None

# Global instance
_evil_transcription_handler = None

def get_evil_transcription_handler() -> EvilTranscriptionHandler:
    """Get singleton evil transcription handler"""
    global _evil_transcription_handler
    if _evil_transcription_handler is None:
        _evil_transcription_handler = EvilTranscriptionHandler()
    return _evil_transcription_handler

async def process_evil_transcription_command(text: str) -> Optional[str]:
    """Process transcription command through the evil handler"""
    handler = get_evil_transcription_handler()
    
    if handler.is_transcription_command(text):
        return await handler.process_transcription_command(text)
    
    return None
