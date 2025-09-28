"""
Test OBS Integration
Tests the OBS web server and overlay generation
"""

import time
import threading
from obs_web_server import OBSWebServer


def test_obs_server():
    """Test the OBS web server with dummy data"""
    
    print("Starting OBS Web Server Test...")
    
    # Create server instance
    server = OBSWebServer(host='localhost', port=5000)
    
    # Start server in background
    server_thread = server.start_background()
    
    # Wait a moment for server to start
    time.sleep(2)
    
    print("\nServer should be running!")
    print("Open these URLs in your browser:")
    print("  Setup Guide: http://localhost:5000")
    print("  Item Table Test: http://localhost:5000/test/item_table")
    print("  Session Stats Test: http://localhost:5000/test/session_stats")
    
    # Test updating data programmatically
    print("\nTesting data updates...")
    
    # Update item table
    dummy_added = [
        {'name': 'Divine Orb', 'type': 'Currency', 'rarity': 'normal', 'value_exalted': 0.8},
        {'name': 'Rare Sword', 'type': 'Weapon', 'rarity': 'rare', 'value_exalted': 0.5}
    ]
    
    dummy_session = {
        'maps_completed': 3,
        'total_value': 8.2,
        'runtime': {'hours': 1, 'minutes': 15}
    }
    
    dummy_map = {
        'map_name': 'Test Map',
        'level': 70
    }
    
    server.update_item_table(dummy_added, [], dummy_session, dummy_map)
    server.update_session_stats(dummy_session)
    
    print("Data updated! Check the overlays:")
    print("  Item Table: http://localhost:5000/obs/item_table")
    print("  Session Stats: http://localhost:5000/obs/session_stats")
    
    print("\nPress Enter to stop the server...")
    input()
    
    print("Test completed!")


def test_flask_install():
    """Check if Flask is installed"""
    try:
        import flask
        print(f"Flask is installed (version {flask.__version__})")
        return True
    except ImportError:
        print("Flask is not installed!")
        print("Install with: pip install flask")
        return False


if __name__ == "__main__":
    print("OBS Integration Test")
    print("=" * 40)
    
    # Check Flask installation
    if not test_flask_install():
        exit(1)
    
    # Run server test
    test_obs_server()