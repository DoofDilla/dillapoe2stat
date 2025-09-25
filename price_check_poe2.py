# price_check_poe2.py (drop-in replacement)
from __future__ import annotations
import re
import requests
from functools import lru_cache
from typing import Dict, List, Tuple, Optional

LEAGUE = "Rise of the Abyssal"  # ggf. "Abyss"
BASE   = "https://poe.ninja/poe2/api/economy/temp/overview"
UA     = "DillaPoE2Stat/0.1 (+you@example.com)"

# --- Normalizer & Helpers -----------------------------------------------------
_PUNCT_RE = re.compile(r"[^\w\s-]+", re.UNICODE)

def _norm(s: str) -> str:
    return (s or "").lower().replace("’", "'").strip()

def _slug(s: str) -> str:
    return _norm(s).replace(" ", "-")

def _nopunct(s: str) -> str:
    # entfernt alle Satzzeichen (lässt Buchstaben/Ziffern/_/-/Space)
    return _PUNCT_RE.sub("", _norm(s)).replace("  ", " ").strip()

def fmt(x: Optional[float], prec: int = 3) -> str:
    if x is None: return "n/a"
    s = f"{x:.{prec}f}"
    return s.rstrip("0").rstrip(".")

# --- Kategorie-Aliase (wir probieren reihum, bis Items kommen) ---------------
OVERVIEW_ALIASES: Dict[str, List[str]] = {
    "Currency": ["Currency", "currency"],
    "omens": ["Ritual", "Omen", "omen"],
    "catalysts": ["Breach", "BreachCatalyst", "Catalyst", "catalysts"],
    "soul-cores": ["Ultimatium", "SoulCores", "SoulCore"],
    "runes": ["Runes", "Runes", "rune"],
    "abyss": ["Abyss", "Abyss", "abyss"],
    "Fragments": ["Fragments", "fragments", "fragment"],
    "essences": ["Essences", "Essence", "essence"],
    "talismans": ["Talismans", "Talisman", "talismans", "talismans"],
    "expeditions": ["Expedition", "Expedition", "expeditions", "expedition"],
    "waystones": ["waystones", "Waystones", "Waystone", "Maps"],
    "delirium": ["Delirium", "delirium", "delirious"],
}

DEFAULT_PROBE = ["Currency", "Ritual", "catalysts", "ultimatum", "runes",
                 "Fragments", "essences", "waystones", "talismans", "expeditions", "delirium"]

# --- Fetch Layer --------------------------------------------------------------
def _fetch_items_once(overview_name: str, league: str = LEAGUE):
    r = requests.get(
        BASE,
        params={"leagueName": league, "overviewName": overview_name},
        timeout=15,
        headers={"User-Agent": UA, "Accept":"application/json", "Referer":"https://poe.ninja/"},
    )
    r.raise_for_status()
    return r.json().get("items", [])

def _fetch_items_with_aliases(category_key: str, league: str = LEAGUE):
    aliases = OVERVIEW_ALIASES.get(category_key, [category_key])
    for alias in aliases:
        items = _fetch_items_once(alias, league)
        if items:
            return items
    # nichts gefunden -> leere Liste
    return []

@lru_cache(maxsize=64)
def fetch_category_prices(category_key: str, league: str = LEAGUE) -> Dict[str, float]:
    """
    Liefert Mapping aus *mehreren* Keys -> Chaos-Wert (primaryValue).
    Keys pro Item: norm(name), slug(name), nopunct(name), norm(id), slug(id), nopunct(id)
    Für Currency ergänzen wir 'Chaos Orb' = 1.0.
    """
    items = _fetch_items_with_aliases(category_key, league)
    prices: Dict[str, float] = {}
    if category_key.lower() == "currency":
        prices[_norm("Chaos Orb")] = 1.0
        prices["chaos"] = 1.0
        prices[_nopunct("Chaos Orb")] = 1.0

    for row in items:
        it = row.get("item") or {}
        name = (it.get("name") or "").strip()
        iid  = (it.get("id") or "").strip()
        pv   = row.get("primaryValue")
        if not isinstance(pv, (int, float)):
            continue
        if name:
            prices[_norm(name)]    = float(pv)
            prices[_slug(name)]    = float(pv)
            prices[_nopunct(name)] = float(pv)
        if iid:
            prices[_norm(iid)]     = float(pv)
            prices[_slug(iid)]     = float(pv)
            prices[_nopunct(iid)]  = float(pv)
    return prices

