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
                "id": "sim_post_1",
                "typeLine": "Exalted Orb",
                "baseType": "Exalted Orb", 
                "rarity": "Currency",
                "stackSize": 2,
                "x": 2,
                "y": 1
            },
            {
                "id": "sim_post_2",
                "typeLine": "Chaos Orb",
                "baseType": "Chaos Orb",
                "rarity": "Currency", 
                "stackSize": 5,
                "x": 3,
                "y": 1
            },
            {
                "id": "sim_post_3",
                "typeLine": "Catalyst",
                "baseType": "Adaptive Catalyst",
                "rarity": "Currency",
                "stackSize": 3,
                "x": 4,
                "y": 1
            }
        ]
    
    def get_latest_debug_files(self) -> Tuple[Optional[str], Optional[str]]:
        """Find the latest debug files"""
        try:
            pre_pattern = os.path.join(self.debug_dir, "pre_inventory_*.json")
            post_pattern = os.path.join(self.debug_dir, "post_inventory_*.json")
            
            pre_files = glob.glob(pre_pattern)
            post_files = glob.glob(post_pattern)
            
            if pre_files and post_files:
                latest_pre = max(pre_files, key=os.path.getctime)
                latest_post = max(post_files, key=os.path.getctime)
                return latest_pre, latest_post
        except Exception as e:
            print(f"[DEBUG] Failed to find debug files: {e}")
        
        return None, None
    
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
            'name': 'Simulated Waystone (Tier 8)',
            'tier': 8,
            'prefixes': ['Area contains additional Monster Packs'],
            'suffixes': ['25% increased Monster Damage'],
            'area_modifiers': {
                'monster_packs': True,
                'monster_damage': 25
            }
        }
    
    def list_available_debug_files(self) -> Dict[str, List[str]]:
        """List all available debug files"""
        pre_files = glob.glob(os.path.join(self.debug_dir, "pre_inventory_*.json"))
        post_files = glob.glob(os.path.join(self.debug_dir, "post_inventory_*.json"))
        
        return {
            'pre_files': [os.path.basename(f) for f in sorted(pre_files, key=os.path.getctime, reverse=True)],
            'post_files': [os.path.basename(f) for f in sorted(post_files, key=os.path.getctime, reverse=True)]
        }