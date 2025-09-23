import json
import uuid
import datetime as dt
import os
from pathlib import Path
from collections import Counter

def log_run(char, added, removed, current_map_info=None, map_value=None, log_file=None, map_runtime=None):
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
        "map_value": map_value,
        "map_runtime": round(map_runtime, 2) if map_runtime is not None else None,
        "added_count": len(added),
        "removed_count": len(removed),
        "added": aggregate(added),       # ggf. strippen/kompakt machen
        "removed": aggregate(removed),
    }
    if log_file is None:
        # Default log file path if not provided
        log_file = Path(os.path.dirname(os.path.abspath(__file__))) / "runs.jsonl"
    
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def aggregate(items):
    c = Counter()
    for it in items:
        c[it.get("typeLine")] += int(it.get("stackSize") or 1)
    # Liste aus Dicts (besser fürs Lesen)
    return [{"name": n, "stack": s} for n, s in c.items()]