import pcbnew
import re

BOARD_IN = 'build/icio500/icio500.kicad_pcb'

def add_track(board, start, end, layer, net, width=0.25):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(pcbnew.VECTOR2I(int(start[0]*1e6), int(start[1]*1e6)))
    track.SetEnd(pcbnew.VECTOR2I(int(end[0]*1e6), int(end[1]*1e6)))
    track.SetWidth(pcbnew.FromMM(width))
    track.SetLayer(layer)
    track.SetNetCode(net)
    board.Add(track)

def add_via(board, pos, net):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(int(pos[0]*1e6), int(pos[1]*1e6)))
    via.SetWidth(pcbnew.FromMM(0.6))
    via.SetDrill(pcbnew.FromMM(0.3))
    via.SetNetCode(net)
    board.Add(via)

def get_net_at(board, x, y):
    # Try pads first
    for fp in board.Footprints():
        for pad in fp.Pads():
            px = pad.GetPosition().x / 1e6
            py = pad.GetPosition().y / 1e6
            if abs(px - x) < 0.1 and abs(py - y) < 0.1:
                return pad.GetNetCode()
    # Try tracks
    for track in board.GetTracks():
        s = track.GetStart()
        sx, sy = s.x/1e6, s.y/1e6
        if abs(sx - x) < 0.1 and abs(sy - y) < 0.1:
            return track.GetNetCode()
        if hasattr(track, 'GetEnd'):
            e = track.GetEnd()
            ex, ey = e.x/1e6, e.y/1e6
            if abs(ex - x) < 0.1 and abs(ey - y) < 0.1:
                return track.GetNetCode()
    return 0

def main():
    board = pcbnew.LoadBoard(BOARD_IN)
    
    with open("final_diodes_drc.txt", "r") as f:
        content = f.read()
    
    blocks = content.split("[unconnected_items]: Missing connection between items")
    for block in blocks[1:]:
        lines = block.strip().split('\n')
        coords = []
        for line in lines:
            m = re.search(r"@\(([\d\.]+)\s*mm,\s*([\d\.]+)\s*mm\)", line)
            if m:
                coords.append((float(m.group(1)), float(m.group(2))))
        
        if len(coords) == 2:
            x1, y1 = coords[0]
            x2, y2 = coords[1]
            net = get_net_at(board, x1, y1)
            print(f"Routing {coords[0]} to {coords[1]} on net {net}")
            
            # Manhattan route
            mid_x = x2
            mid_y = y1
            add_track(board, (x1, y1), (mid_x, mid_y), pcbnew.F_Cu, net)
            add_track(board, (mid_x, mid_y), (x2, y2), pcbnew.F_Cu, net)
        elif len(coords) == 1:
            x1, y1 = coords[0]
            net = get_net_at(board, x1, y1)
            print(f"Adding via at {coords[0]} on net {net}")
            add_via(board, (x1, y1), net)

    # Re-run zone filler just to be sure vias connect to internal planes
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    
    pcbnew.SaveBoard(BOARD_IN, board)
    print("Done fixing diodes.")

if __name__ == '__main__':
    main()
