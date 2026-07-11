import cv2
import numpy as np
import os

def generate_footprint(img_path, out_file):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    h, w = img.shape
    scale = 25.0 / max(w, h)
    offset_x = - (w * scale / 2.0)
    offset_y = - (h * scale / 2.0)
    
    with open(out_file, 'w') as f:
        name = os.path.basename(out_file).replace('.kicad_mod', '')
        f.write(f'(footprint "{name}" (layer "F.Cu")\n')
        f.write('  (attr board_only)\n')
        
        for contour in contours:
            if len(contour) < 5:
                continue
                
            pts = []
            for pt in contour:
                px = pt[0][0]
                py = pt[0][1]
                kx = offset_x + px * scale
                ky = offset_y + py * scale
                pts.append(f'(xy {kx:.4f} {ky:.4f})')
                
            if pts:
                pts_str = '\n      '.join(pts)
                f.write('  (fp_poly (pts\n')
                f.write(f'      {pts_str}\n')
                f.write('    ) (layer "F.Cu") (width 0.1) (fill solid))\n')
                
                f.write('  (fp_poly (pts\n')
                f.write(f'      {pts_str}\n')
                f.write('    ) (layer "F.Mask") (width 0.1) (fill solid))\n')
                
        f.write(')\n')
    print("Generated footprint at", out_file)

def main():
    studio = r'C:\Users\Chris Williams\.gemini\antigravity\brain\fddc0bb3-e31c-4290-9542-89fe3f0dd2f4\studio_encoder_graphic_1783295254743.png'
    brutalist = r'C:\Users\Chris Williams\.gemini\antigravity\brain\fddc0bb3-e31c-4290-9542-89fe3f0dd2f4\brutalist_encoder_graphic_1783295317522.png'
    
    generate_footprint(studio, 'build/icio500/EncoderGraphicStudio.kicad_mod')
    generate_footprint(brutalist, 'build/icio500/EncoderGraphicBrutalist.kicad_mod')

if __name__ == '__main__':
    main()
