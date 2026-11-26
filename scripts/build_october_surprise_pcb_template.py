#!/usr/bin/env python3
"""Create mechanical starter kicad/october_surprise.kicad_pcb for F8 Forward-Annotation.

Strictly adheres to AGENTS.md Rule #2 (Schematic-First Workflow Only):
- Contains ZERO electrical signal/power nets and ZERO copper traces.
- Preserves ONLY verified VPR-500 Edge.Cuts, Dwgs.User mechanical notes, and locked
  mechanical/interconnect footprints (MH1, MH2, J1, U6, J_ENC, U1, J_DAISY_L, J_DAISY_R)
  with `(net 0 "")` and matching schematic `(path ...)` UUIDs so pressing F8
  (Update PCB from Schematic) in KiCad GUI pulls all nets/components cleanly in-place.
"""

import os
import re
import uuid

ROOT_UUID = "a1b2c3d4-0001-4000-8000-000000000001"
REV1_PCB = os.path.join("archive", "rev1_bad_carrier", "kicad_rev1", "icio500.kicad_pcb")
SCH_PATH = os.path.join("kicad", "october_surprise.kicad_sch")
OUT_PCB = os.path.join("kicad", "october_surprise.kicad_pcb")
PINSOCKET_MOD = r"C:\Program Files\KiCad\10.0\share\kicad\footprints\Connector_PinSocket_2.54mm.pretty\PinSocket_1x20_P2.54mm_Vertical.kicad_mod"


def extract_balanced(text, prefix, start_idx=0):
    pos = text.find(prefix, start_idx)
    if pos == -1:
        return None, -1
    d = 0
    for i in range(pos, len(text)):
        if text[i] == "(":
            d += 1
        elif text[i] == ")":
            d -= 1
            if d == 0:
                return text[pos : i + 1], i + 1
    return None, -1


def parse_sch_uuids(sch_txt):
    """Map schematic Reference -> symbol UUID (first unit) for F8 in-place path matching."""
    out = {}
    idx = 0
    while True:
        blk, nxt = extract_balanced(sch_txt, "  (symbol (", idx)
        if blk is None:
            break
        idx = nxt
        rm = re.search(r'\(property "Reference" "([^"]+)"', blk)
        um = re.search(r'\(dnp no\) \(uuid "([^"]+)"\)', blk)
        if rm and um and rm.group(1) not in out:
            out[rm.group(1)] = um.group(1)
    return out


def strip_nets_and_update_fp(fp_txt, new_ref, new_val, new_lib, sch_uuid, at_override=None):
    # Remove any (net ...) attributes from pads (zero net patching!)
    s = re.sub(r'\n\t*\(net\s+(?:\d+\s+)?"[^"]*"\)', "", fp_txt)
    s = re.sub(r'\s*\(net\s+(?:\d+\s+)?"[^"]*"\)', "", s)
    # Replace footprint library id
    first_nl = s.find("\n")
    s = f'\t(footprint "{new_lib}"' + s[first_nl:]
    if at_override:
        s = re.sub(r'\n\t\t\(at [^\)]+\)', f"\n\t\t(at {at_override})", s, count=1)
    # Update Reference & Value properties
    s = re.sub(r'(\(property "Reference" ")[^"]+(")', rf"\g<1>{new_ref}\g<2>", s, count=1)
    if new_val:
        s = re.sub(r'(\(property "Value" ")[^"]+(")', rf"\g<1>{new_val}\g<2>", s, count=1)
    # Replace or insert (path "/ROOT/UUID") and normalize (sheetname "Root")
    path_str = f'/{ROOT_UUID}/{sch_uuid}'
    s = re.sub(r'\(sheetname "[^"]+"\)', '(sheetname "Root")', s)
    if re.search(r'\(path "[^"]+"\)', s):
        s = re.sub(r'\(path "[^"]+"\)', f'(path "{path_str}")', s, count=1)
    else:
        s = s.replace('(layer "F.Cu")', f'(layer "F.Cu")\n\t\t(uuid "{uuid.uuid4()}")', 1) if '(uuid ' not in s else s
        s = re.sub(r'(\n\t\t\(tedit [^\)]+\))', rf'\1\n\t\t(path "{path_str}")', s, count=1)
        if f'(path "{path_str}")' not in s:
            s = s.replace('\t\t(attr ', f'\t\t(path "{path_str}")\n\t\t(attr ', 1)
    # Regenerate pad uuids cleanly so everything is unique
    s = re.sub(r'\(uuid "[^"]+"\)', lambda _: f'(uuid "{uuid.uuid4()}")', s)
    return s


