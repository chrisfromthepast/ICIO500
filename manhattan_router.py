import pcbnew

def mm(val): return int(val * 1000000)

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

nets_to_skip = ['', 'gnd', 'chassis_gnd', 'v_plus_16v', 'v_minus_16v', 'v_plus_48v', 'daisy_digital_gnd', 'daisy_5v_power']

# Remove existing tracks from autorouter.py to clean up
old_tracks = list(board.GetTracks())
for t in old_tracks:
    # Only remove if it's on In1_Cu or In2_Cu to avoid breaking power routes
    if t.GetLayer() in (pcbnew.In1_Cu, pcbnew.In2_Cu):
        board.Remove(t)

print("Extracting pads...")
pads_info = []
for fp in board.GetFootprints():
    for p in fp.Pads():
        netname = str(p.GetNetname())
        if netname and netname not in nets_to_skip:
            pos = pcbnew.VECTOR2I(p.GetPosition())
            pads_info.append({
                'netname': netname,
                'netcode': p.GetNetCode(),
                'x': pos.x,
                'y': pos.y,
                'is_pth': p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH,
            })

nets = {}
for info in pads_info:
    nets.setdefault(info['netname'], []).append(info)

# Find unconnected nets (nets that don't have enough tracks)
rc = board.GetConnectivity()
rc.Build(board)
routed_nets = set([str(t.GetNetname()) for t in board.GetTracks() if t.GetNetname()])
unconnected_nets = [n for n in nets.keys() if n not in routed_nets]

print(f"Manhattan routing {len(unconnected_nets)} nets...")

W = mm(0.25)
VIA_W = mm(0.6)
VIA_D = mm(0.3)

def add_via(x, y, netcode):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(x, y))
    via.SetNetCode(netcode)
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetWidth(VIA_W)
    via.SetDrill(VIA_D)
    board.Add(via)

def add_track(x1, y1, x2, y2, layer, netcode):
    if x1 == x2 and y1 == y2: return
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(x1, y1))
    t.SetEnd(pcbnew.VECTOR2I(x2, y2))
    t.SetLayer(layer)
    t.SetNetCode(netcode)
    t.SetWidth(W)
    board.Add(t)

channel_x = mm(130)  # Start assigning vertical channels around x=130mm
x_step = mm(0.5)

for netname in unconnected_nets:
    if netname not in nets: continue
    
    net_pads = nets[netname]
    netcode = net_pads[0]['netcode']
    # Sort left to right
    net_pads.sort(key=lambda p: p['x'])
    
    for i in range(len(net_pads) - 1):
        p1 = net_pads[i]
        p2 = net_pads[i+1]
        
        x1, y1 = p1['x'], p1['y']
        x2, y2 = p2['x'], p2['y']
        
        # Add start and end vias if SMD
        if not p1['is_pth']: add_via(x1, y1, netcode)
        if not p2['is_pth']: add_via(x2, y2, netcode)
        
        # We need to route from (x1, y1) to (x2, y2).
        # Horizontal on In1_Cu, Vertical on In2_Cu
        
        if y1 == y2:
            # Straight horizontal
            add_track(x1, y1, x2, y2, pcbnew.In1_Cu, netcode)
        elif x1 == x2:
            # Straight vertical
            add_track(x1, y1, x2, y2, pcbnew.In2_Cu, netcode)
        else:
            # L-shape: Horizontal from x1 to channel_x, then vertical to y2, then horizontal to x2
            mid_x = channel_x
            channel_x += x_step # Allocate next channel
            
            # x1 -> mid_x (Horizontal on In1)
            add_track(x1, y1, mid_x, y1, pcbnew.In1_Cu, netcode)
            # Via at (mid_x, y1)
            add_via(mid_x, y1, netcode)
            
            # mid_x, y1 -> mid_x, y2 (Vertical on In2)
            add_track(mid_x, y1, mid_x, y2, pcbnew.In2_Cu, netcode)
            # Via at (mid_x, y2)
            add_via(mid_x, y2, netcode)
            
            # mid_x, y2 -> x2, y2 (Horizontal on In1)
            add_track(mid_x, y2, x2, y2, pcbnew.In1_Cu, netcode)

zf = pcbnew.ZONE_FILLER(board)
zf.Fill(board.Zones())
pcbnew.SaveBoard(board_path, board)
print("Manhattan Routing completed!")
