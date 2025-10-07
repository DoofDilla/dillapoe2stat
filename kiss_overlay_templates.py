# kiss_overlay_templates.py
"""
KISS Overlay Templates
Builds display text from notification template variables
"""


def build_overlay_text(phase_name: str, template_vars: dict) -> str:
    """
    Build overlay display text from template variables
    
    Args:
        phase_name: Human-readable phase name (e.g. "POST-5: Update Session 🔴")
        template_vars: Template variables from NotificationManager.get_template_variables()
        
    Returns:
        Formatted multi-line string for overlay display
    """
    lines = []
    
    # Header: Current Phase
    lines.append(f"Phase: {phase_name}")
    lines.append("─" * 36)
    
    # Section 1: Waystone Info (if available)
    waystone_tier = template_vars.get("waystone_tier")
    if waystone_tier and waystone_tier != "?":
        delirious = template_vars.get("waystone_delirious", "0")
        pack_size = template_vars.get("waystone_pack_size", "0")
        
        lines.append(f"Waystone: T{waystone_tier} | {delirious}% Delirium")
        if pack_size != "0":
            lines.append(f"Pack Size: +{pack_size}%")
        lines.append("─" * 36)
    
    # Section 2: Session Stats (if available)
    session_maps = template_vars.get("session_maps_completed")
    if session_maps and session_maps != "0":
        session_ex_h = template_vars.get("session_value_per_hour_fmt", "0ex/h")
        session_time = template_vars.get("session_runtime_str", "0m")
        
        lines.append(f"Session: {session_maps} maps | {session_ex_h}")
        lines.append(f"Runtime: {session_time}")
        lines.append("─" * 36)
    
    # Section 3: Last Map (if available)
    map_value = template_vars.get("map_value_fmt")
    map_name = template_vars.get("map_name")
    if map_value and map_name:
        lines.append(f"Last Map: {map_value}")
        lines.append(f"Area: {map_name}")
        
        # Top drop from last map
        drop_name = template_vars.get("map_drop_1_name")
        if drop_name and drop_name != "None":
            drop_value = template_vars.get("map_drop_1_value_fmt", "")
            lines.append(f"Top Drop: {drop_name} ({drop_value})")
        
        lines.append("─" * 36)
    
    # Section 4: Session Best (if different from last map)
    session_drop = template_vars.get("session_drop_1_name")
    if session_drop and session_drop != "None":
        session_drop_value = template_vars.get("session_drop_1_value_fmt", "")
        lines.append(f"Session Best: {session_drop}")
        if session_drop_value:
            lines.append(f"Value: {session_drop_value}")
    
    return "\n".join(lines)


def build_waystone_analysis_text(template_vars: dict) -> str:
    """
    Build overlay text specifically for waystone analysis (Ctrl+F2)
    
    Args:
        template_vars: Template variables from NotificationManager.get_template_variables()
        
    Returns:
        Formatted multi-line string for waystone analysis display
    """
    lines = []
    
    # Header
    lines.append("Waystone Analysis")
    lines.append("─" * 36)
    
    # Waystone details
    waystone_name = template_vars.get("waystone_name", "Unknown Waystone")
    waystone_tier = template_vars.get("waystone_tier", "?")
    delirious = template_vars.get("waystone_delirious", "0")
    
    lines.append(f"{waystone_name}")
    lines.append(f"Tier: {waystone_tier} | Delirium: {delirious}%")
    
    # Modifiers (prefixes and suffixes)
    prefixes = template_vars.get("waystone_prefixes", "0")
    suffixes = template_vars.get("waystone_suffixes", "0")
    if prefixes != "0" or suffixes != "0":
        lines.append(f"Prefixes: {prefixes} | Suffixes: {suffixes}")
    
    lines.append("─" * 36)
    
    # Area modifiers
    pack_size = template_vars.get("pack_size", "0")
    magic_monsters = template_vars.get("magic_monsters", "0")
    rare_monsters = template_vars.get("rare_monsters", "0")
    item_rarity = template_vars.get("item_rarity", "0")
    waystone_drop = template_vars.get("waystone_drop_chance", "0")
    
    if pack_size != "0":
        lines.append(f"Pack Size: +{pack_size}%")
    if magic_monsters != "0":
        lines.append(f"Magic Monsters: +{magic_monsters}%")
    if rare_monsters != "0":
        lines.append(f"Rare Monsters: +{rare_monsters}%")
    if item_rarity != "0":
        lines.append(f"Item Rarity: +{item_rarity}%")
    if waystone_drop != "0":
        lines.append(f"Waystone Drop: +{waystone_drop}%")
    
    lines.append("─" * 36)
    
    # Session context (if available)
    session_maps = template_vars.get("session_maps_completed", "0")
    if session_maps != "0":
        session_ex_h = template_vars.get("session_value_per_hour_fmt", "0ex/h")
        lines.append(f"Session: {session_maps} maps | {session_ex_h}")
    
    # Comparison to session average (if available)
    avg_value = template_vars.get("session_avg_value_fmt")
    if avg_value:
        lines.append(f"Avg Map Value: {avg_value}")
    
    return "\n".join(lines)


def build_pre_snapshot_text(template_vars: dict) -> str:
    """PRE-1: Snapshot phase - minimal info"""
    waystone_tier = template_vars.get("waystone_tier", "?")
    delirious = template_vars.get("waystone_delirious", "0")
    
    return f"""Phase: PRE-1: Snapshot
────────────────────────────────────
Preparing: T{waystone_tier} ({delirious}% Delirium)
Taking inventory snapshot...
"""


def build_post_update_session_text(template_vars: dict) -> str:
    """POST-5: Update Session - CRITICAL PHASE (red)"""
    map_value = template_vars.get("map_value_fmt", "0ex")
    session_maps = template_vars.get("session_maps_completed", "0")
    session_ex_h = template_vars.get("session_value_per_hour_fmt", "0ex/h")
    
    return f"""Phase: POST-5: Update Session 🔴
────────────────────────────────────
⚠️  CRITICAL: Adding map to session
────────────────────────────────────
Map Value: {map_value}
Session: {session_maps} maps | {session_ex_h}
"""


def get_template_for_phase(phase: str, phase_name: str, template_vars: dict) -> str:
    """
    Get appropriate template text for current phase
    
    Args:
        phase: Phase key (e.g. 'post_update_session')
        phase_name: Display name (e.g. 'POST-5: Update Session 🔴')
        template_vars: Template variables dict
        
    Returns:
        Formatted display text
    """
    # Special templates for specific phases
    if phase == 'waystone_analysis':
        return build_waystone_analysis_text(template_vars)
    elif phase == 'pre_snapshot':
        return build_pre_snapshot_text(template_vars)
    elif phase == 'post_update_session':
        return build_post_update_session_text(template_vars)
    
    # Default template for all other phases
    return build_overlay_text(phase_name, template_vars)
