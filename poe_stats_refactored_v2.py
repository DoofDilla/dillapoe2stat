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
from game_state import GameState
from app_registration import AppRegistration
from utils import format_time, get_current_timestamp

# Import existing modules
from client_parsing import get_last_map_from_client
from poe_logging import log_run
from poe_api import get_token, get_characters, snapshot_inventory
from gear_rarity_analyzer import GearRarityAnalyzer
from auto_map_detector import AutoMapDetector

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
        
        # Ensure app is registered for proper toast notifications
        AppRegistration.ensure_app_registered()
        
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
        self.game_state = GameState()
        
        # OBS Integration (optional) - Only initialize if auto-start enabled
        self.obs_server = None
        if OBS_AVAILABLE and self.config.OBS_AUTO_START:
            try:
                self.obs_server = OBSWebServer(
                    host=self.config.OBS_HOST, 
                    port=self.config.OBS_PORT,
                    quiet_mode=self.config.OBS_QUIET_MODE
                )
                print("🎬 OBS integration enabled (auto-start)")
            except Exception as e:
                print(f"⚠️  OBS server initialization failed: {e}")
                self.obs_server = None
        elif OBS_AVAILABLE:
            pass  # OBS status will be shown in the startup display
        
        # Simulation Manager (for testing)
        try:
            from simulation_manager import SimulationManager
            self.simulation_manager = SimulationManager(self.config.get_debug_dir())
        except ImportError:
            self.simulation_manager = None
            if self.config.DEBUG_ENABLED:
                print("[DEBUG] Simulation manager not available")
        
        # API and System State (kept in main class)
        self.token = None
        self.pre_inventory = None
        self.last_api_call = 0.0
        
        # Functional Components
        self.gear_rarity_analyzer = None  # Initialized after token is available
        
        # Auto Map Detection
        self.auto_detector = None
        self.auto_mode_enabled = False
    
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
        
        # Initialize currency cache for better performance
        from price_check_poe2 import initialize_currency_cache
        initialize_currency_cache()
        
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
            self.config.OUTPUT_MODE,
            self.game_state.current_gear_rarity
        )
        
        # Display gear rarity info separately
        self._display_gear_rarity_info()
        
        # Initialize auto map detector
        self.auto_detector = AutoMapDetector(
            self.config.CLIENT_LOG,
            self.config,
            on_map_enter=self._auto_pre_snapshot,
            on_map_exit=self._auto_post_snapshot,
            on_waystone_trigger=self._auto_waystone_analysis
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
    
    def _update_gear_rarity(self):
        """Update the cached gear rarity value"""
        try:
            if self.gear_rarity_analyzer:
                result = self.gear_rarity_analyzer.calculate_total_gear_rarity(self.config.CHAR_TO_CHECK)
                if result.get('success', False):
                    self.game_state.update_gear_rarity(result['total_rarity_bonus'])
                else:
                    self.game_state.update_gear_rarity(None)
                    if self.config.DEBUG_ENABLED:
                        print(f"[DEBUG] Gear rarity update failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.game_state.update_gear_rarity(None)
            if self.config.DEBUG_ENABLED:
                print(f"[DEBUG] Gear rarity update exception: {e}")
    
    def get_gear_rarity(self):
        """Get current gear rarity with refresh if needed"""
        if self.game_state.current_gear_rarity is None:
            self._update_gear_rarity()
        return self.game_state.current_gear_rarity
    
    def _display_gear_rarity_info(self):
        """Display gear rarity information"""
        if self.game_state.current_gear_rarity is not None:
            from display import Colors
            rarity_color = Colors.GOLD if self.game_state.current_gear_rarity > 0 else Colors.GRAY
            print(f"✨ Gear Rarity: {rarity_color}{self.game_state.current_gear_rarity}%{Colors.END}")
        elif self.config.DEBUG_ENABLED:
            print("[DEBUG] Gear rarity not available")
    
    def take_pre_snapshot(self):
        """Take PRE-map inventory snapshot"""
        self.rate_limit()
        try:
            map_start_time = get_current_timestamp()
            self.game_state.start_map(map_start_time)
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
                    "map_info": self.game_state.current_map_info
                }
                self.debugger.dump_inventory_to_file(self.pre_inventory, "pre_inventory", metadata)
            
            # Get current map info from client.txt
            client_map_info = get_last_map_from_client(
                self.config.CLIENT_LOG, 
                self.config.CLIENT_LOG_SCAN_BYTES
            )
            
            # Combine client.txt info with cached waystone info if available
            if self.game_state.cached_waystone_info and client_map_info:
                # Use map name from client.txt but add waystone attributes
                map_info = {
                    'map_name': client_map_info['map_name'],
                    'level': client_map_info['level'],
                    'seed': client_map_info['seed'],
                    'source': 'client_log_with_waystone',
                    # Add waystone attributes for logging (but not prefixes/suffixes)
                    'waystone_tier': self.game_state.cached_waystone_info['tier'],
                    'area_modifiers': self.game_state.cached_waystone_info['area_modifiers'],
                    'modifier_count': len(self.game_state.cached_waystone_info['prefixes']) + len(self.game_state.cached_waystone_info['suffixes'])
                }
                print(f"📊 Enhanced with waystone data: T{self.game_state.cached_waystone_info['tier']}, {map_info['modifier_count']} modifiers")
            else:
                # Use standard client.txt info
                map_info = client_map_info
            
            self.game_state.update_map_info(map_info)
            self.display.display_map_info(self.game_state.current_map_info)
            
            # Update session progress and send PRE-map notification  
            progress = self.session_manager.get_session_progress()
            self.game_state.update_session_progress(progress)
            self.notification_manager.notify_pre_map(self.game_state)
                
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
                self.game_state.update_waystone_info(waystone_info)
                print(f"💾 Waystone info cached for F2 map start")
                
                # Debug output
                if self.config.DEBUG_ENABLED:
                    print(f"[DEBUG] Waystone analyzed: {waystone_info['name']} T{waystone_info['tier']}")
                
                # Send experimental analysis notification
                progress = self.session_manager.get_session_progress()
                self.game_state.update_session_progress(progress)
                self.notification_manager.notify_experimental_pre_map(self.game_state)
                
            else:
                print("⚠️  No waystone found in top-left inventory position (0,0)")
                self.game_state.update_waystone_info(None)
                
        except Exception as e:
            self.display.display_error("WAYSTONE ANALYSIS", str(e))
    
    def take_experimental_pre_snapshot(self):
        """Backwards compatibility - redirect to analyze_waystone"""
        self.analyze_waystone()
    
    def take_post_snapshot(self, simulated_data=None):
        """Take POST-map inventory snapshot and analyze differences"""
        if self.pre_inventory is None:
            self.display.display_info_message("[POST] no PRE snapshot yet. Press F2 first.")
            return
        
        if not simulated_data:
            self.rate_limit()
        
        try:
            if simulated_data:
                post_inventory = simulated_data
                self.display.display_inventory_count(len(post_inventory), "[SIMULATED POST]")
            else:
                post_inventory = snapshot_inventory(self.token, self.config.CHAR_TO_CHECK)
                self.display.display_inventory_count(len(post_inventory), "[POST]")
            
            # Debug output
            if self.config.DEBUG_SHOW_SUMMARY:
                self.debugger.dump_item_summary(post_inventory, "[POST-SUMMARY]")
            elif self.config.DEBUG_ENABLED:
                self.debugger.dump_inventory_to_console(post_inventory, "[POST-DEBUG]")
            
            # Calculate map runtime
            map_runtime = None
            if self.game_state.map_start_time is not None:
                map_runtime = time.time() - self.game_state.map_start_time
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
                    obs_map_info = self.game_state.current_map_info.copy() if self.game_state.current_map_info else {}
                    if map_runtime is not None:
                        obs_map_info['map_runtime_seconds'] = map_runtime
                    
                    # Get the same processed data that terminal displays
                    from price_check_poe2 import valuate_items_raw
                    processed_added = []
                    if analysis['added']:
                        added_rows, _ = valuate_items_raw(analysis['added'])
                        processed_added = added_rows
                    
                    self.obs_server.update_item_table(
                        processed_added, 
                        [], 
                        progress, 
                        obs_map_info
                    )
                    self.obs_server.update_session_stats(progress)
                except Exception as e:
                    if self.config.DEBUG_ENABLED:
                        print(f"[DEBUG] OBS update failed: {e}")
            
            # Send POST-map notification AFTER session update
            progress = self.session_manager.get_session_progress()
            
            # Update game state with map completion data
            self.game_state.complete_map(map_value, map_runtime)
            self.game_state.update_session_progress(progress)
            self.notification_manager.notify_post_map(self.game_state)
            
            # Display session progress
            if progress:
                self.display.display_session_progress(**progress)
            
            # Log the run
            log_run(
                self.config.CHAR_TO_CHECK, 
                analysis['added'], 
                analysis['removed'], 
                self.game_state.current_map_info, 
                map_value, 
                self.config.get_log_file_path(), 
                map_runtime, 
                self.session_manager.session_id,
                self.game_state.current_gear_rarity
            )
            
        except Exception as e:
            self.display.display_error("POST", str(e))
        finally:
            self.pre_inventory = None
            # Map state is handled by game_state now
    
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
            # Add auto detection status to stats
            auto_status = self.get_auto_status()
            print(f"🤖 {auto_status}")
            
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
    
    def simulate_pre_snapshot(self):
        """Simulate PRE-map snapshot using debug files or hardcoded data"""
        if not self.simulation_manager:
            print("⚠️  Simulation not available")
            return
        
        try:
            # Get simulation data
            pre_data, _ = self.simulation_manager.get_simulation_data()
            
            # Set up simulated state
            self.game_state.start_map(time.time())
            self.pre_inventory = pre_data
            
            # Create simulated map info
            map_info = self.simulation_manager.create_simulated_map_info()
            self.game_state.update_map_info(map_info)
            
            # Cache simulated waystone info (like experimental waystone analysis)
            waystone_info = self.simulation_manager.create_simulated_waystone_info()
            self.game_state.update_waystone_info(waystone_info)
            
            self.display.display_inventory_count(len(self.pre_inventory), "[SIMULATED PRE]")
            self.display.display_map_info(self.game_state.current_map_info)
            
            print(f"🧪 Simulated waystone: T{self.game_state.cached_waystone_info['tier']} with {len(self.game_state.cached_waystone_info['prefixes']) + len(self.game_state.cached_waystone_info['suffixes'])} modifiers")
            print("💾 Ready for simulated POST (Ctrl+Shift+F3)")
            
        except Exception as e:
            self.display.display_error("SIMULATION PRE", str(e))
    
    def simulate_post_snapshot(self):
        """Simulate POST-map snapshot using debug files or hardcoded data"""
        if not self.simulation_manager:
            print("⚠️  Simulation not available")
            return
            
        if self.pre_inventory is None:
            print("⚠️  No PRE snapshot. Use Ctrl+Shift+F2 first.")
            return
        
        try:
            # Get simulation data
            _, post_data = self.simulation_manager.get_simulation_data()
            
            # Call normal post-snapshot with simulated data
            self.take_post_snapshot(simulated_data=post_data)
            
        except Exception as e:
            self.display.display_error("SIMULATION POST", str(e))
    
    def toggle_obs_server(self):
        """Toggle OBS web server on/off - F9 always works when Flask is available"""
        if not OBS_AVAILABLE:
            print("❌ OBS integration not available (Flask not installed)")
            print("   Install with: pip install flask")
            return
        
        if self.obs_server is None:
            # Create and start OBS server
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
            # Check if server is actually running
            try:
                # Try to stop gracefully if possible, otherwise just disable
                print("🔴 OBS Web Server stopped")
                self.obs_server = None
            except:
                print("🔴 OBS Web Server disabled")
                self.obs_server = None
    
    def toggle_auto_mode(self):
        """Toggle automatic map detection on/off"""
        if not self.auto_detector:
            print("⚠️  Auto detector not initialized")
            return
            
        if self.auto_mode_enabled:
            # Turn off auto mode
            self.auto_detector.stop()
            self.auto_mode_enabled = False
            print("🔄 Auto mode OFF - Manual F2/F3 required")
            self.notification_manager.notify_info("Auto Detection", "Manual mode enabled")
        else:
            # Turn on auto mode  
            self.auto_detector.start()
            self.auto_mode_enabled = True
            print("🤖 Auto mode ON - F2/F3 triggered automatically")
            print("     🏠 Hideout → Map: Auto F2")
            print("     🗺️  Map → Hideout: Auto F3")
            print("     🕳️  Map → Abyss → Map: No triggers (stays in map)")
            print("     ⚡ Well of Souls → Hideout: Auto Ctrl+F2")
            self.notification_manager.notify_info("Auto Detection", "Automatic F2/F3 + Waystone Analysis enabled")
    
    def _auto_pre_snapshot(self, map_info):
        """Automatic PRE snapshot when entering a map"""
        print(f"🤖 AUTO F2: Entering {map_info['area_name']}")
        try:
            # Set the map info from auto detection
            detected_map_info = {
                'map_name': map_info['area_name'],
                'level': map_info['level'],
                'seed': map_info['seed'],
                'source': 'auto_detection',
                'map_code': map_info['area_code'],
                'timestamp': map_info['timestamp']
            }
            
            # Combine with cached waystone info if available
            if self.game_state.cached_waystone_info:
                detected_map_info.update({
                    'waystone_tier': self.game_state.cached_waystone_info['tier'],
                    'area_modifiers': self.game_state.cached_waystone_info['area_modifiers'],
                    'modifier_count': len(self.game_state.cached_waystone_info['prefixes']) + len(self.game_state.cached_waystone_info['suffixes']),
                    'source': 'auto_detection_with_waystone'
                })
                print(f"📊 Enhanced with waystone data: T{self.game_state.cached_waystone_info['tier']}, {detected_map_info['modifier_count']} modifiers")
            
            # Update game state with the complete map info
            self.game_state.update_map_info(detected_map_info)
            
            # Trigger the actual pre snapshot
            self.take_pre_snapshot()
            
        except Exception as e:
            print(f"⚠️  Auto F2 failed: {e}")
    
    def _auto_post_snapshot(self, map_info):
        """Automatic POST snapshot when exiting a map"""
        print(f"🤖 AUTO F3: Finished {map_info['area_name']}")
        try:
            # Trigger the actual post snapshot
            self.take_post_snapshot()
            
        except Exception as e:
            print(f"⚠️  Auto F3 failed: {e}")
    
    def _auto_waystone_analysis(self, area_info):
        """Automatic waystone analysis when entering trigger areas"""
        print(f"⚡ AUTO CTRL+F2: Waystone analysis triggered at {area_info['area_name']}")
        try:
            # Trigger waystone analysis
            self.analyze_waystone()
            
        except Exception as e:
            print(f"⚠️  Auto waystone analysis failed: {e}")
    
    def _auto_waystone_analysis(self, area_info):
        """Automatic waystone analysis when entering trigger areas"""
        print(f"⚡ AUTO CTRL+F2: Waystone analysis triggered at {area_info['area_name']}")
        try:
            # Trigger waystone analysis
            self.analyze_waystone()
            
        except Exception as e:
            print(f"⚠️  Auto waystone analysis failed: {e}")
    
    def get_auto_status(self):
        """Get current auto detection status"""
        if not self.auto_detector:
            return "Auto detector not initialized"
            
        status = self.auto_detector.get_status()
        if not status['running']:
            return "🔄 Manual mode (Ctrl+F6 to enable auto)"
        
        current_area = status['current_area'] or 'Unknown'
        in_map = "🗺️ IN MAP" if status['is_in_map'] else "🏠 SAFE ZONE"
        
        return f"🤖 Auto mode | {in_map} | Current: {current_area}"

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
        
        # Stop auto detector
        if self.auto_detector and self.auto_mode_enabled:
            self.auto_detector.stop()
        
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
    
    # Configuration summary is now shown in display_startup_info with HasiSkull
    # config.print_config_summary()
    # print()
    
    # Create and run tracker
    tracker = PoEStatsTracker(config)
    
    if config.DEBUG_ENABLED:
        print(f"[DEBUG MODE] Enabled - Debug to file: {config.DEBUG_TO_FILE}, "
              f"Show summary: {config.DEBUG_SHOW_SUMMARY}")
    
    tracker.run()


if __name__ == "__main__":
    main()