"""
Generate full multi-board KiCad 3D assembly files for the ICIO500 modular satellite architecture:
  1. kicad/icio500_satellite_wood_3d.kicad_pcb
     (Carrier + Encoder + 0.8 mm Matte-Black Satellite PCB + 0.15 mm Diffuser Film + 3.175 mm Walnut Slots + Capstan Knob)
  2. kicad/icio500_satellite_acrylic_3d.kicad_pcb
     (Carrier + Encoder + 0.8 mm Matte-Black Satellite PCB + 3.000 mm Dead-Front Smoked Acrylic + Capstan Knob)

All models live under kicad/3d_models/ and are referenced with portable ${KIPRJMOD}/3d_models/... paths.
Does NOT modify in-production kicad/icio500.kicad_pcb, kicad/encoder_board.kicad_pcb, or fabrication/in_production/.
"""

import math
import os
import re
import shutil
import subprocess
import tempfile
import uuid as uuid_mod
import pcbnew

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"

W_FP = 38.10
H_FP = 133.35

HOLES_MOUNT_PCB = [
    ("MH1",      19.050,   3.960, 3.200),
    ("MH2",      19.050, 129.390, 3.200),
    ("MH_TOP_L",  5.050,  24.000, 2.700),
    ("MH_TOP_R", 33.050,  24.000, 2.700),
    ("ENC",      19.050, 109.350, 7.200),
]

SKIRT_PORTS_PCB = [
    ("D11", 19.050,  99.350, 2.400),
    ("D12", 27.710, 104.350, 2.400),
    ("D13", 27.710, 114.350, 2.400),
    ("D14", 19.050, 119.350, 2.400),
    ("D15", 10.390, 114.350, 2.400),
    ("D16", 10.390, 104.350, 2.400),
]

VU_SLOTS_PCB = [(f"D{i + 1}", 19.050, 20.000 + 8.000 * i, 7.200, 2.400) for i in range(10)]
DIFFUSER_RECT = (8.000, 16.500, 30.100, 122.000, 0.500)


def mm(val):
    return int(round(val * 1e6))


