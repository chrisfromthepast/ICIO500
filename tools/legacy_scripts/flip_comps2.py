import pcbnew
import sys

board = pcbnew.LoadBoard('build/icio500/panel_satellite.kicad_pcb')

flipped_count = 0
for fp in board.GetFootprints():
    ref = fp.GetReference()
    
    # We want to flip TSSOP(U), Connector(J), Resistors(R), Capacitors(C), Inductors(L, FB)
    if ref.startswith('U') or ref.startswith('J') or ref.startswith('R') or ref.startswith('C') or ref.startswith('L') or ref.startswith('FB'):
        if fp.GetLayer() == pcbnew.F_Cu:
            print(f"Flipping {ref}...")
            # Use Flip method
            fp.Flip(fp.GetPosition(), False)
            flipped_count += 1

if flipped_count > 0:
    pcbnew.SaveBoard('build/icio500/panel_satellite.kicad_pcb', board)
    print(f"Flipped {flipped_count} components.")
else:
    print("No components to flip.")
