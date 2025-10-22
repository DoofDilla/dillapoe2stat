# DillaPoE2Stat Tracker

> **v0.3.4 "Phase-Based Architecture"** - A hotkey-driven Path of Exile 2 map-tracking assistant that snapshots your inventory, values your loot through poe.ninja, and keeps rich session analytics with desktop notifications.
> Optional OBS overlay mode streams your loot breakdown and session dashboard straight into Browser Sources for easy broadcasting.

## What's New in v0.3.4

# DillaPoE2Stat Tracker

> **v0.3.5 "KISS Overlay"** - A hotkey-driven Path of Exile 2 map-tracking assistant that snapshots your inventory, values your loot through poe.ninja, and keeps rich session analytics with desktop notifications.
> Features a lightweight KISS overlay for streaming your loot breakdown and session dashboard.

## What's New in v0.3.5

- **🎨 KISS Overlay**: Brand new lightweight overlay system
  - Standalone overlay window with transparent background
  - Real-time updates via JSON state file (no Flask server needed)
  - 500ms polling for instant loot visibility
  - Template-based system with phase-aware displays
  - Clean separation: overlay reads state, tracker writes state
  - Easy to start: `start_overlay.bat` or directly via Python
- **✨ Uncut Gems Support**: Price checking now includes Uncut Skill/Spirit/Support Gems
- **📝 Enhanced Documentation**: Improved commit message enforcement with gitmoji rules
- **🔧 Better Configuration**: Clearer instructions for credentials and API setup

## Recent Enhancements (v0.3.0 - v0.3.5)
  - `MapFlowController` orchestrates PRE/POST flows in 9 clear, testable phases
  - Main script reduced from 787 to 640 lines (-18% code reduction)
  - Each phase has one responsibility: easier debugging and testing
- **� Flow Documentation**: New `docs/SESSION_FLOW.md` with complete diagrams, pitfalls, and testing guides
- **🐛 Robust Session Tracking**: Architecture prevents double-counting bugs by design
  - Single point of session update (Phase 5 only)
  - Clear BEFORE/AFTER state separation
- **🔧 Better Error Messages**: Phase-based errors ("Phase 5 failed") instead of generic messages
- **� Enhanced Documentation**: Architecture section in README, improved docstrings throughout

## Recent Enhancements (v0.3.0 - v0.3.4)

The tracker has evolved considerably with a complete modular rewrite and rich feature additions:

- **🤖 Automatic map detection loop:** A dedicated `AutoMapDetector` watches `Client.txt`, triggers PRE/POST snapshots when you zone between hideouts and maps, and can auto-run the waystone analyzer when you pass configured hubs. Toggle it in-game with `Ctrl+F6` for hands-free logging. 
- **🎯 Top Drops Tracking:** Track the 3 most valuable items per map and across your entire session - see what's actually making you currency
- **🏆 Best Map Tracking:** Automatically remembers your highest-value map of the session with full stats (name, tier, value, runtime)
- **🔮 Waystone Pre-Analysis:** Inspect waystones before running them - see tier, prefixes, suffixes, and Delirious % to make informed choices
- **🏗️ Modular v2 architecture:** `poe_stats_refactored_v2.py` wires together dedicated managers for display, hotkeys, sessions, notifications, and inventory diffing
- **💀 HasiSkull startup dashboard:** Tracker initialization splashes colorful ANSI art beside the configuration summary so you can confirm settings at a glance
- **📊 Deeper loot insights:** Run analytics highlight efficiency tiers, color-code top strategies, and surface Divine Orb drop patterns alongside the upgraded price checker
- **🔄 Data upgrade utilities:** Migrate existing `runs.jsonl` archives to the enhanced 2.1 format with full per-item chaos/exalted/Divine values
- **🎨 Configurable display:** Customize column widths, ASCII themes, and output preferences via `config.py` without touching core code
- **📺 OBS overlay mode:** Flask-backed overlay server with Browser Source URLs syncs your loot tables and session stats to your stream
- **🔔 Rich Notifications:** Template-based Windows toast system with formatted values, drop tracking, and session metrics

