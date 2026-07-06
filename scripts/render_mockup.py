import xml.etree.ElementTree as ET
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

def render():
    tree = ET.parse('build/icio500/faceplate_front.svg')
    root = tree.getroot()
    
    # SVG namespace
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    
    # 1. Add background rect
    bg = ET.Element('{http://www.w3.org/2000/svg}rect')
    bg.set('width', '100%')
    bg.set('height', '100%')
    bg.set('fill', '#2c2c2c') # Dark metal
    root.insert(4, bg)
    
    led_paths = []
    
    # 2. Iterate through elements and colorize
    for el in root.iter():
        style = el.get('style', '')
        if style:
            # Change Edge.Cuts (D0D2CD) to invisible or dark
            if '#D0D2CD' in style:
                style = style.replace('#D0D2CD', '#111111')
                
            # Change F.Mask (D864FF)
            if '#D864FF' in style:
                # Is it filled? (LED window). It has fill:#D864FF
                if 'fill:#D864FF' in style and 'fill:none' not in style:
                    led_paths.append(el)
                else:
                    # It's a line (Geometric art exposed)
                    style = style.replace('#D864FF', '#E7BA3D') # Gold
            
            # F.Cu lines (Geometry, C83434)
            if '#C83434' in style:
                style = style.replace('#C83434', '#E7BA3D')
                
            el.set('style', style)
            
    # Sort LED paths by Y-coordinate
    def get_y(element):
        d = element.get('d', '')
        if d.startswith('M'):
            parts = d.split()
            if len(parts) >= 3:
                try:
                    val = parts[2].replace(',', '')
                    return float(val)
                except:
                    return 0
            if len(parts) == 2 and ',' in parts[1]:
                try:
                    return float(parts[1].split(',')[1])
                except:
                    return 0
        return 0
        
    led_paths.sort(key=get_y)
    
    for i, el in enumerate(led_paths):
        style = el.get('style', '')
        if i == 0:
            color = '#FF3333' # Red
        elif i in [1, 2]:
            color = '#FFAA00' # Yellow/Orange
        elif i < 10:
            color = '#33FF33' # Green
        else:
            color = '#111111' # Encoder hole (dark or unlit)
            
        style = style.replace('#D864FF', color)
        el.set('style', style)

    tree.write('build/icio500/faceplate_front_render.svg')
    
    # Convert to PNG
    drawing = svg2rlg('build/icio500/faceplate_front_render.svg')
    renderPM.drawToFile(drawing, 'views/faceplate_progress.png', fmt='PNG', dpi=300)
    print("Rendered beautiful mockup!")

if __name__ == '__main__':
    render()
