import requests
from urllib.parse import quote
from oauth_flow import get_access_token

API_URL = "https://api.pathofexile.com"
USER_AGENT = "DillaPoE2Stat/0.4.0 (+github.com/DoofDilla/dillapoe2stat)"

def get_token(client_id=None, client_secret=None):
    """
    Get OAuth token for Path of Exile API access
    
    Uses OAuth 2.1 Authorization Code Flow with PKCE.
    Opens browser for user authorization on first run.
    Auto-refreshes token when expired.
    
    Args:
        client_id: Ignored (kept for compatibility)
        client_secret: Ignored (kept for compatibility)
    
    Returns:
        str: Valid access token
    """
    # New OAuth 2.1 flow - ignores old credentials
    return get_access_token()

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