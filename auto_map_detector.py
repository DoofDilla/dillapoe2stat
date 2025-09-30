"""
Automatic Map Detection System for PoE Stats Tracker
Monitors client.txt for map entry/exit patterns and triggers automatic snapshots
Handles complex flows like Map -> Abyss -> Map correctly
"""

import re
import os
import time
import threading
from collections import deque
from pathlib import Path
from typing import Optional, Dict, Set, Callable

# Import existing modules
from client_parsing import GEN_RE, code_to_title
from config import Config


class AutoMapDetector:
    """Automatic detection of map entry/exit for seamless tracking"""
    
    def __init__(self, client_log_path: str, config: Config, on_map_enter: Callable = None, on_map_exit: Callable = None, on_waystone_trigger: Callable = None):
        """
        Initialize the auto detector
        
        Args:
            client_log_path: Path to Client.txt
            config: Config object with hideout/town definitions
            on_map_enter: Callback when entering a map (receives map_info dict)
            on_map_exit: Callback when exiting a map (receives previous map_info dict)
            on_waystone_trigger: Callback when entering waystone trigger area (receives area_info dict)
        """
        self.client_log_path = Path(client_log_path)
        self.config = config
        self.on_map_enter = on_map_enter
        self.on_map_exit = on_map_exit
        self.on_waystone_trigger = on_waystone_trigger
        
        # State tracking
        self.current_area = None
        self.current_map_info = None
        self.is_in_map = False
        self.last_file_position = 0
        self.running = False
        self.monitor_thread = None
        
        # History for better decision making
        self.area_history = deque(maxlen=15)  # Increased for complex flows
        
        # Performance settings
        self.check_interval = 1.0  # Check every second
        self.scan_bytes = 50000    # Scan last 50KB for changes
    
    def is_hideout_or_town(self, area_code: str) -> bool:
        """Check if area code represents a hideout or town"""
        # Use config-defined lists
        return (area_code in self.config.AUTO_HIDEOUT_AREAS or 
                area_code in self.config.AUTO_TOWN_AREAS or
                area_code.lower().startswith('hideout') or
                area_code.lower().startswith('town'))
    
    def is_waystone_trigger_area(self, area_code: str) -> bool:
        """Check if area code should trigger waystone analysis"""
        return area_code in getattr(self.config, 'AUTO_WAYSTONE_TRIGGER_AREAS', set())
    
    def is_abyss_area(self, area_code: str) -> bool:
        """Check if area code represents an abyss (sub-area within maps)"""
        return (area_code.startswith('Abyss_') or 
                'Abyss' in area_code or
                area_code.startswith('Breach_') or  # Breach areas are similar
                'Breach' in area_code)
    
    def is_map_area(self, area_code: str) -> bool:
        """Check if area code represents an actual map"""
        # Maps typically start with "Map" prefix or are not hideouts/towns/abyss
        return (area_code.startswith('Map') or 
                (not self.is_hideout_or_town(area_code) and 
                 not self.is_abyss_area(area_code) and
                 not area_code.startswith('Tutorial') and
                 not area_code.startswith('Cinematic')))
    
    def get_area_context(self) -> str:
        """Get context of recent area transitions for better decision making"""
        if len(self.area_history) < 2:
            return "insufficient_history"
        
        recent = [area['area_code'] for area in list(self.area_history)[-5:]]
        return " -> ".join(recent)
    
    def parse_new_area_entries(self) -> list:
        """Parse new area generation entries from client log"""
        if not self.client_log_path.exists():
            return []
            
        try:
            file_size = self.client_log_path.stat().st_size
            
            # If file got smaller (rotated), reset position
            if file_size < self.last_file_position:
                self.last_file_position = 0
            
            # Read from last position
            with open(self.client_log_path, 'rb') as f:
                f.seek(self.last_file_position)
                new_data = f.read()
                self.last_file_position = f.tell()
            
            if not new_data:
                return []
                
            # Decode and find area generation lines
            text = new_data.decode('utf-8', errors='ignore')
            new_areas = []
            
            for line in text.splitlines():
                match = GEN_RE.search(line)
                if match:
                    area_info = {
                        'timestamp': match.group('ts'),
                        'level': int(match.group('lvl')),
                        'area_code': match.group('code'),
                        'area_name': code_to_title(match.group('code')),
                        'seed': int(match.group('seed')),
                        'raw_line': line
                    }
                    new_areas.append(area_info)
            
            return new_areas
            
        except Exception as e:
            print(f"⚠️  Error parsing client log: {e}")
            return []
    
    def process_area_change(self, area_info: dict):
        """Process a detected area change with smart flow detection"""
        area_code = area_info['area_code']
        area_name = area_info['area_name']
        
        # Add to history
        self.area_history.append(area_info)
        
        print(f"🗺️  Area detected: {area_name} ({area_code})")
        
        # Determine area types
        is_new_map = self.is_map_area(area_code)
        is_safe_zone = self.is_hideout_or_town(area_code)
        is_abyss = self.is_abyss_area(area_code)
        
        # Get context for better decisions
        context = self.get_area_context()
        
        # Handle map entry (hideout/town -> map)
        if is_new_map and not self.is_in_map:
            print(f"🚀 MAP ENTRY DETECTED: {area_name}")
            print(f"   Context: {context}")
            self.is_in_map = True
            self.current_area = area_code
            self.current_map_info = area_info
            
            if self.on_map_enter:
                try:
                    self.on_map_enter(area_info)
                except Exception as e:
                    print(f"⚠️  Error in map enter callback: {e}")
        
        # Handle abyss entry (map -> abyss) - NO ACTION, still in map!
        elif is_abyss and self.is_in_map:
            print(f"🕳️  ABYSS ENTRY: {area_name} (staying in map mode)")
            self.current_area = area_code
            # DO NOT change is_in_map state!
        
        # Handle return from abyss (abyss -> map) - NO ACTION
        elif is_new_map and self.is_in_map and len(self.area_history) >= 2:
            prev_area = self.area_history[-2]['area_code']
            if self.is_abyss_area(prev_area):
                print(f"🔄 RETURN FROM ABYSS: Back to {area_name}")
                self.current_area = area_code
                # DO NOT trigger map enter again!
            else:
                # This is a different map - treat as new map entry
                print(f"🗺️  NEW MAP: {area_name} (different from previous)")
                self.current_map_info = area_info
                self.current_area = area_code
        
        # Handle map exit (map/abyss -> hideout/town)
        elif is_safe_zone and self.is_in_map:
            print(f"🏠 MAP EXIT DETECTED: Returned to {area_name}")
            print(f"   Context: {context}")
            previous_map = self.current_map_info
            self.is_in_map = False
            self.current_area = area_code
            
            if self.on_map_exit and previous_map:
                try:
                    self.on_map_exit(previous_map)
                except Exception as e:
                    print(f"⚠️  Error in map exit callback: {e}")
            
            self.current_map_info = None
        
        # Handle waystone trigger areas (e.g., Well of Souls -> Hideout)
        elif is_safe_zone and not self.is_in_map and len(self.area_history) >= 2:
            prev_area = self.area_history[-2]['area_code']
            if self.is_waystone_trigger_area(prev_area) and area_code in self.config.AUTO_HIDEOUT_AREAS:
                print(f"⚡ WAYSTONE TRIGGER: {self.area_history[-2]['area_name']} → {area_name}")
                if self.on_waystone_trigger:
                    try:
                        self.on_waystone_trigger(area_info)
                    except Exception as e:
                        print(f"⚠️  Error in waystone trigger callback: {e}")
        
        # Update current area for other transitions
        else:
            self.current_area = area_code
            if is_safe_zone and not self.is_in_map:
                print(f"🏠 Safe zone: {area_name}")
            elif is_abyss:
                print(f"🕳️  Sub-area: {area_name}")
    
    def monitor_loop(self):
        """Main monitoring loop running in background thread"""
        print("🔍 Auto map detector started")
        
        while self.running:
            try:
                new_areas = self.parse_new_area_entries()
                
                # Process each new area change
                for area_info in new_areas:
                    self.process_area_change(area_info)
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"⚠️  Error in monitor loop: {e}")
                time.sleep(self.check_interval * 2)  # Wait longer on error
    
    def start(self):
        """Start the automatic monitoring"""
        if self.running:
            print("⚠️  Auto detector already running")
            return
            
        print("🎯 Starting automatic map detection...")
        print(f"   📁 Monitoring: {self.client_log_path}")
        print(f"   🏠 Hideouts: {', '.join(list(self.config.AUTO_HIDEOUT_AREAS)[:3])}...")
        print(f"   🏛️  Towns: {', '.join(list(self.config.AUTO_TOWN_AREAS)[:3])}...")
        
        # Initialize file position to end of file
        if self.client_log_path.exists():
            self.last_file_position = self.client_log_path.stat().st_size
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("✅ Auto detector running in background")
    
    def stop(self):
        """Stop the automatic monitoring"""
        if not self.running:
            return
            
        print("🛑 Stopping auto map detector...")
        self.running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        
        print("✅ Auto detector stopped")
    
    def get_status(self) -> dict:
        """Get current detector status"""
        return {
            'running': self.running,
            'current_area': self.current_area,
            'is_in_map': self.is_in_map,
            'current_map_info': self.current_map_info,
            'recent_areas': list(self.area_history)[-5:] if self.area_history else []
        }


def test_auto_detector():
    """Test the auto detector with sample callbacks"""
    
    def on_map_enter(map_info):
        print(f"🔥 AUTO F2 TRIGGERED: Entering {map_info['area_name']}")
        print(f"   Level: {map_info['level']}, Seed: {map_info['seed']}")
    
    def on_map_exit(map_info):
        print(f"💰 AUTO F3 TRIGGERED: Finished {map_info['area_name']}")
    
    def on_waystone_trigger(area_info):
        print(f"⚡ AUTO CTRL+F2 TRIGGERED: Waystone analysis at {area_info['area_name']}")
    
    # Create detector
    config = Config()  # Use default config
    detector = AutoMapDetector(
        config.CLIENT_LOG,
        config,
        on_map_enter=on_map_enter,
        on_map_exit=on_map_exit,
        on_waystone_trigger=on_waystone_trigger
    )
    
    try:
        detector.start()
        
        print("\n🎮 Test running... Go enter/exit some maps!")
        print("   Try: Hideout -> Map -> Abyss -> Map -> Hideout")
        print("Press Ctrl+C to stop")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    finally:
        detector.stop()


if __name__ == "__main__":
    test_auto_detector()