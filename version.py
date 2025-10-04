"""
Version management for DillaPoE2Stat
Single source of truth for all version-related information
"""

__version__ = "0.3.2"
__version_info__ = (0, 3, 2)

# Semantic versioning components
MAJOR = 0  # Breaking changes
MINOR = 3  # New features, backwards compatible
PATCH = 2  # Bug fixes

# Release information
RELEASE_DATE = "2025-10-04"
RELEASE_NAME = "Top Drops Tracking"  # Optional codename for major releases

# Data format version (for runs.jsonl compatibility)
# 2.0: Initial enhanced format with waystone attributes
# 2.1: Added delirious tracking
DATA_FORMAT_VERSION = "2.1"

# Build/commit info (optional, can be populated by CI/CD)
BUILD_NUMBER = None
GIT_COMMIT = None


def get_version_string():
    """Get full version string"""
    return __version__


def get_version_display():
    """Get version string for display purposes"""
    if RELEASE_NAME:
        return f"v{__version__} ({RELEASE_NAME})"
    return f"v{__version__}"


def get_app_identifier():
    """Get application identifier for Windows notifications (includes version for display)"""
    return f"BoneBunnyStats v{__version__}"


def get_toast_app_id():
    """Get stable App ID for Windows registry (NO VERSION - stays constant)
    
    This ID is used for Windows toast notification registration.
    It MUST NOT change between versions to avoid registry pollution.
    """
    return "DoofDilla.BoneBunnyStats"  # Stable, no version number


def get_version_info():
    """Get comprehensive version information dictionary"""
    return {
        'version': __version__,
        'version_info': __version_info__,
        'major': MAJOR,
        'minor': MINOR,
        'patch': PATCH,
        'release_date': RELEASE_DATE,
        'release_name': RELEASE_NAME,
        'data_format_version': DATA_FORMAT_VERSION,
        'build_number': BUILD_NUMBER,
        'git_commit': GIT_COMMIT,
    }
