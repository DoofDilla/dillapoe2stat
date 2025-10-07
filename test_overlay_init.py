#!/usr/bin/env python3
"""Test KISS Overlay initialization and file creation"""

from config import Config
from overlay_state_writer import OverlayStateWriter
from notification_manager import NotificationManager
from game_state import GameState
import os

print("=" * 50)
print("KISS Overlay Test")
print("=" * 50)

# Check config
config = Config()
print(f"\n1. Config Check:")
print(f"   KISS_OVERLAY_ENABLED: {config.KISS_OVERLAY_ENABLED}")
print(f"   KISS_OVERLAY_STATE_FILE: {config.KISS_OVERLAY_STATE_FILE}")

# Initialize writer
print(f"\n2. Initialize OverlayStateWriter:")
try:
    writer = OverlayStateWriter(
        state_file=config.KISS_OVERLAY_STATE_FILE
    )
    print(f"   ✅ Writer initialized")
    print(f"   State file path: {writer.state_file}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Get template variables
print(f"\n3. Get template variables:")
try:
    notification_manager = NotificationManager(config)
    game_state = GameState()
    template_vars = notification_manager.get_template_variables(game_state)
    print(f"   ✅ Got {len(template_vars)} variables")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Write overlay state
print(f"\n4. Write overlay state:")
try:
    writer.update(
        current_phase='pre_snapshot',
        template_variables=template_vars
    )
    print(f"   ✅ State written")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Check if file exists
print(f"\n5. Check file creation:")
if os.path.exists(config.KISS_OVERLAY_STATE_FILE):
    print(f"   ✅ File created: {config.KISS_OVERLAY_STATE_FILE}")
    file_size = os.path.getsize(config.KISS_OVERLAY_STATE_FILE)
    print(f"   File size: {file_size} bytes")
    
    # Read and display first few lines
    print(f"\n6. File contents (first 500 chars):")
    with open(config.KISS_OVERLAY_STATE_FILE, 'r', encoding='utf-8') as f:
        content = f.read(500)
        print(f"   {content}")
else:
    print(f"   ❌ File NOT created: {config.KISS_OVERLAY_STATE_FILE}")

print(f"\n{'=' * 50}")
print("✅ Test completed!")
print(f"{'=' * 50}")
