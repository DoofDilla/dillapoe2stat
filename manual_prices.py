"""
Manual Price Database for PoE Stats Tracker
Handles custom item prices for items not covered by poe.ninja API
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple


class ManualPriceDatabase:
    """Manages manual prices for special items"""
    
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent
        self.prices_file = self.config_dir / "manual_prices.json"
        self.prices = {}
        self.currency_rates = {}
        self.load_prices()
    
    def load_prices(self):
        """Load manual price mappings from JSON file"""
        try:
            if self.prices_file.exists():
                with open(self.prices_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.mappings = data.get('item_mappings', {})
            else:
                # Create default prices file
                self.create_default_prices()
        except Exception as e:
            print(f"Error loading manual prices: {e}")
            self.create_default_prices()
    
    def create_default_prices(self):
        """Create default manual prices file"""
        default_data = {
            "item_mappings": {
                "Idol of Estazunti": {
                    "maps_to": "Orb of Annulment",
                    "amount": 1,
                    "description": "Unique idol worth 1 Orb of Annulment",
                    "category": "Unique Idol"
                }
            },
            "description": "Manual item mappings - maps special items to existing currency/items with known market prices",
            "last_updated": "2025-09-25"
        }
        
        try:
            with open(self.prices_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2, ensure_ascii=False)
            self.mappings = default_data['item_mappings']
            print(f"Created default manual prices file: {self.prices_file}")
        except Exception as e:
            print(f"Error creating default prices file: {e}")
    
    def get_item_price(self, item_name: str, league: str = "Rise of the Abyssal") -> Optional[Tuple[float, float, str]]:
        """
        Get price for an item from manual database using existing price lookup methods
        
        Args:
            item_name: Name of the item to look up
            league: League name for price lookup
        
        Returns:
            Tuple of (chaos_value, exalted_value, category) or None if not found
        """
        # Load mappings if not already loaded
        if not hasattr(self, 'mappings'):
            self.load_prices()
        
        mappings = getattr(self, 'mappings', {})
        if item_name not in mappings:
            return None
        
        item_data = mappings[item_name]
        target_item = item_data['maps_to']
        amount = item_data['amount']
        display_name = item_data.get('description', item_data.get('category', 'Manual'))
        
        # Use existing price lookup methods
        try:
            from price_check_poe2 import get_value_for_name_and_category, DEFAULT_PROBE
            
            # Try to find the target item price using existing methods
            chaos_per_unit = None
            ex_per_unit = None
            
            # Try different categories to find the target item
            for cat in DEFAULT_PROBE:
                chaos_per_unit, ex_per_unit = get_value_for_name_and_category(target_item, cat, league)
                if chaos_per_unit is not None:
                    break
            
            if chaos_per_unit is None:
                print(f"Warning: Could not find market price for '{target_item}' (mapped from '{item_name}')")
                return None
            
            # Calculate final price
            total_chaos = chaos_per_unit * amount
            total_ex = ex_per_unit * amount if ex_per_unit else None
            
            return total_chaos, total_ex, display_name
            
        except ImportError as e:
            print(f"Error importing price lookup functions: {e}")
            return None
    
    def add_item_mapping(self, item_name: str, maps_to: str, amount: float = 1.0, 
                        category: str = "Manual", description: str = ""):
        """
        Add a new manual item mapping
        
        Args:
            item_name: Name of the item to map
            maps_to: Name of the currency/item it maps to (must exist in poe.ninja)
            amount: Amount of the target item
            category: Item category
            description: Optional description
        """
        if not hasattr(self, 'mappings'):
            self.mappings = {}
        
        self.mappings[item_name] = {
            'maps_to': maps_to,
            'amount': amount,
            'category': category,
            'description': description or f"{item_name} maps to {amount} {maps_to}"
        }
        self.save_prices()
    
    def save_prices(self):
        """Save current mappings to JSON file"""
        try:
            data = {
                'item_mappings': getattr(self, 'mappings', {}),
                'description': "Manual item mappings - maps special items to existing currency/items with known market prices",
                'last_updated': "2025-09-25"
            }
            
            with open(self.prices_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving manual prices: {e}")
    
    def list_manual_items(self) -> Dict:
        """Get all manual item mappings for display"""
        return getattr(self, 'mappings', {}).copy()
    
    def has_manual_price(self, item_name: str) -> bool:
        """Check if item has a manual mapping"""
        mappings = getattr(self, 'mappings', {})
        return item_name in mappings
    
    def remove_item_price(self, item_name: str) -> bool:
        """Remove a manual mapping entry"""
        mappings = getattr(self, 'mappings', {})
        if item_name in mappings:
            del mappings[item_name]
            self.save_prices()
            return True
        return False


# Global instance for easy access
_manual_price_db = None

def get_manual_price_database():
    """Get the global manual price database instance"""
    global _manual_price_db
    if _manual_price_db is None:
        _manual_price_db = ManualPriceDatabase()
    return _manual_price_db


def get_manual_item_price(item_name: str) -> Optional[Tuple[float, float, str]]:
    """
    Quick function to get manual price for an item
    
    Args:
        item_name: Name of the item
    
    Returns:
        Tuple of (chaos_value, exalted_value, category) or None
    """
    db = get_manual_price_database()
    return db.get_item_price(item_name)