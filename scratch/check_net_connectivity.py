import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
rc = board.GetConnectivity()
rc.Build(board)

# Group pads by net
net_pads = {}
for fp in board.GetFootprints():
    for pad in fp.Pads():
        netname = str(pad.GetNetname())
        if netname:
            net_pads.setdefault(netname, []).append(pad)

# Check each net
for netname, pads in net_pads.items():
    if len(pads) < 2:
        continue
        
    # Cluster pads into connected groups
    unvisited = list(pads)
    groups = []
    while unvisited:
        p = unvisited.pop(0)
        group = [p]
        connected_to_p = list(rc.GetConnectedPads(p))
        
        # Helper to check if a pad matches one in the list of connected pads
        def is_connected(pad_obj):
            for c in connected_to_p:
                if c.GetParentFootprint().GetReference() == pad_obj.GetParentFootprint().GetReference() and c.GetName() == pad_obj.GetName():
                    return True
            return False
            
        i = 0
        while i < len(unvisited):
            other = unvisited[i]
            if is_connected(other):
                group.append(other)
                unvisited.pop(i)
            else:
                i += 1
        groups.append(group)
        
    if len(groups) > 1:
        print(f"Net '{netname}' is split into {len(groups)} unconnected groups:")
        for idx, g in enumerate(groups):
            ref_pads = [f"{pad.GetParentFootprint().GetReference()}.{pad.GetName()}" for pad in g]
            print(f"  Group {idx+1}: {', '.join(ref_pads)}")
