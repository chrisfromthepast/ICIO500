import pcbnew
import sys
import os

pcb_path = os.path.abspath(sys.argv[1])
dsn_path = os.path.abspath(sys.argv[2])

print(f"Loading board from {pcb_path}")
board = pcbnew.LoadBoard(pcb_path)
print(f"Exporting Specctra DSN to {dsn_path}")
pcbnew.ExportSpecctraDSN(board, dsn_path)
print("Export complete.")
