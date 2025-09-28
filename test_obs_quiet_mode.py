"""
Test OBS Server Quiet Mode
Verify that Flask request logs are suppressed when quiet_mode=True
"""

import time
import requests
import threading
from obs_web_server import OBSWebServer


def test_quiet_mode():
    """Test that quiet mode suppresses Flask logs"""
    
    print("🔇 Testing OBS Server Quiet Mode")
    print("=" * 40)
    
    # Test with quiet mode enabled (default)
    print("\n1. Testing with QUIET MODE ENABLED")
    print("   Should NOT see Flask request logs...")
    
    server_quiet = OBSWebServer(host='localhost', port=5001, quiet_mode=True)
    thread_quiet = server_quiet.start_background()
    
    # Wait for server to start
    time.sleep(2)
    
    # Make some requests
    try:
        print("   Making test requests...")
        for i in range(3):
            response = requests.get('http://localhost:5001/obs/session_stats', timeout=2)
            print(f"   Request {i+1}: Status {response.status_code}")
            time.sleep(0.5)
        
        print("   ✅ Quiet mode test complete - no Flask logs should appear above")
        
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print("\n🎉 Quiet Mode Test Results:")
    print("   - If you see NO Flask request logs above, quiet mode works!")
    print("   - If you see '127.0.0.1 - - [timestamp] GET /obs/...' logs, it's not working")
    
    print(f"\n📺 Test URLs (server running on port 5001):")
    print(f"   Item Table: http://localhost:5001/obs/item_table")
    print(f"   Session Stats: http://localhost:5001/obs/session_stats")
    print(f"   Setup Guide: http://localhost:5001")
    
    print(f"\n💡 The server will keep running for testing.")
    print(f"   Open the URLs in your browser to verify overlays work.")
    print(f"   No request logs should appear in this terminal!")
    
    input("\nPress Enter to stop the test server...")
    print("✅ Test completed!")


def test_verbose_mode():
    """Test that verbose mode shows Flask logs"""
    
    print("\n🔊 Testing VERBOSE MODE (for comparison)")
    print("   Should see Flask request logs...")
    
    server_verbose = OBSWebServer(host='localhost', port=5002, quiet_mode=False)
    thread_verbose = server_verbose.start_background()
    
    # Wait for server to start
    time.sleep(2)
    
    # Make some requests
    try:
        print("   Making test requests...")
        for i in range(2):
            response = requests.get('http://localhost:5002/obs/session_stats', timeout=2)
            print(f"   Request {i+1}: Status {response.status_code}")
            time.sleep(0.5)
        
        print("   ✅ Verbose mode test complete - Flask logs should appear above")
        
    except Exception as e:
        print(f"   ❌ Request failed: {e}")


if __name__ == "__main__":
    try:
        test_quiet_mode()
        # Uncomment to test verbose mode too:
        # test_verbose_mode()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    
    print("Test finished!")