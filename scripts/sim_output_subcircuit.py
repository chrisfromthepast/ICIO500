#!/usr/bin/env python3
"""In-KiCad ngspice verification suite for Subcircuit #3 (OUTPUT / CCOS) ONLY.

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

OUTPUT_CAPS = {"C21", "C22", "C24", "C25", "C26", "C27", "C28", "C29", "C39", "C40"}
PLOT_OUT = os.path.join("docs", "subcircuit3_output_spice.png")
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
    full_deck = "* Subcircuit #3 OUTPUT/CCOS Verification\n" + fixed_body + "\n" + bench_stimulus

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
    return m.group(1), m.group(2)


def main():
    os.makedirs("docs", exist_ok=True)
    scratch_cir = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611\scratch\october_surprise_output_raw.cir"
    cir_txt = export_kicad_netlist(scratch_cir)

    r19_n1, r19_n2 = find_res_nodes(cir_txt, "R19")
    r25_n1, r25_n2 = find_res_nodes(cir_txt, "R25")
    u7a_out_node = r19_n2 if r19_n1.upper() == "OUT_P" else r19_n1
    u7b_out_node = r25_n2 if r25_n1.upper() == "OUT_N" else r25_n1

    # -------------------------------------------------------------------------
    # SESSION 1: .op, .ac (Gain, RF, 10nF Stability), .tran (Stress Loads)
    # -------------------------------------------------------------------------
    bench_lin = """
V_PLUS16  +16V_RAW 0 DC 16.0
V_MINUS16 -16V_RAW 0 DC -16.0
V_CHASSIS CHASSIS_GND 0 DC 0

V_INP IN_P 0 DC 0
V_INN IN_N 0 DC 0
V_DAISY_3V3D 3V3_D 0 DC 3.3
V_DAISY_3V3A 3V3_A 0 DC 3.3
R_DAISY_ZIN  DAISY_AUDIO_IN 0 13.6k

* Codec DAC output source (0 dBFS = 1.0 Vrms = 1.414 Vpk at DAISY_AUDIO_OUT via 100R Zout)
V_DY_OUT   daisy_dac_src 0 DC 0 AC 1 SIN(0 1.414 1000)
R_DY_ZOUT  daisy_dac_src DAISY_AUDIO_OUT 100

