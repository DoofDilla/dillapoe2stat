import requests
from urllib.parse import quote

AUTH_URL = "https://www.pathofexile.com/oauth/token"
API_URL = "https://api.pathofexile.com"
USER_AGENT = "DillaPoE2Stat/0.1 (+you@example.com)"

def get_token(client_id, client_secret):
    """Get OAuth token for Path of Exile API access"""
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "account:characters account:profile",
    }
    r = requests.post(AUTH_URL, data=data, headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    tok = r.json()
    print("Got token, expires in", tok.get("expires_in"), "seconds")
    return tok["access_token"]

def get_characters(access_token):
    """Get list of characters from Path of Exile API"""
    headers = {"Authorization": f"Bearer {access_token}",
               "User-Agent": USER_AGENT}
    r = requests.get(f"{API_URL}/character/poe2", headers=headers)
    r.raise_for_status()
    return r.json()

def get_character_details(access_token, name):
    """Get detailed information about a specific character"""
    headers = {"Authorization": f"Bearer {access_token}",
               "User-Agent": USER_AGENT}
    r = requests.get(f"{API_URL}/character/poe2/{quote(name)}", headers=headers)
    r.raise_for_status()
    return r.json()

def snapshot_inventory(access_token, name):
    """Take a snapshot of a character's inventory"""
    details = get_character_details(access_token, name)
    char = details.get("character", {})
    inv = char.get("inventory", [])
    return inv