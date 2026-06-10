import pcbnew
import os

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

print("--- RUNNING PCB TESTS ---")

# 1. Test unrouted nets
rc = board.GetConnectivity()
rc.Build(board)
unrouted = rc.GetUnconnectedCount(False)
print(f"Test 1: Unrouted traces: {unrouted} (Should be 0 before manufacturing!)")

# 2. Test filled zones
zones_unfilled = 0
for zone in board.Zones():
    if not zone.IsFilled():
        zones_unfilled += 1
print(f"Test 2: Unfilled zones: {zones_unfilled} (Should be 0)")

print("\n--- GENERATING GERBERS ---")
plot_dir = 'build/icio500/gerbers/'
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

pctl = pcbnew.PLOT_CONTROLLER(board)
popt = pctl.GetPlotOptions()
popt.SetOutputDirectory(plot_dir)
popt.SetPlotFrameRef(False)
popt.SetSketchPadLineWidth(pcbnew.FromMM(0.1))
popt.SetAutoScale(False)
popt.SetScale(1)
popt.SetMirror(False)
popt.SetUseGerberAttributes(True)
popt.SetUseGerberProtelExtensions(False)
popt.SetUseAuxOrigin(True)
popt.SetSubtractMaskFromSilk(False)

layers = [
    ("F_Cu", pcbnew.F_Cu, "Top Copper"),
    ("In1_Cu", pcbnew.In1_Cu, "Inner1 Copper"),
    ("In2_Cu", pcbnew.In2_Cu, "Inner2 Copper"),
    ("B_Cu", pcbnew.B_Cu, "Bottom Copper"),
    ("F_SilkS", pcbnew.F_SilkS, "Top Silkscreen"),
    ("B_SilkS", pcbnew.B_SilkS, "Bottom Silkscreen"),
    ("F_Mask", pcbnew.F_Mask, "Top Solder Mask"),
    ("B_Mask", pcbnew.B_Mask, "Bottom Solder Mask"),
    ("Edge_Cuts", pcbnew.Edge_Cuts, "Board Outline")
]

for layer_info in layers:
    pctl.SetLayer(layer_info[1])
    pctl.OpenPlotfile(layer_info[0], pcbnew.PLOT_FORMAT_GERBER, layer_info[2])
    print(f"Plotted {layer_info[0]}")
    pctl.PlotLayer()

pctl.ClosePlot()

# Generate Drill files
drlwriter = pcbnew.EXCELLON_WRITER(board)
drlwriter.SetMapFileFormat(pcbnew.PLOT_FORMAT_PDF)

mirror = False
minimalHeader = False
offset = pcbnew.VECTOR2I(0,0)
mergeNPTH = False
drlwriter.SetOptions(mirror, minimalHeader, offset, mergeNPTH)
drlwriter.SetFormat(True)
drlwriter.CreateDrillandMapFilesSet(pctl.GetPlotOptions().GetOutputDirectory(), True, False)
print("Plotted Drill files")

print(f"\nSUCCESS! Gerbers and Drill files saved to {os.path.abspath(plot_dir)}")
