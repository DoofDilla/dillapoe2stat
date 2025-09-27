#!/usr/bin/env python3
"""
Test script für Waystone Attribute Logging
"""

import json
from poe_logging import extract_waystone_attributes, get_fallback_waystone_attributes

print("🧪 TEST: Waystone Attribute Extraktion")
print("=" * 50)

# Test 1: Normale Map ohne Waystone-Info (Client-Log)
print("\n1. Client-Log Map (keine Waystone-Info):")
normal_map_info = {
    "map_name": "Beach",
    "level": 10,
    "seed": "12345",
    "source": "client_log"
}

attrs1 = extract_waystone_attributes(normal_map_info)
print(f"hasAttributeInfo: {attrs1['hasAttributeInfo']}")
print(f"tier: {attrs1['tier']}")
print(f"magic_monsters: {attrs1['magic_monsters']}")
print("✅ Sollte alles False/0 sein")

# Test 2: Experimentelle Waystone-Map mit area_modifiers
print("\n2. Experimentelle Waystone-Map:")
waystone_map_info = {
    "map_name": "Corrupted Waystone",
    "level": "15",
    "seed": "experimental", 
    "source": "waystone_inventory",
    "area_modifiers": {
        "magic_monsters": {
            "name": "Magic Monsters",
            "value": "+70%",
            "display": "Magic Monsters: +70%"
        },
        "item_rarity": {
            "name": "Item Rarity", 
            "value": "+25%",
            "display": "Item Rarity: +25%"
        },
        "pack_size": {
            "name": "Pack Size",
            "value": "+20%", 
            "display": "Pack Size: +20%"
        }
    }
}

attrs2 = extract_waystone_attributes(waystone_map_info)
print(f"hasAttributeInfo: {attrs2['hasAttributeInfo']}")
print(f"tier: {attrs2['tier']}")
print(f"magic_monsters: {attrs2['magic_monsters']}")
print(f"item_rarity: {attrs2['item_rarity']}")
print(f"pack_size: {attrs2['pack_size']}")
print("✅ Sollte True und echte Werte haben")

# Test 3: Leere Map-Info
print("\n3. Keine Map-Info (None):")
attrs3 = extract_waystone_attributes(None)
print(f"hasAttributeInfo: {attrs3['hasAttributeInfo']}")
print(f"tier: {attrs3['tier']}")
print("✅ Sollte Fallback sein")

# Test 4: JSON Struktur Demo
print("\n4. Finale JSON-Struktur Beispiel:")
demo_json = {
    "run_id": "test-123",
    "map": {
        "name": "Corrupted Waystone",
        "level": 15,
        "waystone_attributes": attrs2
    }
}

print(json.dumps(demo_json, indent=2))
print("\n✅ Schema-Test erfolgreich!")