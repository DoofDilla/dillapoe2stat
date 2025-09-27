# Module Reference

This reference summarises every script that participates in the runtime tracker, the key classes/functions they expose, and the data they operate on. Use this as a starting point before diving into source files.

> **Tip:** The signatures below are simplified for readability. Check the actual modules for edge-case handling and additional keyword arguments.

## `poe_api.py`
Thin wrapper around the official Path of Exile API.

| Function | Description |
| --- | --- |
| `get_token(client_id, client_secret)` | Exchanges OAuth client credentials for an access token. Raises an HTTP error on failure. |
| `get_characters(access_token)` | Lists characters for the authenticated account. Returns the JSON payload from `/character/poe2`. |
| `get_character_details(access_token, name)` | Fetches the full character payload (inventory, equipment, etc.) by name. |
| `snapshot_inventory(access_token, name)` | Convenience helper that returns only the `character.inventory` list from `get_character_details`. |

## `poe_stats_refactored_v2.py`
Main orchestration script. See [Core Loop Overview](Core-Loop-Overview.md) for the full lifecycle. The table below highlights helpers that other modules call back into.

| Member | Description |
| --- | --- |
| `PoEStatsTracker.take_pre_snapshot()` | Handles PRE-map workflow, including reading `Client.txt`, caching waystone metadata, debug dumps, and notifications. |
| `PoEStatsTracker.take_post_snapshot()` | POST-map workflow; produces diffs, valuations, logging, and notifications. |
| `PoEStatsTracker.analyze_waystone()` | Experimental waystone preview invoked by `Ctrl+F2`. |
| `PoEStatsTracker.check_current_inventory_value()` | On-demand valuation without altering PRE/POST state. |
| `PoEStatsTracker.display_session_stats()` | Prints the rolling session dashboard using the log files. |

## `inventory_analyzer.py`
Inventory diffing and categorisation utilities.

| Function/Class | Description |
| --- | --- |
| `inv_key(item)` | Generates a stable identifier for an inventory item using ID, typeLine, coordinates, and baseType fallbacks. |
| `diff_inventories(before, after)` | Returns `(added, removed)` lists by comparing inventories with `inv_key`. |
| `InventoryAnalyzer.analyze_changes(pre, post)` | Wraps `diff_inventories` and returns metadata (counts, net change, sizes). |
| `InventoryAnalyzer.get_item_summary(items)` | Aggregates counts, unique types, and stack totals for display/debug. |
| `InventoryAnalyzer.categorize_items(items)` | Rough classification of items (currency, gems, equipment, consumables, other). |
| `InventoryAnalyzer.find_valuable_items(items, min_value)` | Heuristic to flag rare/interesting drops before pricing. |
| `InventoryAnalyzer.get_position_map(items)` | Maps `(x, y)` coordinates to items for spatial analysis. |
| `InventoryAnalyzer.detect_stash_changes(pre, post)` | Highlights items that moved slots, hinting at stash interactions. |

## `price_check_poe2.py`
Interfaces with poe.ninja’s economy API and performs valuation.

| Function | Description |
| --- | --- |
| `fetch_category_prices(category_key, league)` | Cached request for a poe.ninja overview, producing a name ➜ chaos value map with multiple lookup keys. |
| `exalted_price(league)` | Convenience accessor for the current Exalted Orb price (via currency overview). |
| `guess_category_from_item(item)` | Uses rarity, icon hints, and name heuristics to infer the best poe.ninja category. |
| `get_value_for_name_and_category(name, category, league)` | Looks up a single item name in a category, returning chaos and exalt equivalents. |
| `get_value_for_inventory_item(item, league)` | Full valuation pipeline for one inventory entry (manual overrides ➜ heuristics ➜ fallbacks). |
| `valuate_items_raw(items, league)` | Aggregates chaos/exalt totals per item name, returning row summaries plus `(sum_chaos, sum_ex)`. |

## `display.py`
All console output and table formatting.

| Function/Class | Description |
| --- | --- |
| `Colors` | ANSI escape definitions used throughout. |
| `DisplayManager.set_output_mode(mode)` | Switches between `normal` and `comprehensive` price views. |
| `DisplayManager.display_startup_info(...)` | Prints banners, hotkey help, and ASCII themed headers at startup. |
| `DisplayManager.display_inventory_changes(added, removed)` | Lists added/removed items (full detail in comprehensive mode). |
| `DisplayManager.display_price_analysis(added, removed, ...)` | Calls `valuate_items_raw`, renders price tables, and returns the map’s net value. |
| `DisplayManager.display_current_inventory_value(items)` | Snapshots and values the live inventory table. |
| `DisplayManager.display_session_progress(...)` | Shows session summary cards after each map. |
| `DisplayManager.display_session_stats(...)` | Pretty-prints the multi-map dashboard used on exit and `F7`. |

## `session_manager.py`
Session lifecycle, counters, and log integration.

| Function/Class | Description |
| --- | --- |
| `SessionManager.start_new_session()` | Generates a new session UUID, resets counters, and logs a start event. |
| `SessionManager.end_current_session()` | Logs an end event with runtime, value, and map count. |
| `SessionManager.add_completed_map(map_value)` | Increments counters after a POST snapshot and tallies map value. |
| `SessionManager.get_current_session_stats(runs_log_file)` | Combines live runtime with aggregated stats from `runs.jsonl`. |
| `SessionManager.get_session_progress()` | Lightweight progress dictionary for notifications (`maps`, `runtime`, `avg value`). |
| `SessionManager.is_session_active()` | Returns `True` when a session UUID is present. |

