import requests
import time
from urllib.parse import quote

CLIENT_ID = "dillapoe2stat"        # deine Client Id
CLIENT_SECRET = "UgraAmlUXdP1"  # hier dein Secret eintragen

CHAR_TO_CHECK = "Mettmanwalking"

AUTH_URL = "https://www.pathofexile.com/oauth/token"
API_URL = "https://api.pathofexile.com"

USER_AGENT = "DillaPoE2Stat/0.1 (+you@example.com)"

def get_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "account:characters account:profile",
    }
    r = requests.post(AUTH_URL, data=data, headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    tok = r.json()
    print("Got token, expires in", tok.get("expires_in"), "seconds")
    return tok["access_token"]

def get_characters(access_token):
    headers = {"Authorization": f"Bearer {access_token}",
               "User-Agent": USER_AGENT}
    r = requests.get(f"{API_URL}/character/poe2", headers=headers)
    r.raise_for_status()
    return r.json()

def get_character_details(access_token, name):
    headers = {"Authorization": f"Bearer {access_token}",
               "User-Agent": USER_AGENT}
    r = requests.get(f"{API_URL}/character/poe2/{quote(name)}", headers=headers)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    token = get_token()
    chars = get_characters(token)
    print("Characters:")
    for c in chars.get("characters", []):
        print("-", c.get("name"), f"(lvl {c.get('level')}, class {c.get('class')})")

    if chars.get("characters"):
        # name = chars["characters"][0]["name"]
        name = CHAR_TO_CHECK

        print(f"\nFetching details for: {name}")
        details = get_character_details(token, name)
        char = details.get("character", {})
        inv = char.get("inventory", [])
        print(f"{name} inventory items: {len(inv)}")
        for it in inv:  # no [:10]
            base = it.get("baseType") or ""
            tl   = it.get("typeLine") or ""
            pos  = (it.get("x"), it.get("y"))
            stack = f" x{it['stackSize']}" if it.get("stackSize") else ""
            print(f"• {base} — {tl}{stack} @ {pos}")