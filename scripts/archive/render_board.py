import sys, os
import pcbnew
import xml.etree.ElementTree as ET
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

def render_board(pcb_path, svg_path, png_path):
    # Export SVG via KiCad CLI
    # We'll call kicad-cli from Python using os.system (quick)
    cmd = f"\"C:\\Program Files\\KiCad\\10.0\\bin\\kicad-cli.exe\" pcb export svg --page-size-mode 2 --mode-single --layers Edge.Cuts,F.Cu,F.Mask,F.SilkS --exclude-drawing-sheet -o {svg_path} {pcb_path}"
    os.system(cmd)
    # Parse and colorize SVG similar to previous render_mockup
    tree = ET.parse(svg_path)
    root = tree.getroot()
    # Add dark background
    bg = ET.Element('{http://www.w3.org/2000/svg}rect')
    bg.set('width', '100%')
    bg.set('height', '100%')
    bg.set('fill', '#2c2c2c')
    root.insert(4, bg)
    for el in root.iter():
        style = el.get('style', '')
        if style:
            if '#D0D2CD' in style:
                style = style.replace('#D0D2CD', '#111111')
            if '#D864FF' in style:
                if 'fill:#D864FF' in style and 'fill:none' not in style:
                    # LED window – render as dark (transparent)
                    style = style.replace('#D864FF', '#111111')
                else:
                    style = style.replace('#D864FF', '#E7BA3D')
            if '#C83434' in style:
                style = style.replace('#C83434', '#E7BA3D')
            el.set('style', style)
    tree.write(svg_path)
    # Convert to PNG
    drawing = svg2rlg(svg_path)
    renderPM.drawToFile(drawing, png_path, fmt='PNG', dpi=300)
    print(f"Rendered {pcb_path} to {png_path}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: render_board.py <pcb.kicad_pcb> <output.svg> <output.png>')
        sys.exit(1)
    render_board(sys.argv[1], sys.argv[2], sys.argv[3])
