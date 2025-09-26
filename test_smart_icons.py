#!/usr/bin/env python3
"""
Quick test script to debug smart icon system
"""

from icon_color_analyzer import IconColorMapper, ColorAnalyzer

def test_smart_icons():
    """Test the smart icon system with sample items"""
    
    # Create instances
    color_analyzer = ColorAnalyzer()
    icon_mapper = IconColorMapper()
    
    # Test items
    test_items = [
        {'typeLine': 'Twilight Reliquary Key', 'icon': None},
        {'typeLine': 'Scroll of Wisdom', 'icon': None},
        {'typeLine': 'Omen of Amelioration', 'icon': None}, 
        {'typeLine': 'Precursor Tablet', 'icon': None},
        {'typeLine': 'Chaos Orb', 'icon': None},
        {'typeLine': 'Exalted Orb', 'icon': None},
        {'typeLine': 'Divine Orb', 'icon': None}
    ]
    
    print("🎯 TESTING SMART UNICODE SYSTEM")
    print("="*50)
    
    for item in test_items:
        item_name = item['typeLine']
        
        # Test shape detection
        shape = color_analyzer.detect_item_shape(item)
        print(f"\n📦 {item_name}")
        print(f"   Shape: {shape}")
        
        # Test smart unicode
        try:
            smart_char = icon_mapper.get_smart_unicode_for_item(item, color_analyzer)
            print(f"   Smart: {smart_char}")
        except Exception as e:
            print(f"   ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        # Test old method for comparison
        old_char = icon_mapper.get_emoji_for_color('gold')
        print(f"   Old:   {old_char}")

if __name__ == '__main__':
    test_smart_icons()