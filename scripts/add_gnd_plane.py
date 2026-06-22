import pcbnew
import sys

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

gnd_net = None
for net in board.GetNetsByName().values():
    if net.GetNetname() == "gnd":
        gnd_net = net
        break

if not gnd_net:
    print("Could not find exact 'gnd' net.")
    sys.exit(1)

print(f"Found Ground net: {gnd_net.GetNetname()}")

bbox = board.GetBoardEdgesBoundingBox()
bbox.Inflate(pcbnew.FromMM(1))

zone = pcbnew.ZONE(board)
zone.SetLayer(pcbnew.In1_Cu)
zone.SetNetCode(gnd_net.GetNetCode())

poly = pcbnew.SHAPE_POLY_SET()
poly.NewOutline()
poly.Append(bbox.GetX(), bbox.GetY())
poly.Append(bbox.GetRight(), bbox.GetY())
poly.Append(bbox.GetRight(), bbox.GetBottom())
poly.Append(bbox.GetX(), bbox.GetBottom())

zone.AddPolygon(poly.Outline(0))
zone.SetIsFilled(True)
zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)

board.Add(zone)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

pcbnew.SaveBoard(board_path, board)
print("Successfully added GND plane to In1.Cu")
