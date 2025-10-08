# kiss_overlay_standalone.py
"""
KISS Overlay - Standalone File-Polling Version
Reads overlay_state.json every 500ms, displays phase + key metrics
"""

import tkinter as tk
from tkinter import font as tkfont
import json
import os
import sys


# Import template builder
try:
    from kiss_overlay_templates import get_template_for_phase
except ImportError:
    # Fallback if running standalone without template module
    def get_template_for_phase(phase, phase_name, template_vars):
        return f"Phase: {phase_name}\n\nTemplate module not found."


class KISSOverlayStandalone:
    def __init__(self, state_file="overlay_state.json", poll_interval_ms=500):
        self.state_file = state_file
        self.poll_interval_ms = poll_interval_ms
        self.last_mtime = 0
        
        # Tkinter window setup
        self.root = tk.Tk()
        self.root.title("PoE Stats Overlay")
        self.root.overrideredirect(True)  # No window frame
        self.root.wm_attributes("-topmost", True)  # Always on top
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.wm_attributes("-alpha", 0.75)
        
        # Window geometry (from config or defaults)
        width, height = 400, 250  # Slightly taller for more content
        x, y = 50, 50
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
        
        # Start file polling
        self.check_file()
    
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
    
    parser = argparse.ArgumentParser(description="KISS Overlay - Standalone")
    parser.add_argument("--state-file", default="overlay_state.json", 
                       help="Path to overlay state JSON file")
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
    print("   - Drag with left mouse to move")
    print("   - Close window to exit")
    
    try:
        overlay.run()
    except KeyboardInterrupt:
        print("\n✅ KISS Overlay closed cleanly")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
