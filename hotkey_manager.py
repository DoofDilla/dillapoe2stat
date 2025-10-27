"""
Hotkey Manager for PoE Stats Tracker
Handles global hotkey registration and waiting for user input
"""

import platform
import sys

# Conditional import for keyboard library
if platform.system() == "Windows":
    import keyboard
    HOTKEYS_ENABLED = True
else:
    HOTKEYS_ENABLED = False
    keyboard = None  # Placeholder


class HotkeyManager:
    """Manages hotkey registration and input waiting"""

    def __init__(self, tracker=None):
        self.callbacks = {}
        self.registered_hotkeys = []
        self.tracker = tracker  # Reference to the tracker for callback execution
        self.is_linux = platform.system() != "Windows"

        if self.is_linux:
            print("ℹ️ Hotkeys disabled on Linux (non-privileged mode); use console commands")

    def register_hotkey(self, hotkey, callback):
        """Register a hotkey with callback function"""
        # Always store the callback for console mode
        self.callbacks[hotkey] = callback

        if not HOTKEYS_ENABLED:
            print(f"ℹ️ Hotkey '{hotkey}' skipped (not supported on this platform)")
            return False

        try:
            keyboard.add_hotkey(hotkey, callback)
            self.registered_hotkeys.append(hotkey)
            print(f"✅ Registered hotkey: {hotkey}")
            return True
        except Exception as e:
            print(f"❌ Failed to register hotkey {hotkey}: {e}")
            return False

    def setup_default_hotkeys(self, tracker):
        """Set up default hotkeys for the tracker"""
        self.tracker = tracker  # Set tracker reference

        hotkeys = {
            'f2': lambda: tracker.take_pre_snapshot(),  # Start map tracking (pre-map snapshot)
            'f3': lambda: tracker.take_post_snapshot(),  # End map tracking (post-map)
            'ctrl+f6': lambda: tracker.toggle_auto_mode(),  # Toggle auto-detection
            'f5': lambda: tracker.check_current_inventory_value(),  # Check inventory value
            'f7': lambda: tracker.display_session_stats(),  # Session dashboard
            'ctrl+f2': lambda: tracker.take_experimental_pre_snapshot(),  # Analyze waystone
            'f4': lambda: tracker.toggle_debug_mode(),  # Toggle debug mode
            'f6': lambda: tracker.start_new_session(),  # End current session and start new one
            'f8': lambda: tracker.toggle_output_mode(),  # Switch output modes
            'f9': lambda: tracker.toggle_obs_server(),  # Toggle OBS overlay server
            'ctrl+shift+f2': lambda: tracker.simulate_pre_snapshot(),  # Simulate pre-snapshot
            'ctrl+shift+f3': lambda: tracker.simulate_post_snapshot(),  # Simulate post-snapshot
        }

        success_count = 0
        for hotkey, callback in hotkeys.items():
            if self.register_hotkey(hotkey, callback):
                success_count += 1

        if success_count != len(hotkeys):
            print("Warning: Some hotkeys failed to register")

        return success_count == len(hotkeys)

    def unregister_all(self):
        """Unregister all hotkeys"""
        if HOTKEYS_ENABLED:
            for hotkey in self.registered_hotkeys:
                try:
                    keyboard.remove_hotkey(hotkey)
                except:
                    pass
            self.registered_hotkeys.clear()

    def wait_for_exit_key(self, exit_key='ctrl+esc'):
        """Wait for exit key or console command"""
        if HOTKEYS_ENABLED and not self.is_linux:
            # Use keyboard library on Windows
            keyboard.wait(exit_key)
        else:
            # Console-based waiting on Linux: Poll for commands
            print("\nℹ️ Linux Mode: Enter commands (e.g., 'f2' or 'debug') or 'exit' to quit.")
            print("Type 'help' for full list.\n")

            while True:
                try:
                    user_input = input("Command: ").strip().lower()
                    if user_input == 'exit':
                        break
                    elif user_input == 'help':
                        self._print_help()
                        continue

                    # Map command to callback (aliases for ease of use)
                    command_map = {
                        # Primary aliases (easy to remember)
                        'start': 'f2',  # Start map tracking
                        'end': 'f3',  # End map tracking
                        'auto': 'ctrl+f6',  # Toggle auto-detection
                        'inventory': 'f5',  # Check inventory value
                        'stats': 'f7',  # Session dashboard
                        'waystone': 'ctrl+f2',  # Analyze waystone
                        'debug': 'f4',  # Toggle debug mode
                        'restart': 'f6',  # Restart session
                        'output': 'f8',  # Toggle output mode
                        'obs': 'f9',  # Toggle OBS
                        'simpre': 'ctrl+shift+f2',  # Simulate pre
                        'simpost': 'ctrl+shift+f3',  # Simulate post

                        # Fallback to direct hotkey strings
                        'f2': 'f2',
                        'f3': 'f3',
                        'ctrl+f6': 'ctrl+f6',
                        'f5': 'f5',
                        'f7': 'f7',
                        'ctrl+f2': 'ctrl+f2',
                        'f4': 'f4',
                        'f6': 'f6',
                        'f8': 'f8',
                        'f9': 'f9',
                        'ctrl+shift+f2': 'ctrl+shift+f2',
                        'ctrl+shift+f3': 'ctrl+shift+f3',
                    }

                    hotkey = command_map.get(user_input)
                    if hotkey and hotkey in self.callbacks:
                        print(f"Executing: {hotkey}")
                        self.callbacks[hotkey]()  # Trigger the callback
                    else:
                        print(f"ℹ️ Unknown command '{user_input}'. Type 'help' for options.")

                except (EOFError, KeyboardInterrupt):
                    print("\nExiting...")
                    break

        print("Exiting...")

    def _print_help(self):
        """Print available console commands"""
        help_text = """
Commands (use aliases for simplicity or full hotkey strings):
- start (or f2): Start map tracking (pre-map snapshot)
- end (or f3): End map tracking (post-map snapshot)
- auto (or ctrl+f6): Toggle auto-detection
- inventory (or f5): Check current inventory value
- stats (or f7): Display session stats (dashboard)
- waystone (or ctrl+f2): Analyze waystone (experimental)
- debug (or f4): Toggle debug mode
- restart (or f6): End current session and start new one
- output (or f8): Toggle output mode (normal/comprehensive)
- obs (or f9): Toggle OBS overlay server
- simpre (or ctrl+shift+f2): Simulate pre-snapshot
- simpost (or ctrl+shift+f3): Simulate post-snapshot
- exit: Quit the application
- help: Show this help
        """
        print(help_text)
