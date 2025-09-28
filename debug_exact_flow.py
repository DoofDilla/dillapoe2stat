#!/usr/bin/env python3
"""
Debug script to simulate EXACT data flow from main script to OBS overlay
"""

from obs_web_server import OBSWebServer
import time

def main():
    print("🔍 Simulating EXACT data flow from main script...")
    
    # Create OBS server
    server = OBSWebServer()
    
    # Simulate what the main script generates in take_post_snapshot()
    print("\n📊 Simulating analysis data (like inventory_analyzer.analyze_changes output)...")
    
    # This would be the output from analysis['added'] and analysis['removed']
    analysis_added = [
        {'name': 'Exalted Orb', 'type': 'Currency', 'rarity': 'normal', 'value_exalted': 1.0},
        {'name': 'Chaos Orb', 'type': 'Currency', 'rarity': 'normal', 'value_exalted': 0.007}
    ]
    analysis_removed = []
    
    print("\n📈 Simulating session progress data (like session_manager.get_session_progress output)...")
    
    # This would be the output from session_manager.get_session_progress()
    session_progress = {
        'maps_completed': 3,
        'total_value': 8.5,
        'runtime': {'hours': 1, 'minutes': 23, 'seconds': 45}  # This is session runtime, not map runtime
    }
    
    print("\n🏔️ Simulating map info data (like current_map_info)...")
    
    # This would be the value of self.current_map_info
    current_map_info = {
        'map_name': 'Cemetery of the Eternals',
        'level': 72,
        'seed': 'abc123def',
        'source': 'client_log'
    }
    
    print("\n🔄 Calling update_item_table exactly like main script does...")
    print(f"  analysis['added']: {len(analysis_added)} items")
    print(f"  analysis['removed']: {len(analysis_removed)} items") 
    print(f"  progress: {session_progress}")
    print(f"  current_map_info: {current_map_info}")
    
    # This is the EXACT call from line 328-332 in main script
    server.update_item_table(
        analysis_added,           # analysis['added']
        analysis_removed,         # analysis['removed']
        session_progress,         # progress
        current_map_info          # self.current_map_info
    )
    
    print("\n📊 Data stored in OBS server:")
    print(f"  item_table keys: {list(server.current_data['item_table'].keys())}")
    print(f"  added_items: {server.current_data['item_table']['added_items']}")
    print(f"  session_stats: {server.current_data['item_table']['session_stats']}")
    print(f"  map_info: {server.current_data['item_table']['map_info']}")
    print(f"  total_value: {server.current_data['item_table']['total_value']}")
    
    print("\n🎯 Testing HTML generation with this data...")
    
    # Get the stored data
    item_data = server.current_data['item_table']
    added = item_data['added_items']
    removed = item_data['removed_items']
    total = item_data['total_value']
    session = item_data['session_stats']
    map_info = item_data['map_info']
    
    html = server.overlay_manager._create_item_table_html(added, removed, total, session, map_info)
    
    print("Generated HTML preview (key sections):")
    
    # Extract key parts
    lines = html.split('\n')
    for i, line in enumerate(lines):
        if 'map_name' in line or 'Runtime:' in line or 'Exalted Orb' in line or 'Net Value:' in line:
            print(f"  Line {i}: {line.strip()}")
    
    # Check what the /obs/item_table endpoint returns
    print("\n🌐 Testing /obs/item_table endpoint (what OBS would see)...")
    with server.app.test_client() as client:
        response = client.get('/obs/item_table')
        endpoint_html = response.get_data(as_text=True)
        
        # Extract same key parts
        endpoint_lines = endpoint_html.split('\n')
        for i, line in enumerate(endpoint_lines):
            if 'map_name' in line or 'Runtime:' in line or 'Exalted Orb' in line or 'Net Value:' in line:
                print(f"  Endpoint Line {i}: {line.strip()}")

if __name__ == "__main__":
    main()