"""
Display and formatting utilities for PoE Stats Tracker
Handles all console output, colors, and formatting logic
"""

from price_check_poe2 import valuate_items_raw, fmt


class Colors:
    """ANSI color codes for console output"""
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


class DisplayManager:
    """Handles all display and formatting operations"""
    
    def __init__(self, output_mode="normal"):
        self.output_mode = output_mode
    
    def set_output_mode(self, mode):
        """Set output mode: 'normal' or 'comprehensive'"""
        self.output_mode = mode
    
    def display_startup_info(self, character_name, session_id, output_mode):
        """Display startup information"""
        print(f"🎮 Using character: {Colors.CYAN}{character_name}{Colors.END}")
        print(f"📋 Output mode: {Colors.BOLD}{output_mode.upper()}{Colors.END}")
        print(f"🆔 Session ID: {Colors.GRAY}{session_id[:8]}...{Colors.END}")
        print(f"⌨️  Hotkeys: {Colors.GREEN}F2{Colors.END}=PRE | {Colors.GREEN}F3{Colors.END}=POST | "
              f"{Colors.GREEN}F4{Colors.END}=Debug | {Colors.GREEN}F6{Colors.END}=New Session | "
              f"{Colors.GREEN}F7{Colors.END}=Session Stats | {Colors.RED}Esc{Colors.END}=Quit")
    
    def display_map_info(self, map_info):
        """Display current map information"""
        if map_info:
            print(f"🗺️  {Colors.BOLD}{map_info['map_name']}{Colors.END} "
                  f"{Colors.GRAY}(T{map_info['level']}, seed {map_info['seed']}){Colors.END}")
    
    def display_runtime(self, runtime_seconds):
        """Display map runtime"""
        minutes = int(runtime_seconds // 60)
        seconds = int(runtime_seconds % 60)
        print(f"\n⏱️  {Colors.BOLD}Runtime:{Colors.END} {Colors.CYAN}{minutes}m {seconds}s{Colors.END}")
    
    def display_inventory_changes(self, added, removed):
        """Display added and removed items"""
        if self.output_mode == "comprehensive":
            print(f"\n📥 Added items ({len(added)}):")
            for item in added:
                stack = f" x{item['stackSize']}" if item.get("stackSize") else ""
                print(f"  {Colors.GREEN}+{Colors.END} {item.get('typeLine')}{stack} "
                      f"@ {Colors.GRAY}({item.get('x')},{item.get('y')}){Colors.END}")

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
                self._display_normal_mode_prices(valuable_added, valuable_removed)
            else:  # comprehensive mode
                self._display_comprehensive_mode_prices(added_rows, removed_rows)

            # Calculate and display net value
            net_c = (add_c or 0) - (rem_c or 0)
            net_e = None
            if add_e is not None and rem_e is not None:
                net_e = (add_e or 0) - (rem_e or 0)

            return self._display_net_value(net_c, net_e)
                
        except Exception as pe:
            print(f"❌ [VALUE] price-check error: {pe}")
            return None
    
    def _display_normal_mode_prices(self, valuable_added, valuable_removed):
        """Display prices in normal mode (only valuable items)"""
        if valuable_added:
            print(f"\n💰 {Colors.BOLD}Valuable Loot:{Colors.END}")
            for r in valuable_added:
                ex_str = f" | {Colors.GOLD}{fmt(r['ex_total'])}ex{Colors.END}" if r['ex_total'] and r['ex_total'] > 0.01 else ""
                print(f"  {Colors.GREEN}+{Colors.END} {Colors.WHITE}{r['name']}{Colors.END} "
                      f"{Colors.GRAY}x{r['qty']}{Colors.END} => {Colors.GOLD}{fmt(r['chaos_total'])}c{Colors.END}{ex_str}")
        
        if valuable_removed:
            print(f"\n💸 {Colors.BOLD}Valuable Items Used:{Colors.END}")
            for r in valuable_removed:
                ex_str = f" | {Colors.GOLD}{fmt(r['ex_total'])}ex{Colors.END}" if r['ex_total'] and r['ex_total'] > 0.01 else ""
                print(f"  {Colors.RED}-{Colors.END} {Colors.WHITE}{r['name']}{Colors.END} "
                      f"{Colors.GRAY}x{r['qty']}{Colors.END} => {Colors.GOLD}{fmt(r['chaos_total'])}c{Colors.END}{ex_str}")
    
    def _display_comprehensive_mode_prices(self, added_rows, removed_rows):
        """Display prices in comprehensive mode (all items)"""
        print(f"\n💰 {Colors.BOLD}[VALUE] Added:{Colors.END}")
        for r in added_rows:
            ex_str = f" | {Colors.GOLD}{fmt(r['ex_total'])}ex{Colors.END}" if r['ex_total'] is not None else ""
            print(f"  {Colors.GREEN}+{Colors.END} {r['name']} {Colors.GRAY}[{r.get('category') or 'n/a'}]{Colors.END} "
                  f"x{r['qty']} => {Colors.GOLD}{fmt(r['chaos_total'])}c{Colors.END}{ex_str}")

        print(f"\n💸 {Colors.BOLD}[VALUE] Removed:{Colors.END}")
        for r in removed_rows:
            ex_str = f" | {Colors.GOLD}{fmt(r['ex_total'])}ex{Colors.END}" if r['ex_total'] is not None else ""
            print(f"  {Colors.RED}-{Colors.END} {r['name']} {Colors.GRAY}[{r.get('category') or 'n/a'}]{Colors.END} "
                  f"x{r['qty']} => {Colors.GOLD}{fmt(r['chaos_total'])}c{Colors.END}{ex_str}")
    
    def _display_net_value(self, net_c, net_e):
        """Display net value and return the exalt value"""
        if net_c > 0.01 or (net_e and net_e > 0.01):
            print(f"\n🏆 {Colors.BOLD}Net Value:{Colors.END} {Colors.GOLD}{fmt(net_c)}c{Colors.END}", end="")
            if net_e is not None and net_e > 0.01:
                print(f" | {Colors.GOLD}{fmt(net_e)}ex{Colors.END}")
            else:
                print()
            return net_e
        else:
            print(f"\n💰 {Colors.GRAY}No valuable loot this run{Colors.END}")
            return None
    
    def display_completion_separator(self):
        """Display completion separator"""
        print(f"\n{'='*50}")
        print(f"🎯 {Colors.GREEN}Ready for next map!{Colors.END}")
        print(f"{'='*50}\n")
    
    def display_session_header(self, session_id, start_time_str):
        """Display new session header"""
        print(f"\n🎬 {Colors.BOLD}NEW SESSION STARTED{Colors.END}")
        print(f"🆔 Session ID: {Colors.CYAN}{session_id[:8]}...{Colors.END}")
        print(f"🕐 Started at: {Colors.GRAY}{start_time_str}{Colors.END}")
        print(f"{'='*50}\n")
    
    def display_session_stats(self, session_id, hours, minutes, seconds, maps_completed, 
                             total_value, session_stats):
        """Display comprehensive session statistics"""
        print(f"\n📊 {Colors.BOLD}CURRENT SESSION STATS{Colors.END}")
        print(f"🆔 Session ID: {Colors.CYAN}{session_id[:8]}...{Colors.END}")
        print(f"⏱️  Total Time: {Colors.CYAN}{hours}h {minutes}m {seconds}s{Colors.END}")
        print(f"🗺️  Maps Completed: {Colors.GREEN}{maps_completed}{Colors.END}")
        
        if total_value > 0:
            print(f"💰 Total Value: {Colors.GOLD}{fmt(total_value)}ex{Colors.END}")
            if maps_completed > 0:
                avg_value = total_value / maps_completed
                print(f"📈 Average per Map: {Colors.GOLD}{fmt(avg_value)}ex{Colors.END}")
        else:
            print(f"💰 Total Value: {Colors.GRAY}0ex{Colors.END}")
        
        if session_stats['maps']:
            self._display_recent_maps(session_stats['maps'])
        
        print(f"{'='*50}\n")
    
    def _display_recent_maps(self, maps):
        """Display recent maps from session"""
        print(f"\n📜 {Colors.BOLD}Recent Maps:{Colors.END}")
        for i, map_run in enumerate(maps[-5:], 1):  # Show last 5 maps
            map_name = map_run['map']['name']
            map_level = map_run['map']['level']
            map_value = map_run.get('map_value', 0) or 0
            runtime = map_run.get('map_runtime')
            
            time_str = f"{int(runtime//60)}m {int(runtime%60)}s" if runtime else "N/A"
            value_str = f"{fmt(map_value)}ex" if map_value > 0.01 else "0ex"
            
            print(f"  {i}. {Colors.WHITE}{map_name}{Colors.END} {Colors.GRAY}(T{map_level}){Colors.END} "
                  f"- {Colors.CYAN}{time_str}{Colors.END} - {Colors.GOLD}{value_str}{Colors.END}")
    
    def display_session_progress(self, session_time_str, maps_completed, total_value, 
                                avg_value=None, avg_time=None, runtime_seconds=None):
        """Display session progress after each map completion"""
        print(f"\n📈 {Colors.BOLD}SESSION PROGRESS{Colors.END}")
        print(f"🕐 Session Time: {Colors.CYAN}{session_time_str}{Colors.END} | "
              f"🗺️  Maps: {Colors.GREEN}{maps_completed}{Colors.END} | "
              f"💰 Total Value: {Colors.GOLD}{fmt(total_value)}ex{Colors.END}")
        
        if avg_value is not None and avg_time is not None:
            print(f"📊 Avg/Map: {Colors.GOLD}{fmt(avg_value)}ex{Colors.END} | "
                  f"⏱️  Avg Time: {Colors.CYAN}{avg_time:.1f}m{Colors.END}")
        
        print(f"{'-'*30}")
    
    def display_session_completion(self, maps_completed, total_value):
        """Display session completion summary"""
        print(f"\n📊 {Colors.BOLD}Session completed!{Colors.END}")
        print(f"🗺️  Total maps: {Colors.GREEN}{maps_completed}{Colors.END}")
        print(f"💰 Total value: {Colors.GOLD}{fmt(total_value)}ex{Colors.END}")
    
    def display_inventory_count(self, count, prefix):
        """Display inventory item count"""
        if self.output_mode == "comprehensive":
            print(f"📦 {prefix} captured: {count} items")
    
    def display_mode_change(self, new_mode):
        """Display output mode change"""
        print(f"🔄 Output mode changed to: {Colors.BOLD}{new_mode.upper()}{Colors.END}")
    
    def display_error(self, error_type, error_message):
        """Display error messages"""
        print(f"❌ [{error_type}] error: {error_message}")
    
    def display_info_message(self, message):
        """Display general info messages"""
        print(message)