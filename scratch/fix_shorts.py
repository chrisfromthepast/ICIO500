import pcbnew
import math

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# Deltas we will apply to components
moves = {
    'R3': (0, 3), 'R4': (0, 3), 'R5': (0, 2), 'R6': (0, 2),
    'C17': (0, 5), 'C18': (0, 3),
    'D3': (2, 0), 'D4': (2, 0), 'D5': (2, 0), 'D6': (2, 0)
}

# 1. Read original positions
pad_nets = {}
for fp in board.Footprints():
    ref = fp.GetReference()
    for pad in fp.Pads():
        nc = pad.GetNetCode()
        nn = pad.GetNetname()
        if nc == 0 or not nn: continue
        pos = pad.GetPosition()
        x, y = pos.x/1e6, pos.y/1e6
        # Apply delta if this component is moving
        if ref in moves:
            dx, dy = moves[ref]
            x += dx
            y += dy
        
        if nc not in pad_nets:
            pad_nets[nc] = {'name': nn, 'pads': []}
            
        # Deduplicate
        is_dup = False
        for e in pad_nets[nc]['pads']:
            if math.sqrt((x-e[0])**2 + (y-e[1])**2) < 0.05:
                is_dup = True
                break
        if not is_dup:
            pad_nets[nc]['pads'].append((x,y))

# 2. Delete tracks
for t in list(board.GetTracks()):
    board.Remove(t)

# 3. Move components
for ref, (dx, dy) in moves.items():
    fp = board.FindFootprintByReference(ref)
    if fp:
        pos = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(int(pos.x + dx*1e6), int(pos.y + dy*1e6)))

# 4. Route
def dist(a, b): return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def build_mst(points):
    if len(points) <= 1: return []
    n = len(points)
    in_tree = [False]*n
    in_tree[0] = True
    edges = []
    for _ in range(n-1):
        bd, bi, bj = float('inf'), -1, -1
        for i in range(n):
            if not in_tree[i]: continue
            for j in range(n):
                if in_tree[j]: continue
                d = dist(points[i], points[j])
                if d < bd: bd, bi, bj = d, i, j
        if bj >= 0:
            in_tree[bj] = True
            edges.append((bi, bj))
    return edges

power_nets = {'v_plus', 'v_minus', 'gnd', 'v_plus_16v', 'v_minus_16v',
              'daisy_5v_power', 'daisy_digital_gnd', 'chassis_gnd'}
FCu, BCu = pcbnew.F_Cu, pcbnew.B_Cu

def add_track(start, end, layer, nc, width):
    if abs(start[0]-end[0]) < 0.001 and abs(start[1]-end[1]) < 0.001: return
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(int(start[0]*1e6), int(start[1]*1e6)))
    t.SetEnd(pcbnew.VECTOR2I(int(end[0]*1e6), int(end[1]*1e6)))
    t.SetWidth(pcbnew.FromMM(width))
    t.SetLayer(layer)
    t.SetNetCode(nc)
    board.Add(t)

def add_via(pos, nc):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(int(pos[0]*1e6), int(pos[1]*1e6)))
    v.SetWidth(pcbnew.FromMM(0.6))
    v.SetDrill(pcbnew.FromMM(0.3))
    v.SetNetCode(nc)
    board.Add(v)

power_list = [(nc, info) for nc, info in pad_nets.items() if len(info['pads']) >= 2 and info['name'] in power_nets]
signal_list = [(nc, info) for nc, info in pad_nets.items() if len(info['pads']) >= 2 and info['name'] not in power_nets]

total = 0
for nc, info in power_list:
    edges = build_mst(info['pads'])
    for i, j in edges:
        p1, p2 = info['pads'][i], info['pads'][j]
        mid = (p2[0], p1[1])
        add_track(p1, mid, FCu, nc, 0.4)
        add_track(mid, p2, FCu, nc, 0.4)
        total += 1

for idx, (nc, info) in enumerate(signal_list):
    layer = FCu if idx % 2 == 0 else BCu
    edges = build_mst(info['pads'])
    for i, j in edges:
        p1, p2 = info['pads'][i], info['pads'][j]
        if layer == BCu:
            add_via(p1, nc)
            add_via(p2, nc)
        mid = (p2[0], p1[1])
        add_track(p1, mid, layer, nc, 0.25)
        add_track(mid, p2, layer, nc, 0.25)
        total += 1

# Silkscreen
for text, x, y in [('POWER', 155, 142), ('INPUT', 165, 113), ('SCALING', 145, 83), ('DRIVER', 135, 58), ('DAISY SEED', 75, 78)]:
    txt = pcbnew.PCB_TEXT(board)
    txt.SetText(text)
    txt.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))
    txt.SetTextSize(pcbnew.VECTOR2I(int(1.0*1e6), int(1.0*1e6)))
    txt.SetTextThickness(int(0.15*1e6))
    txt.SetLayer(pcbnew.F_SilkS)
    board.Add(txt)

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print(f'Routed {total} MST edges')
