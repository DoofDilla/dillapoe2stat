"""
Terminal Icon Display POC - Proof of Concept
Testing different methods to display actual icons in terminal
Separate from main script for experimentation
"""

import os
import sys
from pathlib import Path
import requests
from PIL import Image
import io
import subprocess
import platform


class TerminalIconTester:
    """Test different methods to display icons in terminal"""
    
    def __init__(self):
        self.test_dir = Path("terminal_icon_test")
        self.test_dir.mkdir(exist_ok=True)
        
        # Test image URLs from PoE
        self.test_images = {
            "Chaos Orb": "https://web.poecdn.com/image/Art/2DItems/Currency/CurrencyRerollRare.png",
            "Exalted Orb": "https://web.poecdn.com/image/Art/2DItems/Currency/CurrencyAddModToRare.png",
            "Divine Orb": "https://web.poecdn.com/image/Art/2DItems/Currency/CurrencyModValues.png",
            "Mirror": "https://web.poecdn.com/image/Art/2DItems/Currency/CurrencyDuplicate.png"
        }
        
    def download_test_image(self, name, url):
        """Download a test image"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            file_path = self.test_dir / f"{name.replace(' ', '_').lower()}.png"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded: {name}")
            return file_path
        except Exception as e:
            print(f"❌ Failed to download {name}: {e}")
            return None
    
    def download_all_test_images(self):
        """Download all test images"""
        print("📥 Downloading test images...")
        downloaded = {}
        
        for name, url in self.test_images.items():
            file_path = self.download_test_image(name, url)
            if file_path:
                downloaded[name] = file_path
        
        print(f"📁 Images saved to: {self.test_dir.absolute()}")
        return downloaded
    
    def check_terminal_capabilities(self):
        """Check what the current terminal supports"""
        print("\n🔍 TERMINAL CAPABILITY CHECK")
        print("=" * 50)
        
        # Basic info
        print(f"Platform: {platform.system()}")
        print(f"Terminal: {os.environ.get('TERM', 'Unknown')}")
        print(f"Terminal Program: {os.environ.get('TERM_PROGRAM', 'Unknown')}")
        
        # Check for specific terminal features
        capabilities = {
            "Sixel Support": self._check_sixel_support(),
            "Kitty Graphics": self._check_kitty_graphics(),
            "iTerm2 Images": self._check_iterm2_support(),
            "True Color": self._check_truecolor_support(),
            "Unicode Support": self._check_unicode_support()
        }
        
        print("\n📊 Capabilities:")
        for feature, supported in capabilities.items():
            status = "✅" if supported else "❌"
            print(f"  {status} {feature}")
        
        return capabilities
    
    def _check_sixel_support(self):
        """Check if terminal supports Sixel graphics"""
        # Simple heuristic - not 100% accurate but good enough for testing
        term = os.environ.get('TERM', '').lower()
        term_program = os.environ.get('TERM_PROGRAM', '').lower()
        
        return ('xterm' in term or 'mlterm' in term or 
                'mintty' in term_program or 'wezterm' in term_program)
    
    def _check_kitty_graphics(self):
        """Check if terminal supports Kitty graphics protocol"""
        return os.environ.get('TERM') == 'xterm-kitty'
    
    def _check_iterm2_support(self):
        """Check if terminal supports iTerm2 image protocol"""
        return os.environ.get('TERM_PROGRAM') == 'iTerm.app'
    
    def _check_truecolor_support(self):
        """Check if terminal supports 24-bit colors"""
        colorterm = os.environ.get('COLORTERM', '').lower()
        return 'truecolor' in colorterm or '24bit' in colorterm
    
    def _check_unicode_support(self):
        """Check basic Unicode support"""
        try:
            # Try to print some Unicode characters
            test_chars = "🎮💰⚔️🛡️💎"
            print(f"Unicode test: {test_chars}", end="")
            print(" (if you see symbols, Unicode works!)")
            return True
        except UnicodeEncodeError:
            return False
    
    def test_method_1_sixel(self, image_path):
        """Test Method 1: Sixel Graphics (for compatible terminals)"""
        print(f"\n🎨 METHOD 1: SIXEL GRAPHICS")
        print("-" * 30)
        
        try:
            # Try pure Python sixel implementation first
            sixel_output = self._create_simple_sixel(image_path)
            if sixel_output:
                print("Sixel output (pure Python implementation):")
                print(sixel_output)
                print("(If you see the image above, Sixel works!)")
                return True
            
        except Exception as e:
            print(f"❌ Pure Python sixel failed: {e}")
        
        try:
            # Fallback: Try ImageMagick if available
            result = subprocess.run([
                'magick', str(image_path), '-resize', '64x64', 'sixel:-'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("Sixel output (ImageMagick):")
                print(result.stdout)
                return True
            else:
                print("❌ ImageMagick available but failed")
                
        except FileNotFoundError:
            print("❌ ImageMagick (magick command) not found")
        except subprocess.TimeoutExpired:
            print("❌ ImageMagick timeout")
        except Exception as e:
            print(f"❌ ImageMagick error: {e}")
        
        # Final fallback: Try libsixel if available
        try:
            from libsixel import sixel_dither_new, sixel_encode
            
            with Image.open(image_path) as img:
                img = img.resize((64, 64))
                img = img.convert('RGB')
                
                print("✅ libsixel library available - would work for sixel conversion")
                return True
                
        except ImportError:
            print("❌ libsixel library not available")
        
        return False
    
    def _create_simple_sixel(self, image_path):
        """Create a simple sixel representation using pure Python"""
        try:
            with Image.open(image_path) as img:
                # Handle transparency
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                else:
                    img = img.convert('RGB')
                
                # Resize to reasonable size for sixel
                img = img.resize((48, 48))
                
                # Simple sixel header
                sixel_data = "\033Pq"  # Sixel start sequence
                
                # Define a simple color palette (we'll use 16 colors for simplicity)
                colors = [
                    (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
                    (0, 0, 128), (128, 0, 128), (0, 128, 128), (192, 192, 192),
                    (128, 128, 128), (255, 0, 0), (0, 255, 0), (255, 255, 0),
                    (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255)
                ]
                
                # Define palette in sixel format
                for i, (r, g, b) in enumerate(colors):
                    # Convert RGB to sixel color definition
                    sixel_data += f"#{i};2;{r*100//255};{g*100//255};{b*100//255}"
                
                # Convert image to sixel data (simplified version)
                # Process image in strips of 6 pixels high (sixel limitation)
                for y in range(0, img.height, 6):
                    strip_height = min(6, img.height - y)
                    
                    # For each color, create a line
                    for color_idx in range(len(colors)):
                        sixel_data += f"#{color_idx}"
                        line_data = ""
                        
                        for x in range(img.width):
                            # Create sixel character for this column
                            sixel_char = 0
                            for row in range(strip_height):
                                if y + row < img.height:
                                    pixel = img.getpixel((x, y + row))
                                    # Find closest color
                                    closest_color = self._find_closest_color(pixel, colors)
                                    if closest_color == color_idx:
                                        sixel_char |= (1 << row)
                            
                            if sixel_char:
                                line_data += chr(63 + sixel_char)  # Sixel encoding
                        
                        if line_data:
                            sixel_data += line_data + "$"  # End of line
                    
                    sixel_data += "-"  # Next strip
                
                # Sixel end sequence
                sixel_data += "\033\\"
                
                return sixel_data
                
        except Exception as e:
            print(f"❌ Simple sixel creation failed: {e}")
            return None
    
    def _find_closest_color(self, pixel, colors):
        """Find closest color in palette"""
        r, g, b = pixel
        min_distance = float('inf')
        closest_idx = 0
        
        for i, (cr, cg, cb) in enumerate(colors):
            # Simple Euclidean distance
            distance = ((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_idx = i
        
        return closest_idx
    
    def _display_all_icons_colored_blocks(self, downloaded_images):
        """Display all icons using colored blocks method in 3 sizes"""
        print(f"\n🎨 ALL ICONS - COLORED BLOCKS METHOD (3 SIZES)")
        print("=" * 60)
        
        sizes = [(8, "Small"), (16, "Medium"), (32, "Large")]
        
        for size, size_name in sizes:
            print(f"\n📏 {size_name} ({size}x{size}):")
            print("-" * 40)
            
            # Show all icons in a row for smaller sizes, individual for larger
            if size <= 16:
                self._render_icons_in_row(downloaded_images, size)
            else:
                for name, image_path in downloaded_images.items():
                    print(f"\n🟡 {name}:")
                    self._render_single_icon_colored_blocks(image_path, size)
    
    def _display_all_icons_braille(self, downloaded_images):
        """Display all icons using braille art method"""
        print(f"\n⠿ ALL ICONS - BRAILLE ART METHOD (FIXED ASPECT RATIO)")
        print("=" * 60)
        
        for name, image_path in downloaded_images.items():
            print(f"\n⠿ {name}:")
            self._render_single_icon_braille(image_path)
    
    def _display_all_icons_ascii(self, downloaded_images):
        """Display all icons using ASCII art method"""
        print(f"\n🎭 ALL ICONS - ASCII ART METHOD")
        print("=" * 60)
        
        for name, image_path in downloaded_images.items():
            print(f"\n🎭 {name}:")
            self._render_single_icon_ascii(image_path)
    
    def _render_single_icon_colored_blocks(self, image_path, size=16):
        """Render a single icon using colored blocks"""
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Use specified size
                target_width = size
                target_height = size
                img = img.resize((target_width, target_height))
                
                # Process image in pairs of rows
                for y in range(0, img.height, 2):
                    line = ""
                    for x in range(img.width):
                        # Get top pixel with alpha
                        pixel1 = img.getpixel((x, y))
                        if len(pixel1) == 4:
                            r1, g1, b1, a1 = pixel1
                        else:
                            r1, g1, b1, a1 = pixel1[0], pixel1[1], pixel1[2], 255
                        
                        # Get bottom pixel with alpha
                        if y + 1 < img.height:
                            pixel2 = img.getpixel((x, y + 1))
                            if len(pixel2) == 4:
                                r2, g2, b2, a2 = pixel2
                            else:
                                r2, g2, b2, a2 = pixel2[0], pixel2[1], pixel2[2], 255
                        else:
                            r2, g2, b2, a2 = r1, g1, b1, a1
                        
                        # Handle transparency
                        if a1 < 50 and a2 < 50:
                            line += " "
                        elif a1 < 50:
                            line += f"\033[38;2;{r2};{g2};{b2}m▄\033[0m"
                        elif a2 < 50:
                            line += f"\033[38;2;{r1};{g1};{b1}m▀\033[0m"
                        else:
                            line += f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀\033[0m"
                    print(line)
        except Exception as e:
            print(f"❌ Error rendering {image_path}: {e}")
    
    def _render_single_icon_braille(self, image_path):
        """Render a single icon using braille art (compact version)"""
        try:
            with Image.open(image_path) as img:
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Use 1:1 ratio for square icons - simpler and more accurate
                target_width = 24
                target_height = 24  # Square ratio for round icons
                img = img.resize((target_width, target_height))
                img = img.convert('L')
                
                for y in range(0, img.height, 4):
                    line = ""
                    for x in range(0, img.width, 2):
                        dots = 0
                        dot_positions = [
                            (0, 0, 0x01), (0, 1, 0x08),
                            (0, 2, 0x02), (0, 3, 0x10),
                            (1, 0, 0x04), (1, 1, 0x20),
                            (1, 2, 0x40), (1, 3, 0x80)
                        ]
                        
                        for dx, dy, bit in dot_positions:
                            if x + dx < img.width and y + dy < img.height:
                                pixel = img.getpixel((x + dx, y + dy))
                                if pixel < 180:
                                    dots |= bit
                        
                        braille_char = chr(0x2800 + dots)
                        line += braille_char
                    print(line)
        except Exception as e:
            print(f"❌ Error rendering {image_path}: {e}")
    
    def _render_single_icon_ascii(self, image_path):
        """Render a single icon using ASCII art (compact version)"""
        try:
            with Image.open(image_path) as img:
                img = img.resize((20, 10))
                img = img.convert('L')
                
                ascii_chars = "@%#*+=-:. "
                
                for y in range(img.height):
                    line = ""
                    for x in range(img.width):
                        pixel = img.getpixel((x, y))
                        char_index = pixel * (len(ascii_chars) - 1) // 255
                        line += ascii_chars[char_index]
                    print(line)
        except Exception as e:
            print(f"❌ Error rendering {image_path}: {e}")
    
    def _render_icons_in_row(self, downloaded_images, size):
        """Render multiple small icons side by side"""
        try:
            # Prepare all icons
            icon_data = {}
            names = list(downloaded_images.keys())
            
            for name, image_path in downloaded_images.items():
                try:
                    with Image.open(image_path) as img:
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        
                        img = img.resize((size, size))
                        icon_data[name] = img.copy()
                except Exception as e:
                    continue
            
            if not icon_data:
                return
            
            # Print names header (shortened)
            header = ""
            for name in names:
                if name in icon_data:
                    short_name = name.replace(" Orb", "")[:6]
                    header += f"{short_name:<{size+2}}"
            print(header)
            
            # Render all icons line by line
            for y in range(0, size, 2):
                line = ""
                
                for name in names:
                    if name not in icon_data:
                        continue
                    
                    img = icon_data[name]
                    icon_line = ""
                    
                    for x in range(size):
                        # Get pixels and handle transparency (same logic as before)
                        pixel1 = img.getpixel((x, y))
                        r1, g1, b1, a1 = pixel1 if len(pixel1) == 4 else (*pixel1, 255)
                        
                        if y + 1 < size:
                            pixel2 = img.getpixel((x, y + 1))
                            r2, g2, b2, a2 = pixel2 if len(pixel2) == 4 else (*pixel2, 255)
                        else:
                            r2, g2, b2, a2 = r1, g1, b1, a1
                        
                        if a1 < 50 and a2 < 50:
                            icon_line += " "
                        elif a1 < 50:
                            icon_line += f"\033[38;2;{r2};{g2};{b2}m▄\033[0m"
                        elif a2 < 50:
                            icon_line += f"\033[38;2;{r1};{g1};{b1}m▀\033[0m"
                        else:
                            icon_line += f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀\033[0m"
                    
                    line += icon_line + "  "
                
                print(line)
                
        except Exception as e:
            print(f"❌ Error rendering row: {e}")
            # Fallback to individual rendering
            for name, image_path in downloaded_images.items():
                print(f"\n🟡 {name}:")
                self._render_single_icon_colored_blocks(image_path, size)
    
    def test_method_2_kitty(self, image_path):
        """Test Method 2: Kitty Graphics Protocol"""
        print(f"\n🐱 METHOD 2: KITTY GRAPHICS PROTOCOL")
        print("-" * 30)
        
        if not self._check_kitty_graphics():
            print("❌ Not running in Kitty terminal")
            return False
        
        try:
            import base64
            
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Kitty graphics protocol escape sequence
            print(f"\033_Gf=100,s=64,v=64;{image_data}\033\\")
            print("✅ Kitty graphics protocol sent!")
            return True
            
        except Exception as e:
            print(f"❌ Kitty graphics failed: {e}")
            return False
    
    def test_method_3_iterm2(self, image_path):
        """Test Method 3: iTerm2 Image Protocol"""
        print(f"\n🖥️  METHOD 3: ITERM2 IMAGE PROTOCOL")
        print("-" * 30)
        
        if not self._check_iterm2_support():
            print("❌ Not running in iTerm2")
            return False
        
        try:
            import base64
            
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # iTerm2 image protocol
            print(f"\033]1337;File=inline=1;width=64px;height=64px:{image_data}\007")
            print("✅ iTerm2 image protocol sent!")
            return True
            
        except Exception as e:
            print(f"❌ iTerm2 image failed: {e}")
            return False
    
    def test_method_4_ascii_art(self, image_path):
        """Test Method 4: ASCII Art Conversion"""
        print(f"\n🎭 METHOD 4: ASCII ART CONVERSION")
        print("-" * 30)
        
        try:
            with Image.open(image_path) as img:
                # Resize to smaller size for ASCII
                img = img.resize((32, 16))
                img = img.convert('L')  # Grayscale
                
                # ASCII characters from dark to light
                ascii_chars = "@%#*+=-:. "
                
                ascii_art = []
                for y in range(img.height):
                    line = ""
                    for x in range(img.width):
                        pixel = img.getpixel((x, y))
                        char_index = pixel * (len(ascii_chars) - 1) // 255
                        line += ascii_chars[char_index]
                    ascii_art.append(line)
                
                print("ASCII Art:")
                for line in ascii_art:
                    print(line)
                
                return True
                
        except Exception as e:
            print(f"❌ ASCII art conversion failed: {e}")
            return False
    
    def test_method_5_colored_blocks(self, image_path):
        """Test Method 5: Colored Unicode Blocks"""
        print(f"\n🌈 METHOD 5: COLORED UNICODE BLOCKS")
        print("-" * 30)
        
        try:
            with Image.open(image_path) as img:
                # Keep original with alpha channel for transparency handling
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Use proper aspect ratio - each terminal char is roughly 1:2 (width:height)
                # We'll use half-blocks (▀▄) to get 2 pixels per character vertically
                target_width = 24
                target_height = target_width  # 1:1 ratio because we'll use half-blocks
                img = img.resize((target_width, target_height))
                
                print("Colored blocks (24-bit color with proper aspect ratio):")
                
                # Process image in pairs of rows (top/bottom half-blocks)
                for y in range(0, img.height, 2):
                    line = ""
                    for x in range(img.width):
                        # Get top pixel with alpha
                        pixel1 = img.getpixel((x, y))
                        if len(pixel1) == 4:  # RGBA
                            r1, g1, b1, a1 = pixel1
                        else:  # RGB
                            r1, g1, b1, a1 = pixel1[0], pixel1[1], pixel1[2], 255
                        
                        # Get bottom pixel with alpha (if exists)
                        if y + 1 < img.height:
                            pixel2 = img.getpixel((x, y + 1))
                            if len(pixel2) == 4:  # RGBA
                                r2, g2, b2, a2 = pixel2
                            else:  # RGB
                                r2, g2, b2, a2 = pixel2[0], pixel2[1], pixel2[2], 255
                        else:
                            r2, g2, b2, a2 = r1, g1, b1, a1  # Use same pixel if no bottom pixel
                        
                        # Handle transparency - skip if both pixels are fully transparent
                        if a1 < 50 and a2 < 50:
                            line += " "  # Just a space for fully transparent areas
                            continue
                        
                        # Handle semi-transparent pixels
                        if a1 < 50:  # Top pixel transparent
                            if a2 >= 50:  # Bottom pixel opaque
                                # Use bottom half block ▄
                                line += f"\033[38;2;{r2};{g2};{b2}m▄\033[0m"
                            else:
                                line += " "  # Both transparent
                        elif a2 < 50:  # Bottom pixel transparent
                            # Use top half block ▀
                            line += f"\033[38;2;{r1};{g1};{b1}m▀\033[0m"
                        else:
                            # Both pixels opaque - use full block with both colors
                            line += f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀\033[0m"
                    print(line)
                
                print("\n(Each colored square above represents a pixel from the icon)")
                return True
                
        except Exception as e:
            print(f"❌ Colored blocks failed: {e}")
            return False
    
    def test_method_6_braille_art(self, image_path):
        """Test Method 6: Braille Pattern Art"""
        print(f"\n⠿ METHOD 6: BRAILLE PATTERN ART")
        print("-" * 30)
        
        try:
            with Image.open(image_path) as img:
                # Handle transparency
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Use 1:1 ratio for square icons - the terminal will handle the rest
                img = img.resize((24, 24))
                img = img.convert('L')  # Grayscale
                
                braille_art = []
                
                # Braille Unicode range starts at U+2800
                for y in range(0, img.height, 4):
                    line = ""
                    for x in range(0, img.width, 2):
                        # Get 2x4 pixel block
                        dots = 0
                        dot_positions = [
                            (0, 0, 0x01), (0, 1, 0x08),
                            (0, 2, 0x02), (0, 3, 0x10),
                            (1, 0, 0x04), (1, 1, 0x20),
                            (1, 2, 0x40), (1, 3, 0x80)
                        ]
                        
                        for dx, dy, bit in dot_positions:
                            if x + dx < img.width and y + dy < img.height:
                                pixel = img.getpixel((x + dx, y + dy))
                                if pixel < 180:  # Inverted threshold - dark pixels become dots
                                    dots |= bit
                        
                        # Convert to braille character
                        braille_char = chr(0x2800 + dots)
                        line += braille_char
                    
                    braille_art.append(line)
                
                print("Braille Art:")
                for line in braille_art:
                    print(line)
                
                return True
                
        except Exception as e:
            print(f"❌ Braille art failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all terminal icon display tests"""
        print("🧪 TERMINAL ICON DISPLAY POC")
        print("=" * 50)
        
        # Check capabilities first
        capabilities = self.check_terminal_capabilities()
        
        # Download test images
        downloaded = self.download_all_test_images()
        
        if not downloaded:
            print("❌ No test images available, aborting tests")
            return
        
        # Test with first image to check capabilities
        test_image_name = list(downloaded.keys())[0]
        test_image_path = downloaded[test_image_name]
        
        print(f"\n🎯 Testing capabilities with: {test_image_name}")
        
        # Test all methods with first image
        methods = [
            ("Method 1: Sixel Graphics", self.test_method_1_sixel),
            ("Method 2: Kitty Graphics", self.test_method_2_kitty),
            ("Method 3: iTerm2 Images", self.test_method_3_iterm2),
            ("Method 4: ASCII Art", self.test_method_4_ascii_art),
            ("Method 5: Colored Blocks", self.test_method_5_colored_blocks),
            ("Method 6: Braille Art", self.test_method_6_braille_art)
        ]
        
        results = {}
        for method_name, method_func in methods:
            try:
                result = method_func(test_image_path)
                results[method_name] = result
            except Exception as e:
                print(f"❌ {method_name} crashed: {e}")
                results[method_name] = False
        
        # Now show all icons using the best working method
        working_methods = [name for name, success in results.items() if success]
        
        if "Method 5: Colored Blocks" in working_methods:
            self._display_all_icons_colored_blocks(downloaded)
        elif "Method 6: Braille Art" in working_methods:
            self._display_all_icons_braille(downloaded)
        elif "Method 4: ASCII Art" in working_methods:
            self._display_all_icons_ascii(downloaded)
        
        # Summary
        print(f"\n📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        working_methods = []
        for method_name, success in results.items():
            status = "✅ WORKS" if success else "❌ FAILED"
            method_display = method_name.replace('test_method_', '').replace('_', ' ').title()
            print(f"{status} - {method_display}")
            
            if success:
                working_methods.append(method_display)
        
        if working_methods:
            print(f"\n🎉 Working methods for your terminal:")
            for method in working_methods:
                print(f"  ✅ {method}")
        else:
            print(f"\n😞 No methods worked perfectly, but ASCII/Braille should work in most terminals")
        
        print(f"\n💡 Recommendation:")
        if "5 Colored Blocks" in working_methods:
            print("  🌈 Use colored Unicode blocks - best quality with true colors!")
        elif "6 Braille Art" in working_methods:
            print("  ⠿ Use Braille patterns - high detail in compact form!")
        elif "4 Ascii Art" in working_methods:
            print("  🎭 Use ASCII art - universal compatibility!")
        else:
            print("  😅 Stick with emojis - they're the most reliable!")


def main():
    """Main function"""
    print("🎨 Welcome to the Terminal Icon Display POC!")
    print("This will test different methods to show actual images in your terminal.\n")
    
    tester = TerminalIconTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n📁 Test files saved in: {tester.test_dir.absolute()}")
    print("🧹 You can delete this folder when done testing")


    def _render_icons_in_row(self, downloaded_images, size):
        """Render multiple small icons side by side"""
        try:
            # Prepare all icons
            icon_data = {}
            names = list(downloaded_images.keys())
            
            for name, image_path in downloaded_images.items():
                try:
                    with Image.open(image_path) as img:
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        
                        img = img.resize((size, size))
                        icon_data[name] = img.copy()
                except Exception as e:
                    continue
            
            if not icon_data:
                return
            
            # Print names header (shortened)
            header = ""
            for name in names:
                if name in icon_data:
                    short_name = name.replace(" Orb", "")[:6]
                    header += f"{short_name:<{size+2}}"
            print(header)
            
            # Render all icons line by line
            for y in range(0, size, 2):
                line = ""
                
                for name in names:
                    if name not in icon_data:
                        continue
                    
                    img = icon_data[name]
                    icon_line = ""
                    
                    for x in range(size):
                        # Get pixels and handle transparency (same logic as before)
                        pixel1 = img.getpixel((x, y))
                        r1, g1, b1, a1 = pixel1 if len(pixel1) == 4 else (*pixel1, 255)
                        
                        if y + 1 < size:
                            pixel2 = img.getpixel((x, y + 1))
                            r2, g2, b2, a2 = pixel2 if len(pixel2) == 4 else (*pixel2, 255)
                        else:
                            r2, g2, b2, a2 = r1, g1, b1, a1
                        
                        if a1 < 50 and a2 < 50:
                            icon_line += " "
                        elif a1 < 50:
                            icon_line += f"\033[38;2;{r2};{g2};{b2}m▄\033[0m"
                        elif a2 < 50:
                            icon_line += f"\033[38;2;{r1};{g1};{b1}m▀\033[0m"
                        else:
                            icon_line += f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀\033[0m"
                    
                    line += icon_line + "  "
                
                print(line)
                
        except Exception as e:
            print(f"❌ Error rendering row: {e}")
            # Fallback to individual rendering
            for name, image_path in downloaded_images.items():
                print(f"\n🟡 {name}:")
                self._render_single_icon_colored_blocks(image_path, size)


def main():
    """Main function"""
    print("🎨 Welcome to the Terminal Icon Display POC!")
    print("This will test different methods to show actual images in your terminal.\n")
    
    tester = TerminalIconTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n📁 Test files saved in: {tester.test_dir.absolute()}")
    print("🧹 You can delete this folder when done testing")


if __name__ == "__main__":
    main()