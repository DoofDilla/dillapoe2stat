"""
Gear Rarity Analyzer - Berechnet die Gesamt-Item-Rarity vom Character Equipment

Dieses Modul analysiert das getragene Equipment eines Characters und summiert
alle "XX% increased rarity of items found" Modifikatoren auf.
"""

import re
import json
from typing import Dict, List, Optional, Union
from poe_api import get_character_details

class GearRarityAnalyzer:
    """Analysiert das Equipment eines Characters für Item Rarity Boni"""
    
    # Regex Pattern für "X% increased rarity of items found" Mods
    # POE API nutzt Localization Tags wie [ItemRarity|Rarity of Items]
    RARITY_MOD_PATTERN = re.compile(
        r'(\d+)%\s+increased\s+(?:\[ItemRarity\|)?(?:rarity\s+of\s+items|Rarity\s+of\s+Items)(?:\])?(?:\s+found)?',
        re.IGNORECASE
    )
    
    def __init__(self, access_token: str):
        """
        Initialisiert den Analyzer mit einem gültigen POE API Access Token
        
        Args:
            access_token: Gültiger OAuth Token für die POE API
        """
        self.access_token = access_token
    
    def get_character_equipment(self, character_name: str) -> Dict:
        """
        Holt die Character-Details inklusive Equipment von der POE API
        
        Args:
            character_name: Name des Characters
            
        Returns:
            Character-Details Dictionary von der API
        """
        return get_character_details(self.access_token, character_name)
    
    def extract_equipment_items(self, character_data: Dict) -> List[Dict]:
        """
        Extrahiert die Equipment-Items aus den Character-Daten
        
        Args:
            character_data: Character-Daten von der API
            
        Returns:
            Liste der Equipment-Items (nicht Inventory)
        """
        character = character_data.get("character", {})
        equipment = []
        
        # Variante 1: Direktes 'equipment' Array
        direct_equipment = character.get("equipment", [])
        if direct_equipment:
            equipment.extend(direct_equipment)
        
        # Variante 2: Items mit 'equipped' Flag
        all_items = character.get("items", [])
        if all_items:
            equipped_items = [item for item in all_items if item.get("equipped", False)]
            equipment.extend(equipped_items)
        
        # Variante 3: Items mit speziellen inventoryId (Equipment-Slots)
        # Bekannte Equipment-InventoryIds in POE
        equipment_inventory_ids = {
            "Helm", "Helmet", "BodyArmour", "Gloves", "Boots", 
            "MainHand", "OffHand", "Weapon", "Weapon2", "Shield",
            "Belt", "Amulet", "Ring", "Ring2", "LeftRing", "RightRing",
            "Flask", "Flask2", "Flask3", "Flask4", "Flask5"
        }
        
        if all_items:
            for item in all_items:
                inventory_id = item.get("inventoryId", "")
                if inventory_id in equipment_inventory_ids:
                    # Prüfe ob nicht schon in der Liste (Duplikate vermeiden)
                    item_id = item.get("id", "")
                    if not any(eq.get("id", "") == item_id for eq in equipment if item_id):
                        equipment.append(item)
        
        return equipment
    
    def find_rarity_mods_in_item(self, item: Dict, debug: bool = False) -> List[int]:
        """
        Findet alle "increased rarity of items found" Mods in einem Item
        
        Args:
            item: Item-Dictionary von der API
            debug: Wenn True, druckt Debug-Informationen
            
        Returns:
            Liste der gefundenen Rarity-Werte (als Integer)
        """
        rarity_values = []
        item_name = item.get("name", item.get("typeLine", "Unknown Item"))
        
        if debug:
            print(f"\n--- DEBUG: Analysiere Item '{item_name}' ---")
        
        # Alle Mod-Typen durchsuchen
        mod_types = [
            ("explicitMods", item.get("explicitMods", [])),
            ("implicitMods", item.get("implicitMods", [])),
            ("craftedMods", item.get("craftedMods", [])),
            ("enchantMods", item.get("enchantMods", [])),  # Zusätzlich auch enchantMods prüfen
        ]
        
        for mod_type_name, mods in mod_types:
            if debug and mods:
                print(f"  {mod_type_name}: {len(mods)} Mods")
            
            for i, mod in enumerate(mods):
                if isinstance(mod, str):
                    if debug:
                        print(f"    [{i}] '{mod}'")
                    
                    matches = self.RARITY_MOD_PATTERN.findall(mod)
                    if matches:
                        rarity_values.extend([int(match) for match in matches])
                        if debug:
                            print(f"      -> MATCH: {matches}")
                    else:
                        # Zusätzliche Debug-Info: Prüfe ob "rarity" im Text vorkommt
                        if debug and "rarity" in mod.lower():
                            print(f"      -> Enthält 'rarity' aber kein Match mit Pattern")
        
        if debug:
            print(f"  Gesamt gefundene Rarity-Werte: {rarity_values}")
        
        return rarity_values
    
    def calculate_total_gear_rarity(self, character_name: str) -> Dict:
        """
        Berechnet die Gesamt-Item-Rarity vom Equipment eines Characters
        
        Args:
            character_name: Name des Characters
            
        Returns:
            Dictionary mit Ergebnissen der Analyse
        """
        try:
            # Character-Daten holen
            character_data = self.get_character_equipment(character_name)
            
            # Equipment-Items extrahieren
            equipment_items = self.extract_equipment_items(character_data)
            
            total_rarity = 0
            item_details = []
            
            # Durch alle Equipment-Items iterieren
            for item in equipment_items:
                item_name = item.get("name", item.get("typeLine", "Unknown Item"))
                item_type = item.get("typeLine", "Unknown Type")
                inventory_id = item.get("inventoryId", "Unknown Slot")
                
                # Rarity-Mods in diesem Item finden
                rarity_mods = self.find_rarity_mods_in_item(item)
                item_rarity_total = sum(rarity_mods)
                
                if rarity_mods:
                    item_details.append({
                        "name": item_name,
                        "type": item_type,
                        "slot": inventory_id,
                        "rarity_mods": rarity_mods,
                        "rarity_total": item_rarity_total
                    })
                    total_rarity += item_rarity_total
            
            # Debug-Info: Alle Equipment-Items sammeln
            all_equipment_info = []
            for item in equipment_items:
                item_name = item.get("name", item.get("typeLine", "Unknown Item"))
                item_type = item.get("typeLine", "Unknown Type")
                inventory_id = item.get("inventoryId", "Unknown Slot")
                
                all_equipment_info.append({
                    "name": item_name,
                    "type": item_type,
                    "slot": inventory_id,
                    "has_rarity": len(self.find_rarity_mods_in_item(item)) > 0
                })
            
            return {
                "character_name": character_name,
                "total_rarity_bonus": total_rarity,
                "equipment_count": len(equipment_items),
                "items_with_rarity": len(item_details),
                "item_details": item_details,
                "all_equipment": all_equipment_info,  # Debug-Info
                "success": True
            }
            
        except Exception as e:
            return {
                "character_name": character_name,
                "error": str(e),
                "success": False
            }
    
    def print_rarity_summary(self, character_name: str, debug: bool = False) -> None:
        """
        Druckt eine schöne Zusammenfassung der Item Rarity Analyse
        
        Args:
            character_name: Name des Characters
            debug: Wenn True, zeigt alle Equipment-Items (auch ohne Rarity)
        """
        result = self.calculate_total_gear_rarity(character_name)
        
        if not result.get("success", False):
            print(f"FEHLER bei der Analyse von {character_name}: {result.get('error', 'Unbekannter Fehler')}")
            return
        
        print(f"\nItem Rarity Analyse für Character: {character_name}")
        print("=" * 60)
        print(f"Gesamt-Item-Rarity-Bonus: {result['total_rarity_bonus']}%")
        print(f"Equipment-Items analysiert: {result['equipment_count']}")
        print(f"Items mit Rarity-Boni: {result['items_with_rarity']}")
        
        if debug and result.get('all_equipment'):
            print("\nAlle Equipment-Items (Debug):")
            print("-" * 60)
            for item in result['all_equipment']:
                rarity_marker = " [RARITY]" if item['has_rarity'] else ""
                print(f"  - {item['name']} ({item['slot']}){rarity_marker}")
                print(f"    Typ: {item['type']}")
                print()
        
        if result['item_details']:
            print("\nDetails der Items mit Rarity-Boni:")
            print("-" * 60)
            for item in result['item_details']:
                mods_str = " + ".join([f"{mod}%" for mod in item['rarity_mods']])
                print(f"  - {item['name']}")
                print(f"    Typ: {item['type']}")
                print(f"    Slot: {item['slot']}")
                print(f"    Rarity: {mods_str} = {item['rarity_total']}%")
                print()
        else:
            print("\nKeine Items mit 'increased rarity of items found' Mods gefunden.")


