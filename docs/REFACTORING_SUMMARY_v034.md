# KISS Overlay Refactoring Summary (v0.3.4+)

## Changes Overview

Complete reorganization of KISS Overlay into dedicated package with Win32 API enhancements and hotkey system.

---

## File Structure Changes

### New Directory Structure
```
kiss_overlay/
├── __init__.py                      # Package marker (v0.3.4)
├── kiss_overlay_standalone.py       # Main overlay application (372 lines)
├── kiss_overlay_state_writer.py     # JSON state writer (95 lines)
├── kiss_overlay_templates.py        # String-based templates (200 lines)
├── kiss_overlay_state.json          # Runtime state (created by tracker)
├── kiss_overlay_position.json       # Window position (created by overlay)
└── KISS_OVERLAY_README.md          # Documentation
```

### Renamed Files
| Old Location | New Location | Changes |
|--------------|--------------|---------|
| `overlay_state_writer.py` | `kiss_overlay/kiss_overlay_state_writer.py` | Renamed, updated default path |
| `kiss_overlay_standalone.py` | `kiss_overlay/kiss_overlay_standalone.py` | Moved, added Win32 + hotkeys |
| `kiss_overlay_templates.py` | `kiss_overlay/kiss_overlay_templates.py` | Moved (no changes) |
| `overlay_state.json` | `kiss_overlay/kiss_overlay_state.json` | Moved, updated path in config |

---

## New Features (v0.3.4)

### 1. Win32 API Integration
- **Always-on-Top:** Uses `SetWindowPos()` with `HWND_TOPMOST` flag
- **Click-Through:** Toggleable `WS_EX_TRANSPARENT` extended style
- **Layered Window:** `WS_EX_LAYERED` with 75% opacity via `SetLayeredWindowAttributes()`
- **Documentation:** Researched from official Microsoft Learn docs

**Win32 Constants:**
```python
GWL_EXSTYLE = -20                # Extended window styles
WS_EX_LAYERED = 0x00080000       # Layered window (alpha support)
WS_EX_TRANSPARENT = 0x00000020   # Click-through mode
HWND_TOPMOST = -1                # Always-on-top Z-order
LWA_ALPHA = 0x00000002           # Layered alpha attribute
```

### 2. Global Hotkey System
- **F10:** Toggle visibility (show/hide overlay window)
- **Shift+F10:** Toggle click-through mode (green ↔ orange)
- Uses `keyboard` library with `suppress=True` for global capture
- Registered via `_setup_hotkeys()` method

### 3. Position Persistence
- **Auto-save:** Window position saved on exit via `atexit.register()`
- **Auto-load:** Position restored from `kiss_overlay_position.json` on startup
- Saves: x, y, width, height

### 4. Visual Feedback
- **Green title:** Click-through ON (clicks pass through overlay)
- **Orange title:** Click-through OFF (overlay draggable)
- **Status messages:** Console output for all toggles

---

## Updated Imports

### Main Tracker
```python
# OLD
from overlay_state_writer import OverlayStateWriter

# NEW
from kiss_overlay.kiss_overlay_state_writer import OverlayStateWriter
```

### Test Files
```python
# OLD
from kiss_overlay_templates import get_template_for_phase

# NEW
from kiss_overlay.kiss_overlay_templates import get_template_for_phase
```

---

## Configuration Changes

### config.py
```python
# OLD
KISS_OVERLAY_STATE_FILE = "overlay_state.json"

# NEW
KISS_OVERLAY_STATE_FILE = "kiss_overlay/kiss_overlay_state.json"
```

### .gitignore
```
# OLD
overlay_state.json
overlay_state.json.tmp

# NEW
kiss_overlay/kiss_overlay_state.json
kiss_overlay/kiss_overlay_state.json.tmp
kiss_overlay/kiss_overlay_position.json
```

---

## Running the Overlay

### From Project Root
```bash
cd kiss_overlay
py kiss_overlay_standalone.py
```

### Output
```
   ✅ Hotkeys registered (F10, Shift+F10)
   ✅ Click-through enabled by default (WS_EX_TRANSPARENT)
   ✅ Always-on-top enforced (HWND_TOPMOST)
🔍 KISS Overlay (Standalone) started
   State file: ../kiss_overlay_state.json
   Poll interval: 500ms

   🎮 Hotkeys:
      F10         → Toggle visibility (show/hide)
      Shift+F10   → Toggle click-through (green/orange)

   🎨 Title Colors:
      🟢 Green    → Click-through ON (clicks pass through)
      🟠 Orange   → Click-through OFF (draggable)

   💾 Position saved on exit → kiss_overlay_position.json
   ❌ Close window or Ctrl+C to exit
```

