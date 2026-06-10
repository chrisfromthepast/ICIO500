import pcbnew
import sys
import os

pcb_path = os.path.join("build", "icio500", "icio500.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

nets = board.GetNetsByName()
if 'in_plus' not in nets or 'v_plus' not in nets:
    print("Error: Could not find required nets.")
    sys.exit(1)

net_in_plus = nets['in_plus']
net_in_minus = nets['in_minus']
net_v_plus = nets['v_plus']
net_v_minus = nets['v_minus']

for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref == 'D3':
        fp.FindPadByNumber('1').SetNet(net_in_plus)
        fp.FindPadByNumber('2').SetNet(net_v_plus)
    elif ref == 'D4':
        fp.FindPadByNumber('1').SetNet(net_v_minus)
        fp.FindPadByNumber('2').SetNet(net_in_plus)
    elif ref == 'D5':
        fp.FindPadByNumber('1').SetNet(net_in_minus)
        fp.FindPadByNumber('2').SetNet(net_v_plus)
    elif ref == 'D6':
        fp.FindPadByNumber('1').SetNet(net_v_minus)
        fp.FindPadByNumber('2').SetNet(net_in_minus)

pcbnew.SaveBoard(pcb_path, board)
print("Wired protection diodes D3, D4, D5, D6 successfully.")
sys.exit(0)
