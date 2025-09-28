import json
import uuid
import datetime as dt
import os
from pathlib import Path
from collections import Counter

def extract_waystone_attributes(map_info):
    """Extract waystone attributes from map_info with proper fallback logic"""
    if not map_info:
        return get_fallback_waystone_attributes()
    
    # Check if we have waystone area_modifiers (from experimental waystone analysis)
    area_modifiers = map_info.get("area_modifiers", {})
    has_waystone_info = bool(area_modifiers and len(area_modifiers) > 0)
    
    if has_waystone_info:
        # Extract numeric values from area modifier strings like "+70%"
        return {
            "hasAttributeInfo": True,
            "tier": int(map_info.get("level", 0)) if map_info.get("level") != "Unknown" else 0,
            "magic_monsters": extract_numeric_value(area_modifiers.get("magic_monsters", {}).get("value", "0")),
            "rare_monsters": extract_numeric_value(area_modifiers.get("rare_monsters", {}).get("value", "0")),
            "item_rarity": extract_numeric_value(area_modifiers.get("item_rarity", {}).get("value", "0")),
            "item_quantity": extract_numeric_value(area_modifiers.get("item_quantity", {}).get("value", "0")),
            "waystone_drop_chance": extract_numeric_value(area_modifiers.get("waystone_drop_chance", {}).get("value", "0")),
            "pack_size": extract_numeric_value(area_modifiers.get("pack_size", {}).get("value", "0"))
        }
    else:
        # No waystone info available (normal client log maps)
        return get_fallback_waystone_attributes()

def get_fallback_waystone_attributes():
    """Return fallback waystone attributes with all values set to 0"""
    return {
        "hasAttributeInfo": False,
        "tier": 0,
        "magic_monsters": 0,
        "rare_monsters": 0,
        "item_rarity": 0,
        "item_quantity": 0,
        "waystone_drop_chance": 0,
        "pack_size": 0
    }

def extract_numeric_value(value_string):
    """Extract numeric value from strings like '+70%' or '70%' or '70'"""
    if not value_string:
        return 0
    
    # Remove common prefixes and suffixes
    clean_value = str(value_string).replace("+", "").replace("%", "").replace("-", "").strip()
    
    try:
        return int(float(clean_value))
    except (ValueError, TypeError):
        return 0

def log_run(char, added, removed, current_map_info=None, map_value=None, log_file=None, map_runtime=None, session_id=None, gear_rarity=None):
    # Extract waystone attributes with fallback logic
    waystone_attrs = extract_waystone_attributes(current_map_info)
    
    rec = {
        "run_id": str(uuid.uuid4()),
        "session_id": session_id,
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "character": char,
        "gear_rarity": gear_rarity,  # Character's total item rarity from equipment
        "map": {
            "name": current_map_info["map_name"],
            "level": current_map_info["level"],
            "seed": current_map_info.get("seed"),
            "source": current_map_info.get("source", "client_log"),
            # Include waystone attributes if available (but not prefixes/suffixes)
            "waystone_tier": current_map_info.get("waystone_tier"),
            "area_modifiers": current_map_info.get("area_modifiers", {}),
            "modifier_count": current_map_info.get("modifier_count"),
            "waystone_attributes": waystone_attrs
        } if current_map_info else {
            "name": "Unknown",
            "level": 0,
            "waystone_attributes": get_fallback_waystone_attributes()
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