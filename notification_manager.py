"""
Notification Manager for PoE Stats Tracker
Handles all toast notifications in one centralized place
"""

from win11toast import notify
from price_check_poe2 import fmt


class NotificationManager:
    """Manages all toast notifications for the PoE Stats Tracker"""
    
    def __init__(self, config):
        self.config = config
    
    def _format_time(self, seconds):
        """Format seconds into a readable time string"""
        if seconds is None:
            return "N/A"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {secs}s"
    
    def _get_icon_path(self):
        """Get the notification icon path"""
        return f'file://{self.config.get_icon_path()}'
    
    def notify_startup(self, session_info):
        """Create notification for application startup"""
        if not self.config.NOTIFICATION_ENABLED:
            return
        
        session_id_short = session_info["session_id"][:8]
        
        notification_msg = (f"🎮 Character: {self.config.CHAR_TO_CHECK}\n"
                           f"🆔 Session: {session_id_short}...\n"
                           f"⌨️ F2=PRE | F3=POST | F5=Inventory\n"
                           f"✅ Ready! Press F2 to start mapping")
        
        notify('DillaPoE2Stat Started!', notification_msg, icon=self._get_icon_path())
    
    def notify_pre_map(self, map_info, session_progress):
        """Create notification for PRE-map snapshot"""
        if not self.config.NOTIFICATION_ENABLED:
            return
        
        map_name = map_info["map_name"] if map_info else "Unknown Map"
        session_time = self._format_time(session_progress['runtime_seconds']) if session_progress else "N/A"
        session_value = fmt(session_progress['total_value']) if session_progress else "0"
        maps_completed = session_progress['maps_completed'] if session_progress else 0
        
        notification_msg = (f"🗺️ {map_name}\n"
                           f"⏰ Session: {session_time} | 🗺️ Maps: {maps_completed}\n"
                           f"💰 Session Value: {session_value}ex\n"
                           f"🚀 Starting new map run!")
        
        notify('Starting Map Run!', notification_msg, icon=self._get_icon_path())
    
    def notify_post_map(self, map_info, map_runtime, map_value, session_progress):
        """Create notification for POST-map completion"""
        if not self.config.NOTIFICATION_ENABLED:
            return
        
        map_name = map_info["map_name"] if map_info else "Unknown Map"
        map_time = self._format_time(map_runtime)
        map_val = fmt(map_value) if map_value and map_value > 0.01 else "0"
        session_time = self._format_time(session_progress['runtime_seconds']) if session_progress else "N/A"
        session_value = fmt(session_progress['total_value']) if session_progress else "0"
        
        notification_msg = (f"🗺️ {map_name}\n"
                           f"⏱️ Runtime: {map_time} | 💰 Value: {map_val}ex\n"
                           f"⏰ Session: {session_time} | 💰 Session Value: {session_value}ex\n"
                           f"✅ Map completed!")
        
        notify('Map Completed!', notification_msg, icon=self._get_icon_path())
    
    def notify_experimental_pre_map(self, waystone_info, session_progress):
        """Create notification for experimental PRE-map snapshot"""
        if not self.config.NOTIFICATION_ENABLED:
            return
        
        if waystone_info:
            map_name = waystone_info['name']
            tier = waystone_info['tier']
            prefix_count = len(waystone_info['prefixes'])
            suffix_count = len(waystone_info['suffixes'])
        else:
            map_name = "No Waystone"
            tier = "?"
            prefix_count = 0
            suffix_count = 0
        
        session_time = self._format_time(session_progress['runtime_seconds']) if session_progress else "N/A"
        maps_completed = session_progress['maps_completed'] if session_progress else 0
        
        notification_msg = (f"🧪 {map_name} (T{tier})\n"
                           f"⚗️ Prefixes: {prefix_count} | 🔮 Suffixes: {suffix_count}\n"
                           f"🗺️ Maps: {maps_completed} | ⏰ Session: {session_time}\n"
                           f"🚀 Experimental mode activated!")
        
        notify('Experimental Map Run!', notification_msg, icon=self._get_icon_path())
    
    def notify_inventory_check(self, inventory_items):
        """Create notification for inventory check"""
        if not self.config.NOTIFICATION_ENABLED:
            return
        
        try:
            from price_check_poe2 import valuate_items_raw
            rows, (total_c, total_e) = valuate_items_raw(inventory_items)
            
            valuable_items = [r for r in rows if (r['chaos_total'] or 0) > 0.01 or (r['ex_total'] or 0) > 0.01]
            total_items = len([r for r in rows if r['qty'] > 0])
            
            if total_e and total_e > 0.01:
                value_str = f"{fmt(total_e)}ex"
            elif total_c and total_c > 0.01:
                value_str = f"{fmt(total_c)}c"
            else:
                value_str = "No valuable items"
            
            notification_msg = (f"💼 {total_items} items scanned\n"
                               f"💎 {len(valuable_items)} valuable items found\n"
                               f"💰 Total Value: {value_str}\n"
                               f"✅ Inventory check complete!")
            
            notify('Inventory Check', notification_msg, icon=self._get_icon_path())
        except Exception:
            notify('Inventory Check', 'Current inventory scanned!', icon=self._get_icon_path())
    
    def notify_session_start(self, session_info):
        """Create notification for new session start"""
        if not self.config.NOTIFICATION_ENABLED:
            return
        
        session_id_short = session_info["session_id"][:8]
        start_time = session_info["start_time_str"]
        
        notification_msg = (f"🚀 Character: {self.config.CHAR_TO_CHECK}\n"
                           f"🆔 ID: {session_id_short}...\n"
                           f"🕐 Started: {start_time}\n"
                           f"✅ New session ready!")
        
        notify('New Session Started!', notification_msg, icon=self._get_icon_path())
    
    def notify_info(self, title, message):
        """Create generic info notification"""
        if not self.config.NOTIFICATION_ENABLED:
            return
        
        notify(title, message, icon=self._get_icon_path())