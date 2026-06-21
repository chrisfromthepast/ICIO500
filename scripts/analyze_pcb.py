import pcbnew

board = pcbnew.LoadBoard(r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\icio500.kicad_pcb")

# Get track width statistics
widths = {}
via_count = 0
segment_count = 0
for t in board.GetTracks():
    cls = t.GetClass()
    if cls == "PCB_VIA":
        via_count += 1
    else:
        segment_count += 1
        w = t.GetWidth() / 1e6
        widths[w] = widths.get(w, 0) + 1

print("=== Track Width Distribution ===")
for w in sorted(widths.keys()):
    mil = w / 0.0254
    print(f"  {w:.4f} mm ({mil:.1f} mil): {widths[w]} tracks")

print(f"\nTotal segments: {segment_count}")
print(f"Total vias: {via_count}")

# Get footprint info
print("\n=== Footprints ===")
for fp in board.GetFootprints():
    ref = fp.GetReference()
    x = fp.GetPosition().x / 1e6
    y = fp.GetPosition().y / 1e6
    lib = fp.GetFPID().GetUniStringLibItemName()
    print(f"  {ref}: at ({x:.2f}, {y:.2f}) - {lib}")

# Check zones
zone_count = len(board.Zones())
print(f"\n=== Zones: {zone_count} ===")
for z in board.Zones():
    net = z.GetNetname()
    layer = board.GetLayerName(z.GetLayer())
    print(f"  Net={net}, Layer={layer}")

# Get net info
print("\n=== Nets ===")
netinfo = board.GetNetInfo()
for net in netinfo.NetsByName():
    name = net
    print(f"  {name}")

# Board dimensions
print("\n=== Board Edge.Cuts ===")
for d in board.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        bbox = d.GetBoundingBox()
        print(f"  Edge cut item found")
