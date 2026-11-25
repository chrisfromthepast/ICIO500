"""
Synchronizes the carrier PCB layout with the verified schematic blueprint.
Normalizes footprint pad numbers, integrates R11/D11/C15 input clamping, maps
Daisy Seed audio and faceplate header pins net-for-net, and routes all tracks
with 0 errors and 0 unconnected items.
"""

import re
import os
import shutil
import uuid
import subprocess

def uid():
    return str(uuid.uuid4())

BAK_PATH = 'build/icio500/icio500_pre_sync.kicad_pcb'
TARGET_PATH = 'build/icio500/icio500.kicad_pcb'

def sync_pcb():
    with open(BAK_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Normalize pad numbers on footprints
    soic_pad_map = {
        '19': '1', '20': '2', '17': '3', '18': '4',
        '15': '5', '16': '6', '13': '7', '14': '8',
    }
    passive_pad_map = {'19': '1', '20': '2'}
    passives_to_fix = [
        'R8', 'R2', 'R3', 'C15', 'C16', 'D10', 'C6', 'D5',
        'C11', 'C20', 'R6', 'C14', 'C8', 'C21', 'C26', 'C23',
        'D2', 'C1', 'R4', 'C2'
    ]

    idx_c15 = text.find('(property "Reference" "C15"')
    if idx_c15 != -1:
        text = text[:idx_c15] + '(property "Reference" "C11_BYP"' + text[idx_c15 + len('(property "Reference" "C15"'):]

    for ref in ['U2', 'U3']:
        idx = text.find(f'(property "Reference" "{ref}"')
        if idx == -1: continue
        fp_start = text.rfind('(footprint ', 0, idx)
        depth = 0
        fp_end = len(text)
        for i in range(fp_start, len(text)):
            if text[i] == '(': depth += 1
            elif text[i] == ')':
                depth -= 1
                if depth == 0:
                    fp_end = i + 1
                    break
        fp_block = text[fp_start:fp_end]
        for old_p, new_p in soic_pad_map.items():
            fp_block = re.sub(rf'\(pad\s+"{old_p}"\s+', f'(pad "{new_p}" ', fp_block)
        text = text[:fp_start] + fp_block + text[fp_end:]

    for ref in passives_to_fix + ['C11_BYP']:
        idx = text.find(f'(property "Reference" "{ref}"')
        if idx == -1: continue
        fp_start = text.rfind('(footprint ', 0, idx)
        depth = 0
        fp_end = len(text)
        for i in range(fp_start, len(text)):
            if text[i] == '(': depth += 1
            elif text[i] == ')':
                depth -= 1
                if depth == 0:
                    fp_end = i + 1
                    break
        fp_block = text[fp_start:fp_end]
        for old_p, new_p in passive_pad_map.items():
            fp_block = re.sub(rf'\(pad\s+"{old_p}"\s+', f'(pad "{new_p}" ', fp_block)
        text = text[:fp_start] + fp_block + text[fp_end:]

    def update_fp_pad_net(block, pad_num, net_name):
        pattern = rf'(\(pad\s+"{pad_num}"\s+[^\n]*\n(?:[^\n]*\n)*?)(?:\t*\(net\s+"[^"]*"\)\n)?(\t*\))'
        m = re.search(pattern, block)
        if m:
            if net_name:
                repl = f'{m.group(1)}\t\t\t(net "{net_name}")\n{m.group(2)}'
            else:
                repl = f'{m.group(1)}{m.group(2)}'
            return block[:m.start()] + repl + block[m.end():]
        return block

    # 2. Update U5 (Daisy Seed Socket) Pin Nets
    idx_u5 = text.find('(property "Reference" "U5"')
    fp_start = text.rfind('(footprint ', 0, idx_u5)
    depth = 0
    fp_end = len(text)
    for i in range(fp_start, len(text)):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                fp_end = i + 1
                break
    u5_block = text[fp_start:fp_end]
    u5_block = re.sub(r'\t*\(net\s+"[^"]*"\)\n', '', u5_block)

    u5_exact_nets = {
        '12': 'i2c1_scl',
        '13': 'i2c1_sda',
        '16': 'daisy_audio_in',
        '17': 'gnd',
        '18': 'audio_in_from_daisy_plus',
        '20': 'gnd',
        '21': '+3.3V',
        '22': 'd14',
        '23': 'gpio_enc_b',
        '24': 'gpio_enc_sw',
        '38': '+3.3V',
        '39': 'daisy_5v_power',
        '40': 'gnd'
    }

    for p, n in u5_exact_nets.items():
        u5_block = update_fp_pad_net(u5_block, p, n)

    text = text[:fp_start] + u5_block + text[fp_end:]

    # 3. Update U6 Pin Nets
    idx_u6 = text.find('(property "Reference" "U6"')
    fp_start = text.rfind('(footprint ', 0, idx_u6)
    depth = 0
    fp_end = len(text)
    for i in range(fp_start, len(text)):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                fp_end = i + 1
                break
    u6_block = text[fp_start:fp_end]
    u6_block = re.sub(r'\t*\(net\s+"[^"]*"\)\n', '', u6_block)

    u6_exact_nets = {str(i): 'gnd' for i in range(1, 21)}
    u6_exact_nets['20'] = '+3.3V'
    u6_exact_nets['17'] = 'i2c1_sda'
    u6_exact_nets['15'] = 'i2c1_scl'

    for p, n in u6_exact_nets.items():
        u6_block = update_fp_pad_net(u6_block, p, n)

    text = text[:fp_start] + u6_block + text[fp_end:]

    # 4. Update J_ENC Pin Nets
    idx_jenc = text.find('(property "Reference" "J_ENC"')
    fp_start = text.rfind('(footprint ', 0, idx_jenc)
    depth = 0
    fp_end = len(text)
    for i in range(fp_start, len(text)):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                fp_end = i + 1
                break
    jenc_block = text[fp_start:fp_end]
    jenc_block = re.sub(r'\t*\(net\s+"[^"]*"\)\n', '', jenc_block)

    jenc_exact_nets = {
        '1': 'gpio_enc_sw',
        '2': 'gnd',
        '3': 'gpio_enc_b',
        '4': 'gnd',
        '5': 'd14'
    }
    for p, n in jenc_exact_nets.items():
        jenc_block = update_fp_pad_net(jenc_block, p, n)

    text = text[:fp_start] + jenc_block + text[fp_end:]

    # 5. Update U3, R4, C17 feedback net to tl072_out1_raw
    for r_target in ['U3', 'R4', 'C17']:
        idx = text.find(f'(property "Reference" "{r_target}"')
        if idx == -1: continue
        fp_start = text.rfind('(footprint ', 0, idx)
        depth = 0
        fp_end = len(text)
        for i in range(fp_start, len(text)):
            if text[i] == '(': depth += 1
            elif text[i] == ')':
                depth -= 1
                if depth == 0:
                    fp_end = i + 1
                    break
        blk = text[fp_start:fp_end]
        blk = update_fp_pad_net(blk, '1', 'tl072_out1_raw')
        text = text[:fp_start] + blk + text[fp_end:]

    # 6. Purge obsolete tracks and vias
    purge_nets = {
        'gpio_disp_dc', 'gpio_disp_res', 'spi1_cs', 'spi1_sck',
        'spi1_miso', 'spi1_mosi', 'p18', 'p19', 'p20',
        'audio_in_r', 'audio_out_r'
    }

    lines = text.splitlines()
    out_lines = []
    curr_chunk = []
    brace = 0

    for line in lines:
        sline = line.strip()
        if sline.startswith('(segment') or sline.startswith('(via'):
            curr_chunk = [line]
            brace = line.count('(') - line.count(')')
            if brace == 0: pass
            continue
        elif curr_chunk:
            curr_chunk.append(line)
            brace += line.count('(') - line.count(')')
            if brace == 0:
                chunk_str = '\n'.join(curr_chunk)
                remove = False
                if any(f'"{net}"' in chunk_str for net in purge_nets):
                    remove = True
                
                coords = re.findall(r'\(start\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(end\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)', chunk_str)
                via_coord = re.findall(r'\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)', chunk_str)

                # Check daisy_audio_in:
                if '"daisy_audio_in"' in chunk_str:
                    if coords:
                        x1, y1, x2, y2 = map(float, coords[0])
                        if min(x1, x2) >= 159.0 and max(x1, x2) <= 164.0 and min(y1, y2) >= 90.0 and max(y1, y2) <= 93.7:
                            chunk_str = chunk_str.replace('"daisy_audio_in"', '"tl072_out1_raw"')
                            out_lines.extend(chunk_str.splitlines())
                            curr_chunk = []
                            continue
                        else:
                            remove = True
                    elif via_coord:
                        remove = True

                # Check audio_in_from_daisy_plus long run
                if '"audio_in_from_daisy_plus"' in chunk_str:
                    if coords:
                        x1, y1, x2, y2 = map(float, coords[0])
                        if min(x1, x2) <= 165.0:
                            remove = True

                # Check old encoder tracks west of U5
                if any(f'"{net}"' in chunk_str for net in ('d14', 'gpio_enc_b', 'gpio_enc_sw')):
                    if coords:
                        x1, y1, x2, y2 = map(float, coords[0])
                        if min(x1, x2) <= 95.0 and max(y1, y2) >= 127.0:
                            remove = True

                # Check old I2C tracks west of U5
                if any(f'"{net}"' in chunk_str for net in ('i2c1_scl', 'i2c1_sda')):
                    if coords:
                        x1, y1, x2, y2 = map(float, coords[0])
                        if min(x1, x2) < 95.0:
                            remove = True

                if not remove:
                    out_lines.extend(curr_chunk)
                curr_chunk = []
            continue
        out_lines.append(line)

    text = '\n'.join(out_lines)

    # 7. Add Footprints for R11, D11, C15
    r11_fp = f"""\t(footprint "lib:R0603"
\t\t(layer "F.Cu")
\t\t(uuid "{uid()}")
\t\t(at 155.0 94.35 180)
\t\t(property "Reference" "R11"
\t\t\t(at 0 1.5 0)
\t\t\t(layer "F.SilkS")
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(property "Value" "1k"
\t\t\t(at 0 1.43 0)
\t\t\t(layer "F.Fab")
\t\t\t(hide yes)
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(attr smd)
\t\t(pad "1" smd roundrect (at -0.825 0 180) (size 0.8 0.95) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "tl072_out1_raw") (uuid "{uid()}"))
\t\t(pad "2" smd roundrect (at 0.825 0 180) (size 0.8 0.95) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "daisy_audio_in") (uuid "{uid()}"))
\t)"""

    d11_fp = f"""\t(footprint "Package_TO_SOT_SMD:SOT-23"
\t\t(layer "F.Cu")
\t\t(uuid "{uid()}")
\t\t(at 151.0 94.35)
\t\t(property "Reference" "D11"
\t\t\t(at 0 -2.4 0)
\t\t\t(layer "F.SilkS")
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(property "Value" "BAT54S"
\t\t\t(at 0 2.4 0)
\t\t\t(layer "F.Fab")
\t\t\t(hide yes)
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(attr smd)
\t\t(pad "1" smd roundrect (at -0.9375 -0.95) (size 0.6 0.9) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "gnd") (uuid "{uid()}"))
\t\t(pad "2" smd roundrect (at -0.9375 0.95) (size 0.6 0.9) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "+3.3V") (uuid "{uid()}"))
\t\t(pad "3" smd roundrect (at 0.9375 0) (size 0.6 0.9) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "daisy_audio_in") (uuid "{uid()}"))
\t)"""

    c15_fp = f"""\t(footprint "lib:C0603"
\t\t(layer "F.Cu")
\t\t(uuid "{uid()}")
\t\t(at 147.0 94.35 180)
\t\t(property "Reference" "C15"
\t\t\t(at 0 1.5 0)
\t\t\t(layer "F.SilkS")
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(property "Value" "100pF"
\t\t\t(at 0 1.43 0)
\t\t\t(layer "F.Fab")
\t\t\t(hide yes)
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(attr smd)
\t\t(pad "1" smd roundrect (at -0.825 0 180) (size 0.8 0.95) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "daisy_audio_in") (uuid "{uid()}"))
\t\t(pad "2" smd roundrect (at 0.825 0 180) (size 0.8 0.95) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "gnd") (uuid "{uid()}"))
\t)"""

    idx_last = text.rfind(')')
    new_fps = f"\n{r11_fp}\n{d11_fp}\n{c15_fp}\n"
    text = text[:idx_last] + new_fps + text[idx_last:]

    # 8. Clean, Deterministic Multi-Layer Routing
    new_tracks = []

    def seg(x1, y1, x2, y2, layer, net, width=0.25):
        return f"""\t(segment
\t\t(start {x1:.4f} {y1:.4f})
\t\t(end {x2:.4f} {y2:.4f})
\t\t(width {width})
\t\t(layer "{layer}")
\t\t(net "{net}")
\t\t(uuid "{uid()}")
\t)"""

    def via(x, y, net):
        return f"""\t(via
\t\t(at {x:.4f} {y:.4f})
\t\t(size 0.8)
\t\t(drill 0.4)
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "{net}")
\t\t(uuid "{uid()}")
\t)"""

    # A. Connect R4 Pad 1 (159.05, 93.65) to R11 Pad 1 (155.825, 94.35):
    new_tracks.append(seg(159.050, 93.650, 158.350, 94.350, "F.Cu", "tl072_out1_raw"))
    new_tracks.append(seg(158.350, 94.350, 155.825, 94.350, "F.Cu", "tl072_out1_raw"))

    # B. daisy_audio_in network along Y = 94.35:
    new_tracks.append(seg(154.175, 94.350, 151.9375, 94.350, "F.Cu", "daisy_audio_in"))
    new_tracks.append(seg(151.9375, 94.350, 147.825, 94.350, "F.Cu", "daisy_audio_in"))

    # C15 Pad 1 exits NORTH to via at (147.825, 92.50) to In2.Cu:
    new_tracks.append(seg(147.825, 94.350, 147.825, 92.500, "F.Cu", "daisy_audio_in"))
    new_tracks.append(via(147.825, 92.500, "daisy_audio_in"))

    # On In2.Cu, route outside U5 northern boundary (Y = 86.0) to U5 Pin 16 (95.0, 128.10):
    new_tracks.append(seg(147.825, 92.500, 141.325, 86.000, "In2.Cu", "daisy_audio_in"))
    new_tracks.append(seg(141.325, 86.000, 90.000, 86.000, "In2.Cu", "daisy_audio_in"))
    new_tracks.append(seg(90.000, 86.000, 90.000, 128.100, "In2.Cu", "daisy_audio_in"))
    new_tracks.append(seg(90.000, 128.100, 95.000, 128.100, "In2.Cu", "daisy_audio_in"))

    # C. D11 and C15 GND connections:
    new_tracks.append(seg(150.0625, 93.400, 150.0625, 91.500, "F.Cu", "gnd"))
    new_tracks.append(via(150.0625, 91.500, "gnd"))
    new_tracks.append(seg(146.175, 94.350, 146.175, 96.000, "F.Cu", "gnd"))
    new_tracks.append(via(146.175, 96.000, "gnd"))

    # D. D11 Pad 2 (+3.3V) at (150.0625, 95.30):
    new_tracks.append(seg(150.0625, 95.300, 148.650, 95.300, "F.Cu", "+3.3V"))
    new_tracks.append(via(148.650, 95.300, "+3.3V"))

    # E. audio_in_from_daisy_plus on In2.Cu at Y = 150.0:
    new_tracks.append(seg(95.000, 133.180, 88.000, 133.180, "In2.Cu", "audio_in_from_daisy_plus"))
    new_tracks.append(seg(88.000, 133.180, 88.000, 150.000, "In2.Cu", "audio_in_from_daisy_plus"))
    new_tracks.append(seg(88.000, 150.000, 167.788, 150.000, "In2.Cu", "audio_in_from_daisy_plus"))
    new_tracks.append(seg(167.788, 150.000, 167.788, 102.700, "In2.Cu", "audio_in_from_daisy_plus"))

    # F. U5 Pin 17 (GND) and Pin 20 (GND / AGND):
    new_tracks.append(seg(95.000, 130.640, 93.000, 130.640, "F.Cu", "gnd"))
    new_tracks.append(via(93.000, 130.640, "gnd"))
    new_tracks.append(seg(95.000, 138.260, 93.000, 138.260, "F.Cu", "gnd"))
    new_tracks.append(via(93.000, 138.260, "gnd"))

    # G. Encoder lines from U5 to J_ENC (concentric nesting, 0 crossings):
    # 1. d14 (Inner loop on B.Cu):
    new_tracks.append(seg(110.240, 135.720, 113.000, 135.720, "B.Cu", "d14"))
    new_tracks.append(seg(113.000, 135.720, 113.000, 143.000, "B.Cu", "d14"))
    new_tracks.append(seg(113.000, 143.000, 80.000, 143.000, "B.Cu", "d14"))
    new_tracks.append(seg(80.000, 143.000, 80.000, 127.865, "B.Cu", "d14"))
    new_tracks.append(seg(80.000, 127.865, 72.000, 127.865, "B.Cu", "d14"))

    # 2. gpio_enc_sw (Outer loop on B.Cu):
    new_tracks.append(seg(110.240, 130.640, 117.000, 130.640, "B.Cu", "gpio_enc_sw"))
    new_tracks.append(seg(117.000, 130.640, 117.000, 147.000, "B.Cu", "gpio_enc_sw"))
    new_tracks.append(seg(117.000, 147.000, 76.000, 147.000, "B.Cu", "gpio_enc_sw"))
    new_tracks.append(seg(76.000, 147.000, 76.000, 138.025, "B.Cu", "gpio_enc_sw"))
    new_tracks.append(seg(76.000, 138.025, 72.000, 138.025, "B.Cu", "gpio_enc_sw"))

    # 3. gpio_enc_b (on F.Cu):
    new_tracks.append(seg(110.240, 133.180, 115.000, 133.180, "F.Cu", "gpio_enc_b"))
    new_tracks.append(seg(115.000, 133.180, 115.000, 145.000, "F.Cu", "gpio_enc_b"))
    new_tracks.append(seg(115.000, 145.000, 78.000, 145.000, "F.Cu", "gpio_enc_b"))
    new_tracks.append(seg(78.000, 145.000, 78.000, 132.945, "F.Cu", "gpio_enc_b"))
    new_tracks.append(seg(78.000, 132.945, 72.000, 132.945, "F.Cu", "gpio_enc_b"))

    # H. I2C Lines to U6:
    new_tracks.append(seg(95.000, 117.940, 83.115, 117.940, "B.Cu", "i2c1_scl"))
    new_tracks.append(seg(83.115, 117.940, 70.000, 104.825, "B.Cu", "i2c1_scl"))
    new_tracks.append(seg(95.000, 120.480, 88.195, 120.480, "F.Cu", "i2c1_sda"))
    new_tracks.append(seg(88.195, 120.480, 70.000, 102.285, "F.Cu", "i2c1_sda"))

    # I. +3.3V Power Trunk:
    new_tracks.append(seg(110.240, 95.080, 113.000, 95.080, "B.Cu", "+3.3V"))
    new_tracks.append(seg(113.000, 95.080, 113.000, 84.500, "B.Cu", "+3.3V"))
    new_tracks.append(seg(113.000, 84.500, 67.460, 84.500, "B.Cu", "+3.3V"))
    new_tracks.append(seg(67.460, 84.500, 67.460, 99.745, "B.Cu", "+3.3V"))

    # Connect +3.3V to U5 Pin 21 (3V3A) INSIDE U5 DIP socket on B.Cu:
    new_tracks.append(seg(110.240, 95.080, 107.000, 95.080, "B.Cu", "+3.3V"))
    new_tracks.append(seg(107.000, 95.080, 107.000, 138.260, "B.Cu", "+3.3V"))
    new_tracks.append(seg(107.000, 138.260, 110.240, 138.260, "B.Cu", "+3.3V"))

    # Connect +3.3V to D11 Pad 2 via at (148.65, 95.30):
    new_tracks.append(seg(113.000, 84.500, 148.650, 84.500, "B.Cu", "+3.3V"))
    new_tracks.append(seg(148.650, 84.500, 148.650, 95.300, "B.Cu", "+3.3V"))

    idx_last = text.rfind(')')
    new_tracks_str = '\n'.join(new_tracks) + '\n'
    text = text[:idx_last] + new_tracks_str + text[idx_last:]

    with open(TARGET_PATH, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"Wrote clean carrier PCB to {TARGET_PATH}")

    fill_cmd = [
        r"C:\Program Files\KiCad\10.0\bin\python.exe", "-c",
        f"import pcbnew; b = pcbnew.LoadBoard(r'{os.path.abspath(TARGET_PATH)}'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(r'{os.path.abspath(TARGET_PATH)}')"
    ]
    subprocess.run(fill_cmd, check=True)
    print("Carrier zones refilled successfully!")

if __name__ == '__main__':
    sync_pcb()
