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
    YELLOW = '\033[93m'  # Same as GOLD for compatibility
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
        self._display_basic_info(character_name, session_id, output_mode)
        self._display_hotkey_help()
        self._display_session_footer()
    
    def _display_basic_info(self, character_name, session_id, output_mode):
        """Display basic tracker information"""
        print(f"🎮 Using character: {Colors.CYAN}{character_name}{Colors.END}")
        print(f"📋 Output mode: {Colors.BOLD}{output_mode.upper()}{Colors.END}")
        print(f"🆔 Session ID: {Colors.GRAY}{session_id[:8]}...{Colors.END}")
    
    def _display_hotkey_help(self):
        """Display hotkey help information"""
        print(f"⌨️  Hotkeys: {Colors.GREEN}F2{Colors.END}=PRE | {Colors.MAGENTA}Ctrl+F2{Colors.END}=Exp.PRE | "
              f"{Colors.GREEN}F3{Colors.END}=POST | {Colors.GREEN}F4{Colors.END}=Debug")
        print(f"         {Colors.GREEN}F5{Colors.END}=Inventory | {Colors.GREEN}F6{Colors.END}=New Session | "
              f"{Colors.GREEN}F7{Colors.END}=Session Stats | {Colors.GREEN}F8{Colors.END}=Output Mode")
        print(f"         {Colors.RED}Ctrl+Esc{Colors.END}=Quit | {Colors.MAGENTA}Ctrl+F2{Colors.END}=Experimental waystone mode")
    
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
            # Get price data for all items
            price_data = self._get_price_data(added, removed)
            
            # Display prices based on current mode
            self._display_prices_by_mode(price_data)
            
            # Calculate and display net value
            return self._calculate_and_display_net_value(price_data)
                
        except Exception as pe:
            print(f"❌ [VALUE] price-check error: {pe}")
            return None
    
    def _get_price_data(self, added, removed):
        """Get and organize price data for items"""
        added_rows, (add_c, add_e) = valuate_items_raw(added)
        removed_rows, (rem_c, rem_e) = valuate_items_raw(removed)
        
        # Filter valuable items for normal mode
        valuable_added = [r for r in added_rows if (r['chaos_total'] or 0) > 0.01 or (r['ex_total'] or 0) > 0.01]
        valuable_removed = [r for r in removed_rows if (r['chaos_total'] or 0) > 0.01 or (r['ex_total'] or 0) > 0.01]
        
        return {
            'added_rows': added_rows,
            'removed_rows': removed_rows,
            'valuable_added': valuable_added,
            'valuable_removed': valuable_removed,
            'totals': {'add_c': add_c, 'add_e': add_e, 'rem_c': rem_c, 'rem_e': rem_e}
        }
    
    def _display_prices_by_mode(self, price_data):
        """Display prices based on current output mode"""
        if self.output_mode == "normal":
            self._display_normal_mode_prices(price_data['valuable_added'], price_data['valuable_removed'])
        else:  # comprehensive mode
            self._display_comprehensive_mode_prices(price_data['added_rows'], price_data['removed_rows'])
    
    def _calculate_and_display_net_value(self, price_data):
        """Calculate net value and display it"""
        totals = price_data['totals']
        net_c = (totals['add_c'] or 0) - (totals['rem_c'] or 0)
        net_e = None
        if totals['add_e'] is not None and totals['rem_e'] is not None:
            net_e = (totals['add_e'] or 0) - (totals['rem_e'] or 0)
        
        return self._display_net_value(net_c, net_e)
    
    def _display_normal_mode_prices(self, valuable_added, valuable_removed):
        """Display prices in normal mode (only valuable items)"""
        if valuable_added:
            print(f"\n💰 {Colors.BOLD}Valuable Loot:{Colors.END}")
            # Get smart emojis for added items
            item_emojis = self._get_smart_emojis_for_items(valuable_added)
            for r in valuable_added:
                emoji = item_emojis.get(r['name'])
                print(self._format_item_value_line(r, "+", Colors.GREEN, emoji))
        
        if valuable_removed:
            print(f"\n💸 {Colors.BOLD}Valuable Items Used:{Colors.END}")
            # Get smart emojis for removed items  
            item_emojis = self._get_smart_emojis_for_items(valuable_removed)
            for r in valuable_removed:
                emoji = item_emojis.get(r['name'])
                print(self._format_item_value_line(r, "-", Colors.RED, emoji))
    
    def _display_comprehensive_mode_prices(self, added_rows, removed_rows):
        """Display prices in comprehensive mode (all items)"""
        print(f"\n💰 {Colors.BOLD}[VALUE] Added:{Colors.END}")
        # Get smart emojis for added items
        added_emojis = self._get_smart_emojis_for_items(added_rows)
        for r in added_rows:
            emoji = added_emojis.get(r['name'])
            print(self._format_comprehensive_item_line(r, "+", Colors.GREEN, emoji))

        print(f"\n💸 {Colors.BOLD}[VALUE] Removed:{Colors.END}")
        # Get smart emojis for removed items
        removed_emojis = self._get_smart_emojis_for_items(removed_rows)
        for r in removed_rows:
            emoji = removed_emojis.get(r['name'])
            print(self._format_comprehensive_item_line(r, "-", Colors.RED, emoji))
    
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
        print(f"\n{'-'*50}")
        print(f"✅ {Colors.GRAY}Map completed{Colors.END}")
        print(f"{'-'*50}")
    
    def display_session_header(self, session_id, start_time_str):
        """Display new session header"""
        print(f"\n🎬 {Colors.BOLD}NEW SESSION STARTED{Colors.END}")
        print(f"🆔 Session ID: {Colors.CYAN}{session_id[:8]}...{Colors.END}")
        print(f"🕐 Started at: {Colors.GRAY}{start_time_str}{Colors.END}")
        self._display_session_footer()
    
    def display_session_stats(self, session_id, hours, minutes, seconds, maps_completed, 
                             total_value, session_stats, custom_header=None):
        """Display comprehensive session statistics"""
        header = custom_header if custom_header else "CURRENT SESSION STATS"
        print(f"\n📊 {Colors.BOLD}{header}{Colors.END}")
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
        
        self._display_session_footer()
    
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
        
        print(f"🎯 {Colors.GREEN}Ready for next map!{Colors.END}")
        self._display_session_footer()
    
    def _display_session_footer(self):
        """Display a beautiful PoE2-style footer with timestamp using theme system"""
        from datetime import datetime
        from config import Config
        
        try:
            # Get current theme configuration
            theme_config = Config.get_ascii_theme_config()
            
            # Get current timestamp in configured format (with Unicode fallback)
            try:
                timestamp = datetime.now().strftime(theme_config["timestamp_format"])
            except UnicodeEncodeError:
                # Fallback to safe ASCII timestamp if Unicode fails
                timestamp = datetime.now().strftime("%H:%M:%S • %d.%m.%Y")
                print(f"Warning: Theme timestamp format contains unsupported characters, using fallback")
            
            # Get colors from theme (with fallbacks for unknown colors)
            deco_color = getattr(Colors, theme_config.get("decoration_color", "CYAN"), Colors.CYAN)
            middle_color = getattr(Colors, theme_config.get("middle_color", "CYAN"), Colors.CYAN)
            timestamp_color = getattr(Colors, theme_config.get("timestamp_color", "GRAY"), Colors.GRAY)
            
            # Apply colors to decorations (with Unicode fallback)
            left_raw = theme_config["left_decoration"]
            right_raw = theme_config["right_decoration"]
            
            left_deco = f"{deco_color}{left_raw}{Colors.END}"
            right_deco = f"{deco_color}{right_raw}{Colors.END}"
            
            # Calculate padding for centered timestamp
            total_width = theme_config["total_width"]
            timestamp_text = f" {timestamp} "
            deco_width = len(left_raw) + len(right_raw)  # Width without color codes
            available_width = total_width - len(timestamp_text) - deco_width
            padding = max(0, available_width // 2)
            
            # Create the beautiful footer line
            middle_char = theme_config["middle_char"]
            middle_line = f"{middle_color}{middle_char * padding}{Colors.END}"
            footer_line = f"{left_deco}{middle_line}{timestamp_color}{timestamp_text}{Colors.END}{middle_line}{right_deco}"
            
            print(f"\n{footer_line}\n")
            
        except UnicodeEncodeError as e:
            # Ultimate fallback to simple ASCII footer
            print(f"\n{Colors.GRAY}--- {datetime.now().strftime('%H:%M:%S')} ---{Colors.END}\n")
            print(f"Warning: Theme contains unsupported Unicode characters: {e}")
        except Exception as e:
            # Fallback for any other theme-related errors
            print(f"\n{Colors.GRAY}--- {datetime.now().strftime('%H:%M:%S')} ---{Colors.END}\n")
            print(f"Warning: Theme error: {e}")
    
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
        print(f"❌ [{error_type}] Error: {error_message}")
    
    def display_current_inventory_value(self, inventory_items):
        """Display value analysis of current inventory with smart icons"""
        try:
            from price_check_poe2 import valuate_items_raw
            rows, (total_c, total_e) = valuate_items_raw(inventory_items)
            
            print(f"\n💼 {Colors.BOLD}CURRENT INVENTORY VALUE{Colors.END}")
            
            # Filter valuable items for display
            valuable_items = [r for r in rows if (r['chaos_total'] or 0) > 0.01 or (r['ex_total'] or 0) > 0.01]
            
            if valuable_items:
                print(f"\n💰 {Colors.BOLD}Valuable Items:{Colors.END}")
                
                # Get smart emojis for valuable items - use original inventory items for icon analysis
                item_emojis = self._get_smart_emojis_for_current_inventory(inventory_items, valuable_items)
                
                for r in valuable_items:
                    ex_str = f" | {Colors.GOLD}{fmt(r['ex_total'])}ex{Colors.END}" if r['ex_total'] and r['ex_total'] > 0.01 else ""
                    emoji = item_emojis.get(r['name'], '💎')  # fallback to diamond
                    print(f"  {emoji} {Colors.WHITE}{r['name']}{Colors.END} "
                          f"{Colors.GRAY}x{r['qty']} [{r.get('category') or 'n/a'}]{Colors.END} "
                          f"=> {Colors.GOLD}{fmt(r['chaos_total'])}c{Colors.END}{ex_str}")
                
                # Display totals
                print(f"\n🏆 {Colors.BOLD}Total Inventory Value:{Colors.END}")
                print(f"💰 Chaos: {Colors.GOLD}{fmt(total_c)}c{Colors.END}")
                if total_e is not None and total_e > 0.01:
                    print(f"💰 Exalted: {Colors.GOLD}{fmt(total_e)}ex{Colors.END}")
                
                # Show percentage of valuable vs total items
                valuable_count = len(valuable_items)
                total_count = len([r for r in rows if r['qty'] > 0])
                if total_count > valuable_count:
                    worthless_count = total_count - valuable_count
                    print(f"\n📊 {Colors.GRAY}Items: {valuable_count} valuable, {worthless_count} worthless{Colors.END}")
            else:
                print(f"\n💰 {Colors.GRAY}No valuable items found in current inventory{Colors.END}")
                total_items = len([r for r in rows if r['qty'] > 0])
                print(f"📦 Total items: {total_items}")
            
            self._display_session_footer()
                
        except Exception as e:
            print(f"❌ [INVENTORY VALUE] error: {e}")
    
    def display_experimental_waystone_info(self, waystone_info):
        """Display experimental waystone information with prefixes"""
        if not waystone_info:
            print("⚠️  No waystone information available")
            return
        
        print(f"🧪 {Colors.BOLD}EXPERIMENTAL MODE{Colors.END} - Waystone Analysis")
        print(f"🗺️  {Colors.BOLD}{waystone_info['name']}{Colors.END} "
              f"{Colors.GRAY}(Tier {waystone_info['tier']}){Colors.END}")
        
        # Display prefixes (explicit mods)
        if waystone_info['prefixes']:
            print(f"⚗️  {Colors.BOLD}Prefixes ({len(waystone_info['prefixes'])}){Colors.END}:")
            for i, prefix in enumerate(waystone_info['prefixes'], 1):
                print(f"   {Colors.MAGENTA}{i}.{Colors.END} {Colors.WHITE}{prefix}{Colors.END}")
        else:
            print(f"⚗️  {Colors.GRAY}No prefixes found{Colors.END}")
        
        # Display suffixes (implicit mods)
        if waystone_info['suffixes']:
            print(f"🔮 {Colors.BOLD}Suffixes ({len(waystone_info['suffixes'])}){Colors.END}:")
            for i, suffix in enumerate(waystone_info['suffixes'], 1):
                print(f"   {Colors.CYAN}{i}.{Colors.END} {Colors.WHITE}{suffix}{Colors.END}")
        else:
            print(f"🔮 {Colors.GRAY}No suffixes found{Colors.END}")
        
        # Display area modifiers (the bonus stats from properties)
        if waystone_info['area_modifiers']:
            print(f"📊 {Colors.BOLD}Area Modifiers ({len(waystone_info['area_modifiers'])}){Colors.END}:")
            for key, modifier in waystone_info['area_modifiers'].items():
                print(f"   {Colors.GREEN}▶{Colors.END} {Colors.WHITE}{modifier['display']}{Colors.END}")
        else:
            print(f"📊 {Colors.GRAY}No area modifiers found{Colors.END}")
        
        print(f"{Colors.GRAY}Source: Waystone from inventory position (0,0){Colors.END}")
    
    def display_info_message(self, message):
        """Display general info messages"""
        print(message)
    
    def display_icon_system_stats(self):
        """Display statistics about the smart icon system"""
        try:
            from smart_icon_system import get_smart_icon_system
            icon_system = get_smart_icon_system()
            stats = icon_system.get_system_stats()
            
            print(f"\n🎨 {Colors.BOLD}SMART ICON SYSTEM STATS{Colors.END}")
            print(f"📁 Cached Icons: {Colors.GREEN}{stats['cached_icons']}{Colors.END}")
            print(f"💾 Cache Size: {Colors.CYAN}{stats['cache_size_mb']:.1f} MB{Colors.END}")
            print(f"🎨 Analyzed Colors: {Colors.YELLOW}{stats['analyzed_colors']}{Colors.END}")
            print(f"📂 Cache Directory: {Colors.GRAY}{stats.get('cache_dir', 'N/A')}{Colors.END}")
            self._display_session_footer()
            
        except Exception as e:
            print(f"❌ Could not get icon system stats: {e}")
    
    def test_smart_icons(self, sample_items=None):
        """Test the smart icon system with sample items"""
        if not sample_items:
            # Create some sample items for testing
            sample_items = [
                {'typeLine': 'Chaos Orb', 'icon': 'https://web.poecdn.com/image/Art/2DItems/Currency/CurrencyRerollRare.png'},
                {'typeLine': 'Exalted Orb', 'icon': 'https://web.poecdn.com/image/Art/2DItems/Currency/CurrencyAddModToRare.png'},
                {'typeLine': 'Divine Orb', 'icon': 'https://web.poecdn.com/image/Art/2DItems/Currency/CurrencyModValues.png'},
                {'typeLine': 'Iron Sword', 'icon': None},  # Test fallback
                {'typeLine': 'Test Item', 'icon': 'invalid_url'}  # Test error handling
            ]
        
        try:
            from smart_icon_system import get_smart_icon_system
            icon_system = get_smart_icon_system()
            
            print(f"\n🧪 {Colors.BOLD}TESTING SMART ICON SYSTEM{Colors.END}")
            
            for item in sample_items:
                emoji = icon_system.get_item_emoji(item, enable_downloads=True)
                icon_status = "📡" if item.get('icon') else "🔄"
                print(f"  {icon_status} {emoji} {Colors.WHITE}{item['typeLine']}{Colors.END}")
            
            self._display_session_footer()
            
        except Exception as e:
            print(f"❌ Smart icon test failed: {e}")
            import traceback
            traceback.print_exc()
    
    def display_ascii_themes(self):
        """Display available ASCII themes"""
        from config import Config
        print(f"\n🎨 {Colors.BOLD}ASCII THEMES{Colors.END}")
        themes_info = Config.list_ascii_themes()
        print(themes_info)
        print(f"\nTo change theme, use: Config.set_ascii_theme('theme_name')")
        self._display_session_footer()
    
    def change_ascii_theme(self, theme_name):
        """Change the ASCII theme and show preview"""
        from config import Config
        
        if Config.set_ascii_theme(theme_name):
            print(f"🎨 Theme changed to: {Colors.BOLD}{theme_name}{Colors.END}")
            preview = Config.preview_ascii_theme(theme_name)
            print(f"Preview:\n{preview}")
            self._display_session_footer()
            return True
        else:
            print(f"❌ Theme '{theme_name}' not found")
            self.display_ascii_themes()
            return False
    
    def _get_smart_emojis_for_items(self, items_data):
        """
        Get smart emojis for a list of items using the icon system
        
        Args:
            items_data: List of item data dicts (from price analysis)
            
        Returns:
            dict: Mapping of item names to emojis
        """
        try:
            # Try to get the smart icon system
            from smart_icon_system import get_smart_icon_system
            icon_system = get_smart_icon_system()
            
            # Convert price analysis items back to API format for icon analysis
            api_items = []
            for item in items_data:
                # Create a mock API item dict
                api_item = {
                    'typeLine': item['name'],
                    'name': item['name'],
                    # Add more fields if available from original data
                }
                api_items.append(api_item)
            
            # Get emojis (limit downloads to avoid delays)
            return icon_system.batch_analyze_items(api_items, max_downloads=5)
            
        except Exception as e:
            from config import Config
            if Config.DEBUG_ENABLED:
                print(f"[ICON] Warning: Could not get smart emojis: {e}")
            # Fallback to simple emojis
            return {item['name']: '⚪' for item in items_data}
    
    def _get_smart_emojis_for_current_inventory(self, inventory_items, valuable_items):
        """
        Get smart emojis for current inventory items (has access to original API data)
        
        Args:
            inventory_items: Original inventory items from API (with icon URLs)
            valuable_items: Filtered valuable items from price analysis
            
        Returns:
            dict: Mapping of item names to emojis
        """
        try:
            from smart_icon_system import get_smart_icon_system
            icon_system = get_smart_icon_system()
            
            # Create mapping of valuable item names
            valuable_names = {item['name'] for item in valuable_items}
            
            # Filter inventory items to only valuable ones
            valuable_inventory_items = [
                item for item in inventory_items 
                if (item.get('typeLine') or item.get('name', '')) in valuable_names
            ]
            
            # Only show debug message in debug mode
            from config import Config
            if Config.DEBUG_ENABLED:
                print(f"[ICON] Analyzing {len(valuable_inventory_items)} valuable items...")
            
            # Get emojis using original API data (has icon URLs)
            result = icon_system.batch_analyze_items(valuable_inventory_items, max_downloads=10)
            
            return result
            
        except Exception as e:
            import traceback
            from config import Config
            if Config.DEBUG_ENABLED:
                print(f"[ICON] Warning: Could not get smart emojis for inventory: {e}")
                print(f"[ICON] Full traceback:")
                traceback.print_exc()
            # Fallback to simple emojis
            return {item['name']: '💎' for item in valuable_items}
    
    # Helper methods for reducing code duplication
    def _format_ex_value(self, ex_value):
        """Format exalted value display string"""
        if ex_value and ex_value > 0.01:
            return f" | {Colors.GOLD}{fmt(ex_value)}ex{Colors.END}"
        return ""
    
    def _format_item_value_line(self, item_data, prefix_symbol, prefix_color, item_emoji=None):
        """Format a single item value line with consistent styling"""
        ex_str = self._format_ex_value(item_data.get('ex_total'))
        emoji_str = f"{item_emoji} " if item_emoji else ""
        return (f"  {prefix_color}{prefix_symbol}{Colors.END} {emoji_str}{Colors.WHITE}{item_data['name']}{Colors.END} "
                f"{Colors.GRAY}x{item_data['qty']}{Colors.END} => {Colors.GOLD}{fmt(item_data['chaos_total'])}c{Colors.END}{ex_str}")
    
    def _format_comprehensive_item_line(self, item_data, prefix_symbol, prefix_color, item_emoji=None):
        """Format comprehensive mode item line with category info"""
        ex_str = self._format_ex_value(item_data.get('ex_total'))
        category = item_data.get('category') or 'n/a'
        emoji_str = f"{item_emoji} " if item_emoji else ""
        return (f"  {prefix_color}{prefix_symbol}{Colors.END} {emoji_str}{item_data['name']} {Colors.GRAY}[{category}]{Colors.END} "
                f"x{item_data['qty']} => {Colors.GOLD}{fmt(item_data['chaos_total'])}c{Colors.END}{ex_str}")