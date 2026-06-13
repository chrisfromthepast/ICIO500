import os

def get_that1200_symbol():
    # U2 has (mirror x) in the schematic.
    # We want these absolute deltas (which means internal Y = -delta_Y):
    # Pin 1 (Ref): X=-12.7, Y=-7.62
    # Pin 2 (In-): X=7.62, Y=-2.54 
    # Pin 3 (In+): X=7.62, Y=2.54
    # Pin 4 (V-): X=0, Y=-7.62
    # Pin 5 (Sm): X=-2.54, Y=-7.62
    # Pin 6 (Cm): X=2.54, Y=7.62
    # Pin 7 (Out): X=-7.62, Y=0
    # Pin 8 (V+): X=1.27, Y=7.62
    
    return """
    (symbol "icio500:THAT1200" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at -10.16 6.35 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "icio500:THAT1200" (at 0 6.35 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "THAT1200_0_1"
        (polyline
          (pts
            (xy 5.08 5.08)
            (xy -5.08 0)
            (xy 5.08 -5.08)
            (xy 5.08 5.08)
          )
          (stroke (width 0.254) (type default))
          (fill (type background))
        )
      )
      (symbol "THAT1200_1_1"
        (pin input line (at 7.62 -2.54 180) (length 2.54)
            (name "-" (effects (font (size 1.27 1.27))))
            (number "2" (effects (font (size 1.27 1.27))))
        )
        (pin input line (at 7.62 2.54 180) (length 2.54)
            (name "+" (effects (font (size 1.27 1.27))))
            (number "3" (effects (font (size 1.27 1.27))))
        )
        (pin output line (at -7.62 0 0) (length 2.54)
            (name "Out" (effects (font (size 1.27 1.27))))
            (number "7" (effects (font (size 1.27 1.27))))
        )
        (pin power_in line (at 1.27 7.62 270) (length 2.54)
            (name "V+" (effects (font (size 1.27 1.27))))
            (number "8" (effects (font (size 1.27 1.27))))
        )
        (pin power_in line (at 0 -7.62 90) (length 2.54)
            (name "V-" (effects (font (size 1.27 1.27))))
            (number "4" (effects (font (size 1.27 1.27))))
        )
        (pin power_in line (at -12.7 -7.62 90) (length 2.54)
            (name "Ref" (effects (font (size 1.27 1.27))))
            (number "1" (effects (font (size 1.27 1.27))))
        )
        (pin passive line (at 2.54 7.62 270) (length 2.54)
            (name "Cm" (effects (font (size 1.27 1.27))))
            (number "6" (effects (font (size 1.27 1.27))))
        )
        (pin passive line (at -2.54 -7.62 90) (length 2.54)
            (name "Sm" (effects (font (size 1.27 1.27))))
            (number "5" (effects (font (size 1.27 1.27))))
        )
      )
    )
"""

def get_that1646_symbol():
    # U1 (THAT1646) has no mirror.
    # 2 (In+): X=-7.62, Y=-3.81
    # 3 (In-): X=-7.62, Y=3.81
    # 1 (Out+): X=12.70, Y=-5.08
    # 7 (Out-): X=12.70, Y=5.08
    # 8 (V+): X=0, Y=-7.62
    # 4 (V-): X=0, Y=7.62
    # 5 (GND): X=2.54, Y=7.62
    # 6 (Sense-): X=8.89, Y=11.43
    
    return """
    (symbol "icio500:THAT1646" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 6.35 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "icio500:THAT1646" (at 10.16 6.35 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "THAT1646_0_1"
        (polyline
          (pts
            (xy -5.08 5.08)
            (xy 5.08 0)
            (xy -5.08 -5.08)
            (xy -5.08 5.08)
          )
          (stroke (width 0.254) (type default))
          (fill (type background))
        )
      )
      (symbol "THAT1646_1_1"
        (pin input line (at -7.62 -3.81 0) (length 2.54)
            (name "+" (effects (font (size 1.27 1.27))))
            (number "2" (effects (font (size 1.27 1.27))))
        )
        (pin input line (at -7.62 3.81 0) (length 2.54)
            (name "-" (effects (font (size 1.27 1.27))))
            (number "3" (effects (font (size 1.27 1.27))))
        )
        (pin output line (at 12.70 -5.08 180) (length 2.54)
            (name "Out+" (effects (font (size 1.27 1.27))))
            (number "1" (effects (font (size 1.27 1.27))))
        )
        (pin output line (at 12.70 5.08 180) (length 2.54)
            (name "Out-" (effects (font (size 1.27 1.27))))
            (number "7" (effects (font (size 1.27 1.27))))
        )
        (pin power_in line (at 0 -7.62 270) (length 2.54)
            (name "V+" (effects (font (size 1.27 1.27))))
            (number "8" (effects (font (size 1.27 1.27))))
        )
        (pin power_in line (at 0 7.62 90) (length 2.54)
            (name "V-" (effects (font (size 1.27 1.27))))
            (number "4" (effects (font (size 1.27 1.27))))
        )
        (pin power_in line (at 2.54 7.62 90) (length 2.54)
            (name "GND" (effects (font (size 1.27 1.27))))
            (number "5" (effects (font (size 1.27 1.27))))
        )
        (pin passive line (at 8.89 11.43 90) (length 2.54)
            (name "Sen-" (effects (font (size 1.27 1.27))))
            (number "6" (effects (font (size 1.27 1.27))))
        )
      )
    )
"""

if __name__ == '__main__':
    # We write these to icio500.kicad_sym to be perfectly aligned with existing wires
    lib_content = f"""(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)
{get_that1200_symbol()}
{get_that1646_symbol()}
)
"""
    with open("build/icio500/icio500.kicad_sym", "w", encoding='utf-8') as f:
        f.write(lib_content)
    print("Updated icio500.kicad_sym with precise matched coordinates.")
