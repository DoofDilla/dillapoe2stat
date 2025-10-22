"""
Configuration settings for PoE Stats Tracker
Centralized configuration management
"""

import os
from pathlib import Path
from version import __version__, get_app_identifier, get_toast_app_id


class Config:
    """Configuration settings for the PoE Stats Tracker"""
    
    # ============================================================================
    # APPLICATION INFORMATION
    # ============================================================================
    APP_NAME = "BoneBunnyStats"
    VERSION = __version__  # Imported from version.py
    APP_ID = get_app_identifier()  # Display identifier with version (e.g. "BoneBunnyStats v0.3.1")
    TOAST_APP_ID = get_toast_app_id()  # Stable registry ID WITHOUT version (e.g. "DoofDilla.BoneBunnyStats")
    
    # ============================================================================
    # USER SETTINGS - Customize these for your setup
    # ============================================================================
    
    # OAuth 2.1 Authentication
    # Authentication handled automatically via browser-based OAuth flow
    # Tokens are stored in tokens.json (auto-generated, gitignored)
    # No CLIENT_ID or CLIENT_SECRET needed in config
    
    # Character name to track (UPDATE THIS!)
    CHAR_TO_CHECK = "Mettmanwalking"
    
    # PoE2 Client
    CLIENT_LOG = r"C:\GAMESSD\Path of Exile 2\logs\Client.txt"  # Update this path
    
    # ============================================================================
    # ASSETS & RESOURCES
    # ============================================================================
    
    # Images Directory
    IMAGES_DIR = 'images'
    
    # Notification Icons
    ICON_DEFAULT = 'HasiSkull_64x64.png'
    ICON_PRE_MAP = 'icon_start_map_64x64.png'
    ICON_POST_MAP = 'icon_finish_map_64x64.png'
    ICON_WAYSTONE = 'icon_waypoint_64x64.png'
    ICON_AUTOMODE = 'icon_automode_64x64.png'
    
    # ANSI Art Files
    ANSI_HASISKULL_SOURCE = 'HasiSkull_64x64.png'  # Source image for ANSI conversion
    ANSI_HASISKULL_DEFAULT = 'hasiskull_colored_blocks_32x32.ansi'  # Default startup banner
    
    # ASCII Theme Configuration
    ASCII_THEME = "celestial"  # Options: "default", "ancient", "elegant", "minimal", "hardcore", "royal", "cyber", "stars", "celestial"
    
    # ============================================================================
    # DISPLAY SETTINGS
    # ============================================================================
    
    OUTPUT_MODE = "normal"  # "normal" or "comprehensive"
    SHOW_ALL_ITEMS = True  # Show items without value (with '-' for price)
    
    # Table Display
    TABLE_SEPARATOR_CHAR = '─'
    TABLE_MIN_NAME_WIDTH = 35
    TABLE_QTY_WIDTH = 4
    TABLE_CATEGORY_WIDTH = 12
    TABLE_CHAOS_WIDTH = 10
    TABLE_EXALTED_WIDTH = 12
    
    # ============================================================================
    # DEBUG SETTINGS
    # ============================================================================
    
    # Master switch for debug mode (toggleable with F4 hotkey)
    DEBUG_ENABLED = False
    
    # Save debug snapshots to JSON files in /debug folder
    DEBUG_TO_FILE = False
    
    # Show concise summaries (True) vs full detailed dumps (False)
    DEBUG_SHOW_SUMMARY = True
    
    # ============================================================================
    # NOTIFICATIONS
    # ============================================================================
    
    NOTIFICATION_ENABLED = True
    
    # ============================================================================
    # OBS INTEGRATION
    # ============================================================================
    
    OBS_HOST = "localhost"
    OBS_PORT = 5000
    OBS_AUTO_START = False  # Auto-start OBS server on tracker startup (F9 always works)
    OBS_QUIET_MODE = True  # Suppress Flask request logs for cleaner output
    
    # ============================================================================
    # KISS OVERLAY
    # ============================================================================
    
    KISS_OVERLAY_ENABLED = True  # Enable file-based overlay state updates
    KISS_OVERLAY_STATE_FILE = "kiss_overlay/kiss_overlay_state.json"  # State file (relative to project root)
    
    # ============================================================================
    # API & RATE LIMITING
    # ============================================================================
    
    API_RATE_LIMIT = 2.5  # Minimum seconds between API calls
    
    # ============================================================================
    # LOG SCANNING
    # ============================================================================
    
    CLIENT_LOG_SCAN_BYTES = 1_500_000  # Bytes to scan from end of client log
    
    # ============================================================================
    # AUTO MAP DETECTION
    # ============================================================================
    
    AUTO_DETECTION_ENABLED = False  # Toggleable with hotkey
    AUTO_DETECTION_CHECK_INTERVAL = 1.0  # Check every N seconds
    AUTO_DETECTION_SCAN_BYTES = 50000  # Bytes to scan from end of log
    
    # Hideout Areas (safe zones for pre-map snapshots)
    AUTO_HIDEOUT_AREAS = {
        'HideoutFelled',           # Felled Hideout
        'HideoutOvergrown',        # Overgrown Hideout  
        'HideoutCoral',            # Coral Hideout
        'HideoutRitual',           # Ritual Hideout
        'Hideout',                 # Generic hideout
        'Hideout1',                # Basic hideout variants
        'Hideout2',
        'Hideout3',
    }
    
    # Town/Safe Zone Areas
    AUTO_TOWN_AREAS = {
        'Act1Town',               # Well of Souls - often used for inventory refresh
        'Act1_Town',
        'Act2Town',               # Act 2 town
        'Act2_Town', 
        'Act3Town',               # Act 3 town
        'Act3_Town',
        'WellOfSouls',            # Alternative name for Act 1 town
        'Abyss_Hub',              # Well of Souls (confirmed area code)
        'Town',                   # Generic town
        'Clearfell',              # Act 1 town alternative name
        'Ogham',                  # Act 2 town
        'NakuriForest',           # Act 3 town
    }
    
    # Areas that trigger automatic waystone analysis
    AUTO_WAYSTONE_TRIGGER_AREAS = {
        'Abyss_Hub',              # Well of Souls - common waystone checking location
    }
    
    # ============================================================================
    # METHODS - ASCII Theme Management
    # ============================================================================
    
    @classmethod
    def get_ascii_theme_config(cls):
        """Get the current ASCII theme configuration"""
        from ascii_theme_manager import get_theme_manager
        theme_manager = get_theme_manager()
        return theme_manager.get_theme(cls.ASCII_THEME)
    
    @classmethod
    def set_ascii_theme(cls, theme_name):
        """Set the ASCII theme"""
        from ascii_theme_manager import get_theme_manager
        theme_manager = get_theme_manager()
        if theme_manager.set_theme(theme_name):
            cls.ASCII_THEME = theme_name
            return True
        return False
    
    @classmethod
    def list_ascii_themes(cls):
        """List available ASCII themes"""
        from ascii_theme_manager import get_theme_manager
        theme_manager = get_theme_manager()
        return theme_manager.list_themes()
    
    @classmethod
    def preview_ascii_theme(cls, theme_name):
        """Preview an ASCII theme"""
        from ascii_theme_manager import get_theme_manager
        theme_manager = get_theme_manager()
        return theme_manager.preview_theme(theme_name)
    
    # ============================================================================
    # METHODS - Path Helpers
    # ============================================================================
    
    # ============================================================================
    # METHODS - Path Helpers
    # ============================================================================
    
    @classmethod
    def get_script_dir(cls):
        """Get the directory where the script is located"""
        return Path(os.path.dirname(os.path.abspath(__file__)))
    
    @classmethod
    def get_images_dir(cls):
        """Get the images directory path"""
        return cls.get_script_dir() / cls.IMAGES_DIR
    
    @classmethod
    def get_ansi_path(cls, ansi_filename=None):
        """Get path to ANSI art file
        
        Args:
            ansi_filename: Name of ANSI file (defaults to ANSI_HASISKULL_DEFAULT)
        """
        filename = ansi_filename or cls.ANSI_HASISKULL_DEFAULT
        return cls.get_images_dir() / filename
    
    @classmethod
    def get_image_path(cls, image_filename):
        """Get path to any image file in images directory
        
        Args:
            image_filename: Name of image file
        """
        return cls.get_images_dir() / image_filename
    
    @classmethod
    def get_log_file_path(cls):
        """Get the path for the runs log file"""
        return cls.get_script_dir() / "runs.jsonl"
    
    @classmethod
    def get_session_log_file_path(cls):
        """Get the path for the sessions log file"""
        return cls.get_script_dir() / "sessions.jsonl"
    
    @classmethod
    def get_icon_path(cls, icon_type=None):
        """Get the path for notification icons
        
        Args:
            icon_type: Type of icon ('pre_map', 'post_map', 'waystone', 'automode', or None for default)
        """
        icon_mapping = {
            'pre_map': cls.ICON_PRE_MAP,
            'post_map': cls.ICON_POST_MAP,
            'waystone': cls.ICON_WAYSTONE,
            'automode': cls.ICON_AUTOMODE,
        }
        
        icon_filename = icon_mapping.get(icon_type, cls.ICON_DEFAULT)
        return cls.get_images_dir() / icon_filename
    
    @classmethod
    def get_debug_dir(cls):
        """Get the debug output directory"""
        return cls.get_script_dir() / "debug"
    
    # ============================================================================
    # METHODS - Validation & Configuration Management
    # ============================================================================
    
    # ============================================================================
    # METHODS - Validation & Configuration Management
    # ============================================================================
    
    @classmethod
    def validate_config(cls):
        """Validate the configuration settings"""
        errors = []
        warnings = []
        
        # Check required settings
        if cls.CHAR_TO_CHECK == "YourCharacterName":
            warnings.append("Using default character name - please update CHAR_TO_CHECK in config.py")
        
        # Check file paths
        client_log_path = Path(cls.CLIENT_LOG)
        if not client_log_path.exists():
            errors.append(f"Client log file not found: {cls.CLIENT_LOG}")
        
        # Check output mode
        if cls.OUTPUT_MODE not in ["normal", "comprehensive"]:
            errors.append(f"Invalid OUTPUT_MODE: {cls.OUTPUT_MODE}. Must be 'normal' or 'comprehensive'")
        
        # Check rate limit
        if cls.API_RATE_LIMIT < 1.0:
            warnings.append(f"API_RATE_LIMIT is very low ({cls.API_RATE_LIMIT}s) - consider increasing to avoid rate limiting")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @classmethod
    def print_config_summary(cls):
        """Print a summary of current configuration with themed header"""
        # Use display manager for themed banner
        from display import DisplayManager
        display = DisplayManager()
        display._display_themed_banner("CONFIGURATION")
        
        # Configuration with colors (matching _display_basic_info style)
        from display import Colors
        print(f"📋 Character: {Colors.CYAN}{cls.CHAR_TO_CHECK}{Colors.END}{'':20} 🎮 Output Mode: {Colors.BOLD}{cls.OUTPUT_MODE.upper()}{Colors.END}")
        debug_status = f"{Colors.GREEN}Enabled{Colors.END}" if cls.DEBUG_ENABLED else f"{Colors.GRAY}Disabled{Colors.END}"
        debug_file_status = f"{Colors.GREEN}Enabled{Colors.END}" if cls.DEBUG_TO_FILE else f"{Colors.GRAY}Disabled{Colors.END}"
        print(f"🐛 Debug: {debug_status}{'':15} 📁 Debug to File: {debug_file_status}")
        print(f"📄 Client Log: {Colors.YELLOW}{cls.CLIENT_LOG}{Colors.END}")
        print(f"⏱️  API Rate Limit: {Colors.CYAN}{cls.API_RATE_LIMIT}s{Colors.END}")
        print()
        
        validation = cls.validate_config()
        if validation['warnings']:
            print("\nWarnings:")
            for warning in validation['warnings']:
                print(f"  ⚠️  {warning}")
        
        if validation['errors']:
            print("\nErrors:")
            for error in validation['errors']:
                print(f"  ❌ {error}")
    
    @classmethod
    def update_character(cls, character_name):
        """Update the character name"""
        cls.CHAR_TO_CHECK = character_name
    
    @classmethod
    def update_output_mode(cls, mode):
        """Update the output mode"""
        if mode in ["normal", "comprehensive"]:
            cls.OUTPUT_MODE = mode
            return True
        return False
    
    @classmethod
    def toggle_debug(cls):
        """Toggle debug mode"""
        cls.DEBUG_ENABLED = not cls.DEBUG_ENABLED
        return cls.DEBUG_ENABLED


# ============================================================================
# BACKWARD COMPATIBILITY - Module-level constants
# ============================================================================
# CLIENT_ID and CLIENT_SECRET removed in v0.4.0 (OAuth 2.1 migration)
CHAR_TO_CHECK = Config.CHAR_TO_CHECK
CLIENT_LOG = Config.CLIENT_LOG
DEBUG_ENABLED = Config.DEBUG_ENABLED
DEBUG_TO_FILE = Config.DEBUG_TO_FILE
DEBUG_SHOW_SUMMARY = Config.DEBUG_SHOW_SUMMARY
OUTPUT_MODE = Config.OUTPUT_MODE