def make_pinsocket_fp(mod_txt, ref, val, at_str, sch_uuid):
    s = mod_txt.replace('(footprint "PinSocket_1x20_P2.54mm_Vertical"', f'\t(footprint "Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical"\n\t\t(locked yes)', 1)
    # Indent nicely
    lines = s.splitlines()
    out_lines = [lines[0]]
    inserted_at = False
    for l in lines[1:]:
        if l.strip().startswith('(layer "F.Cu")') and not inserted_at:
            out_lines.append('\t\t' + l.strip())
            out_lines.append(f'\t\t(uuid "{uuid.uuid4()}")')
            out_lines.append(f'\t\t(at {at_str})')
            out_lines.append(f'\t\t(path "/{ROOT_UUID}/{sch_uuid}")')
            out_lines.append('\t\t(sheetname "Root")')
            out_lines.append('\t\t(sheetfile "october_surprise.kicad_sch")')
            inserted_at = True
        else:
            out_lines.append('\t' + l)
    res = "\n".join(out_lines)
    res = res.replace('(property "Reference" "REF**"', f'(property "Reference" "{ref}"')
    res = res.replace('(property "Value" "PinSocket_1x20_P2.54mm_Vertical"', f'(property "Value" "{val}"')
    res = re.sub(r'\(pad ', f'(pad ', res)
    # Remove version/generator lines illegal inside embedded board footprint
    res = re.sub(r'\n\t+\(version [^\)]+\)', "", res)
    res = re.sub(r'\n\t+\(generator "[^"]+"\)', "", res)
    res = re.sub(r'\n\t+\(generator_version "[^"]+"\)', "", res)
    return res


