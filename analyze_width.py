import re

with open('hasiskull_colored_blocks_32x32.ansi', 'r') as f:
    lines = f.readlines()

print("Analyzing ANSI art line widths:")
max_width = 0
for i, line in enumerate(lines[4:20]):  # Check art lines, skip header
    if line.strip() and not line.startswith('#'):
        clean = re.sub(r'\033\[[0-9;]*[mK]', '', line.rstrip())
        width = len(clean)
        max_width = max(max_width, width)
        print(f'Line {i+1}: width={width:2d} chars: "{clean}"')

print(f"\nMax width: {max_width} characters")