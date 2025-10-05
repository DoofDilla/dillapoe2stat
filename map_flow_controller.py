"""
Map Flow Controller - Phase-Based Architecture
Orchestrates the complete PRE/POST map tracking flow in clear, testable phases

Flow Overview:
    PRE-MAP:  Snapshot → Parse Map → Update State → Notify
    POST-MAP: Snapshot → Diff → Value → Capture Before → Update → Notify → Reset
"""

import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

from inventory_snapshot import InventorySnapshotService, InventorySnapshot
from inventory_analyzer import InventoryAnalyzer
from game_state import GameState
from session_manager import SessionManager
from display import DisplayManager
from notification_manager import NotificationManager
from client_parsing import get_last_map_from_client
from poe_logging import log_run
from price_check_poe2 import valuate_items_raw


@dataclass
class DiffResult:
    """Result of inventory diff operation
    
    Attributes:
        added_items: Items that were added to inventory
        removed_items: Items that were removed from inventory
        added_count: Number of items added
        removed_count: Number of items removed
    """
    added_items: List[Dict[str, Any]]
    removed_items: List[Dict[str, Any]]
    
    @property
    def added_count(self) -> int:
        return len(self.added_items)
    
    @property
    def removed_count(self) -> int:
        return len(self.removed_items)


@dataclass
class ValueResult:
    """Result of loot value calculation
    
    Attributes:
        total_value_ex: Total value in exalted orbs
        total_value_chaos: Total value in chaos orbs
        items_with_values: List of items with valuation data (from valuate_items_raw)
        top_3_items: Top 3 most valuable items
    """
    total_value_ex: float
    total_value_chaos: float
    items_with_values: List[Dict[str, Any]]
    top_3_items: List[Dict[str, Any]]


@dataclass
class SessionSnapshot:
    """Snapshot of session state at a point in time
    
    Used for capturing session state BEFORE adding current map,
    enabling comparison in notifications (Run ex/h vs Session Avg ex/h)
    
    Attributes:
        maps_completed: Number of maps completed
        total_value: Total value accumulated
        runtime_seconds: Total session runtime in seconds
        value_per_hour: Calculated ex/h rate
    """
    maps_completed: int
    total_value: float
    runtime_seconds: float
    value_per_hour: float


