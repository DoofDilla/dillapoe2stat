# DillaPoE2Stat - AI Coding Agent Instructions

## Project Overview

**Path of Exile 2 farming tracker** with phase-based architecture for inventory snapshots, loot valuation, and session analytics. Hotkey-driven Windows tool with OBS overlay support for streamers.

**Tech Stack:** Python 3.10+, Windows-only (`keyboard`, `win11toast`), OAuth API integration, Flask web server

**Core Entry Point:** `poe_stats_refactored_v2.py` - main tracker with global hotkey bindings

## Critical Architecture Patterns

### Phase-Based Flow Controller (v0.3.4+)

**THE MOST IMPORTANT PATTERN** - All map tracking uses `MapFlowController` with explicit phases:

```python
# PRE-MAP (F2): 4 phases
Phase 1: Snapshot → Phase 2: Parse → Phase 3: Update State → Phase 4: Notify

# POST-MAP (F3): 9 phases  
Phase 1-3: Snapshot → Diff → Value
Phase 4: Capture session BEFORE (critical for comparison)
Phase 5: Update session (ONLY place to call add_completed_map())
Phase 6-9: Notify → Log → Display → Reset
```

**Why this matters:**
- **Session double-counting bug prevention:** Only Phase 5 can add maps to session
- **Accurate notifications:** Phase 4 captures "session before this map" for ex/h comparison
- Read `docs/SESSION_FLOW.md` for complete flow diagrams and common pitfalls

**When modifying tracking flow:**
1. Never call `session_manager.add_completed_map()` outside `_phase_update_post_state()`
2. Use `_phase_capture_session_before()` for baseline metrics before updating
3. Each phase returns explicit dataclass result (`DiffResult`, `ValueResult`, `SessionSnapshot`)

### Manager-Based Modular Architecture

```
PoEStatsTracker (main orchestrator)
  ├── MapFlowController (phases)
  │     └── InventorySnapshotService (API + rate limiting)
  ├── GameState (central state: map, session, drops)
  ├── SessionManager (session lifecycle, stats)
  ├── InventoryAnalyzer (diff, categorize)
  ├── DisplayManager (console output, themes)
  ├── NotificationManager (Windows toasts)
  ├── WaystoneAnalyzer (experimental waystone parsing)
  └── AutoMapDetector (Client.txt monitoring)
```

**Managers are singletons** - initialize once in `PoEStatsTracker.__init__`, pass to flow controller

## Data Persistence & Versioning

### JSON Lines Format (Not JSON)

```python
# runs.jsonl - ONE JSON object per line (append-only)
{"run_id": "abc123", "format_version": "2.1", "delirious": 0, ...}
{"run_id": "def456", "format_version": "2.1", "delirious": 15, ...}

# sessions.jsonl - Event log
{"event_type": "session_start", "session_id": "xyz", ...}
{"event_type": "session_end", "session_id": "xyz", "total_maps": 5, ...}
```

**Data Format Versions:**
- `2.0`: Added per-item valuations (chaos/exalted/divine)
- `2.1`: Added `delirious` field for waystone tracking
- Use `upgrade_runs_data.py` to migrate old data (creates timestamped backups)

**When adding new fields:**
1. Bump `DATA_FORMAT_VERSION` in `version.py`
2. Update `upgrade_runs_data.py` with migration logic
3. Document in CHANGELOG.md

## Configuration System

### Config.py Pattern

All settings live in `Config` class (NOT module globals):

```python
# WRONG - Don't use module globals
CLIENT_ID = "myid"

# RIGHT - Use Config class
from config import Config
client_id = Config.CLIENT_ID
```

**Key config groups:**
- `CLIENT_ID/CLIENT_SECRET`: OAuth credentials (must have `account:characters account:profile` scopes)
- `CHAR_TO_CHECK`: Character name (case-sensitive)
- `CLIENT_LOG`: Absolute path to `Client.txt` (typically `Documents\My Games\Path of Exile 2\logs`)
- `AUTO_HIDEOUT_AREAS/AUTO_TOWN_AREAS`: Area codes for auto-detection (extend for custom hideouts)

