"""
Color Analysis System for PoE Icons
Analyzes dominant colors from item icons and maps them to emojis

==== HOW TO ADD/EDIT ITEM EMOJIS ====

To customize emojis for specific items:
1. Find the IconColorMapper class (around line 209)
2. Edit the self.item_emoji_map dictionary
3. Add/modify entries like: 'item name': 'emoji'

Examples:
- Specific items: 'chaos orb': '🟡'
- Generic types: 'catalyst': '🔬'

Priority order: Specific item names > Generic types > Equipment categories > Color analysis
"""

import os
from pathlib import Path
from PIL import Image, ImageStat
import colorsys
from collections import Counter


class ColorAnalyzer:
    """Analyzes colors from item icons"""
    
    def __init__(self):
        # Color name mappings for debugging
        self.color_names = {
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'orange': (255, 165, 0),
            'purple': (128, 0, 128),
            'brown': (139, 69, 19),
            'gold': (255, 215, 0),
            'silver': (192, 192, 192),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'gray': (128, 128, 128)
        }
    
    def get_dominant_color(self, image_path):
        """
        Get the dominant color from an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            tuple: (r, g, b) dominant color or None if failed
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize for faster processing
                img = img.resize((50, 50))
                
                # Get all colors and count them
                colors = img.getcolors(maxcolors=256*256*256)
                if not colors:
                    return None
                
                # Sort by frequency and get most common
                colors.sort(key=lambda x: x[0], reverse=True)
                
                # Skip background colors (very dark or very bright)
                for count, color in colors:
                    r, g, b = color
                    brightness = r + g + b
                    
                    # Skip if too dark (likely shadow/background)
                    if brightness < 50:
                        continue
                        
                    # Skip if too bright/white (likely transparent background)
                    if brightness > 600:  # Very bright whites
                        continue
                        
                    # Skip if very close to white/gray
                    if r > 200 and g > 200 and b > 200:
                        continue
                        
                    return color
                
                # Fallback to most common color
                return colors[0][1] if colors else None
                
        except Exception as e:
            print(f"[COLOR] Error analyzing {image_path}: {e}")
            return None
    
    def get_average_color(self, image_path):
        """
        Get average color from image (alternative method)
        
        Args:
            image_path: Path to the image file
            
        Returns:
            tuple: (r, g, b) average color or None if failed
        """
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Get average color using ImageStat
                stat = ImageStat.Stat(img)
                avg_color = stat.mean
                return tuple(int(c) for c in avg_color)
                
        except Exception as e:
            print(f"[COLOR] Error getting average color from {image_path}: {e}")
            return None
    
    def color_to_hsl(self, rgb_color):
        """Convert RGB to HSL for better color categorization"""
        if not rgb_color:
            return None
        
        r, g, b = [c/255.0 for c in rgb_color]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (int(h*360), int(s*100), int(l*100))
    
    def categorize_color(self, rgb_color):
        """
        Categorize an RGB color into a general color category
        
        Args:
            rgb_color: (r, g, b) tuple
            
        Returns:
            str: Color category name
        """
        if not rgb_color:
            return 'unknown'
        
        r, g, b = rgb_color
        
        # Convert to HSL for better categorization
        hsl = self.color_to_hsl(rgb_color)
        if not hsl:
            return 'unknown'
        
        h, s, l = hsl
        
        # Very dark colors
        if l < 20:
            return 'black'
        
        # Very light colors
        if l > 80 and s < 20:
            return 'white'
        
        # Gray colors (low saturation)
        if s < 20:
            if l > 60:
                return 'silver'
            elif l > 30:
                return 'gray'
            else:
                return 'black'
        
        # Colorful colors (high saturation)
        if h < 15 or h > 345:
            return 'red'
        elif h < 45:
            if l > 50:
                return 'orange'
            else:
                return 'brown'
        elif h < 75:
            return 'yellow' if l > 40 else 'gold'
        elif h < 150:
            return 'green'
        elif h < 210:
            return 'cyan'
        elif h < 270:
            return 'blue'
        elif h < 330:
            return 'purple'
        else:
            return 'red'
    
    def analyze_icon_palette(self, image_path, num_colors=5):
        """
        Analyze the color palette of an icon
        
        Args:
            image_path: Path to the image file
            num_colors: Number of dominant colors to extract
            
        Returns:
            list: List of (color, category, percentage) tuples
        """
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize for faster processing
                img = img.resize((32, 32))
                
                # Get all pixels
                pixels = list(img.getdata())
                
                # Count colors
                color_counts = Counter(pixels)
                total_pixels = len(pixels)
                
                # Get top colors
                top_colors = color_counts.most_common(num_colors)
                
                results = []
                for color, count in top_colors:
                    percentage = (count / total_pixels) * 100
                    category = self.categorize_color(color)
                    results.append((color, category, percentage))
                
                return results
                
        except Exception as e:
            print(f"[COLOR] Error analyzing palette for {image_path}: {e}")
            return []


class IconColorMapper:
    """Maps analyzed colors to appropriate emojis"""
    
    def __init__(self):
        # ===== EDITABLE ITEM-EMOJI MAPPING TABLE =====
        # Priority: Specific items > Item types > Color analysis
        # To add new items: Add entry to item_emoji_map below
        self.item_emoji_map = {
            # === CURRENCY ITEMS ===
            'chaos orb': '🟡',
            'exalted orb': '🟠', 
            'greater exalted orb': '🟠',
            'divine orb': '⭐',
            'regal orb': '🟤',
            'greater regal orb': '🟤',
            'perfect orb of augmentation': '🔵',
            'orb of annulment': '⚪',
            'vaal orb': '🟠',
            'gemcutter\'s prism': '💎',
            'glassblower\'s bauble': '⚪',
            'armourer\'s scrap': '⚫',
            'scroll of wisdom': '🟤',
            
            # === CATALYSTS ===
            'chayula\'s catalyst': '🔬',
            'esh\'s catalyst': '🔬',
            'tul\'s catalyst': '🔬',
            'sibilant catalyst': '🔬',
            
            # === SPLINTERS ===
            'breach splinter': '🌟',  # Glowing star for splinters
            'simulacrum splinter': '🌟',  # Glowing star for splinters
            
            # === RUNES ===
            'greater desert rune': '🔵',
            'greater storm rune': '🔵',
            'greater vision rune': '🔵',
            'greater rebirth rune': '🔵',
            'farrul\'s rune of the hunt': '🟣',  # Special purple for unique runes
            'perfect desert rune': '🟨',
            'perfect vision rune': '🟨',
            
            # === ESSENCES ===
            'greater essence of opulence': '✨',
            'greater essence of alacrity': '✨',
            'perfect essence of command': '✨',
            'perfect essence of the infinite': '✨',
            
            # === DELIRIUM ===
            # 'diluted liquid guilt': '⚫',  # Removed for color analysis
            'diluted liquid greed': '⚫',
            'liquid despair': '🔵',
            
            # === RITUAL ===
            # 'omen of amelioration': '⬜',  # Entfernt für Farbanalyse
            
            # === FRAGMENTS ===
            'ancient crisis fragment': '🧩',
            
            # === WAYSTONES ===
            'waystone': '🏰',  # Castle for waystones (better padding)
            
            # === TABLETS ===
            'tablet': '📜',  # Scroll for all tablets
            'precursor tablet': '📜',  # Scroll for precursor tablets
            
            # === GEMS (MATERIALS) ===
            'sapphire': '🔷',  # Blue diamond for sapphire
            'emerald': '🔶',  # Green diamond for emerald
            'ruby': '🔴',     # Red circle for ruby (if needed)
            
            # === GENERIC TYPE FALLBACKS ===
            # These are used if specific item name not found above
            'catalyst': '🔬',  # Default for any catalyst
            'splinter': '🌟',  # Default for any splinter (glowing star)
            'orb': '🟡',      # Default for any orb
            # 'rune': '🔵',     # Removed for color analysis
            'essence': '✨',   # Default for any essence
            'fragment': '🧩', # Default for any fragment
            'gem': '💎',      # Default for any gem
        }
        
        # Color-based emoji mappings (used when no specific item/type match found)
        # Currency items get circles, non-currency get squares
        self.color_emoji_map = {
            'red': '🔴',
            'green': '🟢', 
            'blue': '🔵',
            'yellow': '🟡',
            'orange': '🟠',
            'purple': '🟣',
            'brown': '🟤',
            'gold': '🟨',
            'silver': '⚪',
            'white': '⚪',
            'black': '⚫',
            'gray': '⚫',
            'cyan': '🔵',
            'unknown': '⚪'
        }
        
        # Square variants for non-currency items
        self.color_square_map = {
            'red': '🟥',
            'green': '🟩', 
            'blue': '🟦',
            'yellow': '🟨',
            'orange': '🟧',
            'purple': '🟦',  # Use blue square for purple
            'brown': '🟤',  # Use brown circle as fallback
            'gold': '🟨',
            'silver': '⬜',
            'white': '⬜',
            'black': '⬛',
            'gray': '⬛',
            'cyan': '🟦',
            'unknown': '⬜'
        }
    
    def get_emoji_for_color(self, color_category, item_data=None):
        """Get emoji for a color category - circles for currency, squares for others"""
        # Check if it's a currency item
        if item_data:
            type_line = (item_data.get('typeLine') or '').lower()
            icon_url = item_data.get('icon', '')
            
            # Simple currency check - only real currency items
            currency_keywords = ['orb', 'currency']
            is_currency = any(keyword in type_line for keyword in currency_keywords) or 'currency' in icon_url.lower()
            
            if not is_currency:
                # Use squares for non-currency
                return self.color_square_map.get(color_category, '⬜')
        
        # Use circles for currency (default)
        return self.color_emoji_map.get(color_category, '⚪')
    
    def get_emoji_for_item(self, item_data, dominant_color_category=None):
        """
        Get the best emoji for an item using the editable mapping table
        
        Priority order:
        1. Specific item name match (e.g., 'chaos orb')
        2. Generic type match (e.g., 'catalyst', 'orb')
        3. Equipment category (weapons, armor, accessories)
        4. Color analysis
        5. Default fallback
        
        Args:
            item_data: Item data dict from API
            dominant_color_category: Analyzed dominant color category
            
        Returns:
            str: Best emoji for the item
        """
        # Get item info
        type_line = (item_data.get('typeLine') or '').lower()
        base_type = (item_data.get('baseType') or '').lower()
        icon_url = item_data.get('icon', '')
        
        # 1. Try exact item name match first
        if type_line in self.item_emoji_map:
            return self.item_emoji_map[type_line]
        
        # 2. Try generic type matches
        for item_type, emoji in self.item_emoji_map.items():
            if item_type in type_line:
                return emoji
        
        # 3. Equipment category fallbacks (not in mapping table)
        if any(weapon in type_line for weapon in ['sword', 'axe', 'mace', 'bow', 'staff', 'wand', 'dagger', 'claw']):
            return '⚔️'
        elif any(armor in type_line for armor in ['helmet', 'chest', 'gloves', 'boots', 'shield']):
            return '🛡️'
        elif any(acc in type_line for acc in ['ring', 'amulet', 'belt']):
            return '💍'
        elif 'gem' in type_line or 'skill' in icon_url:
            return '💎'
        elif 'flask' in type_line:
            return '🧪'
        elif 'map' in type_line or 'waystone' in type_line:
            return '🗺️'
        
        # 4. Color-based fallback
        if dominant_color_category:
            return self.get_emoji_for_color(dominant_color_category, item_data)
        
        # 5. Ultimate fallback
        return '⚪'


# Global instances
_color_analyzer = None
_color_mapper = None

def get_color_analyzer():
    """Get the global color analyzer instance"""
    global _color_analyzer
    if _color_analyzer is None:
        _color_analyzer = ColorAnalyzer()
    return _color_analyzer

def get_icon_color_mapper():
    """Get the global icon color mapper instance"""
    global _color_mapper
    if _color_mapper is None:
        _color_mapper = IconColorMapper()
    return _color_mapper