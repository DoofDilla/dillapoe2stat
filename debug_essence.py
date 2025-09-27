#!/usr/bin/env python3
"""
Debug Test für Essence Werte
"""

# Simuliere was bei der Greater Essence of Electricity passiert
essence_chaos_value = 0  # Das sehen wir im Screenshot

print("🔍 DEBUG: Essence Wert-Behandlung")
print("=" * 40)

def get_plain_value_old(val, suffix):
    """Alte Version"""
    if not val or val < 0.005:
        return "-"
    formatted = f"{val:.2f}".rstrip("0").rstrip(".")
    if formatted.startswith("0."):
        formatted = formatted[1:]
    return f"{formatted} {suffix}"

def get_plain_value_new(val, suffix):
    """Neue Version"""
    if val is None or val == 0:
        return "-"
    if val < 0.005:
        return "-"
    formatted = f"{val:.2f}".rstrip("0").rstrip(".")
    if formatted.startswith("0."):
        formatted = formatted[1:]
    return f"{formatted} {suffix}"

def format_colored_number_sim(value, precision=2, suffix=""):
    """Simulation der _format_colored_number"""
    if value is None or value == 0:
        return "-"
    # Rest der Logik...
    return f"formatted {suffix}"

print(f"Essence Chaos Value: {essence_chaos_value}")
print(f"Alte get_plain_value: '{get_plain_value_old(essence_chaos_value, 'c')}'")
print(f"Neue get_plain_value: '{get_plain_value_new(essence_chaos_value, 'c')}'")
print(f"format_colored_number: '{format_colored_number_sim(essence_chaos_value, 2, 'c')}'")

print("\n🔍 Test verschiedener Werte:")
test_values = [0, 0.001, 0.004, 0.005, 0.06]
for val in test_values:
    print(f"Value {val}: old='{get_plain_value_old(val, 'c')}' new='{get_plain_value_new(val, 'c')}'")

print("\n✅ Das Problem könnte sein, dass der Wert nicht exakt 0 ist")
print("🎯 Schauen wir uns an was der Screenshot tatsächlich zeigt...")