R_LOAD     OUT_P OUT_N 10k
C_LOAD     OUT_P OUT_N 1p
R_SHORT    OUT_N 0 1e9
.options reltol=0.003 method=gear itl4=100
.end
"""
    ng = open_deck(cir_txt, bench_lin)

    print("=" * 78)
    print("SUBCIRCUIT #3 (OUTPUT / CCOS) - TEST 1: .OP & CAPACITOR DERATING")
    print("=" * 78)
    ng.cmd("op")

    def scalar(n):
        return float(ng.vec_real(n.lower())[0])

    print(f"  +16V = {scalar('+16V'):+8.4f} V | -16V = {scalar('-16V'):+8.4f} V")
    print(f"  U7A.1 = {scalar(u7a_out_node):+8.4f} V | OUT_P = {scalar('OUT_P'):+8.4f} V | OUT_N = {scalar('OUT_N'):+8.4f} V")

    print("\n  Zone 4 Cap | Node 1                 | Node 2                 | DC V    | Worst Fault | Rating | Margin | Status")
    print("  " + "-" * 104)
    for cname, n1, n2 in parse_caps_from_cir(cir_txt):
        if cname not in OUTPUT_CAPS:
            continue
        v1 = 0.0 if n1.upper() == "GND" else scalar(n1)
        v2 = 0.0 if n2.upper() == "GND" else scalar(n2)
        dv = v1 - v2
        rating = CAP_RATINGS_V.get(cname, 50.0)
        worst = 48.0 if cname in ("C39", "C40") else max(abs(dv), 1.0)
        margin = rating / max(worst, 0.1)
        ok = margin >= 2.0
        print(f"  {cname:10s} | {n1:22s} | {n2:22s} | {dv:+7.3f} | {worst:7.1f} V   | {rating:4.0f} V | {margin:5.1f}x | {'PASS' if ok else 'FAIL'}")
        assert ok, f"Zone 4 cap {cname} failed 2x derating ({margin:.2f}x)!"

    print("\n" + "=" * 78)
    print("SUBCIRCUIT #3 - TEST 2: .AC OUTPUT GAIN (10 Hz - 10 MHz) & 10 nF STABILITY")
    print("=" * 78)
    ng.cmd("ac dec 50 10 10meg")
    ng.cmd("let f_hz = real(frequency)")
    ng.cmd("let mag_out = mag(v(out_p) - v(out_n))")
    freqs = ng.vec_real("f_hz")
    ac_db = 20.0 * np.log10(np.maximum(ng.vec_real("mag_out"), 1e-12))
    for ft in [20.0, 100.0, 1000.0, 20000.0, 100000.0, 1000000.0, 10000000.0]:
        idx = int(np.argmin(np.abs(freqs - ft)))
        print(f"  f = {freqs[idx]:10.1f} Hz | Gain(OUT_P-OUT_N / DAC) = {ac_db[idx]:+7.3f} dB")
    g_20 = float(ac_db[int(np.argmin(np.abs(freqs - 20.0)))])
    g_1k = float(ac_db[int(np.argmin(np.abs(freqs - 1000.0)))])
    g_20k = float(ac_db[int(np.argmin(np.abs(freqs - 20000.0)))])

    ng.cmd("alter c_load = 10n")
    ng.cmd("ac dec 50 10 10meg")
    ng.cmd("let mag_out10 = mag(v(out_p) - v(out_n))")
    ac_10n_db = 20.0 * np.log10(np.maximum(ng.vec_real("mag_out10"), 1e-12))
    peak_10n = float(np.max(ac_10n_db)) - g_1k
    print(f"  10 nF Cable Load Peaking = {peak_10n:+.2f} dB rel. 1 kHz (Limit < +3.0 dB)")
    assert peak_10n < 3.0, f"10 nF load peaking {peak_10n:.2f} dB too high!"
    ng.cmd("alter c_load = 1p")

    print("\n" + "=" * 78)
    print("SUBCIRCUIT #3 - TEST 3: TRANSIENT (+18.7 / +20 dBu, 600R, SHORT OUT_N->GND, 10nF)")
    print("=" * 78)
    def run_out_tran(dac_pk):
        ng.cmd(f"alter @v_dy_out[sin] = [ 0 {dac_pk} 1000 ]")
        ng.cmd("tran 5u 6m 3m")
        vp = ng.vec_real("out_p")
        vn = ng.vec_real("out_n")
        vd = vp - vn
        vdy = ng.vec_real("daisy_audio_out")
        rms_in = float(np.sqrt(np.mean(vdy ** 2)))
        rms_out = float(np.sqrt(np.mean(vd ** 2)))
        pk_out = float(np.max(np.abs(vd)))
        return dict(rms_in=rms_in, rms_out=rms_out, pk_out=pk_out, vp=vp, vn=vn,
                    gain=20.0 * math.log10(rms_out / rms_in))

    r_10k_187 = run_out_tran(1.414)
    print(f"  10k Bal  (+18.7 dBu / 0 dBFS): Out = {r_10k_187['rms_out']:.3f} Vrms | Gain = {r_10k_187['gain']:+.3f} dB")
    r_10k_20 = run_out_tran(1.642)
    print(f"  10k Bal  (+20.0 dBu Peak)    : Out = {r_10k_20['rms_out']:.3f} Vrms | Gain = {r_10k_20['gain']:+.3f} dB")

    ng.cmd("alter r_load = 600")
    r_600_20 = run_out_tran(1.642)
    print(f"  600R Bal (+20.0 dBu)         : Out = {r_600_20['rms_out']:.3f} Vrms | I_load_pk = {r_600_20['pk_out']/600*1e3:.1f} mA")

    ng.cmd("alter r_load = 10k")
    ng.cmd("alter r_short = 1")
    r_unbal = run_out_tran(1.414)
    drop_unbal = 20.0 * math.log10(r_unbal["rms_out"] / r_10k_187["rms_out"])
    print(f"  OUT_N->GND Short (+18.7 dBu) : Diff = {r_unbal['rms_out']:.3f} Vrms | OUT_P = {np.sqrt(np.mean(r_unbal['vp']**2)):.3f} V | OUT_N = {np.sqrt(np.mean(r_unbal['vn']**2)):.4f} V | Delta = {drop_unbal:+.3f} dB")
    assert abs(drop_unbal) < 0.15, f"CCOS unbalanced delta {drop_unbal:+.3f} dB exceeded 0.15 dB!"

    ng.cmd("alter r_short = 1e9")
    ng.cmd("alter c_load = 10n")
    r_10n = run_out_tran(1.414)
    print(f"  10 nF Cap Load (+18.7 dBu)   : Out = {r_10n['rms_out']:.3f} Vrms | Delta = {20*math.log10(r_10n['rms_out']/r_10k_187['rms_out']):+.3f} dB")

    # Dedicated clean .noise pass for Output Stage
    bench_noise = """
