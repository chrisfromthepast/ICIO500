import pcbnew

def mm(v): return int(v * 1_000_000)

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

def move_block(refs, dx, dy):
    for ref in refs:
        fp = board.FindFootprintByReference(ref)
        if fp:
            pos = fp.GetPosition()
            fp.SetPosition(pcbnew.VECTOR2I(pos.x + mm(dx), pos.y + mm(dy)))

# U3 block (Scaling)
u3_refs = ['U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6']
# Move U3 UP from Y=140 to Y=85 (between U4 at Y=70 and U2 at Y=105)
# Delta-Y = -55.
move_block(u3_refs, dx=0, dy=-55)

# Power Block
power_refs = ['U1', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'D1', 'D2']
# Move Power DOWN from Y=100-105 to Y=135
# Delta-Y = +35.
move_block(power_refs, dx=-10, dy=35) # Moved a bit left too so it doesn't hit the edge connector? Actually let's just do dy=35 first.
# Wait, let's just do dy=35.
move_block(power_refs, dx=0, dy=35)

# Daisy Seed
daisy_refs = ['U5']
# Move Daisy DOWN from Y=105 to Y=130
move_block(daisy_refs, dx=0, dy=25)

# Also delete all non-footprint graphics on silkscreen and drawings layers to clean up the old "DC-DC ISO" boxes
layers_to_clean = [pcbnew.F_SilkS, pcbnew.User_Comments, pcbnew.User_Drawings]
for item in list(board.GetDrawings()):
    if item.GetLayer() in layers_to_clean:
        board.Remove(item)

board.Save('build/icio500/icio500.kicad_pcb')
print("Blocks moved and silkscreen cleaned.")
