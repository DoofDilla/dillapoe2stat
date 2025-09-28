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
        """Create the HTML content for item value table"""
        
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
        
        # Start HTML document
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
            background: rgba(0, 0, 0, 0.8);
            color: #ffffff;
            margin: 0;
            padding: 10px;
            font-size: 14px;
            line-height: 1.2;
        }}
        
        .container {{
            max-width: 600px;
            margin: 0 0;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 15px;
            border-bottom: 2px solid #444;
            padding-bottom: 10px;
        }}
        
        .map-info {{
            color: #87CEEB;
            font-size: 12px;
            margin-bottom: 5px;
        }}
        
        .timestamp {{
            color: #888;
            font-size: 11px;
        }}
        
        .summary {{
            background: rgba(255, 215, 0, 0.1);
            border: 1px solid #FFD700;
            border-radius: 5px;
            padding: 8px;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .total-value {{
            color: #FFD700;
            font-size: 18px;
            font-weight: bold;
        }}
        
        .session-stats {{
            color: #90EE90;
            font-size: 12px;
            margin-top: 5px;
        }}
        
        .items-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 10px;
        }}
        
        .items-table th {{
            background: rgba(255, 255, 255, 0.1);
            color: #FFD700;
            padding: 8px 6px;
            text-align: left;
            border-bottom: 1px solid #444;
            font-size: 12px;
        }}
        
        .items-table td {{
            padding: 6px;
            border-bottom: 1px solid #333;
            font-size: 11px;
        }}
        
        .item-added {{
            background: rgba(0, 255, 0, 0.05);
            border-left: 3px solid #00ff00;
        }}
        
        .item-removed {{
            background: rgba(255, 0, 0, 0.05);
            border-left: 3px solid #ff0000;
        }}
        
        .item-name {{
            color: #ffffff;
            font-weight: bold;
        }}
        
        .item-value {{
            color: #FFD700;
            text-align: right;
        }}
        
        .item-type {{
            color: #87CEEB;
            font-size: 10px;
        }}
        
        .rarity-normal {{ color: #c8c8c8; }}
        .rarity-magic {{ color: #8888ff; }}
        .rarity-rare {{ color: #ffff77; }}
        .rarity-unique {{ color: #af6025; }}
        
        .no-items {{
            text-align: center;
            color: #888;
            font-style: italic;
            padding: 20px;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .container {{
            animation: fadeIn 0.3s ease-in;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="map-info">
                {'📍 ' + map_info.get('map_name', 'Unknown Map') if map_info else 'PoE Stats Tracker'}
            </div>
            <div class="timestamp">Last Update: {timestamp}</div>
        </div>
        
        <div class="summary">
            <div class="total-value">💰 {total_value:.2f} Exalted</div>
            {self._generate_session_stats_html(session_stats) if session_stats else ''}
        </div>
"""
        
        # Add items table if we have items
        if added_items or removed_items:
            html += """
        <table class="items-table">
            <thead>
                <tr>
                    <th>Item</th>
                    <th>Type</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
"""
            
            # Add added items (green)
            for item in added_items:
                rarity_class = self._get_rarity_class(item.get('rarity', 'normal'))
                value_text = f"{item.get('value_exalted', 0):.2f}ex" if item.get('value_exalted', 0) > 0 else '-'
                
                html += f"""
                <tr class="item-added">
                    <td class="item-name {rarity_class}">+ {item.get('name', 'Unknown Item')}</td>
                    <td class="item-type">{item.get('type', 'Unknown')}</td>
                    <td class="item-value">{value_text}</td>
                </tr>
"""
            
            # Add removed items (red) 
            for item in removed_items:
                rarity_class = self._get_rarity_class(item.get('rarity', 'normal'))
                value_text = f"{item.get('value_exalted', 0):.2f}ex" if item.get('value_exalted', 0) > 0 else '-'
                
                html += f"""
                <tr class="item-removed">
                    <td class="item-name {rarity_class}">- {item.get('name', 'Unknown Item')}</td>
                    <td class="item-type">{item.get('type', 'Unknown')}</td>
                    <td class="item-value">{value_text}</td>
                </tr>
"""
            
            html += """
            </tbody>
        </table>
"""
        else:
            html += """
        <div class="no-items">
            No items to display - Complete a map to see loot analysis
        </div>
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
                Maps: {maps} | Total: {total_value:.1f}ex
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
        <div class="session-title">Session Stats</div>
        <div class="stat-line maps">Maps: {maps_completed}</div>
        <div class="stat-line value">Value: {total_value:.1f} Exalted</div>
        <div class="stat-line time">Time: {hours}h {minutes}m</div>
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