"""
PoE Stats Tracker - Refactored Main Script
Tracks inventory changes, session statistics, and loot values for Path of Exile 2
"""

import time
from win11toast import notify
from pathlib import Path

# Import our new modules
from config import Config
from display import DisplayManager
from session_manager import SessionManager
from inventory_analyzer import InventoryAnalyzer
from hotkey_manager import HotkeyManager

# Import existing modules
from price_check_poe2 import fmt
from client_parsing import get_last_map_from_client
from poe_logging import log_run
from poe_api import get_token, get_characters, snapshot_inventory
from inventory_debug import InventoryDebugger


class PoEStatsTracker:
    """Main tracker class - now simplified and modular"""
    
    def __init__(self, config=None):
        # Use provided config or default
        self.config = config or Config()
        
        # Initialize managers
        self.display = DisplayManager(self.config.OUTPUT_MODE)
        self.session_manager = SessionManager(
            self.config.CHAR_TO_CHECK, 
            self.config.get_session_log_file_path()
        )
        self.inventory_analyzer = InventoryAnalyzer()
        self.hotkey_manager = HotkeyManager()
        self.debugger = InventoryDebugger(
            debug_enabled=self.config.DEBUG_ENABLED,
            output_dir=self.config.get_debug_dir()
        )
        
        # State variables
        self.token = None
        self.pre_inventory = None
        self.current_map_info = None
        self.last_api_call = 0.0
        self.map_start_time = None
    
    def initialize(self):
        """Initialize the tracker with API token and character validation"""
        # Validate configuration
        validation = self.config.validate_config()
        if not validation['valid']:
            print("Configuration errors found:")
            for error in validation['errors']:
                print(f"  ❌ {error}")
            raise SystemExit("Please fix configuration errors before running")
        
        if validation['warnings']:
            print("Configuration warnings:")
            for warning in validation['warnings']:
                print(f"  ⚠️  {warning}")
            print()
        
        # Get API token and validate character
        self.token = get_token(self.config.CLIENT_ID, self.config.CLIENT_SECRET)
        chars = get_characters(self.token)
        
        if not chars.get("characters"):
            print("No characters found")
            raise SystemExit
        
        # Start new session
        session_info = self.session_manager.start_new_session()
        
        # Setup hotkeys
        if not self.hotkey_manager.setup_default_hotkeys(self):
            print("Warning: Some hotkeys failed to register")
        
        # Display startup information
        if self.config.NOTIFICATION_ENABLED:
            self._create_startup_notification(session_info)
        
        self.display.display_startup_info(
            self.config.CHAR_TO_CHECK, 
            session_info['session_id'], 
            self.config.OUTPUT_MODE
        )
        
        self.display.display_session_header(
            session_info['session_id'],
            session_info['start_time_str']
        )
    
    def rate_limit(self, min_gap=None):
        """Enforce rate limiting for API calls"""
        min_gap = min_gap or self.config.API_RATE_LIMIT
        now = time.time()
        wait = min_gap - (now - self.last_api_call)
        if wait > 0:
            time.sleep(wait)
        self.last_api_call = time.time()
    
    def take_pre_snapshot(self):
        """Take PRE-map inventory snapshot"""
        self.rate_limit()
        try:
            self.map_start_time = time.time()
            self.pre_inventory = snapshot_inventory(self.token, self.config.CHAR_TO_CHECK)
            
            self.display.display_inventory_count(len(self.pre_inventory), "[PRE]")
            
            # Debug output
            if self.config.DEBUG_SHOW_SUMMARY:
                self.debugger.dump_item_summary(self.pre_inventory, "[PRE-SUMMARY]")
            elif self.config.DEBUG_ENABLED:
                self.debugger.dump_inventory_to_console(self.pre_inventory, "[PRE-DEBUG]")
            
            if self.config.DEBUG_TO_FILE:
                metadata = {
                    "character": self.config.CHAR_TO_CHECK,
                    "snapshot_type": "PRE",
                    "map_info": self.current_map_info
                }
                self.debugger.dump_inventory_to_file(self.pre_inventory, "pre_inventory", metadata)
            
            # Get current map info
            self.current_map_info = get_last_map_from_client(
                self.config.CLIENT_LOG, 
                self.config.CLIENT_LOG_SCAN_BYTES
            )
            
            self.display.display_map_info(self.current_map_info)
            
            if self.config.NOTIFICATION_ENABLED:
                self._create_pre_map_notification(self.current_map_info)
                
        except Exception as e:
            self.display.display_error("PRE", str(e))
    
    def take_post_snapshot(self):
        """Take POST-map inventory snapshot and analyze differences"""
        if self.pre_inventory is None:
            self.display.display_info_message("[POST] no PRE snapshot yet. Press F2 first.")
            return
        
        self.rate_limit()
        try:
            post_inventory = snapshot_inventory(self.token, self.config.CHAR_TO_CHECK)
            
            self.display.display_inventory_count(len(post_inventory), "[POST]")
            
            # Debug output
            if self.config.DEBUG_SHOW_SUMMARY:
                self.debugger.dump_item_summary(post_inventory, "[POST-SUMMARY]")
            elif self.config.DEBUG_ENABLED:
                self.debugger.dump_inventory_to_console(post_inventory, "[POST-DEBUG]")
            
            # Calculate map runtime
            map_runtime = None
            if self.map_start_time is not None:
                map_runtime = time.time() - self.map_start_time
                self.display.display_runtime(map_runtime)
            
            # Analyze inventory changes
            analysis = self.inventory_analyzer.analyze_changes(self.pre_inventory, post_inventory)
            
            if 'error' in analysis:
                self.display.display_error("ANALYSIS", analysis['error'])
                return
            
            # Debug: show inventory comparison (comprehensive mode only)
            if self.config.OUTPUT_MODE == "comprehensive":
                self.debugger.compare_inventories(self.pre_inventory, post_inventory)
            
            # Display changes and price analysis
            self.display.display_inventory_changes(analysis['added'], analysis['removed'])
            map_value = self.display.display_price_analysis(analysis['added'], analysis['removed'])
            
            self.display.display_completion_separator()
            
            # Update session tracking FIRST
            self.session_manager.add_completed_map(map_value)
            
            # Create notification AFTER session update
            if self.config.NOTIFICATION_ENABLED:
                self._create_completion_notification(map_runtime, map_value, self.current_map_info)
            
            # Display session progress
            progress = self.session_manager.get_session_progress()
            if progress:
                self.display.display_session_progress(**progress)
            
            # Log the run
            log_run(
                self.config.CHAR_TO_CHECK, 
                analysis['added'], 
                analysis['removed'], 
                self.current_map_info, 
                map_value, 
                self.config.get_log_file_path(), 
                map_runtime, 
                self.session_manager.session_id
            )
            
        except Exception as e:
            self.display.display_error("POST", str(e))
        finally:
            self.pre_inventory = None
            self.map_start_time = None
    
    def _format_time(self, seconds):
        """Format seconds into a readable time string"""
        if seconds is None:
            return "N/A"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {secs}s"
    
    def _create_pre_map_notification(self, map_info):
        """Create notification for PRE-map snapshot"""
        progress = self.session_manager.get_session_progress()
        
        map_name = map_info["map_name"] if map_info else "Unknown Map"
        session_time = self._format_time(progress['runtime_seconds']) if progress else "N/A"
        session_value = fmt(progress['total_value']) if progress else "0"
        
        # Optimized for 4-line toast limit
        maps_completed = progress['maps_completed'] if progress else 0
        notification_msg = (f"🗺️ {map_name}\n"
                           f"⏰ Session: {session_time} | 🗺️ Maps: {maps_completed}\n"
                           f"💰 Session Value: {session_value}ex\n"
                           f"🚀 Starting new map run!")
        
        notify('Starting Map Run!', notification_msg, icon=f'file://{self.config.get_icon_path()}')
    
    def _create_completion_notification(self, map_runtime, map_value, map_info):
        """Create notification for map completion"""
        progress = self.session_manager.get_session_progress()
        
        map_name = map_info["map_name"] if map_info else "Unknown Map"
        map_time = self._format_time(map_runtime)
        map_val = fmt(map_value) if map_value and map_value > 0.01 else "0"
        session_time = self._format_time(progress['runtime_seconds']) if progress else "N/A"
        session_value = fmt(progress['total_value']) if progress else "0"
        
        # Optimized for 4-line toast limit
        notification_msg = (f"🗺️ {map_name}\n"
                           f"⏱️ Runtime: {map_time} | 💰 Value: {map_val}ex\n"
                           f"⏰ Session: {session_time} | 💰 Total: {session_value}ex\n"
                           f"✅ Map completed!")
        
        # Debug: Print notification content to console for troubleshooting
        if self.config.DEBUG_ENABLED:
            print(f"[DEBUG] POST notification content:")
            print(f"  map_name: '{map_name}'")
            print(f"  map_time: '{map_time}'")
            print(f"  map_val: '{map_val}'")
            print(f"  session_time: '{session_time}'")
            print(f"  session_value: '{session_value}'")
            print(f"  notification_msg: '{notification_msg}'")
        
        notify('Map Completed!', notification_msg, icon=f'file://{self.config.get_icon_path()}')
    
    def _create_inventory_check_notification(self, inventory_items):
        """Create notification for inventory check"""
        try:
            from price_check_poe2 import valuate_items_raw
            rows, (total_c, total_e) = valuate_items_raw(inventory_items)
            
            valuable_items = [r for r in rows if (r['chaos_total'] or 0) > 0.01 or (r['ex_total'] or 0) > 0.01]
            total_items = len([r for r in rows if r['qty'] > 0])
            
            if total_e and total_e > 0.01:
                value_str = f"{fmt(total_e)}ex"
            elif total_c and total_c > 0.01:
                value_str = f"{fmt(total_c)}c"
            else:
                value_str = "No valuable items"
            
            notification_msg = (f"💼 {total_items} items scanned\n"
                               f"💎 {len(valuable_items)} valuable items found\n"
                               f"💰 Total Value: {value_str}\n"
                               f"✅ Inventory check complete!")
            
            notify('Inventory Check', notification_msg, icon=f'file://{self.config.get_icon_path()}')
        except Exception:
            notify('Inventory Check', 'Current inventory scanned!', icon=f'file://{self.config.get_icon_path()}')
    
    def _create_session_start_notification(self, session_info):
        """Create notification for new session start"""
        session_id_short = session_info["session_id"][:8]
        start_time = session_info["start_time_str"]
        
        notification_msg = (f"🚀 Character: {self.config.CHAR_TO_CHECK}\n"
                           f"🆔 ID: {session_id_short}...\n"
                           f"� Started: {start_time}\n"
                           f"✅ New session ready!")
        
        notify('New Session Started!', notification_msg, icon=f'file://{self.config.get_icon_path()}')
    
    def _create_startup_notification(self, session_info):
        """Create notification for application startup - 7 lines test"""
        session_id_short = session_info["session_id"][:8]
        
        notification_msg = (f"🎮 Character: {self.config.CHAR_TO_CHECK}\n"
                           f"🆔 Session: {session_id_short}...\n"
                           f"⌨️ F2=PRE | F3=POST | F5=Inventory\n"
                           f"✅ Ready! Press F2 to start mapping")
        
        notify('DillaPoE2Stat Started!', notification_msg, icon=f'file://{self.config.get_icon_path()}')
    
    def toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        new_state = self.config.toggle_debug()
        self.debugger.set_debug_enabled(new_state)
    
    def toggle_output_mode(self):
        """Toggle between normal and comprehensive output mode"""
        new_mode = "comprehensive" if self.config.OUTPUT_MODE == "normal" else "normal"
        self.config.update_output_mode(new_mode)
        self.display.set_output_mode(new_mode)
        self.display.display_mode_change(new_mode)
    
    def start_new_session(self):
        """Start a new session"""
        session_info = self.session_manager.start_new_session()
        self.display.display_session_header(
            session_info['session_id'],
            session_info['start_time_str']
        )
        
        if self.config.NOTIFICATION_ENABLED:
            self._create_session_start_notification(session_info)
    
    def check_current_inventory_value(self):
        """Check and display the value of the current inventory"""
        self.rate_limit()
        try:
            current_inventory = snapshot_inventory(self.token, self.config.CHAR_TO_CHECK)
            
            self.display.display_inventory_count(len(current_inventory), "[CURRENT]")
            
            # Debug output
            if self.config.DEBUG_SHOW_SUMMARY:
                self.debugger.dump_item_summary(current_inventory, "[CURRENT-SUMMARY]")
            elif self.config.DEBUG_ENABLED:
                self.debugger.dump_inventory_to_console(current_inventory, "[CURRENT-DEBUG]")
            
            # Display current inventory value
            self.display.display_current_inventory_value(current_inventory)
            
            if self.config.NOTIFICATION_ENABLED:
                self._create_inventory_check_notification(current_inventory)
                
        except Exception as e:
            self.display.display_error("INVENTORY CHECK", str(e))
    
    def display_session_stats(self):
        """Display current session statistics"""
        stats = self.session_manager.get_current_session_stats(self.config.get_log_file_path())
        if stats:
            self.display.display_session_stats(
                stats['session_id'],
                stats['runtime']['hours'],
                stats['runtime']['minutes'],
                stats['runtime']['seconds'],
                stats['maps_completed'],
                stats['total_value'],
                stats['detailed_stats']
            )
    
    def run(self):
        """Main application loop"""
        try:
            self.initialize()
            self.hotkey_manager.wait_for_exit_key('ctrl+esc')
        except KeyboardInterrupt:
            pass
        finally:
            # Clean up and show final stats
            self._cleanup()
    
    def _cleanup(self):
        """Clean up resources and display final statistics"""
        # Unregister hotkeys
        self.hotkey_manager.unregister_all()
        
        # End session and show final stats
        if self.session_manager.is_session_active():
            session_end_info = self.session_manager.end_current_session()
            if session_end_info and session_end_info['maps_completed'] > 0:
                self.display.display_session_completion(
                    session_end_info['maps_completed'],
                    session_end_info['total_value']
                )
        
        print("Bye.")


def main():
    """Main entry point"""
    # You can customize the configuration here if needed
    config = Config()
    
    # Print configuration summary
    config.print_config_summary()
    print()
    
    # Create and run tracker
    tracker = PoEStatsTracker(config)
    
    if config.DEBUG_ENABLED:
        print(f"[DEBUG MODE] Enabled - Debug to file: {config.DEBUG_TO_FILE}, "
              f"Show summary: {config.DEBUG_SHOW_SUMMARY}")
    
    tracker.run()


if __name__ == "__main__":
    main()