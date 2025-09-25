"""
Manual Price Manager - Easy tool to add/update manual prices
Run this script to manage manual item prices
"""

from manual_prices import get_manual_price_database


def add_price_interactive():
    """Interactive tool to add a new manual item mapping"""
    db = get_manual_price_database()
    
    print("=== Add Manual Item Mapping ===")
    item_name = input("Item name: ").strip()
    if not item_name:
        print("Item name cannot be empty!")
        return
    
    print("\nCommon currencies to map to:")
    print("1. Orb of Annulment")
    print("2. Divine Orb")
    print("3. Orb of Fusing")
    print("4. Chaos Orb")
    print("5. Exalted Orb")
    print("6. Vaal Orb")
    print("Or type any other item/currency name")
    
    currency_choice = input("\nSelect target item (1-6 or type custom): ").strip()
    
    currency_map = {
        '1': 'Orb of Annulment',
        '2': 'Divine Orb',
        '3': 'Orb of Fusing',
        '4': 'Chaos Orb',
        '5': 'Exalted Orb',
        '6': 'Vaal Orb'
    }
    
    maps_to = currency_map.get(currency_choice, currency_choice)
    
    try:
        amount = float(input(f"Amount of '{maps_to}': ").strip())
    except ValueError:
        print("Invalid amount!")
        return
    
    category = input("Category (optional): ").strip() or "Manual"
    description = input("Description (optional): ").strip()
    
    db.add_item_mapping(item_name, maps_to, amount, category, description)
    print(f"\n✅ Added mapping: {item_name} → {amount} {maps_to}")
    
    # Show converted values using real market prices
    result = db.get_item_price(item_name)
    if result:
        chaos_val, ex_val, cat = result
        print(f"   Current market value: {chaos_val:.2f}c | {ex_val:.3f}ex | Category: {cat}")


def list_manual_prices():
    """List all manual item mappings"""
    db = get_manual_price_database()
    items = db.list_manual_items()
    
    if not items:
        print("No manual item mappings found.")
        return
    
    print("=== Manual Item Mappings ===")
    for item_name, data in items.items():
        result = db.get_item_price(item_name)
        if result:
            chaos_val, ex_val, category = result
            print(f"{item_name}:")
            print(f"  Maps to: {data['amount']} × {data['maps_to']}")
            print(f"  Current value: {chaos_val:.2f}c | {ex_val:.3f}ex")
            print(f"  Category: {category}")
            if data.get('description'):
                print(f"  Description: {data['description']}")
            print()


def test_item_lookup():
    """Test looking up an existing item mapping"""
    db = get_manual_price_database()
    
    print("=== Test Item Lookup ===")
    item_name = input("Enter item name to test: ").strip()
    if not item_name:
        print("Item name cannot be empty!")
        return
    
    result = db.get_item_price(item_name)
    if result:
        chaos_val, ex_val, category = result
        print(f"\n✅ Found: {item_name}")
        print(f"   Current market value: {chaos_val:.2f}c | {ex_val:.3f}ex")
        print(f"   Category: {category}")
        
        # Show mapping details
        mappings = db.list_manual_items()
        if item_name in mappings:
            data = mappings[item_name]
            print(f"   Maps to: {data['amount']} × {data['maps_to']}")
    else:
        print(f"\n❌ No mapping found for: {item_name}")
        print("Use option 1 to add a new mapping.")


def main():
    """Main menu"""
    while True:
        print("\n=== Manual Price Manager ===")
        print("1. Add new item mapping")
        print("2. List all item mappings")
        print("3. Test item lookup")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            add_price_interactive()
        elif choice == '2':
            list_manual_prices()
        elif choice == '3':
            test_item_lookup()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()