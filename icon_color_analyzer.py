"""
Color Analysis System for PoE Icons
Analyzes dominant colors from item icons and maps them to emojis
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
                
                # Skip very dark/black colors that might be background
                for count, color in colors:
                    r, g, b = color
                    # Skip if too dark (likely background/shadow)
                    if r + g + b > 50:  # Brightness threshold
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
    
    def detect_item_shape(self, item_data):
        """
        Detect item shape based on name/type (no image analysis needed!)
        
        Args:
            item_data: Item data dict from API
            
        Returns:
            str: Shape category
        """
        type_line = (item_data.get('typeLine') or '').lower()
        base_type = (item_data.get('baseType') or '').lower()
        
        # We KNOW what PoE items look like - no analysis needed!
        if 'chaos' in type_line:
            return 'hexagon'  # Chaos Orb is hexagonal
        elif 'exalted' in type_line:
            return 'diamond'  # Exalted Orb is diamond-shaped
        elif 'divine' in type_line:
            return 'ornate'   # Divine Orb is ornate/star-like
        elif 'mirror' in type_line:
            return 'circle'   # Mirror is circular
        elif any(weapon in type_line for weapon in ['sword', 'axe', 'mace', 'bow', 'staff', 'wand', 'dagger', 'claw']):
            return 'weapon'
        elif any(armor in type_line for armor in ['helmet', 'chest', 'gloves', 'boots']):
            return 'shield'
        elif 'shield' in type_line:
            return 'shield'
        elif any(gem in type_line for gem in ['gem', 'skill']):
            return 'diamond'  # Gems are diamond-shaped
        elif 'essence' in type_line:
            return 'star'     # Essences are star-like
        elif 'fragment' in type_line or 'reliquary key' in type_line:
            return 'triangle' # Fragments and keys are triangular
        elif 'scroll of wisdom' in type_line:
            return 'triangle' # Scrolls are triangular
        elif 'tablet' in type_line:
            return 'square'   # Tablets are square-ish  
        elif 'omen' in type_line:
            return 'diamond'  # Omens are diamond-shaped
        elif 'waystone' in type_line or 'map' in type_line:
            return 'square'   # Maps are square-ish
        elif 'orb' in type_line:
            return 'circle'   # Default orbs are circular
        else:
            return 'circle'   # Default fallback
    
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
        # Emoji mappings based on color categories and item types
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
        
        # Special item type overrides
        self.item_type_emojis = {
            'currency': {
                'chaos': '🟡',
                'exalted': '🟠', 
                'divine': '🟨',
                'orb': '⚪'
            },
            'weapon': '⚔️',
            'armor': '🛡️',
            'accessory': '💍',
            'gem': '💎',
            'flask': '🧪',
            'map': '🗺️',
            'fragment': '🧩',
            'essence': '✨',
            'catalyst': '⚡'
        }
        
        # Smart Unicode Map - VERSCHIEDENE FORMEN + ECHTE FARBEN!
        self.smart_unicode_map = {
            # Circular shapes (like most orbs)
            'circle': {'gold': '🟡', 'orange': '🟠', 'red': '🔴', 'blue': '🔵', 'green': '🟢', 'white': '⚪', 'black': '⚫', 'brown': '🟤', 'gray': '⚫', 'silver': '⚪', 'default': '🟡'},
            
            # Hexagonal shapes (like Chaos Orb) - ECHTE HEXAGONS!
            'hexagon': {'gold': '🟨', 'yellow': '🟨', 'orange': '🟧', 'white': '⬜', 'black': '⬛', 'brown': '🟫', 'gray': '⬛', 'silver': '⬜', 'default': '🟨'},
            
            # Diamond/Crystal shapes (like Exalted Orb) - ECHTE DIAMONDS!
            'diamond': {'gold': '�', 'orange': '�', 'white': '⬜', 'blue': '�', 'black': '⬛', 'brown': '🟫', 'gray': '⬛', 'silver': '⬜', 'default': '�'},
            
            # Complex/Ornate shapes (like Divine Orb) - Stars für ornate!
            'ornate': {'gold': '⭐', 'yellow': '🌟', 'white': '✨', 'black': '⬛', 'brown': '🟫', 'gray': '⬛', 'silver': '✨', 'default': '⭐'},
            
            # Square/Rectangular shapes (like maps)
            'square': {'brown': '🟫', 'yellow': '🟨', 'white': '⬜', 'blue': '🟦', 'black': '⬛', 'gold': '🟨', 'orange': '🟧', 'gray': '⬛', 'silver': '⬜', 'default': '⬛'},
            
            # Triangular shapes (like fragments) - ECHTE TRIANGLES!
            'triangle': {'red': '🔺', 'blue': '🔷', 'orange': '🔸', 'white': '⬜', 'black': '⬛', 'brown': '🟫', 'gold': '🟨', 'gray': '⬛', 'silver': '⬜', 'default': '🔸'},
            
            # Star shapes (like essences) - ECHTE STARS!
            'star': {'gold': '⭐', 'yellow': '🌟', 'white': '✨', 'blue': '�', 'black': '⬛', 'brown': '🟫', 'gray': '⬛', 'silver': '✨', 'default': '⭐'}
        }
    
    def get_emoji_for_color(self, color_category):
        """Get emoji for a color category"""
        return self.color_emoji_map.get(color_category, '⚪')
    
    def get_smart_unicode_for_item(self, item_data, color_analyzer, color_category=None):
        """ENTFERNT - Zurück zum einfachen System"""
        # Einfach die alte get_emoji_for_item Methode verwenden
        return self.get_emoji_for_item(item_data, color_category)
    
    def _guess_color_from_name(self, item_data):
        """Guess color from item name (for items without cached color analysis)"""
        type_line = (item_data.get('typeLine') or '').lower()
        
        if 'chaos' in type_line:
            return 'gold'
        elif 'exalted' in type_line:
            return 'orange'
        elif 'divine' in type_line:
            return 'gold'
        elif 'mirror' in type_line:
            return 'silver'
        elif any(word in type_line for word in ['rusty', 'copper', 'bronze']):
            return 'brown'
        elif any(word in type_line for word in ['iron', 'steel']):
            return 'silver'
        elif any(word in type_line for word in ['gold', 'golden']):
            return 'gold'
        elif any(word in type_line for word in ['blue', 'sapphire', 'azure']):
            return 'blue'  
        elif any(word in type_line for word in ['red', 'ruby', 'crimson']):
            return 'red'
        elif any(word in type_line for word in ['green', 'emerald']):
            return 'green'
        else:
            return 'gold'  # Default PoE color
    
    def get_emoji_for_item(self, item_data, dominant_color_category=None):
        """
        Get the best emoji for an item based on type and color
        
        Args:
            item_data: Item data dict from API
            dominant_color_category: Analyzed dominant color category
            
        Returns:
            str: Best emoji for the item
        """
        # Get item type info
        type_line = (item_data.get('typeLine') or '').lower()
        base_type = (item_data.get('baseType') or '').lower()
        icon_url = item_data.get('icon', '')
        
        # Special handling for currency
        if 'orb' in type_line or 'currency' in icon_url:
            if 'chaos' in type_line:
                return '🟡'  # Gold/yellow for chaos orbs
            elif 'exalted' in type_line:
                return '🟠'  # Orange for exalted orbs
            elif 'divine' in type_line:
                return '🟨'  # Bright yellow for divine orbs
            else:
                return self.get_emoji_for_color(dominant_color_category) if dominant_color_category else '⚪'
        
        # Special handling for other item types
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
        elif 'fragment' in type_line:
            return '🧩'
        elif 'essence' in type_line:
            return '✨'
        elif 'catalyst' in type_line:
            return '⚡'
        
        # Fallback to color-based emoji
        if dominant_color_category:
            return self.get_emoji_for_color(dominant_color_category)
        
        # Ultimate fallback
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