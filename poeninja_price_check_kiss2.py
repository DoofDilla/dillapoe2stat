import requests

URL = "https://poe.ninja/poe2/api/economy/temp/overview"
PARAMS = {"leagueName": "Rise of the Abyssal", "overviewName": "Currency"}
UA = "DillaPoE2Stat/0.1 (+you@example.com)"

def fetch_chaos_prices():
    r = requests.get(URL, params=PARAMS, timeout=15,
                     headers={"User-Agent": UA, "Accept":"application/json", "Referer":"https://poe.ninja/"})
    r.raise_for_status()
    items = r.json().get("items", [])
    prices = {"Chaos Orb": 1.0}  # baseline (steht nicht im Feed)

    for row in items:
        it = row.get("item", {}) or {}
        name = (it.get("name") or "").strip()
        pv = row.get("primaryValue")  # => direkt "Value in Chaos" (wie UI)
        if name and isinstance(pv, (int, float)):
            prices[name] = float(pv)
    return prices

if __name__ == "__main__":
    prices = fetch_chaos_prices()
PREC = 3
NAMES = [
    "Divine Orb",
    "Exalted Orb",
    "Orb of Alchemy",
    "Greater Exalted Orb",
    "Perfect Regal Orb",
    "Orb of Annulment",
    "Greater Chaos Orb",
    "Mirror of Kalandra",
]

def fmt(x, prec=PREC):
    s = f"{x:.{prec}f}"
    return s.rstrip("0").rstrip(".")

prices = fetch_chaos_prices()  # dein bestehender Fetch mit primaryValue -> chaos

ex_price = prices.get("Exalted Orb")
if not ex_price:
    print("Exalted-Preis fehlt im Feed – ohne den kann ich nicht in Exalted umrechnen.")
else:
    print("=== Value (Chaos & Exalted) ===")
    for nm in NAMES:
        c = prices.get(nm)
        if c is None:
            print(f"{nm:22s} : n/a")
            continue
        e = c / ex_price
        print(f"{nm:22s} ≈ {fmt(c)} chaos  |  {fmt(e)} ex")

