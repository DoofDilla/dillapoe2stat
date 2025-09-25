import json
import uuid
import datetime as dt
import os
from pathlib import Path
from collections import Counter

def log_run(char, added, removed, current_map_info=None, map_value=None, log_file=None, map_runtime=None, session_id=None):
    rec = {
        "run_id": str(uuid.uuid4()),
        "session_id": session_id,
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "character": char,
        "map": {
            "name": current_map_info["map_name"],
            "level": current_map_info["level"],
            "seed": current_map_info.get("seed"),
            "source": current_map_info.get("source", "client_log"),
            # Include waystone attributes if available (but not prefixes/suffixes)
            "waystone_tier": current_map_info.get("waystone_tier"),
            "area_modifiers": current_map_info.get("area_modifiers", {}),
            "modifier_count": current_map_info.get("modifier_count")
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

def log_session_start(session_id, char, log_file=None):
    """Log the start of a new session"""
    rec = {
        "event_type": "session_start",
        "session_id": session_id,
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "character": char,
    }
    if log_file is None:
        log_file = Path(os.path.dirname(os.path.abspath(__file__))) / "sessions.jsonl"
    
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def log_session_end(session_id, char, total_runtime, total_value, total_maps, log_file=None):
    """Log the end of a session with summary statistics"""
    rec = {
        "event_type": "session_end",
        "session_id": session_id,
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "character": char,
        "session_runtime": round(total_runtime, 2) if total_runtime is not None else None,
        "total_value": total_value,
        "total_maps": total_maps,
    }
    if log_file is None:
        log_file = Path(os.path.dirname(os.path.abspath(__file__))) / "sessions.jsonl"
    
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def get_session_stats(session_id, runs_log_file=None):
    """Get statistics for a specific session"""
    if runs_log_file is None:
        runs_log_file = Path(os.path.dirname(os.path.abspath(__file__))) / "runs.jsonl"
    
    if not runs_log_file.exists():
        return {"total_maps": 0, "total_value": 0, "total_runtime": 0, "maps": []}
    
    session_runs = []
    total_value = 0
    total_runtime = 0
    
    with runs_log_file.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                run = json.loads(line.strip())
                if run.get("session_id") == session_id:
                    session_runs.append(run)
                    if run.get("map_value"):
                        total_value += run["map_value"]
                    if run.get("map_runtime"):
                        total_runtime += run["map_runtime"]
            except json.JSONDecodeError:
                continue
    
    return {
        "total_maps": len(session_runs),
        "total_value": total_value,
        "total_runtime": total_runtime,
        "maps": session_runs
    }

def aggregate(items):
    c = Counter()
    for it in items:
        c[it.get("typeLine")] += int(it.get("stackSize") or 1)
    # Liste aus Dicts (besser fürs Lesen)
    return [{"name": n, "stack": s} for n, s in c.items()]