@lru_cache(maxsize=1)
def exalted_price(league: str = LEAGUE) -> Optional[float]:
    cur = fetch_category_prices("Currency", league)
    return cur.get(_norm("Exalted Orb")) or cur.get("exalted") or cur.get(_nopunct("Exalted Orb"))

def _lookup_name(it: dict) -> str:
    tl = it.get("typeLine") or ""
    bt = it.get("baseType") or ""
    name = tl or bt or it.get("name") or ""
    nlow = _norm(name)
    # Für Waystones lieber baseType (stabil), weil typeLine Magic/Rare-Titel hat
    if "waystone" in nlow and bt:
        return bt
    return name

# --- Category Guess (aus Inventory-Item) -------------------------------------
def guess_category_from_item(it: dict) -> Optional[str]:
    name = name = _lookup_name(it)
    icon = _norm(it.get("icon") or "")
    frame = it.get("frameType")
    stack = it.get("stackSize")

    txt = name

    if frame == 5 and (stack or "/currency/" in icon or " orb" in txt):
        return "Currency"
    if "catalyst" in txt or "breach splinter" in txt or "/breachcatalyst" in icon:
        return "catalysts"
    if txt.endswith(" rune") or " rune" in txt or "/runes/" in icon:
        return "runes"
    if "key" in txt or "fragment" in txt or "runic splinter" in txt or "/fragments/" in icon:
        return "fragments"
    if "waystone" in txt or "/endgamemap" in icon:
        return "waystones"
    if "essence" in txt or "/essence/" in icon:
        return "essences"
    if "soul core" in txt or "/ultimatium" in icon:
        return "soul-cores"
    if "talisman" in txt or "/talismans/" in icon:
        return "talismans"
    if "expedition" in txt or "artifact" in txt or "/expeditions/" in icon:
        return "expeditions"
    if "delirium" in txt or "diluted" in txt or "liquid" in txt or "simulacrum" in txt or "/delirium/" in icon:
        return "delirium"
    if "preserved" in txt or "ancient" in txt or "gnawed" in txt or "/abyss/" in icon:
        return "abyss"
    if "omen" in txt or "/ritual/" in icon:
        return "omens"
    
    return None

# --- Lookups ------------------------------------------------------------------
def _lookup(prices: Dict[str, float], name: str) -> Optional[float]:
    return (prices.get(_norm(name))
            or prices.get(_slug(name))
            or prices.get(_nopunct(name)))

def get_value_for_name_and_category(item_name: str, category: str,
                                    league: str = LEAGUE) -> Tuple[Optional[float], Optional[float]]:
    prices = fetch_category_prices(category, league)
    chaos = _lookup(prices, item_name)

    # kleine Spezialregel: „… Splinter“ → fallback auf „Breach Splinter“, falls direct miss
    if chaos is None and "splinter" in _norm(item_name):
        chaos = _lookup(prices, "Breach Splinter")

    if chaos is None:
        return None, None
    ex = exalted_price(league)
    return chaos, (chaos / ex) if ex else None

def get_value_for_inventory_item(it: dict, league: str = LEAGUE) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    name = it.get("typeLine") or it.get("baseType") or it.get("name")
    if not name:
        return None, None, None

    # 0) Check manual prices first (highest priority)
    try:
        from manual_prices import get_manual_item_price
        
        # Try multiple name fields for manual lookup
        potential_names = [
            it.get("name"),          # For uniques like "The Grand Project"
            it.get("typeLine"),      # For normal items
            it.get("baseType"),      # Fallback
        ]
        
        for potential_name in potential_names:
            if potential_name:
                manual_result = get_manual_item_price(potential_name)
                if manual_result:
                    chaos, ex, category = manual_result
                    return chaos, ex, f"Manual-{category}"
                    
    except ImportError:
        pass  # Manual prices module not available
    except Exception as e:
        print(f"Warning: Manual price lookup failed for '{name}': {e}")

    # 1) Heuristik
    cat = guess_category_from_item(it)
    tried = set()
    if cat:
        chaos, ex = get_value_for_name_and_category(name, cat, league)
        tried.add(cat)
        if chaos is not None:
            return chaos, ex, cat

    # 2) Fallback: probeweise über Standard-Kategorien
    for c in DEFAULT_PROBE:
        if c in tried: 
            continue
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
