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
from poe_logging import log_run
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
DEBUG_TO_FILE = True  # Set to False to only show debug in console
DEBUG_SHOW_SUMMARY = True  # Show item summary instead of full JSON dump

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
    def __init__(self, client_id, client_secret, character_name, client_log_path, debug_enabled=False):
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
        
        # Setup paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(script_dir, 'cat64x64.png')
        self.log_file = Path(script_dir) / "runs.jsonl"
        
        # Initialize debugger
        self.debugger = InventoryDebugger(debug_enabled=debug_enabled)
    
    def initialize(self):
        """Initialize the tracker with API token and character validation"""
        self.token = get_token(self.client_id, self.client_secret)
        chars = get_characters(self.token)
        
        if not chars.get("characters"):
            print("No characters found")
            raise SystemExit
        
        notify('Starting DillaPoE2Stat', f'Watching character: {self.character_name}', 
               icon=f'file://{self.icon_path}')
        print(f"Using character: {self.character_name}")
        print("Hotkeys:  F2 = PRE snapshot   |   F3 = POST snapshot + diff   |   Esc = quit")
    
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
            # Record the start time for map runtime calculation
            self.map_start_time = time.time()
            
            self.pre_inventory = snapshot_inventory(self.token, self.character_name)
            print(f"[PRE] captured: {len(self.pre_inventory)} items")
            
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
                print(f"[MAP] {self.current_map_info['map_name']} (T{self.current_map_info['level']}, seed {self.current_map_info['seed']})")
            
            mapname = self.current_map_info["map_name"] if self.current_map_info else "Unknown"
            notify('Hallo Dilla!', f'Starting Map Run! {mapname}')
        except Exception as e:
            print("[PRE] error:", e)
    
    def display_inventory_changes(self, added, removed):
        """Display added and removed items"""
        print(f"\nAdded items ({len(added)}):")
        for item in added:
            stack = f" x{item['stackSize']}" if item.get("stackSize") else ""
            print(" +", item.get("typeLine"), stack, "@", (item.get("x"), item.get("y")))

        print(f"\nRemoved items ({len(removed)}):")
        for item in removed:
            stack = f" x{item['stackSize']}" if item.get("stackSize") else ""
            print(" -", item.get("typeLine"), stack)
    
    def display_price_analysis(self, added, removed):
        """Display price analysis for added/removed items"""
        try:
            added_rows, (add_c, add_e) = valuate_items_raw(added)
            removed_rows, (rem_c, rem_e) = valuate_items_raw(removed)

            print("\n[VALUE] Added:")
            for r in added_rows:
                print(f" + {r['name']} [{r.get('category') or 'n/a'}] x{r['qty']}  "
                    f"=> {fmt(r['chaos_total'])}c"
                    f"{'' if r['ex_total'] is None else ' | ' + fmt(r['ex_total']) + 'ex'}")

            print("\n[VALUE] Removed:")
            for r in removed_rows:
                print(f" - {r['name']} [{r.get('category') or 'n/a'}] x{r['qty']}  "
                    f"=> {fmt(r['chaos_total'])}c"
                    f"{'' if r['ex_total'] is None else ' | ' + fmt(r['ex_total']) + 'ex'}")

            net_c = (add_c or 0) - (rem_c or 0)
            net_e = None
            if add_e is not None and rem_e is not None:
                net_e = (add_e or 0) - (rem_e or 0)

            print(f"\n[VALUE] Totals:  +{fmt(add_c)}c  /  -{fmt(rem_c)}c  =>  Net {fmt(net_c)}c")
            if net_e is not None:
                print(f"                 +{fmt(add_e)}ex /  -{fmt(rem_e)}ex =>  Net {fmt(net_e)}ex")
                self.map_value = net_e
        except Exception as pe:
            print("[VALUE] price-check error:", pe)
    
    def take_post_snapshot(self):
        """Take POST-map inventory snapshot and analyze differences"""
        if self.pre_inventory is None:
            print("[POST] no PRE snapshot yet. Press F2 first.")
            return
        
        self.rate_limit()
        try:
            post_inventory = snapshot_inventory(self.token, self.character_name)
            print(f"[POST] captured: {len(post_inventory)} items")
            
            # Debug: dump post inventory and comparison
            if DEBUG_SHOW_SUMMARY:
                self.debugger.dump_item_summary(post_inventory, "[POST-SUMMARY]")
            else:
                self.debugger.dump_inventory_to_console(post_inventory, "[POST-DEBUG]")
            
            if DEBUG_TO_FILE:
                metadata = {
                    "character": self.character_name,
                    "snapshot_type": "POST",
                    "map_info": self.current_map_info
                }
                self.debugger.dump_inventory_to_file(post_inventory, "post_inventory", metadata)
            
            # Calculate map runtime
            map_runtime = None
            if self.map_start_time is not None:
                map_runtime = time.time() - self.map_start_time
                minutes = int(map_runtime // 60)
                seconds = int(map_runtime % 60)
                print(f"[RUNTIME] Map completed in {minutes}m {seconds}s")
            
            added, removed = diff_inventories(self.pre_inventory, post_inventory)
            
            # Debug: show inventory comparison
            self.debugger.compare_inventories(self.pre_inventory, post_inventory)
            
            self.display_inventory_changes(added, removed)
            self.display_price_analysis(added, removed)
            
            print("\n=== ready for next map ===\n")
            notify('Hallo Dilla!', 'Map Run done!' + (f', Value: {fmt(self.map_value)}ex' if self.map_value else '') + 
                   (f', Time: {minutes}m {seconds}s' if map_runtime else ''))
            
            log_run(self.character_name, added, removed, self.current_map_info, self.map_value, self.log_file, map_runtime)
            
        except Exception as e:
            print("[POST] error:", e)
        finally:
            self.pre_inventory = None  # reset for next run
            self.map_start_time = None  # reset start time
    
    def toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        current_state = self.debugger.debug_enabled
        self.debugger.set_debug_enabled(not current_state)
    
    def setup_hotkeys(self):
        """Setup keyboard hotkeys"""
        keyboard.add_hotkey('f2', self.take_pre_snapshot)
        keyboard.add_hotkey('f3', self.take_post_snapshot)
        keyboard.add_hotkey('f4', self.toggle_debug_mode)  # F4 to toggle debug mode
    
    def run(self):
        """Main application loop"""
        self.initialize()
        self.setup_hotkeys()
        
        try:
            keyboard.wait('esc')
        except KeyboardInterrupt:
            pass
        finally:
            print("Bye.")


if __name__ == "__main__":
    tracker = PoEStatsTracker(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        character_name=CHAR_TO_CHECK,
        client_log_path=CLIENT_LOG,
        debug_enabled=DEBUG_ENABLED
    )
    
    if DEBUG_ENABLED:
        print(f"[DEBUG MODE] Enabled - Debug to file: {DEBUG_TO_FILE}, Show summary: {DEBUG_SHOW_SUMMARY}")
    
    tracker.run()
