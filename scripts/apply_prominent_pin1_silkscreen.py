import re
import pcbnew

def fix_carrier():
    path = "build/icio500/icio500.kicad_pcb"
    print("Fixing carrier board pin 1 silkscreen...")
    b = pcbnew.LoadBoard(path)
    
    # 1. Clean existing board-level pin 1 drawings on F.SilkS
    to_remove = []
    for dwg in b.GetDrawings():
        if dwg.GetLayer() == pcbnew.F_SilkS:
            if isinstance(dwg, pcbnew.PCB_TEXT) and dwg.GetText() in ["1", "A"]:
                to_remove.append(dwg)
            elif isinstance(dwg, pcbnew.PCB_SHAPE) and dwg.GetShapeStr() == "Circle":
                # Remove our added dots
                pos = dwg.GetCenter()
                px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
                for cx, cy in [(155.32, 70.6), (162.0, 90.0), (160.72, 118.9), (92.0, 90.0), (168.0, 145.49), (74.0, 138.025), (72.0, 122.605), (149.0, 93.4), (153.8, 72.05), (162.15, 91.8), (162.25, 117.34), (92.5, 90.0)]:
                    if abs(px - cx) < 0.8 and abs(py - cy) < 0.8:
                        to_remove.append(dwg)
                        break
    for item in to_remove:
        b.Remove(item)
    print(f"  Removed {len(to_remove)} existing pin 1 markers on carrier")

    # (ref, dot_x, dot_y, text_x, text_y)
    items = [
        ("U4 (THAT1646)", 155.32, 70.60, 155.32, 69.30),
        ("U3 (TL072)", 162.00, 90.00, 162.00, 88.70),
        ("U2 (THAT1200)", 162.80, 117.34, 162.80, 118.70),
        ("U5 (Daisy Seed Socket)", 92.00, 90.00, 92.00, 88.50),
        ("U1 (TSR 1-2450)", 168.00, 145.49, 168.00, 147.00),
        ("J_ENC (Encoder Header)", 74.00, 138.025, 74.00, 139.50),
        ("U6 (Faceplate Header)", 72.00, 122.605, 72.00, 124.00),
        ("D11 (BAT54S)", 149.00, 93.40, 149.00, 94.60),
    ]

    for label, cx, cy, tx, ty in items:
        # Solid disc: diameter 0.90 mm (radius 0.45 mm)
        dot = pcbnew.PCB_SHAPE(b)
        dot.SetShape(pcbnew.SHAPE_T_CIRCLE)
        dot.SetFilled(True)
        dot.SetCenter(pcbnew.VECTOR2I_MM(cx, cy))
        dot.SetRadius(pcbnew.FromMM(0.45))
        dot.SetLayer(pcbnew.F_SilkS)
        dot.SetWidth(pcbnew.FromMM(0.10))
        b.Add(dot)

        # Bold numeral '1' text
        txt = pcbnew.PCB_TEXT(b)
        txt.SetText("1")
        txt.SetPosition(pcbnew.VECTOR2I_MM(tx, ty))
        txt.SetTextSize(pcbnew.VECTOR2I_MM(1.0, 1.0))
        txt.SetTextThickness(pcbnew.FromMM(0.18))
        txt.SetLayer(pcbnew.F_SilkS)
        txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        txt.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        b.Add(txt)
        print(f"  Added Pin 1 marker for {label}: dot=({cx:.2f}, {cy:.2f}), '1'=({tx:.2f}, {ty:.2f})")

    b.Save(path)
    
    # 3. In the raw S-expression, remove the footprint circles that cause silk_over_copper warnings
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove (-3.6 -1.905) circles from SOIC-8 footprints
    content = re.sub(
        r'\t\t\(fp_circle\s*\n\t\t\t\(center -3\.6 -1\.905\)\s*\n\t\t\t\(end -3\.25 -1\.905\)\s*\n\t\t\t\(stroke\s*\n\t\t\t\t\(width 0\.1\)\s*\n\t\t\t\t\(type solid\)\s*\n\t\t\t\)\s*\n\t\t\t\(fill yes\)\s*\n\t\t\t\(layer "F\.SilkS"\)\s*\n\t\t\t\(uuid "[^"]+"\)\s*\n\t\t\)',
        '',
        content
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Carrier card updated and clean.")

def fix_faceplate():
    path = "build/icio500/faceplate_front.kicad_pcb"
    print("\nFixing faceplate board pin 1 silkscreen and layer count...")
    b = pcbnew.LoadBoard(path)
    
    to_remove = []
    for dwg in b.GetDrawings():
        if dwg.GetLayer() == pcbnew.B_SilkS:
            if isinstance(dwg, pcbnew.PCB_TEXT) and dwg.GetText() == "1":
                to_remove.append(dwg)
            elif isinstance(dwg, pcbnew.PCB_SHAPE) and dwg.GetShapeStr() == "Circle":
                pos = dwg.GetCenter()
                px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
                if abs(px - 37.50) < 1.0 or abs(px - 10.26) < 1.0 or abs(px - 11.20) < 1.0:
                    to_remove.append(dwg)
    for item in to_remove:
        b.Remove(item)
    print(f"  Removed {len(to_remove)} existing pin 1 markers on faceplate")

    # U1 (PCA9555PW TSSOP-24 on B.SilkS)
    dot_u1 = pcbnew.PCB_SHAPE(b)
    dot_u1.SetShape(pcbnew.SHAPE_T_CIRCLE)
    dot_u1.SetFilled(True)
    dot_u1.SetCenter(pcbnew.VECTOR2I_MM(37.50, 18.863))
    dot_u1.SetRadius(pcbnew.FromMM(0.45))
    dot_u1.SetLayer(pcbnew.B_SilkS)
    dot_u1.SetWidth(pcbnew.FromMM(0.10))
    b.Add(dot_u1)

    txt_u1 = pcbnew.PCB_TEXT(b)
    txt_u1.SetText("1")
    txt_u1.SetPosition(pcbnew.VECTOR2I_MM(37.50, 20.30))
    txt_u1.SetTextSize(pcbnew.VECTOR2I_MM(1.0, 1.0))
    txt_u1.SetTextThickness(pcbnew.FromMM(0.18))
    txt_u1.SetLayer(pcbnew.B_SilkS)
    txt_u1.SetMirrored(True)
    txt_u1.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    txt_u1.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    b.Add(txt_u1)
    print("  Added U1 (PCA9555PW) Pin 1 dot and '1' at (37.50, 18.86) on B.SilkS")

    # J1 (2x10 socket on B.SilkS)
    dot_j1 = pcbnew.PCB_SHAPE(b)
    dot_j1.SetShape(pcbnew.SHAPE_T_CIRCLE)
    dot_j1.SetFilled(True)
    dot_j1.SetCenter(pcbnew.VECTOR2I_MM(11.20, 63.57))
    dot_j1.SetRadius(pcbnew.FromMM(0.45))
    dot_j1.SetLayer(pcbnew.B_SilkS)
    dot_j1.SetWidth(pcbnew.FromMM(0.10))
    b.Add(dot_j1)

    txt_j1 = pcbnew.PCB_TEXT(b)
    txt_j1.SetText("1")
    txt_j1.SetPosition(pcbnew.VECTOR2I_MM(11.20, 62.00))
    txt_j1.SetTextSize(pcbnew.VECTOR2I_MM(1.0, 1.0))
    txt_j1.SetTextThickness(pcbnew.FromMM(0.18))
    txt_j1.SetLayer(pcbnew.B_SilkS)
    txt_j1.SetMirrored(True)
    txt_j1.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    txt_j1.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    b.Add(txt_j1)
    print("  Added J1 Pin 1 dot and '1' at (11.20, 63.57) on B.SilkS")

    # Enforce 2 copper layers
    b.SetCopperLayerCount(2)
    b.Save(path)

    # In raw S-expression, remove the footprint circle inside U1 that touched pad 1 solder mask
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(
        r'\t\t\(fp_circle\s*\n\t\t\t\(center -3\.86 3\.58\)\s*\n\t\t\t\(end -3\.46 3\.58\)\s*\n\t\t\t\(stroke\s*\n\t\t\t\t\(width 0\.1\)\s*\n\t\t\t\t\(type solid\)\s*\n\t\t\t\)\s*\n\t\t\t\(fill (?:yes|none)\)\s*\n\t\t\t\(layer "B\.SilkS"\)\s*\n\t\t\t\(uuid "[^"]+"\)\s*\n\t\t\)',
        '',
        content
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Faceplate board updated and clean.")

def fix_encoder():
    path = "build/icio500/encoder_board.kicad_pcb"
    print("\nFixing encoder board pin 1 markings...")
    b = pcbnew.LoadBoard(path)
    
    to_remove = []
    for dwg in b.GetDrawings():
        if dwg.GetLayer() in [pcbnew.F_SilkS, pcbnew.B_SilkS]:
            if isinstance(dwg, pcbnew.PCB_TEXT) and dwg.GetText() in ["1", "A"]:
                to_remove.append(dwg)
            elif isinstance(dwg, pcbnew.PCB_SHAPE) and dwg.GetShapeStr() == "Circle":
                to_remove.append(dwg)
    for item in to_remove:
        b.Remove(item)

    # P1 (1x5 female header on B.SilkS)
    dot_p1 = pcbnew.PCB_SHAPE(b)
    dot_p1.SetShape(pcbnew.SHAPE_T_CIRCLE)
    dot_p1.SetFilled(True)
    dot_p1.SetCenter(pcbnew.VECTOR2I_MM(4.20, 2.50))
    dot_p1.SetRadius(pcbnew.FromMM(0.45))
    dot_p1.SetLayer(pcbnew.B_SilkS)
    dot_p1.SetWidth(pcbnew.FromMM(0.10))
    b.Add(dot_p1)

    txt_p1 = pcbnew.PCB_TEXT(b)
    txt_p1.SetText("1")
    txt_p1.SetPosition(pcbnew.VECTOR2I_MM(4.20, 3.80))
    txt_p1.SetTextSize(pcbnew.VECTOR2I_MM(1.0, 1.0))
    txt_p1.SetTextThickness(pcbnew.FromMM(0.18))
    txt_p1.SetLayer(pcbnew.B_SilkS)
    txt_p1.SetMirrored(True)
    txt_p1.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    txt_p1.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    b.Add(txt_p1)
    print("  Added P1 Pin 1 dot and '1' at (4.20, 2.50) on B.SilkS")

    # ENC1 (Rotary Encoder on F.SilkS)
    dot_enc = pcbnew.PCB_SHAPE(b)
    dot_enc.SetShape(pcbnew.SHAPE_T_CIRCLE)
    dot_enc.SetFilled(True)
    dot_enc.SetCenter(pcbnew.VECTOR2I_MM(11.00, 0.50))
    dot_enc.SetRadius(pcbnew.FromMM(0.45))
    dot_enc.SetLayer(pcbnew.F_SilkS)
    dot_enc.SetWidth(pcbnew.FromMM(0.10))
    b.Add(dot_enc)

    txt_enc = pcbnew.PCB_TEXT(b)
    txt_enc.SetText("A")
    txt_enc.SetPosition(pcbnew.VECTOR2I_MM(11.00, -0.70))
    txt_enc.SetTextSize(pcbnew.VECTOR2I_MM(1.0, 1.0))
    txt_enc.SetTextThickness(pcbnew.FromMM(0.18))
    txt_enc.SetLayer(pcbnew.F_SilkS)
    txt_enc.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    txt_enc.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    b.Add(txt_enc)
    print("  Added ENC1 Pin A dot and 'A' at (11.00, 0.50) on F.SilkS")

    b.SetCopperLayerCount(2)
    b.Save(path)
    print("Encoder board updated and clean.")

if __name__ == "__main__":
    fix_carrier()
    fix_faceplate()
    fix_encoder()
