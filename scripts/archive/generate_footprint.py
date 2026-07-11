import cv2
import numpy as np
import sys
import math

def main():
    img_path = r"C:\Users\Chris Williams\.gemini\antigravity\brain\fddc0bb3-e31c-4290-9542-89fe3f0dd2f4\wispy_art_v2_1782758751936.png"
    out_path = "build/icio500/WispyArt.kicad_mod"
    
    # Load image and threshold
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error loading image: {img_path}")
        sys.exit(1)
        
    _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Board dimensions: 38.1 x 133.35
    # Max target size: 36 x 130
    # Offset target center: X=19.05, Y=66.67
    
    h, w = img.shape
    scale = min(36.0 / w, 130.0 / h)
    
    offset_x = 19.05 - (w * scale / 2.0)
    offset_y = 66.67 - (h * scale / 2.0)
    
    out = []
    out.append('(footprint "WispyArt"')
    out.append('  (layer "F.Cu")')
    out.append('  (attr board_only)')
    
    for cnt in contours:
        # Simplify contour
        epsilon = 0.002 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        
        # Filter tiny specks
        area = cv2.contourArea(approx)
        if area < 10:
            continue
            
        pts = []
        for pt in approx:
            x = pt[0][0] * scale + offset_x
            y = pt[0][1] * scale + offset_y
            pts.append(f'(xy {x:.4f} {y:.4f})')
            
        pts_str = " ".join(pts)
        
        if len(pts) < 3:
            continue
            
        # Large contours -> ENIG (F.Cu + F.Mask)
        # Small contours -> Silkscreen (F.SilkS)
        if area > 100:
            out.append(f'  (fp_poly (pts {pts_str}) (layer "F.Cu") (width 0) (fill solid))')
            out.append(f'  (fp_poly (pts {pts_str}) (layer "F.Mask") (width 0) (fill solid))')
        else:
            out.append(f'  (fp_poly (pts {pts_str}) (layer "F.SilkS") (width 0) (fill solid))')
            
    out.append(")")
    
    with open(out_path, "w") as f:
        f.write("\n".join(out))
        
    print(f"Generated footprint at {out_path}")

if __name__ == "__main__":
    main()
