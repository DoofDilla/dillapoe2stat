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
        """Display a summary of inventory items with key properties"""
        if not self.debug_enabled:
            return
        
        print(f"\n{prefix} Inventory summary ({len(inventory)} items):")
        print("=" * 60)
        print(f"{'#':<3} {'Type':<25} {'Stack':<6} {'Position':<8} {'ID':<10}")
        print("-" * 60)
        
        for i, item in enumerate(inventory):
            item_type = item.get('typeLine', 'Unknown')[:24]
            stack_size = item.get('stackSize', 1)
            position = f"({item.get('x', '?')},{item.get('y', '?')})"
            item_id = item.get('id', 'No ID')[:9]
            
            print(f"{i+1:<3} {item_type:<25} {stack_size:<6} {position:<8} {item_id:<10}")
    
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