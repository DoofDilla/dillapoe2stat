# Session Tracking Flow Documentation

## Overview

This document explains the **session tracking flow** in the PoE Stats Tracker, specifically focusing on how session state is captured, updated, and used for notifications.

Understanding this flow is critical to avoid bugs like double-counting maps or incorrect session metrics.

---

## Key Concepts

### Session State Components

1. **SessionManager**: Tracks actual session data
   - `session_maps_completed`: Number of completed maps
   - `session_total_value`: Cumulative value in exalted orbs
   - `session_start_time`: Session start timestamp

2. **GameState.session_progress**: Cached snapshot of session state
   - Used by notifications and display
   - Updated after each map completion

3. **SessionSnapshot**: Immutable snapshot at a point in time
   - `maps_completed`: Maps completed at snapshot time
   - `total_value`: Total value at snapshot time
   - `runtime_seconds`: Session runtime at snapshot time
   - `value_per_hour`: Calculated ex/h at snapshot time

---

## POST-Map Flow (Phase by Phase)

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ F3 PRESSED (POST-MAP)                                        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Take Inventory Snapshot                            │
│ - API call to get POST inventory                            │
│ - Rate limited                                               │
│ - Returns: InventorySnapshot object                          │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Diff Inventories (PRE vs POST)                     │
│ - Compare PRE and POST snapshots                             │
│ - Returns: DiffResult (added/removed items)                  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Calculate Loot Value                               │
│ - Price check added/removed items                            │
│ - Extract items with values for top drops                    │
│ - Returns: ValueResult (total_value_ex, items_with_values)   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Capture Session State BEFORE Update               │
│ ⚠️  CRITICAL: This does NOT add the map!                    │
│                                                              │
│ session_before = session_manager.get_session_progress()     │
│   → Maps: N                                                  │
│   → Total: X ex                                              │
│   → Runtime: T seconds                                       │
│                                                              │
│ Calculate: session_value_per_hour_before = X / (T/3600)     │
│                                                              │
│ Purpose: Needed for notification comparison:                │
│   "Run: 1440ex/h 🆚 Avg: 740ex/h"                          │
│         ^^^^^^^^      ^^^^^^^^                               │
│         this map      BEFORE map (session average)           │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Update Session & Game State                        │
│ ⚠️  CRITICAL: Map is added ONCE here!                       │
│                                                              │
│ game_state.complete_map(map_value, map_runtime)             │
│   → Updates: map_value, map_runtime                          │
│                                                              │
│ session_manager.add_completed_map(map_value)  ← SINGLE CALL │
│   → Increments: session_maps_completed += 1                  │
│   → Adds value: session_total_value += map_value             │
│                                                              │
│ session_after = session_manager.get_session_progress()      │
│   → Maps: N+1                                                │
│   → Total: X + map_value                                     │
│   → Runtime: T + map_time                                    │
│                                                              │
│ game_state.update_session_progress(session_after)           │
│   → Caches session state for notifications                   │
│                                                              │
│ game_state.update_map_completion(items_with_values)         │
│   → Updates: last_map, best_map, top_drops                   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 6: Send Notification                                  │
│                                                              │
│ game_state.set_session_comparison_baseline(                 │
│     session_before.value_per_hour                            │
│ )                                                            │
│   → Stores ex/h BEFORE this map for comparison               │
│                                                              │
│ notification_manager.notify_post_map(game_state)            │
│   → Uses session_value_per_hour_before for comparison        │
│   → Uses session_after (updated) for current stats           │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 7: Log Run to File                                    │
│ - Write run data to runs.jsonl                               │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 8: Display Session Progress                           │
│ - Terminal output with session stats                         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 9: Reset Current Map State                            │
│                                                              │
│ game_state.reset_current_map()                               │
│   → Clears: current_map_info, map_start_time, map_value      │
│   → Keeps: cached_waystone_info (for reference)              │
│   → Keeps: last_map_info (moved from current)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Common Pitfalls and How to Avoid Them

### ❌ PITFALL #1: Double-Counting Maps

**Problem:**
```python
# WRONG - Two calls to add_completed_map!
session_before = session_manager.get_session_progress()
session_manager.add_completed_map(map_value)  # ← First call

# ... some code ...

session_manager.add_completed_map(map_value)  # ← Second call (BUG!)
```

**Result:** Session shows 2 maps when only 1 was run, total value is doubled.

**Solution:**
- `add_completed_map()` must be called **EXACTLY ONCE** per POST flow
- In `MapFlowController`, this happens in `_phase_update_post_state()`
- Phase 4 (`_phase_capture_session_before`) only **reads** session state

---

### ❌ PITFALL #2: Using Wrong Session State for Notifications

**Problem:**
```python
# WRONG - Using session state AFTER adding map for comparison
session_manager.add_completed_map(map_value)
session_after = session_manager.get_session_progress()

# Notification shows: "Run: 1440ex/h 🆚 Avg: 1440ex/h"
#                     ↑ current map    ↑ includes current map (WRONG!)
notification_manager.notify_post_map(session_after)
```

