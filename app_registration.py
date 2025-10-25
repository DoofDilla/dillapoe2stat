"""
Windows App Registration for Toast Notifications
Handles automatic registration of the app for proper toast notification display
"""

import platform
from pathlib import Path
from config import Config

# Conditional import for Windows only
if platform.system() == "Windows":
    import winreg
    APP_REGISTRATION_ENABLED = True
else:
    APP_REGISTRATION_ENABLED = False
    winreg = None  # Placeholder to avoid reference errors if needed


class AppRegistration:
    """Handles Windows app registration for toast notifications"""

    @staticmethod
    def ensure_app_registered():
        """Ensure the app is registered in Windows for toast notifications"""
        if not APP_REGISTRATION_ENABLED:
            # On non-Windows platforms, skip silently or log for awareness
            print("ℹ️ App registration skipped (non-Windows platform)")
            return

        # Windows-specific registration logic
        try:
            config = Config()
            toast_app_id = config.TOAST_APP_ID  # Use stable ID from config
            key_path = r"SOFTWARE\Classes\AppUserModelId\\" + toast_app_id

            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, None, 0, winreg.REG_SZ, toast_app_id)
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "PoE Stats Tracker")
                winreg.SetValueEx(key, "ShowInShell", 0, winreg.REG_DWORD, 0)

            print("✅ App registered successfully for toast notifications")
        except Exception as e:
            print(f"⚠️ App registration failed: {e}")

    @staticmethod
    def _is_correctly_registered(reg_path, expected_name, expected_icon):
        """Check if app is already registered correctly"""
        if not APP_REGISTRATION_ENABLED:
            return False  # Cannot check on non-Windows

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
        if not APP_REGISTRATION_ENABLED:
            return  # Cannot create on non-Windows

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
        if not APP_REGISTRATION_ENABLED:
            return True  # No cleanup needed on non-Windows

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
