"""
Game State Manager for PoE Stats Tracker
Centralized storage for map, session, and character information
"""

class GameState:
    """Centralized state management for game-related data"""
    
    def __init__(self):
        # Map State
        self.current_map_info = None
        self.map_start_time = None
        self.map_value = 0.0
        self.map_runtime = None
        
        # Waystone Information
        self.cached_waystone_info = None
        
        # Character Information
        self.current_gear_rarity = None
        
        # Session Information (complementary to SessionManager)
        self.session_progress = None  # Cache for session progress data
        
    def update_map_info(self, map_info):
        """Update current map information"""
        self.current_map_info = map_info
    
    def start_map(self, map_start_time):
        """Mark the start of a new map"""
        self.map_start_time = map_start_time
        self.map_value = 0.0
        self.map_runtime = None
    
    def complete_map(self, map_value, map_runtime):
        """Mark map completion with value and runtime"""
        self.map_value = map_value
        self.map_runtime = map_runtime
    
    def update_waystone_info(self, waystone_info):
        """Update cached waystone information"""
        self.cached_waystone_info = waystone_info
    
    def update_gear_rarity(self, gear_rarity):
        """Update current gear rarity"""
        self.current_gear_rarity = gear_rarity
    
    def update_session_progress(self, session_progress):
        """Cache session progress for notifications"""
        self.session_progress = session_progress
    
    def get_notification_data(self):
        """Get all data needed for notifications in one dict"""
        # Calculate map-specific ex/h
        map_value_per_hour = 0.0
        if self.map_runtime and self.map_runtime > 0 and self.map_value:
            map_hours = self.map_runtime / 3600  # convert seconds to hours
            map_value_per_hour = self.map_value / map_hours
        
        return {
            # Map data
            'map_name': self.current_map_info.get('map_name') if self.current_map_info else 'Unknown Map',
            'map_level': self.current_map_info.get('level') if self.current_map_info else '?',
            'map_seed': self.current_map_info.get('seed') if self.current_map_info else '?',
            'map_value': self.map_value,
            'map_runtime': self.map_runtime,
            'map_value_per_hour': map_value_per_hour,
            
            # Waystone data
            'waystone_name': self.cached_waystone_info.get('name') if self.cached_waystone_info else 'No Waystone',
            'waystone_tier': self.cached_waystone_info.get('tier') if self.cached_waystone_info else '?',
            'waystone_prefixes': len(self.cached_waystone_info.get('prefixes', [])) if self.cached_waystone_info else 0,
            'waystone_suffixes': len(self.cached_waystone_info.get('suffixes', [])) if self.cached_waystone_info else 0,
            
            # Waystone area modifiers (extracted from area_modifiers)
            'magic_monsters': self._extract_modifier_value('magic_monsters'),
            'rare_monsters': self._extract_modifier_value('rare_monsters'),
            'item_rarity': self._extract_modifier_value('item_rarity'),
            'item_quantity': self._extract_modifier_value('item_quantity'),
            'waystone_drop_chance': self._extract_modifier_value('waystone_drop_chance'),
            'pack_size': self._extract_modifier_value('pack_size'),
            
            # Character data
            'gear_rarity': self.current_gear_rarity,
            
            # Session data (from cached progress - already calculated by SessionManager)
            'session_time': self.session_progress.get('session_time_str') if self.session_progress else 'N/A',
            'session_runtime_seconds': self.session_progress.get('runtime_seconds') if self.session_progress else 0,
            'session_maps_completed': self.session_progress.get('maps_completed') if self.session_progress else 0,
            'session_total_value': self.session_progress.get('total_value') if self.session_progress else 0.0,
            
            # Already calculated by SessionManager - avg per map values
            'session_avg_value': self.session_progress.get('avg_value') if self.session_progress else 0.0,  # ex/map
            'session_avg_time': self.session_progress.get('avg_time') if self.session_progress else 0.0,    # min/map
            
            # Calculate per hour values from existing data
            'session_maps_per_hour': (self.session_progress.get('maps_completed', 0) / (self.session_progress.get('runtime_seconds', 1) / 3600)) if self.session_progress and self.session_progress.get('runtime_seconds', 0) > 0 else 0.0,
            'session_value_per_hour': (self.session_progress.get('total_value', 0) / (self.session_progress.get('runtime_seconds', 1) / 3600)) if self.session_progress and self.session_progress.get('runtime_seconds', 0) > 0 else 0.0,
        }
    
    def reset_map_state(self):
        """Reset map-specific state"""
        self.current_map_info = None
        self.map_start_time = None
        self.map_value = 0.0
        self.map_runtime = None
    
    def _extract_modifier_value(self, modifier_key):
        """Extract numeric value from waystone area modifiers (e.g., '+70%' -> 70)"""
        if not self.cached_waystone_info:
            return 0
        
        area_modifiers = self.cached_waystone_info.get('area_modifiers', {})
        modifier = area_modifiers.get(modifier_key, {})
        value_str = modifier.get('value', '0')
        
        # Extract number from strings like '+70%' or '70%' or '70'
        import re
        numbers = re.findall(r'-?\d+', str(value_str))
        return int(numbers[0]) if numbers else 0
    
    def __str__(self):
        """String representation for debugging"""
        return (f"GameState(map={self.current_map_info.get('map_name') if self.current_map_info else None}, "
                f"session_maps={self.session_progress.get('maps_completed') if self.session_progress else 0}, "
                f"session_value={self.session_progress.get('total_value') if self.session_progress else 0.0})")