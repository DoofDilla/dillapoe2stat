import json
import os
from datetime import datetime
from pathlib import Path

class InventoryDebugger:
    def __init__(self, debug_enabled=False, output_dir=None):
        self.debug_enabled = debug_enabled
        if output_dir is None:
            output_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "debug"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def dump_inventory_to_console(self, inventory, prefix="[INVENTORY]"):
        """Dump inventory items to console in readable JSON format"""
        if not self.debug_enabled:
            return
        
        print(f"\n{prefix} Inventory dump ({len(inventory)} items):")
        print("=" * 60)
        for i, item in enumerate(inventory):
            print(f"Item {i+1}:")
            print(json.dumps(item, indent=2, ensure_ascii=False))
            print("-" * 40)
    
    def dump_inventory_to_file(self, inventory, filename_prefix="inventory", metadata=None):
        """Dump inventory items to a JSON file with timestamp"""
        if not self.debug_enabled:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        debug_data = {
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "item_count": len(inventory),
            "items": inventory
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] Inventory dumped to: {filepath}")
            return filepath
        except Exception as e:
            print(f"[DEBUG] Error writing inventory to file: {e}")
            return None
    
    def dump_item_summary(self, inventory, prefix="[SUMMARY]"):
        """Display a summary of inventory items with key properties and detailed analysis for important items"""
        if not self.debug_enabled:
            return
        
        print(f"\n{prefix} Inventory summary ({len(inventory)} items):")
        print("=" * 80)
        print(f"{'#':<3} {'Type':<25} {'Stack':<6} {'Rarity':<10} {'Position':<10} {'ID':<10}")
        print("-" * 80)
        
        # Track important items for detailed analysis
        important_items = []
        
        for i, item in enumerate(inventory):
            item_type = item.get('typeLine', 'Unknown')[:24]
            base_type = item.get('baseType', '')[:24]
            stack_size = item.get('stackSize', 1)
            rarity = item.get('rarity', 'Normal')[:9]
            position = f"({item.get('x', '?')},{item.get('y', '?')})"
            item_id = item.get('id', 'No ID')[:9]
            
            # Mark important items for detailed analysis
            if any(keyword in item_type.lower() for keyword in ['precursor', 'tablet', 'grand', 'project', 'divine', 'exalted', 'jeweller', 'orb']):
                important_items.append((i+1, item))
                marker = "⭐"
            else:
                marker = "  "
            
            print(f"{marker}{i+1:<3} {item_type:<25} {stack_size:<6} {rarity:<10} {position:<10} {item_id:<10}")
        
        # Show detailed analysis for important items
        if important_items:
            print(f"\n{prefix} 🔍 DETAILED ANALYSIS for important items:")
            print("=" * 80)
            
            for item_num, item in important_items:
                print(f"\n--- Item #{item_num}: {item.get('typeLine', 'Unknown')} ---")
                print(f"  🏷️  Type Line: '{item.get('typeLine', 'N/A')}'")
                print(f"  📦 Base Type: '{item.get('baseType', 'N/A')}'")
                print(f"  🔤 Name: '{item.get('name', 'N/A')}'")
                print(f"  🎨 Rarity: {item.get('rarity', 'N/A')}")
                print(f"  🆔 ID: {item.get('id', 'N/A')}")
                print(f"  📍 Position: ({item.get('x', '?')}, {item.get('y', '?')})")
                print(f"  📊 Stack: {item.get('stackSize', 1)}/{item.get('maxStackSize', '?')}")
                print(f"  ✅ Identified: {item.get('identified', 'N/A')}")
                print(f"  🔸 Corrupted: {item.get('corrupted', False)}")
                
                # Show properties if available
                if 'properties' in item and item['properties']:
                    print(f"  ⚙️  Properties:")
                    for prop in item['properties'][:3]:  # Show first 3 properties
                        name = prop.get('name', 'Unknown')
                        values = prop.get('values', [])
                        if values:
                            value_str = ', '.join([str(v[0]) if isinstance(v, list) else str(v) for v in values[:2]])
                            print(f"     - {name}: {value_str}")
                        else:
                            print(f"     - {name}: (no values)")
                
                # Price check hints
                price_key = item.get('baseType') or item.get('typeLine', 'Unknown')
                print(f"  💰 Price lookup would use: '{price_key}'")
                
                # Icon hint for debugging
                icon = item.get('icon', '')
                if icon:
                    icon_hint = icon.split('/')[-1] if '/' in icon else icon
                    print(f"  🖼️  Icon hint: {icon_hint[:50]}{'...' if len(icon_hint) > 50 else ''}")
                
                print()  # Empty line between items
    
    def analyze_item_detailed(self, item, item_index=None):
        """Analyze a single item in detail for debugging pricing issues"""
        if not self.debug_enabled:
            return
        
        print("\n" + "="*80)
        if item_index is not None:
            print(f"DETAILED ITEM ANALYSIS #{item_index + 1}")
        else:
            print("DETAILED ITEM ANALYSIS")
        print("="*80)
        
        # Basic identification fields
        print("🔍 IDENTIFICATION:")
        print(f"  name: {repr(item.get('name', None))}")
        print(f"  typeLine: {repr(item.get('typeLine', None))}")
        print(f"  baseType: {repr(item.get('baseType', None))}")
        print(f"  id: {item.get('id', 'None')}")
        
        # Frame and rarity info
        print(f"\n🎨 VISUAL/RARITY:")
        print(f"  frameType: {item.get('frameType', 'None')}")
        print(f"  rarity: {repr(item.get('rarity', None))}")
        print(f"  identified: {item.get('identified', 'None')}")
        print(f"  corrupted: {item.get('corrupted', 'False')}")
        
        # Position and stack info
        print(f"\n📍 POSITION/STACK:")
        print(f"  position: ({item.get('x', '?')}, {item.get('y', '?')})")
        print(f"  stackSize: {item.get('stackSize', 'None')}")
        print(f"  maxStackSize: {item.get('maxStackSize', 'None')}")
        
        # Icon and category hints
        print(f"\n🖼️ ICON/CATEGORY:")
        icon = item.get('icon', '')
        print(f"  icon: {icon}")
        if icon:
            # Extract category hints from icon path
            icon_parts = icon.split('/')
            if len(icon_parts) > 5:
                category_hint = icon_parts[5] if len(icon_parts) > 5 else 'unknown'
                print(f"  icon_category: {category_hint}")
        
        # Properties
        properties = item.get('properties', [])
        if properties:
            print(f"\n⚙️ PROPERTIES ({len(properties)}):")
            for i, prop in enumerate(properties):
                prop_name = prop.get('name', f'Property {i}')
                prop_values = prop.get('values', [])
                prop_display = prop.get('displayMode', 0)
                prop_type = prop.get('type', 'None')
                print(f"  {i+1}. {prop_name}")
                print(f"     values: {prop_values}")
                print(f"     displayMode: {prop_display}, type: {prop_type}")
        
        # Mods (explicit, implicit, etc.)
        mod_types = ['explicitMods', 'implicitMods', 'craftedMods', 'enchantMods', 'fracturedMods']
        for mod_type in mod_types:
            mods = item.get(mod_type, [])
            if mods:
                print(f"\n🔮 {mod_type.upper()} ({len(mods)}):")
                for i, mod in enumerate(mods):
                    print(f"  {i+1}. {mod}")
        
        # Try price lookup using existing methods
        print(f"\n💰 PRICE ANALYSIS:")
        try:
            from price_check_poe2 import get_value_for_inventory_item, guess_category_from_item
            
            # Try category guessing
            guessed_cat = guess_category_from_item(item)
            print(f"  guessed_category: {guessed_cat}")
            
            # Try price lookup
            chaos, ex, category = get_value_for_inventory_item(item)
            if chaos is not None:
                print(f"  ✅ FOUND PRICE: {chaos:.3f}c | {ex:.3f}ex | Category: {category}")
            else:
                print(f"  ❌ NO PRICE FOUND")
                
                # Try manual price lookup
                try:
                    from manual_prices import get_manual_item_price
                    item_name = item.get('typeLine') or item.get('baseType') or item.get('name')
                    if item_name:
                        manual_result = get_manual_item_price(item_name)
                        if manual_result:
                            m_chaos, m_ex, m_cat = manual_result
                            print(f"  ✅ MANUAL PRICE: {m_chaos:.3f}c | {m_ex:.3f}ex | Category: {m_cat}")
                        else:
                            print(f"  ❌ NO MANUAL PRICE for '{item_name}'")
                except ImportError:
                    print(f"  ⚠️ Manual price lookup not available")
            
        except Exception as e:
            print(f"  ❌ Price analysis error: {e}")
        
        print("="*80)
    
    def find_and_analyze_item_by_name(self, inventory, search_name, prefix="[ITEM_SEARCH]"):
        """Find and analyze items matching a name pattern"""
        if not self.debug_enabled:
            return
        
        print(f"\n{prefix} Searching for items matching: '{search_name}'")
        matches = []
        
        for i, item in enumerate(inventory):
            item_name = item.get('name', '')
            type_line = item.get('typeLine', '')
            base_type = item.get('baseType', '')
            
            # Check if search term matches any name field
            search_lower = search_name.lower()
            if (search_lower in item_name.lower() or 
                search_lower in type_line.lower() or 
                search_lower in base_type.lower()):
                matches.append((i, item))
        
        if matches:
            print(f"Found {len(matches)} matching item(s):")
            for i, (item_index, item) in enumerate(matches):
                print(f"\n--- Match {i+1} ---")
                self.analyze_item_detailed(item, item_index)
        else:
            print(f"No items found matching '{search_name}'")
    
    def compare_inventories(self, before, after, prefix="[DIFF]"):
        """Compare two inventories and show differences"""
        if not self.debug_enabled:
            return
        
        print(f"\n{prefix} Inventory comparison:")
        print("=" * 60)
        print(f"Before: {len(before)} items")
        print(f"After:  {len(after)} items")
        
        # Simple comparison by item ID or position
        before_ids = {item.get('id') or f"{item.get('typeLine')}_{item.get('x')}_{item.get('y')}" for item in before}
        after_ids = {item.get('id') or f"{item.get('typeLine')}_{item.get('x')}_{item.get('y')}" for item in after}
        
        added_ids = after_ids - before_ids
        removed_ids = before_ids - after_ids
        
        print(f"Added items: {len(added_ids)}")
        for item_id in added_ids:
            item = next((i for i in after if (i.get('id') or f"{i.get('typeLine')}_{i.get('x')}_{i.get('y')}") == item_id), None)
            if item:
                print(f"  + {item.get('typeLine', 'Unknown')}")
        
        print(f"Removed items: {len(removed_ids)}")
        for item_id in removed_ids:
            item = next((i for i in before if (i.get('id') or f"{i.get('typeLine')}_{i.get('x')}_{i.get('y')}") == item_id), None)
            if item:
                print(f"  - {item.get('typeLine', 'Unknown')}")
    
    def analyze_item_properties(self, inventory, prefix="[ANALYSIS]"):
        """Analyze and display statistics about item properties"""
        if not self.debug_enabled:
            return
        
        print(f"\n{prefix} Item property analysis:")
        print("=" * 60)
        
        # Collect statistics
        properties = {}
        for item in inventory:
            for key in item.keys():
                if key not in properties:
                    properties[key] = 0
                properties[key] += 1
        
        print("Property frequency:")
        for prop, count in sorted(properties.items(), key=lambda x: x[1], reverse=True):
            print(f"  {prop}: {count} items ({count/len(inventory)*100:.1f}%)")
        
        # Stack size analysis
        stack_sizes = [item.get('stackSize', 1) for item in inventory]
        if stack_sizes:
            print(f"\nStack size stats:")
            print(f"  Total stacks: {len(stack_sizes)}")
            print(f"  Max stack: {max(stack_sizes)}")
            print(f"  Min stack: {min(stack_sizes)}")
            print(f"  Avg stack: {sum(stack_sizes)/len(stack_sizes):.1f}")
    
    def set_debug_enabled(self, enabled):
        """Toggle debug mode on/off"""
        self.debug_enabled = enabled
        status = "enabled" if enabled else "disabled"
        print(f"[DEBUG] Inventory debugging {status}")
    
    def quick_item_analysis(self, inventory, show_details=False):
        """Quick analysis of inventory for debugging purposes"""
        if not self.debug_enabled:
            return
        
        print(f"\n[QUICK-ANALYSIS] {len(inventory)} items:")
        
        # Group by type
        type_counts = {}
        total_value = 0
        
        for item in inventory:
            item_type = item.get('typeLine', 'Unknown')
            stack_size = item.get('stackSize', 1)
            
            if item_type not in type_counts:
                type_counts[item_type] = {'count': 0, 'total_stack': 0}
            
            type_counts[item_type]['count'] += 1
            type_counts[item_type]['total_stack'] += stack_size
        
        # Display summary
        print("Item type summary:")
        for item_type, data in sorted(type_counts.items(), key=lambda x: x[1]['total_stack'], reverse=True):
            if data['count'] > 1:
                print(f"  {item_type}: {data['count']} items, {data['total_stack']} total stack")
            else:
                print(f"  {item_type}: {data['total_stack']} stack")
        
        if show_details:
            print("\nDetailed item list:")
            for i, item in enumerate(inventory):
                rarity = item.get('rarity', 'Unknown')
                corrupted = " (corrupted)" if item.get('corrupted') else ""
                identified = " (unidentified)" if not item.get('identified', True) else ""
                print(f"  {i+1}. {item.get('typeLine', 'Unknown')} [{rarity}]{corrupted}{identified}")
    
    def export_item_list(self, inventory, filename="item_list.txt"):
        """Export a simple text list of items"""
        if not self.debug_enabled:
            return None
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Inventory Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n")
                f.write(f"Total items: {len(inventory)}\n\n")
                
                for i, item in enumerate(inventory):
                    stack = f" x{item.get('stackSize', 1)}" if item.get('stackSize', 1) > 1 else ""
                    pos = f"@({item.get('x', '?')},{item.get('y', '?')})"
                    rarity = item.get('rarity', 'Unknown')
                    
                    f.write(f"{i+1:3}. {item.get('typeLine', 'Unknown')}{stack} [{rarity}] {pos}\n")
            
            print(f"[DEBUG] Item list exported to: {filepath}")
            return filepath
        except Exception as e:
            print(f"[DEBUG] Error exporting item list: {e}")
            return None
    
    def analyze_item_detailed(self, item, prefix="[ITEM-DETAIL]"):
        """Provide detailed analysis of a single item for debugging"""
        if not self.debug_enabled:
            return
        
        print(f"\n{prefix} Detailed item analysis:")
        print("=" * 50)
        
        # Basic identification
        print("📋 IDENTIFICATION:")
        print(f"  Type Line: {item.get('typeLine', 'N/A')}")
        print(f"  Base Type: {item.get('baseType', 'N/A')}")
        print(f"  Name: {item.get('name', 'N/A')}")
        print(f"  ID: {item.get('id', 'N/A')}")
        
        # Visual and rarity
        print("\n🎨 VISUAL/RARITY:")
        print(f"  Rarity: {item.get('rarity', 'N/A')}")
        print(f"  Frame Type: {item.get('frameType', 'N/A')}")
        print(f"  Identified: {item.get('identified', 'N/A')}")
        print(f"  Corrupted: {item.get('corrupted', 'N/A')}")
        
        # Position and stack
        print("\n📍 POSITION/STACK:")
        print(f"  Position: ({item.get('x', 'N/A')}, {item.get('y', 'N/A')})")
        print(f"  Width: {item.get('w', 'N/A')}")
        print(f"  Height: {item.get('h', 'N/A')}")
        print(f"  Stack Size: {item.get('stackSize', 'N/A')}")
        print(f"  Max Stack Size: {item.get('maxStackSize', 'N/A')}")
        
        # Icon and category hints
        print("\n🔗 ICON/CATEGORY:")
        print(f"  Icon: {item.get('icon', 'N/A')[:50]}{'...' if len(str(item.get('icon', ''))) > 50 else ''}")
        print(f"  League: {item.get('league', 'N/A')}")
        
        # Properties
        if 'properties' in item and item['properties']:
            print("\n⚙️ PROPERTIES:")
            for prop in item['properties']:
                name = prop.get('name', 'Unknown')
                values = prop.get('values', [])
                if values:
                    value_str = ', '.join([str(v[0]) if isinstance(v, list) else str(v) for v in values])
                    print(f"  {name}: {value_str}")
                else:
                    print(f"  {name}: (no values)")
        
        # Mods
        if any(key in item for key in ['implicitMods', 'explicitMods', 'craftedMods']):
            print("\n🔧 MODS:")
            for mod_type in ['implicitMods', 'explicitMods', 'craftedMods']:
                mods = item.get(mod_type, [])
                if mods:
                    print(f"  {mod_type.replace('Mods', '').capitalize()}:")
                    for mod in mods:
                        print(f"    - {mod}")
        
        # Price analysis attempt
        print("\n💰 PRICE ANALYSIS:")
        print(f"  Would try to price as: '{item.get('baseType') or item.get('typeLine', 'Unknown')}'")
        print(f"  Category hints: rarity={item.get('rarity')}, corrupted={item.get('corrupted')}")
        print(f"  Stack considerations: current={item.get('stackSize', 1)}, max={item.get('maxStackSize', 1)}")
    
    def find_and_analyze_item_by_name(self, inventory, item_name, prefix="[SEARCH]"):
        """Find items by name and analyze them in detail"""
        if not self.debug_enabled:
            return
        
        print(f"\n{prefix} Searching for item: '{item_name}'")
        found_items = []
        
        # Search in multiple fields
        for item in inventory:
            type_line = item.get('typeLine', '').lower()
            base_type = item.get('baseType', '').lower()
            name = item.get('name', '').lower()
            search_term = item_name.lower()
            
            if (search_term in type_line or 
                search_term in base_type or 
                search_term in name or
                type_line == search_term or
                base_type == search_term):
                found_items.append(item)
        
        if found_items:
            print(f"✅ Found {len(found_items)} matching item(s):")
            for i, item in enumerate(found_items):
                print(f"\n--- Match {i+1}/{len(found_items)} ---")
                self.analyze_item_detailed(item, f"{prefix}-{i+1}")
        else:
            print(f"❌ No items found matching: '{item_name}'")
            print("\n📋 Available item types in inventory:")
            unique_types = set()
            for item in inventory:
                type_line = item.get('typeLine', 'Unknown')
                base_type = item.get('baseType', '')
                name = item.get('name', '')
                
                unique_types.add(type_line)
                if base_type and base_type != type_line:
                    unique_types.add(base_type)
                if name and name != type_line:
                    unique_types.add(name)
            
            sorted_types = sorted(list(unique_types))
            for item_type in sorted_types[:20]:  # Show first 20
                print(f"  - {item_type}")
            
            if len(sorted_types) > 20:
                print(f"  ... and {len(sorted_types) - 20} more types")