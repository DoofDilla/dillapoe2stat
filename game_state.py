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
        self.current_map_top_drops = []  # Top drops for current/just completed map
        
        # Waystone Information
        self.cached_waystone_info = None
        
        # Character Information
        self.current_gear_rarity = None
        
        # Session Information (complementary to SessionManager)
        self.session_progress = None  # Cache for session progress data
        
        # Last completed map (set at POST-map)
        self.last_map_info = None  # {name, tier, value, runtime, top_drops}
        
        # Best map in session (updated at POST-map)
        self.best_map_info = None  # {name, tier, value, runtime}
        
        # Session cumulative top drops (updated at POST-map)
        self.session_top_drops = []  # [{name, stack, value_ex}, ...]
        
    def update_map_info(self, map_info):
        """Update current map information"""
        self.current_map_info = map_info
    
    def start_map(self, map_start_time):
        """Mark the start of a new map"""
        self.map_start_time = map_start_time
        self.map_value = 0.0
        self.map_runtime = None
        self.current_map_top_drops = []  # Reset for new map
    
    def complete_map(self, map_value, map_runtime):
        """Mark map completion with value and runtime"""
        self.map_value = map_value
        self.map_runtime = map_runtime
    
    def reset_current_map(self):
        """Reset current map state after POST (map is completed, data moved to last_map_info)"""
        self.current_map_info = None
        self.map_start_time = None
        self.map_value = 0.0
        self.map_runtime = None
        self.current_map_top_drops = []
        # Note: cached_waystone_info stays until next Ctrl+F2 (user might check same waystone again)
    
    def update_waystone_info(self, waystone_info):
        """Update cached waystone information"""
        self.cached_waystone_info = waystone_info
    
    def update_gear_rarity(self, gear_rarity):
        """Update current gear rarity"""
        self.current_gear_rarity = gear_rarity
    
    def update_session_progress(self, session_progress):
        """Cache session progress for notifications"""
        self.session_progress = session_progress
    
    def update_map_completion(self, added_items_with_values):
        """Update last map, best map, and top drops after POST-map
        
        Args:
            added_items_with_values: List of items with value data from valuate_items_raw
        """
        if not self.current_map_info:
            return
        
        # Calculate top 3 drops for this map
        self.current_map_top_drops = self._calculate_top_drops(added_items_with_values)
        
        # Update last_map_info (this map becomes "last map")
        self.last_map_info = {
            'name': self.current_map_info.get('map_name', 'Unknown'),
            'tier': self.current_map_info.get('level', '?'),
            'value': self.map_value,
            'runtime': self.map_runtime,
            'top_drops': self.current_map_top_drops  # Top 3 of this specific map
        }
        
        # Update best_map_info if this map is better
        if not self.best_map_info or self.map_value > self.best_map_info.get('value', 0):
            self.best_map_info = {
                'name': self.current_map_info.get('map_name', 'Unknown'),
                'tier': self.current_map_info.get('level', '?'),
                'value': self.map_value,
                'runtime': self.map_runtime
            }
        
        # Update session_top_drops (cumulative - merge with existing)
        self._update_session_top_drops(self.current_map_top_drops)
    
    def _calculate_top_drops(self, items_with_values):
        """Calculate top 3 most valuable items from a list
        
        Args:
            items_with_values: List of items with total_value_exalted field
            
        Returns:
            List of top 3 items as {name, stack, value_ex} dicts
        """
        # Filter items with value > 0 and sort by total exalted value
        valuable_items = [
            item for item in items_with_values
            if item.get('total_value_exalted', 0) > 0
        ]
        
        sorted_items = sorted(
            valuable_items,
            key=lambda x: x.get('total_value_exalted', 0),
            reverse=True
        )
        
        # Take top 3 and create simplified format
        return [
            {
                'name': item.get('name', 'Unknown'),
                'stack': item.get('qty', 1),
                'value_ex': item.get('total_value_exalted', 0)
            }
            for item in sorted_items[:3]
        ]
    
    def _update_session_top_drops(self, new_drops):
        """Merge new drops with existing session top drops and keep top 3
        
        Args:
            new_drops: List of top drops from current map
        """
        # Merge all session drops (existing + new)
        all_drops = self.session_top_drops + new_drops
        
        # Re-sort by value and take top 3
        self.session_top_drops = sorted(
            all_drops,
            key=lambda x: x['value_ex'],
            reverse=True
        )[:3]
    
    def reset_session_tracking(self):
        """Reset session-specific tracking (call when new session starts)"""
        self.last_map_info = None
        self.best_map_info = None
        self.session_top_drops = []
    
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
            
            # Current Map Top Drops (top 3 items from current/just completed map)
            'map_drop_1_name': self.current_map_top_drops[0]['name'] if len(self.current_map_top_drops) > 0 else 'None',
            'map_drop_1_stack': self.current_map_top_drops[0]['stack'] if len(self.current_map_top_drops) > 0 else 0,
            'map_drop_1_value': self.current_map_top_drops[0]['value_ex'] if len(self.current_map_top_drops) > 0 else 0.0,
            'map_drop_2_name': self.current_map_top_drops[1]['name'] if len(self.current_map_top_drops) > 1 else 'None',
            'map_drop_2_stack': self.current_map_top_drops[1]['stack'] if len(self.current_map_top_drops) > 1 else 0,
            'map_drop_2_value': self.current_map_top_drops[1]['value_ex'] if len(self.current_map_top_drops) > 1 else 0.0,
            'map_drop_3_name': self.current_map_top_drops[2]['name'] if len(self.current_map_top_drops) > 2 else 'None',
            'map_drop_3_stack': self.current_map_top_drops[2]['stack'] if len(self.current_map_top_drops) > 2 else 0,
            'map_drop_3_value': self.current_map_top_drops[2]['value_ex'] if len(self.current_map_top_drops) > 2 else 0.0,
            
            # Waystone data
            'waystone_name': self.cached_waystone_info.get('name') if self.cached_waystone_info else 'No Waystone',
            'waystone_tier': self.cached_waystone_info.get('tier') if self.cached_waystone_info else '?',
            'waystone_prefixes': len(self.cached_waystone_info.get('prefixes', [])) if self.cached_waystone_info else 0,
            'waystone_suffixes': len(self.cached_waystone_info.get('suffixes', [])) if self.cached_waystone_info else 0,
            'waystone_delirious': self.cached_waystone_info.get('delirious', 0) if self.cached_waystone_info else 0,
            
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
            
            # Session ex/h BEFORE current map (for comparison) - stored separately
            'session_value_per_hour_before': getattr(self, '_session_value_per_hour_before', 0.0),
            
            # Last map data (previous completed map)
            'last_map_name': self.last_map_info['name'] if self.last_map_info else 'None',
            'last_map_tier': self.last_map_info['tier'] if self.last_map_info else '?',
            'last_map_value': self.last_map_info['value'] if self.last_map_info else 0,
            'last_map_runtime': self.last_map_info['runtime'] if self.last_map_info else 0,
            
            # Last map top 3 drops
            'last_map_drop_1_name': self.last_map_info['top_drops'][0]['name'] if self.last_map_info and len(self.last_map_info.get('top_drops', [])) > 0 else '',
            'last_map_drop_1_stack': self.last_map_info['top_drops'][0]['stack'] if self.last_map_info and len(self.last_map_info.get('top_drops', [])) > 0 else 0,
            'last_map_drop_1_value': self.last_map_info['top_drops'][0]['value_ex'] if self.last_map_info and len(self.last_map_info.get('top_drops', [])) > 0 else 0,
            
            'last_map_drop_2_name': self.last_map_info['top_drops'][1]['name'] if self.last_map_info and len(self.last_map_info.get('top_drops', [])) > 1 else '',
            'last_map_drop_2_stack': self.last_map_info['top_drops'][1]['stack'] if self.last_map_info and len(self.last_map_info.get('top_drops', [])) > 1 else 0,
            'last_map_drop_2_value': self.last_map_info['top_drops'][1]['value_ex'] if self.last_map_info and len(self.last_map_info.get('top_drops', [])) > 1 else 0,
            
            'last_map_drop_3_name': self.last_map_info['top_drops'][2]['name'] if self.last_map_info and len(self.last_map_info.get('top_drops', [])) > 2 else '',
            'last_map_drop_3_stack': self.last_map_info['top_drops'][2]['stack'] if self.last_map_info and len(self.last_map_info.get('top_drops', [])) > 2 else 0,
            'last_map_drop_3_value': self.last_map_info['top_drops'][2]['value_ex'] if self.last_map_info and len(self.last_map_info.get('top_drops', [])) > 2 else 0,
            
            # Best map in session
            'best_map_name': self.best_map_info['name'] if self.best_map_info else 'None',
            'best_map_tier': self.best_map_info['tier'] if self.best_map_info else '?',
            'best_map_value': self.best_map_info['value'] if self.best_map_info else 0,
            'best_map_runtime': self.best_map_info['runtime'] if self.best_map_info else 0,
            
            # Session top 3 drops (cumulative best)
            'session_drop_1_name': self.session_top_drops[0]['name'] if len(self.session_top_drops) > 0 else '',
            'session_drop_1_stack': self.session_top_drops[0]['stack'] if len(self.session_top_drops) > 0 else 0,
            'session_drop_1_value': self.session_top_drops[0]['value_ex'] if len(self.session_top_drops) > 0 else 0,
            
            'session_drop_2_name': self.session_top_drops[1]['name'] if len(self.session_top_drops) > 1 else '',
            'session_drop_2_stack': self.session_top_drops[1]['stack'] if len(self.session_top_drops) > 1 else 0,
            'session_drop_2_value': self.session_top_drops[1]['value_ex'] if len(self.session_top_drops) > 1 else 0,
            
            'session_drop_3_name': self.session_top_drops[2]['name'] if len(self.session_top_drops) > 2 else '',
            'session_drop_3_stack': self.session_top_drops[2]['stack'] if len(self.session_top_drops) > 2 else 0,
            'session_drop_3_value': self.session_top_drops[2]['value_ex'] if len(self.session_top_drops) > 2 else 0,
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