---

## Modified Methods

### kiss_overlay_standalone.py

#### New Methods
```python
def _setup_hotkeys(self):
    """Register F10 and Shift+F10 global hotkeys"""
    
def _load_position(self):
    """Load window position from kiss_overlay_position.json"""
    
def _save_position(self):
    """Save window position on exit (called by atexit)"""
    
def _toggle_visibility(self):
    """Toggle window visibility with F10"""
```

#### Updated Methods
```python
def __init__(self, state_file="../kiss_overlay_state.json", position_file="kiss_overlay_position.json", poll_interval_ms=500):
    # Added position_file parameter
    # Loads saved position on startup
    # Registers atexit handler for position save
    # Calls _setup_hotkeys()

def _apply_win32_styles(self):
    # Always starts with click-through ON
    # Removed click_through parameter
    
def _toggle_click_through(self):
    # Removed event parameter (called by hotkey)
    # Updated status messages (Shift+F10 instead of right-click)
    # Prints console feedback
```

---

## Breaking Changes

### Removed Features
- ❌ `--no-click-through` command-line argument
- ❌ Right-click to toggle (replaced with Shift+F10 hotkey)
- ❌ `click_through` parameter in `__init__`
- ❌ `self.click_through_enabled` instance variable

### Why Removed?
- **WS_EX_TRANSPARENT blocks ALL mouse events** including right-click and Ctrl+drag
- Hotkeys work globally without mouse interaction
- Overlay always starts with click-through ON (most common use case)
- Simpler UX: F10 for visibility, Shift+F10 for mode toggle

---

## Testing

### Verified Working ✅
1. Directory structure created successfully
2. All files moved and renamed
3. Imports updated across codebase
4. Overlay launches without errors
5. Hotkeys registered (F10, Shift+F10)
6. Win32 API features active (always-on-top, click-through)
7. Position persistence (JSON created on exit)
8. Console output shows all features active

### Test Command
```bash
cd kiss_overlay
py kiss_overlay_standalone.py
```

### Expected Behavior
- Window appears always-on-top
- Title bar is GREEN (click-through ON)
- F10 toggles visibility
- Shift+F10 toggles click-through (green ↔ orange)
- Window position saved when closed

---

## Files Updated

### Core Files (7)
1. `kiss_overlay/kiss_overlay_standalone.py` - Main overlay app
2. `kiss_overlay/kiss_overlay_state_writer.py` - State writer
3. `kiss_overlay/kiss_overlay_templates.py` - Templates
4. `config.py` - Updated state file path
5. `poe_stats_refactored_v2.py` - Updated import
6. `.gitignore` - Updated exclusion paths
7. `kiss_overlay/__init__.py` - Package marker (new)

### Test Files (3)
8. `test_overlay_init.py` - Updated import
9. `test_kiss_templates.py` - Updated import
10. `test_overlay_templates.py` - Updated import

---

## Documentation TODO

The following documentation files need updating:
- [ ] `IMPLEMENTATION_SUMMARY.md` - Update file paths and Win32 API features
- [ ] `kiss_overlay/KISS_OVERLAY_README.md` - Add hotkey documentation, Win32 API details
- [ ] `.github/copilot-instructions.md` - Update file structure section
- [ ] `README.md` - Update KISS Overlay section if present

---

## Git Commit Message (Suggested)

```bash
feat: ✨ Reorganize KISS Overlay with Win32 API + hotkeys

- Create kiss_overlay/ package with consistent naming
- Implement Win32 API: always-on-top, click-through, layered alpha
- Add global hotkeys: F10 (visibility), Shift+F10 (click-through)
- Add position persistence (kiss_overlay_position.json)
- Remove mouse-based toggle (WS_EX_TRANSPARENT blocks all mouse)
- Update all imports across codebase
- Update config.py, .gitignore with new paths

BREAKING: Removed --no-click-through arg, right-click toggle
```

---

## References

**Microsoft Learn Documentation:**
- [SetWindowPos function](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowpos)
- [Extended Window Styles](https://learn.microsoft.com/en-us/windows/win32/winmsg/extended-window-styles)
- [SetLayeredWindowAttributes](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setlayeredwindowattributes)
- [GetWindowLongW/SetWindowLongW](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowlongw)

**Related Files:**
- `.github/copilot-instructions.md` - KISS Overlay architecture patterns
- `docs/SESSION_FLOW.md` - Phase-based flow controller
- `notification_templates.py` - Template variable reference (40+ vars)