## `inventory_debug.py`
Optional tooling for verbose inspection.

| Function/Class | Description |
| --- | --- |
| `InventoryDebugger.dump_inventory_to_console(items, prefix)` | Pretty-prints each item in JSON when debug mode is active. |
| `InventoryDebugger.dump_inventory_to_file(items, filename_prefix, metadata)` | Writes a timestamped JSON snapshot inside `debug/`. |
| `InventoryDebugger.dump_item_summary(items, prefix)` | Produces tabular summaries and per-item deep dives, highlighting interesting loot. |
| `InventoryDebugger.find_and_analyze_item_by_name(items, name, prefix)` | (See source) Searches for items and prints contextual details. |
| `InventoryDebugger.analyze_item_detailed(item, index)` | Extracts categorical hints, properties, mods, and price lookup attempts for a single item. |

## `notification_manager.py`
Centralised Windows toast notifications (via `win11toast`).

| Function | Description |
| --- | --- |
| `notify_startup(session_info)` | Announces tracker startup, character, and hotkeys. |
| `notify_pre_map(map_info, session_progress)` | Summarises PRE snapshot context (map, session runtime/value). |
| `notify_post_map(map_info, map_runtime, map_value, session_progress)` | Reports map runtime, value, and updated session totals. |
| `notify_experimental_pre_map(waystone_info, session_progress)` | Shares cached waystone tier/modifier data. |
| `notify_inventory_check(inventory_items)` | Values the current inventory and surfaces the number of valuable drops. |
| `notify_session_start(session_info)` | Triggered when starting a fresh session (F6). |

## `waystone_analyzer.py`
Utilities for the experimental waystone workflow.

| Function/Class | Description |
| --- | --- |
| `WaystoneAnalyzer.find_waystone_in_inventory(items)` | Searches slot `(0, 0)` for an item whose `typeLine` contains “Waystone”. |
| `WaystoneAnalyzer.parse_waystone_info(item)` | Extracts name, tier, prefixes, suffixes, and select area modifiers for display/logging. |
| `WaystoneAnalyzer.take_experimental_pre_snapshot(...)` | Legacy helper that performs the full PRE snapshot + display cycle for experimentation. |

## `hotkey_manager.py`
Lightweight wrapper around the `keyboard` package.

| Function/Class | Description |
| --- | --- |
| `HotkeyManager.register_hotkey(key, callback, description)` | Registers a single hotkey and stores metadata for later listings. |
| `HotkeyManager.unregister_hotkey(key)` | Removes a specific binding. |
| `HotkeyManager.unregister_all()` | Clears all registered keys (used during shutdown). |
| `HotkeyManager.setup_default_hotkeys(tracker)` | Binds F2–F8 and Ctrl+F2 to the tracker methods. |
| `HotkeyManager.wait_for_exit_key(exit_key)` | Blocks until the exit key (default `Ctrl+Esc`) is pressed. |

## `client_parsing.py`
Reads `Client.txt` to figure out the last generated map instance.

| Function | Description |
| --- | --- |
| `get_last_map_from_client(path, scan_bytes)` | Scans the tail of the log file for the newest “Generating level …” line and returns its metadata. |
| `code_to_title(code)` | Converts internal map codes such as `MapAzmerianRanges` into display-friendly titles. |

## `poe_logging.py`
JSON Lines log writers/readers.

| Function | Description |
| --- | --- |
| `log_run(char, added, removed, map_info, map_value, log_file, map_runtime, session_id)` | Persists a map run, aggregating stacks and storing enriched map metadata. |
| `log_session_start(session_id, char, log_file)` | Appends a session start event to `sessions.jsonl`. |
| `log_session_end(session_id, char, runtime, value, map_count, log_file)` | Appends a session end event. |
| `get_session_stats(session_id, runs_log_file)` | Reads `runs.jsonl` and computes totals for the given session. |
| `aggregate(items)` | Helper that collapses a list of raw items into `{name, stack}` counts for logging. |

## `utils.py`
Grab bag of helpers used by the tracker and waystone analyser.

| Function | Description |
| --- | --- |
| `format_time(seconds)` | Formats seconds as “Hh Mm” or “Mm Ss”. |
| `get_current_timestamp()` | Returns `time.time()` (used to record PRE snapshot start time). |
| `validate_inventory_position(item, x, y)` | Checks whether an inventory item occupies coordinates `(x, y)`. |
| `extract_tier_from_typeline(type_line)` | Regex-based helper to obtain the numeric tier from strings like “Waystone (Tier 15)”. |
| `clean_mod_text(mod)` | Normalises mod strings by trimming whitespace and ignoring empties. |
| `create_empty_map_info(source)` | Returns a placeholder structure when real map data is unavailable. |
| `safe_get_nested_value(data, keys, default)` | Traverses nested dicts defensively, returning `default` on missing keys. |

Refer back to this page whenever you add new helpers—keeping it updated ensures the automation can push complete documentation to the GitHub Wiki.
