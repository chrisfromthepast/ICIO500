import pcbnew
import subprocess
import os

board_path = 'build/icio500/icio500.kicad_pcb'
dsn_path = 'build/icio500/board.dsn'
ses_path = 'build/icio500/board.ses'

print("Loading board...")
board = pcbnew.LoadBoard(board_path)

print("Exporting DSN...")
pcbnew.ExportSpecctraDSN(board, dsn_path)

print("Running FreeRouting...")
# -mt 1 runs multiple passes, but let's just do a normal route
cmd = ["java", "-jar", "freerouting.jar", "-de", dsn_path, "-do", ses_path, "-mp", "10", "-as"]
subprocess.run(cmd, check=True)

print("Importing SES...")
board = pcbnew.LoadBoard(board_path) # reload fresh
pcbnew.ImportSpecctraSES(board, ses_path)

print("Filling Zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

print("Saving board...")
pcbnew.SaveBoard(board_path, board)

print("Checking unrouted count...")
rc = board.GetConnectivity()
rc.Build(board)
print("Unrouted count:", rc.GetUnconnectedCount(False))