**Path Helpers:** Always use `Config.get_*_path()` methods (handles absolute paths, creates directories)

## PoE API Integration

### Rate Limiting is Critical

```python
# Rate limiting handled by InventorySnapshotService
snapshot_service = InventorySnapshotService(
    token=token,
    min_gap_seconds=Config.API_RATE_LIMIT  # Default: 2.5s
)

# NEVER call poe_api.snapshot_inventory() directly
# Always go through InventorySnapshotService
```

**API Endpoints:**
- `get_token()`: OAuth client credentials flow
- `get_characters()`: List characters (for validation)
- `snapshot_inventory()`: Get current inventory (rate-limited)

### Price Checking (poe.ninja)

```python
from price_check_poe2 import valuate_items_raw

# Returns items with chaos/exalted/divine values
valued_items = valuate_items_raw(items)

# CurrencyCache singleton - loads once at startup
# Don't manually refresh unless poe.ninja data changes mid-session
```

**League Configuration:** Update `LEAGUE` constant in `price_check_poe2.py` for new leagues

## Notification System

### Template Variables (40+)

Templates in `notification_templates.py` use formatted variables:

```python
# Currency values: Always use _fmt suffix for display
{map_value_fmt}            # "123.5ex" (clean formatting)
{session_value_per_hour_fmt}  # "1440ex/h"

# Top drops tracking
{map_drop_1_name}          # Current map top drop
{session_drop_1_value_fmt} # Session cumulative best

# Waystone data
{waystone_tier}            # 80
{waystone_delirious}       # 15 (extracted from suffixes)
```

**When adding notification variables:**
1. Add to `GameState` or `SessionManager` 
2. Pass via `get_template_variables()` in `NotificationManager`
3. Document in `notification_templates.py` docstring

### Windows Toast Registration

```python
# STABLE App ID (no version) - prevents registry pollution
Config.TOAST_APP_ID = "DoofDilla.BoneBunnyStats"  # Never change

# Display ID (with version)
Config.APP_ID = "BoneBunnyStats v0.3.4"
```

`AppRegistration.ensure_app_registered()` runs on startup - handles registry setup

## Hotkey System

### Global Keyboard Bindings

```python
# Registered in hotkey_manager.py
F2        → PRE snapshot (before map)
F3        → POST snapshot (after map)
Ctrl+F2   → Waystone analyzer (experimental)
F4        → Toggle debug mode
F5        → Current inventory value
F6        → New session
Ctrl+F6   → Toggle auto-detection
F7        → Session stats
F8        → Output mode toggle
F9        → OBS server toggle
Ctrl+Esc  → Exit tracker
```

**Hotkeys work globally** (no terminal focus needed) via `keyboard` package

**When adding hotkeys:**
1. Register in `HotkeyManager.setup_default_hotkeys()`
2. Add description for terminal output
3. Update README.md hotkey table

## Auto Map Detection

### Client.txt Log Parsing

```python
# AutoMapDetector monitors for zone transitions
Hideout → Map    = Trigger F2 (PRE snapshot)
Map → Hideout    = Trigger F3 (POST snapshot)

# Respects abyssal/breach zones (stays in "map mode")
```

**Area Code Configuration:**
- `AUTO_HIDEOUT_AREAS`: Safe zones for inventory (e.g., `HideoutFelled`)
- `AUTO_TOWN_AREAS`: Towns that trigger waystone analysis (e.g., `Abyss_Hub`)
- `AUTO_WAYSTONE_TRIGGER_AREAS`: Where to auto-analyze waystones

**Client.txt scanning:** Last 50KB by default (`AUTO_DETECTION_SCAN_BYTES`)

## OBS Integration

### Flask Web Server

```python
# Optional - toggle with F9 or Config.OBS_AUTO_START
OBSWebServer(
    host="localhost",
    port=5000,
    quiet_mode=True  # Suppress Flask request logs
)

# Browser Source URLs
/obs/item_table      # Loot table (600x400)
/obs/session_stats   # Session dashboard (300x200)
```

**Templates:** `obs_overlays/` directory - HTML with inline CSS (no external files)

