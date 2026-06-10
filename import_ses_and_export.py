import pcbnew
import sys
import os
import subprocess

board_path = 'build/icio500/icio500.kicad_pcb'
ses_path = 'build/icio500/board.ses'
gerber_dir = 'build/icio500/gerbers'

print("Loading board...")
board = pcbnew.LoadBoard(board_path)

print(f"Importing {ses_path}...")
try:
    pcbnew.ImportSpecctraSES(board, ses_path)
except Exception as e:
    print(f"Failed to import SES: {e}")
    sys.exit(1)

# Check connectivity
print("Rebuilding connectivity...")
rc = board.GetConnectivity()
rc.Build(board)
unconnected = rc.GetUnconnectedCount(False)
print(f"Unconnected traces: {unconnected}")

print("Saving board...")
pcbnew.SaveBoard(board_path, board)

if unconnected > 0:
    print("Warning: Board is not fully routed!")

# Zone refill
print("Refilling zones...")
zf = pcbnew.ZONE_FILLER(board)
zf.Fill(board.Zones())
pcbnew.SaveBoard(board_path, board)

print("Exporting gerbers...")
os.makedirs(gerber_dir, exist_ok=True)
pctl = pcbnew.PLOT_CONTROLLER(board)
popt = pctl.GetPlotOptions()
popt.SetOutputDirectory(gerber_dir)
popt.SetPlotFrameRef(False)
popt.SetUseAuxOrigin(True)

layers = [
    ("F_Cu", pcbnew.F_Cu),
    ("In1_Cu", pcbnew.In1_Cu),
    ("In2_Cu", pcbnew.In2_Cu),
    ("B_Cu", pcbnew.B_Cu),
    ("F_SilkS", pcbnew.F_SilkS),
    ("B_SilkS", pcbnew.B_SilkS),
    ("F_Mask", pcbnew.F_Mask),
    ("B_Mask", pcbnew.B_Mask),
    ("Edge_Cuts", pcbnew.Edge_Cuts),
]

for name, layer_id in layers:
    pctl.SetLayer(layer_id)
    pctl.OpenPlotfile(name, pcbnew.PLOT_FORMAT_GERBER, name)
    pctl.PlotLayer()

pctl.ClosePlot()
print("Gerbers exported successfully!")
