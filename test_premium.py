import pcbnew
import os

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

# Fill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

# Test knockout text
text = pcbnew.PCB_TEXT(board)
text.SetText("PREMIUM AUDIO")
text.SetPosition(pcbnew.VECTOR2I(int(100*1e6), int(50*1e6)))
text.SetLayer(pcbnew.F_SilkS)
text.SetTextSize(pcbnew.VECTOR2I(int(3*1e6), int(3*1e6)))
text.SetTextThickness(int(0.5*1e6))
# Try to set knockout
if hasattr(text, 'SetIsKnockout'):
    text.SetIsKnockout(True)
board.Add(text)

# Add a solid shape behind it to test knockout
s = pcbnew.PCB_SHAPE(board)
s.SetShape(pcbnew.SHAPE_RECT)
s.SetStart(pcbnew.VECTOR2I(int(90*1e6), int(45*1e6)))
s.SetEnd(pcbnew.VECTOR2I(int(110*1e6), int(55*1e6)))
s.SetLayer(pcbnew.F_SilkS)
s.SetFilled(True)
board.Add(s)

pcbnew.SaveBoard(pcb_path, board)
print("Zones filled and knockout text tested.")
