#!/usr/bin/env python3
"""
Echter Emoji-Breiten-Test im Terminal
"""

print("🔍 ECHTER EMOJI-BREITEN-TEST")
print("=" * 40)

emojis = ['⚔️', '🟠', '💍', '🔷', '📜', '🏰', '✨', '🌟', '🏹', '🗡️']

print("Emoji-Darstellung mit Markern:")
for emoji in emojis:
    display = f"|{emoji}|"
    calculated_len = len(display)
    print(f"{display:<10} len={calculated_len}")

print(f"\n🎯 WENN ALLE GLEICH AUSSEHEN:")
print("Dann sind alle Emojis 2 characters breit im Terminal!")

print(f"\n🎯 WENN ⚔️ 🏹 BREITER AUSSEHEN:")
print("Dann ist mein wide_emoji Ansatz richtig!")

print(f"\n📏 STRING-LÄNGEN-TEST:")
test_strings = [
    "⚔️ Obliterator Bow",
    "🟠 Exalted Orb", 
    "💍 Gold Ring"
]

for s in test_strings:
    print(f"'{s}' → len={len(s)}")

print(f"\n💡 DEBUGGING-PLAN:")
print("1. Schaue dir die Ausgabe visuell an")
print("2. Wenn alle Emojis gleich breit aussehen → wide_emojis ist falsch")
print("3. Dann alle Emojis auf width=2 setzen")
print("4. Wenn ⚔️ breiter aussieht → Terminal-Font Problem")