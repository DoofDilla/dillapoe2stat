"""
Manual Price Manager - Easy tool to add/update manual prices
Run this script to manage manual item prices
"""

from manual_prices import get_manual_price_database


def add_price_interactive():
    """Interactive tool to add a new manual price"""
    db = get_manual_price_database()
    
    print("=== Add Manual Price ===")
    item_name = input("Item name: ").strip()
    if not item_name:
        print("Item name cannot be empty!")
        return
    
    print("\nAvailable currencies:")
    print("1. chaos - Chaos Orb")
    print("2. exalted - Exalted Orb") 
    print("3. orb_of_annulment - Orb of Annulment")
    print("4. divine_orb - Divine Orb")
    print("5. orb_of_fusing - Orb of Fusing")
    
    currency_choice = input("\nSelect currency (1-5 or type custom): ").strip()
    
    currency_map = {
        '1': 'chaos',
        '2': 'exalted',
        '3': 'orb_of_annulment',
        '4': 'divine_orb',
        '5': 'orb_of_fusing'
    }
    
    currency = currency_map.get(currency_choice, currency_choice)
    
    try:
        amount = float(input(f"Amount of {currency}: ").strip())
    except ValueError:
        print("Invalid amount!")
        return
    
    category = input("Category (optional): ").strip() or "Manual"
    description = input("Description (optional): ").strip()
    
    db.add_item_price(item_name, currency, amount, category, description)
    print(f"\n✅ Added: {item_name} = {amount} {currency}")
    
    # Show converted values
    result = db.get_item_price(item_name)
    if result:
        chaos_val, ex_val, cat = result
        print(f"   Converted: {chaos_val:.2f}c | {ex_val:.3f}ex | Category: {cat}")


def list_manual_prices():
    """List all manual prices"""
    db = get_manual_price_database()
    items = db.list_manual_items()
    
    if not items:
        print("No manual prices found.")
        return
    
    print("=== Manual Prices ===")
    for item_name, data in items.items():
        result = db.get_item_price(item_name)
        if result:
            chaos_val, ex_val, category = result
            print(f"{item_name}:")
            print(f"  Original: {data['amount']} {data['currency']}")
            print(f"  Converted: {chaos_val:.2f}c | {ex_val:.3f}ex")
            print(f"  Category: {category}")
            if data.get('description'):
                print(f"  Description: {data['description']}")
            print()


def update_currency_rates():
    """Update currency conversion rates"""
    db = get_manual_price_database()
    
    print("=== Update Currency Rates ===")
    print("Current rates:")
    rates = db.list_currency_rates()
    for currency, data in rates.items():
        print(f"  {currency}: {data['chaos_value']}c | {data['exalted_value']}ex")
    
    print("\nUpdate a rate (or press Enter to skip):")
    currency = input("Currency name: ").strip()
    if not currency:
        return
    
    try:
        chaos_value = float(input(f"Chaos value for {currency}: ").strip())
        exalted_value = float(input(f"Exalted value for {currency}: ").strip())
    except ValueError:
        print("Invalid values!")
        return
    
    description = input("Description (optional): ").strip()
    
    db.update_currency_rate(currency, chaos_value, exalted_value, description)
    print(f"✅ Updated {currency} rates: {chaos_value}c | {exalted_value}ex")


def main():
    """Main menu"""
    while True:
        print("\n=== Manual Price Manager ===")
        print("1. Add new manual price")
        print("2. List all manual prices")
        print("3. Update currency rates")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            add_price_interactive()
        elif choice == '2':
            list_manual_prices()
        elif choice == '3':
            update_currency_rates()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()