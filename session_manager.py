"""
Session management for PoE Stats Tracker
Handles session lifecycle, tracking, and statistics
"""

import time
import uuid
from pathlib import Path
from poe_logging import log_session_start, log_session_end, get_session_stats


class SessionManager:
    """Manages tracking sessions and statistics"""
    
    def __init__(self, character_name, session_log_file=None):
        self.character_name = character_name
        self.session_log_file = session_log_file
        
        # Session state
        self.session_id = None
        self.session_start_time = None
        self.session_maps_completed = 0
        self.session_total_value = 0.0
    
    def start_new_session(self):
        """Start a new tracking session"""
        # Log end of previous session if it exists
        if self.session_id and self.session_maps_completed > 0:
            self.end_current_session()
        
        # Initialize new session
        self.session_id = str(uuid.uuid4())
        self.session_start_time = time.time()
        self.session_maps_completed = 0
        self.session_total_value = 0.0
        
        # Log session start
        log_session_start(self.session_id, self.character_name, self.session_log_file)
        
        return {
            'session_id': self.session_id,
            'start_time': self.session_start_time,
            'start_time_str': time.strftime("%H:%M:%S", time.localtime(self.session_start_time))
        }
    
    def end_current_session(self):
        """End the current session and log statistics"""
        if not self.session_id:
            return None
        
        session_runtime = time.time() - self.session_start_time
        log_session_end(
            self.session_id, 
            self.character_name, 
            session_runtime,
            self.session_total_value, 
            self.session_maps_completed, 
            self.session_log_file
        )
        
        return {
            'session_id': self.session_id,
            'runtime': session_runtime,
            'maps_completed': self.session_maps_completed,
            'total_value': self.session_total_value
        }
    
    def add_completed_map(self, map_value=None):
        """Record a completed map with optional value"""
        self.session_maps_completed += 1
        if map_value and map_value > 0:
            self.session_total_value += map_value
    
    def get_current_session_stats(self, runs_log_file=None):
        """Get detailed statistics for the current session"""
        if not self.session_id:
            return None
        
        # Calculate runtime
        current_time = time.time()
        session_runtime = current_time - self.session_start_time
        hours = int(session_runtime // 3600)
        minutes = int((session_runtime % 3600) // 60)
        seconds = int(session_runtime % 60)
        
        # Get detailed session stats from log
        session_stats = get_session_stats(self.session_id, runs_log_file)
        
        return {
            'session_id': self.session_id,
            'runtime': {
                'total_seconds': session_runtime,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds
            },
            'maps_completed': self.session_maps_completed,
            'total_value': self.session_total_value,
            'detailed_stats': session_stats
        }
    
    def get_session_progress(self):
        """Get current session progress for display"""
        if not self.session_id:
            return None
        
        current_time = time.time()
        session_runtime = current_time - self.session_start_time
        hours = int(session_runtime // 3600)
        minutes = int((session_runtime % 3600) // 60)
        
        session_time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        result = {
            'session_time_str': session_time_str,
            'maps_completed': self.session_maps_completed,
            'total_value': self.session_total_value,
            'runtime_seconds': session_runtime
        }
        
        # Calculate averages if we have completed maps
        if self.session_maps_completed > 0:
            result['avg_value'] = self.session_total_value / self.session_maps_completed
            result['avg_time'] = session_runtime / self.session_maps_completed / 60  # in minutes
        
        return result
    
    def get_session_info(self):
        """Get basic session information"""
        return {
            'session_id': self.session_id,
            'start_time': self.session_start_time,
            'maps_completed': self.session_maps_completed,
            'total_value': self.session_total_value
        }
    
    def is_session_active(self):
        """Check if a session is currently active"""
        return self.session_id is not None