"""
Full relayout of ICIO500 within the existing board outline.
- Board outline: X: 50.6 -> 195.0, Y: 55.0 -> 160.0
- Edge connector J1 on right side at X=198.5
- Signal flow: J1 (right) -> Power (center-right) -> Input -> Scaling -> Driver -> back to J1

Component blocks from atopile source:
  POWER:  D1, D2, C1, C2, C3, C4, U1(DC-DC), C5, C6
  INPUT:  U2, R1, R2, C9, C10, C11, C12, C13, C14, C7, C8, C15, C16, D3, D4, D5, D6
  SCALE:  U3, R3, R4, R5, R6, C17, C18
  DRIVER: U4, C19, C20, C21, C22, C23, C24, R7, R8, C25, C26
  DIGITAL: U5(Daisy DIP-40), U6(sw), U7(sw)
"""
import pcbnew

BOARD_IN = 'build/icio500/icio500.kicad_pcb'

def main():
    board = pcbnew.LoadBoard(BOARD_IN)
    
    # =========================================================
    # STEP 1: Delete all existing tracks, vias, zones, and bad silkscreen
    # =========================================================
    tracks_to_remove = list(board.GetTracks())
    for t in tracks_to_remove:
        board.Remove(t)
    print(f"Removed {len(tracks_to_remove)} tracks/vias")
    
    # Remove bad silkscreen text labels I previously added
    bad_labels = ["BALANCED INPUT STAGE", "LINE DRIVER STAGE", 
                  "SCALING & SHIFTING", "POWER CONDITIONING",
                  "POWER / REGS", "GAIN TRIM RESISTOR"]
    drawings_to_remove = []
    for dwg in board.GetDrawings():
        if isinstance(dwg, pcbnew.PCB_TEXT):
            if dwg.GetText() in bad_labels:
                drawings_to_remove.append(dwg)
    for dwg in drawings_to_remove:
        board.Remove(dwg)
    print(f"Removed {len(drawings_to_remove)} bad silkscreen labels")
    
    # Remove zones (we'll re-add ground zones later)
    zones_to_remove = list(board.Zones())
    for z in zones_to_remove:
        board.Remove(z)
    print(f"Removed {len(zones_to_remove)} zones")
    
    # =========================================================
    # STEP 2: Place components in logical blocks
    # =========================================================
    # Board usable area: X: 55 -> 193, Y: 57 -> 158
    # J1 is fixed at (198.5, 98.9) - don't move it
    
    def place(ref, x, y, rot=None):
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            print(f"  WARNING: {ref} not found!")
            return
        fp.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
        if rot is not None:
            fp.SetOrientationDegrees(rot)
        print(f"  Placed {ref} at ({x}, {y}) rot={rot}")
    
    # ----- BLOCK: EDGE CONNECTOR (fixed) -----
    # J1 stays at (198.5, 98.9) — don't touch
    
    # ----- BLOCK: POWER SUPPLY (center of board, near J1) -----
    # D1/D2 protection diodes near J1 power pins
    # C1/C3 bulk electrolytics centrally  
    # C2/C4 ceramic bypass near bulk caps
    # U1 DC-DC converter central
    # C5/C6 DC-DC output caps near U1
    
    print("\n=== POWER SUPPLY ===")
    # Protection diodes close to J1 (right side)
    place("D1", 185, 120, 0)    # V+ protection
    place("D2", 185, 130, 0)    # V- protection
    
    # Bulk electrolytics - central, with room
    place("C1", 165, 125, 0)    # 220uF V+ bulk
    place("C3", 165, 135, 0)    # 220uF V- bulk
    
    # Ceramic bypass near bulk caps
    place("C2", 175, 125, 0)    # 100nF V+ ceramic
    place("C4", 175, 135, 0)    # 100nF V- ceramic
    
    # DC-DC converter - central
    place("U1", 130, 130, 0)    # Isolated DC-DC 5V
    
    # DC-DC output caps near U1
    place("C5", 140, 127, 0)    # 10uF iso output
    place("C6", 140, 133, 0)    # 100nF iso output
    
    # ----- BLOCK: BALANCED INPUT (U2 area, upper-right) -----
    print("\n=== BALANCED INPUT STAGE ===")
    # U2 (THAT1200) - right-center area, close to J1 audio input pins
    place("U2", 170, 100, 0)
    
    # RF filter resistors (signal enters from J1 on right)
    place("R1", 180, 95, 0)     # RF+ resistor (in_plus from J1)
    place("R2", 180, 105, 0)    # RF- resistor (in_minus from J1)
    
    # RF shunt caps (chassis referenced)
    place("C10", 185, 92, 0)    # chassis shunt +
    place("C11", 185, 108, 0)   # chassis shunt -
    
    # Differential RF cap between + and -
    place("C9", 182, 100, 90)   # 220pF diff cap
    
    # AC coupling caps (between RF filter and IC inputs)
    place("C12", 175, 95, 0)    # AC coupling +
    place("C13", 175, 105, 0)   # AC coupling -
    
    # CM bootstrap cap
    place("C14", 165, 105, 90)  # cm-sm bootstrap
    
    # Power bypass caps for U2
    place("C7",  165, 95, 90)   # V+ bypass
    place("C15", 163, 95, 90)   # V+ bypass (2nd)
    place("C8",  165, 108, 90)  # V- bypass
    place("C16", 163, 108, 90)  # V- bypass (2nd)
    
    # Clamping diodes - tight cluster near IC input pins
    place("D3", 172, 93, 90)    # In+ -> V+
    place("D4", 172, 97, 90)    # V- -> In+
    place("D5", 172, 103, 90)   # In- -> V+
    place("D6", 172, 107, 90)   # V- -> In-
    
    # ----- BLOCK: ACTIVE SCALING (U3 area, center) -----
    print("\n=== ACTIVE SCALING ===")
    # U3 (OPA2134) - center of board
    place("U3", 140, 95, 0)
    
    # Half A: Input attenuation (from THAT1200 output)
    place("R3", 148, 90, 0)     # 22k input series
    place("R4", 148, 93, 0)     # 10k feedback  
    place("C17", 145, 100, 90)  # 47pF filter
    
    # Half B: Output gain (from Daisy, to THAT1646)
    place("R5", 148, 97, 0)     # 10k output series
    place("R6", 148, 100, 0)    # 22k output feedback
    place("C18", 145, 90, 90)   # 47pF filter
    
    # ----- BLOCK: LINE DRIVER (U4 area, upper-center) -----
    print("\n=== LINE DRIVER ===")
    # U4 (THAT1646) - upper area, output goes back to J1
    place("U4", 140, 70, 0)
    
    # Power bypass caps for U4
    place("C19", 148, 68, 90)   # V+ bulk bypass
    place("C20", 150, 68, 90)   # V+ ceramic bypass
    place("C21", 148, 75, 90)   # V- bulk bypass
    place("C22", 150, 75, 90)   # V- ceramic bypass
    
    # External caps (Out -> Sense)
    place("C23", 135, 65, 0)    # Out+ -> Sense+
    place("C24", 135, 75, 0)    # Out- -> Sense-
    
    # Zobel networks - RIGHT NEXT to U4 output
    place("R7",  130, 65, 0)    # Zobel+ resistor
    place("C25", 125, 65, 0)    # Zobel+ cap
    place("R8",  130, 75, 0)    # Zobel- resistor
    place("C26", 125, 75, 0)    # Zobel- cap
    
    # ----- BLOCK: DIGITAL / DAISY SEED (left side) -----
    print("\n=== DIGITAL SECTION ===")
    # U5 (Daisy Seed DIP-40) - large, takes up left side
    place("U5", 80, 100, 90)    # Rotated to fit
    
    # Switches right next to Daisy (they connect to D13/D14 GPIO)
    place("U6", 65, 108, 0)     # Switch - bypass (near U5 pin 15)
    place("U7", 65, 100, 0)     # Switch - noise (near U5 pin 16)
    
    # =========================================================
    # STEP 3: Save
    # =========================================================
    pcbnew.SaveBoard(BOARD_IN, board)
    print("\n=== RELAYOUT COMPLETE ===")
    print("All components placed. Traces cleared. Ready for routing.")

if __name__ == '__main__':
    main()
