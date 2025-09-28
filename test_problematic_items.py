#!/usr/bin/env python3
"""
Test the OBS server with problematic items that could cause None errors
"""

from obs_web_server import OBSWebServer

def main():
    print("🔍 Testing OBS server with problematic items...")
    
    # Create OBS server
    server = OBSWebServer()
    
    # Test with problematic items that could have None values
    problematic_items = [
        {
            'id': 'test1',
            'typeLine': None,  # None value
            'baseType': 'Some Item',
            'rarity': 'Currency'
        },
        {
            'id': 'test2',
            'typeLine': 'Valid Item',
            'baseType': None,  # None value
            'rarity': None  # None value
        },
        {
            'id': 'test3'
            # Missing most fields
        }
    ]
    
    session_data = {
        'maps_completed': 1,
        'total_value': 2.5,
        'runtime': {'hours': 0, 'minutes': 5, 'seconds': 0}
    }
    
    map_data = {
        'map_name': 'Test Map',
        'level': 68
    }
    
    print("\n🔄 Calling update_item_table with problematic items...")
    
    try:
        server.update_item_table(problematic_items, [], session_data, map_data)
        print("✅ update_item_table completed successfully")
        
        # Test HTML generation
        with server.app.test_client() as client:
            response = client.get('/obs/item_table')
            if response.status_code == 200:
                print("✅ HTML generation completed successfully")
                html = response.get_data(as_text=True)
                print(f"📝 HTML contains {len(html)} characters")
            else:
                print(f"❌ HTML generation failed with status {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()