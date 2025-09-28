"""
OBS Web Server
Simple Flask server to serve HTML overlays for OBS Studio Browser Sources
Provides live-updating overlays with minimal overhead
"""

from flask import Flask, render_template_string, jsonify, send_from_directory
import os
import json
import time
from datetime import datetime
from typing import Dict, Optional
import threading
import webbrowser

from obs_overlay_manager import OBSOverlayManager


class OBSWebServer:
    """Flask web server for OBS overlay integration"""
    
    def __init__(self, host: str = "localhost", port: int = 5000, quiet_mode: bool = True):
        self.host = host
        self.port = port
        self.quiet_mode = quiet_mode
        self.app = Flask(__name__)
        self.overlay_manager = OBSOverlayManager()
        
        # Data storage for live updates
        self.current_data = {
            'item_table': None,
            'session_stats': None,
            'last_update': time.time()
        }
        
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes for OBS overlays"""
        
        @self.app.route('/')
        def index():
            """Main index page with OBS setup instructions"""
            return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>PoE Stats - OBS Integration</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .url-box { background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 4px; font-family: monospace; margin: 10px 0; }
        .step { margin: 20px 0; padding: 15px; border-left: 4px solid #007bff; background: #f8f9fa; }
        .preview { text-align: center; margin: 20px 0; }
        .preview a { display: inline-block; margin: 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }
        .status { color: #28a745; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 PoE Stats OBS Integration</h1>
            <p class="status">✅ Server running on http://{{ request.host }}</p>
        </div>
        
        <h2>📺 OBS Studio Setup</h2>
        
        <div class="step">
            <h3>Step 1: Add Browser Source</h3>
            <p>In OBS Studio, add a new <strong>Browser Source</strong> to your scene.</p>
        </div>
        
        <div class="step">
            <h3>Step 2: Configure URL</h3>
            <p>Use one of these URLs in your Browser Source:</p>
            
            <h4>📊 Item Value Table (Recommended)</h4>
            <div class="url-box">http://{{ request.host }}/obs/item_table</div>
            <p><em>Shows beautiful loot analysis after each map</em></p>
            
            <h4>📈 Session Stats</h4>
            <div class="url-box">http://{{ request.host }}/obs/session_stats</div>
            <p><em>Shows current session statistics</em></p>
        </div>
        
        <div class="step">
            <h3>Step 3: Browser Source Settings</h3>
            <ul>
                <li><strong>Width:</strong> 600px (item table) or 300px (session stats)</li>
                <li><strong>Height:</strong> 400px (item table) or 200px (session stats)</li>
                <li><strong>Refresh browser when scene becomes active:</strong> ✅ Checked</li>
                <li><strong>Shutdown source when not visible:</strong> ✅ Checked</li>
            </ul>
        </div>
        
        <div class="preview">
            <h3>🔍 Preview Overlays</h3>
            <a href="/obs/item_table" target="_blank">Preview Item Table</a>
            <a href="/obs/session_stats" target="_blank">Preview Session Stats</a>
        </div>
        
        <div class="step">
            <h3>💡 Tips</h3>
            <ul>
                <li>Overlays update automatically after each map completion</li>
                <li>No auto-refresh to prevent flickering in OBS</li>
                <li>Transparent background works great for streaming</li>
                <li>Right-aligned layout for better OBS positioning</li>
                <li>Test with dummy data using <code>/test</code> endpoints</li>
            </ul>
        </div>
    </div>
</body>
</html>
            """)
        
        @self.app.route('/obs/item_table')
        def obs_item_table():
            """Serve item value table overlay for OBS"""
            # Get current data or use dummy data
            item_data = self.current_data.get('item_table')
            
            if not item_data or item_data is None:
                # Return empty state
                return self.overlay_manager._create_item_table_html([], [], 0, None, None)
            
            # Safe access with None handling
            added_items = item_data.get('added_items', []) or []
            removed_items = item_data.get('removed_items', []) or []
            total_value = item_data.get('total_value', 0) or 0
            session_stats = item_data.get('session_stats') or {}
            map_info = item_data.get('map_info') or {}
            
            return self.overlay_manager._create_item_table_html(
                added_items,
                removed_items,
                total_value,
                session_stats,
                map_info
            )
        
        @self.app.route('/obs/session_stats')
        def obs_session_stats():
            """Serve session stats overlay for OBS"""
            session_data = self.current_data.get('session_stats', {})
            # Ensure session_data is never None
            if session_data is None:
                session_data = {}
            return self.overlay_manager._create_session_overlay_html(session_data)
        
        @self.app.route('/api/update_item_table', methods=['POST'])
        def api_update_item_table():
            """API endpoint to update item table data"""
            try:
                from flask import request
                data = request.get_json()
                
                self.current_data['item_table'] = data
                self.current_data['last_update'] = time.time()
                
                return jsonify({'status': 'success', 'timestamp': self.current_data['last_update']})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/api/update_session_stats', methods=['POST'])  
        def api_update_session_stats():
            """API endpoint to update session stats"""
            try:
                from flask import request
                data = request.get_json()
                
                self.current_data['session_stats'] = data
                self.current_data['last_update'] = time.time()
                
                return jsonify({'status': 'success', 'timestamp': self.current_data['last_update']})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/api/status')
        def api_status():
            """Get server status and last update time"""
            return jsonify({
                'status': 'running',
                'last_update': self.current_data['last_update'],
                'has_item_data': self.current_data['item_table'] is not None,
                'has_session_data': self.current_data['session_stats'] is not None
            })
        
        # Test endpoints with dummy data
        @self.app.route('/test/item_table')
        def test_item_table():
            """Test item table with dummy data"""
            dummy_added = [
                {'name': 'Divine Orb', 'type': 'Currency', 'rarity': 'normal', 'value_exalted': 0.8},
                {'name': 'Exalted Orb', 'type': 'Currency', 'rarity': 'normal', 'value_exalted': 1.0},
                {'name': 'Rare Helmet', 'type': 'Armour', 'rarity': 'rare', 'value_exalted': 0.3},
                {'name': 'Unique Ring', 'type': 'Accessory', 'rarity': 'unique', 'value_exalted': 1.2}
            ]
            
            dummy_removed = [
                {'name': 'Portal Scroll', 'type': 'Currency', 'rarity': 'normal', 'value_exalted': 0.0}
            ]
            
            dummy_session = {
                'maps_completed': 7,
                'total_value': 15.4,
                'runtime': {'hours': 2, 'minutes': 15}
            }
            
            dummy_map = {
                'map_name': 'Cemetery of the Eternals',
                'level': 72
            }
            
            return self.overlay_manager._create_item_table_html(
                dummy_added, dummy_removed, 3.3, dummy_session, dummy_map
            )
        
        @self.app.route('/test/session_stats')
        def test_session_stats():
            """Test session stats with dummy data"""
            dummy_stats = {
                'maps_completed': 12,
                'total_value': 28.7,
                'runtime': {'hours': 3, 'minutes': 42}
            }
            
            return self.overlay_manager._create_session_overlay_html(dummy_stats)
    
    def update_item_table(self, added_items: list, removed_items: list, 
                         session_stats: Optional[Dict] = None, map_info: Optional[Dict] = None):
        """Update item table data (called from main tracker)"""
        total_value = sum(item.get('value_exalted', 0) for item in added_items)
        
        self.current_data['item_table'] = {
            'added_items': added_items,
            'removed_items': removed_items,
            'total_value': total_value,
            'session_stats': session_stats,
            'map_info': map_info
        }
        self.current_data['last_update'] = time.time()
        
        # No need for auto-refresh since OBS will fetch updated data on next request
    
    def update_session_stats(self, session_stats: Dict):
        """Update session statistics (called from main tracker)"""
        self.current_data['session_stats'] = session_stats
        self.current_data['last_update'] = time.time()
        
        # No need for auto-refresh since OBS will fetch updated data on next request
    
    def start_server(self, debug: bool = False, open_browser: bool = False):
        """Start the Flask server"""
        if open_browser:
            # Open browser after a short delay
            def open_browser_delayed():
                time.sleep(1.5)
                webbrowser.open(f'http://{self.host}:{self.port}')
            
            browser_thread = threading.Thread(target=open_browser_delayed)
            browser_thread.daemon = True
            browser_thread.start()
        
        print(f"🌐 Starting OBS Web Server...")
        print(f"📺 OBS Browser Source URLs:")
        print(f"   Item Table: http://{self.host}:{self.port}/obs/item_table")
        print(f"   Session Stats: http://{self.host}:{self.port}/obs/session_stats")
        print(f"🔧 Setup Instructions: http://{self.host}:{self.port}")
        
        # Suppress Flask request logs when not in debug mode and quiet mode is enabled
        if not debug and self.quiet_mode:
            import logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
        
        self.app.run(host=self.host, port=self.port, debug=debug)
    
    def start_background(self):
        """Start server in background thread"""
        def run_server():
            # Suppress Flask request logs if quiet mode is enabled
            if self.quiet_mode:
                import logging
                log = logging.getLogger('werkzeug')
                log.setLevel(logging.ERROR)
            
            self.app.run(host=self.host, port=self.port, debug=False)
        
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        print(f"🌐 OBS Web Server started in background on http://{self.host}:{self.port}")
        return server_thread


# Standalone server for testing
def main():
    """Run standalone OBS web server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PoE Stats OBS Web Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--browser', action='store_true', help='Open browser automatically')
    
    args = parser.parse_args()
    
    server = OBSWebServer(host=args.host, port=args.port)
    
    try:
        server.start_server(debug=args.debug, open_browser=args.browser)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


if __name__ == "__main__":
    main()