import pcbnew
import math

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

def place(ref, x, y, rot=0):
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
        fp.SetOrientationDegrees(rot)

# 1. DELETE ALL TRACKS AND ZONES TO CLEAN UP PROPERLY!
to_delete = []
for t in list(board.GetTracks()):
    to_delete.append(t)
for z in list(board.Zones()):
    to_delete.append(z)
for item in to_delete:
    board.Remove(item)

# Base coordinates for U3 (NJM2114 / TL072)
u3_x = 165.0
u3_y = 140.0

# Place U3
place("U3", u3_x, u3_y, 0)

# Pin 1: (u3_x - 2.475, u3_y - 1.905)
# Pin 2: (u3_x - 2.475, u3_y - 0.635)
# Pin 3: (u3_x - 2.475, u3_y + 0.635)
# Pin 4: (u3_x - 2.475, u3_y + 1.905)
# Pin 5: (u3_x + 2.475, u3_y + 1.905)
# Pin 6: (u3_x + 2.475, u3_y + 0.635)
# Pin 7: (u3_x + 2.475, u3_y - 0.635)
# Pin 8: (u3_x + 2.475, u3_y - 1.905)

# 2. Power Bypassing
# C15 (100nF V+) near Pin 8 (167.5, 138.1)
place("C15", u3_x + 5.5, u3_y - 1.905, 90) # Vertical, right of Pin 8

# C16 (100nF V-) near Pin 4 (162.5, 141.9)
place("C16", u3_x - 5.5, u3_y + 1.905, 90) # Vertical, left of Pin 4

# 3. Half A (Left side)
# C17 (47pF) and R4 (10k) bridge Pin 1 and Pin 2
place("C17", u3_x - 5.5, u3_y - 1.27, 0) # Horizontal
place("R4", u3_x - 8.0, u3_y - 1.27, 0) # Horizontal

# R3 (22k) series resistor into Pin 2
place("R3", u3_x - 8.0, u3_y - 0.0, 0) # Horizontal

# 4. Half B (Right side)
# C18 (47pF) and R6 (22k) bridge Pin 7 and Pin 6
place("C18", u3_x + 5.5, u3_y + 0.0, 0) # Horizontal
place("R6", u3_x + 8.0, u3_y + 0.0, 0) # Horizontal

# R5 (10k) series resistor into Pin 6
place("R5", u3_x + 8.0, u3_y + 1.27, 0) # Horizontal

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print("U3 layout optimized.")