def test_gear_rarity_analyzer():
    """Test-Funktion für den Gear Rarity Analyzer"""
    print("Test des Gear Rarity Analyzers")
    print("=" * 50)
    
    # Test-Item mit verschiedenen Mod-Varianten
    test_item = {
        "name": "Test Ring",
        "typeLine": "Gold Ring",
        "explicitMods": [
            "15% increased rarity of items found",
            "+20 to maximum Life",
            "Adds 1-3 Lightning Damage to Attacks"
        ],
        "implicitMods": [
            "5% increased rarity of items found"
        ],
        "craftedMods": [
            "10% increased rarity of items found"
        ]
    }
    
    # Analyzer ohne Token für Test
    analyzer = GearRarityAnalyzer("test_token")
    
    # Test der Mod-Extraktion
    rarity_mods = analyzer.find_rarity_mods_in_item(test_item)
    expected_total = 15 + 5 + 10  # 30%
    
    print(f"Test-Item: {test_item['name']}")
    print(f"Gefundene Rarity-Mods: {rarity_mods}")
    print(f"Gesamt-Rarity: {sum(rarity_mods)}%")
    print(f"Erwartet: {expected_total}%")
    
    if sum(rarity_mods) == expected_total:
        print("Test erfolgreich!")
    else:
        print("Test fehlgeschlagen!")


if __name__ == "__main__":
    # Führe Test aus wenn direkt ausgeführt
    test_gear_rarity_analyzer()