import os
import math

def build_geometric_scale(out_file):
    name = os.path.basename(out_file).replace('.kicad_mod', '')
    with open(out_file, 'w') as f:
        f.write(f'(footprint "{name}" (layer "F.Cu")\n')
        f.write('  (attr board_only)\n')
        
        layers = ['F.Cu', 'F.Mask']
        
        for layer in layers:
            # Concentric circles
            f.write(f'  (fp_circle (center 0 0) (end 12 0) (layer "{layer}") (width 0.25) (fill none))\n')
            f.write(f'  (fp_circle (center 0 0) (end 9 0) (layer "{layer}") (width 0.25) (fill none))\n')
            
            # Upright Square (bounding the 12mm circle)
            r_sq = 12.0
            pts = [(-r_sq, -r_sq), (r_sq, -r_sq), (r_sq, r_sq), (-r_sq, r_sq)]
            for i in range(4):
                p1 = pts[i]
                p2 = pts[(i+1)%4]
                f.write(f'  (fp_line (start {p1[0]:.4f} {p1[1]:.4f}) (end {p2[0]:.4f} {p2[1]:.4f}) (layer "{layer}") (width 0.25))\n')
                
            # Rotated Square (Diamond) bounding the square corners
            # The corner of the square is at distance 12*sqrt(2) = 16.97
            r_dia = 16.97
            pts_dia = [(0, -r_dia), (r_dia, 0), (0, r_dia), (-r_dia, 0)]
            for i in range(4):
                p1 = pts_dia[i]
                p2 = pts_dia[(i+1)%4]
                f.write(f'  (fp_line (start {p1[0]:.4f} {p1[1]:.4f}) (end {p2[0]:.4f} {p2[1]:.4f}) (layer "{layer}") (width 0.25))\n')
                
            # Crosshairs (clipped at inner circle radius 9mm, extending to 19mm)
            r_inner = 9.0
            r_outer = 19.0
            angles = [0, 90, 180, 270, 45, 135, 225, 315]
            for deg in angles:
                rad = deg * math.pi / 180.0
                x1 = r_inner * math.cos(rad)
                y1 = r_inner * math.sin(rad)
                x2 = r_outer * math.cos(rad)
                y2 = r_outer * math.sin(rad)
                f.write(f'  (fp_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (layer "{layer}") (width 0.25))\n')
                
            # Radial ticks on the outer circle (12mm)
            num_ticks = 24
            for i in range(num_ticks):
                rad = i * 2 * math.pi / num_ticks
                x1 = 11.0 * math.cos(rad)
                y1 = 11.0 * math.sin(rad)
                x2 = 12.0 * math.cos(rad)
                y2 = 12.0 * math.sin(rad)
                f.write(f'  (fp_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (layer "{layer}") (width 0.25))\n')
                
        f.write(')\n')
    print("Generated", out_file)

def build_studio_scale(out_file):
    name = os.path.basename(out_file).replace('.kicad_mod', '')
    with open(out_file, 'w') as f:
        f.write(f'(footprint "{name}" (layer "F.Cu")\n')
        f.write('  (attr board_only)\n')
        
        layers = ['F.Cu', 'F.Mask']
        
        for layer in layers:
            num_ticks = 21
            start_angle = 135 * math.pi / 180.0
            end_angle = 405 * math.pi / 180.0
            
            for i in range(num_ticks):
                angle = start_angle + i * (end_angle - start_angle) / (num_ticks - 1)
                
                # Major ticks every 5th tick
                is_major = (i % 5 == 0)
                r_in = 8.0 if is_major else 10.0
                r_out = 12.0
                
                x1 = r_in * math.cos(angle)
                y1 = r_in * math.sin(angle)
                x2 = r_out * math.cos(angle)
                y2 = r_out * math.sin(angle)
                
                f.write(f'  (fp_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (layer "{layer}") (width 0.25))\n')
                
        f.write(')\n')
    print("Generated", out_file)

def main():
    build_geometric_scale('build/icio500/custom.pretty/EncoderGraphicGeometric.kicad_mod')
    build_studio_scale('build/icio500/custom.pretty/EncoderGraphicStudio.kicad_mod')

if __name__ == '__main__':
    main()