class MapFlowController:
    """Controls the complete PRE/POST map tracking flow in clear phases
    
    This controller orchestrates all components needed for map tracking:
    - Inventory snapshots (via InventorySnapshotService)
    - Game state management (via GameState)
    - Session tracking (via SessionManager)
    - Display output (via DisplayManager)
    - Notifications (via NotificationManager)
    
    Each public method (execute_*_flow) represents a complete user action flow,
    broken down into small, testable phases.
    """
    
    def __init__(
        self,
        snapshot_service: InventorySnapshotService,
        inventory_analyzer: InventoryAnalyzer,
        game_state: GameState,
        session_manager: SessionManager,
        display: DisplayManager,
        notification: NotificationManager,
        config,
        debugger=None
    ):
        """Initialize flow controller with all required services
        
        Args:
            snapshot_service: Service for taking inventory snapshots
            inventory_analyzer: Analyzer for inventory diffs
            game_state: Central game state manager
            session_manager: Session tracking manager
            display: Display manager for console output
            notification: Notification manager for toasts
            config: Configuration object
            debugger: Optional debug helper
        """
        self.snapshot_service = snapshot_service
        self.inventory_analyzer = inventory_analyzer
        self.game_state = game_state
        self.session = session_manager
        self.display = display
        self.notify = notification
        self.config = config
        self.debugger = debugger
        
        # Snapshot storage
        self.pre_snapshot: Optional[InventorySnapshot] = None
    
    # ============================================================================
    # PRE-MAP FLOW (4 Phases)
    # ============================================================================
    
    def execute_pre_map_flow(self) -> bool:
        """Execute complete PRE-map flow
        
        Flow Phases:
            1. Take inventory snapshot
            2. Parse map info from client.txt
            3. Update game state
            4. Send notification
            
        Returns:
            True if flow completed successfully, False otherwise
        """
        try:
            # Phase 1: Snapshot
            self.pre_snapshot = self._phase_pre_snapshot()
            
            # Phase 2: Parse map info
            map_info = self._phase_parse_map_info()
            
            # Phase 3: Update state
            self._phase_update_pre_state(map_info)
            
            # Phase 4: Notify
            self._phase_pre_notification()
            
            return True
            
        except Exception as e:
            self.display.display_error("PRE-FLOW", str(e))
            return False
    
    def _phase_pre_snapshot(self) -> InventorySnapshot:
        """Phase 1: Take PRE-map inventory snapshot
        
        Returns:
            InventorySnapshot object with PRE inventory data
        """
        snapshot = self.snapshot_service.take_snapshot(
            self.config.CHAR_TO_CHECK,
            snapshot_type="PRE"
        )
        
        self.display.display_inventory_count(snapshot.item_count, "[PRE]")
        
        # Debug output
        if self.debugger:
            if self.config.DEBUG_SHOW_SUMMARY:
                self.debugger.dump_item_summary(snapshot.items, "[PRE-SUMMARY]")
            elif self.config.DEBUG_ENABLED:
                self.debugger.dump_inventory_to_console(snapshot.items, "[PRE-DEBUG]")
            
            if self.config.DEBUG_TO_FILE:
                metadata = {
                    "character": self.config.CHAR_TO_CHECK,
                    "snapshot_type": "PRE",
                    "map_info": self.game_state.current_map_info
                }
                self.debugger.dump_inventory_to_file(snapshot.items, "pre_inventory", metadata)
        
        return snapshot
    
    def _phase_parse_map_info(self) -> Optional[Dict[str, Any]]:
        """Phase 2: Parse map information from client.txt
        
        Combines client.txt map info with cached waystone info if available.
        
        Returns:
            Dict with map information or None if not found
        """
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
        
        return map_info
    
    def _phase_update_pre_state(self, map_info: Optional[Dict[str, Any]]):
        """Phase 3: Update game state for PRE-map
        
        Args:
            map_info: Parsed map information from Phase 2
        """
        # Start map tracking with current timestamp
        from utils import get_current_timestamp
        map_start_time = get_current_timestamp()
        self.game_state.start_map(map_start_time)
        
        # Update map info
        self.game_state.update_map_info(map_info)
        self.display.display_map_info(self.game_state.current_map_info)
        
        # Update session progress cache
        progress = self.session.get_session_progress()
        self.game_state.update_session_progress(progress)
    
    def _phase_pre_notification(self):
        """Phase 4: Send PRE-map notification"""
        self.notify.notify_pre_map(self.game_state)
    
    # ============================================================================
    # POST-MAP FLOW (7 Phases)
    # ============================================================================
    
    def execute_post_map_flow(self, simulated_data: Optional[List] = None, obs_server=None) -> bool:
        """Execute complete POST-map flow
        
        Flow Phases:
            1. Take inventory snapshot
            2. Diff inventories (PRE vs POST)
            3. Calculate loot value
            4. Capture session state BEFORE adding this map
            5. Update session & game state
            6. Send notification
            7. Reset current map state
            
        Args:
            simulated_data: Optional simulated POST inventory (for testing)
            obs_server: Optional OBS server for overlay updates
            
        Returns:
            True if flow completed successfully, False otherwise
        """
        # Validation: Must have PRE snapshot
        if self.pre_snapshot is None:
            self.display.display_info_message("[POST] no PRE snapshot yet. Press F2 first.")
            return False
        
        try:
            # Phase 1: Snapshot
            post_snapshot = self._phase_post_snapshot(simulated_data)
            
            # Phase 2: Diff inventories
            diff_result = self._phase_inventory_diff(post_snapshot)
            
            # Phase 3: Calculate value
            value_result = self._phase_calculate_value(diff_result, post_snapshot)
            
            # Calculate map runtime
            map_runtime = self._calculate_map_runtime()
            
            # Phase 4: Capture session state BEFORE update (for notification comparison)
            session_before = self._phase_capture_session_before()
            
            # Phase 5: Update session & state
            self._phase_update_post_state(value_result, map_runtime, obs_server)
            
            # Phase 6: Notify
            self._phase_post_notification(session_before)
            
            # Phase 7: Log the run
            self._phase_log_run(diff_result, value_result.total_value_ex, map_runtime)
            
            # Phase 8: Display session progress
            self._phase_display_session()
            
            # Phase 9: Reset current map
            self._phase_reset_map()
            
            return True
            
        except Exception as e:
            self.display.display_error("POST-FLOW", str(e))
            return False
    
    def _phase_post_snapshot(self, simulated_data: Optional[List] = None) -> InventorySnapshot:
        """Phase 1: Take POST-map inventory snapshot
        
        Args:
            simulated_data: Optional simulated inventory data for testing
            
        Returns:
            InventorySnapshot object with POST inventory data
        """
        if simulated_data:
            # Create snapshot from simulated data (no API call)
            snapshot = InventorySnapshot(
                items=simulated_data,
                snapshot_type="POST",
                timestamp=time.time()
            )
            self.display.display_inventory_count(snapshot.item_count, "[SIMULATED POST]")
        else:
            # Take real snapshot via API
            snapshot = self.snapshot_service.take_snapshot(
                self.config.CHAR_TO_CHECK,
                snapshot_type="POST"
            )
            self.display.display_inventory_count(snapshot.item_count, "[POST]")
        
        # Debug output
        if self.debugger:
            if self.config.DEBUG_SHOW_SUMMARY:
                self.debugger.dump_item_summary(snapshot.items, "[POST-SUMMARY]")
            elif self.config.DEBUG_ENABLED:
                self.debugger.dump_inventory_to_console(snapshot.items, "[POST-DEBUG]")
        
        return snapshot
    
    def _phase_inventory_diff(self, post_snapshot: InventorySnapshot) -> DiffResult:
        """Phase 2: Calculate inventory differences (PRE vs POST)
        
        Args:
            post_snapshot: POST inventory snapshot
            
        Returns:
            DiffResult with added/removed items
        """
        analysis = self.inventory_analyzer.analyze_changes(
            self.pre_snapshot.items,
            post_snapshot.items
        )
        
        if 'error' in analysis:
            raise Exception(f"Inventory diff failed: {analysis['error']}")
        
        # Debug: show inventory comparison (comprehensive mode only)
        if self.config.OUTPUT_MODE == "comprehensive" and self.debugger:
            self.debugger.compare_inventories(self.pre_snapshot.items, post_snapshot.items)
        
        return DiffResult(
            added_items=analysis.get('added', []),
            removed_items=analysis.get('removed', [])
        )
    
    def _phase_calculate_value(self, diff_result: DiffResult, post_snapshot: InventorySnapshot) -> ValueResult:
        """Phase 3: Calculate loot value and extract item data
        
        Args:
            diff_result: Inventory diff result from Phase 2
            post_snapshot: POST snapshot for emoji analysis
            
        Returns:
            ValueResult with values and item data
        """
        # Display changes
        self.display.display_inventory_changes(diff_result.added_items, diff_result.removed_items)
        
        # Calculate value (this also displays the price table)
        total_value_ex = self.display.display_price_analysis(
            diff_result.added_items,
            diff_result.removed_items,
            post_inventory=post_snapshot.items,
            pre_inventory=self.pre_snapshot.items
        )
        
        self.display.display_completion_separator()
        
        # Get items with value data for top drops tracking
        items_with_values = []
        if diff_result.added_items:
            added_rows, _ = valuate_items_raw(diff_result.added_items)
            items_with_values = added_rows
        
        # Calculate top 3 items
        top_3 = self._calculate_top_3(items_with_values)
        
        return ValueResult(
            total_value_ex=total_value_ex,
            total_value_chaos=0.0,  # Could be extracted from display_price_analysis if needed
            items_with_values=items_with_values,
            top_3_items=top_3
        )
    
    def _calculate_map_runtime(self) -> Optional[float]:
        """Calculate map runtime in seconds
        
        Returns:
            Runtime in seconds or None if no map start time
        """
        if self.game_state.map_start_time is not None:
            runtime = time.time() - self.game_state.map_start_time
            self.display.display_runtime(runtime)
            return runtime
        return None
    
    def _phase_capture_session_before(self) -> SessionSnapshot:
        """Phase 4: Capture session state BEFORE adding current map
        
        CRITICAL: This does NOT add the map to session!
        Purpose: Get baseline metrics for notification comparison (Run ex/h vs Avg ex/h)
        
        Returns:
            SessionSnapshot with state BEFORE current map is added
        """
        progress = self.session.get_session_progress()
        
        # Calculate ex/h from BEFORE state
        if progress and progress.get('runtime_seconds', 0) > 0:
            value_per_hour = progress.get('total_value', 0) / (progress.get('runtime_seconds', 1) / 3600)
        else:
            value_per_hour = 0.0
        
        return SessionSnapshot(
            maps_completed=progress.get('maps_completed', 0) if progress else 0,
            total_value=progress.get('total_value', 0.0) if progress else 0.0,
            runtime_seconds=progress.get('runtime_seconds', 0.0) if progress else 0.0,
            value_per_hour=value_per_hour
        )
    
    def _phase_update_post_state(self, value_result: ValueResult, map_runtime: Optional[float], obs_server=None):
        """Phase 5: Update session and game state with map completion
        
        CRITICAL: This is where the map is added to session (SINGLE call!)
        
        Args:
            value_result: Value calculation result from Phase 3
            map_runtime: Map runtime in seconds
            obs_server: Optional OBS server for overlay updates
        """
        # Update game state with map completion data
        self.game_state.complete_map(value_result.total_value_ex, map_runtime)
        
        # Add map to session tracking (SINGLE CALL - the only place this happens!)
        self.session.add_completed_map(value_result.total_value_ex)
        
        # Get updated session progress AFTER adding map
        progress_after = self.session.get_session_progress()
        self.game_state.update_session_progress(progress_after)
        
        # Update top drops and best map tracking
        self.game_state.update_map_completion(value_result.items_with_values)
        
        # Update OBS overlays if available
        if obs_server:
            try:
                obs_map_info = self.game_state.current_map_info.copy() if self.game_state.current_map_info else {}
                if map_runtime is not None:
                    obs_map_info['map_runtime_seconds'] = map_runtime
                
                obs_server.update_item_table(
                    value_result.items_with_values,
                    [],
                    progress_after,
                    obs_map_info
                )
                obs_server.update_session_stats(progress_after)
            except Exception as e:
                if self.config.DEBUG_ENABLED:
                    print(f"[DEBUG] OBS update failed: {e}")
    
    def _phase_post_notification(self, session_before: SessionSnapshot):
        """Phase 6: Send POST-map notification
        
        Args:
            session_before: Session state from Phase 4 (BEFORE map was added)
        """
        # Store session_before ex/h for notification comparison
        self.game_state.set_session_comparison_baseline(session_before.value_per_hour)
        
        # Send notification (uses session_before for comparison)
        self.notify.notify_post_map(self.game_state)
    
    def _phase_log_run(self, diff_result: DiffResult, map_value: float, map_runtime: Optional[float]):
        """Phase 7: Log the run to file
        
        Args:
            diff_result: Inventory diff from Phase 2
            map_value: Total map value
            map_runtime: Map runtime in seconds
        """
        log_run(
            self.config.CHAR_TO_CHECK,
            diff_result.added_items,
            diff_result.removed_items,
            self.game_state.current_map_info,
            map_value,
            self.config.get_log_file_path(),
            map_runtime,
            self.session.session_id,
            self.game_state.current_gear_rarity
        )
    
    def _phase_display_session(self):
        """Phase 8: Display session progress"""
        progress = self.session.get_session_progress()
        if progress:
            self.display.display_session_progress(**progress)
    
    def _phase_reset_map(self):
        """Phase 9: Reset current map state
        
        After POST is complete, current map becomes "last map" and state is cleared.
        Note: cached_waystone_info persists for reference.
        """
        self.game_state.reset_current_map()
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _calculate_top_3(self, items_with_values: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate top 3 most valuable items
        
        Args:
            items_with_values: Items with valuation data from valuate_items_raw
            
        Returns:
            List of top 3 items sorted by ex_total value
        """
        # Filter items with value > 0 and sort by total exalted value
        # Ensure ex_total is not None before comparison
        valuable_items = [
            item for item in items_with_values
            if (item.get('ex_total') or 0) > 0
        ]
        
        sorted_items = sorted(
            valuable_items,
            key=lambda x: x.get('ex_total', 0) or 0,
            reverse=True
        )
        
        return sorted_items[:3]
