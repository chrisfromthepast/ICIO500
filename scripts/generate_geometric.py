import pcbnew
import math

def build_geometric_scale(out_file):
    name = os.path.basename(out_file).replace('.kicad_mod', '')
    with open(out_file, 'w') as f:
        f.write(f'(footprint "{name}" (layer "F.Cu")\n')
        f.write('  (attr board_only)\n')
        
        layers = ['F.Cu', 'F.Mask']
        
        r_in = 10.0
        r_out = r_in * math.sqrt(2.0)
        
        for layer in layers:
            # Concentric circles
            f.write(f'  (fp_circle (center 0 0) (end {r_out:.4f} 0) (layer "{layer}") (width 0.25) (fill none))\n')
            f.write(f'  (fp_circle (center 0 0) (end {r_in:.4f} 0) (layer "{layer}") (width 0.25) (fill none))\n')
            
            # Upright Square
            pts = [(-r_in, -r_in), (r_in, -r_in), (r_in, r_in), (-r_in, r_in)]
            for i in range(4):
                p1 = pts[i]
                p2 = pts[(i+1)%4]
                f.write(f'  (fp_line (start {p1[0]:.4f} {p1[1]:.4f}) (end {p2[0]:.4f} {p2[1]:.4f}) (layer "{layer}") (width 0.25))\n')
                
            # Rotated Square (Diamond)
            pts_dia = [(0, -r_out), (r_out, 0), (0, r_out), (-r_out, 0)]
            for i in range(4):
                p1 = pts_dia[i]
                p2 = pts_dia[(i+1)%4]
                f.write(f'  (fp_line (start {p1[0]:.4f} {p1[1]:.4f}) (end {p2[0]:.4f} {p2[1]:.4f}) (layer "{layer}") (width 0.25))\n')
                
            # Crosshairs (start inside the inner circle, extend past outer)
            r_start = 5.0
            r_cross = r_out + 3.0
            angles = [0, 90, 180, 270, 45, 135, 225, 315]
            for deg in angles:
                rad = deg * math.pi / 180.0
                x1 = r_start * math.cos(rad)
                y1 = r_start * math.sin(rad)
                x2 = r_cross * math.cos(rad)
                y2 = r_cross * math.sin(rad)
                f.write(f'  (fp_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (layer "{layer}") (width 0.25))\n')
                
            # Radial ticks on the outer circle
            num_ticks = 48
            for i in range(num_ticks):
                rad = i * 2 * math.pi / num_ticks
                is_major = (i % 6 == 0) # every 45 degrees
                tick_out = r_out + (2.5 if is_major else 1.2)
                
                x1 = r_out * math.cos(rad)
                y1 = r_out * math.sin(rad)
                x2 = tick_out * math.cos(rad)
                y2 = tick_out * math.sin(rad)
                f.write(f'  (fp_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (layer "{layer}") (width 0.25))\n')
                
        f.write(')\n')
    print("Generated", out_file)

if __name__ == '__main__':
    import os
    build_geometric_scale('build/icio500/custom.pretty/EncoderGraphicGeometric.kicad_mod')
