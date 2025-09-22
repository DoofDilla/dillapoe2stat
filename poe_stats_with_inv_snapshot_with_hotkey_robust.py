import requests, time, threading
from urllib.parse import quote
import keyboard
from win10toast import ToastNotifier
from queue import Queue

CLIENT_ID = "dillapoe2stat"
CLIENT_SECRET = "UgraAmlUXdP1"
CHAR_TO_CHECK = "Mettmanwalking"

AUTH_URL = "https://www.pathofexile.com/oauth/token"
API_URL  = "https://api.pathofexile.com"
USER_AGENT = "DillaPoE2Stat/0.1 (+you@example.com)"

toaster = ToastNotifier()
pre_inv = None
last_call = 0.0

def get_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "account:characters account:profile",
    }
    r = requests.post(AUTH_URL, data=data, headers={"User-Agent": USER_AGENT}, timeout=15)
    r.raise_for_status()
    tok = r.json()
    print("Got token, expires in", tok.get("expires_in"), "seconds")
    return tok["access_token"]

def get_characters(access_token):
    headers = {"Authorization": f"Bearer {access_token}", "User-Agent": USER_AGENT}
    r = requests.get(f"{API_URL}/character/poe2", headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()

def get_character_details(access_token, name):
    headers = {"Authorization": f"Bearer {access_token}", "User-Agent": USER_AGENT}
    r = requests.get(f"{API_URL}/character/poe2/{quote(name)}", headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()

def snapshot_inventory(access_token, name):
    details = get_character_details(access_token, name)
    char = details.get("character", {})
    inv = char.get("inventory", [])
    return inv

def inv_key(item):
    return item.get("id") or f"{item.get('typeLine')}|{item.get('x')},{item.get('y')}|{item.get('baseType')}"

def diff_inventories(before, after):
    before_keys = {inv_key(i): i for i in before}
    after_keys  = {inv_key(i): i for i in after}
    added = [after_keys[k] for k in after_keys if k not in before_keys]
    removed = [before_keys[k] for k in before_keys if k not in after_keys]
    return added, removed

def rate_limit(min_gap=2.5):
    global last_call
    now = time.time()
    wait = min_gap - (now - last_call)
    if wait > 0:
        time.sleep(wait)
    last_call = time.time()

def safe_toast(title, msg, duration=5):
    try:
        toaster.show_toast(title, msg, duration=duration, threaded=True)
    except Exception as e:
        # niemals Exception aus Hotkey in den Hook-Thread blubbern lassen
        print("[TOAST] error:", e)

def job_pre(token, name):
    global pre_inv
    try:
        rate_limit()
        pre_inv = snapshot_inventory(token, name)
        print(f"[PRE] captured: {len(pre_inv)} items")
        safe_toast("PoE2 Snapshot", "PRE captured.", 3)
    except Exception as e:
        print("[PRE] error:", e)
        safe_toast("PoE2 Snapshot", f"PRE error: {e}", 5)

def job_post(token, name):
    global pre_inv
    if pre_inv is None:
        print("[POST] no PRE snapshot yet. Press F9 first.")
        safe_toast("PoE2 Snapshot", "No PRE snapshot. Press F9.", 4)
        return
    try:
        rate_limit()
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
        safe_toast("Hallo Dilla!", "Map Run done!", 5)
    except Exception as e:
        print("[POST] error:", e)
        safe_toast("PoE2 Snapshot", f"POST error: {e}", 5)
    finally:
        pre_inv = None

# Worker-Queue: Hotkeys posten nur noch Jobs → Hook-Thread bleibt sauber
q = Queue()

def worker_loop(token, name):
    while True:
        fn = q.get()
        if fn is None:
            break
        try:
            fn(token, name)
        except Exception as e:
            print("[WORKER] uncaught:", e)
        finally:
            q.task_done()

if __name__ == "__main__":
    token = get_token()
    chars = get_characters(token)
    if not chars.get("characters"):
        print("No characters found"); raise SystemExit

    name = CHAR_TO_CHECK
    print(f"Using character: {name}")
    print("Hotkeys:  F2 = PRE snapshot   |   F3 = POST snapshot + diff   |   Esc = quit")

    threading.Thread(target=worker_loop, args=(token, name), daemon=True).start()

    # WICHTIG: hier nur enqueue, keinerlei I/O/Network im Hook-Thread
    keyboard.add_hotkey('f2',  lambda: q.put(job_pre))
    keyboard.add_hotkey('f3', lambda: q.put(job_post))

    try:
        keyboard.wait('esc')
    except KeyboardInterrupt:
        pass
    finally:
        q.put(None)
        print("Bye.")
