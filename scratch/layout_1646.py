import pcbnew
import math

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

def place(ref, x, y, rot=0):
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
        fp.SetOrientationDegrees(rot)

# Remove tracks related to U4 to cleanly re-route
u4_nets = set()
for pad in board.FindFootprintByReference('U4').Pads():
    u4_nets.add(pad.GetNetCode())
    
to_delete = []
for t in board.GetTracks():
    if t.GetNetCode() in u4_nets and t.GetNetCode() != 0:
        to_delete.append(t)
for item in to_delete:
    board.Remove(item)

# Base coordinates for U4
u4_x = 165.0
u4_y = 70.0

# 1. Place U4 (THAT1646 SOIC-8)
place("U4", u4_x, u4_y, 0)

# Pin 1: (u4_x - 2.475, u4_y - 1.905)
# Pin 2: (u4_x - 2.475, u4_y - 0.635)
# Pin 3: (u4_x - 2.475, u4_y + 0.635)
# Pin 4: (u4_x - 2.475, u4_y + 1.905)
# Pin 5: (u4_x + 2.475, u4_y + 1.905)
# Pin 6: (u4_x + 2.475, u4_y + 0.635)
# Pin 7: (u4_x + 2.475, u4_y - 0.635)
# Pin 8: (u4_x + 2.475, u4_y - 1.905)

# 2. V+ Bypass (Pin 6: Right side, u4_y + 0.635)
# C20 (100nF) right next to Pin 6.
place("C20", u4_x + 4.5, u4_y + 0.635, 90) # Vertical
# C19 (10uF bulk) right next to C20.
place("C19", u4_x + 6.5, u4_y + 0.635, 90)

# 3. V- Bypass (Pin 2: Left side, u4_y - 0.635)
# C22 (100nF) right next to Pin 2.
place("C22", u4_x - 4.5, u4_y - 0.635, 90) # Vertical
# C21 (10uF bulk) right next to C22.
place("C21", u4_x - 6.5, u4_y - 0.635, 90)

# 4. Sense Capacitors
# C23 bridges Pin 1 (Out+) and Pin 8 (Sense+). Both are at Y = u4_y - 1.905.
# Place horizontally just above the IC!
place("C23", u4_x, u4_y - 3.5, 0) # Horizontal

# C24 bridges Pin 3 (Out-) and Pin 7 (Sense-).
# Pin 3 is at Y = u4_y + 0.635. Pin 7 is at Y = u4_y - 0.635.
# Place horizontally just below the IC!
place("C24", u4_x, u4_y + 3.5, 0) # Horizontal

# 5. Zobel Networks (Out+ to GND, Out- to GND)
# Out+ is Pin 1 (Top-Left).
place("R7", u4_x - 4.5, u4_y - 2.5, 0) # Horizontal, left of Pin 1
place("C25", u4_x - 7.0, u4_y - 2.5, 0) # Horizontal, left of R7

# Out- is Pin 3 (Mid-Bot Left).
place("R8", u4_x - 4.5, u4_y + 1.5, 0) # Horizontal, left of Pin 3
place("C26", u4_x - 7.0, u4_y + 1.5, 0) # Horizontal, left of R8

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print("1646 layout optimized.")
