#!/usr/bin/env python3
"""
Systematische Debug-Analyse der Emoji-Padding-Problems
"""

print("🔍 SYSTEMATISCHE DEBUG-ANALYSE")
print("=" * 50)

# Simuliere was bei den Bows passiert
bow_name = "Obliterator Bow of the Drought"
bow_emoji = "⚔️"

def simulate_old_method():
    """Alte Methode ohne Emoji-Breiten-Berücksichtigung"""
    item_name_visible = f"{bow_emoji} {bow_name}"
    return len(item_name_visible), item_name_visible

def simulate_new_method():
    """Neue Methode mit Emoji-Breiten"""
    wide_emojis = ['⚔️', '🏹', '🗡️', '🔱', '⚔', '🛡️', '🏹']
    emoji_width = 3 if bow_emoji in wide_emojis else 2
    item_name_visible_length = emoji_width + 1 + len(bow_name)
    return item_name_visible_length, f"{bow_emoji} {bow_name}"

print("🎯 SIMULATION:")
print(f"Bow Name: '{bow_name}'")
print(f"Bow Emoji: '{bow_emoji}'")
print(f"len(bow_name): {len(bow_name)}")

old_len, old_display = simulate_old_method()
new_len, new_display = simulate_new_method()

print(f"\n📊 ALTE METHODE:")
print(f"  Display: '{old_display}'")
print(f"  len(display): {old_len}")

print(f"\n📊 NEUE METHODE:")
print(f"  Display: '{new_display}'")  
print(f"  calculated length: {new_len}")

print(f"\n🤔 PROBLEM-DIAGNOSE:")
print(f"  - Alter Wert: {old_len}")
print(f"  - Neuer Wert: {new_len}")
print(f"  - Unterschied: {new_len - old_len}")

print(f"\n🎯 WAS KÖNNTE SCHIEF GEHEN:")
print("1. Emoji wird in Terminal anders dargestellt als berechnet")
print("2. Terminal-Font zeigt ⚔️ nicht als 3 chars breit")
print("3. Header-Berechnung und Zeilen-Berechnung nutzen verschiedene Werte")
print("4. Die wide_emojis Liste enthält nicht das richtige Zeichen")

print(f"\n🔍 EMOJI-ANALYSE:")
print(f"  Emoji bytes: {bow_emoji.encode('utf-8')}")
print(f"  Emoji repr: {repr(bow_emoji)}")
print(f"  Ist in wide_emojis: {'⚔️' in ['⚔️', '🏹', '🗡️', '🔱', '⚔', '🛡️', '🏹']}")

print(f"\n💡 NÄCHSTE SCHRITTE:")
print("1. Überprüfen ob Header-Berechnung tatsächlich neue Funktion nutzt")
print("2. Prüfen ob Emoji-Character exakt übereinstimmt")
print("3. Eventuell width auf 2 reduzieren und sehen ob es dann funktioniert")
print("4. Debug-Output in echte Funktion einbauen")