## Table of Contents
- [Recent Enhancements](#recent-enhancements)
- [Overview](#overview)
- [Feature Highlights](#feature-highlights)
- [Repository Layout](#repository-layout)
- [Documentation & Wiki](#documentation--wiki)
- [Installation (Windows)](#installation-windows)
- [Quick Start](#quick-start)
  - [1. Gather prerequisites](#1-gather-prerequisites)
  - [2. Configure the tracker](#2-configure-the-tracker)
  - [3. Run the tracker](#3-run-the-tracker)
- [Usage Guide](#usage-guide)
  - [Hotkeys](#hotkeys)
  - [Automatic map detection](#automatic-map-detection)
  - [Output modes](#output-modes)
  - [Experimental waystone analyzer](#experimental-waystone-analyzer)
  - [OBS overlay mode](#obs-overlay-mode)
  - [Notifications](#notifications)
  - [ASCII themes & visual tuning](#ascii-themes--visual-tuning)
- [Data & Logs](#data--logs)
- [Debugging Toolkit](#debugging-toolkit)
- [How loot valuation works](#how-loot-valuation-works)
- [Troubleshooting](#troubleshooting)
- [Extending the Project](#extending-the-project)
- [Acknowledgements](#acknowledgements)

## Overview
DillaPoE2Stat is a Python toolkit that automates your Path of Exile 2 farming sessions. The refreshed `poe_stats_refactored_v2.py` script glues together OAuth-authenticated API calls, poe.ninja price lookups, inventory diffing, and session logging into a streamlined loop that you operate entirely with keyboard shortcuts—or let the automatic detector drive the hotkeys for you. Whether you are min-maxing a single character or running long farming sessions, the tracker keeps consistent logs, highlights valuable drops, fires desktop toasts, and summarizes your progress at a glance with customizable ASCII theming and a celebratory HasiSkull banner at startup.

## Feature Highlights

### Core Tracking Features
- **📍 Session-First Workflow:** Start and finish map runs with two key presses while the tracker records runtimes, loot summaries, and session value trends automatically
- **🌀 Delirious % Tracking:** Automatic extraction from waystone suffixes - see which maps are delirious before and after completion
- **💎 Top Drops Analysis:** Track the 3 most valuable items per map, per session, and your best map ever
- **📊 Smart Session Metrics:** Compare map performance vs session average (calculated *before* current map for accuracy)
- **🔔 Formatted Notifications:** Clean currency formatting (12.5ex instead of 12.456789) throughout all toasts and overlays

### Automation & Analysis
- **🤖 Automatic Detection:** Background log monitoring triggers snapshots as you zone - focus on gameplay, not hotkeys
- **🔮 Waystone Pre-Analysis:** Inspect waystones before slotting them - see tier, mods, Delirious %, and make informed decisions
- **💰 Price Intelligence:** poe.ninja data cached and normalized for resilient lookups across catalysts, runes, fragments, waystones, and more
- **📈 Run Analytics:** Efficiency tiers, color-coded strategies, Divine Orb drop patterns, and per-map delirious correlations
- **🔄 Data Versioning:** Format 2.1 schema with upgrade utilities to migrate historical data without loss

### Display & Integration
- **🎨 Visual Polish:** ASCII footer themes, dynamic emoji detection, comprehensive item tables, and HasiSkull startup banner
- **📺 OBS Overlays:** Built-in Flask server mirrors loot tables and session dashboards as browser sources for streaming
- **🪟 Windows-Native:** Global hotkeys and toast notifications keep you informed even when the terminal is minimized
- **🐛 Debug-Friendly:** Toggle verbose dumps, export inventories to JSON, inspect categories mid-session, search items by name

### Architecture & Extensibility
- **🏗️ Modular Design:** Dedicated modules for config, display, logging, API access, hotkeys, notifications, and analytics
- **� Easy Extension:** Replace or extend individual layers with minimal friction - clean interfaces throughout
- **📝 Template System:** Customizable notification templates with 40+ variables including drops, session stats, and waystone data
- **💾 Persistent Logging:** JSON Lines format for runs and sessions - easily parsed by external tools or custom scripts

## Repository Layout

| Path | Purpose |
| ---- | ------- |
| `poe_stats_refactored_v2.py` | Main entry point; orchestrates hotkeys, inventory snapshots, notifications, and session analytics via modular managers. |
| `poe_api.py` | Lightweight wrapper around the OAuth flow and character/inventory endpoints of the PoE API. |
| `price_check_poe2.py` | Fetches poe.ninja economy data, normalizes item names, and calculates chaos/exalt values. |
| `client_parsing.py` | Extracts the latest generated map instance from Path of Exile's `Client.txt` log. |
| `inventory_analyzer.py` | Diffs pre/post inventories, categorizes loot, and feeds price valuation. |
| `inventory_debug.py` | Optional diagnostics for printing or exporting raw inventory JSON, plus targeted item search. |
| `poe_logging.py` | Persists per-run and per-session records to JSON Lines files and retrieves session statistics. |
| `display.py` | Centralized console formatting, ASCII footer themes, emoji logic, and presentation tables. |
| `session_manager.py` | Tracks cumulative session runtime, map history, and session summaries. |
| `hotkey_manager.py` | Wraps the `keyboard` library for registering and cleaning up hotkeys. |
| `notification_manager.py` | Sends Windows toast notifications with formatted currency values, drop tracking, and session metrics. |
| `notification_templates.py` | Template definitions with 40+ variables including drops, delirious %, session stats, and waystone data. |
| `waystone_analyzer.py` | Parses waystones for tier, mods, and Delirious % extraction from suffixes. |
| `run_analyzer.py` | Analyzes historical run data from runs.jsonl with efficiency tiers and delirious correlations. |
| `session_manager.py` | Tracks cumulative session runtime, map history, best map, and top drops across session. |
| `session_display.py` | Renders session dashboards with Divine Orb trends and color-coded performance metrics. |
| `version.py` | Single source of truth for version information and data format versioning. |
| `ascii_theme_manager.py` / `ascii_themes.json` | Configure decorative footer themes and timestamp styling. |
| `config.py` | Declarative configuration (credentials, character name, log paths, debug switches, table/visual settings). |
| `CHANGELOG.md` | Detailed release history tracking all features, changes, and fixes. |

Several legacy or experimental scripts (`poe_stats_with_inv_snapshot_with_hotkey_price2.py`, `poeninja_price_check*.py`, etc.) remain in the repository for reference.

## Documentation & Wiki

- The in-repo wiki lives under [`docs/wiki/`](docs/wiki/). Pages are written using GitHub-flavoured Markdown so they render both here and inside the hosted GitHub Wiki.
- Start from [`docs/wiki/Home.md`](docs/wiki/Home.md) for navigation links to the core loop overview, module reference, and external API documentation.
- A GitHub Actions workflow ([`.github/workflows/wiki-sync.yml`](.github/workflows/wiki-sync.yml)) mirrors the folder into the GitHub Wiki whenever changes land on `main`. Edit pages in-repo to keep the wiki source of truth under version control.

## Installation (Windows)

1. **Install Python (if needed):** Follow the [official Python for Windows installation guide](https://docs.python.org/3/using/windows.html#installing-python). The tracker assumes a working Python 3.10+ environment is already configured on your system.
2. **Download the project:** Clone this repository or extract a ZIP of the latest release into a convenient folder, e.g. `C:\Tools\DillaPoE2Stat`.
3. **(Recommended) Create a virtual environment:**
   ```powershell
   cd C:\Tools\DillaPoE2Stat
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. **Install required packages:** Use `pip` to install the dependencies listed in [`requirements.txt`](requirements.txt).
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. **Verify optional tools:** If you plan to experiment with auxiliary scripts (e.g., DualSense helpers), also install any optional packages they mention in their module headers.

> **Tip:** When re-opening a new PowerShell session, reactivate the virtual environment with `.\.venv\Scripts\Activate.ps1` before running the tracker.

## Quick Start

### 1. Gather prerequisites
- **Operating system:** Windows 10/11 (required for `win11toast` notifications and low-level keyboard hooks).
- **Python:** 3.10 or newer is recommended.
- **Path of Exile account:** Create an OAuth client ID/secret via the [Path of Exile Developer Portal](https://www.pathofexile.com/developer/docs/api) with `account:characters` and `account:profile` scopes.
- **Game log access:** Locate your `Client.txt` log (typically under `Documents\My Games\Path of Exile 2\logs` or your custom install path).
- **Python dependencies:** Install the core libraries with `pip install -r requirements.txt`. Optional utilities (used by side scripts) include `pywin32`, `pydualsense`, and `pynput`.

### 2. Configure the tracker
1. Open [`config.py`](config.py) and adjust:
   - `CLIENT_ID` / `CLIENT_SECRET` to match your PoE OAuth application.
   - `CHAR_TO_CHECK` to the character you want to monitor.
   - `CLIENT_LOG` to the absolute path of your `Client.txt`.
   - Toggle `OUTPUT_MODE`, `DEBUG_ENABLED`, and related flags as desired.
   - (Optional) Flip `AUTO_DETECTION_ENABLED` to `True` or tweak the `AUTO_*` area sets if you want the automatic loop to start enabled or recognise custom hideouts.
2. (Optional) Enable OBS overlays by setting `OBS_ENABLED = True`. Adjust `OBS_HOST`, `OBS_PORT`, `OBS_AUTO_START`, and `OBS_QUIET_MODE` if you want the Flask web server to start automatically or surface request logs while testing scene layouts.
3. Run the configuration sanity check:
   ```bash
   python -c "from config import Config; Config.print_config_summary()"
   ```
   (The `Config.print_config_summary()` helper also runs automatically when `poe_stats_refactored_v2.py` starts.)

### 3. Run the tracker
With Path of Exile running and your character logged in:
```bash
python poe_stats_refactored_v2.py
```
You will see a HasiSkull banner plus the configuration summary, receive a Windows toast that monitoring has begun, and a list of active hotkeys (including the experimental waystone analyzer, OBS controls, and the auto-detection toggle). Keep the terminal open while you play.

Tap `Ctrl+F6` after the startup banner if you prefer the tracker to trigger PRE/POST snapshots automatically while you focus on gameplay.

If the OBS server is enabled (or you toggle it on mid-run with `F9`), the console prints the Browser Source URLs you can paste into OBS Studio.

## Usage Guide

### Hotkeys
| Key | Action |
| --- | ------ |
| `F2` | Capture the **pre-map** inventory snapshot and read the latest map info from `Client.txt` (augmented with cached waystone data when available). |
| `Ctrl+F2` | Run the **experimental waystone analyzer**, exposing prefixes/suffixes and caching the results for the next `F2`. |
| `F3` | Capture the **post-map** inventory, diff changes, evaluate loot value, update session totals, and log the run. |
| `Ctrl+Shift+F2` | Simulate a pre-map snapshot (helpful for rehearsal and overlay layout tests). |
| `Ctrl+Shift+F3` | Simulate a post-map snapshot to preview notifications and OBS overlays without running a map. |
| `F4` | Toggle debug mode (enables verbose inventory dumps and file exports via `InventoryDebugger`). |
| `F5` | Run an on-demand inventory scan and display your current stash value with smart emoji hints. |
| `F6` | End the active session (persist summary) and immediately start a fresh one. |
| `Ctrl+F6` | Toggle the automatic map detection loop that fires `F2`/`F3` (and optional waystone scans) when you zone. |
| `F7` | Print the current session dashboard, including the last five maps. |
| `F8` | Switch between `normal` (valuable items only) and `comprehensive` output modes. |
| `F9` | Toggle the OBS overlay web server on/off (prints Browser Source URLs when enabled). |
| `Ctrl+Esc` | Gracefully exit the tracker and unregister all hotkeys. |

> Tip: The hotkeys are registered globally through the `keyboard` package—no terminal focus required.

### Automatic map detection
- Press `Ctrl+F6` once to let the tracker watch `Client.txt` for area transitions. Hideout/town → map triggers an automatic PRE snapshot, while map → hideout fires the POST snapshot so your runs are logged without touching `F2`/`F3`.
- When you pass through configured hubs (e.g., Well of Souls) the detector can queue a waystone analysis automatically, mimicking a manual `Ctrl+F2`.
- The loop respects abyss/breach detours so it stays in “map mode” until you actually zone home again.
- Tweak intervals and which area codes count as hideouts, towns, or waystone triggers via the `AUTO_*` settings near the bottom of `config.py` if your layout differs.

### Output modes
- **Normal:** Minimal clutter; highlights only items whose chaos/exalt totals exceed 0.01.
- **Comprehensive:** Prints every added/removed item, category tags, stack counts, and raw chaos/exalt conversions (with optional zero-value rows when `SHOW_ALL_ITEMS` is enabled).
Switch modes on the fly with `F8`.

### Inventory value check
- Tap `F5` at any time (even mid-map) to snapshot your current inventory and display a full valuation breakdown.
- The console highlights valuable finds, optional zero-value rows, total chaos/exalt tallies, and how many items met the value threshold.
- When notifications are enabled you'll also receive a toast summarizing item counts and value.

### Experimental waystone analyzer
- Press `Ctrl+F2` with a waystone in the top-left inventory slot to inspect its tier, prefixes, suffixes, and Delirious % without starting a map.
- The analyzer caches tier and modifier counts so the next `F2` snapshot displays richer map context and notifications include the tier and delirious % automatically.
- Delirious percentage is extracted from the first suffix using pattern matching: "X% Delirious" or "Delirious X%"
- Debug mode prints extra traces for troubleshooting waystone parsing.

### OBS overlay mode
- Toggle the Flask web server at any time with `F9`. Successful startups print:
  - `http://<host>:<port>/obs/item_table` – Loot recap table sized for a ~600×400 Browser Source.
  - `http://<host>:<port>/obs/session_stats` – Slim session dashboard ideal for a ~300×200 Browser Source.
- In OBS Studio add a **Browser Source**, paste the printed URL, set the suggested width/height, and enable *Refresh browser when scene becomes active* plus *Shutdown source when not visible* to avoid stale overlays.
- Overlays refresh whenever you finish a map and mirror the same emoji/value formatting shown in the terminal.
- Use the simulation hotkeys (`Ctrl+Shift+F2` / `Ctrl+Shift+F3`) to test overlay styling without running real maps.

### Notifications
- Startup, new session, experimental waystone analysis, map start, map completion, and manual inventory checks pop toast notifications (icon provided in `cat64x64.png`).
- **Map start toasts** include current session runtime, total value, and session average ex/h.
- **Completion toasts** report map runtime/value/ex/h alongside session totals and comparison to pre-map session average.
- **Formatted values** throughout: All currency displays use clean formatting (e.g., "12.5ex" instead of "12.456789").
- **Top drops tracking**: See your 3 most valuable drops per map and session cumulative best drops.
- **Delirious tracking**: Waystone analyzer and map notifications show Delirious % when present.
- **Template customization**: Edit `notification_templates.py` to customize messages - 40+ variables available including drops, session stats, waystone data, and more.
- Disable notifications by setting `NOTIFICATION_ENABLED = False` in `config.py`.

### ASCII themes & visual tuning
- Pick a footer theme by setting `ASCII_THEME` in `config.py` (options live in `ascii_themes.json`).
- Adjust table widths, separator characters, and whether to show zero-value loot through the `TABLE_*` and `SHOW_ALL_ITEMS` flags.
- Theme rendering gracefully falls back to safe ASCII if your terminal cannot display the chosen Unicode glyphs.

## Data & Logs
- **Run history:** `runs.jsonl` stores a JSON record per map containing runtime, map metadata (tier, delirious %, cached waystone data), aggregated loot, and per-item chaos/exalted/Divine valuations in the enhanced 2.1 format.
- **Session history:** `sessions.jsonl` records session start/end events, runtime, cumulative value, best map, top drops, and per-map history for the in-terminal dashboard.
- **Data versioning:** Current DATA_FORMAT_VERSION is 2.1 (adds delirious field). Version 2.0 added per-item valuations.
- **Data upgrades:** Run `upgrade_runs_data.py` to back up and convert legacy run entries so every item inherits the new valuation fields without losing history.
- **Debug exports:** When `DEBUG_TO_FILE` is `True`, inventories are written to timestamped JSON files inside the `debug/` folder.
- **Icon assets:** `cat64x64.png` is used for Windows toasts—swap it out if you prefer another image.

The session dashboard (triggered via `F7`) reads from `runs.jsonl` to compute averages and shows the five most recent maps so you can track streaks at a glance. For deep dives, the standalone analyzers in `run_analyzer.py` and `session_display.py` crunch the same enhanced logs to color-code efficiency, surface Divine Orb trends, correlate delirious % with performance, and recommend waystone strategies.

## Debugging Toolkit
- `InventoryDebugger` can print a compact table (`dump_item_summary`), full JSON dumps (`dump_inventory_to_console`), export snapshots to disk, or search for an individual item by name.
- `InventoryAnalyzer` exposes helpers such as `analyze_changes`, `categorize_items`, and `find_valuable_items` for deeper insights or custom reports.
- `WaystoneAnalyzer` parses experimental waystone metadata (tier, mods, delirious %), validates slot placement, and caches attributes for the next run.
- `run_analyzer.py` and `session_display.py` provide post-run deep dives with color-coded efficiency tiers, Divine Orb drop breakdowns, delirious correlation analysis, and modifier pattern detection for your best maps.
- Flip `DEBUG_ENABLED` and `DEBUG_TO_FILE` in `config.py` or press `F4` during runtime to toggle diagnostics without restarting.
- Adjust `DEBUG_SHOW_SUMMARY` to swap between concise summaries and exhaustive JSON dumps.
- Check `CHANGELOG.md` for detailed version history and `version.py` for current version and data format info.

## How loot valuation works
1. The tracker hands `InventoryAnalyzer`'s "added" list to `price_check_poe2.valuate_items_raw`.
2. `price_check_poe2` fetches poe.ninja overview data per category (currency, catalysts, waystones, etc.) and normalizes item names to improve match rates.
3. Each item now receives chaos, exalted, and Divine Orb equivalents while category-aware icons flag catalysts, waystones, fragments, and more.
4. Results are aggregated per item type (including stack sizes) and persisted back into `runs.jsonl` with full per-item valuation metadata (format version 2.1).
5. Top 3 most valuable items are tracked separately for current map, last map, and cumulative session.
6. Any items below the `0.01c` threshold are omitted from normal mode to keep noise low, but comprehensive mode and the analyzers still capture the full data for post-run studies.
7. All notification displays use formatted currency values via `_format_currency()` for clean, readable output.

## Troubleshooting
| Symptom | Possible Cause & Fix |
| ------- | -------------------- |
| `Config` errors about missing `Client.txt` | Update `CLIENT_LOG` to the correct absolute path; ensure the game has created the log file. |
| Hotkeys do not trigger | Run the terminal as Administrator, ensure no other app is capturing the same keys, and confirm the `keyboard` package installed correctly. |
| API requests fail with 401 | Double-check `CLIENT_ID`/`CLIENT_SECRET` and verify the OAuth app has `account:characters account:profile` scopes. |
| No loot valuation shown | poe.ninja may be rate-limiting or lacking data for the selected league; try again later or switch leagues in `price_check_poe2.LEAGUE`. |
| Toast notifications missing | `win11toast` requires Windows 10/11—disable notifications in `config.py` when running on unsupported systems. |

## Architecture

The tracker uses a **phase-based flow architecture** for clean, maintainable code:

### Core Components

- **`MapFlowController`**: Orchestrates PRE/POST map tracking in 9 clear phases
  - Phase 1-4 (PRE): Snapshot → Parse → State → Notify
  - Phase 1-9 (POST): Snapshot → Diff → Value → Capture → Update → Notify → Log → Display → Reset
- **`InventorySnapshotService`**: API calls with automatic rate limiting
- **`GameState`**: Central state management for maps, session, tracking data
- **`SessionManager`**: Session lifecycle and statistics
- **`DisplayManager`**: Console output formatting
- **`NotificationManager`**: Windows toast notifications

### Flow Documentation

See **[`docs/SESSION_FLOW.md`](docs/SESSION_FLOW.md)** for detailed flow diagrams, phase descriptions, common pitfalls, and testing procedures.

**Key Benefits:**
- ✅ Each phase has one clear responsibility
- ✅ Easy to test individual phases
- ✅ Clear error messages ("Phase 5 failed" vs "POST failed")
- ✅ Well-documented session tracking prevents double-counting bugs

## Extending the Project
- **Custom Analytics:** Implement stash tab scraping or price thresholds using `InventoryAnalyzer.categorize_items` as a base.
- **Alternative Notifications:** Swap the notification backend (Discord webhooks, Telegram bots, custom OBS overlays) by editing the notifier calls in `poe_stats_refactored_v2.py` or `notification_manager.py`.
- **Template Customization:** Edit `notification_templates.py` to create custom notification messages - 40+ variables available including all drop tracking, session metrics, waystone data, and delirious %.
- **Data Export:** Add export commands (CSV, Google Sheets, database) by consuming the JSON Lines logs in `poe_logging.py` - format version 2.1 includes full per-item valuations and delirious tracking.
- **Run Analysis:** Extend `run_analyzer.py` to correlate delirious % with drop quality, find optimal waystone mod combinations, or analyze efficiency by tier.
- **Controller Integration:** Integrate controller support or macros using the `dualsense_*.py` experiments bundled in this repository.
- **Custom Overlays:** Build additional Flask endpoints in `obs_web_server.py` for specialized stream overlays or monitoring dashboards.

## Acknowledgements
Thanks to Grinding Gear Games for exposing the Path of Exile API and poe.ninja for public economy data. Special thanks to the PoE community for feedback and testing. This project was bootstrapped for Dilla's PoE 2 adventures—adapt it to your own grinding routine!

## Version History
See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

**Current Version:** 0.3.4 "Phase-Based Architecture"  
**Data Format Version:** 2.1  
**Last Updated:** October 5, 2025
