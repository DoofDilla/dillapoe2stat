# DillaPoE2Stat - AI Coding Agent Instructions

## Project Overview

**Path of Exile 2 farming tracker** with phase-based architecture for inventory snapshots, loot valuation, and session analytics. Hotkey-driven Windows tool with OBS overlay support for streamers.

**Tech Stack:** Python 3.10+, Windows-only (`keyboard`, `win11toast`), OAuth API integration, Flask web server

**Core Entry Point:** `poe_stats_refactored_v2.py` - main tracker with global hotkey bindings

## ⚠️ CRITICAL: Git Commit Rules (READ THIS FIRST!)

**EVERY COMMIT MUST HAVE GITMOJI - NO EXCEPTIONS!**

### How to Commit (Windows)

**❌ NEVER do this:**
```bash
git commit -m "feat: Add feature"  # Missing gitmoji! PowerShell strips emojis!
```

**✅ ALWAYS do this:**
```bash
& "C:\Program Files\Git\bin\bash.exe" -c "
  cd /c/temp/dillapoe2stat && 
  printf 'feat: \xE2\x9C\xA8 Add feature\n\n- Detail 1\n- Detail 2\n' > commit_msg.txt && 
  git commit -F commit_msg.txt && 
  rm commit_msg.txt
"
```

**Common gitmoji hex codes (MEMORIZE THESE):**
- ✨ `feat:` new feature → `\xE2\x9C\xA8`
- 🐛 `fix:` bug fix → `\xF0\x9F\x90\x9B`
- 📝 `docs:` documentation → `\xF0\x9F\x93\x9D`
- 🔧 `chore:` config/tooling → `\xF0\x9F\x94\xA7`
- 🚀 `perf:` performance → `\xF0\x9F\x9A\x80`
- 🔖 `chore:` version bump → `\xF0\x9F\x94\x96`

**If you forget gitmoji:**
1. STOP immediately
2. `git reset --soft HEAD~1`
3. Re-commit with proper gitmoji using Git Bash

**Why:** PowerShell cannot handle UTF-8 emojis - they get stripped before Git sees them!

## Available MCP Servers

This project has access to specialized MCP servers for enhanced AI assistance:

### Microsoft Learn MCP Server (`microsoft_docs_*`)
- **Purpose:** Trusted, up-to-date information from official Microsoft documentation
- **Use for:** Windows API questions, Python on Windows, Azure integration, .NET interop
- **Tools available:**
  - `microsoft_docs_search` - Search official docs (returns 10 concise chunks)
  - `microsoft_code_sample_search` - Find code examples from Microsoft Learn
  - `microsoft_docs_fetch` - Get full documentation pages in markdown
- **When to use:** Win32 API questions (like HWND_TOPMOST, WS_EX_TRANSPARENT), ctypes with Windows, Python best practices
- **Workflow:** Search → Get overview → Fetch full page if needed

### MCP Memory Server (`mcp_memory_*`)
- **Purpose:** Persistent knowledge graph across chat sessions
- **See:** "Memory Management" section below for detailed usage guidelines

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

**Important:** `runs.jsonl` and `sessions.jsonl` are **NOT tracked in Git** (local data only)
- Listed in `.gitignore` to prevent accidental commits
- Sample files provided: `runs.jsonl.sample`, `sessions.jsonl.sample`
- New users: Copy `.sample` files to create initial data files

**Data Format Versions:**
- `2.0`: Added per-item valuations (chaos/exalted/divine)
- `2.1`: Added `delirious` field for waystone tracking
- Use `upgrade_runs_data.py` to migrate old data (creates timestamped backups)

**When adding new fields:**
1. Bump `DATA_FORMAT_VERSION` in `version.py`
2. Update `upgrade_runs_data.py` with migration logic
3. Document in CHANGELOG.md

### Local Backups

**Backup utility:** `backup_session_data.py` creates timestamped backups

```bash
# Create backup (saves to ./backups/)
python backup_session_data.py

# Keep only 5 most recent backups
python backup_session_data.py --keep 5

# Custom backup directory
python backup_session_data.py --backup-dir C:\MyBackups

# Cleanup old backups only (no new backup)
python backup_session_data.py --cleanup-only --keep 10
```

**Auto-backup before major changes:**
- Run `upgrade_runs_data.py` automatically creates backups
- Manually backup before version upgrades or major refactoring
- Backup directory (`backups/`) is ignored by Git

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
- `CHAR_TO_CHECK`: Character name (case-sensitive, set directly in config.py)
- `CLIENT_LOG`: Absolute path to `Client.txt` (typically `Documents\My Games\Path of Exile 2\logs`)
- `AUTO_HIDEOUT_AREAS/AUTO_TOWN_AREAS`: Area codes for auto-detection (extend for custom hideouts)

