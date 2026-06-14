import pcbnew

board = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')
u2 = board.FindFootprintByReference('U2')

def get_net(ref, pad_num):
    fp = board.FindFootprintByReference(ref)
    if fp:
        pad = fp.FindPadByNumber(str(pad_num))
        if pad: return pad.GetNet().GetNetname()
    return None

comps = {}

# We know U2 nets:
# Pin 2: in_minus
# Pin 3: in_plus
# Pin 5: sm
# Pin 6: cm

for m in board.GetFootprints():
    ref = m.GetReference()
    if ref.startswith('C') or ref.startswith('D') or ref.startswith('R'):
        net1 = get_net(ref, 1)
        net2 = get_net(ref, 2)
        
        # c_cm: between sm and cm
        if (net1 == "sm" and net2 == "cm") or (net1 == "cm" and net2 == "sm"):
            comps['c_cm'] = ref
            
        # c_ac_plus: between in_plus and a net going to r_rf_plus
        if net1 == "in_plus" or net2 == "in_plus":
            other = net2 if net1 == "in_plus" else net1
            if not other in ["v_plus", "v_minus", "gnd"]:
                # Could be c_ac_plus
                comps['c_ac_plus'] = ref
                comps['r_rf_plus_net'] = other

        # c_ac_minus: between in_minus and a net going to r_rf_minus
        if net1 == "in_minus" or net2 == "in_minus":
            other = net2 if net1 == "in_minus" else net1
            if not other in ["v_plus", "v_minus", "gnd"]:
                comps['c_ac_minus'] = ref
                comps['r_rf_minus_net'] = other
                
        # Clamping diodes:
        # d_clamp_p_vplus: in_plus and v_plus
        if (net1 == "in_plus" and net2 == "v_plus") or (net1 == "v_plus" and net2 == "in_plus"):
            if ref.startswith('D'): comps['d_clamp_p_vplus'] = ref
        # d_clamp_p_vminus: in_plus and v_minus
        if (net1 == "in_plus" and net2 == "v_minus") or (net1 == "v_minus" and net2 == "in_plus"):
            if ref.startswith('D'): comps['d_clamp_p_vminus'] = ref
        # d_clamp_n_vplus: in_minus and v_plus
        if (net1 == "in_minus" and net2 == "v_plus") or (net1 == "v_plus" and net2 == "in_minus"):
            if ref.startswith('D'): comps['d_clamp_n_vplus'] = ref
        # d_clamp_n_vminus: in_minus and v_minus
        if (net1 == "in_minus" and net2 == "v_minus") or (net1 == "v_minus" and net2 == "in_minus"):
            if ref.startswith('D'): comps['d_clamp_n_vminus'] = ref

for k, v in comps.items():
    print(f"{k}: {v}")
    
# Find resistors
for m in board.GetFootprints():
    ref = m.GetReference()
    if ref.startswith('R'):
        net1 = get_net(ref, 1)
        net2 = get_net(ref, 2)
        if net1 == comps.get('r_rf_plus_net') or net2 == comps.get('r_rf_plus_net'):
            comps['r_rf_plus'] = ref
        if net1 == comps.get('r_rf_minus_net') or net2 == comps.get('r_rf_minus_net'):
            comps['r_rf_minus'] = ref

# Find rf caps
for m in board.GetFootprints():
    ref = m.GetReference()
    if ref.startswith('C'):
        net1 = get_net(ref, 1)
        net2 = get_net(ref, 2)
        if (net1 == comps.get('r_rf_plus_net') and net2 == comps.get('r_rf_minus_net')) or \
           (net1 == comps.get('r_rf_minus_net') and net2 == comps.get('r_rf_plus_net')):
            comps['c_rf'] = ref
        if (net1 == comps.get('r_rf_plus_net') and net2 == "chassis_gnd") or \
           (net1 == "chassis_gnd" and net2 == comps.get('r_rf_plus_net')):
            comps['c_rf_plus_chas'] = ref
        if (net1 == comps.get('r_rf_minus_net') and net2 == "chassis_gnd") or \
           (net1 == "chassis_gnd" and net2 == comps.get('r_rf_minus_net')):
            comps['c_rf_minus_chas'] = ref

print("\nFinal mapping:")
for k, v in comps.items():
    print(f"{k}: {v}")
