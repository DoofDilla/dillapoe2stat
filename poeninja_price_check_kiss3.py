# poe2_price_lookup.py
import requests
from typing import Optional, Tuple

BASE = "https://poe.ninja/poe2/api/economy/temp/overview"
UA   = "DillaPoE2Stat/0.1 (+you@example.com)"
LEAGUE = "Rise of the Abyssal"  # ggf. "Abyss"

def _fetch_items(overview_name: str, league: str = LEAGUE):
    """Holt die Rohdaten für eine PoE2-Kategorie (temp endpoint)."""
    r = requests.get(
        BASE,
        params={"leagueName": league, "overviewName": overview_name},
        timeout=15,
        headers={"User-Agent": UA, "Accept": "application/json", "Referer": "https://poe.ninja/"},
    )
    r.raise_for_status()
    return r.json().get("items", [])

def _normalize_key(s: str) -> str:
    return s.strip().lower().replace("’", "'")

def _slugify(s: str) -> str:
    # sehr leichtes slugging: spaces -> '-', entfernt Doppelleerzeichen
    return _normalize_key(s).replace(" ", "-")

def fetch_category_prices(overview_name: str, league: str = LEAGUE) -> dict:
    """
    Baut ein Mapping -> Chaos-Preis (primaryValue).
    Keys enthalten sowohl den **Name** als auch die **ID** (beide normalisiert).
    """
    items = _fetch_items(overview_name, league)
    prices = {}

    # Chaos selbst kommt in Currency nicht vor → setze baseline
    if overview_name.lower() == "currency":
        prices[_normalize_key("Chaos Orb")] = 1.0
        prices["chaos"] = 1.0

    for row in items:
        it  = row.get("item", {}) or {}
        name = it.get("name") or ""
        iid  = it.get("id") or ""   # z. B. "divine", "exalted", …
        pv   = row.get("primaryValue")
        if isinstance(pv, (int, float)):
            if name:
                prices[_normalize_key(name)] = float(pv)
                prices[_slugify(name)]       = float(pv)  # zusätzlicher Key
            if iid:
                prices[_normalize_key(iid)]  = float(pv)
                prices[_slugify(iid)]        = float(pv)
    return prices

def get_item_value(category: str, name: str, league: str = LEAGUE) -> Tuple[Optional[float], Optional[float]]:
    """
    Liefert (chaos_value, exalted_value) für ein Item in einer Kategorie.
    chaos_value: float oder None
    exalted_value: float oder None (None, wenn Exalted-Preis fehlt)
    """
    # 1) Currency laden, um Exalted-Preis zu bekommen
    cur = fetch_category_prices("Currency", league)
    ex_price = cur.get(_normalize_key("Exalted Orb")) or cur.get("exalted")
    # 2) Kategoriepreise holen
    prices = fetch_category_prices(category, league)

    key = _normalize_key(name)
    chaos_value = prices.get(key) or prices.get(_slugify(name))
    if chaos_value is None:
        return None, None

    exalted_value = (chaos_value / ex_price) if ex_price else None
    return chaos_value, exalted_value

def fmt(x: Optional[float], prec: int = 3) -> str:
    if x is None: return "n/a"
    s = f"{x:.{prec}f}"
    return s.rstrip("0").rstrip(".")

if __name__ == "__main__":
    # Beispiele: zwei Soul Cores
    tests = [
        ("Ultimatum", "Soul Core of Quipolatl"),
        ("Ultimatum", "Soul Core of Tzamoto"),
        ("Abyss", "Ancient Rib"),
        ("Essences", "Perfect Essence of Battle"),
        # weitere Beispiele:
        ("Currency", "Divine Orb"),
        ("Currency", "Greater Exalted Orb"),
    ]
    for cat, name in tests:
        c, e = get_item_value(cat, name)
        print(f"{name:28s} [{cat}]  ->  {fmt(c)} chaos  |  {fmt(e)} ex")
