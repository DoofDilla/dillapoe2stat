# Changelog

All notable changes to DillaPoE2Stat will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-10-22

### Added
- **🔐 OAuth 2.1 Migration**: Complete replacement of deprecated client_credentials flow
  - New `oauth_flow.py` module with PKCE implementation (400 lines)
  - `PKCEGenerator`: Creates code_verifier and SHA256 code_challenge
  - `CallbackHandler`: HTTP server receives authorization codes on port 8080
  - `OAuthFlow`: Browser-based authorization with automatic callback handling
  - `TokenManager`: Automatic token storage, loading, and refresh logic
  - Public Client configuration (no client secret required)
  - Authorization Code Grant with PKCE (Proof Key for Code Exchange)
  - Token lifetimes: 10h access tokens, 7d refresh tokens
- **🛡️ Secure Token Storage**: `tokens.json` with automatic gitignore
  - Stores access_token, refresh_token, expires_at, username
  - Auto-refresh before expiration
  - Browser re-authorization after 7 days
- **🌐 User-Agent Header**: Added to all OAuth requests to prevent Cloudflare blocking
- **📝 OAuth Documentation**: Updated README with Public Client setup instructions

### Changed
- **Deprecated Manual Credentials**: `CLIENT_ID`/`CLIENT_SECRET` in `config.py` marked as deprecated
  - OAuth 2.1 flow handles authentication automatically
  - Only `CHAR_TO_CHECK` still read from `credentials.txt` (line 3)
- **Updated `poe_api.py`**: `get_token()` now uses `oauth_flow.get_access_token()`
  - Removed old AUTH_URL and client_credentials logic
  - Ignores client_id/client_secret parameters (backwards compatibility)
- **First-Run Experience**: Tracker opens browser for authorization automatically
  - Clear console feedback ("🔐 Starting OAuth 2.1 Authorization Flow...")
  - Status messages guide user through authorization process

### Fixed
- **Cloudflare 403 Blocking**: Added proper User-Agent headers to token exchange and refresh requests
- **OAuth Flow Timing**: Improved callback server shutdown handling

### Security
- **No More Exposed Secrets**: Public client eliminates need to store client_secret
- **PKCE Protection**: Code challenge prevents authorization code interception attacks
- **Token Isolation**: tokens.json automatically excluded from Git

### Migration Notes
- **Breaking Change**: Old OAuth client_credentials no longer works (GGG deprecated)
- **First Run**: Users must authorize app in browser (one-time setup)
- **Auto-Refresh**: Tokens auto-refresh for 7 days, then re-authorization required
- **credentials.txt**: Only line 3 (character name) still used

## [0.3.5] - 2025-10-22

### Added
- **Phase-Based Flow Architecture**: Complete refactoring of map tracking flow
  - New `MapFlowController` class orchestrates PRE/POST flows in 9 clear phases
  - New `InventorySnapshotService` handles all API calls with rate limiting
  - New `InventorySnapshot` dataclass for immutable snapshot data
  - Phase-specific result objects: `DiffResult`, `ValueResult`, `SessionSnapshot`
- **Comprehensive Flow Documentation**: New `docs/SESSION_FLOW.md`
  - Complete phase diagrams and flow visualization
  - Common pitfalls and solutions documented
  - Testing procedures and debugging guides
  - Session state lifecycle explained
- **Architecture Section in README**: Clear overview of modular components and flow

### Changed
- **Main Script Simplified**: `poe_stats_refactored_v2.py` reduced from 787 to 640 lines (-147 lines)
  - `take_pre_snapshot()`: Now 9-line wrapper (was 60 lines)
  - `take_post_snapshot()`: Now 13-line wrapper (was 140 lines)
  - All complex logic moved to dedicated flow controller
- **Better Error Messages**: Phase-based errors ("Phase 5 failed" vs generic "POST failed")
- **Improved Code Documentation**: Enhanced docstrings with architecture overview and flow references
- **Rate Limiting Refactored**: Moved from main class to `InventorySnapshotService`

### Fixed
- **Session Double-Counting Prevention**: Single `add_completed_map()` call enforced by architecture
  - Only Phase 5 of POST flow can add maps to session
  - Phase 4 captures state BEFORE update for comparison
  - Clear separation prevents accidental duplicate tracking
- **State Management Clarity**: Explicit `set_session_comparison_baseline()` method
  - No more direct attribute assignments
  - Better encapsulation and intent clarity

### Removed
- `self.pre_inventory` attribute (replaced by flow controller snapshots)
- `self.last_api_call` attribute (replaced by rate limiter service)
- `rate_limit()` method (replaced by `InventorySnapshotService`)

### Technical Improvements
- **Testability**: Each phase can be tested independently
- **Maintainability**: Clear phase names make debugging easier
- **Extensibility**: New phases can be added as `_phase_xyz()` methods
- **Robustness**: Type hints via dataclasses, immutable snapshots
- **Documentation**: Flow completely documented for future maintenance

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
