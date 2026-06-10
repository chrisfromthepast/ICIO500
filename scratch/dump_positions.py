import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# Board outline
bbox = board.ComputeBoundingBox()
print(f"Board BBox: X={bbox.GetX()/1e6:.2f} Y={bbox.GetY()/1e6:.2f}  W={bbox.GetWidth()/1e6:.2f} H={bbox.GetHeight()/1e6:.2f}")

# Board edge cuts
print("\n--- Board Edge Cuts ---")
for d in board.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        print(f"  Shape on Edge.Cuts: start=({d.GetStart().x/1e6:.2f}, {d.GetStart().y/1e6:.2f}) end=({d.GetEnd().x/1e6:.2f}, {d.GetEnd().y/1e6:.2f})")

# All footprint positions
print("\n--- All Footprint Positions ---")
fps = []
for fp in board.GetFootprints():
    ref = fp.GetReference()
    pos = fp.GetPosition()
    x, y = pos.x / 1e6, pos.y / 1e6
    rot = fp.GetOrientationDegrees()
    fps.append((ref, x, y, rot))

fps.sort(key=lambda f: f[0])
for ref, x, y, rot in fps:
    print(f"  {ref:6s}  X={x:8.2f}  Y={y:8.2f}  Rot={rot:.1f}")

# Silkscreen drawings
print("\n--- Silkscreen Texts ---")
for d in board.GetDrawings():
    if d.GetLayer() == pcbnew.F_SilkS:
        try:
            txt = d.GetText()
            pos = d.GetPosition()
            print(f"  Text: '{txt}'  at ({pos.x/1e6:.2f}, {pos.y/1e6:.2f})")
        except:
            print(f"  Non-text drawing at ({d.GetStart().x/1e6:.2f}, {d.GetStart().y/1e6:.2f})")

# Track count and layer usage
print("\n--- Track Statistics ---")
layer_counts = {}
for t in board.GetTracks():
    lname = board.GetLayerName(t.GetLayer())
    layer_counts[lname] = layer_counts.get(lname, 0) + 1
for lname, cnt in sorted(layer_counts.items()):
    print(f"  {lname}: {cnt} tracks")

print(f"\nTotal tracks: {sum(layer_counts.values())}")
print(f"Total vias: {sum(1 for t in board.GetTracks() if t.GetClass() == 'PCB_VIA')}")
