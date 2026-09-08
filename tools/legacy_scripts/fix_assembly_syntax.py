import shutil

shutil.copy('build/icio500/icio500.kicad_pcb', 'build/icio500/icio500_3d_assembly.kicad_pcb')

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

dummy = """
  (footprint "DUMMY"
    (layer "F.Cu")
    (at 52.17 112.15)
    (attr exclude_from_pos_files exclude_from_bom)
    (model "./panel_satellite.step"
      (offset
        (xyz 0.8 166.675 -119.05)
      )
      (scale
        (xyz 1 1 1)
      )
      (rotate
        (xyz 0 -90 0)
      )
    )
    (model "./faceplate_front.step"
      (offset
        (xyz -0.8 66.675 -19.05)
      )
      (scale
        (xyz 1 1 1)
      )
      (rotate
        (xyz 0 -90 0)
      )
    )
  )
"""

pos = pcb.rfind('(embedded_fonts no)')
pcb = pcb[:pos] + dummy + pcb[pos:]

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)
print("Fixed assembly file syntax")
