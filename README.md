# DillaPoE2Stat Tracker

> A hotkey-driven Path of Exile 2 map-tracking assistant that snapshots your inventory, values your loot through poe.ninja, and keeps rich session analytics with desktop notifications.
> Optional OBS overlay mode streams your loot breakdown and session dashboard straight into Browser Sources for easy broadcasting.

## Recent Enhancements

The tracker has evolved considerably since the last pull request. Highlights include:

- **Modular v2 main loop:** `poe_stats_refactored_v2.py` is now the recommended entry point, wiring together dedicated managers for display, hotkeys, sessions, notifications, and inventory diffing.
- **Experimental waystone workflow:** `Ctrl+F2` inspects a waystone before a run, surfaces prefixes/suffixes, and enriches the subsequent `F2` map snapshot with cached tier data.
- **Smart visual output:** ASCII footer themes, richer emoji mapping, and optional "show all items" tables make the terminal dashboard more legible at a glance.
- **Notification control:** A centralized `NotificationManager` feeds Windows toasts for startup, experimental waystone checks, map transitions, inventory scans, and session milestones.
- **Configurable display tables:** New settings in `config.py` expose column widths, ASCII themes, and output preferences so you can tailor summaries without touching core code.
- **OBS overlay mode:** Spin up a Flask-backed overlay server, drop Browser Source URLs into OBS, and keep stream viewers synced with your latest loot and session stats.

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
DillaPoE2Stat is a Python toolkit that automates your Path of Exile 2 farming sessions. The refreshed `poe_stats_refactored_v2.py` script glues together OAuth-authenticated API calls, poe.ninja price lookups, inventory diffing, and session logging into a streamlined loop that you operate entirely with keyboard shortcuts. Whether you are min-maxing a single character or running long farming sessions, the tracker keeps consistent logs, highlights valuable drops, fires desktop toasts, and summarizes your progress at a glance with customizable ASCII theming.

## Feature Highlights
- **Session-first workflow:** Start and finish map runs with two key presses while the tracker records runtimes, loot summaries, and session value trends automatically.
- **Modular architecture:** Dedicated modules handle configuration, display, logging, API access, hotkeys, notifications, and analytics so you can replace or extend individual layers with minimal friction.
- **Price intelligence:** poe.ninja data is cached and normalized for resilient lookups, ensuring consistent valuations across catalysts, runes, fragments, and more.
- **Debug-friendly:** Toggle verbose dumps, export inventories to JSON, inspect category breakdowns mid-session without restarting the tool, or search for a single item by name.
- **Visual polish:** ASCII footer themes, dynamic emoji detection, and comprehensive item tables make the terminal output readable even during marathon sessions.
- **Windows-native niceties:** Global hotkeys and toast notifications keep you informed even when the terminal is minimized.
- **Stream-ready overlays:** Built-in OBS overlay server (Flask) mirrors loot tables and session dashboards as browser sources for streaming or recording.

### Core capabilities
- 🔐 Securely authenticate against the official Path of Exile API, snapshot your character list, and capture inventory states on demand.
- ⌨️ Bind hotkeys to grab "pre" and "post" map inventories, toggle debug output, and flip between concise and comprehensive reporting without touching your mouse.
- 💰 Estimate the chaos- and exalt-equivalent value of your loot by querying poe.ninja's public economy endpoints and aggregating results per item name.
- 🧪 Analyze a waystone before slotting it in, preview its prefixes/suffixes, and carry its tier data into the next `F2` map snapshot.
- 📊 Log every map run (inventory deltas, runtime, and pricing) alongside session metadata and present digestible progress summaries right in the terminal.
- 🔔 Send Windows toast notifications when a session starts, a map begins, a waystone is inspected, an inventory check finishes, or a run completes.

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
| `notification_manager.py` | Sends Windows toast notifications for lifecycle events and inventory checks. |
| `waystone_analyzer.py` | Parses waystones for experimental map previews and caches tier/mod info. |
| `ascii_theme_manager.py` / `ascii_themes.json` | Configure decorative footer themes and timestamp styling. |
| `config.py` | Declarative configuration (credentials, character name, log paths, debug switches, table/visual settings). |

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
You will see a configuration summary, receive a Windows toast that monitoring has begun, and a list of active hotkeys (including the experimental waystone analyzer and OBS controls). Keep the terminal open while you play.

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
| `F7` | Print the current session dashboard, including the last five maps. |
| `F8` | Switch between `normal` (valuable items only) and `comprehensive` output modes. |
| `F9` | Toggle the OBS overlay web server on/off (prints Browser Source URLs when enabled). |
| `Ctrl+Esc` | Gracefully exit the tracker and unregister all hotkeys. |

> Tip: The hotkeys are registered globally through the `keyboard` package—no terminal focus required.

