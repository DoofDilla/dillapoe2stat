"""
Cleanup old version-specific registry keys
Run this once to clean up registry pollution from old app IDs
"""

import winreg
import re


def cleanup_old_version_keys():
    """Remove old BoneBunnyStats registry keys with version numbers"""
    base_path = r"SOFTWARE\Classes\AppUserModelId"
    pattern = r"BoneBunnyStats v\d+\.\d+\.\d+"
    
    removed_keys = []
    
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base_path) as parent_key:
            # Enumerate all subkeys
            index = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(parent_key, index)
                    
                    # Check if it's an old versioned BoneBunnyStats key
                    if re.match(pattern, subkey_name):
                        try:
                            # Try to delete it
                            full_path = f"{base_path}\\{subkey_name}"
                            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, full_path)
                            removed_keys.append(subkey_name)
                            print(f"✅ Removed: {subkey_name}")
                        except Exception as e:
                            print(f"❌ Failed to remove {subkey_name}: {e}")
                    
                    index += 1
                    
                except OSError:
                    # No more subkeys
                    break
                    
    except FileNotFoundError:
        print("ℹ️  AppUserModelId registry path not found (nothing to clean)")
        return removed_keys
    except Exception as e:
        print(f"⚠️  Error accessing registry: {e}")
        return removed_keys
    
    return removed_keys


def main():
    print("🧹 Cleaning up old BoneBunnyStats registry keys...\n")
    
    removed = cleanup_old_version_keys()
    
    print(f"\n{'='*60}")
    if removed:
        print(f"✅ Removed {len(removed)} old registry key(s)")
        print("📝 New stable key: DoofDilla.BoneBunnyStats")
    else:
        print("✨ No old keys found - registry is clean!")
    print(f"{'='*60}\n")
    
    print("ℹ️  Going forward, the app will use a stable registry key")
    print("   that doesn't change with version updates.")


if __name__ == "__main__":
    main()
