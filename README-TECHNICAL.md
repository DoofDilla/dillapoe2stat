# Technical Documentation

> **Advanced documentation for developers and contributors**

This document contains technical details about DillaPoE2Stat's architecture, modules, and internals. For basic usage, see the [main README](README.md).

---

## Table of Contents
- [Architecture](#architecture)
- [Repository Layout](#repository-layout)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [How Loot Valuation Works](#how-loot-valuation-works)
- [Session Tracking](#session-tracking)
- [Debugging Toolkit](#debugging-toolkit)
- [Extending the Project](#extending-the-project)
- [API Reference](#api-reference)

---

## Architecture

DillaPoE2Stat uses a **phase-based flow architecture** for clean, maintainable code.

### Phase-Based Flow

**MapFlowController** orchestrates PRE/POST map tracking in 9 clear phases:

#### PRE-Map Phases (1-4)
1. **Snapshot** - Capture inventory state
2. **Parse** - Extract map info from Client.txt
3. **State** - Update game state
4. **Notify** - Send map start notification

#### POST-Map Phases (1-9)
1. **Snapshot** - Capture post-map inventory
2. **Diff** - Calculate inventory changes
3. **Value** - Price items via poe.ninja
4. **Capture** - Record top drops
5. **Update** - Update session statistics
6. **Notify** - Send completion notification
7. **Log** - Persist to runs.jsonl
8. **Display** - Show terminal output
9. **Reset** - Clear temporary state

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    poe_stats_refactored_v2.py              │
│                      (Main Entry Point)                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ Hotkey  │          │ Session │          │  Auto   │
   │ Manager │          │ Manager │          │Detector │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │ MapFlowController  │
                    │  (Phase Manager)   │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │Inventory│          │  Price  │          │Waystone │
   │Analyzer │          │ Checker │          │Analyzer │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Data Persistence │
                    │  (runs.jsonl, etc) │
                    └────────────────────┘
```

**Key Components:**

- **`InventorySnapshotService`** - API calls with automatic rate limiting
- **`GameState`** - Central state management for maps, session, tracking data
- **`SessionManager`** - Session lifecycle and statistics
- **`DisplayManager`** - Console output formatting
- **`NotificationManager`** - Windows toast notifications
- **`AutoMapDetector`** - Background Client.txt monitoring

### Benefits of Phase-Based Architecture

✅ Each phase has one clear responsibility  
✅ Easy to test individual phases  
✅ Clear error messages ("Phase 5 failed" vs "POST failed")  
✅ Well-documented session tracking prevents double-counting bugs

For detailed flow diagrams and common pitfalls, see [docs/SESSION_FLOW.md](docs/SESSION_FLOW.md).

---

## Repository Layout

### Core Modules

| File | Purpose |
|------|---------|
| `poe_stats_refactored_v2.py` | Main entry point; orchestrates hotkeys, snapshots, notifications, and analytics |
| `poe_api.py` | OAuth 2.1 wrapper for PoE API (character/inventory endpoints) |
| `price_check_poe2.py` | poe.ninja data fetching, normalization, and chaos/exalt calculations |
| `client_parsing.py` | Extracts latest map instance from Client.txt log |
| `inventory_analyzer.py` | Diffs pre/post inventories, categorizes loot, feeds price valuation |
| `inventory_debug.py` | Diagnostics: print tables, export JSON, search items by name |

### Session & Display

| File | Purpose |
|------|---------|
| `session_manager.py` | Tracks cumulative runtime, map history, best map, top drops |
| `session_display.py` | Renders session dashboards with Divine trends and metrics |
| `display.py` | Centralized console formatting, ASCII themes, emoji logic, tables |
| `hotkey_manager.py` | Wraps keyboard library for global hotkey registration |
| `notification_manager.py` | Windows toast notifications with formatted values and templates |
| `notification_templates.py` | Template definitions with 40+ variables |

### Analytics & Utilities

| File | Purpose |
|------|---------|
| `waystone_analyzer.py` | Parses waystones for tier, mods, Delirious % extraction |
| `run_analyzer.py` | Historical analysis: efficiency tiers, delirious correlations |
| `poe_logging.py` | Persists per-run and per-session records to JSON Lines files |
| `ascii_theme_manager.py` | Theme configuration and rendering |
| `version.py` | Single source of truth for version and data format versioning |

### Configuration

| File | Purpose |
|------|---------|
| `config.py` | Declarative configuration: credentials, character, paths, debug switches, display settings |
| `ascii_themes.json` | Decorative footer themes and timestamp styling |
| `CHANGELOG.md` | Detailed release history |

### Legacy Scripts

Several legacy or experimental scripts remain in the repository for reference:
- `poe_stats_with_inv_snapshot_with_hotkey_price2.py`
- `poeninja_price_check*.py`
- `dualsense_*.py` (controller experiments)

---

## Core Components

### InventoryAnalyzer

**Purpose:** Diffs pre/post inventories and categorizes loot

**Key Methods:**
```python
analyze_changes(pre_inventory, post_inventory)
# Returns: {
#   'added': [...],
#   'removed': [...],
#   'net_changes': {...}
# }

categorize_items(items)
# Returns: dict with items grouped by category

find_valuable_items(items, threshold=0.01)
# Returns: list of items above value threshold
```

### PriceCheckPoe2

**Purpose:** Fetches and normalizes poe.ninja pricing data

**Key Methods:**
```python
valuate_items_raw(items)
# Returns: items with chaos, exalted, divine values

get_cached_prices(category)
# Returns: cached price data for category

normalize_item_name(name)
# Returns: normalized name for better matching
```

**Supported Categories:**
- Currency
- Catalysts
- Waystones
- Fragments
- Runes
- Skill Gems
- Support Gems
- Spirit Gems

### SessionManager

**Purpose:** Tracks session lifecycle and statistics

**Key Methods:**
```python
start_session()
end_session()
add_map(map_data)
get_session_stats()
get_best_map()
get_top_drops()
```

**Session Data Structure:**
```python
{
    'session_id': str,
    'start_time': datetime,
    'end_time': datetime,
    'runtime': int,  # seconds
    'maps': [...],
    'total_value': {'chaos': float, 'exalted': float, 'divine': float},
    'best_map': {...},
    'top_drops': [...]
}
```

### NotificationManager

**Purpose:** Send Windows toast notifications

**Template Variables (40+):**
- Map info: `map_name`, `map_tier`, `delirious_pct`
- Runtime: `runtime_str`, `session_runtime_str`
- Values: `total_chaos`, `total_exalted`, `total_divine`
- Drops: `top_drop_1_name`, `top_drop_1_value`, etc.
- Session: `session_avg_exh`, `maps_completed`

**Customization:**
Edit `notification_templates.py` to create custom messages.

### AutoMapDetector

**Purpose:** Background Client.txt monitoring for automatic snapshots

**How It Works:**
1. Polls Client.txt at configured interval (default: 2s)
2. Detects area transitions via regex patterns
3. Triggers F2 (PRE) on hideout → map
4. Triggers F3 (POST) on map → hideout
5. Respects abyss/breach detours (stays in "map mode")

**Configuration:**
```python
AUTO_DETECTION_ENABLED = False  # Toggle with Ctrl+F6
AUTO_DETECTION_INTERVAL = 2  # seconds
AUTO_HIDEOUT_AREAS = {'1_1_1', '2_6_3', ...}  # area codes
AUTO_TOWN_AREAS = {'1_1_town', ...}
AUTO_WAYSTONE_HUBS = {'1_5_1'}  # Well of Souls, etc.
```

---

## Data Flow

### Map Tracking Flow

```
User presses F2
    ↓
[Phase 1] Snapshot pre-map inventory via PoE API
    ↓
[Phase 2] Parse Client.txt for map name
    ↓
[Phase 3] Update GameState with map info
    ↓
[Phase 4] Send "Map Started" toast notification
    ↓
User completes map and presses F3
    ↓
[Phase 1] Snapshot post-map inventory
    ↓
[Phase 2] Diff pre/post inventories
    ↓
[Phase 3] Valuate added items via poe.ninja
    ↓
[Phase 4] Extract top 3 drops
    ↓
[Phase 5] Update session statistics
    ↓
[Phase 6] Send "Map Completed" toast
    ↓
[Phase 7] Log to runs.jsonl
    ↓
[Phase 8] Display terminal output
    ↓
[Phase 9] Reset temporary state
```

### OAuth 2.1 Flow

```
First run: No tokens.json exists
    ↓
Open browser to https://www.pathofexile.com/oauth/authorize
    ↓
User clicks "Authorize"
    ↓
Browser redirects to http://127.0.0.1:8080/callback
    ↓
Local server captures authorization code
    ↓
Exchange code for access + refresh tokens
    ↓
Save to tokens.json (10h access, 7d refresh)
    ↓
Subsequent runs: Load tokens.json
    ↓
If access token expired: Auto-refresh using refresh token
    ↓
If refresh token expired (7 days): Re-open browser for new authorization
```

---

## How Loot Valuation Works

### Step-by-Step Process

1. **Inventory Diff**
   - `InventoryAnalyzer.analyze_changes()` compares pre/post snapshots
   - Returns list of added items with metadata

2. **Price Lookup**
   - `price_check_poe2.valuate_items_raw()` receives added items
   - Fetches poe.ninja overview data per category
   - Normalizes item names for better matching

3. **Value Calculation**
   - Each item receives chaos, exalted, and Divine Orb equivalents
   - Category-aware icons flag catalysts, waystones, fragments
   - Stack sizes are multiplied into total values

4. **Data Persistence**
   - Results aggregated per item type
   - Persisted to `runs.jsonl` with full per-item valuation metadata
   - Data format version 2.1

5. **Top Drops Tracking**
   - Top 3 most valuable items tracked separately:
     - Current map
     - Last map
     - Cumulative session

6. **Display Filtering**
   - Items below 0.01c threshold omitted in normal mode
   - Comprehensive mode shows everything
   - All displays use formatted currency via `_format_currency()`

### Price Data Caching

- poe.ninja data cached for 5 minutes (configurable)
- Automatic retry on rate limiting
- Graceful fallback if API unavailable
- League selection in `price_check_poe2.LEAGUE`

### Supported Item Types

| Category | Examples | Icon |
|----------|----------|------|
| Currency | Chaos Orb, Exalted Orb, Divine Orb | 💰 |
| Catalysts | Abrasive, Intrinsic, Tempering | ⚗️ |
| Waystones | T1-T16 waystones | 🗺️ |
| Fragments | Breachstone, Simulacrum | 🔮 |
| Runes | Soul Cores, Runes of various types | 📿 |
| Gems | Skill, Support, Spirit gems | 💎 |

---

## Session Tracking

### Session Data Structure (v2.1)

```json
{
  "session_id": "20250122_143022",
  "start_time": "2025-01-22T14:30:22",
  "end_time": "2025-01-22T16:45:10",
  "runtime": 8088,
  "maps_completed": 12,
  "total_value": {
    "chaos": 1250.5,
    "exalted": 125.05,
    "divine": 12.505
  },
  "best_map": {
    "name": "Crimson Temple",
    "tier": 15,
    "value": 180.5,
    "runtime": 245,
    "delirious_pct": 40
  },
  "top_drops": [
    {
      "name": "Divine Orb",
      "value": 100.0,
      "map": "Crimson Temple"
    },
    {
      "name": "Exalted Orb",
      "value": 10.0,
      "map": "Summit"
    }
  ],
  "maps": [...]
}
```

### Run Data Structure (v2.1)

```json
{
  "timestamp": "2025-01-22T14:35:45",
  "map_name": "Crimson Temple",
  "map_tier": 15,
  "delirious_pct": 40,
  "runtime": 245,
  "loot": {
    "Chaos Orb": {
      "count": 15,
      "chaos_value": 15.0,
      "exalted_value": 1.5,
      "divine_value": 0.15,
      "category": "currency"
    }
  },
  "total_value": {
    "chaos": 180.5,
    "exalted": 18.05,
    "divine": 1.805
  },
  "top_drops": [...]
}
```

### Data Versioning

**Version 2.1** (Current)
- Adds `delirious_pct` field to maps
- Full per-item valuations (chaos, exalted, divine)
- Top drops tracking

**Version 2.0**
- Per-item valuation metadata
- Category-aware icons

**Version 1.x**
- Basic runtime and loot tracking

**Upgrading Data:**
```bash
python upgrade_runs_data.py
```

Creates backup and converts legacy entries to latest format.

---

## Debugging Toolkit

### InventoryDebugger

**Available Methods:**

```python
# Print compact item summary
dump_item_summary(inventory)

# Full JSON dump to console
dump_inventory_to_console(inventory)

# Export to timestamped JSON file
export_inventory_to_file(inventory, prefix="inventory")

# Search for specific item
search_item(inventory, search_term)
```

**Toggle Debug Mode:**
- Press `F4` during runtime
- Or set `DEBUG_ENABLED = True` in `config.py`

**Debug Options:**
```python
DEBUG_ENABLED = False
DEBUG_TO_FILE = False  # Export inventories to debug/ folder
DEBUG_SHOW_SUMMARY = True  # Concise vs exhaustive dumps
```

### Run Analyzer

**Analyze Historical Data:**

```bash
python run_analyzer.py
```

**Features:**
- Efficiency tiers (color-coded)
- Divine Orb drop patterns
- Delirious % correlation analysis
- Best performing map analysis
- Modifier pattern detection

### Session Display

**View Session Dashboard:**

Press `F7` or run:
```bash
python session_display.py
```

**Shows:**
- Last 5 maps
- Session averages
- Best map
- Top drops
- Divine Orb trends
- Color-coded performance metrics

---

## Extending the Project

### Custom Analytics

**Example: Implement stash tab scraping**

```python
from inventory_analyzer import InventoryAnalyzer

analyzer = InventoryAnalyzer()

# Your custom logic
def analyze_stash_tab(tab_data):
    items = analyzer.categorize_items(tab_data)
    valuable = analyzer.find_valuable_items(items, threshold=1.0)
    return valuable
```

### Alternative Notifications

**Example: Discord webhook**

```python
import requests
from notification_manager import NotificationManager

class DiscordNotifier(NotificationManager):
    def send_map_completion(self, data):
        webhook_url = "https://discord.com/api/webhooks/..."
        payload = {
            "content": f"Map completed! Value: {data['total_exalted']}ex"
        }
        requests.post(webhook_url, json=payload)
```

### Custom Templates

**Edit `notification_templates.py`:**

```python
CUSTOM_TEMPLATE = {
    'title': 'My Custom Title',
    'body': '{map_name} - {total_exalted}ex in {runtime_str}',
    'actions': []
}
```

**Available Variables (40+):**
- Map: `map_name`, `map_tier`, `delirious_pct`
- Values: `total_chaos`, `total_exalted`, `total_divine`
- Runtime: `runtime_str`, `session_runtime_str`
- Drops: `top_drop_1_name`, `top_drop_1_value`, `top_drop_2_name`, etc.
- Session: `session_avg_exh`, `maps_completed`, `session_total_chaos`

### Data Export

**Example: Export to CSV**

```python
import json
import csv

def export_to_csv(input_file='runs.jsonl', output_file='runs.csv'):
    with open(input_file, 'r') as f:
        runs = [json.loads(line) for line in f]
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'map_name', 'runtime', 'total_exalted'])
        writer.writeheader()
        for run in runs:
            writer.writerow({
                'timestamp': run['timestamp'],
                'map_name': run.get('map_name', 'Unknown'),
                'runtime': run['runtime'],
                'total_exalted': run['total_value']['exalted']
            })
```

### Custom OBS Overlays

**Add Flask endpoint in `obs_web_server.py`:**

```python
@app.route('/obs/custom_overlay')
def custom_overlay():
    # Your custom logic
    data = get_custom_data()
    return render_template('custom_overlay.html', data=data)
```

### Controller Integration

**Example using dualsense experiments:**

```python
from dualsense import DualSenseController

controller = DualSenseController()

# Map controller buttons to hotkeys
controller.on_button('circle', trigger_pre_snapshot)
controller.on_button('square', trigger_post_snapshot)
```

---

## API Reference

### PoE API Endpoints

**Authentication:**
```
POST https://www.pathofexile.com/oauth/token
```

**Character List:**
```
GET https://www.pathofexile.com/api/account/characters
```

**Character Inventory:**
```
GET https://www.pathofexile.com/api/character/{character_name}
```

### poe.ninja API

**Base URL:**
```
https://poe.ninja/api/data/{league}/{category}
```

**Categories:**
- `currency` - Currency exchange rates
- `catalyst` - Catalyst prices
- `waystone` - Waystone prices
- `fragment` - Fragment prices
- `rune` - Rune prices
- `skillgem` - Skill gem prices
- `supportgem` - Support gem prices

**Example:**
```
GET https://poe.ninja/api/data/PathOfExile2Settlers/currency
```

### Rate Limiting

**PoE API:**
- Rate limits are IP-based
- Automatic retry with exponential backoff
- Tokens refresh automatically

**poe.ninja:**
- No explicit rate limits documented
- Recommended: Cache for 5+ minutes
- Our implementation: 5-minute cache by default

---

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints where appropriate
- Document complex functions
- Keep functions focused and testable

### Testing

```bash
# Run with debug mode
python poe_stats_refactored_v2.py

# Toggle debug during runtime
Press F4

# Simulate snapshots (no real API calls)
Ctrl+Shift+F2  # Simulate pre-snapshot
Ctrl+Shift+F3  # Simulate post-snapshot
```

### Adding New Features

1. **Create new module** in project root
2. **Add to appropriate manager** (session, display, etc.)
3. **Update config.py** with new settings
4. **Document in this file**
5. **Add to CHANGELOG.md**

### Debugging Tips

- Use `DEBUG_TO_FILE = True` to export inventories
- Check `debug/` folder for JSON dumps
- Enable verbose logging with `DEBUG_ENABLED = True`
- Use simulation hotkeys to test without running maps

---

## Performance Considerations

### API Calls
- Inventory snapshots: ~1-2s per call
- Rate limiting: Automatic retry with backoff
- Token refresh: Automatic, no user intervention

### Price Data
- Cached for 5 minutes by default
- Disk cache persists between sessions
- Manual refresh with `F5` (inventory check)

### Memory Usage
- Session data kept in memory
- Historical data in JSON Lines files
- Typical memory usage: <100MB

### File I/O
- Append-only for runs.jsonl (fast)
- Session persistence on F6 or exit
- Debug exports optional

---

## Related Documentation

- **[Main README](README.md)** - User guide and quick start
- **[Session Flow](docs/SESSION_FLOW.md)** - Detailed phase diagrams
- **[CHANGELOG](CHANGELOG.md)** - Version history
- **[Wiki](https://github.com/DoofDilla/dillapoe2stat/wiki)** - Full documentation

---

## Support

For technical questions or issues:
- [GitHub Issues](https://github.com/DoofDilla/dillapoe2stat/issues)
- [GitHub Discussions](https://github.com/DoofDilla/dillapoe2stat/discussions)

---

**Last Updated:** October 22, 2025  
**Version:** 0.4.0  
**Data Format:** 2.1
