import os

mod_dir = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\elec\footprints\ICIO500.pretty"
os.makedirs(mod_dir, exist_ok=True)

mod_path = os.path.join(mod_dir, "Neutrik_D_Series_PanelCutout.kicad_mod")

sexpr = """(footprint "Neutrik_D_Series_PanelCutout" (version 20240108) (generator pcbnew)
  (layer "F.Cu")
  (attr board_only exclude_from_pos_files exclude_from_bom)
  (fp_text reference "REF**" (at 0 -15 0) (layer "F.Silkscreen")
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_text value "Neutrik_D_Series_PanelCutout" (at 0 16 0) (layer "F.Fab")
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_circle (center 0 0) (end 12 0) (stroke (width 0.12) (type solid)) (layer "Dwgs.User"))
  (fp_circle (center 0 0) (end 13 0) (stroke (width 0.12) (type solid)) (layer "F.CrtYd"))
  
  (fp_circle (center 0 0) (end 12 0) (stroke (width 0.15) (type default)) (layer "Edge.Cuts"))
  
  (pad "1" thru_hole circle (at -9.5 -12) (size 6 6) (drill 3.2) (layers "*.Cu" "*.Mask"))
  (pad "2" thru_hole circle (at 9.5 12) (size 6 6) (drill 3.2) (layers "*.Cu" "*.Mask"))
)
"""

with open(mod_path, "w") as f:
    f.write(sexpr)

print(f"Created footprint at {mod_path}")
