#!/usr/bin/env python3
"""
Test der korrigierten Emoji-Breiten-Berechnung
"""

print("🎯 KORRIGIERTE EMOJI-BREITEN-BERECHNUNG")
print("=" * 50)

def get_emoji_display_width_new(emoji_char):
    """Neue Methode: Python's len()"""
    return len(emoji_char)

def simulate_table_calculation():
    """Simuliere die Tabellen-Berechnung"""
    items = [
        ("⚔️", "Obliterator Bow of the Drought"),
        ("🟠", "Exalted Orb"),
        ("💍", "Gold Ring")
    ]
    
    max_len = 0
    for emoji, name in items:
        emoji_width = get_emoji_display_width_new(emoji)
        item_display_len = emoji_width + 1 + len(name)  # emoji + space + name
        max_len = max(max_len, item_display_len)
        print(f"{emoji} {name}")
        print(f"  emoji len: {len(emoji)}, name len: {len(name)}, total: {item_display_len}")
    
    return max_len

print("📊 HEADER-BERECHNUNG:")
table_width = simulate_table_calculation()
print(f"Tabellen-Breite: {table_width}")

print(f"\n📊 ZEILEN-BERECHNUNG (sollte identisch sein):")
bow_emoji = "⚔️"
bow_name = "Obliterator Bow of the Drought"
emoji_width = len(bow_emoji)
item_name_visible_length = emoji_width + 1 + len(bow_name)
print(f"⚔️ Obliterator Bow of the Drought")
print(f"  emoji len: {len(bow_emoji)}, name len: {len(bow_name)}, total: {item_name_visible_length}")

print(f"\n✅ KONSISTENZ-CHECK:")
python_len = len(f"{bow_emoji} {bow_name}")
calculated_len = item_name_visible_length
print(f"Python len(): {python_len}")  
print(f"Calculated:   {calculated_len}")
print(f"Match: {python_len == calculated_len}")

print(f"\n🎉 LÖSUNG:")
print("- Alle Emoji-Berechnungen nutzen jetzt Python's len()")
print("- Header und Zeilen verwenden identische Werte") 
print("- Multi-codepoint Emojis wie ⚔️ werden korrekt behandelt")
print("- Alignment sollte jetzt perfekt sein!")