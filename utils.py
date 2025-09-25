"""
Utility functions for PoE Stats Tracker
Common helper functions used across modules
"""

import time


def format_time(seconds):
    """
    Format seconds into a readable time string
    
    Args:
        seconds: Time in seconds (float or int)
    
    Returns:
        str: Formatted time string like "1h 23m" or "5m 42s"
    """
    if seconds is None:
        return "N/A"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m {secs}s"


def get_current_timestamp():
    """Get current timestamp as float"""
    return time.time()


def validate_inventory_position(item, x=0, y=0):
    """
    Check if an item is at a specific inventory position
    
    Args:
        item: Item dictionary from API
        x: X coordinate (default 0)
        y: Y coordinate (default 0)
    
    Returns:
        bool: True if item is at specified position
    """
    return item.get('x') == x and item.get('y') == y


def extract_tier_from_typeline(type_line):
    """
    Extract tier number from typeLine string
    
    Args:
        type_line: String like "Waystone (Tier 15)"
    
    Returns:
        str: Tier number or "Unknown"
    """
    if not type_line or 'Tier' not in type_line:
        return "Unknown"
    
    import re
    tier_match = re.search(r'Tier (\d+)', type_line)
    return tier_match.group(1) if tier_match else "Unknown"


def clean_mod_text(mod):
    """
    Clean and validate mod text
    
    Args:
        mod: Raw mod string
    
    Returns:
        str or None: Cleaned mod text or None if invalid
    """
    if not mod:
        return None
    
    clean_mod = mod.strip()
    return clean_mod if clean_mod else None


def create_empty_map_info(source="unknown"):
    """
    Create an empty map info structure
    
    Args:
        source: Source identifier for the map info
    
    Returns:
        dict: Empty map info structure
    """
    return {
        'map_name': 'Unknown',
        'level': 'Unknown',
        'prefixes': [],
        'suffixes': [],
        'area_modifiers': {},
        'source': source,
        'seed': 'unknown'
    }


def safe_get_nested_value(data, keys, default=None):
    """
    Safely get nested dictionary value
    
    Args:
        data: Dictionary to search
        keys: List of keys to traverse
        default: Default value if key not found
    
    Returns:
        Any: Value at nested key or default
    """
    current = data
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError, IndexError):
        return default