# Changelog

All notable changes to DillaPoE2Stat will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.3] - 2025-10-05

### Added
- **Delirious Tracking**: Automatic detection and tracking of Delirious % from waystone suffixes
  - `waystone_delirious` variable available in notifications and game state
  - Logged to runs.jsonl for run analysis
  - Displayed in EXPERIMENTAL_PRE_MAP template
- **Formatted Drop Values**: All drop value variables now have `_fmt` versions for clean display
  - `map_drop_1/2/3_value_fmt`: Current map top drops
  - `last_map_drop_1/2/3_value_fmt`: Previous map top drops
  - `session_drop_1/2/3_value_fmt`: Session cumulative top drops
  - `best_map_value_fmt`: Best map value
- **Session Comparison Metrics**: New variable for accurate map vs session comparison
  - `session_value_per_hour_before_fmt`: Session ex/h BEFORE current map added
  - POST_MAP template now shows true comparison (map performance vs pre-existing average)

### Changed
- Data format version bumped to 2.1 (added delirious field to runs.jsonl)
- Updated POST_MAP template to use formatted drop values
- Updated EXPERIMENTAL_PRE_MAP template to show delirious percentage
- Notification templates now show map ex/h vs session avg BEFORE map (more accurate comparison)

### Fixed
- Session value comparison now excludes current map from average (prevents self-referential comparison)

## [0.3.2] - 2025-10-04

### Added
- **Top Drops Tracking**: Track top 3 most valuable items per map and across session
  - `current_map_top_drops`: Top drops from current/just completed map
  - `last_map_info.top_drops`: Top drops from previous completed map
  - `session_top_drops`: Cumulative top 3 drops across entire session
- **Best Map Tracking**: Automatically track highest value map in session
  - `best_map_info`: Name, tier, value, and runtime of best performing map
- **Enhanced Notification Variables**: All tracking data available in notification templates
  - `map_drop_1/2/3_name/stack/value`: Current map top drops
  - `last_map_drop_1/2/3_name/stack/value`: Previous map top drops
  - `session_drop_1/2/3_name/stack/value`: Session cumulative top drops
  - `best_map_name/tier/value/runtime`: Best map in session
- Documentation updates for new tracking features

### Changed
- Game state now maintains both current and previous map top drops for flexible templating
- Improved notification template documentation with clearer data flow explanations

## [0.3.1] - 2025-10-04

### Added
- Centralized version management system with `version.py`
- Version information exposed to notification templates
- Version display in startup banner
- Changelog tracking for release history
- Stable Windows toast notification App ID to prevent registry pollution

### Changed
- Refactored version management to single source of truth
- Updated config.py to use centralized version module
- Split App ID into display version (with version number) and registry version (stable)

### Fixed
- Waystone notification template using correct `waystone_drop_chance` variable
- Consistent variable naming across waystone area modifiers
- Template label clarity: "Way" renamed to "Waystone" for better readability
- Windows registry pollution from versioned toast App IDs

## [0.3.0] - 2025-09-30

### Added
- Automatic map detection with client log monitoring (`AutoMapDetector`)
- Waystone analyzer for experimental pre-map snapshots
- OBS overlay integration with Flask-based web server
- Modular architecture with dedicated managers for display, hotkeys, sessions, notifications
- HasiSkull startup dashboard with colorful ANSI art
- Data upgrade utilities for migrating runs.jsonl to format 2.0
- Configurable display tables with customizable column widths and ASCII themes
- Enhanced loot insights with efficiency tiers and color-coded strategies
- Divine Orb drop pattern analysis
- Rich session analytics dashboard
- Desktop notification system with template support

### Changed
- Refactored main loop into modular `poe_stats_refactored_v2.py`
- Enhanced price checker with Divine conversions and tiered icons
- Improved per-item chaos/exalted value tracking

### Fixed
- Compatibility with poe.ninja API changes
- Data format consistency across historic runs

## [0.2.0] - Earlier

### Added
- Initial session tracking system
- Basic inventory snapshot functionality
- Map tracking with client log parsing
- poe.ninja price integration
- Toast notifications for map events

## [0.1.0] - Initial Release

### Added
- Core inventory diffing functionality
- Basic loot valuation
- Simple console output
- Manual hotkey triggers (F2/F3)
