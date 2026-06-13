import pcbnew
import json

def analyze_area(board_path):
    board = pcbnew.LoadBoard(board_path)
    
    # We want to route:
    # 1. C26(Pad 2) to GND track at (170, 92.225)
    # 2. R3(Pad 1) to U2(Pad 7)
    
    c26 = board.FindFootprintByReference("C26")
    r3 = board.FindFootprintByReference("R3")
    u2 = board.FindFootprintByReference("U2")
    
    c26_p2 = c26.FindPadByNumber("2").GetPosition() if c26 else None
    r3_p1 = r3.FindPadByNumber("1").GetPosition() if r3 else None
    u2_p7 = u2.FindPadByNumber("7").GetPosition() if u2 else None
    
    print(f"C26 Pad 2: {c26_p2.x / 1e6}, {c26_p2.y / 1e6}")
    print(f"R3 Pad 1: {r3_p1.x / 1e6}, {r3_p1.y / 1e6}")
    print(f"U2 Pad 7: {u2_p7.x / 1e6}, {u2_p7.y / 1e6}")
    
    obstacles = []
    
    for pad in board.GetPads():
        pos = pad.GetPosition()
        x, y = pos.x / 1e6, pos.y / 1e6
        if 150 < x < 175 and 80 < y < 115:
            obstacles.append({"type": "pad", "net": pad.GetNetname(), "x": x, "y": y})
            
    for track in board.GetTracks():
        start = track.GetStart()
        end = track.GetEnd()
        sx, sy = start.x / 1e6, start.y / 1e6
        ex, ey = end.x / 1e6, end.y / 1e6
        if (150 < sx < 175 and 80 < sy < 115) or (150 < ex < 175 and 80 < ey < 115):
            obstacles.append({"type": "track", "net": track.GetNetname(), "sx": sx, "sy": sy, "ex": ex, "ey": ey, "layer": track.GetLayerName()})
            
    with open('build/icio500/routing_env.json', 'w') as f:
        json.dump(obstacles, f, indent=2)

if __name__ == '__main__':
    analyze_area('build/icio500/icio500.kicad_pcb')
