"""
PoE Stats Tracker - Simplified Main Script
Tracks inventory changes, session statistics, and loot values for Path of Exile 2
Now refactored into modular components for better maintainability
"""

import time

# Import our new modular components
from config import Config
from display import DisplayManager
from session_manager import SessionManager
from inventory_analyzer import InventoryAnalyzer
from hotkey_manager import HotkeyManager
from inventory_debug import InventoryDebugger
from waystone_analyzer import WaystoneAnalyzer
from notification_manager import NotificationManager
from utils import format_time, get_current_timestamp

# Import existing modules
from client_parsing import get_last_map_from_client
from poe_logging import log_run
from poe_api import get_token, get_characters, snapshot_inventory
from gear_rarity_analyzer import GearRarityAnalyzer

# Import OBS integration (optional)
try:
    from obs_web_server import OBSWebServer
    OBS_AVAILABLE = True
except ImportError:
    OBS_AVAILABLE = False
    print("⚠️  OBS integration not available (Flask not installed)")


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
        self.waystone_analyzer = WaystoneAnalyzer(self.config, self.display, self.debugger)
        self.notification_manager = NotificationManager(self.config)
        
        # OBS Integration (optional)
        self.obs_server = None
        if OBS_AVAILABLE and self.config.OBS_ENABLED:
            try:
                self.obs_server = OBSWebServer(
                    host=self.config.OBS_HOST, 
                    port=self.config.OBS_PORT,
                    quiet_mode=self.config.OBS_QUIET_MODE
                )
                print("🎬 OBS integration enabled")
            except Exception as e:
                print(f"⚠️  OBS server initialization failed: {e}")
                self.obs_server = None
        
        # State variables
        self.token = None
        self.pre_inventory = None
        self.current_map_info = None
        self.last_api_call = 0.0
        self.map_start_time = None
        self.cached_waystone_info = None  # Cache for waystone info from Ctrl+F2
        
        # Gear Rarity variables
        self.gear_rarity_analyzer = None  # Initialized after token is available
        self.current_gear_rarity = None   # Cached gear rarity value
    
    def initialize(self):
        """Initialize the tracker with API token and character validation"""
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
        
        # Initialize gear rarity analyzer with token
        self.gear_rarity_analyzer = GearRarityAnalyzer(self.token)
        self._update_gear_rarity()
        
        # Start new session
        session_info = self.session_manager.start_new_session()
        
        # Setup hotkeys
        if not self.hotkey_manager.setup_default_hotkeys(self):
            print("Warning: Some hotkeys failed to register")
        
        # Start OBS server if enabled and auto-start is on
        if self.obs_server and self.config.OBS_AUTO_START:
            try:
                self.obs_server.start_background()
                print(f"🌐 OBS Web Server: http://{self.config.OBS_HOST}:{self.config.OBS_PORT}")
            except Exception as e:
                print(f"⚠️  Failed to start OBS server: {e}")
                self.obs_server = None
        
        # Display startup information and send notification
        self.notification_manager.notify_startup(session_info)
        
        self.display.display_startup_info(
            self.config.CHAR_TO_CHECK, 
            session_info['session_id'], 
            self.config.OUTPUT_MODE
        )
        
        # Display gear rarity info separately
        self._display_gear_rarity_info()
        
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
    
    def _update_gear_rarity(self):
        """Update the cached gear rarity value"""
        try:
            if self.gear_rarity_analyzer:
                result = self.gear_rarity_analyzer.calculate_total_gear_rarity(self.config.CHAR_TO_CHECK)
                if result.get('success', False):
                    self.current_gear_rarity = result['total_rarity_bonus']
                else:
                    self.current_gear_rarity = None
                    if self.config.DEBUG_ENABLED:
                        print(f"[DEBUG] Gear rarity update failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.current_gear_rarity = None
            if self.config.DEBUG_ENABLED:
                print(f"[DEBUG] Gear rarity update exception: {e}")
    
    def get_gear_rarity(self):
        """Get current gear rarity with refresh if needed"""
        if self.current_gear_rarity is None:
            self._update_gear_rarity()
        return self.current_gear_rarity
    
    def _display_gear_rarity_info(self):
        """Display gear rarity information"""
        if self.current_gear_rarity is not None:
            from display import Colors
            rarity_color = Colors.GOLD if self.current_gear_rarity > 0 else Colors.GRAY
            print(f"✨ Gear Rarity: {rarity_color}{self.current_gear_rarity}%{Colors.END}")
        elif self.config.DEBUG_ENABLED:
            print("[DEBUG] Gear rarity not available")
    
    def take_pre_snapshot(self):
        """Take PRE-map inventory snapshot"""
        self.rate_limit()
        try:
            self.map_start_time = get_current_timestamp()
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
            
            # Get current map info from client.txt
            client_map_info = get_last_map_from_client(
                self.config.CLIENT_LOG, 
                self.config.CLIENT_LOG_SCAN_BYTES
            )
            
            # Combine client.txt info with cached waystone info if available
            if self.cached_waystone_info and client_map_info:
                # Use map name from client.txt but add waystone attributes
                self.current_map_info = {
                    'map_name': client_map_info['map_name'],
                    'level': client_map_info['level'],
                    'seed': client_map_info['seed'],
                    'source': 'client_log_with_waystone',
                    # Add waystone attributes for logging (but not prefixes/suffixes)
                    'waystone_tier': self.cached_waystone_info['tier'],
                    'area_modifiers': self.cached_waystone_info['area_modifiers'],
                    'modifier_count': len(self.cached_waystone_info['prefixes']) + len(self.cached_waystone_info['suffixes'])
                }
                print(f"📊 Enhanced with waystone data: T{self.cached_waystone_info['tier']}, {self.current_map_info['modifier_count']} modifiers")
            else:
                # Use standard client.txt info
                self.current_map_info = client_map_info
            
            self.display.display_map_info(self.current_map_info)
            
            # Send PRE-map notification
            progress = self.session_manager.get_session_progress()
            self.notification_manager.notify_pre_map(self.current_map_info, progress)
                
        except Exception as e:
            self.display.display_error("PRE", str(e))
    
    def analyze_waystone(self):
        """Analyze waystone from inventory (experimental) - display only, no map start"""
        self.rate_limit()
        
        try:
            # Take inventory snapshot for waystone analysis only
            current_inventory = snapshot_inventory(self.token, self.config.CHAR_TO_CHECK)
            
            # Find and parse waystone
            waystone = self.waystone_analyzer.find_waystone_in_inventory(current_inventory)
            waystone_info = self.waystone_analyzer.parse_waystone_info(waystone)
            
            if waystone_info:
                print("🧪 EXPERIMENTAL WAYSTONE ANALYSIS")
                self.display.display_experimental_waystone_info(waystone_info)
                
                # Cache waystone info for later use by F2
                self.cached_waystone_info = waystone_info
                print(f"💾 Waystone info cached for F2 map start")
                
                # Debug output
                if self.config.DEBUG_ENABLED:
                    print(f"[DEBUG] Waystone analyzed: {waystone_info['name']} T{waystone_info['tier']}")
                
                # Send experimental analysis notification
                progress = self.session_manager.get_session_progress()
                self.notification_manager.notify_experimental_pre_map(waystone_info, progress)
                
            else:
                print("⚠️  No waystone found in top-left inventory position (0,0)")
                self.cached_waystone_info = None
                
        except Exception as e:
            self.display.display_error("WAYSTONE ANALYSIS", str(e))
    
    def take_experimental_pre_snapshot(self):
        """Backwards compatibility - redirect to analyze_waystone"""
        self.analyze_waystone()
    
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
            # Pass inventory data for better emoji analysis
            map_value = self.display.display_price_analysis(analysis['added'], analysis['removed'], 
                                                           post_inventory=post_inventory, pre_inventory=self.pre_inventory)
            
            self.display.display_completion_separator()
            
            # Update session tracking FIRST
            self.session_manager.add_completed_map(map_value)
            
            # Update OBS overlays if available
            if self.obs_server:
                try:
                    progress = self.session_manager.get_session_progress()
                    
                    # Add map runtime to map_info for OBS display
                    obs_map_info = self.current_map_info.copy() if self.current_map_info else {}
                    if map_runtime is not None:
                        obs_map_info['map_runtime_seconds'] = map_runtime
                    
                    self.obs_server.update_item_table(
                        analysis['added'], 
                        analysis['removed'], 
                        progress, 
                        obs_map_info
                    )
                    self.obs_server.update_session_stats(progress)
                except Exception as e:
                    if self.config.DEBUG_ENABLED:
                        print(f"[DEBUG] OBS update failed: {e}")
            
            # Send POST-map notification AFTER session update
            progress = self.session_manager.get_session_progress()
            self.notification_manager.notify_post_map(self.current_map_info, map_runtime, map_value, progress)
            
            # Display session progress
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
                self.session_manager.session_id,
                self.current_gear_rarity
            )
            
        except Exception as e:
            self.display.display_error("POST", str(e))
        finally:
            self.pre_inventory = None
            self.map_start_time = None
    
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
            
            # Send inventory check notification
            self.notification_manager.notify_inventory_check(current_inventory)
                
        except Exception as e:
            self.display.display_error("INVENTORY CHECK", str(e))
    
    def debug_item_by_name(self, item_name):
        """Debug a specific item by searching current inventory"""
        self.rate_limit()
        try:
            current_inventory = snapshot_inventory(self.token, self.config.CHAR_TO_CHECK)
            print(f"🔍 Searching current inventory for: '{item_name}'")
            self.debugger.find_and_analyze_item_by_name(current_inventory, item_name, "[ITEM_DEBUG]")
        except Exception as e:
            self.display.display_error("ITEM DEBUG", str(e))
    
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
        
        # Send new session notification
        self.notification_manager.notify_session_start(session_info)
    
    def toggle_obs_server(self):
        """Toggle OBS web server on/off - works regardless of config settings"""
        if not OBS_AVAILABLE:
            print("❌ OBS integration not available (Flask not installed)")
            print("   Install with: pip install flask")
            return
        
        if self.obs_server is None:
            # Start OBS server - F9 always works regardless of config
            try:
                self.obs_server = OBSWebServer(
                    host=self.config.OBS_HOST, 
                    port=self.config.OBS_PORT,
                    quiet_mode=self.config.OBS_QUIET_MODE
                )
                self.obs_server.start_background()
                print(f"🎬 OBS Web Server started: http://{self.config.OBS_HOST}:{self.config.OBS_PORT}")
                print(f"   📊 Item Table: http://{self.config.OBS_HOST}:{self.config.OBS_PORT}/obs/item_table")
                print(f"   📈 Session Stats: http://{self.config.OBS_HOST}:{self.config.OBS_PORT}/obs/session_stats")
                if self.config.OBS_QUIET_MODE:
                    print("   🔇 Quiet mode enabled - no request logs")
                print("   💡 F9 again to stop, or F2→F3 to see live data!")
            except Exception as e:
                print(f"❌ Failed to start OBS server: {e}")
                self.obs_server = None
        else:
            # Stop OBS server (Flask doesn't have easy stop, so we just disable it)
            print("🔴 OBS Web Server disabled")
            self.obs_server = None
    
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
        print("\n🔄 Shutting down...")
        
        # Unregister hotkeys
        self.hotkey_manager.unregister_all()
        
        # End session and show final stats
        if self.session_manager.is_session_active():
            # Get final session stats and display with custom header
            stats = self.session_manager.get_current_session_stats(self.config.get_log_file_path())
            if stats:
                self.display.display_session_stats(
                    stats['session_id'],
                    stats['runtime']['hours'],
                    stats['runtime']['minutes'],
                    stats['runtime']['seconds'],
                    stats['maps_completed'],
                    stats['total_value'],
                    stats['detailed_stats'],
                    custom_header="🎬 FINAL SESSION STATS"
                )
            
            # End the session
            session_end_info = self.session_manager.end_current_session()
            
            # Show completion toast if there were maps
            if session_end_info and session_end_info.get('maps_completed', 0) > 0:
                self.display.display_session_completion(
                    session_end_info['maps_completed'],
                    session_end_info['total_value']
                )
        else:
            print("ℹ️ No active session to end")
        
        print("👋 Bye!")


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