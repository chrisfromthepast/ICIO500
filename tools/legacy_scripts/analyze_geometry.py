import re

def get_board_extents(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        pcb = f.read()
    
    # Multi-line gr_line format
    edges = re.findall(
        r'\(gr_line\s*\n?\s*\(start\s+([\d.]+)\s+([\d.]+)\)\s*\n?\s*\(end\s+([\d.]+)\s+([\d.]+)\)',
        pcb
    )
    
    # Filter only Edge.Cuts lines by checking context
    # Actually just get all gr_line on Edge.Cuts
    blocks = re.findall(
        r'\(gr_line\s*\n\s*\(start\s+([\d.]+)\s+([\d.]+)\)\s*\n\s*\(end\s+([\d.]+)\s+([\d.]+)\).*?Edge\.Cuts',
        pcb, re.DOTALL
    )
    
    xs = []
    ys = []
    for b in blocks:
        xs.extend([float(b[0]), float(b[2])])
        ys.extend([float(b[1]), float(b[3])])
    
    return min(xs), max(xs), min(ys), max(ys) if xs else (0,0,0,0)


# Main board
print("=" * 60)
print("MAIN BOARD (icio500.kicad_pcb)")
print("=" * 60)
x1, x2, y1, y2 = get_board_extents('build/icio500/icio500.kicad_pcb')
print(f"  X: {x1:.3f} to {x2:.3f}  (width  = {x2-x1:.3f} mm)")
print(f"  Y: {y1:.3f} to {y2:.3f}  (height = {y2-y1:.3f} mm)")
print(f"  Left edge X = {x1}")

with open('build/icio500/icio500.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()
u6 = re.search(r'PinHeader_2x10.*?\(at\s+([\d.]+)\s+([\d.]+)\s+(\d+)\)', pcb, re.DOTALL)
if u6:
    print(f"  U6: X={u6.group(1)}, Y={u6.group(2)}, Rot={u6.group(3)}")
eda = re.search(r'EDA_306.*?\(at\s+([\d.]+)\s+([\d.]+)', pcb, re.DOTALL)
if eda:
    print(f"  EDA_306: X={eda.group(1)}, Y={eda.group(2)}")

# Satellite board
print()
print("=" * 60)
print("SATELLITE BOARD (panel_satellite.kicad_pcb)")
print("=" * 60)
x1s, x2s, y1s, y2s = get_board_extents('build/icio500/panel_satellite.kicad_pcb')
print(f"  X: {x1s:.3f} to {x2s:.3f}  (width  = {x2s-x1s:.3f} mm)")
print(f"  Y: {y1s:.3f} to {y2s:.3f}  (height = {y2s-y1s:.3f} mm)")
print(f"  Center: ({(x1s+x2s)/2:.3f}, {(y1s+y2s)/2:.3f})")

with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    sat = f.read()
# Find J1 - the socket that mates with U6
j1_fps = re.findall(r'\(footprint.*?Reference"\s+"(J\d+)".*?\(at\s+([\d.]+)\s+([\d.]+)', sat, re.DOTALL)
for ref, x, y in j1_fps:
    print(f"  {ref}: X={x}, Y={y}")

# Faceplate
print()
print("=" * 60)
print("FACEPLATE (faceplate_front.kicad_pcb)")
print("=" * 60)
x1f, x2f, y1f, y2f = get_board_extents('build/icio500/faceplate_front.kicad_pcb')
print(f"  X: {x1f:.3f} to {x2f:.3f}  (width  = {x2f-x1f:.3f} mm)")
print(f"  Y: {y1f:.3f} to {y2f:.3f}  (height = {y2f-y1f:.3f} mm)")
print(f"  Center: ({(x1f+x2f)/2:.3f}, {(y1f+y2f)/2:.3f})")

# STEP export info
print()
print("=" * 60)
print("STEP EXPORT INFO")
print("=" * 60)
print("When exported with --user-origin 0x0in:")
print(f"  Satellite STEP center ≈ board center = ({(x1s+x2s)/2:.3f}, {(y1s+y2s)/2:.3f})")
print(f"  Faceplate STEP center ≈ board center = ({(x1f+x2f)/2:.3f}, {(y1f+y2f)/2:.3f})")
print()
print("When exported WITHOUT --user-origin (default = bounding box center):")
print(f"  Satellite STEP origin = (0, 0, 0) maps to board center ({(x1s+x2s)/2:.3f}, {(y1s+y2s)/2:.3f})")
print(f"  Faceplate STEP origin = (0, 0, 0) maps to board center ({(x1f+x2f)/2:.3f}, {(y1f+y2f)/2:.3f})")

# Assembly DUMMY footprint
print()
print("=" * 60)
print("ASSEMBLY DUMMY FOOTPRINT")
print("=" * 60)
with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    asm = f.read()
dummy = re.search(r'footprint "DUMMY".*?\(at\s+([\d.]+)\s+([\d.]+)\)', asm, re.DOTALL)
if dummy:
    print(f"  DUMMY at: X={dummy.group(1)}, Y={dummy.group(2)}")

# Print existing offsets
models = re.findall(r'\(model "(.*?)"\s*\n\s*\(offset\s*\n\s*\(xyz\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)', asm)
for m in models:
    if 'DUMMY' in asm[asm.find(m[0])-200:asm.find(m[0])] or 'satellite' in m[0] or 'faceplate' in m[0]:
        print(f"  Model: {m[0]}")
        print(f"    Offset: ({m[1]}, {m[2]}, {m[3]})")
