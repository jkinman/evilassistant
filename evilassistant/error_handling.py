#!/usr/bin/env python3
"""
Centralized Error Handling for Evil Assistant
"""

import logging
import traceback
from typing import Optional, Callable, Any
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

class EvilAssistantError(Exception):
    """Base exception for Evil Assistant"""
    def __init__(self, message: str, evil_response: str = None):
        super().__init__(message)
        self.evil_response = evil_response or "My dark powers have encountered an unexpected disturbance, mortal!"

class AudioError(EvilAssistantError):
    """Audio processing errors"""
    def __init__(self, message: str):
        super().__init__(message, "The voices in the digital realm are corrupted, mortal!")

class TranscriptionError(EvilAssistantError):
    """Transcription errors"""
    def __init__(self, message: str):
        super().__init__(message, "The ancient scripts resist transcription, mortal!")

class SmartHomeError(EvilAssistantError):
    """Smart home control errors"""
    def __init__(self, message: str):
        super().__init__(message, "My powers over the physical realm are temporarily weakened, mortal!")

class APIError(EvilAssistantError):
    """External API errors"""
    def __init__(self, message: str, service: str = ""):
        evil_msg = f"The {service} spirits are in rebellion, mortal!" if service else "External forces resist my commands!"
        super().__init__(message, evil_msg)

def evil_error_handler(
    fallback_response: str = None,
    log_level: int = logging.ERROR,
    reraise: bool = False
):
    """
    Decorator for handling errors with evil responses
    
    Args:
        fallback_response: Default evil response if none provided
        log_level: Logging level for errors
        reraise: Whether to reraise the exception after handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except EvilAssistantError as e:
                logger.log(log_level, f"Evil Assistant error in {func.__name__}: {e}")
                if reraise:
                    raise
                return e.evil_response
            except Exception as e:
                logger.log(log_level, f"Unexpected error in {func.__name__}: {e}")
                logger.debug(f"Traceback: {traceback.format_exc()}")
                
                if reraise:
                    raise
                
                return fallback_response or "The dark forces are in chaos, mortal! Try again."
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except EvilAssistantError as e:
                logger.log(log_level, f"Evil Assistant error in {func.__name__}: {e}")
                if reraise:
                    raise
                return e.evil_response
            except Exception as e:
                logger.log(log_level, f"Unexpected error in {func.__name__}: {e}")
                logger.debug(f"Traceback: {traceback.format_exc()}")
                
                if reraise:
                    raise
                
                return fallback_response or "The dark forces are in chaos, mortal! Try again."
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def safe_import(module_name: str, fallback_msg: str = None) -> tuple[bool, Optional[Any]]:
    """
    Safely import a module with evil messaging
    
    Returns:
        (success: bool, module: Optional[Any])
    """
    try:
        import importlib
        module = importlib.import_module(module_name)
        return True, module
    except ImportError as e:
        msg = fallback_msg or f"The {module_name} spirits are not present in this realm!"
        logger.warning(f"Failed to import {module_name}: {e}")
        return False, None
    except Exception as e:
        logger.error(f"Unexpected import error for {module_name}: {e}")
        return False, None

def validate_environment() -> list[str]:
    """
    Validate environment and return list of issues
    """
    issues = []
    
    # Check required environment variables
    import os
    required_vars = ["XAI_API_KEY"]
    optional_vars = ["ELEVENLABS_API_KEY", "PHILIPS_HUE_BRIDGE_IP", "HOME_ASSISTANT_TOKEN"]
    
    for var in required_vars:
        if not os.getenv(var):
            issues.append(f"Missing required environment variable: {var}")
    
    missing_optional = [var for var in optional_vars if not os.getenv(var)]
    if missing_optional:
        issues.append(f"Optional features disabled due to missing vars: {', '.join(missing_optional)}")
    
    # Check critical imports
    critical_modules = [
        ("numpy", "NumPy"),
        ("sounddevice", "SoundDevice"), 
        ("faster_whisper", "Faster-Whisper"),
    ]
    
    for module_name, display_name in critical_modules:
        success, _ = safe_import(module_name)
        if not success:
            issues.append(f"Critical dependency missing: {display_name}")
    
    return issues

class ResourceTracker:
    """Track and cleanup resources"""
    
    def __init__(self):
        self._resources = set()
        self._cleanup_functions = {}
    
    def track_resource(self, resource_id: str, cleanup_func: Callable):
        """Track a resource for cleanup"""
        self._resources.add(resource_id)
        self._cleanup_functions[resource_id] = cleanup_func
        logger.debug(f"Tracking resource: {resource_id}")
    
    def cleanup_resource(self, resource_id: str):
        """Clean up a specific resource"""
        if resource_id in self._resources:
            try:
                cleanup_func = self._cleanup_functions[resource_id]
                cleanup_func()
                self._resources.remove(resource_id)
                del self._cleanup_functions[resource_id]
                logger.debug(f"Cleaned up resource: {resource_id}")
            except Exception as e:
                logger.error(f"Failed to cleanup resource {resource_id}: {e}")
    
    def cleanup_all(self):
        """Clean up all tracked resources"""
        for resource_id in list(self._resources):
            self.cleanup_resource(resource_id)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_all()

# Global resource tracker
_resource_tracker = ResourceTracker()

def get_resource_tracker() -> ResourceTracker:
    """Get global resource tracker"""
    return _resource_tracker
