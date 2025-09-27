# Core Loop Overview

The heart of the project lives in [`poe_stats_refactored_v2.py`](../poe_stats_refactored_v2.py), which wires together modular managers to turn hotkey presses into Path of Exile API calls, inventory snapshots, and rich session analytics. This page outlines the major surfaces you will touch when extending the tracker.

## `PoEStatsTracker`
The `PoEStatsTracker` class orchestrates all runtime behaviour:

| Method | Purpose |
| --- | --- |
| `__init__(config=None)` | Instantiates configuration and manager classes. Inject a custom `Config` if you need overrides for tests or local experiments. |
| `initialize()` | Validates configuration, fetches an OAuth token via `poe_api.get_token`, verifies characters, registers hotkeys, and starts a new session. |
| `rate_limit(min_gap=None)` | Sleeps if necessary to honour `Config.API_RATE_LIMIT` between API calls. Call before any network request to Path of Exile. |
| `take_pre_snapshot()` | Stores the current timestamp, captures a PRE-map inventory via `poe_api.snapshot_inventory`, merges waystone metadata, notifies the user, and caches the inventory for a later diff. |
| `analyze_waystone()` | Runs the experimental waystone preview by taking a fresh snapshot, parsing the waystone in slot `(0, 0)`, and caching its metadata for the next PRE snapshot. |
| `take_post_snapshot()` | Requires a prior PRE snapshot. Captures a POST-map inventory, computes a diff with `InventoryAnalyzer`, values loot via `DisplayManager.display_price_analysis`, logs the run, and notifies the user. |
| `check_current_inventory_value()` | Performs an on-demand snapshot and valuation without altering PRE/POST state. |
| `debug_item_by_name(item_name)` | Snapshots the current inventory and asks `InventoryDebugger` to inspect items that match `item_name`. |
| `display_session_stats()` | Uses `SessionManager.get_current_session_stats` to print the current session dashboard. |
| `toggle_debug_mode()` | Flips `Config.DEBUG_ENABLED` and informs the `InventoryDebugger`. |
| `toggle_output_mode()` | Switches between `normal` and `comprehensive` presentation modes. |
| `start_new_session()` | Ends the active session (if any) and immediately starts/logs a new one. |
| `run()` | Entry point that calls `initialize()` and waits for `Ctrl+Esc` to exit. |
| `_cleanup()` | Gracefully unregisters hotkeys, prints a final session summary, and ends the active session. |

### Hotkey flow
Hotkeys are registered through `HotkeyManager.setup_default_hotkeys` during `initialize()`. Each hotkey directly calls the methods above. The `HotkeyManager.wait_for_exit_key('ctrl+esc')` call keeps the script alive until the user exits.

### Map lifecycle
1. **F2 – PRE snapshot**
   - Rate-limit check ➜ `snapshot_inventory`
   - Optionally dump debug info or summary tables
   - Parse `Client.txt` via `client_parsing.get_last_map_from_client`
   - Merge cached waystone data, display map info, and send a PRE notification
2. **F3 – POST snapshot**
   - Rate-limit check ➜ `snapshot_inventory`
   - Optional debug dumps
   - Compute runtime using `self.map_start_time`
   - `InventoryAnalyzer.analyze_changes` ➜ added/removed lists
   - `DisplayManager` prints diffs and valuations
   - `SessionManager.add_completed_map` updates totals
   - Notifications and logs are issued via `NotificationManager` and `poe_logging.log_run`

### Experimental waystone workflow
Pressing `Ctrl+F2` runs `analyze_waystone()`:
- Captures a live inventory snapshot
- Locates a waystone at `(0, 0)` and parses tier/modifiers with `WaystoneAnalyzer`
- Displays modifiers and caches them so the next PRE snapshot can enrich map info and logs with the waystone context

## Manager responsibilities
- **DisplayManager**: Rendering, ASCII themes, price tables, and net value calculations.
- **SessionManager**: Session lifecycle, counters, and exposing session progress for notifications.
- **InventoryAnalyzer**: Inventory diffs, categorisation, and heuristics for interesting items.
- **InventoryDebugger**: Debug dumps, targeted item analysis, and optional file exports.
- **NotificationManager**: Windows toast notifications for session and map events.
- **WaystoneAnalyzer**: Extracts tier/modifier data from the waystone item format.
- **HotkeyManager**: Wraps the `keyboard` library for easy registration/cleanup.

Use the table above to jump straight to the module-level documentation when you need more details on individual helper classes.
