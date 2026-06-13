import re
import uuid

def fix_missing_units(schem_path):
    with open(schem_path, 'r', encoding='utf-8') as f:
        content = f.read()

    u2_uuid = str(uuid.uuid4())
    u3_uuid = str(uuid.uuid4())
    
    # Place them on a proper 1.27mm grid
    # 12.7 mm = 0.5 inches
    unit2_str = f"""
  (symbol
    (lib_id "Amplifier_Operational:TL072")
    (at 12.7 12.7 0)
    (unit 2)
    (body_style 1)
    (in_bom no)
    (on_board yes)
    (dnp no)
    (uuid "{u2_uuid}")
    (property "Reference" "U3" (at 12.7 12.7 0) (effects (font (size 1.27 1.27))))
    (property "Value" "TL072" (at 12.7 17.78 0) (effects (font (size 1.27 1.27))))
    (instances
      (project "generated_schematic"
        (path "/0cbb3bbb-8297-40d4-b3a9-e92b3d8d375c"
          (reference "U3")
          (unit 2)
        )
      )
    )
  )"""

    unit3_str = f"""
  (symbol
    (lib_id "Amplifier_Operational:TL072")
    (at 12.7 38.1 0)
    (unit 3)
    (body_style 1)
    (in_bom no)
    (on_board yes)
    (dnp no)
    (uuid "{u3_uuid}")
    (property "Reference" "U3" (at 12.7 38.1 0) (effects (font (size 1.27 1.27))))
    (property "Value" "TL072" (at 12.7 43.18 0) (effects (font (size 1.27 1.27))))
    (instances
      (project "generated_schematic"
        (path "/0cbb3bbb-8297-40d4-b3a9-e92b3d8d375c"
          (reference "U3")
          (unit 3)
        )
      )
    )
  )"""

    # Ground labels for unit 2 inputs (pins 5, 6). 
    # Let's just place PWR_FLAGs correctly on existing wires.
    # Where are the VCC, VEE, GND wires?
    # Let's attach PWR_FLAGs to them directly using global labels.
    # A PWR_FLAG symbol has its pin at (0 0) relative to its (at X Y).
    # A global_label has its connection point at (at X Y).
    # If they both have the same (at X Y), they connect!
    
    pwr_flag_vcc = f"""
  (symbol
    (lib_id "power:PWR_FLAG")
    (at 203.2 12.7 0)
    (unit 1)
    (body_style 1)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uuid.uuid4()}")
    (property "Reference" "#FLG0101" (at 203.2 12.7 0) (effects (font (size 1.27 1.27)) hide))
    (property "Value" "PWR_FLAG" (at 203.2 12.7 0) (effects (font (size 1.27 1.27)) hide))
  )
  (global_label "VCC" (shape input) (at 203.2 12.7 0) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify right)) (uuid "{uuid.uuid4()}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)))
"""
    pwr_flag_vee = f"""
  (symbol
    (lib_id "power:PWR_FLAG")
    (at 203.2 25.4 0)
    (unit 1)
    (body_style 1)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uuid.uuid4()}")
    (property "Reference" "#FLG0102" (at 203.2 25.4 0) (effects (font (size 1.27 1.27)) hide))
    (property "Value" "PWR_FLAG" (at 203.2 25.4 0) (effects (font (size 1.27 1.27)) hide))
  )
  (global_label "VEE" (shape input) (at 203.2 25.4 0) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify right)) (uuid "{uuid.uuid4()}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)))
"""
    pwr_flag_gnd = f"""
  (symbol
    (lib_id "power:PWR_FLAG")
    (at 203.2 38.1 0)
    (unit 1)
    (body_style 1)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uuid.uuid4()}")
    (property "Reference" "#FLG0103" (at 203.2 38.1 0) (effects (font (size 1.27 1.27)) hide))
    (property "Value" "PWR_FLAG" (at 203.2 38.1 0) (effects (font (size 1.27 1.27)) hide))
  )
  (global_label "GNDA" (shape input) (at 203.2 38.1 0) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify right)) (uuid "{uuid.uuid4()}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)))
"""

    idx = content.rfind('(sheet_instances')
    if idx == -1:
        idx = len(content) - 2

    # Insert everything
    injection = unit2_str + unit3_str + pwr_flag_vcc + pwr_flag_vee + pwr_flag_gnd
    new_content = content[:idx] + injection + '\n' + content[idx:]

    with open(schem_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == '__main__':
    fix_missing_units('build/icio500/generated_schematic.kicad_sch')
    print("Injected U3 units 2, 3 and PWR_FLAGs")
