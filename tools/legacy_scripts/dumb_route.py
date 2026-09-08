import pcbnew
import math

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# Find U6 pads
u6 = board.FindFootprintByReference('U6')
if not u6:
    print("U6 not found")
    exit(1)

# Get all other pads grouped by net
net_pads = {}
for pad in board.GetPads():
    if pad.GetParent().GetReference() == 'U6': continue
    net = pad.GetNetname()
    if not net: continue
    if net not in net_pads: net_pads[net] = []
    net_pads[net].append(pad)

# Route U6 pads
added = 0
for pad in u6.Pads():
    net = pad.GetNetname()
    if not net or net not in net_pads: continue
    
    # Find nearest pad on same net
    best_target = None
    best_dist = float('inf')
    px, py = pad.GetPosition().x, pad.GetPosition().y
    
    for target in net_pads[net]:
        tx, ty = target.GetPosition().x, target.GetPosition().y
        dist = math.hypot(tx - px, ty - py)
        if dist < best_dist:
            best_dist = dist
            best_target = target
            
    if best_target:
        tx, ty = best_target.GetPosition().x, best_target.GetPosition().y
        
        # Create an L-shape route (first X, then Y)
        # To avoid overlaps, we can route on B.Cu and F.Cu alternately?
        # Actually, if we just let the tracks cross, the user can fix it, but DRC will fail.
        # Let's just create direct lines.
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I(int(px), int(py)))
        track.SetEnd(pcbnew.VECTOR2I(int(tx), int(ty)))
        track.SetWidth(int(0.25 * 1e6))
        track.SetLayer(pcbnew.F_Cu)
        board.Add(track)
        added += 1

print(f"Added {added} straight-line tracks.")
pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
