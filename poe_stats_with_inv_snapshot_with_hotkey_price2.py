import time
import keyboard
from win11toast import notify
from pathlib import Path
import uuid
import os
from collections import Counter
import re
from price_check_poe2 import valuate_items_raw, fmt  # fmt nur für hübsche Ausgabe
from client_parsing import get_last_map_from_client
from poe_logging import log_run, log_session_start, log_session_end, get_session_stats
from poe_api import get_token, get_characters, snapshot_inventory
from inventory_debug import InventoryDebugger

CLIENT_ID = "dillapoe2stat"        # deine Client Id
CLIENT_SECRET = "UgraAmlUXdP1"  # hier dein Secret eintragen

CHAR_TO_CHECK = "Mettmanwalking"
# make sure the path is where the script is located
LOG = Path(os.path.dirname(os.path.abspath(__file__))) / "runs.jsonl"

CLIENT_LOG = r"C:\GAMESSD\Path of Exile 2\logs\Client.txt"  # anpassen!

# Debug settings
DEBUG_ENABLED = True  # Set to False to disable debug output
DEBUG_TO_FILE = False  # Set to False to only show debug in console
DEBUG_SHOW_SUMMARY = True  # Show item summary instead of full JSON dump
OUTPUT_MODE = "normal"  # "normal" or "comprehensive"

# ANSI color codes for console output
class Colors:
    GOLD = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    END = '\033[0m'

def inv_key(item):
    # eindeutiger Key pro Item (Fallback: typeline+pos)
    return (
        item.get("id")
        or f"{item.get('typeLine')}|{item.get('x')},{item.get('y')}|{item.get('baseType')}"
    )

def diff_inventories(before, after):
    before_keys = {inv_key(i): i for i in before}
    after_keys  = {inv_key(i): i for i in after}

    added = [after_keys[k] for k in after_keys if k not in before_keys]
    removed = [before_keys[k] for k in before_keys if k not in after_keys]
    return added, removed