def main():
    rev1 = open(REV1_PCB, encoding="utf-8").read()
    sch = open(SCH_PATH, encoding="utf-8").read()
    sch_uuids = parse_sch_uuids(sch)

    # 1. Board header & setup up to first footprint
    first_fp = rev1.find("\t(footprint ")
    header = rev1[:first_fp]
    header = header.replace('(title "API Series 500 (EDA 306)")', '(title "ICIO500 October Surprise (Carrier Rev 2)")')
    # Only net 0 "" allowed in netlist-free starter
    # Replace net declarations in setup header with just (net 0 "")
    header = re.sub(r'(\n\t\(net \d+ "[^"]*"\))+', '\n\t(net 0 "")', header)

    # 2. Extract Edge.Cuts & Dwgs.User graphics (exclude silkscreen from Rev-1 U2/THAT1200!)
    gr_blocks = []
    idx = 0
    while True:
        m = re.search(r'\t\(gr_(?:line|arc|rect|poly|circle|text)\s+', rev1[idx:])
        if not m:
            break
        pos = idx + m.start()
        blk, end = extract_balanced(rev1, "\t(gr_", pos)
        idx = end
        if '"Edge.Cuts"' in blk or '"Dwgs.User"' in blk:
            gr_blocks.append(blk)

    # 3. Extract locked mechanical footprints & strip nets cleanly
    keep_specs = {
        "MH1": ("MH1", "MountingHole_3.2mm_M3", "MountingHole:MountingHole_3.2mm_M3", None),
        "MH2": ("MH2", "MountingHole_3.2mm_M3", "MountingHole:MountingHole_3.2mm_M3", None),
        "J1": ("J1", "VPR500_Edge_15P", "Cards:EDA_306", None),
        "U6": ("U6", "2541WR-2x10P", "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Horizontal", None),
        "J_ENC": ("J_ENC1", "HX_PZ2.54-1x5P_WZ", "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal", None),
        "U1": ("U1", "TSR_1-2450", "Converter_DCDC:Converter_DCDC_TRACO_TSR-1_THT", None),
    }
    fp_blocks = []
    idx = 0
    while True:
        blk, end = extract_balanced(rev1, "\t(footprint ", idx)
        if blk is None:
            break
        idx = end
        rm = re.search(r'\(property "Reference" "([^"]+)"', blk)
        if rm and rm.group(1) in keep_specs:
            ref, val, lib_id, at_ovr = keep_specs[rm.group(1)]
            fp_blocks.append(strip_nets_and_update_fp(blk, ref, val, lib_id, sch_uuids[ref], at_ovr))

    # 4. Add J_DAISY_L1 (95, 90, 0) & J_DAISY_R1 (110.24, 138.26, 180) aligned to exact Rev-1 DIP-40 socket!
    ps_mod = open(PINSOCKET_MOD, encoding="utf-8").read()
    fp_blocks.append(make_pinsocket_fp(ps_mod, "J_DAISY_L1", "B-2200S20P-A120", "95 90", sch_uuids["J_DAISY_L1"]))
    fp_blocks.append(make_pinsocket_fp(ps_mod, "J_DAISY_R1", "B-2200S20P-A120", "110.24 138.26 180", sch_uuids["J_DAISY_R1"]))

    # 5. Subcircuit #1 (POWER) & #2 (BALANCED INPUT) locked F.SilkS bounding boxes (shifted left clear of J1 silkscreen @ x=177.62)
    pwr_box = (
        f'\t(gr_rect\n'
        f'\t\t(start 140 122)\n'
        f'\t\t(end 176 157)\n'
        f'\t\t(stroke\n\t\t\t(width 0.2)\n\t\t\t(type default)\n\t\t)\n'
        f'\t\t(fill no)\n'
        f'\t\t(layer "F.SilkS")\n'
        f'\t\t(uuid "{uuid.uuid4()}")\n'
        f'\t)'
    )
    pwr_lbl = (
        f'\t(gr_text "POWER"\n'
        f'\t\t(at 147.5 124.5 0)\n'
        f'\t\t(layer "F.SilkS")\n'
        f'\t\t(uuid "{uuid.uuid4()}")\n'
        f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.2 1.2)\n\t\t\t\t(thickness 0.2)\n\t\t\t)\n\t\t)\n'
        f'\t)'
    )
    inp_box = (
        f'\t(gr_rect\n'
        f'\t\t(start 124 94)\n'
        f'\t\t(end 176 118)\n'
        f'\t\t(stroke\n\t\t\t(width 0.2)\n\t\t\t(type default)\n\t\t)\n'
        f'\t\t(fill no)\n'
        f'\t\t(layer "F.SilkS")\n'
        f'\t\t(uuid "{uuid.uuid4()}")\n'
        f'\t)'
    )
    inp_lbl = (
        f'\t(gr_text "BALANCED INPUT"\n'
        f'\t\t(at 135.0 96.5 0)\n'
        f'\t\t(layer "F.SilkS")\n'
        f'\t\t(uuid "{uuid.uuid4()}")\n'
        f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.2 1.2)\n\t\t\t\t(thickness 0.2)\n\t\t\t)\n\t\t)\n'
        f'\t)'
    )
    out_box = (
        f'\t(gr_rect\n'
        f'\t\t(start 124 54)\n'
        f'\t\t(end 176 90)\n'
        f'\t\t(stroke\n\t\t\t(width 0.2)\n\t\t\t(type default)\n\t\t)\n'
        f'\t\t(fill no)\n'
        f'\t\t(layer "F.SilkS")\n'
        f'\t\t(uuid "{uuid.uuid4()}")\n'
        f'\t)'
    )
    out_lbl = (
        f'\t(gr_text "LINE DRIVER"\n'
        f'\t\t(at 134.0 56.5 0)\n'
        f'\t\t(layer "F.SilkS")\n'
        f'\t\t(uuid "{uuid.uuid4()}")\n'
        f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.2 1.2)\n\t\t\t\t(thickness 0.2)\n\t\t\t)\n\t\t)\n'
        f'\t)'
    )
    gr_blocks.extend([pwr_box, pwr_lbl, inp_box, inp_lbl, out_box, out_lbl])

    out = header + "\n".join(fp_blocks) + "\n" + "\n".join(gr_blocks) + "\n)\n"
    open(OUT_PCB, "w", encoding="utf-8").write(out)
    print(f"Wrote netlist-free mechanical starter {OUT_PCB} ({len(out)} bytes, {len(fp_blocks)} footprints, {len(gr_blocks)} mechanical/edge graphics)")


if __name__ == "__main__":
    main()
