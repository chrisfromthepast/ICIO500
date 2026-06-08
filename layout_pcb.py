"""
layout_pcb.py  –  ICIO500 placement pass
=========================================
Places components only. No tracks, no zones.
"""

import pcbnew, os

def mm(v):
    return int(v * 1_000_000)

def move(board, ref, x, y, rot=0):
    for fp in board.GetFootprints():
        if str(fp.GetReference()) == ref:
            fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
            fp.SetOrientationDegrees(rot)
            return
    print(f"  WARNING: {ref} not found")

def apply_layout():
    pcb_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "build", "icio500", "icio500.kicad_pcb"
    )
    board = pcbnew.LoadBoard(pcb_path)
    print("Board loaded.")

    # Check if user actually imported the netlist
    has_u2 = any(str(fp.GetReference()) == 'U2' for fp in board.GetFootprints())
    if not has_u2:
        raise Exception("""
================================================================================
STOP! YOU SKIPPED THE MANUAL GUI STEP!

The Daisy Seed and new components do not exist on the PCB yet.
You MUST pull them in using the KiCad application before running this script.

Please do exactly this:
1. Open the KiCad PCB Editor.
2. Click 'File' -> 'Import' -> 'Netlist...'
3. Select this file: C:\\Users\\Chris Williams\\Documents\\GitHub\\ICIO500\\build\\default.net
4. Click 'Update PCB' (the components will appear on your cursor, click to drop them).
5. Press Ctrl+S to save the PCB.
6. Now you can run this script again.
================================================================================
""")

    Y_IC = 94.0
    
    # ─────────────────────────────────────────────────────────────────
    # The IO Block
    # ─────────────────────────────────────────────────────────────────
    move(board, 'U3', 151, Y_IC)   # TL072 scaling op-amp (was U4)
    move(board, 'U2', 163, Y_IC)   # THAT1200 balanced receiver (was U3)
    move(board, 'U4', 175, Y_IC)   # THAT1646 balanced driver (was U5)

    # receiver bypass caps (U2)
    move(board, 'C7',  165.5, Y_IC - 1.9)   # V+ bypass
    move(board, 'C8',  160.5, Y_IC + 1.9)   # V- bypass
    move(board, 'C14', 163,   Y_IC + 6)     # cm/sm sense cap

    # scaling bypass caps (U3)
    move(board, 'C15', 153.5, Y_IC - 1.9)    # V+ bypass
    move(board, 'C16', 148.5, Y_IC + 1.9)    # V- bypass

    # receiver ac coupling
    move(board, 'C12', 151, Y_IC - 6)        # ac_plus
    move(board, 'C13', 151, Y_IC + 6)        # ac_minus

    # driver bypass caps (U4)
    move(board, 'C19', 177.5, Y_IC + 0.6)   
    move(board, 'C20', 177.5, Y_IC - 2.4)   
    move(board, 'C21', 172.5, Y_IC - 0.6)   
    move(board, 'C22', 172.5, Y_IC + 2.4)   

    move(board, 'C23', 177.5, Y_IC - 5)     
    move(board, 'C24', 177.5, Y_IC + 5)     

    # Zobel network (U4)
    move(board, 'C25', 171, Y_IC - 7)       
    move(board, 'R7',  175, Y_IC - 7)       
    move(board, 'C26', 171, Y_IC + 7)       
    move(board, 'R8',  175, Y_IC + 7)       

    # Input RF filter
    move(board, 'R1',  169, Y_IC - 4)   
    move(board, 'R2',  169, Y_IC + 4)   
    move(board, 'C10', 169, Y_IC - 7)       # c_rf_plus_chas 
    move(board, 'C11', 169, Y_IC + 7)       # c_rf_minus_chas
    move(board, 'C9',  169, Y_IC - 1.5, rot=90)  # c_rf cross 

    # Scaling resistors
    move(board, 'R3',  157, Y_IC - 4)    
    move(board, 'R4',  157, Y_IC + 4)    
    move(board, 'R5',  145, Y_IC - 4)    
    move(board, 'R6',  145, Y_IC + 4)    
    move(board, 'C17', 157, Y_IC - 7)
    move(board, 'C18', 145, Y_IC - 7)

    # ESD protection diodes
    move(board, 'D3',  180, 85)
    move(board, 'D4',  180, 89)
    move(board, 'D5',  180, 100)
    move(board, 'D6',  180, 104)

    # ─────────────────────────────────────────────────────────────────
    # Power supply group (Move DCDC near Daisy to keep loops small)
    # ─────────────────────────────────────────────────────────────────
    Y_PWR = 112.0
    move(board, 'C1',  165, Y_PWR - 4)   
    move(board, 'C3',  165, Y_PWR + 4)   
    move(board, 'C2',  160, Y_PWR - 4)   
    move(board, 'C4',  160, Y_PWR + 4)   
    move(board, 'D1',  155, Y_PWR - 4)   
    move(board, 'D2',  155, Y_PWR + 4)   
    
    # ─────────────────────────────────────────────────────────────────
    # Daisy Seed & Isolated Power Components
    # Place Daisy on the left side, with isolated DCDC underneath it
    # ─────────────────────────────────────────────────────────────────
    # Daisy footprint is a 2x20 header. 
    DAISY_X = 80
    DAISY_Y = 100
    move(board, 'U5', DAISY_X, DAISY_Y)          # Daisy Seed
    move(board, 'U6', DAISY_X, DAISY_Y + 30)     # Switch Noise
    move(board, 'U7', DAISY_X + 15, DAISY_Y + 30)# Switch Bypass

    # Move Isolated DCDC directly adjacent to Daisy to minimize loop area
    move(board, 'U1', DAISY_X, DAISY_Y + 20)     # DCDC Converter
    move(board, 'C5', DAISY_X - 6, DAISY_Y + 20) # c_iso_bulk
    move(board, 'C6', DAISY_X - 10, DAISY_Y + 20) # c_iso_cer

    print("Placement done. Daisy and RFI components positioned.")
    pcbnew.SaveBoard(pcb_path, board)


if __name__ == '__main__':
    apply_layout()