V_PLUS16  +16V_RAW 0 DC 16.0
V_MINUS16 -16V_RAW 0 DC -16.0
V_CHASSIS CHASSIS_GND 0 DC 0
V_INP IN_P 0 DC 0
V_INN IN_N 0 DC 0
V_DAISY_3V3D 3V3_D 0 DC 3.3
V_DAISY_3V3A 3V3_A 0 DC 3.3
R_DAISY_ZIN  DAISY_AUDIO_IN 0 13.6k
V_DY_OUT   daisy_dac_src 0 DC 0 AC 1
R_DY_ZOUT  daisy_dac_src DAISY_AUDIO_OUT 100
R_LOAD     OUT_P OUT_N 10k
.end
"""
    ng_n = open_deck(cir_txt, bench_noise)
    ng_n.cmd("noise v(out_p, out_n) v_dy_out dec 50 20 20k 1")
    ng_n.cmd("setplot noise1")
    f_n = ng_n.vec_real("frequency")
    ext_refs = [f"r{i}" for i in range(10, 27)] + ["r30"]
    ext_dens_sq = np.zeros_like(f_n)
    for rref in ext_refs:
        try:
            ext_dens_sq += ng_n.vec_real(f"onoise_{rref}") ** 2
        except KeyError:
            pass
    vnoise_res_rms = float(np.sqrt(np.trapezoid(ext_dens_sq, f_n)))
    # 4 op-amp noise gains seen at OUT_P-OUT_N: U3B (noise gain 3.37 * diff_out 2 = 6.74), U4A (~2), U7A (~2), U7B (~2)
    en_opa = 2.9e-9 * math.sqrt((6.74 ** 2 + 2.0 ** 2 + 2.0 ** 2 + 2.0 ** 2) * (20000.0 - 20.0))
    vnoise_tot_rms = math.hypot(vnoise_res_rms, en_opa)
    dr_out = 20.0 * math.log10(6.67 / vnoise_tot_rms)
    print(f"\n  [Subcircuit #3 20 Hz - 20 kHz Noise Floor (10k Low-Noise CCOS)]")
    print(f"    External Resistor Thermal Noise = {vnoise_res_rms*1e6:.2f} uVrms (diff OUT_P-OUT_N)")
    print(f"    Total (Resistors + 4x OPA1656 @ 2.9nV/rtHz) = {vnoise_tot_rms*1e6:.2f} uVrms ({20*math.log10(vnoise_tot_rms/0.7746):+.1f} dBu)")
    print(f"    Output Stage Dynamic Range (rel. +18.7 dBu / 6.67 Vrms) = {dr_out:.1f} dB")

    # -------------------------------------------------------------------------
    # SESSION 2: +48V OUTPUT BACK-FEED PHANTOM FAULTS (4A, 4B, 4C)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("SUBCIRCUIT #3 - TEST 4: +48V OUTPUT BACK-FEED PHANTOM FAULT SURVIVABILITY")
    print("=" * 78)

    def run_backfeed(r_fault_p, r_fault_n, r_short_n, v_peak, t_end, pulse_off, label):
        fall_str = f"{pulse_off - 50e-6:.6f} {v_peak} {pulse_off:.6f} 0" if pulse_off else f"{t_end:.6f} {v_peak}"
        bench_f = f"""
V_PLUS16  +16V_RAW 0 DC 16.0
V_MINUS16 -16V_RAW 0 DC -16.0
V_CHASSIS CHASSIS_GND 0 DC 0
V_INP IN_P 0 DC 0
V_INN IN_N 0 DC 0
V_DAISY_3V3D 3V3_D 0 DC 3.3
V_DAISY_3V3A 3V3_A 0 DC 3.3
R_DAISY_ZIN  DAISY_AUDIO_IN 0 13.6k
V_DY_OUT     DAISY_AUDIO_OUT 0 DC 0

