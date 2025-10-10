# price_check_poe2.py (drop-in replacement)
from __future__ import annotations
import re
import requests
from functools import lru_cache
from typing import Dict, List, Tuple, Optional

LEAGUE = "Rise of the Abyssal"  # ggf. "Abyss"
BASE   = "https://poe.ninja/poe2/api/economy/temp/overview"
UA     = "DillaPoE2Stat/0.1 (+you@example.com)"

# Global currency cache for better performance
class CurrencyCache:
    def __init__(self):
        self.chaos_value = 1.0  # Basis
        self.exalted_value = None  # Chaos per Exalted
        self.divine_value = None   # Chaos per Divine
        self.is_loaded = False
        
    def load_currency_rates(self, league: str = LEAGUE):
        """Load basic currency rates once at startup"""
        try:
            print("Loading currency exchange rates...")
            items = _fetch_items_with_aliases("Currency", league)
            
            for row in items:
                it = row.get("item") or {}
                name = (it.get("name") or "").strip().lower()
                rate = row.get("rate") or {}
                
                if name == "exalted orb" and "chaos" in rate:
                    # rate["chaos"] = X bedeutet "X Exalted = 1 Chaos"
                    # Also: 1 Exalted = 1/X Chaos
                    exalted_per_chaos = float(rate["chaos"])
                    self.exalted_value = 1.0 / exalted_per_chaos if exalted_per_chaos > 0 else 0.0675
                    
                elif name == "chaos orb" and "divine" in rate:
                    # rate["divine"] = X bedeutet "X Chaos = 1 Divine"
                    # Also: 1 Divine = X Chaos
                    self.divine_value = float(rate["divine"]) if rate["divine"] > 0 else 23.0
                    
            # Fallback values if not found
            if self.exalted_value is None:
                self.exalted_value = 0.0675  # Fallback
            if self.divine_value is None:
                self.divine_value = 23.0  # Fallback
                
            self.is_loaded = True
            print(f"Currency rates loaded: 1ex = {self.exalted_value:.4f}c, 1div = {self.divine_value:.2f}c")
            
        except Exception as e:
            print(f"Failed to load currency rates: {e}")
            # Use fallback values
            self.exalted_value = 0.0675
            self.divine_value = 23.0
            self.is_loaded = True
            
    def get_exalted_rate(self) -> float:
        if not self.is_loaded:
            self.load_currency_rates()
        return self.exalted_value
        
    def get_divine_rate(self) -> float:
        if not self.is_loaded:
            self.load_currency_rates()
        return self.divine_value

# Global instance
_currency_cache = CurrencyCache()

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
    "uncutgems": ["UncutGems", "UncutGem", "uncutgems"],
}

