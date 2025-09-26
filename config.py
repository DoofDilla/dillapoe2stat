"""
Configuration settings for PoE Stats Tracker
Centralized configuration management
"""

import os
from pathlib import Path


class Config:
    """Configuration settings for the PoE Stats Tracker"""
    
    # API Configuration
    CLIENT_ID = "dillapoe2stat"
    CLIENT_SECRET = "UgraAmlUXdP1"  # Change this to your actual secret
    
    # Character Configuration
    CHAR_TO_CHECK = "Mettmanwalking"  # Change this to your character name
    
    # File Paths
    CLIENT_LOG = r"C:\GAMESSD\Path of Exile 2\logs\Client.txt"  # Update this path
    
    # Debug Settings - Control what debug information is displayed and logged
    # DEBUG_ENABLED: Master switch for debug mode. When True, enables additional debug output
    #                and console logging. Can be toggled at runtime with F4 hotkey.
    #                - False: Normal operation, minimal debug output
    #                - True: Enhanced debugging with detailed item information
    DEBUG_ENABLED = False
    
    # DEBUG_TO_FILE: Controls whether debug snapshots are saved to JSON files in /debug folder
    #                Useful for troubleshooting inventory parsing issues or API responses
    #                - False: No file output, debug info only shown in console
    #                - True: Saves PRE/POST inventory snapshots as timestamped JSON files
    DEBUG_TO_FILE = False
    
    # DEBUG_SHOW_SUMMARY: When debug is enabled, controls the level of detail shown
    #                     This setting determines console output verbosity in debug mode
    #                     - True: Show concise item summaries (name, quantity, location)
    #                     - False: Show full detailed item dumps (all properties, IDs, etc.)
    DEBUG_SHOW_SUMMARY = True
    
    # Display Settings
    OUTPUT_MODE = "normal"  # "normal" or "comprehensive"
    
    # ASCII Theme Configuration - Select your preferred visual theme
    # Available themes are loaded from ascii_themes.json
    # You can easily add new themes by editing the JSON file
    ASCII_THEME = "stars"  # Options: "default", "ancient", "elegant", "minimal", "hardcore", "royal", "cyber", "stars"
    
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
    
    # Rate Limiting
    API_RATE_LIMIT = 2.5  # Minimum seconds between API calls
    
    # Client Log Scanning
    CLIENT_LOG_SCAN_BYTES = 1_500_000  # How many bytes to scan from end of client log
    
    # Notification Settings
    NOTIFICATION_ENABLED = True
    
    @classmethod
    def get_script_dir(cls):
        """Get the directory where the script is located"""
        return Path(os.path.dirname(os.path.abspath(__file__)))
    
    @classmethod
    def get_log_file_path(cls):
        """Get the path for the runs log file"""
        return cls.get_script_dir() / "runs.jsonl"
    
    @classmethod
    def get_session_log_file_path(cls):
        """Get the path for the sessions log file"""
        return cls.get_script_dir() / "sessions.jsonl"
    
    @classmethod
    def get_icon_path(cls):
        """Get the path for the notification icon"""
        return cls.get_script_dir() / 'cat64x64.png'
    
    @classmethod
    def get_debug_dir(cls):
        """Get the debug output directory"""
        return cls.get_script_dir() / "debug"
    
    @classmethod
    def validate_config(cls):
        """Validate the configuration settings"""
        errors = []
        warnings = []
        
        # Check required settings
        if cls.CLIENT_SECRET == "":
            warnings.append("Using default CLIENT_SECRET - please update with your actual secret")
        
        if cls.CHAR_TO_CHECK == "":
            warnings.append("Using default character name - please update CHAR_TO_CHECK")
        
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
        """Print a summary of current configuration"""
        print("Configuration Summary:")
        print(f"  Character: {cls.CHAR_TO_CHECK}")
        print(f"  Output Mode: {cls.OUTPUT_MODE}")
        print(f"  Debug Enabled: {cls.DEBUG_ENABLED}")
        print(f"  Debug to File: {cls.DEBUG_TO_FILE}")
        print(f"  Client Log: {cls.CLIENT_LOG}")
        print(f"  API Rate Limit: {cls.API_RATE_LIMIT}s")
        
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


# For backward compatibility, create module-level constants
CLIENT_ID = Config.CLIENT_ID
CLIENT_SECRET = Config.CLIENT_SECRET
CHAR_TO_CHECK = Config.CHAR_TO_CHECK
CLIENT_LOG = Config.CLIENT_LOG
DEBUG_ENABLED = Config.DEBUG_ENABLED
DEBUG_TO_FILE = Config.DEBUG_TO_FILE
DEBUG_SHOW_SUMMARY = Config.DEBUG_SHOW_SUMMARY
OUTPUT_MODE = Config.OUTPUT_MODE