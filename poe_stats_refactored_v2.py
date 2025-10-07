"""
PoE Stats Tracker - Main Script
Tracks inventory changes, session statistics, and loot values for Path of Exile 2

Architecture:
- Phase-based flow controller for PRE/POST map tracking
- Modular components for better maintainability
- Clean separation of concerns

Flow Documentation: See docs/SESSION_FLOW.md
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

# Import new flow controller (Phase 2 refactoring)
from map_flow_controller import MapFlowController
from inventory_snapshot import InventorySnapshotService

# Import new flow controller (Phase 2 refactoring)
from map_flow_controller import MapFlowController
from inventory_snapshot import InventorySnapshotService

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
    """Main tracker class - Phase-based architecture with modular components
    
    Architecture Overview:
    - MapFlowController: Orchestrates PRE/POST map tracking in clear phases
    - InventorySnapshotService: Handles API calls with rate limiting
    - GameState: Central state management
    - SessionManager: Session tracking and statistics
    - DisplayManager: Console output formatting
    - NotificationManager: Windows toast notifications
    
    Flow:
    - PRE (F2):  Snapshot → Parse Map → Update State → Notify
    - POST (F3): Snapshot → Diff → Value → Track → Update → Notify → Reset
    
    See docs/SESSION_FLOW.md for detailed documentation.
    """
    
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
        
        # KISS Overlay Writer (optional) - File-based IPC for overlay
        self.overlay_writer = None
        if self.config.KISS_OVERLAY_ENABLED:
            try:
                from overlay_state_writer import OverlayStateWriter
                self.overlay_writer = OverlayStateWriter(
                    state_file=self.config.KISS_OVERLAY_STATE_FILE
                )
                print("🔍 KISS Overlay enabled (file-based IPC)")
            except Exception as e:
                print(f"⚠️  KISS Overlay initialization failed: {e}")
                self.overlay_writer = None
        
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
        
        # API and System State
        self.token = None
        
        # Functional Components
        self.gear_rarity_analyzer = None  # Initialized after token is available
        
        # Flow Controller - Handles all snapshot and map flow logic
        self.snapshot_service = None
        self.flow_controller = None
        
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
        
        # Initialize flow controller (Phase 2 refactoring)
        self.snapshot_service = InventorySnapshotService(
            token=self.token,
            min_gap_seconds=self.config.API_RATE_LIMIT
        )
        self.flow_controller = MapFlowController(
            snapshot_service=self.snapshot_service,
            inventory_analyzer=self.inventory_analyzer,
            game_state=self.game_state,
            session_manager=self.session_manager,
            display=self.display,
            notification=self.notification_manager,
            config=self.config,
            debugger=self.debugger,
            tracker=self
        )
        
        # Start new session
        session_info = self.session_manager.start_new_session()
        
        # Reset session-specific tracking in game state
        self.game_state.reset_session_tracking()
        
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
    
    # Note: rate_limit() removed - now handled by InventorySnapshotService
    
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
        """Take PRE-map inventory snapshot
        
        Delegates to MapFlowController which implements the flow in clear phases:
        1. Take snapshot → 2. Parse map info → 3. Update state → 4. Notify
        
        See docs/SESSION_FLOW.md for detailed flow documentation.
        """
        self.flow_controller.execute_pre_map_flow()
    
    def analyze_waystone(self):
        """Analyze waystone from inventory (experimental) - display only, no map start"""
        try:
            # Update overlay - Waystone Analysis phase
            if self.flow_controller:
                self.flow_controller.update_overlay('waystone_analysis')
            
            # Take inventory snapshot for waystone analysis only
            waystone_snapshot = self.snapshot_service.take_snapshot(
                self.config.CHAR_TO_CHECK,
                snapshot_type="WAYSTONE"
            )
            current_inventory = waystone_snapshot.items
            
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
                    print(f"[DEBUG] Waystone analyzed: {waystone_info['name']} T{waystone_info['tier']}, Delirious: {waystone_info.get('delirious', 0)}%")
                
                # Send experimental analysis notification
                progress = self.session_manager.get_session_progress()
                self.game_state.update_session_progress(progress)
                self.notification_manager.notify_experimental_pre_map(self.game_state)
                
                # Update overlay again with waystone data
                if self.flow_controller:
                    self.flow_controller.update_overlay('waystone_analysis')
                
            else:
                print("⚠️  No waystone found in top-left inventory position (0,0)")
                self.game_state.update_waystone_info(None)
                
        except Exception as e:
            self.display.display_error("WAYSTONE ANALYSIS", str(e))
    
    def take_experimental_pre_snapshot(self):
        """Backwards compatibility - redirect to analyze_waystone"""
        self.analyze_waystone()
    
    def take_post_snapshot(self, simulated_data=None):
        """Take POST-map snapshot and analyze loot
        
        Delegates to MapFlowController which implements the flow in 9 clear phases:
        1. Snapshot → 2. Diff → 3. Value → 4. Capture Before → 5. Update State
        → 6. Notify → 7. Log → 8. Display → 9. Reset
        
        See docs/SESSION_FLOW.md for detailed flow documentation.
        """
        self.flow_controller.execute_post_map_flow(
            simulated_data=simulated_data,
            obs_server=self.obs_server
        )
    
    def check_current_inventory_value(self):
        """Check and display the value of the current inventory"""
        try:
            check_snapshot = self.snapshot_service.take_snapshot(
                self.config.CHAR_TO_CHECK,
                snapshot_type="CHECK"
            )
            current_inventory = check_snapshot.items
            
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
        try:
            debug_snapshot = self.snapshot_service.take_snapshot(
                self.config.CHAR_TO_CHECK,
                snapshot_type="DEBUG"
            )
            current_inventory = debug_snapshot.items
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
        
        # Reset session-specific tracking in game state
        self.game_state.reset_session_tracking()
        
        self.display.display_session_header(
            session_info['session_id'],
            session_info['start_time_str']
        )
        
        # Send new session notification
        self.notification_manager.notify_session_start(session_info)
    
    def simulate_pre_snapshot(self):
        """Simulate PRE-map snapshot using debug files or hardcoded data
        
        Note: Simulation creates a fake snapshot in the flow controller for testing.
        """
        if not self.simulation_manager:
            print("⚠️  Simulation not available")
            return
        
        try:
            # Update overlay - Simulated PRE-1
            if self.flow_controller:
                self.flow_controller.update_overlay('pre_snapshot')
            
            # Get simulation data
            pre_data, _ = self.simulation_manager.get_simulation_data()
            
            # Create simulated snapshot in flow controller
            from inventory_snapshot import InventorySnapshot
            self.flow_controller.pre_snapshot = InventorySnapshot(
                items=pre_data,
                snapshot_type="PRE_SIMULATED",
                timestamp=time.time()
            )
            
            # Set up simulated state
            self.game_state.start_map(time.time())
            
            # Update overlay - Simulated PRE-2 (parse)
            if self.flow_controller:
                self.flow_controller.update_overlay('pre_parse')
            
            # Create simulated map info
            map_info = self.simulation_manager.create_simulated_map_info()
            self.game_state.update_map_info(map_info)
            
            # Cache simulated waystone info
            waystone_info = self.simulation_manager.create_simulated_waystone_info()
            self.game_state.update_waystone_info(waystone_info)
            
            # Update overlay - Simulated PRE-3 (update state)
            if self.flow_controller:
                self.flow_controller.update_overlay('pre_update_state')
            
            self.display.display_inventory_count(len(pre_data), "[SIMULATED PRE]")
            self.display.display_map_info(self.game_state.current_map_info)
            
            print(f"🧪 Simulated waystone: T{self.game_state.cached_waystone_info['tier']} with {len(self.game_state.cached_waystone_info['prefixes']) + len(self.game_state.cached_waystone_info['suffixes'])} modifiers")
            print("💾 Ready for simulated POST (Ctrl+Shift+F3)")
            
            # Update overlay - Simulated PRE-4 (notify)
            if self.flow_controller:
                self.flow_controller.update_overlay('pre_notify')
            
        except Exception as e:
            self.display.display_error("SIMULATION PRE", str(e))
    
    def simulate_post_snapshot(self):
        """Simulate POST-map snapshot using debug files or hardcoded data"""
        if not self.simulation_manager:
            print("⚠️  Simulation not available")
            return
            
        if not self.flow_controller.pre_snapshot:
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
            self.notification_manager.notify_automode("Auto Detection", "Manual mode enabled")
        else:
            # Turn on auto mode  
            self.auto_detector.start()
            self.auto_mode_enabled = True
            print("🤖 Auto mode ON - F2/F3 triggered automatically")
            print("     🏠 Hideout → Map: Auto F2")
            print("     🗺️  Map → Hideout: Auto F3")
            print("     🕳️  Map → Abyss → Map: No triggers (stays in map)")
            print("     ⚡ Well of Souls → Hideout: Auto Ctrl+F2")
            self.notification_manager.notify_automode("Auto Detection", "Automatic F2/F3 + Waystone Analysis enabled")
    
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