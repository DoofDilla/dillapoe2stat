# price_check_poe2.py
from __future__ import annotations
import requests
from functools import lru_cache
from typing import Dict, List, Tuple, Optional

LEAGUE = "Rise of the Abyssal"  # ggf. später "Abyss"
BASE   = "https://poe.ninja/poe2/api/economy/temp/overview"
UA     = "DillaPoE2Stat/0.1 (+you@example.com)"

# -------- utils --------
def _norm(s: str) -> str:
    return (s or "").lower().replace("’", "'").strip()

def _slug(s: str) -> str:
    return _norm(s).replace(" ", "-")

def fmt(x: Optional[float], prec: int = 3) -> str:
    if x is None: return "n/a"
    s = f"{x:.{prec}f}"
    return s.rstrip("0").rstrip(".")

# -------- fetch --------
def _fetch_items(overview_name: str, league: str = LEAGUE):
    r = requests.get(
        BASE,
        params={"leagueName": league, "overviewName": overview_name},
        timeout=15,
        headers={"User-Agent": UA, "Accept":"application/json", "Referer":"https://poe.ninja/"},
    )
    r.raise_for_status()
    return r.json().get("items", [])

@lru_cache(maxsize=32)
def fetch_category_prices(overview_name: str, league: str = LEAGUE) -> Dict[str, float]:
    """
    Liefert Mapping aus Name/ID/Slug -> Chaos-Wert (primaryValue) für eine Kategorie.
    Für 'Currency' wird 'Chaos Orb' als 1.0 ergänzt.
    """
    items = _fetch_items(overview_name, league)
    prices: Dict[str, float] = {}
    if overview_name.lower() == "currency":
        prices[_norm("Chaos Orb")] = 1.0
        prices["chaos"] = 1.0

    for row in items:
        it = row.get("item") or {}
        name = (it.get("name") or "").strip()
        iid  = (it.get("id") or "").strip()
        pv   = row.get("primaryValue")
        if isinstance(pv, (int, float)):
            if name:
                prices[_norm(name)] = float(pv)
                prices[_slug(name)] = float(pv)
            if iid:
                prices[_norm(iid)]  = float(pv)
                prices[_slug(iid)]  = float(pv)
    return prices

@lru_cache(maxsize=1)
def exalted_price(league: str = LEAGUE) -> Optional[float]:
    cur = fetch_category_prices("Currency", league)
    return cur.get(_norm("Exalted Orb")) or cur.get("exalted")

# -------- category guess --------
DEFAULT_PROBE = ["Currency", "omens", "breach-catalysts", "soul-cores", "runes",
                 "Fragments", "essences", "waystones"]

def guess_category_from_item(it: dict) -> Optional[str]:
    """
    Sehr robuste KISS-Heuristik anhand der Item-Felder aus deinem Inventory:
    - Currency: frameType==5 UND (stackSize oder '/currency/' im icon oder ' orb' im Namen)
    - Breach Catalysts: 'Catalyst' im Namen oder '/BreachCatalyst' im icon
    - Runes: 'Rune' im Namen oder '/Runes/' im icon
    - Fragments/Splinters/Shards: Name oder icon-Hinweis
    - Waystones (Maps): 'Waystone' im Namen oder '/EndgameMap' im icon
    - Essences: 'Essence' im Namen oder '/Essence/' im icon
    - Omens: 'Omen' im Namen oder '/Omens/' im icon
    """
    name = _norm(it.get("typeLine") or it.get("baseType") or it.get("name"))
    icon = _norm(it.get("icon") or "")
    frame = it.get("frameType")
    stack = it.get("stackSize")

    txt = name

    if frame == 5 and (stack or "/currency/" in icon or " orb" in txt):
        return "Currency"
    if "catalyst" in txt or "/breachcatalyst" in icon:
        return "breach-catalysts"
    if txt.endswith(" rune") or " rune" in txt or "/runes/" in icon:
        return "runes"
    if "shard" in txt or "splinter" in txt or "/breachstonesplinter" in icon or "/fragments/" in icon:
        return "Fragments"
    if "waystone" in txt or "/endgamemap" in icon:
        return "waystones"
    if "essence" in txt or "/essence/" in icon:
        return "essences"
    if "omen" in txt or "/omens/" in icon:
        return "omens"
    return None

# -------- value lookups --------
def get_value_for_name_and_category(item_name: str, category: str,
                                    league: str = LEAGUE) -> Tuple[Optional[float], Optional[float]]:
    prices = fetch_category_prices(category, league)
    chaos = prices.get(_norm(item_name)) or prices.get(_slug(item_name))
    if chaos is None:
        return None, None
    ex = exalted_price(league)
    return chaos, (chaos / ex) if ex else None

def get_value_for_inventory_item(it: dict, league: str = LEAGUE) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Input: ein RAW-Item aus deinem Inventory.
    Output: (chaos_each, exalted_each, used_category)
    """
    name = it.get("typeLine") or it.get("baseType") or it.get("name")
    if not name:
        return None, None, None
    cat = guess_category_from_item(it)
    tried = set()
    if cat:
        chaos, ex = get_value_for_name_and_category(name, cat, league)
        tried.add(cat)
        if chaos is not None:
            return chaos, ex, cat
    # Fallback: kurze Probe über gängige Kategorien (Requests sind gecacht)
    for c in DEFAULT_PROBE:
        if c in tried: continue
        chaos, ex = get_value_for_name_and_category(name, c, league)
        if chaos is not None:
            return chaos, ex, c
    return None, None, None

def valuate_items_raw(items: List[dict], league: str = LEAGUE):
    """
    Nimmt RAW-Items (z. B. deine 'added'-Liste), ermittelt Chaos/Ex-Pro-Item,
    aggregiert nach Name. Rückgabe:
      - rows: [{name, qty, chaos_each, chaos_total, ex_each, ex_total, category}]
      - totals: (sum_chaos, sum_ex or None)
    """
    from collections import defaultdict

    ex_div = exalted_price(league)
    by_name = defaultdict(lambda: {
        "name": None, "qty": 0, "chaos_each": None, "ex_each": None,
        "chaos_total": 0.0, "ex_total": 0.0, "category": None
    })

    for it in items:
        name = it.get("typeLine") or it.get("baseType") or it.get("name") or "Unknown"
        qty  = int(it.get("stackSize") or 1)
        c_each, e_each, cat = get_value_for_inventory_item(it, league)

        rec = by_name[name]
        rec["name"] = name
        rec["qty"] += qty
        rec["category"] = rec["category"] or cat
        if c_each is not None:
            rec["chaos_each"] = c_each
            rec["chaos_total"] += c_each * qty
        if e_each is not None:
            rec["ex_each"] = e_each
            rec["ex_total"] += e_each * qty

    rows = list(by_name.values())
    sum_c = sum(r["chaos_total"] for r in rows)
    sum_e = (sum(r["ex_total"] for r in rows) if ex_div else None)
    return rows, (sum_c, sum_e)
