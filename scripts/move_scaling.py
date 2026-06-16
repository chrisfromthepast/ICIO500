import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

def mm(v): return int(v * 1_000_000)

# Scaling block components (from ato build designator map)
scaling_refs = {'U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6'}

# Find the current bounding box center of the scaling block
fps = [fp for fp in board.GetFootprints() if fp.GetReference() in scaling_refs]

xs = [fp.GetPosition().x for fp in fps]
ys = [fp.GetPosition().y for fp in fps]
cur_cx = (min(xs) + max(xs)) // 2
cur_cy = (min(ys) + max(ys)) // 2

print(f"Scaling block current center: X={cur_cx/1e6:.2f} Y={cur_cy/1e6:.2f}")

# Target: between U4 (Y=70) and U2 (Y=105), aligned with them around X=167
# Place center at X=155, Y=87
target_cx = mm(155)
target_cy = mm(87)

dx = target_cx - cur_cx
dy = target_cy - cur_cy

print(f"Moving by dX={dx/1e6:.2f} dY={dy/1e6:.2f}")

for fp in fps:
    pos = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(pos.x + dx, pos.y + dy))
    print(f"  {fp.GetReference()} -> X={fp.GetPosition().x/1e6:.2f} Y={fp.GetPosition().y/1e6:.2f}")

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print("Done.")
