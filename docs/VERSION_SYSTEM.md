# Version System Implementation

## Overview

This document describes the centralized version management system implemented for DillaPoE2Stat.

## Files Modified/Created

### New Files

1. **`version.py`** - Single source of truth for version information
   - Application version (`__version__ = "0.3.1"`)
   - Semantic versioning components (MAJOR, MINOR, PATCH)
   - Release metadata (date, name)
   - Data format version (for runs.jsonl compatibility)
   - Helper functions for version display and app identification

2. **`CHANGELOG.md`** - Version history and release notes
   - Follows [Keep a Changelog](https://keepachangelog.com/) format
   - Adheres to [Semantic Versioning](https://semver.org/)
   - Documents all notable changes by version

### Modified Files

1. **`config.py`**
   - Imports version from `version.py`
   - Uses centralized `get_app_identifier()` for APP_ID
   - Maintains backward compatibility

2. **`notification_templates.py`**
   - Added SYSTEM section to documentation
   - Documents `app_name` and `app_version` template variables
   - Updated STARTUP template to use `{app_version}`

3. **`notification_manager.py`**
   - Injects `app_name` and `app_version` into all notification templates
   - System variables available alongside currency and other values

4. **`display.py`**
   - Imports `get_version_display()` from version module
   - Shows version in startup configuration banner
   - Format: "CONFIGURATION • v0.3.1 (Waystone Analytics)"

5. **`poe_logging.py`**
   - Imports `DATA_FORMAT_VERSION` from version module
   - Uses centralized constant for runs.jsonl format version
   - Ensures consistency between app and data versions

## Usage

### Updating the Version

To release a new version, update only `version.py`:

```python
# For a patch release (bug fixes)
__version__ = "0.3.2"
PATCH = 2

# For a minor release (new features)
__version__ = "0.4.0"
MINOR = 4
PATCH = 0

# For a major release (breaking changes)
__version__ = "1.0.0"
MAJOR = 1
MINOR = 0
PATCH = 0
```

Also update:
- `RELEASE_DATE` to the new release date
- `RELEASE_NAME` if it's a significant release
- Add entry to `CHANGELOG.md`

### Version in Notifications

All notification templates now have access to:

```python
{app_name}     # "BoneBunnyStats"
{app_version}  # "0.3.1"
```

Example:
```python
CUSTOM_TEMPLATE = {
    'title': '🎮 {app_name} v{app_version}',
    'template': 'Your notification content here'
}
```

### Version Display

The version appears in:
1. **Startup Banner**: "CONFIGURATION • v0.3.1 (Waystone Analytics)"
2. **Notifications**: Toast notification titles show app version
3. **Windows Registry**: App ID includes version for proper grouping

## Semantic Versioning Guide

**MAJOR** version (1.0.0) - Incompatible API changes
- Breaking changes to data format
- Removal of deprecated features
- Major architectural changes

**MINOR** version (0.4.0) - New features, backward compatible
- New functionality added
- New notification templates
- New configuration options
- Non-breaking enhancements

**PATCH** version (0.3.2) - Bug fixes only
- Bug fixes
- Performance improvements
- Documentation updates
- Minor UI tweaks

## Data Format Versioning

The `DATA_FORMAT_VERSION` in `version.py` tracks the runs.jsonl structure:

- **"2.0"** - Current format with enhanced item values
- Future format changes should increment this independently

## Benefits

✅ **Single Source of Truth** - Change version once, applies everywhere  
✅ **Consistency** - No version mismatches across files  
✅ **User Visibility** - Version shown in UI and notifications  
✅ **Professional** - Follows industry-standard semantic versioning  
✅ **CI/CD Ready** - Build and commit fields available for automation  
✅ **Maintainable** - Clear separation of app vs data versioning  
✅ **Documented** - CHANGELOG tracks all changes by version  

## Registry Management

### Problem
The old system included version in the Windows registry AppUserModelId:
- `BoneBunnyStats v0.3.1`
- `BoneBunnyStats v0.3.2` (new key!)
- `BoneBunnyStats v0.4.0` (another new key!)

This created registry pollution with a new key for each version.

### Solution
Two separate identifiers:
1. **`APP_ID`** - For display purposes, includes version: `"BoneBunnyStats v0.3.1"`
2. **`TOAST_APP_ID`** - For registry, stable: `"DoofDilla.BoneBunnyStats"`

The registry key now stays constant across all versions.

### Cleanup Old Keys
Run once to clean up old versioned registry keys:
```powershell
python cleanup_old_registry_keys.py
```

This removes all old `BoneBunnyStats v*` registry entries.

## Future Enhancements

Potential additions:
- Auto-update checker comparing local vs remote version
- Version command-line flag (e.g., `python poe_stats.py --version`)
- Build automation to inject git commit hash
- Version compatibility checker for old runs.jsonl files
