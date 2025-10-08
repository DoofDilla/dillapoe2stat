# kiss_overlay_standalone.py
"""
KISS Overlay - Standalone File-Polling Version
Reads kiss_overlay_state.json every 500ms, displays phase + key metrics

Features:
- Always-on-top (HWND_TOPMOST via Win32 API)
- Click-through toggle (WS_EX_TRANSPARENT via Shift+F10)
- Window visibility toggle (F10)
- Persistent window position (kiss_overlay_position.json)

Hotkeys:
- F10: Toggle overlay visibility (show/hide)
- Shift+F10: Toggle click-through mode (green) / draggable mode (orange)
"""

import tkinter as tk
from tkinter import font as tkfont
import json
import os
import sys
import ctypes
from ctypes import wintypes
import keyboard
import atexit


# Import template builder
try:
    from kiss_overlay_templates import get_template_for_phase
except ImportError:
    # Fallback if running standalone without template module
    def get_template_for_phase(phase, phase_name, template_vars):
        return f"Phase: {phase_name}\n\nTemplate module not found."


class KISSOverlayStandalone:
    def __init__(self, state_file="../kiss_overlay_state.json", poll_interval_ms=500, 
                 position_file="kiss_overlay_position.json"):
        self.state_file = state_file
        self.poll_interval_ms = poll_interval_ms
        self.position_file = position_file
        self.last_mtime = 0
        self.click_through_active = True  # Start with click-through ON
        self.hwnd = None  # Store window handle for Win32 operations
        self.is_visible = True  # Track visibility state
        
        # Load saved position
        position = self._load_position()
        
        # Tkinter window setup
        self.root = tk.Tk()
        self.root.title("PoE Stats Overlay")
        self.root.overrideredirect(True)  # No window frame
        self.root.wm_attributes("-topmost", True)  # Always on top (Tkinter level)
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.wm_attributes("-alpha", 0.75)
        
        # Window geometry (from saved position or defaults)
        width = position.get("width", 400)
        height = position.get("height", 250)
        x = position.get("x", 50)
        y = position.get("y", 50)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.config(bg='black')
        
        # Content frame
        self.frame = tk.Frame(
            self.root,
            bg='#0d0d0d',
            padx=12,
            pady=10,
            highlightthickness=1,
            highlightbackground='#2a2a2a'
        )
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Fonts
        self.title_font = tkfont.Font(family="Consolas", size=11, weight="bold")
        self.data_font = tkfont.Font(family="Consolas", size=9)
        
        # Title label
        self.title_label = tk.Label(
            self.frame,
            text="🔍 PoE Stats Overlay",
            font=self.title_font,
            fg="#00ff88",
            bg="#0d0d0d"
        )
        self.title_label.pack(anchor='w')
        
        # Data label (updated from JSON)
        self.data_label = tk.Label(
            self.frame,
            text="Waiting for tracker...",
            font=self.data_font,
            fg="#cccccc",
            bg="#0d0d0d",
            justify=tk.LEFT,
            anchor='nw'
        )
        self.data_label.pack(anchor='w', pady=(5, 0), fill=tk.BOTH, expand=True)
        
        # Drag & drop support
        self.drag_data = {"x": 0, "y": 0}
        self.frame.bind("<Button-1>", self._start_drag)
        self.frame.bind("<B1-Motion>", self._on_drag)
        self.title_label.bind("<Button-1>", self._start_drag)
        self.title_label.bind("<B1-Motion>", self._on_drag)
        
        # Setup hotkeys (global)
        self._setup_hotkeys()
        
        # Save position on exit
        atexit.register(self._save_position)
        
        # Apply Win32 API enhancements after window is created
        self.root.update_idletasks()  # Ensure window is created
        self._apply_win32_styles()
        
        # Start file polling
        self.check_file()
    
    def _setup_hotkeys(self):
        """Setup global hotkeys for overlay control"""
        try:
            # F10: Toggle visibility
            keyboard.add_hotkey('f10', self._toggle_visibility, suppress=True)
            
            # Shift+F10: Toggle click-through
            keyboard.add_hotkey('shift+f10', self._toggle_click_through, suppress=True)
            
            print("   ✅ Hotkeys registered (F10, Shift+F10)")
        except Exception as e:
            print(f"   ⚠️  Hotkey registration failed: {e}")
    
    def _load_position(self):
        """Load saved window position from JSON file"""
        try:
            if os.path.exists(self.position_file):
                with open(self.position_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_position(self):
        """Save current window position to JSON file"""
        try:
            position = {
                "x": self.root.winfo_x(),
                "y": self.root.winfo_y(),
                "width": self.root.winfo_width(),
                "height": self.root.winfo_height()
            }
            with open(self.position_file, 'w') as f:
                json.dump(position, f, indent=2)
        except Exception as e:
            print(f"Failed to save position: {e}")
    
    def _apply_win32_styles(self):
        """
        Apply Win32 API styles for always-on-top and click-through
        Uses official Microsoft Win32 API via ctypes
        """
        try:
            # Get window handle
            self.hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            
            # Win32 constants (from Microsoft Learn docs)
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            LWA_ALPHA = 0x00000002
            
            # Get current extended styles
            user32 = ctypes.windll.user32
            current_style = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
            
            # Add WS_EX_LAYERED for alpha transparency
            new_style = current_style | WS_EX_LAYERED
            
            # Add WS_EX_TRANSPARENT for click-through (always start with click-through ON)
            new_style |= WS_EX_TRANSPARENT
            print("   ✅ Click-through enabled by default (WS_EX_TRANSPARENT)")
            
            # Apply new extended styles
            user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, new_style)
            
            # Set layered window attributes (75% opacity)
            alpha = int(255 * 0.75)
            user32.SetLayeredWindowAttributes(self.hwnd, 0, alpha, LWA_ALPHA)
            
            # Enforce always-on-top with HWND_TOPMOST
            user32.SetWindowPos(
                self.hwnd,
                HWND_TOPMOST,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )
            
            print("   ✅ Always-on-top enforced (HWND_TOPMOST)")
            
        except Exception as e:
            print(f"   ⚠️  Win32 API setup failed: {e}")
            print("   → Falling back to Tkinter-only mode")
    
    def _toggle_visibility(self):
        """Toggle overlay visibility (F10)"""
        if self.root.state() == 'withdrawn':
            self.root.deiconify()
            print("   👁️  Overlay visible")
        else:
            self.root.withdraw()
            print("   👁️  Overlay hidden")
    
    def _toggle_click_through(self):
        """Toggle click-through on/off (Shift+F10)"""
        if self.click_through_active:
            # Disable click-through
            try:
                GWL_EXSTYLE = -20
                WS_EX_TRANSPARENT = 0x00000020
                
                user32 = ctypes.windll.user32
                current_style = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
                new_style = current_style & ~WS_EX_TRANSPARENT  # Remove WS_EX_TRANSPARENT
                user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, new_style)
                
                self.click_through_active = False
                self.title_label.config(fg="#ffaa00")  # Orange = interactive mode
                self.data_label.config(text="🔓 Click-Through OFF\n(Shift+F10 to toggle)")
                print("   🔓 Click-through disabled (draggable)")
            except Exception as e:
                print(f"Toggle failed: {e}")
        else:
            # Enable click-through
            try:
                GWL_EXSTYLE = -20
                WS_EX_TRANSPARENT = 0x00000020
                
                user32 = ctypes.windll.user32
                current_style = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
                new_style = current_style | WS_EX_TRANSPARENT  # Add WS_EX_TRANSPARENT back
                user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, new_style)
                
                self.click_through_active = True
                self.title_label.config(fg="#00ff88")  # Green = click-through mode
                self.data_label.config(text="✅ Click-Through ON\n(Shift+F10 to toggle)")
                print("   ✅ Click-through enabled (transparent to clicks)")
                # Restore normal display after short delay
                self.root.after(1000, lambda: self._restore_normal_display())
            except Exception as e:
                print(f"Toggle failed: {e}")
    
    def _restore_normal_display(self):
        """Restore normal overlay display after toggle message"""
        # Will be overwritten by next file poll anyway
        pass
    
    def _start_drag(self, event):
        """Start drag operation"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def _on_drag(self, event):
        """Handle drag motion"""
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        x = self.root.winfo_x() + delta_x
        y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{x}+{y}")
    
    def check_file(self):
        """Poll overlay state file for changes"""
        try:
            if not os.path.exists(self.state_file):
                self.data_label.config(
                    text="Waiting for tracker...\n\n(overlay_state.json not found)",
                    fg="#888888"
                )
            else:
                mtime = os.path.getmtime(self.state_file)
                if mtime > self.last_mtime:
                    self.last_mtime = mtime
                    with open(self.state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    self.update_display(state)
        
        except json.JSONDecodeError as e:
            self.data_label.config(
                text=f"⚠️  JSON Parse Error\n\n{str(e)[:100]}",
                fg="#ff6666"
            )
        except Exception as e:
            self.data_label.config(
                text=f"⚠️  Error\n\n{str(e)[:100]}",
                fg="#ff6666"
            )
        
        # Reschedule next check (THIS WORKS - same thread!)
        self.root.after(self.poll_interval_ms, self.check_file)
    
    def update_display(self, state: dict):
        """
        Update overlay display with state data using template system
        
        Args:
            state: Parsed overlay_state.json content
        """
        phase = state.get("current_phase", "unknown")
        phase_name = state.get("phase_display_name", "Unknown Phase")
        color = state.get("phase_color", "#00ff88")
        template_vars = state.get("template_variables", {})
        
        # Use template system to build display text
        display_text = get_template_for_phase(phase, phase_name, template_vars)
        
        # Update label
        self.data_label.config(text=display_text, fg=color)
    
    def run(self):
        """Start Tkinter mainloop"""
        self.root.mainloop()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="KISS Overlay - Standalone (Win32 Always-on-Top, Click-Through)"
    )
    parser.add_argument("--state-file", default="../kiss_overlay_state.json", 
                       help="Path to overlay state JSON file (relative to kiss_overlay/)")
    parser.add_argument("--poll-interval", type=int, default=500,
                       help="File polling interval in milliseconds")
    
    args = parser.parse_args()
    
    overlay = KISSOverlayStandalone(
        state_file=args.state_file,
        poll_interval_ms=args.poll_interval
    )
    
    print("🔍 KISS Overlay (Standalone) started")
    print(f"   State file: {args.state_file}")
    print(f"   Poll interval: {args.poll_interval}ms")
    print("\n   🎮 Hotkeys:")
    print("      F10         → Toggle visibility (show/hide)")
    print("      Shift+F10   → Toggle click-through (green/orange)")
    print("\n   🎨 Title Colors:")
    print("      🟢 Green    → Click-through ON (clicks pass through)")
    print("      🟠 Orange   → Click-through OFF (draggable)")
    print("\n   💾 Position saved on exit → kiss_overlay_position.json")
    print("   ❌ Close window or Ctrl+C to exit\n")
    
    try:
        overlay.run()
    except KeyboardInterrupt:
        print("\n✅ KISS Overlay closed cleanly")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
