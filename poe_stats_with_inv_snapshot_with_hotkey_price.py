import requests
import time
from urllib.parse import quote
import keyboard
from win11toast import notify
import json
import datetime as dt
from pathlib import Path
import uuid
import os
from collections import Counter
import re

CLIENT_ID = "dillapoe2stat"        # deine Client Id
CLIENT_SECRET = "UgraAmlUXdP1"  # hier dein Secret eintragen

CHAR_TO_CHECK = "Mettmanwalking"
# make sure the path is where the script is located
LOG = Path(os.path.dirname(os.path.abspath(__file__))) / "runs.jsonl"
CLIENT_LOG = r"C:\GAMESSD\Path of Exile 2\logs\Client.txt"  # anpassen!

AUTH_URL = "https://www.pathofexile.com/oauth/token"
API_URL = "https://api.pathofexile.com"

USER_AGENT = "DillaPoE2Stat/0.1 (+you@example.com)"

# passt auf die von dir gezeigte Zeile
GEN_RE = re.compile(
    r'^(?P<ts>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*?Generating level (?P<lvl>\d+) area "(?P<code>[^"]+)" with seed (?P<seed>\d+)',
    re.IGNORECASE
)

def code_to_title(code: str) -> str:
    # "MapAzmerianRanges" -> "Azmerian Ranges"
    if code.startswith("Map"):
        code = code[3:]
    out = []
    for i, ch in enumerate(code):
        if i and ch.isupper() and (not code[i-1].isupper()):
            out.append(" ")
        out.append(ch)
    return "".join(out).strip()

def get_last_map_from_client(client_path, scan_bytes=1_500_000):
    size = os.path.getsize(client_path)
    with open(client_path, "rb") as f:
        f.seek(max(0, size - scan_bytes))
        buf = f.read()
    text = buf.decode("utf-8", errors="ignore")
    for line in reversed(text.splitlines()):
        m = GEN_RE.search(line)
        if m:
            ts  = m.group("ts")
            lvl = int(m.group("lvl"))
            code = m.group("code")
            seed = int(m.group("seed"))
            return {
                "timestamp": ts,
                "level": lvl,
                "map_code": code,
                "map_name": code_to_title(code),
                "seed": seed,
                "raw": line
            }
    return None

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

def aggregate(items):
    c = Counter()
    for it in items:
        c[it.get("typeLine")] += int(it.get("stackSize") or 1)
    # Liste aus Dicts (besser fürs Lesen)
    return [{"name": n, "stack": s} for n, s in c.items()]

def log_run(char, added, removed):
    global current_map_info
    rec = {
        "run_id": str(uuid.uuid4()),
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "character": char,
        "map": {
            "name": current_map_info["map_name"],
            "level": current_map_info["level"]
        } if current_map_info else {
            "name": "Unknown",
            "level": 0
        },
        "added_count": len(added),
        "removed_count": len(removed),
        "added": aggregate(added),       # ggf. strippen/kompakt machen
        "removed": aggregate(removed),
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")



if __name__ == "__main__":
    token = get_token()
    chars = get_characters(token)
    if not chars.get("characters"):
        print("No characters found")
        raise SystemExit

    name = CHAR_TO_CHECK
    notify('Starting DillaPoE2Stat', f'Watching character: {name}', icon='file://C:/temp/PythonPlayground/Dillapoe2stat/cat64x64.png')
    print(f"Using character: {name}")
    print("Hotkeys:  F2 = PRE snapshot   |   F3 = POST snapshot + diff   |   Esc = quit")

    pre_inv = None
    current_map_info = None  # global variable to store current map info
    last_call = 0.0  # timestamp of last API call

    def rate_limit(min_gap=2.5):
        global last_call
        now = time.time()
        wait = min_gap - (now - last_call)
        if wait > 0:
            time.sleep(wait)
        last_call = time.time()

    def do_pre():
        global pre_inv, current_map_info
        rate_limit()
        try:
            pre_inv = snapshot_inventory(token, name)
            print(f"[PRE] captured: {len(pre_inv)} items")
            
            # print the whole inventory for debugging with every item on a new line and every detail available
            #for item in pre_inv:
            #    print(json.dumps(item, indent=2, ensure_ascii=False))


            current_map_info = get_last_map_from_client(CLIENT_LOG)
            if current_map_info:
                print(f"[MAP] {current_map_info['map_name']} (T{current_map_info['level']}, seed {current_map_info['seed']})")
            mapname = current_map_info["map_name"] if current_map_info else "Unknown"
            notify('Hallo Dilla!', f'Starting Map Run! {mapname}')
        except Exception as e:
            print("[PRE] error:", e)

    def do_post():
        global pre_inv
        if pre_inv is None:
            print("[POST] no PRE snapshot yet. Press F2 first.")
            return
        rate_limit()
        try:
            inv_after = snapshot_inventory(token, name)
            print(f"[POST] captured: {len(inv_after)} items")
            added, removed = diff_inventories(pre_inv, inv_after)

            print(f"\nAdded items ({len(added)}):")
            for it in added:
                stack = f" x{it['stackSize']}" if it.get("stackSize") else ""
                print(" +", it.get("typeLine"), stack, "@", (it.get("x"), it.get("y")))

            print(f"\nRemoved items ({len(removed)}):")
            for it in removed:
                stack = f" x{it['stackSize']}" if it.get("stackSize") else ""
                print(" -", it.get("typeLine"), stack)
            print("\n=== ready for next map ===\n")
            notify('Hallo Dilla!', 'Map Run done!')
            log_run(name, added, removed)
        except Exception as e:
            print("[POST] error:", e)
        finally:
            pre_inv = None  # reset for next run

    keyboard.add_hotkey('f2', do_pre)
    keyboard.add_hotkey('f3', do_post)

    try:
        keyboard.wait('esc')
    except KeyboardInterrupt:
        pass
    finally:
        print("Bye.")
