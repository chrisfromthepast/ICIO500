import pcbnew
import sys

board_path = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\icio500.kicad_pcb"

try:
    board = pcbnew.LoadBoard(board_path)
    
    # Add Ground Copper Pours (Zones) on F.Cu and B.Cu
    gnd_net = board.FindNet("GND")
    if not gnd_net:
        gnd_net = board.FindNet("gnd")
        
    if gnd_net:
        try:
            gnd_netcode = int(gnd_net.GetNetCode())
        except AttributeError:
            gnd_netcode = int(gnd_net)
        
        # KiCad 10 bounding box methods
        bbox = board.GetBoardEdgesBoundingBox()
        x = bbox.GetX()
        y = bbox.GetY()
        w = bbox.GetWidth()
        h = bbox.GetHeight()
        
        for layer in [pcbnew.F_Cu, pcbnew.B_Cu]:
            zone = pcbnew.ZONE(board)
            zone.SetLayer(layer)
            zone.SetNetCode(gnd_netcode)
            
            # Create boundary polygon covering the board
            poly = pcbnew.SHAPE_POLY_SET()
            poly.NewOutline()
            poly.Append(pcbnew.VECTOR2I(x - 5000000, y - 5000000))
            poly.Append(pcbnew.VECTOR2I(x + w + 5000000, y - 5000000))
            poly.Append(pcbnew.VECTOR2I(x + w + 5000000, y + h + 5000000))
            poly.Append(pcbnew.VECTOR2I(x - 5000000, y + h + 5000000))
            
            zone.SetOutline(poly)
            board.Add(zone)
            
        # Refill zones
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        print("Added and filled GND copper pours on Top and Bottom layers.")
    
    board.Save(board_path)
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
