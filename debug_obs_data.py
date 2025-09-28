#!/usr/bin/env python3
"""
Debug script to check OBS server data state
"""

from obs_web_server import OBSWebServer

def main():
    print("🔍 Creating fresh OBS server instance...")
    server = OBSWebServer()
    
    print("📊 Current data state:")
    print(f"  item_table: {server.current_data['item_table']}")
    print(f"  session_stats: {server.current_data['session_stats']}")
    print(f"  last_update: {server.current_data['last_update']}")
    
    print("\n🧪 Testing update_item_table method...")
    
    # Simulate calling update_item_table like the main script does
    dummy_added = [{'name': 'Test Item', 'value_exalted': 1.5}]
    dummy_removed = []
    dummy_progress = {'maps_completed': 3, 'total_value': 4.5}
    dummy_map_info = {'map_name': 'Test Map', 'level': 68}
    
    server.update_item_table(dummy_added, dummy_removed, dummy_progress, dummy_map_info)
    
    print("📊 Data state AFTER update:")
    print(f"  item_table: {server.current_data['item_table']}")
    print(f"  session_stats: {server.current_data['session_stats']}")
    print(f"  last_update: {server.current_data['last_update']}")
    
    print("\n🎯 Checking what HTML would be generated...")
    html = server.overlay_manager._create_item_table_html(
        dummy_added, dummy_removed, 1.5, dummy_progress, dummy_map_info
    )
    
    # Show first 500 chars of HTML
    print(f"Generated HTML (first 500 chars):")
    print(html[:500] + "..." if len(html) > 500 else html)

if __name__ == "__main__":
    main()