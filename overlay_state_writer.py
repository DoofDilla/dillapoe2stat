# overlay_state_writer.py
"""
Simple JSON file writer for KISS Overlay state
Reuses existing NotificationManager.get_template_variables()
"""

import json
import os
import time


PHASE_COLORS = {
    # PRE phases (green)
    'pre_snapshot': '#00ff88',
    'pre_parse': '#00ff88',
    'pre_update_state': '#00ff88',
    'pre_notify': '#00ff88',
    
    # POST phases (green, except Phase 5)
    'post_snapshot': '#00ff88',
    'post_diff': '#00ff88',
    'post_value': '#00ff88',
    'post_capture_session': '#00ff88',
    'post_update_session': '#ff6666',  # RED - critical phase!
    'post_notify': '#00ff88',
    'post_log': '#00ff88',
    'post_display': '#00ff88',
    'post_reset': '#00ff88',
    
    # Waystone analysis (blue)
    'waystone_analysis': '#88ccff'
}

PHASE_DISPLAY_NAMES = {
    'pre_snapshot': 'PRE-1: Snapshot',
    'pre_parse': 'PRE-2: Parse Map',
    'pre_update_state': 'PRE-3: Update State',
    'pre_notify': 'PRE-4: Notify',
    'post_snapshot': 'POST-1: Snapshot',
    'post_diff': 'POST-2: Diff Items',
    'post_value': 'POST-3: Value Items',
    'post_capture_session': 'POST-4: Capture Session',
    'post_update_session': 'POST-5: Update Session 🔴',
    'post_notify': 'POST-6: Notify',
    'post_log': 'POST-7: Log',
    'post_display': 'POST-8: Display',
    'post_reset': 'POST-9: Reset',
    'waystone_analysis': 'Waystone Analysis'
}


class OverlayStateWriter:
    """Writes overlay state to JSON file using notification template variables"""
    
    def __init__(self, state_file="overlay_state.json"):
        self.state_file = state_file
    
    def update(self, current_phase: str, template_variables: dict):
        """
        Write current phase + template variables to JSON
        
        Args:
            current_phase: Phase key (e.g. 'post_update_session')
            template_variables: Dict from NotificationManager.get_template_variables()
        """
        try:
            state = {
                "current_phase": current_phase,
                "phase_display_name": PHASE_DISPLAY_NAMES.get(current_phase, current_phase),
                "phase_color": PHASE_COLORS.get(current_phase, "#00ff88"),
                "timestamp": time.time(),
                "template_variables": template_variables
            }
            
            # Atomic write (write to temp, then rename)
            temp_file = f"{self.state_file}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            # Atomic rename (Windows-safe)
            if os.path.exists(self.state_file):
                os.remove(self.state_file)  # Windows needs this before rename
            os.rename(temp_file, self.state_file)
            
        except Exception as e:
            # Silent failure - overlay not critical for tracker
            pass
