# Top Drops & Best Map Tracking - Implementation Summary

## Overview
Added comprehensive tracking of top item drops and best maps to the game state system, making all data available for notifications.

## What Was Added

### GameState (game_state.py)

**New Tracking Fields:**
```python
self.current_map_top_drops = []  # Top drops for current/just completed map
self.last_map_info = None        # Last completed map with top drops
self.best_map_info = None         # Best map in session (highest value)
self.session_top_drops = []       # Cumulative top 3 drops across session
```

**New Methods:**
- `update_map_completion(added_items_with_values)` - Updates all tracking after POST-map
- `_calculate_top_drops(items)` - Calculates top 3 from item list
- `_update_session_top_drops(new_drops)` - Merges and maintains session top 3
- `reset_session_tracking()` - Resets all session-specific tracking

**New Notification Data Available:**

### Current/Just Completed Map
```python
'map_name'                # e.g. "Grimhaven"
'map_level'               # e.g. "80"
'map_value'               # Total ex value
'map_runtime'             # Runtime in seconds

# Top 3 drops from current/just completed map
'map_drop_1_name'         # e.g. "Greater Exalted Orb"
'map_drop_1_stack'        # Stack size
'map_drop_1_value'        # Value in ex
# ... _2_ and _3_ variants
```

### Last Map (Previous Completed Map)
```python
'last_map_name'           # e.g. "Necropolis"
'last_map_tier'           # e.g. "15"
'last_map_value'          # Total ex value
'last_map_runtime'        # Runtime in seconds

# Top 3 drops from last map (the one before current)
'last_map_drop_1_name'    # e.g. "Divine Orb"
'last_map_drop_1_stack'   # Stack size
'last_map_drop_1_value'   # Value in ex
# ... _2_ and _3_ variants
```

### Best Map in Session
```python
'best_map_name'           # Name of highest value map
'best_map_tier'           # Tier of best map
'best_map_value'          # Value in ex (highest so far)
'best_map_runtime'        # Runtime in seconds
```

### Session Top Drops (Cumulative)
```python
'session_drop_1_name'     # #1 drop across all maps
'session_drop_1_stack'    # Stack size
'session_drop_1_value'    # Value in ex
# ... _2_ and _3_ variants
```

## Integration Points

### poe_stats_refactored_v2.py

**At Startup & New Session:**
```python
# Resets all session tracking
self.game_state.reset_session_tracking()
```

**After POST-map:**
```python
# Update top drops and best map
added_rows, _ = valuate_items_raw(analysis['added'])
self.game_state.update_map_completion(added_rows)
```

## Data Flow

```
POST-Map Snapshot
    ↓
Analyze Items (valuate_items_raw)
    ↓
update_map_completion(items_with_values)
    ├─→ Calculate top 3 drops THIS map → current_map_top_drops
    ├─→ Update last_map_info (current map becomes "last")
    ├─→ Compare with best_map_info (update if better)
    └─→ Merge into session_top_drops (keep cumulative top 3)
    ↓
All data available in get_notification_data()
    ↓
Templates can use any of the new variables
```

## Usage in Templates

Example template using new data:

```python
POST_MAP = {
    'title': '🏁 {map_name} ◉ {map_value_fmt}{currency_icon}',
    'template': (
        '💎 Top Drop: {map_drop_1_name} ({map_drop_1_value}ex)\n'
        '🏆 Session Best Map: {best_map_name} ({best_map_value}ex)\n'
        '✅ Map completed!'
    )
}

# Or show previous map comparison during PRE
PRE_MAP = {
    'title': '🚀 {map_name}',
    'template': (
        '📊 Last Map: {last_map_name} ({last_map_value}ex)\n'
        '💎 Last Best: {last_map_drop_1_name} ({last_map_drop_1_value}ex)\n'
        '⚡ Starting new map!'
    )
}
```

## Example Data Structure

After completing a map with drops:

```python
# current_map_top_drops (just completed map)
[
    {'name': 'Greater Exalted Orb', 'stack': 2, 'value_ex': 100.0},
    {'name': 'Divine Orb', 'stack': 1, 'value_ex': 50.0},
    {'name': 'Exalted Orb', 'stack': 5, 'value_ex': 5.0}
]

# last_map_info (previous map - the one before current)
{
    'name': 'Grimhaven',
    'tier': '15',
    'value': 67.5,
    'runtime': 345.2,
    'top_drops': [
        {'name': 'Divine Orb', 'stack': 1, 'value_ex': 50.0},
        {'name': 'Exalted Orb', 'stack': 3, 'value_ex': 3.0},
        {'name': 'Chaos Orb', 'stack': 10, 'value_ex': 1.0}
    ]
}

# best_map_info
{
    'name': 'Necropolis',
    'tier': '15',
    'value': 480.3,  # Highest so far
    'runtime': 587.5
}

# session_top_drops (across all maps)
[
    {'name': 'Greater Exalted Orb', 'stack': 2, 'value_ex': 431.0},
    {'name': 'Divine Orb', 'stack': 3, 'value_ex': 150.0},
    {'name': 'Exalted Orb', 'stack': 10, 'value_ex': 10.0}
]
```

## Next Steps

The data is now captured and available. You can:

1. **Use in existing templates** - Add top drops to POST_MAP notification
2. **Create new templates** - Special notification for new best map
3. **Add to OBS overlays** - Show best map/drops in browser source
4. **Create analytics** - Track patterns in top drops over time

All variables are documented in `notification_templates.py` header.
