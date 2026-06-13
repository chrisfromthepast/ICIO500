from skip import Schematic, Symbol
import os

sch_path = os.path.join("build", "icio500", "icio500.kicad_sch")
sch = Schematic(sch_path)

print("Number of symbols before:", len(sch.symbol))

# Can we create a Symbol directly from an S-expression?
raw_sexp = '''(symbol (lib_id "Device:R") (in_bom yes) (on_board yes)
    (property "Reference" "R_TEST" (at 5.08 0 90)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "R" (at 0 0 90)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at -1.778 0 90)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "~" (at 0 0 0)
      (effects (font (size 1.27 1.27)) hide)
    )
  )
'''

import sexpdata

try:
    parsed = sexpdata.loads(raw_sexp)
    new_sym = Symbol(parsed, sch)
    sch.symbol.append(new_sym)
    print("Successfully created and appended symbol!")
except Exception as e:
    print("Error:", e)

# Test if we can save it
out_path = os.path.join("scratch", "test_out.kicad_sch")
try:
    sch.write(out_path)
    print("Successfully wrote schematic!")
    
    # Verify by loading
    sch2 = Schematic(out_path)
    print("Number of symbols after load:", len(sch2.symbol))
except Exception as e:
    print("Error saving:", e)
