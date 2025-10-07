#!/usr/bin/env python3
"""Test overlay templates with mock data"""

from kiss_overlay_templates import get_template_for_phase

# Mock template variables (same as notifications)
mock_vars = {
    "waystone_tier": "80",
    "waystone_delirious": "15",
    "waystone_pack_size": "20",
    "session_maps_completed": "5",
    "session_value_per_hour_fmt": "1440ex/h",
    "session_runtime_str": "1h 23m",
    "map_name": "Hideout Felled",
    "map_tier": "80",
    "map_value_fmt": "123.5ex",
    "map_drop_1_name": "Mirror Shard",
    "map_drop_1_value_fmt": "150ex",
    "session_drop_1_name": "Mirror Shard",
    "session_drop_1_value_fmt": "150ex"
}

# Test different phases
phases = [
    ('pre_snapshot', 'PRE-1: Snapshot'),
    ('pre_parse', 'PRE-2: Parse Map'),
    ('post_update_session', 'POST-5: Update Session 🔴'),
    ('waystone_analysis', 'Waystone Analysis'),
    ('post_display', 'POST-8: Display')  # Generic template
]

for phase, phase_name in phases:
    print(f"\n{'='*40}")
    print(f"Phase: {phase}")
    print(f"{'='*40}")
    text = get_template_for_phase(phase, phase_name, mock_vars)
    print(text)
    print()