class PoEStatsTracker:
    def __init__(self, client_id, client_secret, character_name, client_log_path, debug_enabled=False, output_mode="normal"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.character_name = character_name
        self.client_log_path = client_log_path
        
        # State variables
        self.token = None
        self.pre_inventory = None
        self.current_map_info = None
        self.map_value = None
        self.last_api_call = 0.0
        self.map_start_time = None
        
        # Session tracking
        self.session_id = str(uuid.uuid4())
        self.session_start_time = time.time()
        self.session_maps_completed = 0
        self.session_total_value = 0
        
        # Setup paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(script_dir, 'cat64x64.png')
        self.log_file = Path(script_dir) / "runs.jsonl"
        self.session_log_file = Path(script_dir) / "sessions.jsonl"
        
        # Initialize debugger
        self.debugger = InventoryDebugger(debug_enabled=debug_enabled)
        self.output_mode = output_mode
    
    def initialize(self):
        """Initialize the tracker with API token and character validation"""
        self.token = get_token(self.client_id, self.client_secret)
        chars = get_characters(self.token)
        
        if not chars.get("characters"):
            print("No characters found")
            raise SystemExit
        
        # Start new session
        self.start_new_session()
        
        notify('Starting DillaPoE2Stat', f'Watching character: {self.character_name}', 
               icon=f'file://{self.icon_path}')
        print(f"🎮 Using character: {Colors.CYAN}{self.character_name}{Colors.END}")
        print(f"📋 Output mode: {Colors.BOLD}{self.output_mode.upper()}{Colors.END}")
        print(f"🆔 Session ID: {Colors.GRAY}{self.session_id[:8]}...{Colors.END}")
        print(f"⌨️  Hotkeys: {Colors.GREEN}F2{Colors.END}=PRE | {Colors.GREEN}F3{Colors.END}=POST | {Colors.GREEN}F4{Colors.END}=Debug | {Colors.GREEN}F6{Colors.END}=New Session | {Colors.GREEN}F7{Colors.END}=Session Stats | {Colors.RED}Esc{Colors.END}=Quit")
    
    def rate_limit(self, min_gap=2.5):
        """Enforce rate limiting for API calls"""
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
            self.pre_inventory = snapshot_inventory(self.token, self.character_name)
            
            if self.output_mode == "comprehensive":
                print(f"📦 [PRE] captured: {len(self.pre_inventory)} items")
                
                # Debug: dump inventory information
                if DEBUG_SHOW_SUMMARY:
                    self.debugger.dump_item_summary(self.pre_inventory, "[PRE-SUMMARY]")
                else:
                    self.debugger.dump_inventory_to_console(self.pre_inventory, "[PRE-DEBUG]")
            
            if DEBUG_TO_FILE:
                metadata = {
                    "character": self.character_name,
                    "snapshot_type": "PRE",
                    "map_info": self.current_map_info
                }
                self.debugger.dump_inventory_to_file(self.pre_inventory, "pre_inventory", metadata)
            
            self.current_map_info = get_last_map_from_client(self.client_log_path)
            if self.current_map_info:
                print(f"🗺️  {Colors.BOLD}{self.current_map_info['map_name']}{Colors.END} {Colors.GRAY}(T{self.current_map_info['level']}, seed {self.current_map_info['seed']}){Colors.END}")
            
            mapname = self.current_map_info["map_name"] if self.current_map_info else "Unknown"
            notify('Hallo Dilla!', f'Starting Map Run! {mapname}')
        except Exception as e:
            print(f"❌ [PRE] error: {e}")
    
    def display_inventory_changes(self, added, removed):
        """Display added and removed items"""
        if self.output_mode == "comprehensive":
            print(f"\n📥 Added items ({len(added)}):")
            for item in added:
                stack = f" x{item['stackSize']}" if item.get("stackSize") else ""
                print(f"  {Colors.GREEN}+{Colors.END} {item.get('typeLine')}{stack} @ {Colors.GRAY}({item.get('x')},{item.get('y')}){Colors.END}")

            print(f"\n📤 Removed items ({len(removed)}):")
            for item in removed:
                stack = f" x{item['stackSize']}" if item.get("stackSize") else ""
                print(f"  {Colors.RED}-{Colors.END} {item.get('typeLine')}{stack}")
    
    def display_price_analysis(self, added, removed):
        """Display price analysis for added/removed items"""
        try:
            added_rows, (add_c, add_e) = valuate_items_raw(added)
            removed_rows, (rem_c, rem_e) = valuate_items_raw(removed)

            # Filter items with value for normal mode
            valuable_added = [r for r in added_rows if (r['chaos_total'] or 0) > 0.01 or (r['ex_total'] or 0) > 0.01]
            valuable_removed = [r for r in removed_rows if (r['chaos_total'] or 0) > 0.01 or (r['ex_total'] or 0) > 0.01]

            if self.output_mode == "normal":
                # Normal mode: Only show valuable items
                if valuable_added:
                    print(f"\n💰 {Colors.BOLD}Valuable Loot:{Colors.END}")
                    for r in valuable_added:
                        ex_str = f" | {Colors.GOLD}{fmt(r['ex_total'])}ex{Colors.END}" if r['ex_total'] and r['ex_total'] > 0.01 else ""
                        print(f"  {Colors.GREEN}+{Colors.END} {Colors.WHITE}{r['name']}{Colors.END} {Colors.GRAY}x{r['qty']}{Colors.END} "
                              f"=> {Colors.GOLD}{fmt(r['chaos_total'])}c{Colors.END}{ex_str}")
                
                if valuable_removed:
                    print(f"\n💸 {Colors.BOLD}Valuable Items Used:{Colors.END}")
                    for r in valuable_removed:
                        ex_str = f" | {Colors.GOLD}{fmt(r['ex_total'])}ex{Colors.END}" if r['ex_total'] and r['ex_total'] > 0.01 else ""
                        print(f"  {Colors.RED}-{Colors.END} {Colors.WHITE}{r['name']}{Colors.END} {Colors.GRAY}x{r['qty']}{Colors.END} "
                              f"=> {Colors.GOLD}{fmt(r['chaos_total'])}c{Colors.END}{ex_str}")
            
            else:  # comprehensive mode
                print(f"\n💰 {Colors.BOLD}[VALUE] Added:{Colors.END}")
                for r in added_rows:
                    ex_str = f" | {Colors.GOLD}{fmt(r['ex_total'])}ex{Colors.END}" if r['ex_total'] is not None else ""
                    print(f"  {Colors.GREEN}+{Colors.END} {r['name']} {Colors.GRAY}[{r.get('category') or 'n/a'}]{Colors.END} x{r['qty']} "
                          f"=> {Colors.GOLD}{fmt(r['chaos_total'])}c{Colors.END}{ex_str}")

                print(f"\n💸 {Colors.BOLD}[VALUE] Removed:{Colors.END}")
                for r in removed_rows:
                    ex_str = f" | {Colors.GOLD}{fmt(r['ex_total'])}ex{Colors.END}" if r['ex_total'] is not None else ""
                    print(f"  {Colors.RED}-{Colors.END} {r['name']} {Colors.GRAY}[{r.get('category') or 'n/a'}]{Colors.END} x{r['qty']} "
                          f"=> {Colors.GOLD}{fmt(r['chaos_total'])}c{Colors.END}{ex_str}")

            # Calculate and display net value
            net_c = (add_c or 0) - (rem_c or 0)
            net_e = None
            if add_e is not None and rem_e is not None:
                net_e = (add_e or 0) - (rem_e or 0)

            # Show totals (always show in both modes if there's value)
            if net_c > 0.01 or (net_e and net_e > 0.01):
                print(f"\n🏆 {Colors.BOLD}Net Value:{Colors.END} {Colors.GOLD}{fmt(net_c)}c{Colors.END}", end="")
                if net_e is not None and net_e > 0.01:
                    print(f" | {Colors.GOLD}{fmt(net_e)}ex{Colors.END}")
                else:
                    print()
                self.map_value = net_e
            else:
                print(f"\n💰 {Colors.GRAY}No valuable loot this run{Colors.END}")
                
        except Exception as pe:
            print(f"❌ [VALUE] price-check error: {pe}")
    
    def take_post_snapshot(self):
        """Take POST-map inventory snapshot and analyze differences"""
        if self.pre_inventory is None:
            print("[POST] no PRE snapshot yet. Press F2 first.")
            return
        
        self.rate_limit()
        try:
            post_inventory = snapshot_inventory(self.token, self.character_name)
            
            if self.output_mode == "comprehensive":
                print(f"📦 [POST] captured: {len(post_inventory)} items")
                
                # Debug: dump post inventory and comparison
                if DEBUG_SHOW_SUMMARY:
                    self.debugger.dump_item_summary(post_inventory, "[POST-SUMMARY]")
                else:
                    self.debugger.dump_inventory_to_console(post_inventory, "[POST-DEBUG]")
            
            # Calculate map runtime
            map_runtime = None
            if self.map_start_time is not None:
                map_runtime = time.time() - self.map_start_time
                minutes = int(map_runtime // 60)
                seconds = int(map_runtime % 60)
                print(f"\n⏱️  {Colors.BOLD}Runtime:{Colors.END} {Colors.CYAN}{minutes}m {seconds}s{Colors.END}")
            
            added, removed = diff_inventories(self.pre_inventory, post_inventory)
            
            # Debug: show inventory comparison (only in comprehensive mode)
            if self.output_mode == "comprehensive":
                self.debugger.compare_inventories(self.pre_inventory, post_inventory)
            
            self.display_inventory_changes(added, removed)
            self.display_price_analysis(added, removed)
            
            print(f"\n{'='*50}")
            print(f"🎯 {Colors.GREEN}Ready for next map!{Colors.END}")
            print(f"{'='*50}\n")
            
            # Create notification message with runtime and value
            notification_msg = ""
            if map_runtime:
                notification_msg += f"\n⏱️ Time: {minutes}m {seconds}s"
            if self.map_value and self.map_value > 0.01:
                notification_msg += f"\n💰 Value: {fmt(self.map_value)}ex"
            else:
                notification_msg += "\n💰 No valuable loot"
            
            notify('Map Completed!', notification_msg, icon=f'file://{self.icon_path}')
            
            # Update session tracking
            self.session_maps_completed += 1
            if self.map_value and self.map_value > 0:
                self.session_total_value += self.map_value
            
            # Display session progress after each run
            self.display_session_progress()
            
            log_run(self.character_name, added, removed, self.current_map_info, self.map_value, self.log_file, map_runtime, self.session_id)
            
        except Exception as e:
            print(f"❌ [POST] error: {e}")
        finally:
            self.pre_inventory = None  # reset for next run
            self.map_start_time = None  # reset start time
    
    def toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        current_state = self.debugger.debug_enabled
        self.debugger.set_debug_enabled(not current_state)
    
    def toggle_output_mode(self):
        """Toggle between normal and comprehensive output mode"""
        self.output_mode = "comprehensive" if self.output_mode == "normal" else "normal"
        print(f"🔄 Output mode changed to: {Colors.BOLD}{self.output_mode.upper()}{Colors.END}")
    
    def start_new_session(self):
        """Start a new session"""
        # Log end of previous session if it exists
        if hasattr(self, 'session_id') and self.session_maps_completed > 0:
            session_runtime = time.time() - self.session_start_time
            log_session_end(self.session_id, self.character_name, session_runtime, 
                          self.session_total_value, self.session_maps_completed, self.session_log_file)
        
        # Start new session
        self.session_id = str(uuid.uuid4())
        self.session_start_time = time.time()
        self.session_maps_completed = 0
        self.session_total_value = 0
        
        log_session_start(self.session_id, self.character_name, self.session_log_file)
        
        session_time = time.strftime("%H:%M:%S", time.localtime(self.session_start_time))
        print(f"\n🎬 {Colors.BOLD}NEW SESSION STARTED{Colors.END}")
        print(f"🆔 Session ID: {Colors.CYAN}{self.session_id[:8]}...{Colors.END}")
        print(f"🕐 Started at: {Colors.GRAY}{session_time}{Colors.END}")
        print(f"{'='*50}\n")
        
        notify('New Session Started!', f'Session ID: {self.session_id[:8]}...', 
               icon=f'file://{self.icon_path}')
    
    def display_session_stats(self):
        """Display current session statistics"""
        current_time = time.time()
        session_runtime = current_time - self.session_start_time
        hours = int(session_runtime // 3600)
        minutes = int((session_runtime % 3600) // 60)
        seconds = int(session_runtime % 60)
        
        # Get detailed session stats from log
        session_stats = get_session_stats(self.session_id, self.log_file)
        
        print(f"\n📊 {Colors.BOLD}CURRENT SESSION STATS{Colors.END}")
        print(f"🆔 Session ID: {Colors.CYAN}{self.session_id[:8]}...{Colors.END}")
        print(f"⏱️  Total Time: {Colors.CYAN}{hours}h {minutes}m {seconds}s{Colors.END}")
        print(f"🗺️  Maps Completed: {Colors.GREEN}{self.session_maps_completed}{Colors.END}")
        
        if self.session_total_value > 0:
            print(f"💰 Total Value: {Colors.GOLD}{fmt(self.session_total_value)}ex{Colors.END}")
            if self.session_maps_completed > 0:
                avg_value = self.session_total_value / self.session_maps_completed
                print(f"📈 Average per Map: {Colors.GOLD}{fmt(avg_value)}ex{Colors.END}")
        else:
            print(f"💰 Total Value: {Colors.GRAY}0ex{Colors.END}")
        
        if session_stats['maps']:
            print(f"\n📜 {Colors.BOLD}Recent Maps:{Colors.END}")
            for i, map_run in enumerate(session_stats['maps'][-5:], 1):  # Show last 5 maps
                map_name = map_run['map']['name']
                map_level = map_run['map']['level']
                map_value = map_run.get('map_value', 0) or 0
                runtime = map_run.get('map_runtime')
                
                time_str = f"{int(runtime//60)}m {int(runtime%60)}s" if runtime else "N/A"
                value_str = f"{fmt(map_value)}ex" if map_value > 0.01 else "0ex"
                
                print(f"  {i}. {Colors.WHITE}{map_name}{Colors.END} {Colors.GRAY}(T{map_level}){Colors.END} "
                      f"- {Colors.CYAN}{time_str}{Colors.END} - {Colors.GOLD}{value_str}{Colors.END}")
        
        print(f"{'='*50}\n")
    
    def display_session_progress(self):
        """Display session progress after each map completion"""
        current_time = time.time()
        session_runtime = current_time - self.session_start_time
        hours = int(session_runtime // 3600)
        minutes = int((session_runtime % 3600) // 60)
        
        session_time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        print(f"\n📈 {Colors.BOLD}SESSION PROGRESS{Colors.END}")
        print(f"🕐 Session Time: {Colors.CYAN}{session_time_str}{Colors.END} | "
              f"🗺️  Maps: {Colors.GREEN}{self.session_maps_completed}{Colors.END} | "
              f"💰 Total Value: {Colors.GOLD}{fmt(self.session_total_value)}ex{Colors.END}")
        
        if self.session_maps_completed > 0:
            avg_value = self.session_total_value / self.session_maps_completed
            avg_time = session_runtime / self.session_maps_completed / 60  # in minutes
            print(f"📊 Avg/Map: {Colors.GOLD}{fmt(avg_value)}ex{Colors.END} | "
                  f"⏱️  Avg Time: {Colors.CYAN}{avg_time:.1f}m{Colors.END}")
        
        print(f"{'-'*30}")
    
    def setup_hotkeys(self):
        """Setup keyboard hotkeys"""
        keyboard.add_hotkey('f2', self.take_pre_snapshot)
        keyboard.add_hotkey('f3', self.take_post_snapshot)
        keyboard.add_hotkey('f4', self.toggle_debug_mode)
        keyboard.add_hotkey('f5', self.toggle_output_mode)  # F5 to toggle output mode
        keyboard.add_hotkey('f6', self.start_new_session)   # F6 to start new session
        keyboard.add_hotkey('f7', self.display_session_stats)  # F7 to view session stats
    
    def run(self):
        """Main application loop"""
        self.initialize()
        self.setup_hotkeys()
        
        try:
            keyboard.wait('ctrl+esc')  # Use Ctrl+Esc to exit
        except KeyboardInterrupt:
            pass
        finally:
            # Log session end on exit
            if self.session_maps_completed > 0:
                session_runtime = time.time() - self.session_start_time
                log_session_end(self.session_id, self.character_name, session_runtime, 
                              self.session_total_value, self.session_maps_completed, self.session_log_file)
                print(f"\n📊 {Colors.BOLD}Session completed!{Colors.END}")
                print(f"🗺️  Total maps: {Colors.GREEN}{self.session_maps_completed}{Colors.END}")
                print(f"💰 Total value: {Colors.GOLD}{fmt(self.session_total_value)}ex{Colors.END}")
            print("Bye.")


if __name__ == "__main__":
    tracker = PoEStatsTracker(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        character_name=CHAR_TO_CHECK,
        client_log_path=CLIENT_LOG,
        debug_enabled=DEBUG_ENABLED,
        output_mode=OUTPUT_MODE
    )
    
    if DEBUG_ENABLED:
        print(f"[DEBUG MODE] Enabled - Debug to file: {DEBUG_TO_FILE}, Show summary: {DEBUG_SHOW_SUMMARY}")
    
    tracker.run()
