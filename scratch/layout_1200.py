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

# Base coordinates for U2 (THAT1200)
u2_x = 175.0
u2_y = 105.0

# Place U2
place("U2", u2_x, u2_y, 0)

# 2. Power Bypassing
# C7 (100nF V+) between Pin 8 (177.5, 103.1) and Pin 1 (172.5, 103.1)
place("C7", u2_x, u2_y - 4.5, 0) # Horizontal, above IC

# C8 (100nF V-) near Pin 4 (172.5, 106.9)
place("C8", u2_x - 5.5, u2_y + 1.905, 90) # Vertical, left of Pin 4

# 3. Bootstrap Capacitor
# C14 between Pin 5 (Sm) and Pin 6 (Cm)
place("C14", u2_x + 5.5, u2_y + 1.27, 90) # Vertical, right of Pins 5/6

# 4. AC Coupling Capacitors
# Pin 3 (In+) is at 105.635
# Pin 2 (In-) is at 104.365
place("C12", u2_x - 5.5, u2_y + 0.635, 0) # Horizontal, left of Pin 3
place("C13", u2_x - 5.5, u2_y - 0.635, 0) # Horizontal, left of Pin 2

# 5. Clamping Diodes (SOD-123 are roughly 3.7x1.6mm)
# Place these stacked neatly to the left of the AC caps
d_x = u2_x - 10.0
place("D3", d_x, u2_y + 2.5, 90)
place("D4", d_x + 2.5, u2_y + 2.5, 90)
place("D5", d_x, u2_y - 2.5, 90)
place("D6", d_x + 2.5, u2_y - 2.5, 90)

# 6. RF Filter section
# Place R1, R2, C9, C10, C11 further left, neat and tight
rf_x = u2_x - 15.0
place("R1", rf_x, u2_y + 0.635, 0)
place("R2", rf_x, u2_y - 0.635, 0)

place("C9", rf_x - 3.0, u2_y, 90) # Bridges the two lines vertically

place("C10", rf_x - 6.0, u2_y + 0.635, 0)
place("C11", rf_x - 6.0, u2_y - 0.635, 0)

pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', board)
print("1200 layout optimized.")
