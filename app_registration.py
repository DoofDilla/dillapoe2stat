"""
Windows App Registration for Toast Notifications
Handles automatic registration of the app for proper toast notification display
"""

import winreg
from pathlib import Path
from config import Config


class AppRegistration:
    """Handle Windows app registration for proper toast notification display"""
    
    @staticmethod
    def ensure_app_registered():
        """Ensure app is registered with Windows for proper toast notification display"""
        try:
            config = Config()
            # Use stable TOAST_APP_ID (no version!) for registry
            toast_app_id = config.TOAST_APP_ID  # "DoofDilla.BoneBunnyStats"
            display_name = config.APP_NAME  # "BoneBunnyStats"
            
            # Use ICO file for app icon
            ico_path = config.get_icon_path().parent / 'HasiSkull_64x64_toast.ico'
            
            # Create ICO if it doesn't exist
            if not ico_path.exists():
                AppRegistration._create_ico_from_png(config.get_icon_path(), ico_path)
            
            # Registry path for toast notifications (stable key!)
            reg_path = r"SOFTWARE\Classes\AppUserModelId\\" + toast_app_id
            
            # Check if already registered correctly
            if AppRegistration._is_correctly_registered(reg_path, display_name, ico_path):
                return True  # Already registered correctly
            
            # Create/update registry entry
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                # Set display name (no version)
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, display_name)
                
                # Set icon path (ICO format for app icon)
                winreg.SetValueEx(key, "IconUri", 0, winreg.REG_SZ, str(ico_path.absolute()))
                
            return True
            
        except Exception as e:
            print(f"Warning: Failed to register app for notifications: {e}")
            return False
    
    @staticmethod
    def _is_correctly_registered(reg_path, expected_name, expected_icon):
        """Check if app is already registered correctly"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                display_name = winreg.QueryValueEx(key, "DisplayName")[0]
                icon_uri = winreg.QueryValueEx(key, "IconUri")[0]
                
                return (display_name == expected_name and 
                        Path(icon_uri) == expected_icon.absolute())
                        
        except (FileNotFoundError, OSError):
            return False
    
    @staticmethod
    def _create_ico_from_png(png_path, ico_path):
        """Create ICO file from PNG if needed"""
        try:
            from PIL import Image
            
            img = Image.open(png_path)
            img.save(ico_path, format='ICO', sizes=[(64, 64), (48, 48), (32, 32), (24, 24), (16, 16)])
            
        except ImportError:
            print("Warning: PIL/Pillow not available - cannot create ICO file")
        except Exception as e:
            print(f"Warning: Failed to create ICO file: {e}")
    
    @staticmethod
    def cleanup_registration():
        """Remove app registration from Windows (cleanup on exit)"""
        try:
            config = Config()
            toast_app_id = config.TOAST_APP_ID  # Use stable ID
            reg_path = r"SOFTWARE\Classes\AppUserModelId\\" + toast_app_id
            
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
            return True
            
        except FileNotFoundError:
            return True  # Already gone
        except Exception:
            return False  # Failed to cleanup