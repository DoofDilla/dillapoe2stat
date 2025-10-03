"""
Notification Templates for PoE Stats Tracker
Centralized template definitions for consistent notifications
"""

class NotificationTemplates:
    """Template definitions for all notification types"""
    
    # Startup Templates
    STARTUP = {
        'title': '🎮 DillaPoE2Stat Started!',
        'template': (
            '🎮 Character: {character}\n'
            '🆔 Session: {session_id_short}...\n'
            '⌨️ F2=PRE | F3=POST | F5=Inventory\n'
            '✅ Ready! Press F2 to start mapping'
        )
    }
    
    NEW_SESSION = {
        'title': '🚀 New Session Started!',
        'template': (
            '🚀 Character: {character}\n'
            '🆔 ID: {session_id_short}...\n'
            '🕐 Started: {start_time}\n'
            '✅ New session ready!'
        )
    }
    
    # Map Templates
    PRE_MAP = {
        'title': '🗺️ Starting Map Run!',
        'template': (
            '🗺️ {map_name}\n'
            '⏰ Session: {session_time} | 🗺️ Maps: {session_maps_completed}\n'
            '💰 Session Value: {session_total_value_fmt}ex\n'
            '🚀 Starting new map run!'
        )
    }
    
    POST_MAP = {
        'title': '✅ Map Completed!',
        'template': (
            '🗺️ {map_name}\n'
            '⏱️ Runtime: {map_runtime_fmt} | 💰 Value: {map_value_fmt}ex\n'
            '⏰ Session: {session_time} | 💰 Session Value: {session_total_value_fmt}ex\n'
            '✅ Map completed!'
        )
    }
    
    # Experimental/Waystone Templates
    EXPERIMENTAL_PRE_MAP = {
        'title': '🧪 Experimental Map Run!',
        'template': (
            '🧪 {waystone_name} (T{waystone_tier})\n'
            '⚗️ Prefixes: {waystone_prefixes} | 🔮 Suffixes: {waystone_suffixes}\n'
            '🗺️ Maps: {session_maps_completed} | ⏰ Session: {session_time}\n'
            '🚀 Experimental mode activated!'
        )
    }
    
    # Inventory Templates
    INVENTORY_CHECK = {
        'title': '💼 Inventory Check',
        'template': (
            '💼 {total_items} items scanned\n'
            '💎 {valuable_items} valuable items found\n'
            '💰 Total Value: {inventory_value}\n'
            '✅ Inventory check complete!'
        )
    }
    
    # Generic Templates
    INFO = {
        'title': '{title}',
        'template': '{message}'
    }
    
    # High Value Loot Template (neue Idee)
    HIGH_VALUE_LOOT = {
        'title': '💎 Valuable Loot Found!',
        'template': (
            '💎 {item_name}\n'
            '💰 Value: {item_value}ex\n'
            '🗺️ Map: {map_name}\n'
            '🎉 Great find!'
        )
    }
    
    # Milestone Templates (neue Idee)
    SESSION_MILESTONE = {
        'title': '🎯 Session Milestone!',
        'template': (
            '🎯 {milestone_type}: {milestone_value}\n'
            '⏰ Session Time: {session_time}\n'
            '🗺️ Maps Completed: {session_maps_completed}\n'
            '🏆 Keep it up!'
        )
    }