"""
layout_pcb.py  –  ICIO500 placement pass
=========================================
Places components only. No tracks, no zones.

4-layer stackup:
  F.Cu   – signal traces
  In1.Cu – GND plane
  In2.Cu – V+ plane
  B.Cu   – spare

Goal: Pack the IO block tightly against the right side (near the J1 
connector) to leave the rest of the board open for future circuitry.
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

    # ─────────────────────────────────────────────────────────────────
    # We pack the ICs closely together on the right side.
    # J1 silkscreen starts at X=177, so we end the block at X=175.
    # ─────────────────────────────────────────────────────────────────
    Y_IC = 94.0
    
    # 12mm spacing between IC centres is tight but allows bypass caps
    move(board, 'U4', 151, Y_IC)   # TL072 scaling op-amp
    move(board, 'U3', 163, Y_IC)   # THAT1200 balanced receiver
    move(board, 'U5', 175, Y_IC)   # THAT1646 balanced driver

    # ─────────────────────────────────────────────────────────────────
    # U3 (THAT1200) bypass caps (tight to pins)
    # V+ pin 8 (top right), V- pin 4 (bottom left)
    # ─────────────────────────────────────────────────────────────────
    move(board, 'C7',  165.5, Y_IC - 1.9)   # V+ bypass
    move(board, 'C8',  160.5, Y_IC + 1.9)   # V- bypass
    move(board, 'C12', 163,   Y_IC + 6)     # cm/sm sense cap

    # ─────────────────────────────────────────────────────────────────
    # U4 (TL072) bypass caps (tight to pins)
    # V+ pin 8 (top right), V- pin 4 (bottom left)
    # ─────────────────────────────────────────────────────────────────
    move(board, 'C13', 153.5, Y_IC - 1.9)    # V+ bypass
    move(board, 'C14', 148.5, Y_IC + 1.9)    # V- bypass

    # Coupling/feedback caps
    move(board, 'C15', 151, Y_IC - 6)        # daisy_audio_in cap
    move(board, 'C16', 151, Y_IC + 6)        # audio_out_to_1646 cap

    # ─────────────────────────────────────────────────────────────────
    # U5 (THAT1646) bypass caps (tight to pins)
    # V+ pin 6 (middle right), V- pin 2 (middle left)
    # ─────────────────────────────────────────────────────────────────
    move(board, 'C17', 177.5, Y_IC + 0.6)   # V+ bypass
    move(board, 'C18', 177.5, Y_IC - 2.4)   # V+ bypass 2
    move(board, 'C19', 172.5, Y_IC - 0.6)   # V- bypass
    move(board, 'C20', 172.5, Y_IC + 2.4)   # V- bypass 2

    move(board, 'C21', 177.5, Y_IC - 5)     # sense+ cap
    move(board, 'C22', 177.5, Y_IC + 5)     # sense- cap

    # ─────────────────────────────────────────────────────────────────
    # Output network: Zobel (R7/C23, R8/C24)
    # Tucked just above and below U5
    # ─────────────────────────────────────────────────────────────────
    move(board, 'C23', 171, Y_IC - 7)       
    move(board, 'R7',  175, Y_IC - 7)       
    move(board, 'C24', 171, Y_IC + 7)       
    move(board, 'R8',  175, Y_IC + 7)       

    # ─────────────────────────────────────────────────────────────────
    # Input RF filter: packed between U3 and U5
    # ─────────────────────────────────────────────────────────────────
    move(board, 'R1',  169, Y_IC - 4)   
    move(board, 'R2',  169, Y_IC + 4)   
    move(board, 'C10', 169, Y_IC - 7)   
    move(board, 'C11', 169, Y_IC + 7)   
    move(board, 'C9',  169, Y_IC - 1.5, rot=90)   

    # ─────────────────────────────────────────────────────────────────
    # Scaling resistors (packed between U4 and U3)
    # ─────────────────────────────────────────────────────────────────
    move(board, 'R3',  157, Y_IC - 4)    
    move(board, 'R4',  157, Y_IC + 4)    
    move(board, 'R5',  145, Y_IC - 4)    
    move(board, 'R6',  145, Y_IC + 4)    

    # ─────────────────────────────────────────────────────────────────
    # ESD protection diodes (near the J1 connector)
    # ─────────────────────────────────────────────────────────────────
    move(board, 'D3',  180, 85)
    move(board, 'D4',  180, 89)
    move(board, 'D5',  180, 100)
    move(board, 'D6',  180, 104)

    # ─────────────────────────────────────────────────────────────────
    # Power supply group
    # Tucked underneath the IO block
    # ─────────────────────────────────────────────────────────────────
    Y_PWR = 112.0
    move(board, 'C2',  165, Y_PWR - 4)   # v+ bulk
    move(board, 'C4',  165, Y_PWR + 4)   # v- bulk
    move(board, 'D1',  155, Y_PWR - 4)   # power diode+
    move(board, 'D2',  155, Y_PWR + 4)   # power diode-
    move(board, 'C5',  145, Y_PWR - 4)   # Daisy 5V
    move(board, 'C6',  145, Y_PWR + 4)   # Daisy GND

    print("Placement done. IO block tightly packed on the right.")
    pcbnew.SaveBoard(pcb_path, board)


if __name__ == '__main__':
    apply_layout()