### Output modes
- **Normal:** Minimal clutter; highlights only items whose chaos/exalt totals exceed 0.01.
- **Comprehensive:** Prints every added/removed item, category tags, stack counts, and raw chaos/exalt conversions (with optional zero-value rows when `SHOW_ALL_ITEMS` is enabled).
Switch modes on the fly with `F8`.

### Inventory value check
- Tap `F5` at any time (even mid-map) to snapshot your current inventory and display a full valuation breakdown.
- The console highlights valuable finds, optional zero-value rows, total chaos/exalt tallies, and how many items met the value threshold.
- When notifications are enabled you'll also receive a toast summarizing item counts and value.

### Experimental waystone analyzer
- Press `Ctrl+F2` with a waystone in the top-left inventory slot to inspect its tier, prefixes, and suffixes without starting a map.
- The analyzer caches tier and modifier counts so the next `F2` snapshot displays richer map context and notifications include the tier automatically.
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
- Map start toasts include the current session runtime and total value so far.
- Completion toasts report map runtime/value alongside the running session totals.
- Disable notifications by setting `NOTIFICATION_ENABLED = False` in `config.py`.

### ASCII themes & visual tuning
- Pick a footer theme by setting `ASCII_THEME` in `config.py` (options live in `ascii_themes.json`).
- Adjust table widths, separator characters, and whether to show zero-value loot through the `TABLE_*` and `SHOW_ALL_ITEMS` flags.
- Theme rendering gracefully falls back to safe ASCII if your terminal cannot display the chosen Unicode glyphs.

## Data & Logs
- **Run history:** `runs.jsonl` stores a JSON record per map containing runtime, map metadata (augmented with cached waystone tiers when available), aggregated loot, and valuation totals.
- **Session history:** `sessions.jsonl` records session start/end events, runtime, cumulative value, and per-map history for the in-terminal dashboard.
- **Debug exports:** When `DEBUG_TO_FILE` is `True`, inventories are written to timestamped JSON files inside the `debug/` folder.
- **Icon assets:** `cat64x64.png` is used for Windows toasts—swap it out if you prefer another image.

The session dashboard (triggered via `F7`) reads from `runs.jsonl` to compute averages and shows the five most recent maps so you can track streaks at a glance.

## Debugging Toolkit
- `InventoryDebugger` can print a compact table (`dump_item_summary`), full JSON dumps (`dump_inventory_to_console`), export snapshots to disk, or search for an individual item by name.
- `InventoryAnalyzer` exposes helpers such as `analyze_changes`, `categorize_items`, and `find_valuable_items` for deeper insights or custom reports.
- `WaystoneAnalyzer` parses experimental waystone metadata, validates slot placement, and caches attributes for the next run.
- Flip `DEBUG_ENABLED` and `DEBUG_TO_FILE` in `config.py` or press `F4` during runtime to toggle diagnostics without restarting.
- Adjust `DEBUG_SHOW_SUMMARY` to swap between concise summaries and exhaustive JSON dumps.

## How loot valuation works
1. The tracker hands `InventoryAnalyzer`'s "added" list to `price_check_poe2.valuate_items_raw`.
2. `price_check_poe2` fetches poe.ninja overview data per category (currency, catalysts, waystones, etc.) and normalizes item names to improve match rates.
3. Each item receives a chaos value and, if the Exalted Orb price is known, an exalt equivalent.
4. Results are aggregated per item type (including stack sizes) to produce totals and net value readouts.
5. Any items below the `0.01c` threshold are omitted from normal mode to keep noise low.

## Troubleshooting
| Symptom | Possible Cause & Fix |
| ------- | -------------------- |
| `Config` errors about missing `Client.txt` | Update `CLIENT_LOG` to the correct absolute path; ensure the game has created the log file. |
| Hotkeys do not trigger | Run the terminal as Administrator, ensure no other app is capturing the same keys, and confirm the `keyboard` package installed correctly. |
| API requests fail with 401 | Double-check `CLIENT_ID`/`CLIENT_SECRET` and verify the OAuth app has `account:characters account:profile` scopes. |
| No loot valuation shown | poe.ninja may be rate-limiting or lacking data for the selected league; try again later or switch leagues in `price_check_poe2.LEAGUE`. |
| Toast notifications missing | `win11toast` requires Windows 10/11—disable notifications in `config.py` when running on unsupported systems. |

## Extending the Project
- Implement stash tab scraping or price thresholds using `InventoryAnalyzer.categorize_items` as a base.
- Swap the notification backend (Discord webhooks, OBS overlays) by editing the notifier calls in `poe_stats_refactored_v2.py` or `notification_manager.py`.
- Add export commands (CSV, Google Sheets) by consuming the JSON Lines logs in `poe_logging.py`.
- Integrate controller support or macros using the `dualsense_*.py` experiments bundled in this repository.

## Acknowledgements
Thanks to Grinding Gear Games for exposing the Path of Exile API and poe.ninja for public economy data. This project was bootstrapped for Dilla's PoE 2 adventures—adapt it to your own grinding routine!
