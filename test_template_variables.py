#!/usr/bin/env python3
"""Test NotificationManager.get_template_variables method"""

from notification_manager import NotificationManager
from game_state import GameState
from config import Config

# Initialize
config = Config()
notification_manager = NotificationManager(config)
game_state = GameState()

# Add some test data to game state
game_state.update_map_info({
    'name': 'Test Map',
    'tier': 80,
    'mods': []
})

# Get template variables
try:
    template_vars = notification_manager.get_template_variables(game_state)
    
    print("✅ get_template_variables() works!")
    print(f"\nTotal variables: {len(template_vars)}")
    print("\nSample variables:")
    for key in sorted(list(template_vars.keys())[:10]):
        print(f"  {key}: {template_vars[key]}")
    
    print("\n✅ Test passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
