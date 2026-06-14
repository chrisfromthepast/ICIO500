import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

u2 = board.FindFootprintByReference('U2')
u2_nets = {}
for pad in u2.Pads():
    u2_nets[pad.GetPadName()] = pad.GetNet().GetNetname()
    print(f"U2 Pin {pad.GetPadName()}: {pad.GetNet().GetNetname()}")

print("\nComponents connected to U2:")
connected = set()
for m in board.GetFootprints():
    if m.GetReference() == 'U2': continue
    for pad in m.Pads():
        if pad.GetNet().GetNetname() in u2_nets.values():
            if pad.GetNet().GetNetname() != "GND" and pad.GetNet().GetNetname() != "V_Plus" and pad.GetNet().GetNetname() != "V_Minus" and pad.GetNet().GetNetname() != "Chassis":
                connected.add(m.GetReference())
print(connected)

# Let's just list ALL components whose value matches the 1200 stage
# 220pF caps:
print("\n220pF Caps:")
for m in board.GetFootprints():
    if "220pF" in m.GetValue(): print(m.GetReference())

print("\n100ohm Resistors:")
for m in board.GetFootprints():
    if "100ohm" in m.GetValue(): print(m.GetReference())

print("\n10uF Caps:")
for m in board.GetFootprints():
    if "10uF" in m.GetValue(): print(m.GetReference())

print("\nDiodes:")
for m in board.GetFootprints():
    if "D_SOD-123" in m.GetFPID().GetLibItemName().c_str(): print(m.GetReference(), m.GetValue())