**Result:** Notification comparison is meaningless (comparing map to itself).

**Solution:**
- Capture `session_before` **BEFORE** calling `add_completed_map()`
- Use `session_before.value_per_hour` for comparison baseline
- Use `session_after` for current session stats

---

### ❌ PITFALL #3: Modifying GameState Attributes Directly

**Problem:**
```python
# WRONG - Direct attribute modification
game_state._session_value_per_hour_before = some_value
```

**Result:** Hard to track, breaks encapsulation, unclear intent.

**Solution:**
```python
# RIGHT - Use explicit setter method
game_state.set_session_comparison_baseline(some_value)
```

---

## Session State Lifecycle

### Session Start
```python
session_manager.start_new_session()
→ session_id = UUID
→ session_start_time = now
→ session_maps_completed = 0
→ session_total_value = 0.0
```

### First Map Completion
```python
# BEFORE: Maps=0, Total=0ex, Runtime=0s, ex/h=0
session_before = get_session_progress()  # Captures empty state

add_completed_map(100.5)

# AFTER: Maps=1, Total=100.5ex, Runtime=300s, ex/h=1206
session_after = get_session_progress()
```

### Second Map Completion
```python
# BEFORE: Maps=1, Total=100.5ex, Runtime=300s, ex/h=1206
session_before = get_session_progress()

add_completed_map(150.2)

# AFTER: Maps=2, Total=250.7ex, Runtime=580s, ex/h=1555
session_after = get_session_progress()
```

### Session End
```python
session_manager.end_current_session()
→ Logs final stats to sessions.jsonl
→ Resets session state
```

---

## Notification Variables Explained

### Session Comparison Variables

| Variable | Source | Purpose |
|----------|--------|---------|
| `session_value_per_hour_before_fmt` | Phase 4 (BEFORE map) | Baseline for comparison |
| `session_value_per_hour_fmt` | Phase 5 (AFTER map) | Current session average |
| `map_value_per_hour_fmt` | Current map runtime | This specific map's rate |

### Example Notification
```
🏁 Grimhaven ▷ 80 ◷ 4m32s ◉ 67💰
Run: 1440💰/h 🆚 Avg: 740💰/h
     ↑ map_value_per_hour_fmt
                      ↑ session_value_per_hour_before_fmt

Session: 15 ◉ 11025💰 ◷ 1480💰/h
         ↑ maps_completed (AFTER)
              ↑ total_value (AFTER)
                         ↑ session_value_per_hour_fmt (AFTER)
```

---

## Testing Session Flow

### Unit Test Example
```python
def test_session_flow_no_double_count():
    """Verify map is only added once to session"""
    controller = MapFlowController(...)
    
    # Execute POST flow
    controller.execute_post_map_flow()
    
    # Verify session was updated exactly once
    assert session_manager.session_maps_completed == 1
    assert session_manager.session_total_value == expected_value
```

### Manual Test Procedure
1. Start new session
2. Run 1 map: Ctrl+F2 → F2 → F3
3. **Verify Terminal Output:**
   - "Maps: 1" (not 2)
   - Total value matches single map value
4. **Verify Notification:**
   - Session shows 1 map completed
   - Total value is correct

---

## Code References

### Main Files
- **`map_flow_controller.py`**: Phase-based flow implementation
- **`session_manager.py`**: Session state tracking
- **`game_state.py`**: Central state management
- **`notification_manager.py`**: Notification rendering

### Key Methods
- `MapFlowController.execute_post_map_flow()`: Main POST flow entry point
- `MapFlowController._phase_capture_session_before()`: Phase 4 (capture BEFORE state)
- `MapFlowController._phase_update_post_state()`: Phase 5 (update session - SINGLE add call)
- `SessionManager.add_completed_map()`: Increment session counters
- `SessionManager.get_session_progress()`: Get current session state snapshot

---

## Changelog

### v0.3.3 (October 5, 2025)
- Added phase-based architecture with `MapFlowController`
- Fixed double-counting bug (was calling `add_completed_map()` twice)
- Added `SessionSnapshot` for immutable state capture
- Improved session flow documentation

---

## Questions?

If you encounter session tracking issues:

1. **Check Phase 4:** Is `session_before` captured BEFORE `add_completed_map()`?
2. **Check Phase 5:** Is `add_completed_map()` called EXACTLY once?
3. **Check Notification:** Is `session_value_per_hour_before` from Phase 4 (BEFORE state)?
4. **Enable Debug:** Add print statements at each phase boundary

Example debug output:
```python
# In Phase 4
print(f"[PHASE 4] Session BEFORE: Maps={session_before.maps_completed}, Total={session_before.total_value}")

# In Phase 5
print(f"[PHASE 5] Adding map with value: {map_value}")
session_manager.add_completed_map(map_value)
print(f"[PHASE 5] Session AFTER: Maps={session_after.maps_completed}, Total={session_after.total_value}")
```