**Path Helpers:** Always use `Config.get_*_path()` methods (handles absolute paths, creates directories)

### ⚠️ OAuth 2.1 Authentication - CRITICAL

**OAuth 2.1 uses Public Client flow (v0.4.0+):**

**tokens.json (auto-generated, NOT tracked in Git):**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_at": 1234567890,
  "username": "CharacterName"
}
```

**config.py (character name):**
```python
CHAR_TO_CHECK = "YourCharacterName"  # Set this to your PoE2 character
```

**NEVER:**
- ❌ Commit `tokens.json` to Git (contains access/refresh tokens)
- ❌ Log or print access tokens in debug output
- ❌ Share tokens.json with anyone (user-specific credentials)

**OAuth 2.1 Flow:**
1. **First run**: Opens browser for authorization → user logs in → callback receives code
2. **Token exchange**: Code exchanged for access_token + refresh_token
3. **Auto-refresh**: Tokens auto-refresh every 10 hours (access token lifetime)
4. **Re-authorization**: After 7 days (refresh token lifetime), browser re-opens

**Implementation Details:**
- `oauth_flow.py`: Complete OAuth 2.1 implementation with PKCE
- Public Client: No client_secret required (desktop app security model)
- PKCE: Proof Key for Code Exchange prevents authorization code interception
- Callback: Local HTTP server on port 8080 receives authorization code
- User-Agent: Required header to prevent Cloudflare blocking

**When modifying config:**
- ✅ Character name set directly in `config.py` as `CHAR_TO_CHECK`
- ✅ OAuth client registration done at https://www.pathofexile.com/developer/docs/api
- ✅ No credentials file needed - OAuth handles authentication

**Security Notes:**
- tokens.json is auto-generated and gitignored
- OAuth Public Client requires no secrets in code
- Browser-based authorization flow handles all authentication

## PoE API Integration

### OAuth 2.1 Authentication (v0.4.0+)

**OAuth Flow Module:** `oauth_flow.py` handles all authentication

```python
from oauth_flow import get_access_token

# Automatic flow - handles browser authorization and token refresh
token = get_access_token()  # Opens browser on first run

# Token automatically refreshed when expired
# Re-authorization required after 7 days (refresh token lifetime)
```

**Key Components:**
- `PKCEGenerator`: Creates code_verifier and SHA256 challenge
- `CallbackHandler`: HTTP server on port 8080 receives authorization code
- `OAuthFlow`: Opens browser, waits for callback, exchanges code for token
- `TokenManager`: Saves/loads `tokens.json`, auto-refreshes before expiration

**Important:**
- User-Agent header REQUIRED on all OAuth requests (prevents Cloudflare 403)
- Public Client: No client_secret needed
- Authorization warning normal (all Public Clients show this)

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
- `get_token()`: OAuth 2.1 flow (via oauth_flow module)
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

## KISS Overlay System (v0.3.4+)

### String-Based Templates

**Critical:** Overlay templates in `kiss_overlay_templates.py` **must match** `notification_templates.py` format:

```python
# ✅ CORRECT - Single-line strings with \n
SECTION_WAYSTONE = (
    'Waystone: T{waystone_tier} | {waystone_delirious}% Delirium\n'
    'Pack Size: +{waystone_pack_size}%\n'
    'Magic Monsters: +{magic_monsters}%'
)

