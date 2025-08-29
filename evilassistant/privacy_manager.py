#!/usr/bin/env python3
"""
Privacy Manager for Evil Assistant
Handles transcript deletion and privacy controls
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class PrivacyManager:
    """Manages privacy controls for transcripts"""
    
    def __init__(self, storage_dir: str = "transcripts"):
        self.storage_dir = storage_dir
        self.encryption_key = self._load_encryption_key()
    
    def _load_encryption_key(self) -> Optional[bytes]:
        """Load encryption key"""
        key_file = ".transcript_key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        return None
    
    def delete_all_transcripts(self) -> str:
        """Delete all transcript files"""
        try:
            if not os.path.exists(self.storage_dir):
                return "No transcripts found to delete, mortal."
            
            deleted_count = 0
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.enc'):
                    file_path = os.path.join(self.storage_dir, filename)
                    os.remove(file_path)
                    deleted_count += 1
                    logger.info(f"Deleted transcript file: {filename}")
            
            if deleted_count > 0:
                return f"Deleted {deleted_count} transcript files. Your secrets are consumed by the void!"
            else:
                return "No transcript files found to delete, mortal."
                
        except Exception as e:
            logger.error(f"Failed to delete transcripts: {e}")
            return "The dark forces protect your transcripts from deletion!"
    
    def delete_transcripts_by_date(self, date_str: str) -> str:
        """Delete transcripts for a specific date (YYYY-MM-DD)"""
        try:
            filename = f"transcripts_{date_str}.enc"
            file_path = os.path.join(self.storage_dir, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted transcript file: {filename}")
                return f"Transcripts for {date_str} have been erased from existence!"
            else:
                return f"No transcripts found for {date_str}, mortal."
                
        except Exception as e:
            logger.error(f"Failed to delete transcripts for {date_str}: {e}")
            return f"Failed to delete transcripts for {date_str}. The void resists!"
    
    def delete_transcripts_older_than(self, days: int) -> str:
        """Delete transcripts older than specified days"""
        try:
            if not os.path.exists(self.storage_dir):
                return "No transcripts found to delete, mortal."
            
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            for filename in os.listdir(self.storage_dir):
                if filename.startswith("transcripts_") and filename.endswith(".enc"):
                    try:
                        # Extract date from filename: transcripts_YYYY-MM-DD.enc
                        date_part = filename.replace("transcripts_", "").replace(".enc", "")
                        file_date = datetime.strptime(date_part, "%Y-%m-%d")
                        
                        if file_date < cutoff_date:
                            file_path = os.path.join(self.storage_dir, filename)
                            os.remove(file_path)
                            deleted_count += 1
                            logger.info(f"Deleted old transcript file: {filename}")
                            
                    except ValueError:
                        # Skip files with invalid date format
                        continue
            
            if deleted_count > 0:
                return f"Deleted {deleted_count} old transcript files. The past is erased!"
            else:
                return f"No transcripts older than {days} days found, mortal."
                
        except Exception as e:
            logger.error(f"Failed to delete old transcripts: {e}")
            return "The ancient archives resist deletion!"
    
    def delete_encryption_key(self) -> str:
        """Delete the encryption key (makes all transcripts unreadable)"""
        try:
            key_file = ".transcript_key"
            if os.path.exists(key_file):
                # Backup key first
                backup_name = f".transcript_key.deleted_{int(datetime.now().timestamp())}"
                os.rename(key_file, backup_name)
                logger.warning(f"Encryption key moved to {backup_name}")
                return "The encryption key has been destroyed! All transcripts are now unreadable forever!"
            else:
                return "No encryption key found to delete, mortal."
                
        except Exception as e:
            logger.error(f"Failed to delete encryption key: {e}")
            return "The key to the dark archives cannot be destroyed!"
    
    def get_privacy_status(self) -> str:
        """Get current privacy status"""
        try:
            if not os.path.exists(self.storage_dir):
                return "📂 No transcript storage exists - perfect privacy!"
            
            transcript_files = [f for f in os.listdir(self.storage_dir) if f.endswith('.enc')]
            
            if not transcript_files:
                return "📂 Transcript storage exists but contains no files - privacy maintained!"
            
            # Calculate total size
            total_size = 0
            for filename in transcript_files:
                file_path = os.path.join(self.storage_dir, filename)
                total_size += os.path.getsize(file_path)
            
            size_mb = total_size / (1024 * 1024)
            
            # Get date range
            dates = []
            for filename in transcript_files:
                try:
                    date_part = filename.replace("transcripts_", "").replace(".enc", "")
                    dates.append(date_part)
                except:
                    continue
            
            if dates:
                dates.sort()
                date_range = f"{dates[0]} to {dates[-1]}" if len(dates) > 1 else dates[0]
            else:
                date_range = "Unknown"
            
            status = f"🔐 {len(transcript_files)} encrypted transcript files\n"
            status += f"📅 Date range: {date_range}\n"
            status += f"💾 Total size: {size_mb:.2f} MB\n"
            status += f"🔑 Encryption key: {'Present' if self.encryption_key else 'Missing'}"
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get privacy status: {e}")
            return "🚫 Unable to determine privacy status!"

def get_privacy_manager() -> PrivacyManager:
    """Get singleton privacy manager"""
    return PrivacyManager()
