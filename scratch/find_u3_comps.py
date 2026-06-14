import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
u3 = board.FindFootprintByReference('U3')

u3_nets = {}
for pad in u3.Pads():
    u3_nets[pad.GetPadName()] = pad.GetNet().GetNetname()
    print(f"U3 Pin {pad.GetPadName()}: {pad.GetNet().GetNetname()}")

print("\nComponents connected to U3:")
connected = {}
for m in board.GetFootprints():
    if m.GetReference() == 'U3': continue
    for pad in m.Pads():
        if pad.GetNet().GetNetname() in u3_nets.values():
            net = pad.GetNet().GetNetname()
            if net not in ["gnd", "v_plus", "v_minus"]:
                if m.GetReference() not in connected:
                    connected[m.GetReference()] = []
                connected[m.GetReference()].append(net)

for ref, nets in connected.items():
    print(f"{ref}: {nets}")
