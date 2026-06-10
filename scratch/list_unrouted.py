import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
rc = board.GetConnectivity()
rc.Build(board)

netinfo = board.GetNetInfo()
for netcode, net in netinfo.NetsByNetcode().items():
    name = net.GetNetname()
    if name == "":
        continue
        
    pads = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() == netcode:
                pads.append(p)
                
    if len(pads) < 2:
        continue
        
    # Find connectivity groups
    unvisited = list(pads)
    groups = []
    while unvisited:
        p = unvisited.pop(0)
        connected_to_p = list(rc.GetConnectedPads(p))
        group = [p]
        i = 0
        while i < len(unvisited):
            other = unvisited[i]
            is_connected = False
            for c in connected_to_p:
                if c.GetParentFootprint().GetReference() == other.GetParentFootprint().GetReference() and c.GetName() == other.GetName():
                    is_connected = True
                    break
            if is_connected:
                group.append(other)
                unvisited.pop(i)
            else:
                i += 1
        groups.append(group)
        
    if len(groups) > 1:
        print(f"Net: {name} is split into {len(groups)} unconnected groups!")
        for idx, g in enumerate(groups):
            ref_pads = [f"{pad.GetParentFootprint().GetReference()}.{pad.GetName()}" for pad in g]
            print(f"  Group {idx+1}: {', '.join(ref_pads)}")
