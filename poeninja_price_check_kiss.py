import requests

LEAGUE = "Abyss"  # oder "HC Abyss"
UA = "DillaPoE2Stat/0.1 (+you@example.com)"

def get_json(url, params):
    r = requests.get(url, params=params, timeout=15, headers={"User-Agent": UA})
    r.raise_for_status()
    return r.json()

def price_map_currency(league=LEAGUE):
    data = get_json("https://poe.ninja/api/data/currencyoverview",
                    {"league": league, "type": "Currency"})
    m = {}
    # lines: enthält Preise; currencyDetails: Metadaten
    for row in data.get("lines", []):
        chaos = row.get("chaosEquivalent")
        name  = (row.get("currencyTypeName") or "").strip()     # z.B. "Exalted Orb"
        slug  = (row.get("detailsId") or "").strip()            # z.B. "exalted-orb"
        if chaos:
            if name: m[name] = float(chaos)
            if slug: m[slug] = float(chaos)  # optionaler zweiter Key für tolerantem Lookup
    return m

def find(prices, *names):
    """toleranter Lookup: Name oder slug, Apostroph-Varianten etc."""
    norm = lambda s: s.lower().replace("’","'").strip()
    norm_map = {norm(k): v for k,v in prices.items()}
    for n in names:
        v = norm_map.get(norm(n))
        if v is not None:
            return v
    # very light fuzzy fallback
    for k,v in norm_map.items():
        if all(w in k for w in norm("exalted orb").split()):
            if any("exalt" in k or "exalted" in k for _ in [0]): return v
    return None

if __name__ == "__main__":
    prices = price_map_currency()
    # Quick sanity: zeig ein paar Keys
    sample = [k for k in prices.keys() if "orb" in k.lower()][:8]
    print("Sample currency keys:", sample[:8])

    chaos = find(prices, "Chaos Orb", "chaos-orb")
    exalt = find(prices, "Exalted Orb", "exalted-orb")
    divine = find(prices, "Divine Orb", "divine-orb")

    print(f"Chaos Orb ≈ {chaos}c")
    print(f"Exalted Orb ≈ {exalt}c")
    print(f"Divine Orb ≈ {divine}c")

    if exalt and divine:
        print(f"\n1 Divine ≈ {divine/exalt:.2f} Exalted")
        print(f"1 Exalted ≈ {exalt/divine:.2f} Divine")
    else:
        print("\nExalted/Divine nicht gefunden – check League oder Keys.")
