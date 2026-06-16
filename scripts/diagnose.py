import pcbnew

PCB_PATH = 'build/icio500/icio500.kicad_pcb'
b = pcbnew.LoadBoard(PCB_PATH)

print("--- Parts near or outside edges ---")
# Board edges (approx)
MIN_X, MAX_X = 50.65 * 1e6, 195.0 * 1e6
MIN_Y, MAX_Y = 55.0 * 1e6, 160.0 * 1e6

for fp in b.GetFootprints():
    bb = fp.GetBoundingBox()
    ref = fp.GetReference()
    
    # Exception for Edge Connector parts
    if ref in ['J1', 'D1', 'D2']:
        if bb.GetBottom() > 160 * 1e6 or bb.GetTop() < 55 * 1e6 or bb.GetRight() > 203 * 1e6:
            print(f"{ref} is outside: Top={bb.GetTop()/1e6}, Bot={bb.GetBottom()/1e6}, L={bb.GetLeft()/1e6}, R={bb.GetRight()/1e6}")
    else:
        if bb.GetLeft() < MIN_X or bb.GetRight() > MAX_X or bb.GetTop() < MIN_Y or bb.GetBottom() > MAX_Y:
            print(f"{ref} is outside: Top={bb.GetTop()/1e6}, Bot={bb.GetBottom()/1e6}, L={bb.GetLeft()/1e6}, R={bb.GetRight()/1e6}")

print("\n--- Silkscreen Shapes/Texts ---")
for d in b.GetDrawings():
    layer = b.GetLayerName(d.GetLayer())
    if layer == 'F.Silkscreen' or layer == 'Dwgs.User':
        if type(d) is pcbnew.PCB_TEXT:
            print(f"[{layer}] TEXT: {d.GetText()}")
        elif type(d) is pcbnew.PCB_SHAPE:
            # We don't need all, just count them
            pass
