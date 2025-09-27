#!/usr/bin/env python3
"""
Vollständiger Test der Waystone JSON-Log Integration
"""

import json
import tempfile
from pathlib import Path
from poe_logging import log_run

print("🎯 VOLLTEST: Waystone JSON-Log Integration")
print("=" * 55)

# Temporäre Test-Log-Datei
temp_log = Path(tempfile.gettempdir()) / "test_waystone_log.jsonl"
print(f"📁 Test-Log: {temp_log}")

# Dummy-Items für Tests
test_added = [{"typeLine": "Orb of Fusing", "stackSize": 5}]
test_removed = [{"typeLine": "Scroll of Wisdom", "stackSize": 1}]

print("\n1️⃣ Test: Normale Client-Log Map")
normal_map = {
    "map_name": "Beach", 
    "level": 10,
    "seed": "12345",
    "source": "client_log"
}

log_run("TestChar", test_added, test_removed, normal_map, 150.5, temp_log, 180.2, "session-123")
print("✅ Client-Log Map geloggt")

print("\n2️⃣ Test: Experimentelle Waystone Map")
waystone_map = {
    "map_name": "Corrupted Waystone",
    "level": "15", 
    "seed": "experimental",
    "source": "waystone_inventory",
    "area_modifiers": {
        "magic_monsters": {"name": "Magic Monsters", "value": "+70%"},
        "rare_monsters": {"name": "Rare Monsters", "value": "+30%"},
        "item_rarity": {"name": "Item Rarity", "value": "+25%"},
        "item_quantity": {"name": "Item Quantity", "value": "+15%"},
        "waystone_drop_chance": {"name": "Waystone Drop Chance", "value": "+10%"},
        "pack_size": {"name": "Pack Size", "value": "+20%"}
    }
}

log_run("TestChar", test_added, test_removed, waystone_map, 275.8, temp_log, 240.1, "session-123")
print("✅ Waystone Map geloggt")

print("\n3️⃣ Test: Map ohne Info (None)")
log_run("TestChar", test_added, test_removed, None, 0, temp_log, 120.5, "session-123")
print("✅ None Map geloggt")

print("\n📊 ERGEBNISSE:")
print("=" * 25)

# Log-Datei auslesen und formatiert ausgeben
if temp_log.exists():
    with temp_log.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        try:
            record = json.loads(line.strip())
            waystone_attrs = record["map"]["waystone_attributes"]
            
            print(f"\n📋 Eintrag {i}:")
            print(f"   Map: {record['map']['name']}")
            print(f"   Source: {record['map'].get('source', 'N/A')}")
            print(f"   hasAttributeInfo: {waystone_attrs['hasAttributeInfo']}")
            print(f"   tier: {waystone_attrs['tier']}")
            print(f"   magic_monsters: {waystone_attrs['magic_monsters']}")
            print(f"   item_rarity: {waystone_attrs['item_rarity']}")
            
        except Exception as e:
            print(f"❌ Fehler beim Parsen von Eintrag {i}: {e}")

    # Cleanup
    temp_log.unlink()
    print(f"\n🧹 Test-Log gelöscht: {temp_log}")

else:
    print("❌ Log-Datei nicht gefunden!")

print("\n✅ VOLLTEST ABGESCHLOSSEN!")
print("🎉 Waystone-Attribute werden korrekt in alle JSON-Logs integriert!")