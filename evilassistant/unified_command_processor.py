#!/usr/bin/env python3
"""
Unified Command Processor for Evil Assistant
All voice commands go through the same processing pipeline
"""

import logging
from typing import Optional, Tuple, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class CommandType(Enum):
    """Types of commands the assistant can handle"""
    TRANSCRIPTION = "transcription"
    SMART_HOME = "smart_home" 
    AI_QUERY = "ai_query"
    SYSTEM = "system"

class UnifiedCommandProcessor:
    """Single point for all command processing after wake phrase detection"""
    
    def __init__(self, smart_home_handler, ai_handler, transcription_handler=None):
        self.smart_home = smart_home_handler
        self.ai = ai_handler
        self.transcription = transcription_handler
        
        # Define command patterns in order of priority
        self.command_patterns = [
            # System commands (highest priority)
            {
                "type": CommandType.SYSTEM,
                "patterns": ["stop", "exit", "quit", "shutdown"],
                "handler": self._handle_system_command
            },
            
            # Transcription commands
            {
                "type": CommandType.TRANSCRIPTION,
                "patterns": self._get_transcription_patterns(),
                "handler": self._handle_transcription_command,
                "enabled": transcription_handler is not None
            },
            
            # Smart home commands
            {
                "type": CommandType.SMART_HOME,
                "patterns": self._get_smart_home_patterns(),
                "handler": self._handle_smart_home_command
            },
            
            # AI query (fallback - lowest priority)
            {
                "type": CommandType.AI_QUERY,
                "patterns": [],  # Catches everything else
                "handler": self._handle_ai_command
            }
        ]
    
    def _get_transcription_patterns(self) -> Dict[str, Any]:
        """Get transcription command patterns"""
        return {
            "start_recording": {
                "triggers": ["start", "begin", "enable", "activate"],
                "subjects": ["recording", "transcription", "surveillance", "monitoring", "listening"]
            },
            "stop_recording": {
                "triggers": ["stop", "end", "disable", "deactivate", "cease"],
                "subjects": ["recording", "transcription", "surveillance", "monitoring", "listening"]
            },
            "search_transcripts": {
                "triggers": ["what did", "who said", "search for", "find conversation", "show me"],
                "subjects": ["conversation", "transcript", "said", "spoke"]
            },
            "speaker_info": {
                "triggers": ["who spoke", "who was talking", "how many people", "who", "speakers"],
                "subjects": ["speaker", "speakers", "voice", "voices", "people", "today", "yesterday"]
            },
            "recent_activity": {
                "triggers": ["recent", "lately", "today", "this hour", "last hour"],
                "subjects": ["activity", "conversation", "transcript"]
            },
            "stats": {
                "triggers": ["stats", "statistics", "summary", "report"],
                "subjects": ["transcription", "surveillance", "recording", ""]
            }
        }
    
    def _get_smart_home_patterns(self) -> Dict[str, Any]:
        """Get smart home command patterns"""
        return {
            "lights": {
                "triggers": ["turn on", "turn off", "set", "change", "make", "dim", "brighten"],
                "subjects": ["light", "lights", "lamp", "brightness"]
            },
            "colors": {
                "triggers": ["set", "change", "make", "turn"],
                "subjects": ["red", "blue", "green", "purple", "yellow", "orange", "pink", "white", "color", "colour"]
            },
            "brightness": {
                "triggers": ["set", "change", "dim", "brighten"],
                "subjects": ["brightness", "percent", "%"]
            }
        }
    
    async def process_command(self, text: str) -> Tuple[CommandType, str]:
        """
        Process any voice command through unified pipeline
        Returns: (command_type, response)
        """
        text_lower = text.lower().strip()
        
        logger.info(f"Processing unified command: '{text}'")
        
        # Try each command type in priority order
        for command_config in self.command_patterns:
            if not command_config.get("enabled", True):
                continue
                
            command_type = command_config["type"]
            patterns = command_config["patterns"]
            handler = command_config["handler"]
            
            # Check if this command matches this type
            if self._matches_command_type(text_lower, command_type, patterns):
                logger.info(f"Command classified as: {command_type.value}")
                
                try:
                    response = await handler(text)
                    if response:
                        return command_type, response
                except Exception as e:
                    logger.error(f"Handler failed for {command_type.value}: {e}")
                    continue
        
        # Should never reach here due to AI fallback, but just in case
        return CommandType.AI_QUERY, "I did not understand that command, mortal."
    
    def _matches_command_type(self, text: str, command_type: CommandType, patterns) -> bool:
        """Check if text matches a specific command type"""
        
        if command_type == CommandType.SYSTEM:
            # Only match system commands if they're standalone words, not part of other commands
            system_words = patterns
            for word in system_words:
                if word in text and not any(trans_word in text for trans_word in ["recording", "transcription", "surveillance"]):
                    return True
            return False
        
        elif command_type == CommandType.TRANSCRIPTION:
            return self._matches_transcription_patterns(text, patterns)
        
        elif command_type == CommandType.SMART_HOME:
            return self._matches_smart_home_patterns(text, patterns)
        
        elif command_type == CommandType.AI_QUERY:
            return True  # Always matches (fallback)
        
        return False
    
    def _matches_transcription_patterns(self, text: str, patterns: Dict) -> bool:
        """Check if text matches transcription command patterns"""
        for pattern_name, pattern_config in patterns.items():
            triggers = pattern_config["triggers"]
            subjects = pattern_config["subjects"]
            
            # Check if we have both a trigger and subject
            has_trigger = any(trigger in text for trigger in triggers)
            has_subject = any(subject in text for subject in subjects if subject)
            
            # For some patterns, subject is optional
            if pattern_name in ["stats"] and has_trigger:
                return True
            elif has_trigger and has_subject:
                return True
        
        return False
    
    def _matches_smart_home_patterns(self, text: str, patterns: Dict) -> bool:
        """Check if text matches smart home command patterns"""
        for pattern_name, pattern_config in patterns.items():
            triggers = pattern_config["triggers"]
            subjects = pattern_config["subjects"]
            
            # Check if we have both a trigger and subject
            has_trigger = any(trigger in text for trigger in triggers)
            has_subject = any(subject in text for subject in subjects)
            
            if has_trigger and has_subject:
                return True
        
        return False
    
    async def _handle_system_command(self, text: str) -> Optional[str]:
        """Handle system commands like stop, exit"""
        if "stop" in text.lower():
            return "Returning to wake mode, mortal."
        return None
    
    async def _handle_transcription_command(self, text: str) -> Optional[str]:
        """Handle transcription commands"""
        if not self.transcription:
            return "Transcription commands are not available, mortal."
        
        try:
            from .evil_transcription_commands import process_evil_transcription_command
            return await process_evil_transcription_command(text)
        except Exception as e:
            logger.error(f"Transcription command failed: {e}")
            return None
    
    async def _handle_smart_home_command(self, text: str) -> Optional[str]:
        """Handle smart home commands"""
        try:
            return await self.smart_home.process_command(text)
        except Exception as e:
            logger.error(f"Smart home command failed: {e}")
            return None
    
    async def _handle_ai_command(self, text: str) -> str:
        """Handle AI queries (always returns a response)"""
        try:
            return self.ai.get_ai_response(text)
        except Exception as e:
            logger.error(f"AI command failed: {e}")
            return "My dark powers are temporarily weakened, mortal. Try again."
    
    def get_command_help(self) -> str:
        """Get help text for available commands"""
        help_text = "🔥 Available Commands:\n\n"
        
        if self.transcription:
            help_text += "🎧 Transcription:\n"
            help_text += "  • 'Start recording' - Begin surveillance\n"
            help_text += "  • 'Stop recording' - End surveillance\n"
            help_text += "  • 'Who spoke today?' - Speaker information\n"
            help_text += "  • 'What did someone say about lights?' - Search transcripts\n"
            help_text += "  • 'Recent activity' - Recent conversations\n"
            help_text += "  • 'Stats' - Transcription statistics\n\n"
        
        help_text += "🏠 Smart Home:\n"
        help_text += "  • 'Turn on the lights' - Control lighting\n"
        help_text += "  • 'Set brightness to 50 percent' - Adjust brightness\n"
        help_text += "  • 'Make the lights red' - Change colors\n\n"
        
        help_text += "🧠 AI Queries:\n"
        help_text += "  • Ask any question for AI response\n"
        
        return help_text
