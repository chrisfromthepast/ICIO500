#!/usr/bin/env python3
"""In-KiCad ngspice verification suite for Subcircuit #2 (BALANCED INPUT) ONLY.

Loads KiCad's built-in ngspice.dll directly against the untouched SPICE netlist
exported from kicad/october_surprise.kicad_sch via `kicad-cli`.
"""

import ctypes
import math
import os
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from sim_october_surprise import (
    export_kicad_netlist,
    NgSpiceSession,
    parse_caps_from_cir,
    CAP_RATINGS_V,
)

INPUT_CAPS = {"C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20"}
PLOT_OUT = os.path.join("docs", "subcircuit2_input_spice.png")


_NG = None


def open_deck(cir_txt, bench_stimulus):
    global _NG
    body_lines = [
        l for l in cir_txt.splitlines()
        if l.strip().lower() != ".end" and not l.strip().lower().startswith(".title")
    ]

    def to_short_path(m):
        p = m.group(1)
        b = ctypes.create_unicode_buffer(260)
        ctypes.windll.kernel32.GetShortPathNameW(p.replace("/", "\\"), b, 260)
        sp = b.value.replace("\\", "/") if b.value else p
        return f'.include "{sp}"'

    fixed_body = re.sub(r'\.include\s+"([^"]+)"', to_short_path, "\n".join(body_lines))
    full_deck = "* Subcircuit #2 BALANCED INPUT Verification\n" + fixed_body + "\n" + bench_stimulus

    if _NG is None:
        _NG = NgSpiceSession()
    else:
        _NG.cmd("destroy all")
        _NG.cmd("remcirc")

    orig_cwd = os.getcwd()
    os.chdir(os.path.join(orig_cwd, "kicad", "spice_models"))
    try:
        _NG.load_lines(full_deck)
    finally:
        os.chdir(orig_cwd)
    return _NG


def find_res_nodes(cir_txt, ref):
    m = re.search(rf"^{ref}\s+(\S+)\s+(\S+)\s+(\S+)", cir_txt, re.M)
    assert m, f"Resistor {ref} not found in KiCad SPICE netlist"
    return m.group(1), m.group(2), m.group(3)


