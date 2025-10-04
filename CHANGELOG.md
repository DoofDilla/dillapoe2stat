# Changelog

All notable changes to DillaPoE2Stat will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Centralized version management system with `version.py`
- Version information exposed to notification templates
- Version display in startup banner
- Changelog tracking for release history

### Changed
- Refactored version management to single source of truth
- Updated config.py to use centralized version module

## [0.3.1] - 2025-10-04

### Fixed
- Waystone notification template using correct `waystone_drop_chance` variable
- Consistent variable naming across waystone area modifiers
- Template label clarity: "Way" renamed to "Waystone" for better readability

### Changed
- Improved notification template variable naming consistency

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
