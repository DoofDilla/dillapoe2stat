# kiss_overlay_templates.py
"""
KISS Overlay Templates
String-based templates matching notification_templates.py style
Uses conditional sections for dynamic content
"""

# ============================================================================
# TEMPLATE SECTIONS (Reusable building blocks)
# ============================================================================

SECTION_WAYSTONE = """Waystone: T{waystone_tier} | {waystone_delirious}% Delirium
Pack Size: +{waystone_pack_size}%"""

SECTION_SESSION = """Session: {session_maps_completed} maps | {session_value_per_hour_fmt}
Runtime: {session_runtime_str}"""

SECTION_LAST_MAP = """Last Map: {map_value_fmt}
Area: {map_name}"""

SECTION_TOP_DROP = """Top Drop: {map_drop_1_name} ({map_drop_1_value_fmt})"""

SECTION_SESSION_BEST = """Session Best: {session_drop_1_name}
Value: {session_drop_1_value_fmt}"""

# ============================================================================
# PHASE-SPECIFIC TEMPLATES
# ============================================================================

TEMPLATE_DEFAULT = """Phase: {phase_name}
────────────────────────────────────
{waystone_section}
{session_section}
{last_map_section}
{session_best_section}"""

TEMPLATE_PRE_SNAPSHOT = """Phase: PRE-1: Snapshot
────────────────────────────────────
Preparing: T{waystone_tier} ({waystone_delirious}% Delirium)
Taking inventory snapshot..."""

TEMPLATE_POST_UPDATE_SESSION = """Phase: POST-5: Update Session 🔴
────────────────────────────────────
⚠️  CRITICAL: Adding map to session
────────────────────────────────────
Map Value: {map_value_fmt}
Session: {session_maps_completed} maps | {session_value_per_hour_fmt}"""

TEMPLATE_WAYSTONE_ANALYSIS = """Waystone Analysis
────────────────────────────────────
{waystone_name}
Tier: {waystone_tier} | Delirium: {waystone_delirious}%
Prefixes: {waystone_prefixes} | Suffixes: {waystone_suffixes}
────────────────────────────────────
{modifiers_section}
────────────────────────────────────
{session_context_section}"""

# ============================================================================
# HELPER FUNCTIONS (Minimal logic for conditional sections)
# ============================================================================

def _build_conditional_section(template: str, template_vars: dict, required_keys: list) -> str:
    """
    Build a section only if required keys have valid values
    
    Args:
        template: Template string with placeholders
        template_vars: Dict of template variables
        required_keys: List of keys that must exist and be non-empty
        
    Returns:
        Formatted section or empty string
    """
    # Check if all required keys have valid values
    for key in required_keys:
        value = template_vars.get(key, "")
        if not value or value in ["?", "0", "None", "Unknown"]:
            return ""
    
    # All keys valid - format and return
    try:
        return template.format(**template_vars) + "\n────────────────────────────────────"
    except KeyError:
        return ""


def _build_modifiers_section(template_vars: dict) -> str:
    """Build waystone modifiers section (only non-zero values)"""
    modifiers = []
    
    modifier_map = {
        'pack_size': 'Pack Size: +{pack_size}%',
        'magic_monsters': 'Magic Monsters: +{magic_monsters}%',
        'rare_monsters': 'Rare Monsters: +{rare_monsters}%',
        'item_rarity': 'Item Rarity: +{item_rarity}%',
        'waystone_drop_chance': 'Waystone Drop: +{waystone_drop_chance}%'
    }
    
    for key, fmt in modifier_map.items():
        value = template_vars.get(key, "0")
        if value and value != "0":
            modifiers.append(fmt.format(**template_vars))
    
    return "\n".join(modifiers) if modifiers else ""


def _build_session_context(template_vars: dict) -> str:
    """Build session context section for waystone analysis"""
    session_maps = template_vars.get("session_maps_completed", "0")
    if session_maps == "0":
        return ""
    
    lines = [f"Session: {session_maps} maps | {template_vars.get('session_value_per_hour_fmt', '0ex/h')}"]
    
    avg_value = template_vars.get("session_avg_value_fmt")
    if avg_value:
        lines.append(f"Avg Map Value: {avg_value}")
    
    return "\n".join(lines)


# ============================================================================
# MAIN TEMPLATE DISPATCHER
# ============================================================================

def get_template_for_phase(phase: str, phase_name: str, template_vars: dict) -> str:
    """
    Get formatted template text for current phase
    
    Args:
        phase: Phase key (e.g. 'post_update_session')
        phase_name: Display name (e.g. 'POST-5: Update Session 🔴')
        template_vars: Template variables dict
        
    Returns:
        Formatted display text
    """
    # Make a copy to avoid mutating original
    vars_copy = dict(template_vars)
    vars_copy['phase_name'] = phase_name
    
    # Special templates for specific phases
    if phase == 'pre_snapshot':
        return TEMPLATE_PRE_SNAPSHOT.format(**vars_copy)
    
    elif phase == 'post_update_session':
        return TEMPLATE_POST_UPDATE_SESSION.format(**vars_copy)
    
    elif phase == 'waystone_analysis':
        # Build conditional sections
        vars_copy['modifiers_section'] = _build_modifiers_section(vars_copy)
        vars_copy['session_context_section'] = _build_session_context(vars_copy)
        return TEMPLATE_WAYSTONE_ANALYSIS.format(**vars_copy)
    
    # Default template with conditional sections
    else:
        # Build conditional sections
        vars_copy['waystone_section'] = _build_conditional_section(
            SECTION_WAYSTONE, vars_copy, ['waystone_tier']
        )
        vars_copy['session_section'] = _build_conditional_section(
            SECTION_SESSION, vars_copy, ['session_maps_completed']
        )
        vars_copy['last_map_section'] = _build_conditional_section(
            SECTION_LAST_MAP, vars_copy, ['map_value_fmt', 'map_name']
        )
        
        # Top drop (only if exists)
        drop_name = vars_copy.get('map_drop_1_name', 'None')
        if drop_name and drop_name != 'None':
            vars_copy['last_map_section'] += "\n" + SECTION_TOP_DROP.format(**vars_copy)
        
        # Session best
        vars_copy['session_best_section'] = _build_conditional_section(
            SECTION_SESSION_BEST, vars_copy, ['session_drop_1_name']
        )
        
        return TEMPLATE_DEFAULT.format(**vars_copy)
