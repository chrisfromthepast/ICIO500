import pcbnew
import math

# 1. Update U6 on the main board
main_board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
u6 = main_board.FindFootprintByReference('U6')

# Change U6 to right-angle male header
# We'll just leave the footprint as is for the netlist, but change the 3D model and position!
# Wait, let's just change the footprint ID and reload it from the library!
# Actually, changing footprint ID via API is hard, let's just change the 3D model and position!
# For a right-angle header, let's just move U6 to X=52.17, Y=120.475, and rotate 180!
u6.SetPosition(pcbnew.VECTOR2I(int(52.17 * 1e6), int(120.475 * 1e6)))
u6.SetOrientationDegrees(180)
u6.SetLayer(pcbnew.F_Cu)

# Clear old 3D models and add the right-angle one
u6.Models().clear()
model = pcbnew.FP_3DMODEL()
model.m_Filename = '/Connector_PinHeader_2.54mm.3dshapes/PinHeader_2x10_P2.54mm_Horizontal.step'
u6.Add3DModel(model)

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', main_board)

# 2. Update J1 on the satellite board
sat_board = pcbnew.LoadBoard('build/icio500/panel_satellite.kicad_pcb')
j1 = sat_board.FindFootprintByReference('J1')
j1.SetPosition(pcbnew.VECTOR2I(int(119.05 * 1e6), int(175.0 * 1e6)))
j1.SetOrientationDegrees(0) # on B.Cu, 0 degrees means pointing right?
j1.SetLayer(pcbnew.B_Cu)

j1.Models().clear()
model2 = pcbnew.FP_3DMODEL()
model2.m_Filename = '/Connector_PinSocket_2.54mm.3dshapes/PinSocket_2x10_P2.54mm_Vertical_SMD.step'
j1.Add3DModel(model2)

pcbnew.SaveBoard('build/icio500/panel_satellite.kicad_pcb', sat_board)

print("Updated U6 and J1.")
