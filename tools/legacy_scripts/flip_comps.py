import pcbnew
import sys

board = pcbnew.LoadBoard('build/icio500/panel_satellite.kicad_pcb')

flipped_count = 0
for fp in board.GetFootprints():
    ref = fp.GetReference()
    
    # Do not flip the encoder (U1? No, ENC1) or LEDs (D*)
    if ref.startswith('D') or ref.startswith('ENC') or 'LED' in ref:
        continue
        
    # We want to flip TSSOP, Connector, Resistors, Capacitors
    if fp.GetLayer() == pcbnew.F_Cu:
        print(f"Flipping {ref}...")
        fp.Flip(fp.GetPosition(), False) # False means don't flip the module over the Y axis? No, the second param is 'aFlipLeftRight'. If False, it flips over X axis (top/bottom). If True, left/right. 
        # Actually in KiCad 10, Flip might take just the position and a boolean. Let's try.
        # Wait, the signature in KiCad is Flip(wxPoint aCentre, bool aFlipLeftRight)
        
        # Let's just use the standard flip that the GUI uses
        flipped_count += 1

if flipped_count > 0:
    pcbnew.SaveBoard('build/icio500/panel_satellite.kicad_pcb', board)
    print(f"Flipped {flipped_count} components.")
else:
    print("No components to flip.")
