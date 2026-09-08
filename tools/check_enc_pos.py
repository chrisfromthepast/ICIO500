import pcbnew
fp = pcbnew.LoadBoard('build/icio500/faceplate_front.kicad_pcb')
enc_fp = None
for f in fp.GetFootprints():
    if 'Encoder' in str(f.GetFPID().GetLibItemName()):
        enc_fp = f
        break
sat = pcbnew.LoadBoard('build/icio500/panel_satellite.kicad_pcb')
enc_sat = sat.FindFootprintByReference('ENC1')
if enc_fp: print(f'Faceplate encoder hole pos: {enc_fp.GetPosition()}')
if enc_sat: print(f'Satellite encoder pos: {enc_sat.GetPosition()}')