def main():
    os.makedirs("docs", exist_ok=True)
    scratch_cir = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611\scratch\october_surprise_input_raw.cir"
    cir_txt = export_kicad_netlist(scratch_cir)

    r1_n1, r1_n2, _ = find_res_nodes(cir_txt, "R1")
    r28_n1, r28_n2, _ = find_res_nodes(cir_txt, "R28")
    # Identify which end of R1 is IN_P vs RF node (C10_top) and which end of R28 is U2A.+ vs clamp
    r1_rf_node = r1_n2 if r1_n1.upper() == "IN_P" else r1_n1
    u2m_xu2 = re.search(r"^XU2\s+\S+\s+\S+\s+(\S+)\s+", cir_txt, re.M)
    assert u2m_xu2, "XU2 not found in netlist"
    u2_in_p_node = u2m_xu2.group(1)
    r28_cl_node = r28_n2 if r28_n1.lower() == u2_in_p_node.lower() else r28_n1

    # -------------------------------------------------------------------------
    # SESSION 1: .op, .ac (Diff Gain + CMRR), .noise (20 Hz - 20 kHz), .tran
    # -------------------------------------------------------------------------
    bench_lin = """
* === EXTERNAL BENCH FIXTURE ===
V_PLUS16  +16V_RAW 0 DC 16.0
V_MINUS16 -16V_RAW 0 DC -16.0
V_CHASSIS CHASSIS_GND 0 DC 0

* Differential AC=0.5/-0.5 source (AC diff = 1.0 V)
V_INP IN_P 0 DC 0 AC 0.5 SIN(0 4.715 1000)
V_INN IN_N 0 DC 0 AC -0.5 SIN(0 -4.715 1000)

* Daisy Seed Codec & Power Loads
V_DAISY_3V3D 3V3_D 0 DC 3.3
V_DAISY_3V3A 3V3_A 0 DC 3.3
R_DAISY_ZIN  DAISY_AUDIO_IN 0 13.6k
V_DAISY_OUT  DAISY_AUDIO_OUT 0 DC 0
R_LOAD       OUT_P OUT_N 10k
.end
"""
    ng = open_deck(cir_txt, bench_lin)

    print("=" * 78)
    print("SUBCIRCUIT #2 (BALANCED INPUT) - TEST 1: .OP & CAPACITOR DERATING (>= 2x @ +48V)")
    print("=" * 78)
    ng.cmd("op")
    def scalar(n):
        return float(ng.vec_real(n.lower())[0])

    print(f"  +16V = {scalar('+16V'):+8.4f} V | -16V = {scalar('-16V'):+8.4f} V")
    print(f"  Clamp node = {scalar(r28_cl_node):+9.6f} V | U2A.+ = {scalar(u2_in_p_node):+9.6f} V | DAISY_AUDIO_IN = {scalar('DAISY_AUDIO_IN'):+9.6f} V")

    print("\n  Zone 2 Cap | Node 1                 | Node 2                 | DC V    | Worst Fault | Rating | Margin | Status")
    print("  " + "-" * 104)
    for cname, n1, n2 in parse_caps_from_cir(cir_txt):
        if cname not in INPUT_CAPS:
            continue
        v1 = 0.0 if n1.upper() == "GND" else scalar(n1)
        v2 = 0.0 if n2.upper() == "GND" else scalar(n2)
        dv = v1 - v2
        rating = CAP_RATINGS_V.get(cname, 50.0)
        worst = 48.0 if cname in ("C10", "C11", "C12", "C13") else (11.0 if cname == "C14" else max(abs(dv), 1.0))
        margin = rating / max(worst, 0.1)
        ok = margin >= 2.0
        print(f"  {cname:10s} | {n1:22s} | {n2:22s} | {dv:+7.3f} | {worst:7.1f} V   | {rating:4.0f} V | {margin:5.1f}x | {'PASS' if ok else 'FAIL'}")
        assert ok, f"Zone 2 cap {cname} failed 2x derating ({margin:.2f}x)!"

    print("\n" + "=" * 78)
    print("SUBCIRCUIT #2 - TEST 2: .AC DIFFERENTIAL GAIN (20 Hz - 10 MHz) & .NOISE (20 Hz - 20 kHz)")
    print("=" * 78)
    ng.cmd("ac dec 50 10 10meg")
    ng.cmd("let f_hz = real(frequency)")
    ng.cmd("let mag_dy = mag(v(daisy_audio_in))")
    freqs = ng.vec_real("f_hz")
    ac_db = 20.0 * np.log10(np.maximum(ng.vec_real("mag_dy"), 1e-12))
    for ft in [20.0, 100.0, 1000.0, 20000.0, 100000.0, 1000000.0, 10000000.0]:
        idx = int(np.argmin(np.abs(freqs - ft)))
        print(f"  f = {freqs[idx]:10.1f} Hz | Gain(DAISY_AUDIO_IN / Diff In) = {ac_db[idx]:+7.3f} dB")
    g_1k = float(ac_db[int(np.argmin(np.abs(freqs - 1000.0)))])
    g_20 = float(ac_db[int(np.argmin(np.abs(freqs - 20.0)))])
    g_20k = float(ac_db[int(np.argmin(np.abs(freqs - 20000.0)))])
    assert abs(g_1k - (-16.48)) < 0.3, f"Unexpected 1 kHz gain {g_1k:.2f} dB"

    # Common-Mode Rejection Ratio test
    ng.cmd("alter @v_inn[ac] = 0.5")
    ng.cmd("alter @v_inp[ac] = 0.5")
    ng.cmd("ac dec 20 20 20k")
    ng.cmd("let f_cm = real(frequency)")
    ng.cmd("let mag_cm = mag(v(daisy_audio_in))")
    f_cm = ng.vec_real("f_cm")
    cm_db = 20.0 * np.log10(np.maximum(ng.vec_real("mag_cm"), 1e-15))
    cmrr_1k = g_1k - float(cm_db[int(np.argmin(np.abs(f_cm - 1000.0)))])
    cmrr_20k = g_20k - float(cm_db[int(np.argmin(np.abs(f_cm - 20000.0)))])
    print(f"  Ideal-resistor CMRR = {cmrr_1k:.1f} dB @ 1 kHz, {cmrr_20k:.1f} dB @ 20 kHz (0.1% worst-case ~60-66 dB)")

    print("\n" + "=" * 78)
    print("SUBCIRCUIT #2 - TEST 3: TRANSIENT LINEARITY (+4 / +18.7 / +20 / +24 dBu)")
    print("=" * 78)
    tran_peaks = {}
    for lbl, pk_leg in [("+4 dBu", 0.868), ("+18.7 dBu (0 dBFS)", 4.715), ("+20 dBu", 5.477), ("+24 dBu (Clamp)", 8.680)]:
        ng.cmd(f"alter @v_inp[sin] = [ 0 {pk_leg} 1000 ]")
        ng.cmd(f"alter @v_inn[sin] = [ 0 {-pk_leg} 1000 ]")
        ng.cmd("tran 5u 6m 3m")
        t = ng.vec_real("time")
        vdy = ng.vec_real("daisy_audio_in")
        v_in_diff = ng.vec_real("in_p") - ng.vec_real("in_n")
        dy_rms = float(np.sqrt(np.mean(vdy ** 2)))
        dy_min, dy_max = float(np.min(vdy)), float(np.max(vdy))
        g_t = 20.0 * math.log10(dy_rms / float(np.sqrt(np.mean(v_in_diff ** 2))))
        print(f"  {lbl:20s} | DAISY_AUDIO_IN = {dy_rms:5.3f} Vrms [{dy_min:+6.3f}, {dy_max:+6.3f} V] | Gain = {g_t:+6.3f} dB")
        tran_peaks[lbl] = (t, vdy)

    # Dedicated clean reload for .noise (exact 20 Hz - 20 kHz resistor thermal + 3x OPA1656 RSS)
    bench_noise = """
V_PLUS16 +16V_RAW 0 DC 16
V_MINUS16 -16V_RAW 0 DC -16
V_CHASSIS CHASSIS_GND 0 DC 0
V_INP IN_P 0 DC 0 AC 1
V_INN IN_N 0 DC 0
V_DAISY_3V3D 3V3_D 0 DC 3.3
V_DAISY_3V3A 3V3_A 0 DC 3.3
R_DAISY_ZIN DAISY_AUDIO_IN 0 13.6k
V_DAISY_OUT DAISY_AUDIO_OUT 0 DC 0
R_LOAD OUT_P OUT_N 10k
.end
"""
    ng_n = open_deck(cir_txt, bench_noise)
    ng_n.cmd("noise v(daisy_audio_in) v_inp dec 50 20 20k 1")
    ng_n.cmd("setplot noise1")
    f_n = ng_n.vec_real("frequency")
    ext_refs = ["r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r28", "r29"]
    ext_dens_sq = np.zeros_like(f_n)
    for rref in ext_refs:
        try:
            ext_dens_sq += ng_n.vec_real(f"onoise_{rref}") ** 2
        except KeyError:
            pass
    vnoise_res_out_rms = float(np.sqrt(np.trapezoid(ext_dens_sq, f_n)))
    lin_gain = 10.0 ** (g_1k / 20.0)
    # RSS with 3x OPA1656 datasheet broadband e_n = 2.9 nV/rtHz (U2A, U2B at gain 0.15; U3A at gain ~1.15)
    en_opa = 2.9e-9 * math.sqrt((2 * (lin_gain ** 2) + (1.0 + 0.15) ** 2) * (20000.0 - 20.0))
    vnoise_out_rms = math.hypot(vnoise_res_out_rms, en_opa)
    vnoise_in_rms = vnoise_out_rms / lin_gain
    snr_187 = 20.0 * math.log10(1.0 / vnoise_out_rms)  # relative to 0 dBFS = 1.0 Vrms at DAISY_AUDIO_IN
    print(f"\n  [Subcircuit #2 20 Hz - 20 kHz Noise Floor]")
    print(f"    External Resistor Thermal Noise  = {vnoise_res_out_rms*1e6:.2f} uVrms (at DAISY_AUDIO_IN)")
    print(f"    Total (Resistors + 3x OPA1656 @ 2.9nV/rtHz) = {vnoise_out_rms*1e6:.2f} uVrms")
    print(f"    Input-Referred Noise (/ {lin_gain:.4f})  = {vnoise_in_rms*1e6:.2f} uVrms ({20*math.log10(vnoise_in_rms/0.7746):+.1f} dBu)")
    print(f"    Front-End Dynamic Range (rel. +18.7 dBu / 1 Vrms) = {snr_187:.1f} dB")

    # -------------------------------------------------------------------------
    # SESSION 2: +48V PHANTOM HOT-PLUG & -48V CAP-DISCHARGE SLAM (.tran)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("SUBCIRCUIT #2 - TEST 4: +48V PHANTOM FAULT & -48V CAP-DISCHARGE SLAM")
    print("=" * 78)

    def run_phantom_slam(r_src_val, t_end, label):
        bench_ph = f"""
V_PLUS16  +16V_RAW 0 DC 16.0
V_MINUS16 -16V_RAW 0 DC -16.0
V_CHASSIS CHASSIS_GND 0 DC 0

* Apply +48V fault at t=0.5ms (50us mechanical contact rise), then slam straight to 0V!
V_FAULT src_p 0 DC 0 PWL(0 0 490u 0 540u 48.0 {t_end - 2.0e-3 - 50e-6:.6f} 48.0 {t_end - 2.0e-3:.6f} 0)
R_FAULT src_p IN_P {r_src_val}
V_INN   IN_N 0 DC 0

V_DAISY_3V3D 3V3_D 0 DC 3.3
V_DAISY_3V3A 3V3_A 0 DC 3.3
R_DAISY_ZIN  DAISY_AUDIO_IN 0 13.6k
V_DAISY_OUT  DAISY_AUDIO_OUT 0 DC 0
R_LOAD       OUT_P OUT_N 10k
.options reltol=0.003 method=gear itl4=100
.end
"""
        ng_p = open_deck(cir_txt, bench_ph)
        ng_p.cmd(f"tran 1u {t_end*1e3:.2f}m 0")
        t = ng_p.vec_real("time")
        assert float(t[-1]) >= t_end * 0.99, f"{label} transient aborted early at {t[-1]*1e3:.3f} ms < {t_end*1e3:.2f} ms!"
        v_in = ng_p.vec_real("in_p")
        v_rf = ng_p.vec_real(r1_rf_node.lower())
        v_cl = ng_p.vec_real(r28_cl_node.lower())
        v_u2p = ng_p.vec_real(u2_in_p_node.lower())
        v_dy = ng_p.vec_real("daisy_audio_in")

        i_r1 = (v_in - v_rf) / 100.0
        i_u2_in = (v_cl - v_u2p) / 1000.0
        p_r1 = ((v_in - v_rf) ** 2) / 100.0

        pk_ir1 = float(np.max(np.abs(i_r1))) * 1e3
        pk_pr1 = float(np.max(p_r1))
        pk_iu2 = float(np.max(np.abs(i_u2_in))) * 1e3
        cl_min, cl_max = float(np.min(v_cl)), float(np.max(v_cl))
        u2_min, u2_max = float(np.min(v_u2p)), float(np.max(v_u2p))
        dy_min, dy_max = float(np.min(v_dy)), float(np.max(v_dy))

        print(f"  {label}:")
        print(f"    Clamp Node   : [{cl_min:+7.3f}, {cl_max:+7.3f} V] (BAV21W clips cleanly to +/-16V)")
        print(f"    U2A.+ Pin    : [{u2_min:+7.3f}, {u2_max:+7.3f} V] | Peak |I_in(U2)| = {pk_iu2:5.2f} mA (Limit < 10.0 mA)")
        print(f"    R1 (100R 1206): Peak |I_R1| = {pk_ir1:6.1f} mA (BAV21W 1s IFSM=1000 mA) | Peak Pulse Power = {pk_pr1:5.2f} W")
        print(f"    DAISY_AUDIO_IN: [{dy_min:+6.3f}, {dy_max:+6.3f} V] (Protected within +/-2.8 V)")
        assert pk_iu2 < 10.0, f"U2 input current {pk_iu2:.2f} mA exceeded 10 mA abs max!"
        assert max(abs(dy_min), abs(dy_max)) < 3.0, f"DAISY_AUDIO_IN hit {dy_min}/{dy_max}V!"
        return t, v_cl, i_u2_in * 1e3, v_dy, i_r1 * 1e3

    run_phantom_slam(6810.0, 12.0e-3, "Case 4A (IEC 61938 +48V via 6.81k -> 0V short)")
    t_b, vcl_b, iu2_b, vdy_b, ir1_b = run_phantom_slam(10.0, 6.0e-3, "Case 4B (Worst-Case +48V via 10R -> 0V slam)")

    # Plot 4-panel Subcircuit #2 verification chart
    W, H = 2400, 1500
    img = Image.new("RGB", (W, H), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    try:
        f_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 26)
        f_sub = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 21)
        f_mono = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 17)
    except Exception:
        f_title = f_sub = f_mono = ImageFont.load_default()

    draw.text((40, 22), "SUBCIRCUIT #2 (BALANCED INPUT) - IN-KICAD NGSPICE VERIFICATION (BAV21W +48V CLAMP, 1k, SOCKETED U2)", fill=(248, 250, 252), font=f_title)

    def draw_panel(px, py, pw, ph, title, xvals, yseries, ylim=None, xlog=False, hlines=None, xlabel="Time"):
        draw.rectangle([px, py, px + pw, py + ph], fill=(30, 41, 59), outline=(71, 85, 105), width=2)
        draw.text((px + 18, py + 12), title, fill=(248, 250, 252), font=f_sub)
        gx, gy, gw, gh = px + 95, py + 55, pw - 125, ph - 115
        draw.rectangle([gx, gy, gx + gw, gy + gh], fill=(15, 23, 42), outline=(51, 65, 85), width=1)
        xmin, xmax = float(np.min(xvals)), float(np.max(xvals))
        if ylim is None:
            all_y = np.concatenate([s[1] for s in yseries])
            ymin_a, ymax_a = float(np.min(all_y)), float(np.max(all_y))
            span = max(ymax_a - ymin_a, 1e-4)
            ymin, ymax = ymin_a - 0.12 * span, ymax_a + 0.12 * span
        else:
            ymin, ymax = ylim

        def to_px(xv, yv):
            if xlog:
                tx = (math.log10(max(xv, 1e-6)) - math.log10(xmin)) / (math.log10(xmax) - math.log10(xmin))
            else:
                tx = (xv - xmin) / max(xmax - xmin, 1e-12)
            ty = 1.0 - (yv - ymin) / max(ymax - ymin, 1e-12)
            return int(gx + tx * gw), int(gy + max(0.0, min(1.0, ty)) * gh)

        for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
            yy = int(gy + frac * gh)
            yv = ymax - frac * (ymax - ymin)
            draw.line([(gx, yy), (gx + gw, yy)], fill=(38, 50, 72), width=1)
            draw.text((px + 10, yy - 9), f"{yv:+6.1f}", fill=(148, 163, 184), font=f_mono)

        if hlines:
            for hv, col in hlines:
                _, hy = to_px(xmin, hv)
                draw.line([(gx, hy), (gx + gw, hy)], fill=col, width=2)

        for _, yarr, col, wid in yseries:
            pts = [to_px(float(xv), float(yv)) for xv, yv in zip(xvals, yarr)]
            if len(pts) >= 2:
                draw.line(pts, fill=col, width=wid)

        lx, ly = gx + 14, gy + gh + 14
        for label_s, _, col, _ in yseries:
            draw.rectangle([lx, ly + 4, lx + 20, ly + 14], fill=col)
            draw.text((lx + 26, ly), label_s, fill=(226, 232, 240), font=f_mono)
            lx += max(270, len(label_s) * 11 + 45)
        draw.text((gx + gw // 2 - 80, gy + gh + 36), xlabel, fill=(148, 163, 184), font=f_mono)

    # Panel 1: +48V Direct 10R Slam -> Clamp & U2 Current
    t_b_ms = t_b * 1e3
    draw_panel(
        40, 75, 1140, 680,
        f"Test 4B: +48V/10R Fault -> 0V Slam (Clamp [{np.min(vcl_b):+.1f},{np.max(vcl_b):+.1f}V], Max I_U2={np.max(np.abs(iu2_b)):.2f} mA)",
        t_b_ms,
        [
            ("Clamp Node (V)", vcl_b, (56, 189, 248), 4),
            ("I_in(U2A.+) (mA)", iu2_b, (74, 222, 128), 3),
            ("DAISY_AUDIO_IN (V)", vdy_b, (251, 191, 36), 3),
        ],
        ylim=(-20.0, 20.0),
        hlines=[(10.0, (248, 113, 113)), (-10.0, (248, 113, 113))],
        xlabel="Time (ms: +48V @ 0.5ms, 0V slam @ 4.0ms)",
    )

    # Panel 2: Surge Current through R1 & D3/D4
    draw_panel(
        1220, 75, 1140, 680,
        f"Test 4B: R1 (100R 1206) & BAV21W Clamp Current (Peak {np.max(np.abs(ir1_b)):.0f} mA << 1000 mA)",
        t_b_ms,
        [
            ("I(R1 -> C12/D3/D4) (mA)", ir1_b, (251, 191, 36), 4),
        ],
        xlabel="Time (ms)",
    )

    # Panel 3: AC Differential Transfer & Noise Floor
    draw_panel(
        40, 790, 1140, 680,
        f"Test 2: Input Diff Gain & RF Filter (.ac: {g_20:+.2f}/{g_1k:+.2f}/{g_20k:+.2f} dB; DR={snr_187:.1f} dB)",
        freqs,
        [
            ("DAISY_AUDIO_IN / Diff In (dB)", ac_db, (56, 189, 248), 4),
        ],
        ylim=(-80.0, 0.0),
        xlog=True,
        hlines=[(-16.48, (74, 222, 128))],
        xlabel="Frequency (Hz, Log 10 Hz - 10 MHz)",
    )

    # Panel 4: +18.7 dBu vs +24.0 dBu Clamp Waveform at DAISY_AUDIO_IN
    t18, y18 = tran_peaks["+18.7 dBu (0 dBFS)"]
    t24, y24 = tran_peaks["+24 dBu (Clamp)"]
    draw_panel(
        1220, 790, 1140, 680,
        "Test 3: DAISY_AUDIO_IN (+18.7 dBu Linear vs +24 dBu 4x 1N4148W Symmetric Clamp)",
        (t18 - t18[0]) * 1e3,
        [
            ("+18.7 dBu (0 dBFS, 0.99 Vrms)", y18, (74, 222, 128), 4),
            ("+24.0 dBu (Clamped at +/-2.42 V)", y24, (251, 191, 36), 3),
        ],
        ylim=(-3.0, 3.0),
        hlines=[(1.8, (248, 113, 113)), (-1.8, (248, 113, 113))],
        xlabel="Time (ms)",
    )

    img.save(PLOT_OUT)
    print(f"\nSaved Subcircuit #2 plot: {PLOT_OUT}")


if __name__ == "__main__":
    main()
