import os, sys
import pcbnew
import subprocess
from pathlib import Path
import shutil

base_dir = Path('build/icio500').absolute()
main_kicad = base_dir / 'icio500.kicad_pcb'
assembly_kicad = base_dir / 'icio500_3d_assembly.kicad_pcb'

# Copy fresh main board to assembly
shutil.copy2(main_kicad, assembly_kicad)

b = pcbnew.LoadBoard(str(assembly_kicad))

# Add DUMMY anchor
dummy = pcbnew.FOOTPRINT(b)
dummy.SetReference('DUMMY')
dummy.SetPosition(pcbnew.VECTOR2I(int(52.17 * 1e6), int(55.0 * 1e6)))

m1 = pcbnew.FP_3DMODEL()
dummy.Models().push_back(m1)
m2 = pcbnew.FP_3DMODEL()
dummy.Models().push_back(m2)

b.Add(dummy)
models = dummy.Models()

# 1. LOGIC FACEPLATE (Satellite)
m_logic = models[0]
m_logic.m_Filename = 'panel_satellite.step'
m_logic.m_Rotation.x = -90
m_logic.m_Rotation.y = 0
m_logic.m_Rotation.z = 90
m_logic.m_Show = True

# Satellite is drawn at X=100, Y=100 in its own PCB file.
# To bring its (100,100) point to the dummy origin, we must translate it.
# Trial and error shows Z shift makes it vertical. Let's shift it perfectly.
# After rotation Rz=90, the object's X axis points down (Y in board), object's Y axis points left (-X in board).
m_logic.m_Offset.x = 100.0  # Counteract the 100mm Y offset from panel_satellite.kicad_pcb
m_logic.m_Offset.y = -100.0 # Counteract the 100mm X offset
# It is placed at X=52.17. We want it flush against faceplate. 
# Let's say faceplate is at offset 0, and satellite is at offset +1.6
m_logic.m_Offset.z = 133.35 # Board height to stand it up. Wait, Z=133.35 was used before.

# 2. FRONT FACEPLATE
m_front = models[1]
m_front.m_Filename = 'faceplate_front.step'
m_front.m_Rotation.x = -90
m_front.m_Rotation.y = 0
m_front.m_Rotation.z = 90
m_front.m_Show = True

m_front.m_Offset.x = 0
m_front.m_Offset.y = 0
m_front.m_Offset.z = 133.35

# Move faceplate 1.6mm in front of satellite
# Wait, X offset in the footprint's local 3D coordinates?
# We will just export it and if it's wrong, we can iterate.

pcbnew.SaveBoard(str(assembly_kicad), b)
