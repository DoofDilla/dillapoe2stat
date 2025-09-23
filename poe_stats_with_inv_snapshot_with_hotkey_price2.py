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
from price_check_poe2 import valuate_items_raw, fmt  # fmt nur für hübsche Ausgabe
from client_parsing import get_last_map_from_client
from poe_logging import log_run

CLIENT_ID = "dillapoe2stat"        # deine Client Id
CLIENT_SECRET = "UgraAmlUXdP1"  # hier dein Secret eintragen

CHAR_TO_CHECK = "Mettmanwalking"
# make sure the path is where the script is located
LOG = Path(os.path.dirname(os.path.abspath(__file__))) / "runs.jsonl"

CLIENT_LOG = r"C:\GAMESSD\Path of Exile 2\logs\Client.txt"  # anpassen!

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
        raise SystemExit

    name = CHAR_TO_CHECK
    # get the current absolute path of the script and create the string for the icon
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, 'cat64x64.png')

    notify('Starting DillaPoE2Stat', f'Watching character: {name}', icon=f'file://{icon_path}')
    print(f"Using character: {name}")
    print("Hotkeys:  F2 = PRE snapshot   |   F3 = POST snapshot + diff   |   Esc = quit")

    pre_inv = None
    current_map_info = None
    map_value = None
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
        global pre_inv, map_value, current_map_info
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

            # ==== Price Check (Chaos & Ex, mit poe.ninja PoE2 temp endpoint) ====
            try:
                added_rows, (add_c, add_e) = valuate_items_raw(added)
                removed_rows, (rem_c, rem_e) = valuate_items_raw(removed)

                print("\n[VALUE] Added:")
                for r in added_rows:
                    print(f" + {r['name']} [{r.get('category') or 'n/a'}] x{r['qty']}  "
                        f"=> {fmt(r['chaos_total'])}c"
                        f"{'' if r['ex_total'] is None else ' | ' + fmt(r['ex_total']) + 'ex'}")

                print("\n[VALUE] Removed:")
                for r in removed_rows:
                    print(f" - {r['name']} [{r.get('category') or 'n/a'}] x{r['qty']}  "
                        f"=> {fmt(r['chaos_total'])}c"
                        f"{'' if r['ex_total'] is None else ' | ' + fmt(r['ex_total']) + 'ex'}")

                net_c = (add_c or 0) - (rem_c or 0)
                net_e = None
                if add_e is not None and rem_e is not None:
                    net_e = (add_e or 0) - (rem_e or 0)

                print(f"\n[VALUE] Totals:  +{fmt(add_c)}c  /  -{fmt(rem_c)}c  =>  Net {fmt(net_c)}c")
                if net_e is not None:
                    print(f"                 +{fmt(add_e)}ex /  -{fmt(rem_e)}ex =>  Net {fmt(net_e)}ex")
                    map_value = net_e
            except Exception as pe:
                print("[VALUE] price-check error:", pe)

            print("\n=== ready for next map ===\n")
            notify('Hallo Dilla!', 'Map Run done!' + (f', Value: {fmt(map_value)}ex' if map_value else ''))
            log_run(name, added, removed, current_map_info, map_value, LOG)  # (wenn du willst, erweitern um totals)
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
