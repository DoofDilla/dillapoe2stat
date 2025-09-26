"""
ASCII Theme Manager for PoE Stats Tracker
Handles loading and managing ASCII art themes from JSON
"""

import json
import os
from pathlib import Path


class ASCIIThemeManager:
    """Manages ASCII themes for the display system"""
    
    def __init__(self, theme_file="ascii_themes.json"):
        self.script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.theme_file_path = self.script_dir / theme_file
        self.themes = {}
        self.current_theme = "default"
        self.load_themes()
    
    def load_themes(self):
        """Load themes from JSON file"""
        try:
            if self.theme_file_path.exists():
                with open(self.theme_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.themes = data.get('themes', {})
            else:
                # Create default theme if file doesn't exist
                self.create_default_themes_file()
                self.load_themes()
        except Exception as e:
            print(f"Warning: Could not load ASCII themes: {e}")
            self.themes = self._get_fallback_theme()
    
    def create_default_themes_file(self):
        """Create default themes file if it doesn't exist"""
        default_themes = {
            "themes": {
                "default": {
                    "name": "PoE2 Classic",
                    "description": "Default elegant theme",
                    "left_decoration": "●▬▬▬๑۩۩๑▬▬▬",
                    "right_decoration": "▬▬▬๑۩۩๑▬▬▬●",
                    "middle_char": "─",
                    "total_width": 80,
                    "timestamp_format": "%H:%M:%S • %d.%m.%Y",
                    "decoration_color": "CYAN",
                    "middle_color": "CYAN",
                    "timestamp_color": "GRAY"
                }
            }
        }
        
        try:
            with open(self.theme_file_path, 'w', encoding='utf-8') as f:
                json.dump(default_themes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not create themes file: {e}")
    
    def _get_fallback_theme(self):
        """Get fallback theme if loading fails"""
        return {
            "default": {
                "name": "Fallback",
                "description": "Simple fallback theme",
                "left_decoration": "---",
                "right_decoration": "---",
                "middle_char": "-",
                "total_width": 50,
                "timestamp_format": "%H:%M:%S",
                "decoration_color": "WHITE",
                "middle_color": "WHITE",
                "timestamp_color": "GRAY"
            }
        }
    
    def get_theme(self, theme_name=None):
        """Get a specific theme or current theme"""
        theme_name = theme_name or self.current_theme
        
        if theme_name in self.themes:
            return self.themes[theme_name]
        else:
            print(f"Warning: Theme '{theme_name}' not found, using default")
            return self.themes.get('default', list(self.themes.values())[0])
    
    def set_theme(self, theme_name):
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        else:
            available = ', '.join(self.themes.keys())
            print(f"Theme '{theme_name}' not found. Available themes: {available}")
            return False
    
    def list_themes(self):
        """List all available themes with descriptions"""
        if not self.themes:
            return "No themes available"
        
        theme_list = []
        for key, theme in self.themes.items():
            name = theme.get('name', key)
            desc = theme.get('description', 'No description')
            current = " (CURRENT)" if key == self.current_theme else ""
            theme_list.append(f"  {key}: {name} - {desc}{current}")
        
        return "Available ASCII Themes:\n" + "\n".join(theme_list)
    
    def get_theme_names(self):
        """Get list of theme names"""
        return list(self.themes.keys())
    
    def add_custom_theme(self, theme_name, theme_data):
        """Add a custom theme (runtime only, not saved)"""
        required_fields = ['left_decoration', 'right_decoration', 'middle_char', 
                          'total_width', 'decoration_color', 'middle_color', 'timestamp_color']
        
        # Validate theme data
        for field in required_fields:
            if field not in theme_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Add defaults
        if 'timestamp_format' not in theme_data:
            theme_data['timestamp_format'] = "%H:%M:%S • %d.%m.%Y"
        if 'name' not in theme_data:
            theme_data['name'] = theme_name.title()
        if 'description' not in theme_data:
            theme_data['description'] = "Custom theme"
        
        self.themes[theme_name] = theme_data
        return True
    
    def preview_theme(self, theme_name):
        """Preview what a theme looks like"""
        theme = self.get_theme(theme_name)
        if not theme:
            return "Theme not found"
        
        # Import here to avoid circular imports
        from datetime import datetime
        
        # Create a sample footer line
        timestamp = datetime.now().strftime(theme['timestamp_format'])
        left_deco = theme['left_decoration']
        right_deco = theme['right_decoration']
        middle_char = theme['middle_char']
        total_width = theme['total_width']
        
        timestamp_text = f" {timestamp} "
        deco_width = len(left_deco) + len(right_deco)
        available_width = total_width - len(timestamp_text) - deco_width
        padding = max(0, available_width // 2)
        middle_line = middle_char * padding
        
        preview_line = f"{left_deco}{middle_line}{timestamp_text}{middle_line}{right_deco}"
        
        return f"Theme '{theme_name}' ({theme.get('name', 'Unknown')}):\n{preview_line}"
    
    def reload_themes(self):
        """Reload themes from file"""
        self.load_themes()
        return f"Themes reloaded. Available: {', '.join(self.get_theme_names())}"


# Global theme manager instance
_theme_manager = None

def get_theme_manager():
    """Get the global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ASCIIThemeManager()
    return _theme_manager