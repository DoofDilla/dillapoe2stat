#!/usr/bin/env python3
"""
Test the OBS server with complete data including map runtime
"""

from obs_web_server import OBSWebServer

def main():
    print("🔍 Testing OBS server with complete data including map runtime...")
    
    # Create OBS server
    server = OBSWebServer()
    
    # Raw API items
    raw_added_items = [
        {
            'id': 'test123',
            'typeLine': 'Exalted Orb',
            'baseType': 'Exalted Orb',
            'rarity': 'Currency',
            'stackSize': 2,
        },
        {
            'id': 'test456', 
            'typeLine': 'Chaos Orb',
            'baseType': 'Chaos Orb',
            'rarity': 'Currency',
            'stackSize': 5,
        }
    ]
    
    session_progress = {
        'maps_completed': 3,
        'total_value': 15.7,
        'runtime': {'hours': 1, 'minutes': 25, 'seconds': 30}  # Session runtime
    }
    
    # Map info WITH map runtime (like the main script now sends)
    map_info_with_runtime = {
        'map_name': 'Cemetery of the Eternals',
        'level': 72,
        'seed': 'abc123',
        'map_runtime_seconds': 245  # 4m 5s map runtime
    }
    
    print(f"\n🔄 Calling update_item_table with map runtime: {map_info_with_runtime['map_runtime_seconds']}s")
    
    server.update_item_table(raw_added_items, [], session_progress, map_info_with_runtime)
    
    print("\n📊 Data stored in OBS server:")
    item_data = server.current_data['item_table']
    print(f"  Map runtime: {item_data['map_info'].get('map_runtime_seconds')}s")
    for item in item_data['added_items']:
        print(f"    - {item['name']}: {item['value_exalted']}ex (qty: {item['quantity']})")
    
    print("\n🎯 Testing HTML generation...")
    
    with server.app.test_client() as client:
        response = client.get('/obs/item_table')
        html = response.get_data(as_text=True)
        
        # Extract runtime and value lines
        lines = html.split('\n')
        for line in lines:
            if 'Runtime:' in line:
                print(f"  📝 {line.strip()}")
            elif 'Exalted Orb' in line and '<td>' in line:
                print(f"  📝 {line.strip()}")
            elif 'Net Value:' in line:
                print(f"  📝 {line.strip()}")

if __name__ == "__main__":
    main()