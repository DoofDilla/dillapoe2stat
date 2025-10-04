"""
Waystone Analysis Module for PoE Stats Tracker
Handles waystone parsing and experimental functionality
"""

from poe_api import snapshot_inventory


class WaystoneAnalyzer:
    """Handles waystone analysis and experimental snapshot functionality"""
    
    def __init__(self, config, display_manager, debugger):
        self.config = config
        self.display = display_manager
        self.debugger = debugger
    
    def find_waystone_in_inventory(self, inventory):
        """Find waystone in top-left inventory position (0,0)"""
        for item in inventory:
            if (item.get('x') == 0 and item.get('y') == 0 and 
                'Waystone' in item.get('typeLine', '')):
                return item
        return None
    
    def parse_waystone_info(self, waystone_item):
        """Extract name, prefixes, suffixes and area modifiers from waystone item"""
        if not waystone_item:
            return None
        
        # Extract basic info
        name = waystone_item.get('name', 'Unknown Waystone')
        type_line = waystone_item.get('typeLine', '')
        
        # Extract tier from typeLine (e.g., "Waystone (Tier 15)")
        tier = "Unknown"
        if 'Tier' in type_line:
            import re
            tier_match = re.search(r'Tier (\d+)', type_line)
            if tier_match:
                tier = tier_match.group(1)
        
        # Extract prefixes from explicit mods
        prefixes = []
        explicit_mods = waystone_item.get('explicitMods', [])
        for mod in explicit_mods:
            clean_mod = mod.strip()
            if clean_mod:
                prefixes.append(clean_mod)
        
        # Extract suffixes from implicit mods and enchant mods
        suffixes = []
        implicit_mods = waystone_item.get('implicitMods', [])
        for mod in implicit_mods:
            clean_mod = mod.strip()
            if clean_mod:
                suffixes.append(clean_mod)
        
        # Also check enchant mods for suffixes
        enchant_mods = waystone_item.get('enchantMods', [])
        for mod in enchant_mods:
            clean_mod = mod.strip()
            if clean_mod:
                suffixes.append(clean_mod)
        
        # Extract delirious percentage from suffixes (check all suffixes, not just first)
        delirious_percent = 0
        if suffixes:
            import re
            # Check all suffixes for delirious (not just first one)
            for suffix in suffixes:
                # Match patterns like "10% Delirious", "Delirious 10%", "12% [Delirious]", etc.
                # Pattern breakdown:
                # - (\d+)%?\s* matches "12% " or "12 "
                # - (?:\[)?[Dd]elirious(?:\])? matches "Delirious", "[Delirious]", "delirious", etc.
                match = re.search(r'(\d+)%?\s*(?:\[)?[Dd]elirious(?:\])?|(?:\[)?[Dd]elirious(?:\])?\s*(\d+)%?', suffix)
                if match:
                    delirious_percent = int(match.group(1) or match.group(2))
                    break  # Found it, stop searching
        
        # Extract area modifiers from properties (Magic Monsters, Item Rarity, etc.)
        area_modifiers = {}
        properties = waystone_item.get('properties', [])
        
        # Look for specific area modifier properties
        modifier_names = {
            'Magic Monsters': 'magic_monsters',
            'Rare Monsters': 'rare_monsters', 
            'Item Rarity': 'item_rarity',
            'Item Quantity': 'item_quantity',
            'Waystone Drop Chance': 'waystone_drop_chance',
            'Pack Size': 'pack_size',
            'Monster Pack Size': 'pack_size'  # Alternative name for pack size
        }
        
        for prop in properties:
            prop_name = prop.get('name', '')
            prop_values = prop.get('values', [])
            
            # Check if this property is one of our area modifiers
            if prop_name in modifier_names and prop_values:
                # Extract the value (usually the first value in the list)
                if len(prop_values) > 0:
                    value = prop_values[0]
                    if isinstance(value, list) and len(value) > 0:
                        area_modifiers[modifier_names[prop_name]] = {
                            'name': prop_name,
                            'value': value[0],  # The actual value string like "+70%"
                            'display': f"{prop_name}: {value[0]}"
                        }
        
        return {
            'name': name,
            'tier': tier,
            'prefixes': prefixes,
            'suffixes': suffixes,
            'delirious': delirious_percent,
            'area_modifiers': area_modifiers,
            'type_line': type_line,
            'full_item': waystone_item
        }
    
    def take_experimental_pre_snapshot(self, token, character_name, session_manager, map_start_time_callback):
        """Take experimental PRE-map snapshot using waystone from inventory"""
        try:
            # Set map start time
            map_start_time_callback()
            
            # Take inventory snapshot
            pre_inventory = snapshot_inventory(token, character_name)
            
            self.display.display_inventory_count(len(pre_inventory), "[EXPERIMENTAL PRE]")
            
            # Find and parse waystone
            waystone = self.find_waystone_in_inventory(pre_inventory)
            waystone_info = self.parse_waystone_info(waystone)
            
            if waystone_info:
                # Create map info structure
                current_map_info = {
                    'map_name': waystone_info['name'],
                    'level': waystone_info['tier'],
                    'prefixes': waystone_info['prefixes'],
                    'suffixes': waystone_info['suffixes'],
                    'area_modifiers': waystone_info['area_modifiers'],
                    'source': 'waystone_inventory',
                    'seed': 'experimental'  # We don't have seed from waystone
                }
                
                # Display waystone info with prefixes
                self.display.display_experimental_waystone_info(waystone_info)
                
                # Debug output
                if self.config.DEBUG_ENABLED:
                    print(f"[DEBUG] Waystone found: {waystone_info}")
                
            else:
                print("⚠️  No waystone found in top-left inventory position (0,0)")
                current_map_info = {
                    'map_name': 'No Waystone Found',
                    'level': 'Unknown',
                    'prefixes': [],
                    'suffixes': [],
                    'area_modifiers': {},
                    'source': 'waystone_inventory',
                    'seed': 'experimental'
                }
            
            # Standard debug output
            if self.config.DEBUG_SHOW_SUMMARY:
                self.debugger.dump_item_summary(pre_inventory, "[EXP-PRE-SUMMARY]")
            elif self.config.DEBUG_ENABLED:
                self.debugger.dump_inventory_to_console(pre_inventory, "[EXP-PRE-DEBUG]")
            
            if self.config.DEBUG_TO_FILE:
                metadata = {
                    "character": character_name,
                    "snapshot_type": "EXPERIMENTAL_PRE",
                    "waystone_info": waystone_info,
                    "map_info": current_map_info
                }
                self.debugger.dump_inventory_to_file(pre_inventory, "exp_pre_inventory", metadata)
            
            return {
                'inventory': pre_inventory,
                'map_info': current_map_info,
                'waystone_info': waystone_info
            }
                
        except Exception as e:
            self.display.display_error("EXPERIMENTAL PRE", str(e))
            return None