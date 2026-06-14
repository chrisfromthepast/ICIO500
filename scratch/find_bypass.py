import pcbnew
board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
for m in board.GetFootprints():
    ref = m.GetReference()
    if ref.startswith('C'):
        net1 = m.FindPadByNumber('1').GetNet().GetNetname() if m.FindPadByNumber('1') else ""
        net2 = m.FindPadByNumber('2').GetNet().GetNetname() if m.FindPadByNumber('2') else ""
        if (net1 == "v_plus" and net2 == "gnd") or (net1 == "gnd" and net2 == "v_plus"):
            print(f"Bypass Plus: {ref}")
        if (net1 == "v_minus" and net2 == "gnd") or (net1 == "gnd" and net2 == "v_minus"):
            print(f"Bypass Minus: {ref}")
