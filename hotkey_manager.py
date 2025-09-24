"""
Hotkey management for PoE Stats Tracker
Handles keyboard shortcuts and their bindings
"""

import keyboard


class HotkeyManager:
    """Manages keyboard hotkeys and their associated actions"""
    
    def __init__(self):
        self.hotkeys = {}
        self.registered_keys = []
    
    def register_hotkey(self, key, callback, description=""):
        """
        Register a hotkey with its callback function
        
        Args:
            key: Key combination (e.g., 'f2', 'ctrl+esc')
            callback: Function to call when hotkey is pressed
            description: Optional description for the hotkey
        """
        try:
            keyboard.add_hotkey(key, callback)
            self.hotkeys[key] = {
                'callback': callback,
                'description': description
            }
            self.registered_keys.append(key)
            return True
        except Exception as e:
            print(f"Failed to register hotkey {key}: {e}")
            return False
    
    def unregister_hotkey(self, key):
        """Unregister a specific hotkey"""
        try:
            keyboard.remove_hotkey(key)
            if key in self.hotkeys:
                del self.hotkeys[key]
            if key in self.registered_keys:
                self.registered_keys.remove(key)
            return True
        except Exception as e:
            print(f"Failed to unregister hotkey {key}: {e}")
            return False
    
    def unregister_all(self):
        """Unregister all hotkeys"""
        for key in self.registered_keys.copy():
            self.unregister_hotkey(key)
    
    def get_hotkey_info(self):
        """Get information about registered hotkeys"""
        return self.hotkeys.copy()
    
    def wait_for_exit_key(self, exit_key='ctrl+esc'):
        """Wait for the specified exit key combination"""
        try:
            keyboard.wait(exit_key)
        except KeyboardInterrupt:
            pass
    
    def setup_default_hotkeys(self, tracker_instance):
        """
        Setup the default hotkeys for the PoE Stats Tracker
        
        Args:
            tracker_instance: The PoEStatsTracker instance to bind callbacks to
        """
        hotkey_mappings = [
            ('f2', tracker_instance.take_pre_snapshot, 'Take PRE-map snapshot'),
            ('f3', tracker_instance.take_post_snapshot, 'Take POST-map snapshot'),
            ('f4', tracker_instance.toggle_debug_mode, 'Toggle debug mode'),
            ('f5', tracker_instance.check_current_inventory_value, 'Check current inventory value'),
            ('f6', tracker_instance.start_new_session, 'Start new session'),
            ('f7', tracker_instance.display_session_stats, 'Display session stats'),
            ('f8', tracker_instance.toggle_output_mode, 'Toggle output mode'),
        ]
        
        successful_registrations = 0
        for key, callback, description in hotkey_mappings:
            if self.register_hotkey(key, callback, description):
                successful_registrations += 1
        
        return successful_registrations == len(hotkey_mappings)
    
    def list_active_hotkeys(self):
        """Return a formatted string of active hotkeys"""
        if not self.hotkeys:
            return "No hotkeys registered"
        
        hotkey_list = []
        for key, info in self.hotkeys.items():
            desc = info.get('description', 'No description')
            hotkey_list.append(f"{key.upper()}: {desc}")
        
        return " | ".join(hotkey_list)
    
    def is_key_registered(self, key):
        """Check if a specific key is already registered"""
        return key in self.registered_keys