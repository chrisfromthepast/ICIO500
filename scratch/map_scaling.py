import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
u3 = board.FindFootprintByReference('U3')

def get_net(ref, pad_num):
    fp = board.FindFootprintByReference(ref)
    if fp:
        pad = fp.FindPadByNumber(str(pad_num))
        if pad: return pad.GetNet().GetNetname()
    return None

comps = {}

# U3 pins:
# 1: out_1
# 2: in_minus_1
# 3: in_plus_1
# 4: v_minus
# 5: in_plus_2
# 6: in_minus_2
# 7: out_2
# 8: v_plus

# In Half A:
# r_in_series: audio_in_from_1200 to in_minus_1
# r_in_feedback: out_1 to in_minus_1
# c_in_filter: out_1 to in_minus_1

# In Half B:
# r_out_series: audio_in_from_daisy to in_minus_2
# r_out_feedback: out_2 to in_minus_2
# c_out_filter: out_2 to in_minus_2

for m in board.GetFootprints():
    ref = m.GetReference()
    if ref.startswith('C') or ref.startswith('R'):
        net1 = get_net(ref, 1)
        net2 = get_net(ref, 2)
        
        # Bypass caps
        if "scaling" in m.GetPath().AsString():
            # Half A passives
            if ref.startswith('C'):
                if (net1 == "scaling.ic.out_1" and net2 == "scaling.ic.in_minus_1") or \
                   (net2 == "scaling.ic.out_1" and net1 == "scaling.ic.in_minus_1"):
                    comps['c_in_filter'] = ref
                if (net1 == "scaling.ic.out_2" and net2 == "scaling.ic.in_minus_2") or \
                   (net2 == "scaling.ic.out_2" and net1 == "scaling.ic.in_minus_2"):
                    comps['c_out_filter'] = ref
                    
            if ref.startswith('R'):
                if (net1 == "scaling.ic.out_1" and net2 == "scaling.ic.in_minus_1") or \
                   (net2 == "scaling.ic.out_1" and net1 == "scaling.ic.in_minus_1"):
                    comps['r_in_feedback'] = ref
                if (net1 == "scaling.ic.out_2" and net2 == "scaling.ic.in_minus_2") or \
                   (net2 == "scaling.ic.out_2" and net1 == "scaling.ic.in_minus_2"):
                    comps['r_out_feedback'] = ref
                    
                if (net1 == "scaling.ic.in_minus_1" and net2 != "scaling.ic.out_1") or \
                   (net2 == "scaling.ic.in_minus_1" and net1 != "scaling.ic.out_1"):
                    comps['r_in_series'] = ref
                if (net1 == "scaling.ic.in_minus_2" and net2 != "scaling.ic.out_2") or \
                   (net2 == "scaling.ic.in_minus_2" and net1 != "scaling.ic.out_2"):
                    comps['r_out_series'] = ref

for k, v in comps.items():
    print(f"{k}: {v}")

print("Bypass candidates:")
for m in board.GetFootprints():
    ref = m.GetReference()
    if ref.startswith('C'):
        net1 = get_net(ref, 1)
        net2 = get_net(ref, 2)
        if "scaling" in m.GetPath().AsString() and \
           ((net1 == "v_plus" and net2 == "gnd") or (net1 == "gnd" and net2 == "v_plus") or \
            (net1 == "v_minus" and net2 == "gnd") or (net1 == "gnd" and net2 == "v_minus")):
            print(ref, net1, net2)

