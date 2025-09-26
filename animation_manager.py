"""
Animation Manager for PoE Stats Tracker
Provides terminal animations like spinners and progress indicators
"""

import threading
import time
import sys


class AnimationManager:
    """Handles terminal animations and loading indicators"""
    
    def __init__(self):
        self.animation_thread = None
        self.stop_animation = False
        
        # Animation styles
        self.spinners = {
            'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'bars': ['|', '/', '-', '\\'],
            'arrows': ['→', '↘', '↓', '↙', '←', '↖', '↑', '↗'],
            'orbs': ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'],
            'poe': ['💰', '⚡', '🔮', '💎'],
            'simple': ['.', '..', '...']
        }
    
    def start_spinner(self, message="Loading", style='dots', delay=0.15):
        """Start a spinner animation with custom message and style"""
        if self.animation_thread and self.animation_thread.is_alive():
            self.stop_spinner()
        
        self.stop_animation = False
        self.animation_thread = threading.Thread(
            target=self._spinner_worker, 
            args=(message, style, delay)
        )
        self.animation_thread.daemon = True
        self.animation_thread.start()
    
    def stop_spinner(self, completion_message=None):
        """Stop the spinner animation"""
        self.stop_animation = True
        if self.animation_thread:
            self.animation_thread.join(timeout=0.5)
        
        # Clear the spinner line, reset cursor immediately, and show completion message
        self._clear_line()
        # Force cursor reset immediately to prevent issues with subsequent output
        sys.stdout.write('\033[?25h\033[2 q')
        sys.stdout.flush()
        if completion_message:
            print(completion_message)
    
    def _spinner_worker(self, message, style, delay):
        """Worker thread for spinner animation"""
        spinner_chars = self.spinners.get(style, self.spinners['dots'])
        i = 0
        
        # Hide cursor (more compatible version)
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()
        
        try:
            while not self.stop_animation:
                char = spinner_chars[i % len(spinner_chars)]
                # Move to beginning of line, clear it, and write new content
                sys.stdout.write(f'\r{char} {message}')
                sys.stdout.flush()
                
                time.sleep(delay)
                i += 1
        finally:
            # Show cursor again and reset to block cursor
            sys.stdout.write('\033[?25h\033[2 q')
            sys.stdout.flush()
    
    def _clear_line(self):
        """Clear the current line"""
        sys.stdout.write('\r\033[K')
        sys.stdout.flush()
    
    def show_progress_dots(self, message, duration=2.0, dot_count=3):
        """Show animated dots building up"""
        if self.animation_thread and self.animation_thread.is_alive():
            self.stop_spinner()
        
        self.stop_animation = False
        self.animation_thread = threading.Thread(
            target=self._progress_dots_worker,
            args=(message, duration, dot_count)
        )
        self.animation_thread.daemon = True
        self.animation_thread.start()
    
    def _progress_dots_worker(self, message, duration, dot_count):
        """Worker for progress dots animation"""
        step_duration = duration / (dot_count + 1)
        
        # Hide cursor
        sys.stdout.write('\033[?25l')
        
        try:
            for i in range(dot_count + 1):
                if self.stop_animation:
                    break
                
                dots = '.' * i
                sys.stdout.write(f'\r{message}{dots}')
                sys.stdout.flush()
                time.sleep(step_duration)
        finally:
            # Show cursor again and reset to block cursor
            sys.stdout.write('\033[?25h\033[2 q')
            sys.stdout.flush()
    
    def context_spinner(self, message="Loading", style='dots', delay=0.15):
        """Context manager for spinner animation"""
        return SpinnerContext(self, message, style, delay)


class SpinnerContext:
    """Context manager for automatic spinner start/stop"""
    
    def __init__(self, animation_manager, message, style, delay):
        self.animation_manager = animation_manager
        self.message = message
        self.style = style
        self.delay = delay
    
    def __enter__(self):
        self.animation_manager.start_spinner(self.message, self.style, self.delay)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.animation_manager.stop_spinner()
        else:
            self.animation_manager.stop_spinner("❌ Error occurred")