"""
OBS Overlay Manager
Generates HTML overlays for OBS Studio from PoE Stats data
Focuses on KISS principle - simple, effective overlays
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any


class OBSOverlayManager:
    """Manages HTML overlays for OBS Studio integration"""
    
    def __init__(self, output_dir: str = "obs_overlays"):
        self.output_dir = output_dir
        self.ensure_output_dir()
        
        # Track last update times for auto-refresh
        self.last_updates = {}
        
    def ensure_output_dir(self):
        """Ensure output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_item_value_table(self, added_items: List[Dict], removed_items: List[Dict], 
                                session_stats: Optional[Dict] = None, map_info: Optional[Dict] = None) -> str:
        """
        Generate beautiful HTML table for item values - perfect for OBS overlay
        
        Args:
            added_items: List of items that were added to inventory
            removed_items: List of items that were removed from inventory 
            session_stats: Optional session statistics
            map_info: Optional map information
            
        Returns:
            Path to generated HTML file
        """
        
        # Calculate totals
        total_value = 0
        for item in added_items:
            if 'value_exalted' in item:
                total_value += item['value_exalted']
        
        # Generate HTML
        html_content = self._create_item_table_html(
            added_items, removed_items, total_value, session_stats, map_info
        )
        
        # Write to file
        output_path = os.path.join(self.output_dir, "item_value_table.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.last_updates['item_table'] = time.time()
        return output_path
    
    def _create_item_table_html(self, added_items: List[Dict], removed_items: List[Dict], 
                              total_value: float, session_stats: Optional[Dict], 
                              map_info: Optional[Dict]) -> str:
        """Create HTML that looks EXACTLY like the terminal output"""
        
        # Ensure parameters are not None
        if added_items is None:
            added_items = []
        if removed_items is None:
            removed_items = []
        if session_stats is None:
            session_stats = {}
        if map_info is None:
            map_info = {}
        
        # Get current timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Calculate total chaos value from processed data
        total_chaos = 0
        for item in added_items:
            if 'value_chaos' in item:
                total_chaos += item['value_chaos']
        
        # Create HTML that looks like terminal output
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PoE Stats - Item Values</title>
    <!-- Auto-refresh disabled to prevent flickering -->
    <style>
        body {{
            font-family: 'Consolas', 'Monaco', monospace;
            background: #1e1e1e;
            color: #ffffff;
            margin: 0;
            padding: 15px;
            font-size: 14px;
            line-height: 1.4;
        }}
        
        .terminal-output {{
            max-width: 900px;
            margin: 0 0;
        }}
        
        .map-header {{
            color: #87CEEB;
            font-size: 16px;
            margin-bottom: 8px;
            font-weight: bold;
        }}
        
        .runtime {{
            color: #DDA0DD;
            font-size: 14px;
            margin-bottom: 12px;
        }}
        
        .valuable-loot-header {{
            color: #FFD700;
            font-size: 16px;
            margin-bottom: 8px;
            font-weight: bold;
        }}
        
        .loot-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
            font-family: 'Consolas', monospace;
        }}
        
        .loot-table th {{
            color: #FFD700;
            text-align: left;
            padding: 4px 12px;
            border-bottom: 1px solid #444;
            font-weight: bold;
        }}
        
        .loot-table td {{
            padding: 2px 12px;
            color: #ffffff;
        }}
        
        .item-qty {{ color: #87CEEB; text-align: center; }}
        .item-category {{ color: #87CEEB; }}
        .chaos-value {{ color: #87CEEB; text-align: right; }}
        .exalted-value {{ color: #FFD700; text-align: right; }}
        
        .net-value {{
            color: #FFD700;
            font-size: 16px;
            font-weight: bold;
            margin-top: 10px;
        }}
        
        .timestamp {{
            color: #888;
            font-size: 12px;
            margin-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="terminal-output">
        <div class="map-header">🏔️ {map_info.get('map_name', 'Unknown Map')} (T{map_info.get('level', '?')}, seed {map_info.get('seed', '?')})</div>
        
        <div class="runtime">⏱️ Runtime: {self._format_map_runtime(map_info.get('map_runtime_seconds'))}</div>
        
        <div class="valuable-loot-header">💰 Valuable Loot:</div>
        
        <table class="loot-table">
            <tr>
                <th>Item Name</th>
                <th>Qty</th>
                <th>Category</th>
                <th>Chaos</th>
                <th>Exalted</th>
            </tr>
"""
        
        # Add items exactly like terminal format
        if added_items:
            for item in added_items:
                # Safe extraction with None handling
                item_type = item.get('type') or 'Unknown'
                item_name = item.get('name') or 'Unknown Item'
                
                emoji = self._get_item_emoji(item_type, item_name)
                name = item_name
                qty = item.get('quantity') or 1
                category = item_type
                exalted_value = item.get('value_exalted') or 0
                chaos_value = item.get('value_chaos') or 0
                
                # Format values exactly like terminal (precision=2, strip trailing zeros, remove leading zero)
                def format_terminal_style(value, suffix):
                    if value is None or value == 0:
                        return "-"
                    formatted = f"{value:.2f}".rstrip("0").rstrip(".")
                    if formatted.startswith("0."):
                        formatted = formatted[1:]  # Remove leading zero: 0.15 -> .15
                    return f"{formatted} {suffix}"
                
                chaos_formatted = format_terminal_style(chaos_value, "c")
                exalted_formatted = format_terminal_style(exalted_value, "ex")
                
                html += f"""
            <tr>
                <td>{emoji} {name}</td>
                <td class="item-qty">{qty}</td>
                <td class="item-category">{category}</td>
                <td class="chaos-value">{chaos_formatted}</td>
                <td class="exalted-value">{exalted_formatted}</td>
            </tr>
"""
        else:
            html += """
            <tr>
                <td colspan="5" style="text-align: center; color: #888; font-style: italic;">
                    No items to display - Complete a map to see loot analysis
                </td>
            </tr>
"""
        
        # Close table and add net value
        html += f"""
        </table>
        
        <div class="net-value">💰 Net Value: {f"{total_chaos:.3f}".rstrip("0").rstrip(".")}c | {f"{total_value:.3f}".rstrip("0").rstrip(".")}ex</div>
        
        <div class="timestamp">Last Update: {timestamp}</div>
"""
        
        # Close HTML  
        html += """
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_session_stats_html(self, session_stats: Optional[Dict]) -> str:
        """Generate HTML for session statistics"""
        if not session_stats or session_stats is None:
            return ""
        
        maps = session_stats.get('maps_completed', 0)
        total_value = session_stats.get('total_value', 0)
        
        return f"""
            <div class="session-stats">
                🗺️ {maps} | 💎 {total_value:.1f}ex
            </div>
        """
    
    def _get_rarity_class(self, rarity: str) -> str:
        """Get CSS class for item rarity"""
        rarity_lower = rarity.lower()
        if 'unique' in rarity_lower:
            return 'rarity-unique'
        elif 'rare' in rarity_lower:
            return 'rarity-rare'
        elif 'magic' in rarity_lower:
            return 'rarity-magic'
        else:
            return 'rarity-normal'
    
    def _format_map_runtime(self, runtime_seconds):
        """Format map runtime from seconds to 'Xm Ys' format"""
        if runtime_seconds is None or runtime_seconds <= 0:
            return "0m 0s"
        
        minutes = int(runtime_seconds // 60)
        seconds = int(runtime_seconds % 60)
        return f"{minutes}m {seconds}s"
    
    def _get_item_emoji(self, item_type: str, item_name: str) -> str:
        """Get emoji for item like in terminal display"""
        # Handle None values safely
        item_type_lower = (item_type or '').lower()
        item_name_lower = (item_name or '').lower()
        
        # Currency items
        if 'currency' in item_type_lower:
            if 'exalted' in item_name_lower:
                return '🟡'  # Exalted Orb
            elif 'divine' in item_name_lower:
                return '🟡'  # Divine Orb
            elif 'chaos' in item_name_lower:
                return '🟡'  # Chaos Orb
            elif 'chance' in item_name_lower:
                return '🟡'  # Chance Shard
            elif 'regal' in item_name_lower:
                return '🟡'  # Regal Orb
            elif 'armourer' in item_name_lower:
                return '⚪'  # Armourer's Scrap
            elif 'simulacrum' in item_name_lower:
                return '🟣'  # Simulacrum Splinter
            else:
                return '🪙'  # Generic currency
        
        # Runes
        elif 'rune' in item_type_lower or 'rune' in item_name_lower:
            return '🔵'  # Runes
        
        # Catalysts
        elif 'catalyst' in item_type_lower or 'catalyst' in item_name_lower:
            return '🟣'  # Catalysts
        
        # Maps/Waystones
        elif 'map' in item_type_lower or 'waystone' in item_name_lower:
            return '🏔️'  # Waystone
        
        # Gems
        elif 'gem' in item_type_lower or 'gem' in item_name_lower:
            return '💎'  # Uncut Support Gem
        
        # Armour
        elif 'armour' in item_type_lower:
            return '🛡️'  # Armour
        
        # Weapons
        elif 'weapon' in item_type_lower:
            return '⚔️'  # Weapons
        
        # Accessories
        elif 'accessory' in item_type_lower:
            return '💍'  # Rings/Amulets
        
        # Default
        else:
            return '📦'  # Unknown items
    
    def generate_session_overlay(self, session_stats: Dict) -> str:
        """
        Generate minimal session stats overlay
        
        Args:
            session_stats: Session statistics dictionary
            
        Returns:
            Path to generated HTML file
        """
        
        html_content = self._create_session_overlay_html(session_stats)
        
        output_path = os.path.join(self.output_dir, "session_stats.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.last_updates['session'] = time.time()
        return output_path
    
    def _create_session_overlay_html(self, session_stats: Optional[Dict]) -> str:
        """Create minimal session stats overlay HTML"""
        
        # Handle None session_stats
        if session_stats is None:
            session_stats = {}
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Safe access to nested dictionaries
        maps_completed = session_stats.get('maps_completed', 0)
        total_value = session_stats.get('total_value', 0.0)
        runtime = session_stats.get('runtime', {})
        hours = runtime.get('hours', 0) if runtime else 0
        minutes = runtime.get('minutes', 0) if runtime else 0
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PoE Session Stats</title>
    <!-- Auto-refresh disabled to prevent flickering -->
    <style>
        body {{
            font-family: 'Consolas', 'Monaco', monospace;
            background: rgba(0, 0, 0, 0.8);
            color: #ffffff;
            margin: 0;
            padding: 15px;
            font-size: 16px;
        }}
        
        .stats-container {{
            background: rgba(255, 215, 0, 0.1);
            border: 2px solid #FFD700;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            max-width: 300px;
            margin: 0 0;
        }}
        
        .session-title {{
            color: #FFD700;
            font-size: 14px;
            margin-bottom: 10px;
        }}
        
        .stat-line {{
            margin: 8px 0;
            font-size: 18px;
        }}
        
        .maps {{ color: #87CEEB; }}
        .value {{ color: #90EE90; }}
        .time {{ color: #DDA0DD; }}
        
        .timestamp {{
            color: #888;
            font-size: 12px;
            margin-top: 10px;
            border-top: 1px solid #444;
            padding-top: 8px;
        }}
        
        .no-data {{
            color: #888;
            font-style: italic;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="stats-container">
        <div class="session-title">📊 Session Stats</div>
        <div class="stat-line maps">🗺️ {maps_completed} Maps</div>
        <div class="stat-line value">💎 {total_value:.1f} Exalted</div>
        <div class="stat-line time">⏱️ {hours}h {minutes}m</div>
        <div class="timestamp">Updated: {timestamp}</div>
    </div>
</body>
</html>
"""
        return html
    
    def get_overlay_urls(self, base_url: str = "http://localhost:5000") -> Dict[str, str]:
        """Get URLs for OBS Browser Sources"""
        return {
            'item_table': f"{base_url}/obs/item_table",
            'session_stats': f"{base_url}/obs/session_stats"
        }


# Test function
def test_obs_overlay():
    """Test the OBS overlay generation"""
    
    overlay_manager = OBSOverlayManager()
    
    # Test data
    added_items = [
        {
            'name': 'Divine Orb',
            'type': 'Currency',
            'rarity': 'normal',
            'value_exalted': 0.8
        },
        {
            'name': 'Rare Helmet',
            'type': 'Armour',
            'rarity': 'rare',
            'value_exalted': 0.3
        },
        {
            'name': 'Unique Ring',
            'type': 'Accessory', 
            'rarity': 'unique',
            'value_exalted': 1.2
        }
    ]
    
    removed_items = [
        {
            'name': 'Portal Scroll',
            'type': 'Currency',
            'rarity': 'normal',
            'value_exalted': 0.0
        }
    ]
    
    session_stats = {
        'maps_completed': 5,
        'total_value': 12.7,
        'runtime': {'hours': 1, 'minutes': 23}
    }
    
    map_info = {
        'map_name': 'Cemetery of the Eternals',
        'level': 72
    }
    
    # Generate overlays
    item_table_path = overlay_manager.generate_item_value_table(
        added_items, removed_items, session_stats, map_info
    )
    
    session_path = overlay_manager.generate_session_overlay(session_stats)
    
    print(f"Generated OBS overlays:")
    print(f"   Item Table: {item_table_path}")
    print(f"   Session Stats: {session_path}")
    print(f"\nFor OBS Studio:")
    print(f"   Add Browser Source with Local File:")
    print(f"   {os.path.abspath(item_table_path)}")
    print(f"   {os.path.abspath(session_path)}")


if __name__ == "__main__":
    test_obs_overlay()