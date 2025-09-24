# DillaPoE2Stat Tracker

> A hotkey-driven Path of Exile 2 map-tracking assistant that snapshots your inventory, values your loot through poe.ninja, and keeps rich session analytics with desktop notifications.

## Table of Contents
- [Overview](#overview)
- [Feature Highlights](#feature-highlights)
- [Repository Layout](#repository-layout)
- [Installation (Windows)](#installation-windows)
- [Quick Start](#quick-start)
  - [1. Gather prerequisites](#1-gather-prerequisites)
  - [2. Configure the tracker](#2-configure-the-tracker)
  - [3. Run the tracker](#3-run-the-tracker)
- [Usage Guide](#usage-guide)
  - [Hotkeys](#hotkeys)
  - [Output modes](#output-modes)
  - [Notifications](#notifications)
- [Data & Logs](#data--logs)
- [Debugging Toolkit](#debugging-toolkit)
- [How loot valuation works](#how-loot-valuation-works)
- [Troubleshooting](#troubleshooting)
- [Extending the Project](#extending-the-project)
- [Acknowledgements](#acknowledgements)

## Overview
DillaPoE2Stat is a Python toolkit that automates your Path of Exile 2 farming sessions. The refactored `poe_stats_refactored.py` script glues together OAuth-authenticated API calls, poe.ninja price lookups, inventory diffing, and session logging into a streamlined loop that you operate entirely with keyboard shortcuts. Whether you are min-maxing a single character or running long farming sessions, the tracker keeps consistent logs, highlights valuable drops, and summarizes your progress at a glance.

## Feature Highlights
- **Session-first workflow:** Start and finish map runs with two key presses while the tracker records runtimes, loot summaries, and session value trends automatically.
- **Modular architecture:** Dedicated modules handle configuration, display, logging, API access, hotkeys, and analytics so you can replace or extend individual layers with minimal friction.
- **Price intelligence:** poe.ninja data is cached and normalized for resilient lookups, ensuring consistent valuations across catalysts, runes, fragments, and more.
- **Debug-friendly:** Toggle verbose dumps, export inventories to JSON, or inspect category breakdowns mid-session without restarting the tool.
- **Windows-native niceties:** Global hotkeys and toast notifications keep you informed even when the terminal is minimized.

### Core capabilities
- 🔐 Securely authenticate against the official Path of Exile API, snapshot your character list, and capture inventory states on demand.
- ⌨️ Bind hotkeys to grab "pre" and "post" map inventories, toggle debug output, and flip between concise and comprehensive reporting without touching your mouse.
- 💰 Estimate the chaos- and exalt-equivalent value of your loot by querying poe.ninja's public economy endpoints and aggregating results per item name.
- 📊 Log every map run (inventory deltas, runtime, and pricing) alongside session metadata and present digestible progress summaries right in the terminal.
- 🔔 Send Windows toast notifications when a session starts, a map begins, or a run finishes, including runtime and value information.

## Repository Layout

| Path | Purpose |
| ---- | ------- |
| `poe_stats_refactored.py` | Main entry point; orchestrates hotkeys, inventory snapshots, notifications, and session analytics. |
| `poe_api.py` | Lightweight wrapper around the OAuth flow and character/inventory endpoints of the PoE API. |
| `price_check_poe2.py` | Fetches poe.ninja economy data, normalizes item names, and calculates chaos/exalt values. |
| `client_parsing.py` | Extracts the latest generated map instance from Path of Exile's `Client.txt` log. |
| `inventory_analyzer.py` | Diffs pre/post inventories and generates summaries, categories, and heuristics for valuable drops. |
| `inventory_debug.py` | Optional diagnostics for printing or exporting raw inventory JSON. |
| `poe_logging.py` | Persists per-run and per-session records to JSON Lines files and retrieves session statistics. |
| `display.py` | Centralized console formatting, color codes, and presentation logic. |
| `session_manager.py` | Tracks cumulative session runtime, value, and history. |
| `hotkey_manager.py` | Wraps the `keyboard` library for registering and cleaning up hotkeys. |
| `config.py` | Declarative configuration (credentials, character name, log paths, debug switches). |

Several legacy or experimental scripts (`poe_stats_with_inv_snapshot_with_hotkey_price2.py`, `poeninja_price_check*.py`, etc.) remain in the repository for reference.

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
2. Run the configuration sanity check:
   ```bash
   python -c "from config import Config; Config.print_config_summary()"
   ```
   (The `Config.print_config_summary()` helper also runs automatically when `poe_stats_refactored.py` starts.)

### 3. Run the tracker
With Path of Exile running and your character logged in:
```bash
python poe_stats_refactored.py
```
You will see a configuration summary, receive a Windows toast that monitoring has begun, and a list of active hotkeys. Keep the terminal open while you play.

## Usage Guide

### Hotkeys
| Key | Action |
| --- | ------ |
| `F2` | Capture the **pre-map** inventory snapshot and read the latest map info from `Client.txt`. |
| `F3` | Capture the **post-map** inventory, diff changes, evaluate loot value, and log the run. |
| `F4` | Toggle debug mode (enables verbose inventory dumps and file exports via `InventoryDebugger`). |
| `F5` | Run an on-demand inventory scan and display your current stash value. |
| `F6` | End the active session (persist summary) and immediately start a fresh one. |
| `F7` | Print the current session dashboard, including the last five maps. |
| `F8` | Switch between `normal` (valuable items only) and `comprehensive` output modes. |
| `Ctrl+Esc` | Gracefully exit the tracker and unregister all hotkeys. |

> Tip: The hotkeys are registered globally through the `keyboard` package—no terminal focus required.

### Output modes
- **Normal:** Minimal clutter; highlights only items whose chaos/exalt totals exceed 0.01.
- **Comprehensive:** Prints every added/removed item, category tags, stack counts, and raw chaos/exalt conversions.
Switch modes on the fly with `F8`.

### Inventory value check
- Tap `F5` at any time (even mid-map) to snapshot your current inventory and display a full valuation breakdown.
- The console highlights valuable finds, total chaos/exalt tallies, and how many items met the value threshold.
- When notifications are enabled you'll also receive a toast summarizing item counts and value.

### Notifications
- Startup, new session, map start, map completion, and manual inventory checks pop toast notifications (icon provided in `cat64x64.png`).
- Map start toasts include the current session runtime and total value so far.
- Completion toasts report map runtime/value alongside the running session totals.
- Disable notifications by setting `NOTIFICATION_ENABLED = False` in `config.py`.

## Data & Logs
- **Run history:** `runs.jsonl` stores a JSON record per map containing runtime, map metadata, aggregated loot, and valuation totals.
- **Session history:** `sessions.jsonl` records session start/end events, runtime, and cumulative value.
- **Debug exports:** When `DEBUG_TO_FILE` is `True`, inventories are written to timestamped JSON files inside the `debug/` folder.
- **Icon assets:** `cat64x64.png` is used for Windows toasts—swap it out if you prefer another image.

The session dashboard (triggered via `F7`) reads from `runs.jsonl` to compute averages and shows the five most recent maps so you can track streaks at a glance.

## Debugging Toolkit
- `InventoryDebugger` can print a compact table (`dump_item_summary`) or full JSON dumps (`dump_inventory_to_console`) of any snapshot.
- `InventoryAnalyzer` exposes helpers such as `get_item_summary`, `categorize_items`, and `find_valuable_items` for deeper insights or custom reports.
- Flip `DEBUG_ENABLED` and `DEBUG_TO_FILE` in `config.py` or press `F4` during runtime to toggle diagnostics without restarting.

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
- Swap the notification backend (Discord webhooks, OBS overlays) by editing the notifier calls in `poe_stats_refactored.py`.
- Add export commands (CSV, Google Sheets) by consuming the JSON Lines logs in `poe_logging.py`.
- Integrate controller support or macros using the `dualsense_*.py` experiments bundled in this repository.

## Acknowledgements
Thanks to Grinding Gear Games for exposing the Path of Exile API and poe.ninja for public economy data. This project was bootstrapped for Dilla's PoE 2 adventures—adapt it to your own grinding routine!
