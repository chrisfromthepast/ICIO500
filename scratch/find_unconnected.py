import pcbnew

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

rc = board.GetConnectivity()
rc.Build(board)

print("--- Unconnected Nets and Pads Details ---")

# Group all pads by net name
nets = {}
for fp in board.GetFootprints():
    for p in fp.Pads():
        netname = str(p.GetNetname())
        if netname:
            nets.setdefault(netname, []).append(p)

def get_pad_key(p):
    fp = p.GetParentFootprint()
    ref = fp.GetReference() if fp else "NoFP"
    return (ref, p.GetName())

for netname, pads in nets.items():
    unvisited = list(pads)
    components = []
    
    while unvisited:
        comp = []
        queue = [unvisited.pop(0)]
        comp.append(queue[0])
        
        while queue:
            curr = queue.pop(0)
            connected_items = rc.GetConnectedPads(curr)
            
            try:
                for item in connected_items:
                    item_key = get_pad_key(item)
                    # check if item is in unvisited
                    to_remove = None
                    for p in unvisited:
                        if get_pad_key(p) == item_key:
                            to_remove = p
                            break
                    if to_remove:
                        unvisited.remove(to_remove)
                        queue.append(to_remove)
                        comp.append(to_remove)
            except Exception as e:
                pass
        components.append(comp)
    
    if len(components) > 1:
        print(f"Net '{netname}' is disconnected into {len(components)} components:")
        for idx, comp in enumerate(components):
            pad_strs = []
            for p in comp:
                fp = p.GetParentFootprint()
                ref = fp.GetReference() if fp else "NoFP"
                pad_strs.append(f"{ref}-{p.GetName()} at ({p.GetPosition().x/1e6:.3f}, {p.GetPosition().y/1e6:.3f})")
            print(f"  Component {idx+1}: {', '.join(pad_strs)}")

