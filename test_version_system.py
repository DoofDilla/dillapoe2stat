"""
Quick test to verify version system integration
Run this to ensure all version imports work correctly
"""

def test_version_system():
    """Test that version system is properly integrated"""
    print("Testing version system integration...\n")
    
    # Test 1: Import version module
    try:
        from version import (
            __version__, 
            get_version_string, 
            get_version_display, 
            get_app_identifier,
            get_toast_app_id,
            get_version_info,
            DATA_FORMAT_VERSION
        )
        print("✅ version.py imports successfully")
        print(f"   Version: {__version__}")
        print(f"   Display: {get_version_display()}")
        print(f"   App ID (display): {get_app_identifier()}")
        print(f"   Toast ID (registry): {get_toast_app_id()}")
        print(f"   Data Format: {DATA_FORMAT_VERSION}")
    except Exception as e:
        print(f"❌ version.py import failed: {e}")
        return False
    
    # Test 2: Config uses version
    try:
        from config import Config
        print(f"\n✅ Config imports version successfully")
        print(f"   Config.VERSION: {Config.VERSION}")
        print(f"   Config.APP_ID: {Config.APP_ID}")
        print(f"   Config.TOAST_APP_ID: {Config.TOAST_APP_ID}")
        assert Config.VERSION == __version__, "Config.VERSION doesn't match version module"
        assert Config.TOAST_APP_ID == get_toast_app_id(), "Config.TOAST_APP_ID doesn't match"
        assert "v" not in Config.TOAST_APP_ID, "TOAST_APP_ID should NOT contain version!"
    except Exception as e:
        print(f"❌ Config version integration failed: {e}")
        return False
    
    # Test 3: Display manager uses version
    try:
        from display import DisplayManager
        print(f"\n✅ DisplayManager imports successfully")
        # Can't fully test without running, but import is good
    except Exception as e:
        print(f"❌ DisplayManager import failed: {e}")
        return False
    
    # Test 4: Notification manager uses version
    try:
        from notification_manager import NotificationManager
        print(f"✅ NotificationManager imports successfully")
    except Exception as e:
        print(f"❌ NotificationManager import failed: {e}")
        return False
    
    # Test 5: Logging uses data format version
    try:
        from poe_logging import DATA_FORMAT_VERSION as LOG_VERSION
        print(f"\n✅ poe_logging imports DATA_FORMAT_VERSION")
        print(f"   Format Version: {LOG_VERSION}")
        assert LOG_VERSION == DATA_FORMAT_VERSION, "Logging format version doesn't match"
    except Exception as e:
        print(f"❌ poe_logging version integration failed: {e}")
        return False
    
    # Test 6: Version info dictionary
    try:
        info = get_version_info()
        print(f"\n✅ Version info dictionary:")
        for key, value in info.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Version info failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("🎉 All version system tests passed!")
    print("="*60)
    return True


if __name__ == "__main__":
    import sys
    success = test_version_system()
    sys.exit(0 if success else 1)
