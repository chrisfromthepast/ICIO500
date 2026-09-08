import pcbnew
import math

b = pcbnew.LoadBoard('build/icio500/icio500_3d_assembly.kicad_pcb')

dummy = b.FindFootprintByReference('DUMMY')
if dummy:
    b.Remove(dummy)

dummy = pcbnew.FOOTPRINT(b)
dummy.SetReference('DUMMY')
# Place dummy exactly at the front edge, centered.
dummy.SetPosition(pcbnew.VECTOR2I(int(52.17 * 1e6), int(112.15 * 1e6)))

# 1. Faceplate
m_front = pcbnew.FP_3DMODEL()
m_front.m_Filename = './faceplate_front.step'
m_front.m_Show = True
# We want faceplate:
# +X_orig -> +Y_board
# +Y_orig -> +Z_board
# +Z_orig -> +X_board
# From standard (X,Y,Z):
# Rx = 90 -> (X, -Z, Y)
# Rz = 90 -> (Z, X, Y) -- Wait. Rz=90 maps (x,y,z) to (-y, x, z).
# Let's just use Euler angles.
# Rz=90, Ry=0, Rx=90.
# V' = Rz * Rx * V
# Rx(90): (x, -z, y)
# Rz(90) on (x, -z, y) -> (-(-z), x, y) = (z, x, y)
# We want X_board = Z_orig, Y_board = X_orig, Z_board = Y_orig.
# But wait, +Z_orig goes OUT of the faceplate. We want +Z_orig to point -X_board (forward).
# So X_board = -Z_orig.
# Let's try Rz=-90, Rx=90
# Rx(90): (x, -z, y)
# Rz(-90) on (x, -z, y) -> (-z, -x, y). So X_board = -Z_orig, Y_board = -X_orig.
# We want Y_board = +X_orig.
# So Rz=90, Rx=-90
# Rx(-90): (x, z, -y)
# Rz(90) on (x, z, -y) -> (-z, x, -y). So X_board = -Z_orig, Y_board = X_orig, Z_board = -Y_orig.
# Z_board = -Y_orig means it points DOWN.
# Let's use Rz=90, Ry=90, Rx=0?
# Ry(90): (z, y, -x)
# Rz(90) on (z, y, -x) -> (-y, z, -x). 
# Let's just set the rotation directly:
m_front.m_Rotation.x = 90.0
m_front.m_Rotation.y = 0.0
m_front.m_Rotation.z = 90.0

# In KiCad python API, m_Offset is applied AFTER rotation.
# With Rx=90, Rz=90: V' = (z, x, y). 
# Origin of faceplate (0,0) maps to (0, 0, 0).
# We want center of faceplate (x=19.05) to be at Y_board=0. So Y_board = x + offset_y -> offset_y = -19.05
# We want bottom of faceplate (y=133.35) to be at Z_board = -66.675. So Z_board = y + offset_z -> offset_z = -66.675
# Faceplate front is Z_orig=0. X_board = z + offset_x. We want it at X_board = -1.6 (flush). So offset_x = -1.6
m_front.m_Offset.x = -1.6
m_front.m_Offset.y = -19.05
m_front.m_Offset.z = -66.675
dummy.Models().push_back(m_front)

# 2. Satellite
m_sat = pcbnew.FP_3DMODEL()
m_sat.m_Filename = './panel_satellite.step'
m_sat.m_Show = True
m_sat.m_Rotation.x = 90.0
m_sat.m_Rotation.y = 0.0
m_sat.m_Rotation.z = 90.0

# Satellite original X = 100 to 138.1, Y = 100 to 233.35.
# X_board = z + offset_x. We want it flush to faceplate (X_board = 0). So offset_x = 0
# Y_board = x + offset_y. We want x=119.05 to map to Y_board=0. So offset_y = -119.05
# Z_board = y + offset_z. We want y=100+133.35/2 = 166.675 to map to Z_board=0. So offset_z = -166.675
m_sat.m_Offset.x = 0.0
m_sat.m_Offset.y = -119.05
m_sat.m_Offset.z = -166.675
dummy.Models().push_back(m_sat)

b.Add(dummy)
pcbnew.SaveBoard('build/icio500/icio500_3d_assembly.kicad_pcb', b)
