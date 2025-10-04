"""
Notification Templates for PoE Stats Tracker
Centralized template definitions for consistent notifications

Available template variables:
==========================

MAP DATA:
- map_name: Name of the current map (e.g. "Grimhaven")
- map_level: Map level (e.g. "80")
- map_seed: Map seed number (e.g. "1234567")
- map_value: Exalted value of this map (number)
- map_runtime: Map runtime in seconds (number)
- map_value_per_hour: This map's ex/h rate (number)
- map_value_fmt: Formatted map value (e.g. "67")
- map_runtime_fmt: Formatted runtime (e.g. "4m32s")
- map_value_per_hour_fmt: Formatted map ex/h (e.g. "1440")

WAYSTONE DATA:
- waystone_name: Waystone name (e.g. "Grimhaven Waystone")
- waystone_tier: Waystone tier (e.g. "15")
- waystone_prefixes: Number of prefix modifiers (number)
- waystone_suffixes: Number of suffix modifiers (number)
- magic_monsters: Magic monsters % modifier (number, e.g. 70)
- rare_monsters: Rare monsters % modifier (number, e.g. 45)
- item_rarity: Item rarity % modifier (number, e.g. 89)
- item_quantity: Item quantity % modifier (number, e.g. 25)
- waystone_drop_chance: Waystone drop chance % modifier (number, e.g. 105)
- pack_size: Pack size % modifier (number, e.g. 15)

CHARACTER DATA:
- gear_rarity: Character's total gear rarity % (number)

SESSION DATA:
- session_time: Session time string (e.g. "1h 30m")
- session_runtime_seconds: Session runtime in seconds (number)
- session_maps_completed: Number of maps completed (number)
- session_total_value: Total session value in ex (number)
- session_avg_value: Average ex per map (number)
- session_avg_time: Average minutes per map (number)
- session_maps_per_hour: Session maps/hour rate (number)  
- session_value_per_hour: Session ex/hour rate (number)

FORMATTED SESSION DATA:
- session_total_value_fmt: Formatted total value (e.g. "740")
- session_avg_value_fmt: Formatted avg ex/map (e.g. "61.7")
- session_avg_time_fmt: Formatted avg time/map (e.g. "5m0s")
- session_maps_per_hour_fmt: Formatted maps/h (e.g. "12.0")
- session_value_per_hour_fmt: Formatted ex/h (e.g. "740")

OTHER:
- character: Character name
- session_id_short: Short session ID (8 chars)
- start_time: Session start time string
- title: Generic title for INFO template
- message: Generic message for INFO template
"""

class NotificationTemplates:
    """Template definitions for all notification types"""
    
    # Currency Display Configuration
    # Change these to customize how currency is displayed in notifications
    CURRENCY_ICON = '💰'  # Options: '💰', 'ex', '🪙', '💎', etc.
    CURRENCY_SUFFIX = ''  # Optional suffix like 'ex' or 'exalted'
    
    # Startup Templates
    STARTUP = {
        'title': '🐰 BoneBunnyStats Started!',
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
        'title': '🚀 {map_name} ◉ {map_level}',
        'template': (
            'Session: {session_maps_completed} ● {session_total_value_fmt}{currency_icon} ● {session_value_per_hour_fmt}{currency_icon}/h\n'
            '⚡ Starting new map run!'
        )
    }
    
    POST_MAP = {
        'title': '🏁 {map_name} ◉ {map_level} ◉ {map_runtime_fmt} ◉ {map_value_fmt}{currency_icon}',
        'template': (
            'Session: {session_maps_completed} ● {session_total_value_fmt}{currency_icon} ● {session_value_per_hour_fmt}{currency_icon}/h\n'
            'Map: {map_value_per_hour_fmt}{currency_icon}/h 📈 Avg: {session_avg_value_fmt}{currency_icon}/map\n'
            '✅ Map completed!'
        )
    }
    
    # Experimental/Waystone Templates
    EXPERIMENTAL_PRE_MAP = {
        'title': '🗺️ {waystone_name} ◉ (T{waystone_tier})',
        'template': (
            '⚗️ Prefixes: {waystone_prefixes} ● 🔮 Suffixes: {waystone_suffixes}\n'
            '◯ Pack {pack_size}% ◯ Magic {magic_monsters}% ◯ Way {waystone_rarity}%\n'
            '◯ Rare {rare_monsters}% ◯ Rarity {item_rarity}%\n'
        )
    }
    
    # Inventory Templates
    INVENTORY_CHECK = {
        'title': '💼 {total_items} items ◉ {inventory_value}{currency_icon}',
        'template': (
            '💎 {valuable_items} valuable items found\n'
            '✅ Inventory scan complete!'
        )
    }
    
    # Generic Templates
    INFO = {
        'title': '{title}',
        'template': '{message}'
    }
    
    # High Value Loot Template (neue Idee)
    HIGH_VALUE_LOOT = {
        'title': '💎 {item_name} • +{item_value}{currency_icon}',
        'template': (
            '🗺️ {map_name}\n'
            '🎉 Great find!'
        )
    }
    
    # Milestone Templates (neue Idee)
    SESSION_MILESTONE = {
        'title': '🎯 {milestone_type}: {milestone_value}',
        'template': (
            '📊 Session: {session_maps_completed} • {session_total_value_fmt}c • {session_time}\n'
            '🏆 Keep it up!'
        )
    }