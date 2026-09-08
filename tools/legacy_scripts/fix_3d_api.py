import pcbnew
import math

b = pcbnew.LoadBoard('build/icio500/icio500_3d_assembly.kicad_pcb')

# Create DUMMY footprint
dummy = pcbnew.FOOTPRINT(b)
dummy.SetReference('DUMMY')
dummy.SetPosition(pcbnew.VECTOR2I(int(52.17 * 1e6), int(112.15 * 1e6)))

# Add faceplate
m_front = pcbnew.FP_3DMODEL()
m_front.m_Filename = './faceplate_front.step'
m_front.m_Show = True
m_front.m_Rotation.x = 0.0
m_front.m_Rotation.y = -90.0
m_front.m_Rotation.z = 0.0
m_front.m_Offset.x = -1.6
m_front.m_Offset.y = -66.675
m_front.m_Offset.z = -19.05
dummy.Models().push_back(m_front)

# Add satellite
m_sat = pcbnew.FP_3DMODEL()
m_sat.m_Filename = './panel_satellite.step'
m_sat.m_Show = True
m_sat.m_Rotation.x = 0.0
m_sat.m_Rotation.y = -90.0
m_sat.m_Rotation.z = 0.0
m_sat.m_Offset.x = 0.0
m_sat.m_Offset.y = -166.675
m_sat.m_Offset.z = -119.05
dummy.Models().push_back(m_sat)

b.Add(dummy)
pcbnew.SaveBoard('build/icio500/icio500_3d_assembly.kicad_pcb', b)
print("Saved cleanly using pcbnew API")
