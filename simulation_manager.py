"""
Simulation Manager for PoE Stats Tracker
Provides simulation capabilities for testing without actual gameplay
"""

import json
import os
import glob
import time
from typing import Dict, List, Optional, Tuple


class SimulationManager:
    """Manages simulation data and functionality for testing"""
    
    def __init__(self, debug_dir: str = "debug"):
        self.debug_dir = debug_dir
        self.simulation_dir = "simulation_data"
        
        # Hardcoded test data as fallback
        self.fallback_pre_inventory = [
            {
                "id": "sim_pre_1",
                "typeLine": "Armourer's Scrap",
                "baseType": "Armourer's Scrap",
                "rarity": "Currency",
                "stackSize": 15,
                "x": 1,
                "y": 1
            },
            {
                "id": "sim_pre_2", 
                "typeLine": "Waystone",
                "baseType": "Waystone (Tier 8)",
                "rarity": "Normal",
                "stackSize": 1,
                "x": 0,
                "y": 0,
                "explicitMods": [
                    "Area contains additional Monster Packs",
                    "25% increased Monster Damage"
                ]
            }
        ]
        
        self.fallback_post_inventory = [
            # Keep original PRE items
            {
                "id": "sim_pre_1",
                "typeLine": "Armourer's Scrap", 
                "baseType": "Armourer's Scrap",
                "rarity": "Currency",
                "stackSize": 15,
                "x": 1,
                "y": 1
            },
            # Real loot from Necropolis run - 25 added items
            {
                "id": "sim_post_1",
                "typeLine": "Preserved Cranium",
                "baseType": "Preserved Cranium",
                "rarity": "Currency",
                "stackSize": 1,
                "x": 2,
                "y": 1
            },
            {
                "id": "sim_post_2", 
                "typeLine": "Preserved Vertebrae",
                "baseType": "Preserved Vertebrae",
                "rarity": "Currency",
                "stackSize": 1,
                "x": 3,
                "y": 1
            },
            {
                "id": "sim_post_3",
                "typeLine": "Greater Regal Orb",
                "baseType": "Greater Regal Orb",
                "rarity": "Currency",
                "stackSize": 1,
                "x": 4,
                "y": 1
            },
            {
                "id": "sim_post_4",
                "typeLine": "Sione's Temper",
                "baseType": "Sione's Temper",
                "rarity": "Unique",
                "stackSize": 1,
                "x": 5,
                "y": 1
            },
            {
                "id": "sim_post_5",
                "typeLine": "Chayula's Catalyst",
                "baseType": "Chayula's Catalyst",
                "rarity": "Currency",
                "stackSize": 1,
                "x": 6,
                "y": 1
            },
            {
                "id": "sim_post_6",
                "typeLine": "Reaver Catalyst",
                "baseType": "Reaver Catalyst",
                "rarity": "Currency", 
                "stackSize": 1,
                "x": 7,
                "y": 1
            },
            {
                "id": "sim_post_7",
                "typeLine": "Diluted Liquid Guilt",
                "baseType": "Diluted Liquid Guilt",
                "rarity": "Currency",
                "stackSize": 2,
                "x": 8,
                "y": 1
            },
            {
                "id": "sim_post_8",
                "typeLine": "Gold Amulet",
                "baseType": "Gold Amulet",
                "rarity": "Normal",
                "stackSize": 1,
                "x": 9,
                "y": 1
            },
            {
                "id": "sim_post_9",
                "typeLine": "Utility Belt",
                "baseType": "Utility Belt",
                "rarity": "Normal",
                "stackSize": 1,
                "x": 0,
                "y": 2
            },
            {
                "id": "sim_post_10",
                "typeLine": "Gemcutter's Prism",
                "baseType": "Gemcutter's Prism",
                "rarity": "Currency",
                "stackSize": 1,
                "x": 1,
                "y": 2
            },
            {
                "id": "sim_post_11",
                "typeLine": "Regal Orb",
                "baseType": "Regal Orb",
                "rarity": "Currency",
                "stackSize": 5,
                "x": 2,
                "y": 2
            },
            {
                "id": "sim_post_12",
                "typeLine": "Chance Shard",
                "baseType": "Chance Shard",
                "rarity": "Currency",
                "stackSize": 1,
                "x": 3,
                "y": 2
            },
            {
                "id": "sim_post_13",
                "typeLine": "Uncut Support Gem (Level 5)",
                "baseType": "Uncut Support Gem",
                "rarity": "Gem",
                "stackSize": 2,
                "x": 4,
                "y": 2
            },
            {
                "id": "sim_post_14",
                "typeLine": "Greater Desert Rune",
                "baseType": "Greater Desert Rune",
                "rarity": "Currency",
                "stackSize": 1,
                "x": 5,
                "y": 2
            },
            {
                "id": "sim_post_15",
                "typeLine": "Waystone (Tier 15)",
                "baseType": "Waystone",
                "rarity": "Normal",
                "stackSize": 2,
                "x": 6,
                "y": 2
            },
            {
                "id": "sim_post_16",
                "typeLine": "Exalted Orb",
                "baseType": "Exalted Orb",
                "rarity": "Currency",
                "stackSize": 6,
                "x": 7,
                "y": 2
            },
            {
                "id": "sim_post_17",
                "typeLine": "Simulacrum Splinter",
                "baseType": "Simulacrum Splinter",
                "rarity": "Currency",
                "stackSize": 6,
                "x": 8,
                "y": 2
            },
            {
                "id": "sim_post_18",
                "typeLine": "Greater Jeweller's Orb",
                "baseType": "Greater Jeweller's Orb",
                "rarity": "Currency",
                "stackSize": 1,
                "x": 9,
                "y": 2
            },
            {
                "id": "sim_post_19",
                "typeLine": "Breach Splinter",
                "baseType": "Breach Splinter",
                "rarity": "Currency",
                "stackSize": 13,
                "x": 0,
                "y": 3
            },
            {
                "id": "sim_post_20",
                "typeLine": "Perfect Orb of Augmentation",
                "baseType": "Perfect Orb of Augmentation",
                "rarity": "Currency",
                "stackSize": 1,
                "x": 1,
                "y": 3
            },
            {
                "id": "sim_post_21",
                "typeLine": "Chaos Orb",
                "baseType": "Chaos Orb",
                "rarity": "Currency",
                "stackSize": 1,
                "x": 2,
                "y": 3
            },
            {
                "id": "sim_post_22",
                "typeLine": "Diluted Liquid Greed",
                "baseType": "Diluted Liquid Greed",
                "rarity": "Currency",
                "stackSize": 1,
                "x": 3,
                "y": 3
            }
        ]
    
    def load_json_file(self, filepath: str) -> Optional[List[Dict]]:
        """Load inventory data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle different JSON structures
                if isinstance(data, dict):
                    return data.get('inventory', [])
                elif isinstance(data, list):
                    return data
                else:
                    return []
        except Exception as e:
            print(f"[DEBUG] Failed to load {filepath}: {e}")
            return None
    
    def get_simulation_data(self) -> Tuple[List[Dict], List[Dict]]:
        """Get simulation data, preferring simulation files over fallback"""
        # Try fixed simulation files first
        pre_file = os.path.join(self.simulation_dir, "pre_inventory.json")
        post_file = os.path.join(self.simulation_dir, "post_inventory.json")
        
        pre_inventory = None
        post_inventory = None
        
        # Try to load from simulation files
        if os.path.exists(pre_file):
            pre_inventory = self.load_json_file(pre_file)
            if pre_inventory:
                print(f"📂 Loaded PRE from simulation_data/pre_inventory.json")
        
        if os.path.exists(post_file):
            post_inventory = self.load_json_file(post_file)
            if post_inventory:
                print(f"📂 Loaded POST from simulation_data/post_inventory.json")
        
        # Fallback to hardcoded data
        if not pre_inventory:
            pre_inventory = self.fallback_pre_inventory
            print("📦 Using hardcoded PRE data (no simulation files)")
            
        if not post_inventory:
            post_inventory = self.fallback_post_inventory
            print("📦 Using hardcoded POST data (no simulation files)")
        
        return pre_inventory, post_inventory
    
    def create_simulated_map_info(self) -> Dict:
        """Create simulated map information"""
        return {
            'map_name': 'Simulated Hideout Felled',
            'level': 65,
            'seed': 'sim_12345',
            'source': 'simulation'
        }
    
    def create_simulated_waystone_info(self) -> Dict:
        """Create simulated waystone information"""
        return {
            'name': 'Simulated Waystone (Tier 15)',
            'tier': 15,
            'prefixes': ['Magic Monsters', 'Item Rarity'],
            'suffixes': ['Rare Monsters', 'Waystone Drop Chance'],
            'area_modifiers': {
                'magic_monsters': {
                    'name': 'Magic Monsters',
                    'value': '+58%',
                    'display': 'Magic Monsters: +58%'
                },
                'rare_monsters': {
                    'name': 'Rare Monsters',
                    'value': '+45%',
                    'display': 'Rare Monsters: +45%'
                },
                'item_rarity': {
                    'name': 'Item Rarity',
                    'value': '+89%',
                    'display': 'Item Rarity: +89%'
                },
                'waystone_drop_chance': {
                    'name': 'Waystone Drop Chance',
                    'value': '+105%',
                    'display': 'Waystone Drop Chance: +105%'
                }
            }
        }
    
