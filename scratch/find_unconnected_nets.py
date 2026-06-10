import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# 1. Group pads by net
net_pads = {}
for fp in board.GetFootprints():
    for pad in fp.Pads():
        netname = str(pad.GetNetname())
        if netname:
            net_pads.setdefault(netname, []).append(pad)

# 2. Build connection graph from tracks
adj = {}
def add_edge(p1, p2):
    adj.setdefault(p1, set()).add(p2)
    adj.setdefault(p2, set()).add(p1)

for t in board.GetTracks():
    p1 = (t.GetStart().x, t.GetStart().y)
    p2 = (t.GetEnd().x, t.GetEnd().y)
    add_edge(p1, p2)

# 3. For each net, check if all pads are connected
for netname, pads in net_pads.items():
    if len(pads) < 2:
        continue
    
    pad_positions = [(p.GetPosition().x, p.GetPosition().y) for p in pads]
    
    # BFS from first pad position
    # Find closest point in adj to start pad
    start = pad_positions[0]
    closest_start = None
    min_dist = float('inf')
    for pt in adj.keys():
        dx = pt[0] - start[0]
        dy = pt[1] - start[1]
        dist = dx*dx + dy*dy
        if dist < min_dist:
            min_dist = dist
            closest_start = pt
            
    # If no tracks in net, it is unconnected
    if closest_start is None or min_dist > 1000000000000: # 1mm tolerance squared
        print(f"Net '{netname}' is completely unconnected!")
        continue
        
    visited = set()
    queue = [closest_start]
    visited.add(closest_start)
    
    while queue:
        curr = queue.pop(0)
        if curr in adj:
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
    # Check if all pads are connected to this cluster
    unconnected_pads = []
    for p, pos in zip(pads, pad_positions):
        connected = False
        for v in visited:
            dx = v[0] - pos[0]
            dy = v[1] - pos[1]
            if dx*dx + dy*dy < 1000000000000: # 1mm tolerance squared
                connected = True
                break
        if not connected:
            unconnected_pads.append(f"{p.GetParentFootprint().GetReference()}.{p.GetName()}")
            
    if unconnected_pads:
        print(f"Net '{netname}' is not fully connected!")
        print(f"  Unconnected pads: {', '.join(unconnected_pads)}")
