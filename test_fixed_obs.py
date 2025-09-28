#!/usr/bin/env python3
"""
Test the fixed OBS server with RAW API items (like the main script sends)
"""

from obs_web_server import OBSWebServer

def main():
    print("🔍 Testing fixed OBS server with RAW API items...")
    
    # Create OBS server
    server = OBSWebServer()
    
    # Simulate RAW API items (what inventory_analyzer.analyze_changes actually returns)
    raw_added_items = [
        {
            'id': 'test123',
            'typeLine': 'Exalted Orb',
            'baseType': 'Exalted Orb',
            'rarity': 'Currency',
            'stackSize': 1,
            'x': 5,
            'y': 2
        },
        {
            'id': 'test456', 
            'typeLine': 'Chaos Orb',
            'baseType': 'Chaos Orb',
            'rarity': 'Currency',
            'stackSize': 3,
            'x': 6,
            'y': 2
        }
    ]
    
    raw_removed_items = []
    
    session_progress = {
        'maps_completed': 5,
        'total_value': 12.3,
        'runtime': {'hours': 2, 'minutes': 15, 'seconds': 30}
    }
    
    current_map_info = {
        'map_name': 'Vaal Temple',
        'level': 75,
        'seed': 'xyz789'
    }
    
    print("\n🔄 Calling update_item_table with RAW API items...")
    print(f"  Raw added items: {[item['typeLine'] for item in raw_added_items]}")
    
    # Call with raw API items (like main script does)
    server.update_item_table(raw_added_items, raw_removed_items, session_progress, current_map_info)
    
    print("\n📊 Data stored in OBS server AFTER processing:")
    item_data = server.current_data['item_table']
    print(f"  Processed added items:")
    for item in item_data['added_items']:
        print(f"    - {item.get('name', 'Unknown')}: {item.get('value_exalted', 0)}ex ({item.get('type', 'Unknown')})")
    print(f"  Total value: {item_data['total_value']}ex")
    
    print("\n🎯 Testing HTML generation with processed data...")
    
    # Test what OBS Browser Source would see
    with server.app.test_client() as client:
        response = client.get('/obs/item_table')
        html = response.get_data(as_text=True)
        
        # Check for real item names and values
        if 'Exalted Orb' in html:
            print("  ✅ Found 'Exalted Orb' in HTML")
        else:
            print("  ❌ 'Exalted Orb' NOT found in HTML")
            
        if 'Unknown' in html:
            print("  ⚠️  Still contains 'Unknown' items")
        else:
            print("  ✅ No 'Unknown' items found")
            
        if 'Net Value: 0c' in html:
            print("  ❌ Still showing 0 value")
        else:
            print("  ✅ Non-zero values detected")
            
        # Show key lines
        lines = html.split('\n')
        for line in lines:
            if 'Exalted Orb' in line or 'Net Value:' in line or 'Runtime:' in line:
                print(f"  📝 {line.strip()}")

if __name__ == "__main__":
    main()