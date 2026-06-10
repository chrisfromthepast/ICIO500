import pcbnew
import os

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)
output_dir = 'build/icio500/proof'
os.makedirs(output_dir, exist_ok=True)

pctl = pcbnew.PLOT_CONTROLLER(board)
popt = pctl.GetPlotOptions()
popt.SetOutputDirectory(output_dir)
popt.SetPlotFrameRef(False)
popt.SetUseAuxOrigin(True)
popt.SetScale(2.0)

pctl.SetLayer(pcbnew.In1_Cu)
pctl.OpenPlotfile("In1_Cu_Proof", pcbnew.PLOT_FORMAT_SVG, "Proof")
pctl.PlotLayer()
pctl.ClosePlot()

pctl.SetLayer(pcbnew.F_Cu)
pctl.OpenPlotfile("F_Cu_Proof", pcbnew.PLOT_FORMAT_SVG, "Proof")
pctl.PlotLayer()
pctl.ClosePlot()

print("Proof SVGs generated!")
