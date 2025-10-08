#!/usr/bin/env python3
"""Test script for KISS overlay templates"""

from kiss_overlay_templates import get_template_for_phase

# Test data
test_vars = {
    'phase_name': 'TEST Phase',
    'waystone_tier': '15',
    'waystone_delirious': '30',
    'waystone_pack_size': '25',
    'session_maps_completed': '5',
    'session_value_per_hour_fmt': '1200ex/h',
    'session_runtime_str': '1h 23m',
    'map_value_fmt': '45.2ex',
    'map_name': 'Cemetery of the Eternals',
    'map_drop_1_name': 'Divine Orb',
    'map_drop_1_value_fmt': '400c',
    'session_drop_1_name': 'Exalted Orb',
    'session_drop_1_value_fmt': '1.0ex'
}

print("=" * 50)
print("TEST 1: Default Phase")
print("=" * 50)
result = get_template_for_phase('default', 'POST-8: Display', test_vars)
print(result)

print("\n" + "=" * 50)
print("TEST 2: PRE Snapshot")
print("=" * 50)
result = get_template_for_phase('pre_snapshot', 'PRE-1: Snapshot', test_vars)
print(result)

print("\n" + "=" * 50)
print("TEST 3: POST Update Session")
print("=" * 50)
result = get_template_for_phase('post_update_session', 'POST-5: Update', test_vars)
print(result)

print("\n" + "=" * 50)
print("TEST 4: Waystone Analysis")
print("=" * 50)
waystone_vars = {
    'waystone_name': 'Waystone of the Cemetery',
    'waystone_tier': '15',
    'waystone_delirious': '30',
    'waystone_prefixes': '2',
    'waystone_suffixes': '3',
    'pack_size': '25',
    'magic_monsters': '40',
    'rare_monsters': '20',
    'item_rarity': '50',
    'waystone_drop_chance': '130',
    'session_maps_completed': '10',
    'session_value_per_hour_fmt': '1500ex/h',
    'session_avg_value_fmt': '35.5ex'
}
result = get_template_for_phase('waystone_analysis', 'Waystone Analysis', waystone_vars)
print(result)

print("\n" + "=" * 50)
print("✅ All tests completed!")
print("=" * 50)
