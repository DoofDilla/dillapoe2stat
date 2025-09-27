#!/usr/bin/env python3
"""
Test der tatsächlichen Emoji-Längen
"""

# Verschiedene Emoji-Arten testen
emojis_to_test = {
    'sword': '⚔️',
    'orb': '🟠', 
    'ring': '💍',
    'gem': '🔷'
}

print("🔍 EMOJI-LÄNGEN DEBUG")
print("=" * 30)

for name, emoji in emojis_to_test.items():
    print(f"{name}: '{emoji}'")
    print(f"  len(): {len(emoji)}")
    print(f"  repr(): {repr(emoji)}")
    print(f"  bytes: {emoji.encode('utf-8')}")
    print()

# Test mit echten Item-Namen
print("📊 ITEM-LÄNGEN TEST:")
items = [
    ('⚔️', 'Obliterator Bow of the Drought'),
    ('🟠', 'Exalted Orb'),
    ('💍', 'Gold Ring')
]

for emoji, name in items:
    full_display = f"{emoji} {name}"
    emoji_len = len(emoji)
    name_len = len(name)
    total_len = len(full_display)
    calculated_len = emoji_len + 1 + name_len
    
    print(f"'{full_display}'")
    print(f"  emoji len: {emoji_len}, name len: {name_len}")
    print(f"  total len(): {total_len}, calculated: {calculated_len}")
    print(f"  match: {total_len == calculated_len}")
    print()