V_PHANTOM p_src 0 DC 0 PWL(0 0 490u 0 540u {v_peak} {fall_str})
R_FAULT_P p_src OUT_P {r_fault_p}
R_FAULT_N p_src OUT_N {r_fault_n}
R_SH_N    OUT_N 0 {r_short_n}
.options reltol=0.005 trtol=7 method=gear maxord=1 itl4=200
.end
"""
        ng_f = open_deck(cir_txt, bench_f)
        ng_f.cmd(f"tran 1u {t_end*1e3:.2f}m 0")
        t = ng_f.vec_real("time")
        assert float(t[-1]) >= t_end * 0.99, f"{label} aborted at {t[-1]*1e3:.3f} ms!"
        vop = ng_f.vec_real("out_p")
        von = ng_f.vec_real("out_n")
        vu7a = ng_f.vec_real(u7a_out_node.lower())
        vp16 = ng_f.vec_real("+16V".lower())
        i_r19 = (vop - vu7a) / 49.9 * 1e3
        p_r19 = ((vop - vu7a) ** 2) / 49.9 * 1e3  # mW
        print(f"  {label}:")
        print(f"    OUT_P = [{np.min(vop):+6.2f}, {np.max(vop):+6.2f} V] | OUT_N = [{np.min(von):+6.2f}, {np.max(von):+6.2f} V] | +16V Rail Max = {np.max(vp16):+6.2f} V")
        print(f"    R19 (49.9R 1206): Max |I_R19| = {np.max(np.abs(i_r19)):6.1f} mA | Max Power = {np.max(p_r19):6.1f} mW")
        assert np.max(vp16) < 25.0, f"+16V rail rose to {np.max(vp16):.2f} V!"
        return t, vop, von, vp16, p_r19

    t4a, vop4a, von4a, vp16_4a, pr19_4a = run_backfeed(6810, 6810, 1e9, 48.0, 5.0e-3, None, "Case 4A (IEC 61938 +48V/6.81k Both Legs)")
    t4b, vop4b, von4b, vp16_4b, pr19_4b = run_backfeed(6810, 1e9, 1.0, 48.0, 5.0e-3, None, "Case 4B (IEC +48V/6.81k OUT_P + OUT_N->GND)")
    assert np.max(pr19_4a) < 250.0 and np.max(pr19_4b) < 250.0, "R19 steady power exceeded 250 mW 1206 rating!"
    t4c, vop4c, von4c, vp16_4c, pr19_4c = run_backfeed(1000, 1e9, 1e9, 48.0, 5.0e-3, 2.5e-3, "Case 4C (7x IEC Phantom +48V/1k 2ms Surge -> 0V)")

    # Plot 4-panel Subcircuit #3 verification chart
    W, H = 2400, 1500
    img = Image.new("RGB", (W, H), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    try:
        f_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 26)
        f_sub = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 21)
        f_mono = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 17)
    except Exception:
        f_title = f_sub = f_mono = ImageFont.load_default()

    draw.text((40, 22), "SUBCIRCUIT #3 (OUTPUT / CCOS) - IN-KICAD NGSPICE VERIFICATION (10k CCOS, BAV21W, C39/C40, SOCKETED U7)", fill=(248, 250, 252), font=f_title)

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

    draw_panel(
        40, 75, 1140, 680,
        f"Test 2: Output Diff Gain (.ac: {g_20:+.2f}/{g_1k:+.2f}/{g_20k:+.2f} dB, 10nF Peak {peak_10n:+.2f} dB, DR={dr_out:.1f} dB)",
        freqs,
        [
            ("10k Bal (dB)", ac_db, (56, 189, 248), 4),
            ("10nF Cap Load (dB)", ac_10n_db, (74, 222, 128), 3),
        ],
        ylim=(-40.0, 25.0),
        xlog=True,
        hlines=[(g_1k, (148, 163, 184))],
        xlabel="Frequency (Hz, Log 10 Hz - 10 MHz)",
    )

    draw_panel(
        1220, 75, 1140, 680,
        f"Test 3: Floating CCOS Action (OUT_N->GND Short Delta = {drop_unbal:+.3f} dB)",
        np.arange(len(r_unbal["vp"])) * 5.0 / 1000.0,
        [
            ("OUT_P (Active Hot Leg V)", r_unbal["vp"], (56, 189, 248), 4),
            ("OUT_N (Shorted to GND)", r_unbal["vn"], (248, 113, 113), 3),
        ],
        xlabel="Time (ms)",
    )

    draw_panel(
        40, 790, 1140, 680,
        f"Test 4A: IEC +48V/6.81k Back-Feed Both Legs (OUT Max {np.max(vop4a):+.2f}V, R19 {np.max(pr19_4a):.1f} mW << 250 mW)",
        t4a * 1e3,
        [
            ("OUT_P (V)", vop4a, (56, 189, 248), 4),
            ("+16V Rail (V)", vp16_4a, (74, 222, 128), 3),
            ("R19 Power / 10 (10mW/div)", pr19_4a / 10.0, (251, 191, 36), 3),
        ],
        ylim=(-5.0, 25.0),
        hlines=[(25.0, (248, 113, 113))],
        xlabel="Time (ms)",
    )

    draw_panel(
        1220, 790, 1140, 680,
        f"Test 4C: 7x IEC +48V/1k 2ms Surge -> 0V (OUT_P [{np.min(vop4c):+.1f},{np.max(vop4c):+.1f}V], +16V Max {np.max(vp16_4c):+.2f}V)",
        t4c * 1e3,
        [
            ("OUT_P Clamped (V)", vop4c, (56, 189, 248), 4),
            ("+16V Rail (V)", vp16_4c, (74, 222, 128), 3),
        ],
        ylim=(-20.0, 25.0),
        hlines=[(25.0, (248, 113, 113))],
        xlabel="Time (ms)",
    )

    img.save(PLOT_OUT)
    print(f"\nSaved Subcircuit #3 plot: {PLOT_OUT}")


if __name__ == "__main__":
    main()
