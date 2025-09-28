"""
Test-Skript für den Gear Rarity Analyzer mit echten POE API Daten

Dieses Skript lädt die Konfiguration und testet den Gear Rarity Analyzer
mit einem echten Character.
"""

import sys
import os
from config import Config
from gear_rarity_analyzer import GearRarityAnalyzer
from poe_api import get_token

def test_with_real_character():
    """Testet den Gear Rarity Analyzer mit echten API-Daten"""
    print("Lade Konfiguration...")
    
    try:
        # Konfiguration aus Config-Klasse laden
        client_id = Config.CLIENT_ID
        client_secret = Config.CLIENT_SECRET
        
        if not client_id or not client_secret:
            print("FEHLER: client_id oder client_secret nicht in der Konfiguration gefunden!")
            print("Stelle sicher, dass config.py korrekt konfiguriert ist.")
            return False
        
        print("Hole OAuth Token...")
        # Token holen
        access_token = get_token(client_id, client_secret)
        
        print("Initialisiere Gear Rarity Analyzer...")
        # Analyzer erstellen
        analyzer = GearRarityAnalyzer(access_token)
        
        # Character-Name aus Config oder Standard
        character_name = Config.CHAR_TO_CHECK
        print(f"Verwende Character aus Konfiguration: {character_name}")
        
        print(f"Analysiere Character: {character_name}")
        print("-" * 60)
        
        # Gear Rarity Analyse durchführen
        analyzer.print_rarity_summary(character_name)
        
        # Zusätzlich auch die rohen Daten anzeigen
        print("\n" + "="*60)
        print("Rohe Analyse-Daten:")
        result = analyzer.calculate_total_gear_rarity(character_name)
        
        if result.get("success"):
            print(f"Character: {result['character_name']}")
            print(f"Gesamt-Rarity-Bonus: {result['total_rarity_bonus']}%")
            print(f"Equipment-Items: {result['equipment_count']}")
            print(f"Items mit Rarity: {result['items_with_rarity']}")
            
            if result['item_details']:
                print("\nItem-Details:")
                for item in result['item_details']:
                    print(f"  {item['name']}: {item['rarity_total']}% (Mods: {item['rarity_mods']})")
        else:
            print(f"Fehler: {result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"FEHLER beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_mod_patterns():
    """Testet verschiedene Varianten von Rarity-Mod-Texten"""
    print("\nTeste verschiedene Mod-Pattern...")
    print("-" * 40)
    
    analyzer = GearRarityAnalyzer("dummy_token")
    
    # Verschiedene Varianten von Rarity-Mods testen
    test_cases = [
        "15% increased rarity of items found",
        "25% Increased Rarity of Items Found",  # Großbuchstaben
        "8% increased rarity of items found",   # Einstellig
        "100% increased rarity of items found", # Dreistellig
        "12% increased Rarity Of Items Found",  # Gemischte Großschreibung
        "5% inc rarity of items found",         # Falsch - sollte nicht matchen
        "20% increased quantity of items found", # Falsch - quantity nicht rarity
    ]
    
    for i, mod_text in enumerate(test_cases, 1):
        test_item = {
            "name": f"Test Item {i}",
            "explicitMods": [mod_text]
        }
        
        rarity_mods = analyzer.find_rarity_mods_in_item(test_item)
        expected = "12% increased Rarity Of Items Found" in mod_text or any(pattern in mod_text.lower() for pattern in ["15%", "25%", "8%", "100%"])
        
        print(f"Test {i}: '{mod_text}'")
        print(f"  Gefunden: {rarity_mods}")
        print(f"  Summe: {sum(rarity_mods)}%")
        
        if "inc rarity" in mod_text or "quantity" in mod_text:
            if not rarity_mods:
                print("  -> Korrekt: Kein Match (wie erwartet)")
            else:
                print("  -> FEHLER: Sollte nicht matchen!")
        else:
            if rarity_mods:
                print("  -> Korrekt: Match gefunden")
            else:
                print("  -> FEHLER: Sollte matchen!")
        print()

if __name__ == "__main__":
    print("=== Gear Rarity Analyzer Test ===")
    print("1. Pattern-Tests")
    test_different_mod_patterns()
    
    print("\n2. Test mit echten API-Daten")
    if len(sys.argv) > 1 and sys.argv[1] == "--skip-api":
        print("API-Test übersprungen (--skip-api Parameter)")
    else:
        success = test_with_real_character()
        if not success:
            print("Füge '--skip-api' Parameter hinzu um nur Pattern-Tests auszuführen.")