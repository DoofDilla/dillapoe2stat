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
    BROWN = '\033[38;5;137m'  # Light brown for main numbers (was 130)
    DARK_BROWN = '\033[38;5;52m'  # Much darker brown for decimals (was 88)
    BOLD = '\033[1m'
    END = '\033[0m'


class DisplayManager:
    """Handles all display and formatting operations"""
    
    def __init__(self, output_mode="normal"):
        self.output_mode = output_mode
        # Import config for table settings
        from config import Config
        self.config = Config()
        # Import config for table settings
        from config import Config
        self.config = Config()
    
    def set_output_mode(self, mode):
        """Set output mode: 'normal' or 'comprehensive'"""
        self.output_mode = mode
    
    def _display_themed_banner(self, content=None, use_timestamp=False):
        """Display a beautiful themed banner with content or timestamp"""
        from datetime import datetime
        
        try:
            # Get current theme configuration
            theme_config = self.config.get_ascii_theme_config()
            if not theme_config:
                # Fallback for no theme
                display_text = content if content else datetime.now().strftime("%H:%M:%S • %d.%m.%Y")
                print(f"=== {display_text} ===")
                return
            
            # Determine content to display
            if use_timestamp:
                try:
                    content_text = datetime.now().strftime(theme_config["timestamp_format"])
                except UnicodeEncodeError:
                    content_text = datetime.now().strftime("%H:%M:%S • %d.%m.%Y")
            else:
                content_text = content or "BANNER"
            
            # Get colors from theme (with fallbacks)
            deco_color = getattr(Colors, theme_config.get("decoration_color", "CYAN"), Colors.CYAN)
            middle_color = getattr(Colors, theme_config.get("middle_color", "CYAN"), Colors.CYAN)
            text_color = getattr(Colors, theme_config.get("timestamp_color", "GRAY"), Colors.GRAY)
            
            # Apply colors to decorations
            left_raw = theme_config["left_decoration"]
            right_raw = theme_config["right_decoration"]
            
            left_deco = f"{deco_color}{left_raw}{Colors.END}"
            right_deco = f"{deco_color}{right_raw}{Colors.END}"
            
            # Calculate padding for centered content
            total_width = theme_config["total_width"]
            display_content = f" {text_color}{content_text}{Colors.END} "
            deco_width = len(left_raw) + len(right_raw)
            content_width = len(content_text) + 2  # +2 for spaces
            available_width = total_width - content_width - deco_width
            padding = max(0, available_width // 2)
            
            # Create the middle section with whitespace padding (cleaner look)
            middle_section = f"{middle_color}{' ' * padding}{Colors.END}"
            
            # Build the complete banner
            banner = f"{left_deco}{middle_section}{display_content}{middle_section}{right_deco}"
            
            print(f"\n{banner}\n")
            
        except Exception as e:
            # Fallback on any error
            display_text = content if content else datetime.now().strftime("%H:%M:%S • %d.%m.%Y")
            print(f"=== {display_text} ===")

    
    def display_startup_info(self, character_name, session_id, output_mode, gear_rarity=None):
        """Display startup information"""
        # Display CONFIGURATION banner first
        self._display_themed_banner("CONFIGURATION")
        self._display_basic_info(character_name, session_id, output_mode, gear_rarity)
        self._display_hotkey_help()
        self._display_session_footer()
    
    def _display_basic_info(self, character_name, session_id, output_mode, gear_rarity=None):
        """Display basic tracker information with HasiSkull ANSI art"""
        hasiskull_lines = self._load_hasiskull_ansi()
        
        # Get configuration info
        from config import Config
        debug_status = f"{Colors.GREEN}Enabled{Colors.END}" if Config.DEBUG_ENABLED else f"{Colors.GRAY}Disabled{Colors.END}"
        debug_file_status = f"{Colors.GREEN}Enabled{Colors.END}" if Config.DEBUG_TO_FILE else f"{Colors.GRAY}Disabled{Colors.END}"
        
        # Check OBS availability
        try:
            from obs_web_server import OBSWebServer
            obs_status = "🎬 OBS integration available (F9 to start)"
        except ImportError:
            obs_status = "⚠️  OBS integration not available (Flask not installed)"
        
        # Format gear rarity
        if gear_rarity is not None:
            rarity_color = Colors.GOLD if gear_rarity > 0 else Colors.GRAY
            gear_rarity_text = f"✨ Gear Rarity: {rarity_color}{gear_rarity}%{Colors.END}"
        else:
            gear_rarity_text = "✨ Gear Rarity: Not available yet"
        
        # Create info lines - each on its own line, with padding at top
        info_lines = [
            "",  # Empty line for top padding
            "",  # Another empty line for top padding
            f"📋 Character: {Colors.CYAN}{character_name}{Colors.END}",
            f"🎮 Output Mode: {Colors.BOLD}{output_mode.upper()}{Colors.END}",
            f"🐛 Debug: {debug_status}",
            f"📁 Debug to File: {debug_file_status}",
            f"📄 Client Log: {Colors.YELLOW}{Config.CLIENT_LOG}{Colors.END}",
            f"⏱️  API Rate Limit: {Colors.CYAN}{Config.API_RATE_LIMIT}s{Colors.END}",
            f"{gear_rarity_text}",
            "",
            f"{obs_status}",
            f"🆔 Session ID: {Colors.GRAY}{session_id[:8]}...{Colors.END}"
        ]
        
        # Display HasiSkull on the left, info on the right
        self._display_side_by_side(hasiskull_lines, info_lines)
    
    def _load_hasiskull_ansi(self):
        """Load HasiSkull 32x32 colored blocks ANSI art"""
        try:
            from config import Config
            ansi_path = Config.get_ansi_path()
            with open(ansi_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Skip header comments and empty lines, return only ANSI art lines
            ansi_lines = []
            for line in lines:
                line = line.rstrip()
                if line and not line.startswith('#'):
                    ansi_lines.append(line)
            
            return ansi_lines
        except FileNotFoundError:
            # Fallback if ANSI file not found - simple ASCII skull
            return [
                "    💀    ",
                "  💀💀💀  ",
                " 💀💀💀💀 ",
                "💀💀💀💀💀",
                " 💀   💀 ",
                "  💀💀💀  "
            ]
        except Exception:
            # Ultimate fallback
            return ["🎮 PoE2", "Stats", "Tracker"]
    
    def _display_side_by_side(self, left_lines, right_lines):
        """Display two columns side by side with fixed 32-char width for left column"""
        import re
        
        # Fixed width for ANSI art (32 characters + padding)
        left_column_width = 37  # 32 chars + 5 padding
        
        # Pad shorter list with empty strings
        max_lines = max(len(left_lines), len(right_lines))
        left_padded = left_lines + [''] * (max_lines - len(left_lines))
        right_padded = right_lines + [''] * (max_lines - len(right_lines))
        
        # Display side by side with fixed width
        for left, right in zip(left_padded, right_padded):
            if left and right:
                # Truncate ANSI art to exactly 32 visual characters
                clean_left = re.sub(r'\033\[[0-9;]*[mK]', '', left)
                if len(clean_left) > 32:
                    # Truncate the visual content to 32 chars
                    # This is complex with ANSI codes, so we'll just use padding approach
                    pass
                
                # Calculate visual width and pad accordingly
                visual_width = len(clean_left)
                padding = ' ' * (left_column_width - visual_width)
                print(f"{left}{padding}{right}")
            elif left:
                print(left)
            elif right:
                # Empty left, pad with spaces
                print(f"{' ' * left_column_width}{right}")
            else:
                print()
    
    def _display_hotkey_help(self):
        """Display hotkey help information with themed header"""
        self._display_themed_banner("HOTKEYS")
        
        # Hotkeys in nice table format
        hotkeys = [
            ("⌨️  F2", "PRE Snapshot", "⌨️  F3", "POST Analysis", "⌨️  F4", "Debug Toggle"),
            ("⌨️  F5", "Inventory Check", "⌨️  F6", "New Session", "⌨️  F7", "Session Stats"),
            ("⌨️  F8", "Output Mode", "⌨️  Ctrl+F2", "Waystone Analysis", "⌨️  Ctrl+Esc", "Quit")
        ]
        
        for row in hotkeys:
            key1, desc1, key2, desc2, key3, desc3 = row
            print(f"{Colors.GREEN}{key1}{Colors.END} = {desc1:<15} "
                  f"{Colors.GREEN}{key2}{Colors.END} = {desc2:<15} "
                  f"{Colors.RED if 'Esc' in key3 else Colors.GREEN}{key3}{Colors.END} = {desc3}")
        print()
    
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
    
    def display_price_analysis(self, added, removed, post_inventory=None, pre_inventory=None):
        """Display loot analysis for added items - simplified unified function"""
        try:
            # Store inventory data for emoji analysis
            self._current_post_inventory = post_inventory
            self._current_pre_inventory = pre_inventory
            
            # Display loot based on output mode
            if self.output_mode == "normal":
                # Normal mode: Use unified display function
                if added:
                    self.display_items_with_values("💰 Valuable Loot:", added, show_totals=False)
            else:
                # Comprehensive mode: Line-by-line display
                if added:
                    from price_check_poe2 import valuate_items_raw
                    added_rows, _ = valuate_items_raw(added)
                    print(f"\n💰 {Colors.BOLD}[VALUE] Added:{Colors.END}")
                    added_emojis = self._get_smart_emojis_for_items(added_rows)
                    for r in added_rows:
                        emoji = added_emojis.get(r['name'], self._get_category_emoji(r.get('category', 'Unknown')))
                        print(self._format_comprehensive_item_line(r, "+", Colors.GREEN, emoji))
            
            # Calculate and return net value (only from added items since removed is unused)
            if added:
                from price_check_poe2 import valuate_items_raw
                _, (add_c, add_e) = valuate_items_raw(added)
                return self._display_net_value(add_c or 0, add_e)
            else:
                return None
                
        except Exception as pe:
            print(f"❌ [VALUE] price-check error: {pe}")
            return None
    

    

    

    
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
            # Calculate session ex/h if we have runtime data
            session_ex_per_hour = 0.0
            if runtime_seconds and runtime_seconds > 0:
                session_ex_per_hour = total_value / (runtime_seconds / 3600)
            
            print(f"📊 Avg/Map: {Colors.GOLD}{fmt(avg_value)}ex{Colors.END} | "
                  f"⏱️  Avg Time: {Colors.CYAN}{avg_time:.1f}m{Colors.END}")
            
            # Show ex/h if we calculated it
            if session_ex_per_hour > 0:
                print(f"📈 Session: {Colors.GOLD}{fmt(session_ex_per_hour)}ex/h{Colors.END}")
        
        print(f"🎯 {Colors.GREEN}Ready for next map!{Colors.END}")
        self._display_session_footer()
    
    def _display_session_footer(self):
        """Display a beautiful PoE2-style footer with timestamp using theme system"""
        self._display_themed_banner(use_timestamp=True)
    
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
    
    def display_items_with_values(self, header, raw_items, original_inventory=None, show_totals=True, show_footer=False, show_stats=False):
        """Universal function for displaying items with prices and SHOW_ALL_ITEMS logic
        
        Args:
            header: Display header (e.g., "💰 Valuable Items:" or "💰 Valuable Loot:")
            raw_items: Raw item data for price analysis
            original_inventory: Optional original inventory for enhanced emoji analysis
            show_totals: Whether to show total values
            show_footer: Whether to show session footer
            show_stats: Whether to show item count statistics
        """
        try:
            from price_check_poe2 import valuate_items_raw
            rows, (total_c, total_e) = valuate_items_raw(raw_items)
            
            # Filter valuable and worthless items
            valuable_items = [r for r in rows if (r['chaos_total'] or 0) > 0.01 or (r['ex_total'] or 0) > 0.01]
            worthless_items = [r for r in rows if (r['chaos_total'] or 0) <= 0.01 and (r['ex_total'] or 0) <= 0.01]
            
            # Apply SHOW_ALL_ITEMS logic
            if self.config.SHOW_ALL_ITEMS and (valuable_items or worthless_items):
                # Show all items with separator
                all_items = valuable_items.copy()
                if valuable_items and worthless_items:
                    all_items.append({"SEPARATOR": True})  # Special separator marker
                all_items.extend(worthless_items)
                
                self._display_valuable_items_list(header, all_items, original_inventory)
            elif valuable_items:
                # Show only valuable items
                self._display_valuable_items_list(header, valuable_items, original_inventory)
            else:
                # No items to show
                print(f"\n💰 {Colors.GRAY}No valuable items found{Colors.END}")
                return 0  # Return 0 value
            
            # Show totals if requested
            if show_totals and (valuable_items or (self.config.SHOW_ALL_ITEMS and worthless_items)):
                print(f"\n🏆 {Colors.BOLD}Total Inventory Value:{Colors.END}")
                print(f"💰 Chaos: {Colors.GOLD}{fmt(total_c)}c{Colors.END}")
                if total_e is not None and total_e > 0.01:
                    print(f"💰 Exalted: {Colors.GOLD}{fmt(total_e)}ex{Colors.END}")
            
            # Show item statistics if requested
            if show_stats and self.config.SHOW_ALL_ITEMS:
                valuable_count = len(valuable_items) 
                worthless_count = len(worthless_items)
                total_count = valuable_count + worthless_count
                if total_count > 0:
                    print(f"\n� {Colors.GRAY}Items: {valuable_count} valuable, {worthless_count} without value{Colors.END}")
            
            # Show footer if requested
            if show_footer:
                self._display_session_footer()
            
            return total_e or 0  # Return exalted value for further processing
            
        except Exception as e:
            print(f"❌ [ITEM VALUES] error: {e}")
            return 0
    
    def display_current_inventory_value(self, inventory_items):
        """Display value analysis of current inventory - now uses unified function"""
        print(f"\n� {Colors.BOLD}CURRENT INVENTORY VALUE{Colors.END}")
        self.display_items_with_values(
            "💰 Valuable Items:", 
            inventory_items, 
            original_inventory=inventory_items,
            show_totals=True, 
            show_footer=True, 
            show_stats=True
        )
    

    
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
    

    

    
    # Helper methods for reducing code duplication
    def _format_colored_number(self, value, precision=2, suffix=""):
        """Format number with brown main digits, darker brown decimals, and gold suffix"""
        if value is None or value == 0:
            return f"{Colors.GRAY}-{Colors.END}"
        
        # Format with specified precision
        formatted = f"{value:.{precision}f}".rstrip("0").rstrip(".")
        
        # If after formatting it becomes "0", treat as zero value
        if formatted == "0" or formatted == "0.0" or formatted == "0.00":
            return f"{Colors.GRAY}-{Colors.END}"
        
        # Split into integer and decimal parts
        if "." in formatted:
            integer_part, decimal_part = formatted.split(".")
            # If integer part is 0, don't display it (0.02 becomes .02)
            if integer_part == "0":
                return f"{Colors.DARK_BROWN}.{decimal_part}{Colors.END} {Colors.GOLD}{suffix}{Colors.END}"
            else:
                return f"{Colors.BROWN}{integer_part}{Colors.END}{Colors.DARK_BROWN}.{decimal_part}{Colors.END} {Colors.GOLD}{suffix}{Colors.END}"
        else:
            return f"{Colors.BROWN}{formatted}{Colors.END} {Colors.GOLD}{suffix}{Colors.END}"
    
    def _get_emoji_display_width(self, emoji_char):
        """Get display width for emoji using simple string length"""
        return len(emoji_char)
    
    def _get_emoji_spacing(self, emoji_char):
        """Get number of spaces needed after emoji for proper alignment"""
        # Some emojis in certain terminals need extra spacing for proper alignment
        emoji_spacing_map = {
            '⚔': 2,      # Sword emojis need 2 spaces
            '⚔️': 2,     # Sword with variation selector
            '🏹': 2,     # Bow emoji (if needed)
            '🗡️': 2,    # Dagger emoji (if needed)
            '🛡️': 2,    # Shield emoji (if needed)

        }
        
        return emoji_spacing_map.get(emoji_char, 1)  # Default: 1 space for most emojis
    
    def _get_category_emoji(self, category):
        """Get emoji based on item category"""
        category_lower = (category or '').lower()
        
        emoji_map = {
            'currency': '🟡',  # Gold for currency
            'delirium': '⚫',   # Black for delirium
            'catalysts': '🔬',  # Microscope for catalysts (science/chemistry)
            'runes': '🔵',     # Blue for runes
            'ritual': '🟠',    # Orange for ritual
            'fragments': '🔴', # Red for fragments
            'maps': '🗺️',      # Map emoji for maps
            'jewels': '💎',    # Diamond for jewels
            'armour': '🛡️',    # Shield for armour
            'weapons': '⚔️',   # Sword for weapons
            'accessories': '💍', # Ring for accessories
            'gems': '🔮',      # Crystal for gems
            'divination': '📜', # Scroll for divination cards
            'essence': '🧪',   # Flask for essences
            'fossil': '🪨',    # Rock for fossils
            'breach': '🔴',    # Red for breach
            'harbinger': '🌟', # Star for harbinger
            'legion': '⚫',    # Black for legion
            'metamorph': '🟢', # Green for metamorph
            'blight': '🍄',    # Mushroom for blight
            'syndicate': '🎭', # Mask for syndicate
            'bestiary': '🐺',  # Wolf for bestiary
            'incursion': '🏛️',  # Temple for incursion
            'delve': '⛏️',     # Pickaxe for delve
        }
        
        # Try exact match first
        if category_lower in emoji_map:
            return emoji_map[category_lower]
        
        # Try partial matches
        for cat, emoji in emoji_map.items():
            if cat in category_lower:
                return emoji
        
        # Fallback based on item characteristics
        if 'orb' in category_lower:
            return '🟡'  # Gold for orbs
        elif 'catalyst' in category_lower:
            return '🔬'  # Microscope for catalysts
        elif 'splinter' in category_lower:
            return '🔴'  # Red for splinters
        elif 'liquid' in category_lower:
            return '⚫'  # Black for liquids
        elif 'rune' in category_lower:
            return '🔵'  # Blue for runes
        
        return '⚪'  # White circle as fallback
    
    def _get_smart_emojis_for_items(self, items_data, inventory_items=None):
        """
        Unified emoji analysis for all item displays
        
        Args:
            items_data: List of item data dicts (from price analysis)
            inventory_items: Optional original inventory items from API (with icon URLs)
            
        Returns:
            dict: Mapping of item names to emojis (smart icons or category fallback)
        """
        # Check if we have inventory data (either passed or from display_price_analysis)
        if inventory_items is None:
            inventory_items = getattr(self, '_current_post_inventory', None)
        
        if inventory_items:
            # We have inventory data! Use full icon analysis
            try:
                from icon_cache_manager import get_icon_cache_manager  
                from icon_color_analyzer import get_color_analyzer, get_icon_color_mapper
                
                cache_manager = get_icon_cache_manager()
                color_analyzer = get_color_analyzer()
                color_mapper = get_icon_color_mapper()
                
                # Create mapping of item names we want emojis for
                item_names = {item['name'] for item in items_data}
                
                # Filter inventory items to only the ones we need
                relevant_inventory_items = [
                    item for item in inventory_items 
                    if (item.get('typeLine') or item.get('name', '')) in item_names
                ]
                
                from config import Config
                if Config.DEBUG_ENABLED:
                    print(f"[ICON] Analyzing {len(relevant_inventory_items)} items with icon analysis...")
                
                result = {}
                for item in relevant_inventory_items:
                    item_name = item.get('typeLine') or item.get('name', 'Unknown')
                    icon_url = item.get('icon')
                    
                    if icon_url:
                        # Try to get cached icon
                        cached_icon = cache_manager.get_cached_icon_path(icon_url)
                        if not cached_icon.exists():
                            # Download if not cached (limit downloads)
                            cached_icon = cache_manager.download_icon(icon_url)
                        
                        if cached_icon and cached_icon.exists():
                            # Analyze color and get emoji
                            dominant_color = color_analyzer.get_dominant_color(cached_icon)
                            color_category = color_analyzer.categorize_color(dominant_color)
                            result[item_name] = color_mapper.get_emoji_for_item(item, color_category)
                        else:
                            # Fallback to item-based emoji without color
                            result[item_name] = color_mapper.get_emoji_for_item(item)
                    else:
                        # No icon URL, use item-based emoji
                        result[item_name] = color_mapper.get_emoji_for_item(item)
                
                # Fill in missing items with category emojis
                for item in items_data:
                    if item['name'] not in result:
                        result[item['name']] = self._get_category_emoji(item.get('category', 'Unknown'))
                
                return result
                
            except Exception as e:
                from config import Config
                if Config.DEBUG_ENABLED:
                    print(f"[ICON] Icon analysis unavailable, using category emojis: {e}")
        
        # Fallback to category-based emojis for all items
        result = {}
        for item in items_data:
            emoji = self._get_category_emoji(item.get('category', 'Unknown'))
            result[item['name']] = emoji
        
        return result
    
    def _display_valuable_items_list(self, header, items_data, inventory_items=None):
        """
        Unified display function for valuable items as formatted table
        
        Args:
            header: Display header (e.g., "💰 Valuable Loot:" or "💰 Valuable Items:")
            items_data: List of item data dicts (from price analysis)
            inventory_items: Optional original inventory items for enhanced emoji analysis
        """
        if not items_data:
            return
            
        print(f"\n{Colors.BOLD}{header}{Colors.END}")
        
        # Show animation during emoji analysis (the slow part)
        from animation_manager import AnimationManager
        animation_manager = AnimationManager()
        
        # Count real items (without separators)
        real_item_count = len([r for r in items_data if not (isinstance(r, dict) and r.get("SEPARATOR"))])
        
        with animation_manager.context_spinner(
            f"📊 Building table for {real_item_count} items", 
            style='dots', 
            delay=0.15
        ):
            # Get emojis using unified analysis (filter out separators)
            real_items = [r for r in items_data if not (isinstance(r, dict) and r.get("SEPARATOR"))]
            item_emojis = self._get_smart_emojis_for_items(real_items, inventory_items)
        
        # Calculate column widths based on ALL data (including items without value, ignore separators)
        all_display_items = [r for r in items_data if not (isinstance(r, dict) and r.get("SEPARATOR"))]
        if all_display_items:
            # Calculate max name length using base spacing (1 space) for all items
            max_name_len = 0
            for r in all_display_items:
                emoji = item_emojis.get(r['name'], self._get_category_emoji(r.get('category', 'Unknown')))
                base_spacing = 1  # Use fixed base spacing for width calculation
                item_display_len = len(emoji) + base_spacing + len(r['name'])  # emoji + 1 space + name
                max_name_len = max(max_name_len, item_display_len)
            
            name_width = max(self.config.TABLE_MIN_NAME_WIDTH, max_name_len + 1)
        else:
            name_width = self.config.TABLE_MIN_NAME_WIDTH
        

        
        # Table header
        header_line = (
            f"{'Item Name':<{name_width}} "
            f"{'Qty':>{self.config.TABLE_QTY_WIDTH}} "
            f"{'Category':<{self.config.TABLE_CATEGORY_WIDTH}} "
            f"{'Chaos':>{self.config.TABLE_CHAOS_WIDTH}} "
            f"{'Exalted':>{self.config.TABLE_EXALTED_WIDTH}}"
        )
        print(header_line)
        
        # Separator line
        separator_width = len(header_line)
        print(self.config.TABLE_SEPARATOR_CHAR * separator_width)
        
        # Table rows
        for r in items_data:
            # Check for separator marker
            if isinstance(r, dict) and r.get("SEPARATOR"):
                print()  # Empty line separator
                continue
                
            emoji = item_emojis.get(r['name'], self._get_category_emoji(r.get('category', 'Unknown')))
            
            # Calculate visible lengths and get emoji spacing once
            spacing = self._get_emoji_spacing(emoji)  # Get spacing once and reuse
            item_name_visible_length = len(emoji) + spacing + len(r['name'])  # emoji + actual spaces + name
            
            # Use gray color for items without value
            is_worthless = (r.get('chaos_total', 0) <= 0.01 and r.get('ex_total', 0) <= 0.01)
            name_color = Colors.GRAY if is_worthless else Colors.WHITE
            
            # Create colored item name using the same spacing
            item_name_colored = f"{emoji}{' ' * spacing}{name_color}{r['name']}{Colors.END}"
            

            
            category = (r.get('category') or 'n/a')[:self.config.TABLE_CATEGORY_WIDTH]
            
            # Get plain text values for width calculation (matching the colored format exactly)
            def get_plain_value(val, suffix):
                if val is None or val == 0:
                    return "-"
                
                # Format with same precision as _format_colored_number
                formatted = f"{val:.2f}".rstrip("0").rstrip(".")
                
                # If after formatting it becomes "0", show as "-"
                if formatted == "0" or formatted == "0.0" or formatted == "0.00":
                    return "-"
                
                # Remove leading zero for values < 1 (to match colored format)
                if formatted.startswith("0."):
                    formatted = formatted[1:]  # Remove the "0"
                return f"{formatted} {suffix}"
            
            chaos_plain = get_plain_value(r['chaos_total'], "c")
            ex_plain = get_plain_value(r['ex_total'], "ex")
            
            # Get colored values
            chaos_val = self._format_colored_number(r['chaos_total'], 2, "c")
            ex_val = self._format_colored_number(r['ex_total'], 2, "ex") if r['ex_total'] and r['ex_total'] >= 0.005 else f"{Colors.GRAY}-{Colors.END}"
            
            # Calculate padding - add 3 extra spaces for weapon emojis as visual correction
            if spacing > 1:  # Weapon emojis that need special treatment
                name_padding = name_width - item_name_visible_length + 3  # +3 spaces for visual correction
            else:  # Normal emojis
                name_padding = name_width - item_name_visible_length + 1  # +1 normal correction
            chaos_padding = self.config.TABLE_CHAOS_WIDTH - len(chaos_plain)
            ex_padding = self.config.TABLE_EXALTED_WIDTH - len(ex_plain)
            


            
            # Format row with proper padding
            row = (
                f"{item_name_colored}{' ' * name_padding} "
                f"{Colors.CYAN}{r['qty']:>{self.config.TABLE_QTY_WIDTH}}{Colors.END} "
                f"{Colors.GRAY}{category:<{self.config.TABLE_CATEGORY_WIDTH}}{Colors.END} "
                f"{' ' * chaos_padding}{chaos_val} "
                f"{' ' * ex_padding}{ex_val}"
            )
            print(row)
    

    
    def _format_comprehensive_item_line(self, item_data, prefix_symbol, prefix_color, item_emoji=None):
        """Format comprehensive mode item line with category info"""
        ex_str = f" | {Colors.GOLD}{fmt(item_data['ex_total'])}ex{Colors.END}" if item_data.get('ex_total') and item_data['ex_total'] > 0.01 else ""
        category = item_data.get('category') or 'n/a'
        emoji_str = f"{item_emoji} " if item_emoji else ""
        return (f"  {prefix_color}{prefix_symbol}{Colors.END} {emoji_str}{item_data['name']} {Colors.GRAY}[{category}]{Colors.END} "
                f"x{item_data['qty']} => {Colors.GOLD}{fmt(item_data['chaos_total'])}c{Colors.END}{ex_str}")