def add_rounded_rect_edges(board, x0, y0, x1, y1, r):
    """Add closed Edge.Cuts segments & corner arcs (clockwise in +Y-down PCB coords)."""
    if r <= 1e-6:
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for i in range(4):
            p1, p2 = pts[i], pts[(i + 1) % 4]
            seg = pcbnew.PCB_SHAPE(board)
            seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
            seg.SetStart(pcbnew.VECTOR2I(mm(p1[0]), mm(p1[1])))
            seg.SetEnd(pcbnew.VECTOR2I(mm(p2[0]), mm(p2[1])))
            seg.SetLayer(pcbnew.Edge_Cuts)
            seg.SetWidth(mm(0.10))
            board.Add(seg)
        return

    straight_edges = [
        ((x0 + r, y0),     (x1 - r, y0)),
        ((x1,     y0 + r), (x1,     y1 - r)),
        ((x1 - r, y1),     (x0 + r, y1)),
        ((x0,     y1 - r), (x0,     y0 + r)),
    ]
    for sp, ep in straight_edges:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(mm(sp[0]), mm(sp[1])))
        seg.SetEnd(pcbnew.VECTOR2I(mm(ep[0]), mm(ep[1])))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.10))
        board.Add(seg)

    corners = [
        ((x1 - r, y0 + r), (x1 - r, y0),     (x1,     y0 + r)),
        ((x1 - r, y1 - r), (x1,     y1 - r), (x1 - r, y1)),
        ((x0 + r, y1 - r), (x0 + r, y1),     (x0,     y1 - r)),
        ((x0 + r, y0 + r), (x0,     y0 + r), (x0 + r, y0)),
    ]
    k = math.sqrt(0.5)
    for (cx, cy), sp, ep in corners:
        mx = cx + k * ((sp[0] - cx) + (ep[0] - cx))
        my = cy + k * ((sp[1] - cy) + (ep[1] - cy))
        arc = pcbnew.PCB_SHAPE(board)
        arc.SetShape(pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry(
            pcbnew.VECTOR2I(mm(sp[0]), mm(sp[1])),
            pcbnew.VECTOR2I(mm(mx), mm(my)),
            pcbnew.VECTOR2I(mm(ep[0]), mm(ep[1])),
        )
        arc.SetLayer(pcbnew.Edge_Cuts)
        arc.SetWidth(mm(0.10))
        board.Add(arc)


def add_circle_cutout(board, cx, cy, diam):
    circ = pcbnew.PCB_SHAPE(board)
    circ.SetShape(pcbnew.SHAPE_T_CIRCLE)
    circ.SetFilled(False)
    circ.SetCenter(pcbnew.VECTOR2I(mm(cx), mm(cy)))
    circ.SetRadius(mm(diam / 2.0))
    circ.SetLayer(pcbnew.Edge_Cuts)
    circ.SetWidth(mm(0.10))
    board.Add(circ)


def add_horizontal_slot_edges(board, cx, cy, width, height):
    """Draw closed stadium/pill slot using 2 horizontal lines and 2 exact 180-deg arcs."""
    r = height / 2.0
    half_straight = (width - height) / 2.0
    x_l = cx - half_straight
    x_r = cx + half_straight

    for (x1, y1), (x2, y2) in [
        ((x_l, cy - r), (x_r, cy - r)),
        ((x_r, cy + r), (x_l, cy + r)),
    ]:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.10))
        board.Add(seg)

    for sp, mp, ep in [
        ((x_r, cy - r), (x_r + r, cy), (x_r, cy + r)),
        ((x_l, cy + r), (x_l - r, cy), (x_l, cy - r)),
    ]:
        arc = pcbnew.PCB_SHAPE(board)
        arc.SetShape(pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry(
            pcbnew.VECTOR2I(mm(sp[0]), mm(sp[1])),
            pcbnew.VECTOR2I(mm(mp[0]), mm(mp[1])),
            pcbnew.VECTOR2I(mm(ep[0]), mm(ep[1])),
        )
        arc.SetLayer(pcbnew.Edge_Cuts)
        arc.SetWidth(mm(0.10))
        board.Add(arc)


def export_panel_vrml(out_wrl, thickness_mm, material_props, rects, circles, slots=None):
    """
    Build a temporary KiCad board with the exact front-panel Edge.Cuts, export it to VRML
    (tenths of inch), strip extra F.Mask/B.Mask skin shapes so only the solid body (SHAPE_1 + SHAPE_2)
    remains, rescale Z to exact target thickness_mm, and apply the material properties.
    Returns (z_min_mm, z_max_mm).
    """
    with tempfile.TemporaryDirectory() as td:
        b = pcbnew.BOARD()
        b.SetCopperLayerCount(2)
        b.GetDesignSettings().SetBoardThickness(mm(thickness_mm))
        for x0, y0, x1, y1, r in rects:
            add_rounded_rect_edges(b, x0, y0, x1, y1, r)
        for cx, cy, diam in circles:
            add_circle_cutout(b, cx, cy, diam)
        for scx, scy, sw, sh in (slots or []):
            add_horizontal_slot_edges(b, scx, scy, sw, sh)

        tmp_pcb = os.path.join(td, "panel.kicad_pcb")
        tmp_wrl = os.path.join(td, "panel.wrl")
        b.Save(tmp_pcb)
        subprocess.run(
            [KICAD_CLI, "pcb", "export", "vrml", "--force", "--units", "tenths", "-o", tmp_wrl, tmp_pcb],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        with open(tmp_wrl, "r", encoding="utf-8") as f:
            wt = f.read()

    # Keep only TXFM_1 -> TXFM_2 -> (SHAPE_1 + SHAPE_2) and discard F.Mask/B.Mask overlays (TXFM_3+)
    cut_idx = wt.find("DEF TXFM_3 Transform {")
    if cut_idx != -1:
        wt = wt[:cut_idx].rstrip() + "\n] }\n"

    # Measure current Z half-extent inside Coordinate point blocks (tenths of inch) and rescale to exact thickness
    raw_zs = []
    for m in re.finditer(r'point\s*\[([^\]]+)\]', wt, re.DOTALL):
        for _, _, z_s in re.findall(r'([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)', m.group(1)):
            raw_zs.append(float(z_s))
    cur_half_z = max(abs(min(raw_zs)), abs(max(raw_zs)))
    target_half_z_tenths = (thickness_mm / 2.0) / 2.54
    z_scale = target_half_z_tenths / cur_half_z

    def _rescale_point_block(match):
        body = match.group(1)
        def _repl_triple(tm):
            x_s, y_s, z_s = tm.group(1), tm.group(2), tm.group(3)
            new_z = float(z_s) * z_scale
            return f"{x_s} {y_s} {new_z:.8f}"
        scaled = re.sub(r'([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)', _repl_triple, body)
        return f"point [{scaled}]"

    wt = re.sub(r'point\s*\[([^\]]+)\]', _rescale_point_block, wt, flags=re.DOTALL)

    # Patch Material block
    mat_block = (
        "material Material {\n"
        f"   ambientIntensity {material_props['ambientIntensity']}\n"
        f"   diffuseColor {material_props['diffuseColor']}\n"
        f"   emissiveColor {material_props.get('emissiveColor', '0 0 0')}\n"
        f"   shininess {material_props['shininess']}\n"
        f"   specularColor {material_props['specularColor']}\n"
        f"   transparency {material_props['transparency']}\n"
        "}"
    )
    wt = re.sub(r'material Material\s*\{[^}]+\}', mat_block, wt)

    with open(out_wrl, "w", encoding="utf-8", newline="\n") as f:
        f.write(wt)

    # Verify exact final Z bounds (mm)
    final_zs = []
    for m in re.finditer(r'point\s*\[([^\]]+)\]', wt, re.DOTALL):
        for _, _, z_s in re.findall(r'([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)', m.group(1)):
            final_zs.append(float(z_s) * 2.54)
    z_min_mm, z_max_mm = min(final_zs), max(final_zs)
    print(f"Generated {out_wrl} ({os.path.getsize(out_wrl):,} B) Z=[{z_min_mm:.4f}..{z_max_mm:.4f}] mm")
    return z_min_mm, z_max_mm


def measure_satellite_step_bounds(step_path):
    """Measure Satellite PCB core Z bounds along its Edge.Cuts outline (X=1.5..36.6, Y=-123.35..-10.0)."""
    board_zs = set()
    with open(step_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.search(
                r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*\)\s*\)",
                line,
            )
            if m:
                x, y, z = float(m.group(1)), float(m.group(2)), float(m.group(3))
                if (abs(x - 1.5) < 0.02 or abs(x - 36.6) < 0.02) and -123.4 <= y <= -9.9:
                    board_zs.add(round(z, 4))
    z_min_sat = min(board_zs)
    z_max_sat = max(board_zs)
    print(f"Measured {step_path} board core Z=[{z_min_sat:.4f}..{z_max_sat:.4f}] mm")
    return z_min_sat, z_max_sat


def build_dummy_footprint(models):
    """Return KiCad DUMMY footprint s-expression at Carrier front ear origin (54.175, 102.85)."""
    fpx = 54.175
    fpy = 102.850
    fp_uuid = str(uuid_mod.uuid4())
    blocks = []
    for mpath, (ox, oy, oz), (rx, ry, rz) in models:
        blocks.append(
            f'\t\t(model "{mpath}"\n'
            f'\t\t\t(offset (xyz {ox:.4f} {oy:.4f} {oz:.4f}))\n'
            f'\t\t\t(scale (xyz 1 1 1))\n'
            f'\t\t\t(rotate (xyz {rx} {ry} {rz}))\n'
            f'\t\t)'
        )
    return (
        f'\n\t(footprint "DUMMY"\n'
        f'\t\t(layer "F.Cu")\n'
        f'\t\t(uuid "{fp_uuid}")\n'
        f'\t\t(at {fpx} {fpy})\n'
        f'\t\t(attr exclude_from_pos_files exclude_from_bom)\n'
        + "\n".join(blocks)
        + "\n\t)\n"
    )


def write_assembly_pcb(src_carrier, out_pcb, dummy_block):
    with open(src_carrier, "r", encoding="utf-8") as f:
        lines = f.readlines()

    out_lines = []
    in_dummy = False
    brace_count = 0
    for line in lines:
        if '(footprint "DUMMY"' in line:
            in_dummy = True
            brace_count = 0
        if in_dummy:
            brace_count += line.count("(") - line.count(")")
            if brace_count == 0:
                in_dummy = False
            continue
        out_lines.append(line)

    pcb_data = "".join(out_lines)
    idx = pcb_data.rfind(")")
    pcb_data = pcb_data[:idx] + dummy_block + "\n)\n"
    with open(out_pcb, "w", encoding="utf-8") as f:
        f.write(pcb_data)
    print(f"Saved assembly PCB: {out_pcb}")


def run():
    models_dir = "kicad/3d_models"
    os.makedirs(models_dir, exist_ok=True)

    # 1. Export fresh Satellite PCB STEP & sync production Capstan Knob STEP into kicad/3d_models/
    sat_pcb = "kicad/faceplate_satellite.kicad_pcb"
    sat_step = os.path.join(models_dir, "faceplate_satellite.step")
    subprocess.run(
        [KICAD_CLI, "pcb", "export", "step", "--force", "--subst-models", "-o", sat_step, sat_pcb],
        check=True,
    )
    # Patch default green KiCad FR4/soldermask color in exported STEP to realistic JLCPCB Matte Black
    with open(sat_step, "r", encoding="utf-8", errors="ignore") as f:
        sat_step_txt = f.read()

    def _mask_to_black(m):
        r, g, b = float(m.group(1)), float(m.group(2)), float(m.group(3))
        if abs(r - 0.3133) < 0.03 and g > r and g > b:
            return "COLOUR_RGB('',0.06,0.062,0.068)"
        return m.group(0)

    sat_step_patched, n_mask = re.subn(
        r"COLOUR_RGB\s*\(\s*''\s*,\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*\)",
        _mask_to_black,
        sat_step_txt,
    )
    assert n_mask >= 1, "Failed to locate PCB soldermask COLOUR_RGB in faceplate_satellite.step"
    with open(sat_step, "w", encoding="utf-8") as f:
        f.write(sat_step_patched)
    print(f"Patched Matte Black soldermask in {sat_step}")

    knob_src = os.path.join("fabrication", "in_production", "jlc3dp_knob", "icio500_capstan_knob.step")
    knob_dst = os.path.join(models_dir, "icio500_capstan_knob.step")
    shutil.copyfile(knob_src, knob_dst)

    # 2. Clean superseded VRML models and export Satin Walnut slots + Diffuser Film + Smoked Acrylic
    for old_wrl in ("faceplate_wood_baltic_birch.wrl", "faceplate_vu_inlay_smoked_acrylic.wrl"):
        op = os.path.join(models_dir, old_wrl)
        if os.path.exists(op):
            os.remove(op)

    wood_wrl = os.path.join(models_dir, "faceplate_wood_walnut_slots.wrl")
    diffuser_wrl = os.path.join(models_dir, "faceplate_diffuser_film.wrl")
    acrylic_wrl = os.path.join(models_dir, "faceplate_acrylic_smoked.wrl")

    z_wood_min, z_wood_max = export_panel_vrml(
        wood_wrl,
        3.175,
        {
            "ambientIntensity": "0.30",
            "diffuseColor": "0.36 0.21 0.11",
            "specularColor": "0.14 0.10 0.07",
            "shininess": "0.22",
            "transparency": "0",
        },
        rects=[(0.0, 0.0, W_FP, H_FP, 0.50)],
        circles=[(cx, cy, d) for _, cx, cy, d in HOLES_MOUNT_PCB + SKIRT_PORTS_PCB],
        slots=[(cx, cy, sw, sh) for _, cx, cy, sw, sh in VU_SLOTS_PCB],
    )

    z_diff_min, z_diff_max = export_panel_vrml(
        diffuser_wrl,
        0.150,
        {
            "ambientIntensity": "0.65",
            "diffuseColor": "0.92 0.93 0.95",
            "specularColor": "0.25 0.25 0.25",
            "shininess": "0.30",
            "transparency": "0.22",
        },
        rects=[DIFFUSER_RECT],
        circles=[(19.050, 109.350, 7.400)],
    )

    z_acr_min, z_acr_max = export_panel_vrml(
        acrylic_wrl,
        3.000,
        {
            "ambientIntensity": "0.08",
            "diffuseColor": "0.015 0.018 0.022",
            "specularColor": "0.75 0.78 0.82",
            "shininess": "0.92",
            "transparency": "0.20",
        },
        rects=[(0.0, 0.0, W_FP, H_FP, 0.50)],
        circles=[(cx, cy, d) for _, cx, cy, d in HOLES_MOUNT_PCB],
    )

    # 3. Compute exact KiCad 3D GUI/Render offsets at DUMMY (54.175, 102.85) under rotate (0, 90, 0)
    _, z_sat_max = measure_satellite_step_bounds(sat_step)
    sat_ox = 0.675
    x_sat_front = sat_ox - z_sat_max  # DUMMY-relative X of satellite F.Cu front face

    ox_diff = x_sat_front + z_diff_min
    x_diff_front = ox_diff - z_diff_max
    diff_cy_pcb = 0.5 * (DIFFUSER_RECT[1] + DIFFUSER_RECT[3])
    oy_diff = (H_FP / 2.0) - diff_cy_pcb  # Center diffuser strip accurately in PCB Y

    ox_wood = x_diff_front + z_wood_min
    x_wood_front = ox_wood - z_wood_max
    ox_knob_wood = x_wood_front - 1.000

    ox_acr = x_sat_front + z_acr_min
    x_acr_front = ox_acr - z_acr_max
    ox_knob_acr = x_acr_front - 1.000

    print(f"Satellite F.Cu X_local = {x_sat_front:.4f} mm")
    print(f"Diffuser     ox={ox_diff:.4f}, oy={oy_diff:.4f}, front X_local={x_diff_front:.4f}")
    print(f"Wood panel   ox={ox_wood:.4f}, front X_local={x_wood_front:.4f}, knob ox={ox_knob_wood:.4f}")
    print(f"Acrylic      ox={ox_acr:.4f}, front X_local={x_acr_front:.4f}, knob ox={ox_knob_acr:.4f}")

    enc_model = ("${KIPRJMOD}/3d_models/encoder_board.step", (7.175, -32.675, 0.240), (0, 90, 0))
    sat_model = ("${KIPRJMOD}/3d_models/faceplate_satellite.step", (sat_ox, 66.675, -8.740), (0, 90, 0))

    wood_models = [
        enc_model,
        sat_model,
        ("${KIPRJMOD}/3d_models/faceplate_diffuser_film.wrl", (ox_diff, oy_diff, 10.310), (0, 90, 0)),
        ("${KIPRJMOD}/3d_models/faceplate_wood_walnut_slots.wrl", (ox_wood, 0.000, 10.310), (0, 90, 0)),
        ("${KIPRJMOD}/3d_models/icio500_capstan_knob.step", (ox_knob_wood, -42.675, 10.310), (0, 90, 0)),
    ]

    acrylic_models = [
        enc_model,
        sat_model,
        ("${KIPRJMOD}/3d_models/faceplate_acrylic_smoked.wrl", (ox_acr, 0.000, 10.310), (0, 90, 0)),
        ("${KIPRJMOD}/3d_models/icio500_capstan_knob.step", (ox_knob_acr, -42.675, 10.310), (0, 90, 0)),
    ]

    src_carrier = "kicad/icio500.kicad_pcb"
    write_assembly_pcb(src_carrier, "kicad/icio500_satellite_wood_3d.kicad_pcb", build_dummy_footprint(wood_models))
    write_assembly_pcb(src_carrier, "kicad/icio500_satellite_acrylic_3d.kicad_pcb", build_dummy_footprint(acrylic_models))


if __name__ == "__main__":
    run()
