import re

def main():
    board_file = 'build/icio500/icio500_3d_assembly.kicad_pcb'
    with open(board_file, 'r') as f:
        content = f.read()
        
    # We want to remove the old DUMMY footprint and insert a new one
    # The old DUMMY footprint starts with (footprint "MountingHole:MountingHole_3.2mm_M3" and ends just before the last )
    
    # Let's just strip everything after (footprint "MountingHole:MountingHole_3.2mm_M3"
    idx = content.find('(footprint "MountingHole:MountingHole_3.2mm_M3"')
    if idx != -1:
        content = content[:idx].rstrip() + '\n)'
        
    dummy_fp = """
  (footprint "MountingHole:MountingHole_3.2mm_M3" (layer "F.Cu")
    (attr exclude_from_pos_files exclude_from_bom)
    (fp_text reference "DUMMY" (at 0 0) (layer "F.SilkS")
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (model "build/icio500/panel_satellite.step"
      (offset (xyz 90 -11.55 166.675))
      (scale (xyz 1 1 1))
      (rotate (xyz -90 0 90))
    )
    (model "build/icio500/faceplate_front.step"
      (offset (xyz 75 -11.55 166.675))
      (scale (xyz 1 1 1))
      (rotate (xyz -90 0 90))
    )
  )
)
"""
    content = content.rstrip()
    if content.endswith(')'):
        content = content[:-1] + dummy_fp
    
    with open(board_file, 'w') as f:
        f.write(content)
    print("Injected fixed DUMMY footprint with correct 3D models offsets.")

if __name__ == '__main__':
    main()
