import pcbnew
import os

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

# Fill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

pcbnew.SaveBoard(pcb_path, board)
print("Zones filled.")
