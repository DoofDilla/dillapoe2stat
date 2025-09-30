#!/usr/bin/env python3
"""
Convert HasiSkull_64x64.png to various ANSI art formats
Uses the existing routines from terminal_icon_poc.py
"""

import os
import sys
from pathlib import Path
from PIL import Image


class HasiSkullANSIConverter:
    """Convert HasiSkull image to various ANSI art formats"""
    
    def __init__(self, image_path):
        self.image_path = Path(image_path)
        if not self.image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
    
    def generate_colored_blocks(self, size=32):
        """Generate colored blocks ANSI art (like terminal_icon_poc method 5)"""
        ansi_lines = []
        
        try:
            with Image.open(self.image_path) as img:
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Resize to target size
                img = img.resize((size, size))
                
                # Process image in pairs of rows (using half-blocks ▀▄)
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
                        
                        # Handle transparency and create ANSI codes
                        if a1 < 50 and a2 < 50:
                            line += " "
                        elif a1 < 50:
                            line += f"\033[38;2;{r2};{g2};{b2}m▄\033[0m"
                        elif a2 < 50:
                            line += f"\033[38;2;{r1};{g1};{b1}m▀\033[0m"
                        else:
                            line += f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀\033[0m"
                    
                    ansi_lines.append(line)
                    
        except Exception as e:
            print(f"❌ Error generating colored blocks: {e}")
            return []
        
        return ansi_lines
    
    def generate_braille_art(self, size=48):
        """Generate braille pattern ANSI art (like terminal_icon_poc method 6)"""
        ansi_lines = []
        
        try:
            with Image.open(self.image_path) as img:
                # Handle transparency by compositing on white background
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Resize and convert to grayscale
                img = img.resize((size, size))
                img = img.convert('L')
                
                # Process in 2x4 pixel blocks for braille patterns
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
                                # Inverted threshold - dark pixels become dots
                                if pixel < 180:
                                    dots |= bit
                        
                        # Convert to braille character
                        braille_char = chr(0x2800 + dots)
                        line += braille_char
                    
                    ansi_lines.append(line)
                    
        except Exception as e:
            print(f"❌ Error generating braille art: {e}")
            return []
        
        return ansi_lines
    
    def generate_ascii_art(self, width=64, height=32):
        """Generate ASCII art (like terminal_icon_poc method 4)"""
        ansi_lines = []
        
        try:
            with Image.open(self.image_path) as img:
                # Resize and convert to grayscale
                img = img.resize((width, height))
                img = img.convert('L')
                
                # ASCII characters from dark to light
                ascii_chars = "@%#*+=-:. "
                
                for y in range(img.height):
                    line = ""
                    for x in range(img.width):
                        pixel = img.getpixel((x, y))
                        char_index = pixel * (len(ascii_chars) - 1) // 255
                        line += ascii_chars[char_index]
                    ansi_lines.append(line)
                    
        except Exception as e:
            print(f"❌ Error generating ASCII art: {e}")
            return []
        
        return ansi_lines
    
    def save_ansi_file(self, ansi_lines, filename, title=""):
        """Save ANSI art to file with optional title"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if title:
                    f.write(f"# {title}\n")
                    f.write(f"# Generated from {self.image_path.name}\n")
                    f.write(f"# Size: {len(ansi_lines)} lines\n")
                    f.write("\n")
                
                for line in ansi_lines:
                    f.write(line + '\n')
            
            print(f"✅ Saved: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving {filename}: {e}")
            return False
    
    def convert_all_formats(self):
        """Convert to all formats and save files"""
        print(f"🎨 Converting {self.image_path.name} to ANSI art formats...\n")
        
        # Generate different formats
        formats = [
            ("colored_blocks_8x8", self.generate_colored_blocks(8), "HasiSkull Colored Blocks 8x8"),
            ("colored_blocks_16x16", self.generate_colored_blocks(16), "HasiSkull Colored Blocks 16x16"),
            ("colored_blocks_32x32", self.generate_colored_blocks(32), "HasiSkull Colored Blocks 32x32"),
            ("braille_48x48", self.generate_braille_art(48), "HasiSkull Braille Art 48x48"),
            ("braille_64x64", self.generate_braille_art(64), "HasiSkull Braille Art 64x64")
        ]
        
        results = []
        for format_name, ansi_lines, title in formats:
            if ansi_lines:
                filename = f"hasiskull_{format_name}.ansi"
                if self.save_ansi_file(ansi_lines, filename, title):
                    results.append((format_name, filename, len(ansi_lines)))
        
        return results
    
    def preview_in_terminal(self, ansi_lines, title=""):
        """Preview ANSI art in terminal"""
        if title:
            print(f"\n🎯 {title}")
            print("=" * len(title))
        
        for line in ansi_lines:
            print(line)
        print()


def main():
    """Main function"""
    image_path = "HasiSkull_64x64.png"
    
    try:
        converter = HasiSkullANSIConverter(image_path)
        
        # Convert and save all formats
        results = converter.convert_all_formats()
        
        if results:
            print(f"\n🎉 Successfully generated {len(results)} ANSI art files:")
            for format_name, filename, lines in results:
                print(f"  📄 {filename} ({lines} lines)")
        
        # Preview some formats in terminal
        print(f"\n🖼️  PREVIEWS:")
        print("=" * 50)
        
        # Show colored blocks 8x8
        colored_8 = converter.generate_colored_blocks(8)
        if colored_8:
            converter.preview_in_terminal(colored_8, "Colored Blocks 8x8")
        
        # Show colored blocks 16x16
        colored_16 = converter.generate_colored_blocks(16)
        if colored_16:
            converter.preview_in_terminal(colored_16, "Colored Blocks 16x16")
        
        # Show colored blocks 32x32
        colored_32 = converter.generate_colored_blocks(32)
        if colored_32:
            converter.preview_in_terminal(colored_32, "Colored Blocks 32x32")
        
        # Show braille art 48x48
        braille_48 = converter.generate_braille_art(48)
        if braille_48:
            converter.preview_in_terminal(braille_48, "Braille Art 48x48")
            
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("Make sure HasiSkull_64x64.png exists in the current directory.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()