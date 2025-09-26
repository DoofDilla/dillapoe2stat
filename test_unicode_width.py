#!/usr/bin/env python3
"""
Test Unicode display widths
"""

def get_unicode_display_width(char):
    """Get actual terminal display width of a single Unicode character"""
    code = ord(char)
    
    # Emoji ranges (typically 2 columns wide)
    if (0x1F600 <= code <= 0x1F64F or  # Emoticons
        0x1F300 <= code <= 0x1F5FF or  # Misc Symbols
        0x1F680 <= code <= 0x1F6FF or  # Transport
        0x1F1E0 <= code <= 0x1F1FF or  # Flags
        0x2600 <= code <= 0x26FF or    # Misc symbols
        0x2700 <= code <= 0x27BF):     # Dingbats
        return 2
        
    # Special Unicode symbols (1 column wide)
    elif (0x2000 <= code <= 0x2BFF or  # General punctuation, symbols
          0x25A0 <= code <= 0x25FF or  # Geometric shapes (⬛, ▲, ◇, etc.)
          0x2600 <= code <= 0x26FF):   # Misc symbols
        return 1
        
    # ASCII and most other characters
    else:
        return 1

def get_text_display_width(text):
    """Calculate actual terminal display width of text"""
    return sum(get_unicode_display_width(char) for char in text)

# Test our icons
icons = ['▲', '🔸', '◇', '⬛', '💎']

for icon in icons:
    width = get_text_display_width(icon)
    code = ord(icon)
    print(f"'{icon}' (U+{code:04X}) -> width: {width}")