DEFAULT_PROBE = ["Currency", "Ritual", "delirium", "catalysts", "ultimatum", "runes",
                 "Fragments", "essences", "waystones", "talismans", "expeditions", "abyss", "uncutgems"]

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
    Für Currency: Chaos Orb = 1.0 (Basis), andere Items umgerechnet in Chaos-Werte.
    """
    items = _fetch_items_with_aliases(category_key, league)
    prices: Dict[str, float] = {}
    
    # Zuerst alle Items aus API verarbeiten
    for row in items:
        it = row.get("item") or {}
        name = (it.get("name") or "").strip()
        iid  = (it.get("id") or "").strip()
        pv   = row.get("primaryValue")
        if not isinstance(pv, (int, float)):
            continue
            
        rate = row.get("rate") or {}
        chaos_value = None
        
        # Für ALLE Items: primaryValue ist in Divine, muss in Chaos umgerechnet werden
        if name.lower() == "chaos orb":
            chaos_value = 1.0  # Chaos ist immer 1.0 Chaos
        elif name.lower() == "exalted orb" and "chaos" in rate:
            # KORREKTUR: rate["chaos"] bedeutet "wieviele Exalted für 1 Chaos"
            # Also: 1 Exalted = (1 / rate["chaos"]) Chaos
            exalted_per_chaos = float(rate["chaos"])
            chaos_value = 1.0 / exalted_per_chaos if exalted_per_chaos > 0 else 0.0675
        else:
            # NEUE LOGIK: Verwende rate.chaos wenn verfügbar (besser als primaryValue)
            if "chaos" in rate and float(rate["chaos"]) > 0:
                # rate["chaos"] = X bedeutet "X Items = 1 Chaos"
                # Also: 1 Item = 1/X Chaos
                items_per_chaos = float(rate["chaos"])
                chaos_value = 1.0 / items_per_chaos
            else:
                # Fallback: FÜR ALLE ANDEREN ITEMS: primaryValue ist in Divine, rechne in Chaos um
                divine_chaos_rate = divine_to_chaos_rate(league)
                
                if divine_chaos_rate and float(pv) > 0:
                    # primaryValue ist in Divine, multipliziere mit echter API Divine-Rate
                    chaos_value = float(pv) * divine_chaos_rate
                else:
                    # Fallback: verwende primaryValue direkt
                    chaos_value = float(pv)
        
        # Fallback: use primaryValue direkt
        if chaos_value is None:
            chaos_value = float(pv)
        
        # Speichere unter verschiedenen Keys
        if name:
            prices[_norm(name)]    = chaos_value
            prices[_slug(name)]    = chaos_value
            prices[_nopunct(name)] = chaos_value
        if iid:
            prices[_norm(iid)]     = chaos_value
            prices[_slug(iid)]     = chaos_value
            prices[_nopunct(iid)]  = chaos_value
    
    # Stelle sicher dass Chaos Orb korrekt ist (falls nicht in API)
    if category_key.lower() == "currency":
        prices[_norm("Chaos Orb")] = 1.0
        prices["chaos"] = 1.0
        prices[_nopunct("Chaos Orb")] = 1.0
    
    return prices

@lru_cache(maxsize=1)
def exalted_price(league: str = LEAGUE) -> Optional[float]:
    """Get Exalted price in Chaos (cached at startup)"""
    return _currency_cache.get_exalted_rate()

def divine_price(league: str = LEAGUE) -> Optional[float]:
    """Get Divine price in Chaos (cached at startup)"""
    return _currency_cache.get_divine_rate()

def divine_to_chaos_rate(league: str = LEAGUE) -> Optional[float]:
    """Get the Divine to Chaos conversion rate (cached at startup)"""
    return _currency_cache.get_divine_rate()

def initialize_currency_cache(league: str = LEAGUE):
    """Initialize currency cache at startup - call this once!"""
    _currency_cache.load_currency_rates(league)

def _lookup_name(it: dict) -> str:
    # Try different name sources (API structure changed)
    tl = it.get("typeLine") or ""
    bt = it.get("baseType") or ""
    direct_name = it.get("name") or ""
    item_name = it.get("item", {}).get("name") or ""  # New API structure
    
    # Prefer item.name (new API), then fallback to old structure
    name = item_name or tl or bt or direct_name or ""
    nlow = _norm(name)
    
    # Für Waystones lieber baseType (stabil), weil typeLine Magic/Rare-Titel hat
    if "waystone" in nlow and bt:
        return bt
    return name

# --- Category Guess (aus Inventory-Item) -------------------------------------
def guess_category_from_item(it: dict) -> Optional[str]:
    name = _lookup_name(it)
    icon = _norm(it.get("icon") or "")
    frame = it.get("frameType")
    stack = it.get("stackSize")

    txt = _norm(name) if name else ""

    if frame == 5 and (stack or "/currency/" in icon or " orb" in txt):
        return "Currency"
    # Uncut Gems zuerst prüfen (vor anderen gem checks)
    if "uncut" in txt and "gem" in txt:
        return "uncutgems"
    # Delirium items zuerst prüfen (vor catalyst/breach splinter check!)
    if "delirium" in txt or "diluted" in txt or "liquid" in txt or "simulacrum" in txt or "/delirium/" in icon:
        return "delirium"
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
                                    league: str = LEAGUE) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    prices = fetch_category_prices(category, league)
    
    # Spezialbehandlung für Divine Orb - es ist die Referenzwährung
    if _norm(item_name) == _norm("Divine Orb") or _norm(item_name) == "divine":
        # Hole Divine-zu-Exalted rate direkt aus API
        items = _fetch_items_with_aliases("Currency", league)
        divine_in_ex = None
        divine_in_chaos = None
        
        for row in items:
            it = row.get("item") or {}
            name = (it.get("name") or "").strip()
            iid = (it.get("id") or "").strip()
            rate = row.get("rate") or {}
            
            # Finde Exalted Orb rate um Divine-zu-Exalted zu berechnen
            if (name.lower() == "exalted orb" or iid == "exalted") and "divine" in rate:
                # rate["divine"] = wieviele Exalted für 1 Divine
                divine_in_ex = rate["divine"]
                break
                
        # Hole auch Chaos rate
        divine_in_chaos = divine_price(league)
        
        if divine_in_ex and divine_in_chaos:
            return divine_in_chaos, divine_in_ex, 1.0
        return None, None, None
    
    chaos = _lookup(prices, item_name)

    # kleine Spezialregel: „… Splinter" → fallback auf „Breach Splinter", falls direct miss
    if chaos is None and "splinter" in _norm(item_name):
        chaos = _lookup(prices, "Breach Splinter")

    if chaos is None:
        return None, None, None
    
    # Berechne Exalted und Divine Werte mit gecachten Raten
    ex_chaos = _currency_cache.get_exalted_rate()  # Chaos pro Exalted
    div_chaos = _currency_cache.get_divine_rate()  # Chaos pro Divine
    
    ex_value = (chaos / ex_chaos) if ex_chaos else None    # Exalted-Wert des Items
    div_value = (chaos / div_chaos) if div_chaos else None # Divine-Wert des Items
    
    return chaos, ex_value, div_value

def get_value_for_inventory_item(it: dict, league: str = LEAGUE) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    name = it.get("typeLine") or it.get("baseType") or it.get("name")
    if not name:
        return None, None, None

    # 1) Heuristik
    cat = guess_category_from_item(it)
    tried = set()
    if cat:
        chaos, ex, div = get_value_for_name_and_category(name, cat, league)
        tried.add(cat)
        if chaos is not None:
            return chaos, ex, cat

    # 2) Fallback: probeweise über Standard-Kategorien
    for c in DEFAULT_PROBE:
        if c in tried: 
            continue
        chaos, ex, div = get_value_for_name_and_category(name, c, league)
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

    ex_div = _currency_cache.get_exalted_rate()
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