# ❌ WRONG - Triple-quote multi-line strings
SECTION_WAYSTONE = """Waystone: T{waystone_tier}
Pack Size: +{waystone_pack_size}%"""
```

**Template Architecture:**
- `SECTION_*` → Reusable template sections (waystone, session, drops)
- `TEMPLATE_*` → Phase-specific full templates (default, pre, post, waystone)
- `get_template_for_phase()` → Main dispatcher with conditional logic
- Helper functions → `_build_modifiers_section()`, `_build_session_context()`

**Template Variable Reuse:**
- Overlay uses **same 40+ variables** as notifications via `get_template_variables()`
- Zero duplication of data extraction logic
- Add variables once in `GameState` / `SessionManager`, available everywhere

**When modifying overlay templates:**
1. Always use single-line format with `\n` (never `"""` multi-line)
2. Use parentheses for multi-line template definitions
3. Add new sections as `SECTION_*` constants
4. Update `get_template_for_phase()` dispatcher for new phases
5. Test with `test_kiss_templates.py` (if exists)

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
| `kiss_overlay/kiss_overlay_templates.py` | Overlay templates | Modifying overlay display |
| `config.py` | All settings + validation | Adding config options |
| `game_state.py` | Central state management | Understanding state lifecycle |
| `CHANGELOG.md` | Release history | Understanding version changes |
| `docs/REFACTORING_SUMMARY_v034.md` | v0.3.4 refactoring details | Understanding recent changes |

## Quick Wins for Contributors

- **Add notification variable:** Extend `GameState` → update `get_template_variables()` → document
- **New ASCII theme:** Add to `ascii_themes.json` → reference in README
- **Support new hideout:** Add area code to `AUTO_HIDEOUT_AREAS` in `config.py`
- **Custom price source:** Extend `price_check_poe2.py` `_fetch_items_with_aliases()`

## Git Workflow & Commits

### Branching Strategy

**Two-Branch Model:** `main` (stable) + `develop` (active development)

```bash
# Branch Structure
main      → v0.3.4, v0.3.5 (tagged releases, production-ready)
develop   → Active development (30 commits/day is fine here)

# Optional: Feature branches for major work
feature/* → Short-lived, merge to develop when done
```

**Daily Workflow:**

```bash
# Work on develop branch
git checkout develop
# ... make changes, commit freely ...
git add <files>
git commit -m "feat: ✨ Add new feature"
git push origin develop

# When ready for release (e.g., v0.3.5)
git checkout main
git merge develop --ff-only  # Fast-forward only (keeps history clean)
git tag v0.3.5
git push origin main --tags

# Bump version in version.py, commit to develop
git checkout develop
# Update __version__ = "0.3.6" in version.py
git commit -m "chore: 🔖 Bump version to 0.3.6-dev"
```

**Optional Feature Branch Workflow** (for major features):

```bash
# Create feature branch from develop
git checkout develop
git checkout -b feature/weboverlay-rename

# ... 30 commits on feature branch ...

# Squash merge back to develop (clean history)
git checkout develop
git merge --squash feature/weboverlay-rename
git commit -m "feat: ✨ Rename OBS to WebOverlay with full refactor"
git branch -d feature/weboverlay-rename
```

**Why This Works:**
- ✅ `main` stays clean for users (releases only)
- ✅ `develop` allows rapid iteration without spamming users
- ✅ Users download from GitHub Releases (tagged on `main`)
- ✅ Contributors can follow active development on `develop`

## Memory Management

**MCP Memory Server** is available for persistent knowledge storage across chat sessions.

### When to Update Memory

Automatically update memory graph after:
- ✅ **Major features** - New systems like KISS Overlay, WebOverlay, Waystone Intelligence
- ✅ **Architecture changes** - Phase flow modifications, new patterns, core refactorings
- ✅ **Bug fixes** - Critical fixes that change behavior or require awareness
- ✅ **Important decisions** - Design choices, rejected approaches, lessons learned
- ✅ **Session milestones** - End of productive session with multiple commits

### Memory Entity Types

Use appropriate entity types for different knowledge:
- `feature` - Completed features (KISS Overlay, Auto-Detection, etc.)
- `architecture` - Design patterns (Phase-Based Flow, Template System)
- `core_pattern` - Critical rules (Session double-counting prevention)
- `security` - Security practices (credentials.txt handling)
- `workflow` - Development workflows (Git branching, gitmoji commits)
- `roadmap` - Planned features (WebOverlay rename, PySide6 migration)
- `session_notes` - Session summaries with commits and changes
- `user` - User preferences and environment details

### Memory Relations

Connect entities with meaningful relations:
- `is_feature_of` - Feature belongs to project
- `is_core_pattern_of` - Pattern is fundamental to project
- `powers` / `uses` - Component dependencies
- `documents_work_on` - Session notes about specific work
- `planned_for` - Future features for project
- `preferred_by` - User preferences

### Memory Best Practices

- 🎯 **Be specific** - Include file names, phase names, exact behavior
- 📊 **Quantify** - "40+ template variables", "9 POST phases", "500ms poll interval"
- 🔗 **Link entities** - Create relations to show connections
- 📝 **Session notes** - Document daily work with dates and commit references
- 🔄 **Update observations** - Add to existing entities instead of creating duplicates

**Note:** Memory is shared across all chat sessions - use it to maintain context!

## Questions to Ask User

When unclear:
1. Which phase should this logic run in? (See SESSION_FLOW.md)
2. Should this be configurable? (Add to Config class)
3. Does this need notification support? (Template variables)
4. Will this work on Windows only? (Target platform)
