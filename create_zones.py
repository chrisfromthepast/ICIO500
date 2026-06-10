import pcbnew
import os
import sys

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

def mm(v): return int(v * 1_000_000)

def make_zone_bounded(board, lyr, net_name, x0, y0, x1, y1):
    net = board.FindNet(net_name)
    if not net:
        print(f"Warning: Net {net_name} not found!")
        return None
            
    z = pcbnew.ZONE(board)
    z.SetLayer(lyr)
    z.SetNet(net)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    ch = pcbnew.SHAPE_LINE_CHAIN()
    ch.Append(mm(x0), mm(y0))
    ch.Append(mm(x1), mm(y0))
    ch.Append(mm(x1), mm(y1))
    ch.Append(mm(x0), mm(y1))
    ch.SetClosed(True)
    z.AddPolygon(ch)
    board.Add(z)
    return z

print("Creating zones...")
make_zone_bounded(board, pcbnew.In1_Cu, 'daisy_digital_gnd', 35, 10, 125, 185)
make_zone_bounded(board, pcbnew.In1_Cu, 'gnd', 125, 10, 240, 185)

print("Filling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

pcbnew.SaveBoard(pcb_path, board)
print("Done creating zones.")
sys.exit(0)
