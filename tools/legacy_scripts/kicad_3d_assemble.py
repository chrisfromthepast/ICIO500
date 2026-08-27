import os
import sys
import pcbnew
import subprocess
from pathlib import Path

def main():
    base_dir = Path('build/icio500').absolute()
    assembly_kicad = base_dir / 'icio500_3d_assembly.kicad_pcb'
    
    if not assembly_kicad.exists():
        print(f"Error: {assembly_kicad} not found.")
        return

    b = pcbnew.LoadBoard(str(assembly_kicad))
    
    dummy = b.FindFootprintByReference('DUMMY')
    if not dummy:
        print("Creating DUMMY anchor footprint...")
        dummy = pcbnew.FOOTPRINT(b)
        dummy.SetReference('DUMMY')
        dummy.SetPosition(pcbnew.VECTOR2I(int(100.0 * 1e6), int(55.0 * 1e6)))
        
        # Add 2 3D models to it
        m1 = pcbnew.FP_3DMODEL()
        m1.m_Show = False
        dummy.Models().push_back(m1)
        m2 = pcbnew.FP_3DMODEL()
        m2.m_Show = False
        dummy.Models().push_back(m2)
        
        b.Add(dummy)

    models = dummy.Models()
    
    # 1. LOGIC FACEPLATE
    # m_Offset is applied in absolute coordinates AFTER rotation.
    # The models are attached to DUMMY, so (0,0,0) offset means the origin is at DUMMY.
    m_logic = models[0]
    m_logic.m_Filename = 'panel_satellite.step'
    m_logic.m_Rotation.x = -90
    m_logic.m_Rotation.y = 0
    m_logic.m_Rotation.z = 90
    
    # Place logic board right on the DUMMY footprint (Offset=0).
    # Shift Z by 133.45 to make it stand up vertically on the board.
    m_logic.m_Offset.x = 0
    m_logic.m_Offset.y = 0
    m_logic.m_Offset.z = 133.45
    m_logic.m_Show = True

    # 2. FRONT FACEPLATE
    m_front = models[1]
    m_front.m_Filename = 'faceplate_front.step'
    m_front.m_Rotation.x = -90
    m_front.m_Rotation.y = 0
    m_front.m_Rotation.z = 90
    
    # Shift -11mm in absolute X to place it in front of the logic board
    m_front.m_Offset.x = -11.0
    m_front.m_Offset.y = 0
    m_front.m_Offset.z = 133.45
    m_front.m_Show = True

    pcbnew.SaveBoard(str(assembly_kicad), b)
    print(f"Saved modified 3D assembly to {assembly_kicad}")

    # Export to STEP
    step_output = str(base_dir / 'icio500_3d_assembly.step')
    kicad_cli = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
    
    print(f"Exporting STEP file to {step_output}...")
    result = subprocess.run([
        kicad_cli, 'pcb', 'export', 'step',
        '--force',
        '--subst-models',
        str(assembly_kicad)
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error exporting STEP:\n{result.stderr}")
    else:
        print("STEP export successful!")

if __name__ == "__main__":
    main()
