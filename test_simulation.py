#!/usr/bin/env python3
"""
Test script for the simulation system
"""

from poe_stats_refactored_v2 import PoEStatsTracker
from config import Config

def main():
    print("🧪 Testing Simulation System...")
    
    # Create config with debug enabled
    config = Config()
    config.DEBUG_ENABLED = True
    
    # Create tracker
    tracker = PoEStatsTracker(config)
    
    # Test simulation manager
    if tracker.simulation_manager:
        print("✅ Simulation manager loaded")
        
        # Test getting simulation data
        pre_data, post_data = tracker.simulation_manager.get_simulation_data()
        print(f"📦 PRE data: {len(pre_data)} items")
        print(f"📦 POST data: {len(post_data)} items")
        
        # Test creating simulated info
        map_info = tracker.simulation_manager.create_simulated_map_info()
        print(f"🗺️ Map info: {map_info['map_name']} (T{map_info['level']})")
        
        waystone_info = tracker.simulation_manager.create_simulated_waystone_info()
        print(f"💎 Waystone: {waystone_info['name']} (T{waystone_info['tier']})")
        
        # Test simulation methods
        print("\n🔧 Testing simulate_pre_snapshot...")
        tracker.simulate_pre_snapshot()
        
        print("\n🔧 Testing simulate_post_snapshot...")
        tracker.simulate_post_snapshot()
        
    else:
        print("❌ Simulation manager not available")

if __name__ == "__main__":
    main()