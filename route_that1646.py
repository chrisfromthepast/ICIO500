import pcbnew
import os
import sys

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

def mm(v): return int(v * 1_000_000)
def to_mm(v): return v / 1_000_000

# 1. Clear existing tracks near U4
u4 = board.FindFootprintByReference('U4')
u4_pos = u4.GetPosition()
u4_x, u4_y = to_mm(u4_pos.x), to_mm(u4_pos.y)

for track in list(board.GetTracks()):
    tx, ty = to_mm(track.GetStart().x), to_mm(track.GetStart().y)
    if u4_x - 20 < tx < u4_x + 20 and u4_y - 15 < ty < u4_y + 15:
        board.Remove(track)

# 2. Position components intelligently to leave routing channels
def move(ref, x, y, rot=0, flip=False):
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
        if flip and not fp.IsFlipped():
            fp.Flip(fp.GetPosition(), False)
        elif not flip and fp.IsFlipped():
            fp.Flip(fp.GetPosition(), False)

x, y = 165.0, 70.0
move('U4', x, y, 0)

# C23 (Sense+ to Out+)
# Bridging Pin 1 (Top Left) to Pin 8 (Top Right).
# Place horizontally right above the pins.
move('C23', x, y - 5.0, 0)

# C24 (Sense- to Out-)
# Bridging Pin 3 (Bottom Left) to Pin 7 (Top Right).
# Place horizontally on the TOP layer, directly ABOVE C23.
# The traces will route up the outer edges of the IC.
move('C24', x, y - 8.0, 0, flip=False)

# Decoupling Caps
# Pin 6 is V+ (Middle Bottom Right). We'll place C20 to the right, slightly down.
move('C20', x + 6.0, y + 1.27, 90) # Ceramic V+
move('C19', x + 10.0, y + 1.27, 90) # Bulk V+

# Pin 2 is V- (Middle Top Left). We'll place C22 to the left, slightly up.
move('C22', x - 6.0, y - 1.27, 90) # Ceramic V-
move('C21', x - 10.0, y - 1.27, 90) # Bulk V-

# Zobels
# Out+ (Pin 1 - left side)
move('R7', x - 8.0, y - 6.0, 0)
move('C25', x - 13.0, y - 6.0, 0)

# Out- (Pin 3 - left side)
move('R8', x - 8.0, y + 6.0, 0)
move('C26', x - 13.0, y + 6.0, 0)

pcbnew.SaveBoard(pcb_path, board)
print("THAT1646 layout positioned optimally.")
sys.exit(0)
