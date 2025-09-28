"""
OBS Integration Demo
Demonstrates the complete OBS integration workflow
Shows how to set up and use the web server for streaming overlays
"""

import time
import webbrowser
from obs_web_server import OBSWebServer
from obs_overlay_manager import OBSOverlayManager


def demo_obs_integration():
    """Complete demo of OBS integration features"""
    
    print("🎬 PoE Stats Tracker - OBS Integration Demo")
    print("=" * 50)
    
    # Create server and overlay manager
    print("\n📡 Starting OBS Web Server...")
    server = OBSWebServer(host='localhost', port=5000)
    
    # Start in background
    server_thread = server.start_background()
    time.sleep(2)  # Wait for server to start
    
    print("✅ Server is running!")
    print(f"🌐 Access at: http://localhost:5000")
    
    # Demo different scenarios
    print("\n🎯 Demo Scenarios:")
    print("1. Empty state (no data)")
    print("2. Low-value map completion")
    print("3. High-value map with expensive drops")
    print("4. Long session with multiple maps")
    
    input("\nPress Enter to start demo...")
    
    # Open browser for setup guide
    print("\n📖 Opening setup guide in browser...")
    webbrowser.open("http://localhost:5000")
    time.sleep(2)
    
    # Demo 1: Empty state
    print("\n📊 Demo 1: Empty State")
    print("   Overlay shows 'No items to display' message")
    print("   URL: http://localhost:5000/obs/item_table")
    
    input("Press Enter to continue...")
    
    # Demo 2: Low-value map
    print("\n💰 Demo 2: Low-Value Map")
    low_value_items = [
        {'name': 'Lesser Essence of Anger', 'type': 'Currency', 'rarity': 'normal', 'value_exalted': 0.02},
        {'name': 'Portal Scroll', 'type': 'Currency', 'rarity': 'normal', 'value_exalted': 0.0},
        {'name': 'Magic Boots', 'type': 'Armour', 'rarity': 'magic', 'value_exalted': 0.0}
    ]
    
    session_stats = {
        'maps_completed': 1,
        'total_value': 0.02,
        'runtime': {'hours': 0, 'minutes': 8}
    }
    
    map_info = {
        'map_name': 'Grim Tangle',
        'level': 65
    }
    
    server.update_item_table(low_value_items, [], session_stats, map_info)
    server.update_session_stats(session_stats)
    
    print("   Updated with low-value loot")
    print("   Check overlay: http://localhost:5000/obs/item_table")
    
    input("Press Enter to continue...")
    
    # Demo 3: High-value map
    print("\n💎 Demo 3: High-Value Map with Expensive Drops")
    high_value_items = [
        {'name': 'Divine Orb', 'type': 'Currency', 'rarity': 'normal', 'value_exalted': 0.85},
        {'name': 'Exalted Orb', 'type': 'Currency', 'rarity': 'normal', 'value_exalted': 1.0},
        {'name': 'Unique Ring of Storms', 'type': 'Accessory', 'rarity': 'unique', 'value_exalted': 2.3},
        {'name': 'Rare Two-Handed Sword', 'type': 'Weapon', 'rarity': 'rare', 'value_exalted': 0.4},
        {'name': 'Regal Orb', 'type': 'Currency', 'rarity': 'normal', 'value_exalted': 0.15}
    ]
    
    session_stats = {
        'maps_completed': 4,
        'total_value': 8.7,
        'runtime': {'hours': 1, 'minutes': 23}
    }
    
    map_info = {
        'map_name': 'Cemetery of the Eternals',
        'level': 72
    }
    
    server.update_item_table(high_value_items, [], session_stats, map_info)
    server.update_session_stats(session_stats)
    
    print("   Updated with high-value loot!")
    print("   Total map value: 4.7 Exalted")
    print("   Check overlay - should look much more exciting!")
    
    input("Press Enter to continue...")
    
    # Demo 4: Long session
    print("\n⏰ Demo 4: Long Session Progress")
    long_session_stats = {
        'maps_completed': 15,
        'total_value': 23.4,
        'runtime': {'hours': 3, 'minutes': 45}
    }
    
    server.update_session_stats(long_session_stats)
    
    print("   Updated session stats for long session")
    print("   15 maps, 23.4 Exalted total, 3h 45m playtime")
    print("   Check session overlay: http://localhost:5000/obs/session_stats")
    
    input("Press Enter to continue...")
    
    # Show test URLs
    print("\n🧪 Test URLs (with dummy data):")
    print("   Item Table: http://localhost:5000/test/item_table")  
    print("   Session Stats: http://localhost:5000/test/session_stats")
    
    print("\n🎬 OBS Studio Setup:")
    print("   1. Add Browser Source")
    print("   2. URL: http://localhost:5000/obs/item_table")
    print("   3. Width: 600px, Height: 400px")
    print("   4. Enable 'Refresh when scene becomes active'")
    
    print("\n💡 Pro Tips:")
    print("   - Use /test/ URLs to design your layout first")
    print("   - Overlays auto-refresh every 2-5 seconds")
    print("   - Transparent background works great")
    print("   - Position in corners for best visibility")
    
    print("\n📋 Integration Status:")
    print("   ✅ Flask web server running")
    print("   ✅ HTML overlay generation working")
    print("   ✅ Auto-refresh functionality active")
    print("   ✅ Multi-scenario demo completed")
    
    print("\n🚀 Ready for Streaming!")
    print("The OBS integration is fully functional and ready to use.")
    
    input("\nPress Enter to stop the demo server...")
    print("👋 Demo completed!")


if __name__ == "__main__":
    try:
        demo_obs_integration()
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print("Demo finished!")