"""
Inventory analysis utilities for PoE Stats Tracker
Handles inventory comparison and item analysis
"""


def inv_key(item):
    """Generate a unique key for inventory items"""
    return (
        item.get("id")
        or f"{item.get('typeLine')}|{item.get('x')},{item.get('y')}|{item.get('baseType')}"
    )


def diff_inventories(before, after):
    """
    Compare two inventories and return added/removed items
    
    Args:
        before: List of items from pre-snapshot
        after: List of items from post-snapshot
    
    Returns:
        tuple: (added_items, removed_items)
    """
    before_keys = {inv_key(i): i for i in before}
    after_keys = {inv_key(i): i for i in after}

    added = [after_keys[k] for k in after_keys if k not in before_keys]
    removed = [before_keys[k] for k in before_keys if k not in after_keys]
    
    return added, removed


class InventoryAnalyzer:
    """Handles inventory analysis and comparison operations"""
    
    def __init__(self):
        pass
    
    def analyze_changes(self, pre_inventory, post_inventory):
        """
        Analyze changes between pre and post inventories
        
        Args:
            pre_inventory: Items before map run
            post_inventory: Items after map run
        
        Returns:
            dict: Analysis results containing added/removed items and metadata
        """
        if not pre_inventory:
            return {
                'error': 'No pre-inventory available',
                'added': [],
                'removed': []
            }
        
        added, removed = diff_inventories(pre_inventory, post_inventory)
        
        return {
            'added': added,
            'removed': removed,
            'added_count': len(added),
            'removed_count': len(removed),
            'pre_inventory_size': len(pre_inventory),
            'post_inventory_size': len(post_inventory),
            'net_change': len(added) - len(removed)
        }
    
    def get_item_summary(self, items):
        """
        Get a summary of items with their key properties
        
        Args:
            items: List of inventory items
        
        Returns:
            dict: Summary information
        """
        if not items:
            return {'total_items': 0, 'unique_types': 0, 'total_stacks': 0}
        
        unique_types = set()
        total_stacks = 0
        
        for item in items:
            item_type = item.get('typeLine') or item.get('baseType') or 'Unknown'
            unique_types.add(item_type)
            total_stacks += item.get('stackSize', 1)
        
        return {
            'total_items': len(items),
            'unique_types': len(unique_types),
            'total_stacks': total_stacks,
            'avg_stack_size': total_stacks / len(items) if items else 0
        }
    
    def categorize_items(self, items):
        """
        Categorize items by type for analysis
        
        Args:
            items: List of inventory items
        
        Returns:
            dict: Items categorized by type
        """
        categories = {
            'currency': [],
            'gems': [],
            'equipment': [],
            'consumables': [],
            'other': []
        }
        
        for item in items:
            frame_type = item.get('frameType', 0)
            icon = item.get('icon', '').lower()
            type_line = item.get('typeLine', '').lower()
            
            if frame_type == 5 or 'currency' in icon or 'orb' in type_line:
                categories['currency'].append(item)
            elif 'gem' in icon or frame_type == 4:
                categories['gems'].append(item)
            elif frame_type in [1, 2, 3]:  # Normal, Magic, Rare equipment
                categories['equipment'].append(item)
            elif 'flask' in type_line or 'consumable' in icon:
                categories['consumables'].append(item)
            else:
                categories['other'].append(item)
        
        return categories
    
    def find_valuable_items(self, items, min_value=0.01):
        """
        Identify potentially valuable items based on basic criteria
        
        Args:
            items: List of inventory items
            min_value: Minimum value threshold (not used in basic implementation)
        
        Returns:
            list: Items that might be valuable
        """
        valuable = []
        
        for item in items:
            frame_type = item.get('frameType', 0)
            type_line = item.get('typeLine', '').lower()
            
            # Basic criteria for potentially valuable items
            if (frame_type >= 2 or  # Magic or higher rarity
                'orb' in type_line or 
                'essence' in type_line or
                'fragment' in type_line or
                'catalyst' in type_line or
                'rune' in type_line):
                valuable.append(item)
        
        return valuable
    
    def get_position_map(self, items):
        """
        Create a position map of items in inventory
        
        Args:
            items: List of inventory items
        
        Returns:
            dict: Position mapping
        """
        position_map = {}
        
        for item in items:
            x = item.get('x')
            y = item.get('y')
            if x is not None and y is not None:
                position_map[(x, y)] = item
        
        return position_map
    
    def detect_stash_changes(self, pre_inventory, post_inventory):
        """
        Detect if items were moved to/from stash based on position changes
        
        Args:
            pre_inventory: Items before
            post_inventory: Items after
        
        Returns:
            dict: Information about potential stash operations
        """
        pre_positions = self.get_position_map(pre_inventory)
        post_positions = self.get_position_map(post_inventory)
        
        # Find items that changed position significantly (might indicate stash operations)
        position_changes = []
        
        for item in post_inventory:
            item_key = inv_key(item)
            # Find same item in pre-inventory
            pre_item = None
            for pre in pre_inventory:
                if inv_key(pre) == item_key:
                    pre_item = pre
                    break
            
            if pre_item:
                pre_x, pre_y = pre_item.get('x'), pre_item.get('y')
                post_x, post_y = item.get('x'), item.get('y')
                
                if (pre_x != post_x or pre_y != post_y) and all(v is not None for v in [pre_x, pre_y, post_x, post_y]):
                    position_changes.append({
                        'item': item.get('typeLine', 'Unknown'),
                        'from': (pre_x, pre_y),
                        'to': (post_x, post_y)
                    })
        
        return {
            'position_changes': position_changes,
            'potential_stash_operations': len(position_changes)
        }