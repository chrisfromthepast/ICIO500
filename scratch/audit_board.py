"""
Audit every component on the board: reference, position, net connections, and what circuit block it belongs to.
"""
import pcbnew

BOARD_IN = 'build/icio500/icio500.kicad_pcb'

def main():
    board = pcbnew.LoadBoard(BOARD_IN)
    
    # Get board outline
    print("=== BOARD OUTLINE ===")
    for dwg in board.GetDrawings():
        if dwg.GetLayer() == pcbnew.Edge_Cuts:
            if hasattr(dwg, 'GetStart') and hasattr(dwg, 'GetEnd'):
                s = dwg.GetStart()
                e = dwg.GetEnd()
                print(f"  Edge: ({s.x/1e6:.1f}, {s.y/1e6:.1f}) -> ({e.x/1e6:.1f}, {e.y/1e6:.1f})")
    
    print("\n=== FOOTPRINTS ===")
    for fp in board.Footprints():
        ref = fp.GetReference()
        pos = fp.GetPosition()
        x, y = pos.x / 1e6, pos.y / 1e6
        rot = fp.GetOrientationDegrees()
        layer = fp.GetLayerName()
        
        # Get pad nets
        nets = set()
        for pad in fp.Pads():
            net_name = pad.GetNetname()
            if net_name:
                nets.add(net_name)
        
        print(f"  {ref:6s}  pos=({x:7.2f}, {y:7.2f})  rot={rot:6.1f}  layer={layer}  nets={sorted(nets)}")
    
    print("\n=== SILKSCREEN TEXT ===")
    for dwg in board.GetDrawings():
        if isinstance(dwg, pcbnew.PCB_TEXT):
            layer_name = board.GetLayerName(dwg.GetLayer())
            if 'Silk' in layer_name or 'silk' in layer_name or 'SilkS' in layer_name:
                pos = dwg.GetPosition()
                print(f"  Text: '{dwg.GetText()}' at ({pos.x/1e6:.1f}, {pos.y/1e6:.1f}) layer={layer_name}")
    
    print("\n=== TRACKS SUMMARY ===")
    layers = {}
    for track in board.GetTracks():
        ln = board.GetLayerName(track.GetLayer())
        layers[ln] = layers.get(ln, 0) + 1
    for ln, count in sorted(layers.items()):
        print(f"  {ln}: {count} segments")
    
    print("\n=== ZONES ===")
    for zone in board.Zones():
        ln = board.GetLayerName(zone.GetLayer())
        net = zone.GetNetname()
        print(f"  Zone on {ln}: net={net}")

if __name__ == '__main__':
    main()
