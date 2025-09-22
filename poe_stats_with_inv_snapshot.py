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

def snapshot_inventory(access_token, name):
    details = get_character_details(access_token, name)
    char = details.get("character", {})
    inv = char.get("inventory", [])
    return inv

def inv_key(item):
    # eindeutiger Key pro Item (Fallback: typeline+pos)
    return (
        item.get("id")
        or f"{item.get('typeLine')}|{item.get('x')},{item.get('y')}|{item.get('baseType')}"
    )

def diff_inventories(before, after):
    before_keys = {inv_key(i): i for i in before}
    after_keys  = {inv_key(i): i for i in after}

    added = [after_keys[k] for k in after_keys if k not in before_keys]
    removed = [before_keys[k] for k in before_keys if k not in after_keys]
    return added, removed

if __name__ == "__main__":
    token = get_token()
    chars = get_characters(token)
    if not chars.get("characters"):
        print("No characters found")
        exit(0)

    name = CHAR_TO_CHECK
    print(f"Using character: {name}")

    input("\nPress ENTER before starting map (snapshot pre-map)...")
    inv_before = snapshot_inventory(token, name)
    print(f"Pre-map snapshot: {len(inv_before)} items")

    input("Run your map, then press ENTER after finishing (snapshot post-map)...")
    inv_after = snapshot_inventory(token, name)
    print(f"Post-map snapshot: {len(inv_after)} items")

    added, removed = diff_inventories(inv_before, inv_after)

    print(f"\nAdded items ({len(added)}):")
    for it in added:
        stack = f" x{it['stackSize']}" if it.get("stackSize") else ""
        print(" +", it.get("typeLine"), stack, "@", (it.get("x"), it.get("y")))

    print(f"\nRemoved items ({len(removed)}):")
    for it in removed:
        stack = f" x{it['stackSize']}" if it.get("stackSize") else ""
        print(" -", it.get("typeLine"), stack)