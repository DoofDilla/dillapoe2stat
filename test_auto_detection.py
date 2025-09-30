"""
Test script for Auto Map Detection System
Tests the detection without affecting the main tracker
"""

import time
from auto_map_detector import AutoMapDetector
from config import Config

def test_detection():
    """Test the auto detection system"""
    
    def on_map_enter(map_info):
        print(f"🔥 WOULD TRIGGER F2: Entering {map_info['area_name']}")
        print(f"   📍 Level: {map_info['level']}, Code: {map_info['area_code']}")
        print(f"   🕐 Time: {map_info['timestamp']}")
        print(f"   🌱 Seed: {map_info['seed']}")
    
    def on_map_exit(map_info):
        print(f"💰 WOULD TRIGGER F3: Finished {map_info['area_name']}")
        print(f"   📊 Ready to process loot and log run")
    
    config = Config()
    detector = AutoMapDetector(
        config.CLIENT_LOG,
        config,
        on_map_enter=on_map_enter,
        on_map_exit=on_map_exit
    )
    
    try:
        print("🎯 Auto Map Detection Test")
        print("=" * 50)
        print(f"📁 Monitoring: {config.CLIENT_LOG}")
        print(f"🏠 Hideouts: {list(config.AUTO_HIDEOUT_AREAS)[:5]}...")
        print(f"🏛️ Towns: {list(config.AUTO_TOWN_AREAS)[:5]}...")
        print()
        print("🎮 Test Scenarios:")
        print("   1. Hideout → Map = Should trigger F2")
        print("   2. Map → Abyss = Should NOT trigger F3")
        print("   3. Abyss → Map = Should NOT trigger F2")
        print("   4. Map → Hideout = Should trigger F3")
        print()
        print("🚀 Starting detection... (Ctrl+C to stop)")
        
        detector.start()
        
        while True:
            time.sleep(2)
            status = detector.get_status()
            if status['current_area']:
                area_status = "🗺️ IN MAP" if status['is_in_map'] else "🏠 SAFE ZONE"
                print(f"🔍 Current: {status['current_area']} ({area_status})")
                
    except KeyboardInterrupt:
        print("\n👋 Test stopped")
    finally:
        detector.stop()
        print("✅ Test completed")

if __name__ == "__main__":
    test_detection()