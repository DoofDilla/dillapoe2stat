import requests, time

LEAGUE = "Abyss"  # ggf. "HC Rise of the Abyssal"
UA = "DillaPoE2Stat/0.1 (+you@example.com)"

def get_json(url, params):
    r = requests.get(url, params=params, timeout=15, headers={"User-Agent": UA})
    r.raise_for_status()
    return r.json()

def price_map_currency(league=LEAGUE):
    data = get_json("https://poe.ninja/api/data/currencyoverview",
                    {"league": league, "type": "Currency"})
    m = {}
    for row in data.get("lines", []):
        name = (row.get("currencyTypeName") or "").strip()
        chaos = row.get("chaosEquivalent")
        if name and chaos:
            m[name] = float(chaos)
    return m

def price_map_items(item_type, league=LEAGUE):
    data = get_json("https://poe.ninja/api/data/itemoverview",
                    {"league": league, "type": item_type})
    m = {}
    for row in data.get("lines", []):
        name = (row.get("name") or "").strip()
        chaos = row.get("chaosValue") or row.get("chaosEquivalent")
        if name and chaos:
            m[name] = float(chaos)
    return m

def build_union_price_map():
    prices = {}
    # Currency
    prices.update(price_map_currency())
    # Omens
    try:
        prices.update(price_map_items("Omen"))
    except Exception:
        pass
    # Breach Catalysts (Fallback: Catalyst)
    try:
        prices.update(price_map_items("BreachCatalyst"))
    except Exception:
        try:
            prices.update(price_map_items("Catalyst"))
        except Exception:
            pass
    return prices

def valuate(items, prices):
    """items: list of (name, stack)"""
    chaos_per_ex = prices.get("Exalted Orb") or prices.get("Exalted Orb (POE2)")  # name variiert selten
    total_chaos = 0.0
    rows = []
    for name, stack in items:
        each = prices.get(name)
        value = (each or 0.0) * stack
        total_chaos += value
        rows.append({
            "name": name, "stack": stack,
            "chaos_each": each, "chaos_total": value
        })
    ex_total = (total_chaos / chaos_per_ex) if chaos_per_ex else None
    return rows, total_chaos, ex_total, chaos_per_ex

if __name__ == "__main__":
    # Proof of concept: Test-Items (so wie sie aus deiner Aggregation kommen würden)
    test_items = [
        ("Chaos Orb", 120),
        ("Exalted Orb", 2),
        ("Tul's Catalyst", 3),
        ("Omen of Refreshing", 1),  # Beispiel-Name; ersetz mit realem Omen
    ]

    prices = build_union_price_map()
    rows, tot_c, tot_ex, ex_price = valuate(test_items, prices)

    print("=== Price Check (poe.ninja) ===")
    print(f"League: {LEAGUE}")
    print(f"Exalted Orb ≈ {ex_price:.1f}c" if ex_price else "Exalted Orb price not found")
    for r in rows:
        ce = f"{r['chaos_each']:.1f}c" if r["chaos_each"] is not None else "n/a"
        print(f" - {r['name']} x{r['stack']} @ {ce}  => {r['chaos_total']:.1f}c")
    print(f"\nSum ≈ {tot_c:.1f} chaos")
    if tot_ex is not None:
        print(f"≈ {tot_ex:.2f} Exalted Orb")