## Debug Workflows

### Debug Mode (F4 Toggle)

```python
Config.DEBUG_ENABLED = True   # Master switch
Config.DEBUG_TO_FILE = True   # Save to debug/*.json
Config.DEBUG_SHOW_SUMMARY = True  # Concise vs full dumps
```

**InventoryDebugger methods:**
- `dump_item_summary()`: Compact table
- `dump_inventory_to_console()`: Full JSON
- `export_inventory_to_file()`: Timestamped exports to `debug/`

### Simulation Hotkeys

```python
Ctrl+Shift+F2  → Simulate PRE snapshot (test notifications)
Ctrl+Shift+F3  → Simulate POST snapshot (test overlays)
```

## Testing Conventions

**No formal test suite** - Manual testing procedures documented in:
- `docs/SESSION_FLOW.md` → Session tracking validation
- README → Troubleshooting common issues

**When testing session logic:**
1. Start new session
2. Run 1-2 maps manually
3. Verify terminal output (maps counted once)
4. Check notifications (comparison uses BEFORE state)
5. Inspect `runs.jsonl` / `sessions.jsonl` format

## Common Pitfalls

### 1. Double-Counting Maps

**Symptom:** Session shows 2 maps when only 1 was run

**Cause:** Multiple `add_completed_map()` calls

**Fix:** Only call in `MapFlowController._phase_update_post_state()`

### 2. Incorrect Notification Comparisons

**Symptom:** "Run: 1440ex/h 🆚 Avg: 1440ex/h" (same values)

**Cause:** Using session state AFTER adding current map

**Fix:** Capture `session_before` in Phase 4 (BEFORE Phase 5 updates)

### 3. Path Separator Issues

**Windows paths:** Use raw strings `r"C:\path\to\file"` or `Path()` objects

```python
# WRONG
CLIENT_LOG = "C:\Users\Name\Path"  # Escape sequences

# RIGHT
CLIENT_LOG = r"C:\Users\Name\Path"  # Raw string
CLIENT_LOG = Config.get_log_file_path()  # Path helper
```

### 4. OAuth Scope Errors (401)

**Required scopes:** `account:characters account:profile`

Verify at https://www.pathofexile.com/developer/docs/api

## Code Style

- **Type hints via dataclasses** (not traditional annotations) - see `InventorySnapshot`, `DiffResult`
- **ANSI colors:** Use `Colors` class from `display.py` (not hardcoded escape codes)
- **Emoji rendering:** Check `DisplayManager.can_display_emoji()` before using Unicode
- **German comments:** Some legacy code has German comments (acceptable, don't refactor)

## Version Management

**Single source of truth:** `version.py`

```python
__version__ = "0.3.4"
RELEASE_NAME = "Phase-Based Architecture"
DATA_FORMAT_VERSION = "2.1"
```

**Version bumping:**
1. Update `version.py`
2. Add CHANGELOG.md entry
3. Update README.md version badge
4. Git tag: `git tag v0.3.4`

## Key Files Reference

| File | Purpose | Read When |
|------|---------|-----------|
| `docs/SESSION_FLOW.md` | Phase flow diagrams | Modifying tracking logic |
| `notification_templates.py` | All 40+ template vars | Adding notification data |
| `config.py` | All settings + validation | Adding config options |
| `game_state.py` | Central state management | Understanding state lifecycle |
| `CHANGELOG.md` | Release history | Understanding version changes |

## Quick Wins for Contributors

- **Add notification variable:** Extend `GameState` → update `get_template_variables()` → document
- **New ASCII theme:** Add to `ascii_themes.json` → reference in README
- **Support new hideout:** Add area code to `AUTO_HIDEOUT_AREAS` in `config.py`
- **Custom price source:** Extend `price_check_poe2.py` `_fetch_items_with_aliases()`

## Questions to Ask User

When unclear:
1. Which phase should this logic run in? (See SESSION_FLOW.md)
2. Should this be configurable? (Add to Config class)
3. Does this need notification support? (Template variables)
4. Will this work on Windows only? (Target platform)
