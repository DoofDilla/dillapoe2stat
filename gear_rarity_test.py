"""
Einfaches Skript zum Testen der Gear Rarity Analyse mit echten Daten

Führe dieses Skript aus um die Item Rarity deines Characters zu berechnen.
"""

from config import Config
from gear_rarity_analyzer import GearRarityAnalyzer
from poe_api import get_token

def main():
    """Hauptfunktion"""
    print("=== POE Gear Rarity Analyzer ===")
    print()
    
    try:
        # Token holen
        print("Hole OAuth Token...")
        access_token = get_token(Config.CLIENT_ID, Config.CLIENT_SECRET)
        
        # Analyzer initialisieren
        print("Initialisiere Analyzer...")
        analyzer = GearRarityAnalyzer(access_token)
        
        # Character aus Config verwenden
        character_name = Config.CHAR_TO_CHECK
        print(f"Analysiere Character: {character_name}")
        print()
        
        # Analyse durchführen und anzeigen
        # Debug-Modus aktivieren um alle Equipment-Items zu sehen
        print("=== NORMALE ANALYSE ===")
        analyzer.print_rarity_summary(character_name)
        
        print("\n" + "="*60)
        print("=== DEBUG: ALLE EQUIPMENT-ITEMS ===")
        analyzer.print_rarity_summary(character_name, debug=True)
        
        # Zusätzlicher Deep-Debug für Items mit "rarity" im Namen oder Mods
        print("\n" + "="*60)
        print("=== DEEP DEBUG: MOD-PARSING ===")
        character_data = analyzer.get_character_equipment(character_name)
        equipment_items = analyzer.extract_equipment_items(character_data)
        
        for item in equipment_items:
            item_name = item.get("name", item.get("typeLine", "Unknown Item"))
            
            # Prüfe alle Mods nach "rarity"
            has_rarity_text = False
            all_mods = []
            
            for mod_type in ["explicitMods", "implicitMods", "craftedMods", "enchantMods"]:
                mods = item.get(mod_type, [])
                for mod in mods:
                    if isinstance(mod, str):
                        all_mods.append(f"{mod_type}: {mod}")
                        if "rarity" in mod.lower():
                            has_rarity_text = True
            
            if has_rarity_text:
                print(f"\n>>> Item mit 'rarity' Text gefunden: {item_name}")
                analyzer.find_rarity_mods_in_item(item, debug=True)
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()