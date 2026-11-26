#!/usr/bin/env python3
"""In-KiCad ngspice verification suite for Subcircuit #1 (POWER) ONLY.

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
    POLARIZED_CAPS,
)

POWER_CAPS = {"C1", "C2", "C3", "C4", "C5", "C23", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38"}
PLOT_OUT = os.path.join("docs", "subcircuit1_power_spice.png")


def build_session(bench_stimulus):
    scratch_cir = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611\scratch\october_surprise_power_raw.cir"
    cir_txt = export_kicad_netlist(scratch_cir)
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
    full_deck = "* Subcircuit #1 POWER Verification\n" + fixed_body + "\n" + bench_stimulus

    ng = NgSpiceSession()
    orig_cwd = os.getcwd()
    os.chdir(os.path.join(orig_cwd, "kicad", "spice_models"))
    try:
        ng.load_lines(full_deck)
    finally:
        os.chdir(orig_cwd)
    return ng, cir_txt


def main():
    os.makedirs("docs", exist_ok=True)

    # Session 1: Loaded OP + AC Rack-to-Audio Transfer + Reflected/Output Ripple + Surge
    bench_main = """
* === EXTERNAL BENCH TEST FIXTURE (DOES NOT MODIFY SCHEMATIC NETLIST) ===
V_PLUS16  +16V_RAW 0 DC 16.0 AC 1
V_MINUS16 -16V_RAW 0 DC -16.0 AC 1
V_CHASSIS CHASSIS_GND 0 DC 0

* Nominal Daisy Seed + Op-Amp DC Loads (+5V: 150 mA, +16V: 40 mA, -16V: 40 mA)
I_LOAD_5V  +5V 0 DC 0.150
I_LOAD_P16 +16V 0 DC 0.040
I_LOAD_M16 0 -16V DC 0.040

* Tie unused audio inputs cleanly & load Codec/Outs neutrally
V_INP IN_P 0 DC 0
V_INN IN_N 0 DC 0
V_DAISY_3V3D 3V3_D 0 DC 3.3
V_DAISY_3V3A 3V3_A 0 DC 3.3
R_DAISY_ZIN  DAISY_AUDIO_IN 0 13.6k
R_DAISY_OUT  DAISY_AUDIO_OUT 0 100
* Output Balanced Load
R_LOAD       OUT_P OUT_N 10k

* Clean unity-gain AC/TRAN probes (avoids +/- operator parsing in ngspice let)
E_PROBE_P16  probe_p16 0 +16V 0 1.0
E_PROBE_M16  probe_m16 0 -16V 0 1.0
E_PROBE_5V   probe_5v  0 +5V  0 1.0

* Controllable 500 kHz Buck Ripple & Surge Current Sources (off during .op / .ac)
I_BUCK_REFL +16V_BUCK 0 DC 0 SIN(0 0 500k)
I_BUCK_5V   0 +5V_BUCK  DC 0 SIN(0 0 500k)
I_SURGE_P   0 +16V_BUS  DC 0 PULSE(0 0 10u 1u 1u 100u 1m)
I_SURGE_M   -16V_BUS 0  DC 0 PULSE(0 0 10u 1u 1u 100u 1m)
.end
"""
    ng, cir_txt = build_session(bench_main)

    print("=" * 78)
    print("SUBCIRCUIT #1 (POWER) - TEST 1: LOADED .OP (150mA +5V, 40mA +/-16V)")
    print("=" * 78)
    ng.cmd("op")

    def scalar(n):
        return float(ng.vec_real(n.lower())[0])

    nodes = [
        "+16V_RAW", "+16V_BUS", "+16V_BUCK", "+16V_FILT", "+16V",
        "-16V_RAW", "-16V_BUS", "-16V_FILT", "-16V",
        "+5V_BUCK", "+5V_FILT", "+5V",
    ]
    for nd in nodes:
        print(f"  {nd:12s} = {scalar(nd):+9.5f} V")

    print("\n  POWER Cap Signed Polarity & Derating:")
    print("  Cap  | Pad 1 Node  | Pad 2 Node  | V(p1)-V(p2) | Rating | Margin | Status")
    print("  " + "-" * 74)
    for cname, n1, n2 in parse_caps_from_cir(cir_txt):
        if cname not in POWER_CAPS:
            continue
        v1 = 0.0 if n1.upper() == "GND" else scalar(n1)
        v2 = 0.0 if n2.upper() == "GND" else scalar(n2)
        dv = v1 - v2
        rating = CAP_RATINGS_V.get(cname, 50.0)
        margin = rating / max(abs(dv), 0.1)
        pol_ok = (dv > 0) if cname in POLARIZED_CAPS else True
        ok = pol_ok and (margin >= 2.0)
        print(f"  {cname:4s} | {n1:11s} | {n2:11s} | {dv:+10.3f}V | {rating:4.0f}V  | {margin:5.1f}x | {'PASS' if ok else 'FAIL'}")
        assert ok, f"Power cap {cname} failed polarity or 2x derating!"

    print("\n" + "=" * 78)
    print("SUBCIRCUIT #1 (POWER) - TEST 2: .AC RACK NOISE REJECTION & LC Q-DAMPING (10 Hz - 10 MHz)")
    print("=" * 78)
    ng.cmd("ac dec 50 10 10meg")
    ng.cmd("let f_hz = real(frequency)")
    ng.cmd("let mag_p16 = mag(v(probe_p16))")
    ng.cmd("let mag_m16 = mag(v(probe_m16))")
    ng.cmd("let mag_5v  = mag(v(probe_5v))")
    freqs = ng.vec_real("f_hz")
    db_p16 = 20.0 * np.log10(np.maximum(ng.vec_real("mag_p16"), 1e-12))
    db_m16 = 20.0 * np.log10(np.maximum(ng.vec_real("mag_m16"), 1e-12))
    db_5v = 20.0 * np.log10(np.maximum(ng.vec_real("mag_5v"), 1e-12))

    peak_p16 = float(np.max(db_p16))
    peak_p16_f = float(freqs[int(np.argmax(db_p16))])
    peak_m16 = float(np.max(db_m16))
    peak_m16_f = float(freqs[int(np.argmax(db_m16))])
    print(f"  Max +16V LC Peaking = {peak_p16:+.2f} dB @ {peak_p16_f:.1f} Hz (Limit < +3.0 dB)")
    print(f"  Max -16V LC Peaking = {peak_m16:+.2f} dB @ {peak_m16_f:.1f} Hz (Limit < +3.0 dB)")
    for ft in [1e3, 10e3, 100e3, 500e3, 1e6, 10e6]:
        idx = int(np.argmin(np.abs(freqs - ft)))
        print(f"  f = {freqs[idx]:10.1f} Hz | +16V = {db_p16[idx]:+7.2f} dB | -16V = {db_m16[idx]:+7.2f} dB | +5V(from +16V_RAW) = {db_5v[idx]:+7.2f} dB")

    assert peak_p16 < 3.0 and peak_m16 < 3.0, f"Undamped LC resonance detected: +16V={peak_p16:.2f} dB, -16V={peak_m16:.2f} dB"

    print("\n" + "=" * 78)
    print("SUBCIRCUIT #1 (POWER) - TEST 3A: TSR-1 500 kHz REFLECTED RIPPLE (150 mAp-p @ +16V_BUCK)")
    print("=" * 78)
    ng.cmd("alter @i_buck_refl[sin] = [ 0 0.075 500k ]")
    ng.cmd("tran 50n 300u 260u")
    t_refl = ng.vec_real("time")
    v_buck_in = ng.vec_real("+16V_BUCK".lower())
    v_bus_in = ng.vec_real("+16V_BUS".lower())
    v_ana_p16 = ng.vec_real("+16V".lower())
    pp_buck = float(np.max(v_buck_in) - np.min(v_buck_in)) * 1e3
    pp_bus = float(np.max(v_bus_in) - np.min(v_bus_in)) * 1e3
    pp_ana = float(np.max(v_ana_p16) - np.min(v_ana_p16)) * 1e3
    atten_refl = 20.0 * math.log10(max(pp_buck, 1e-9) / max(pp_ana, 1e-12))
    print(f"  +16V_BUCK Ripple = {pp_buck:7.3f} mVp-p")
    print(f"  +16V_BUS  Ripple = {pp_bus:7.4f} mVp-p (Atten = {20*math.log10(max(pp_buck,1e-9)/max(pp_bus,1e-12)):.1f} dB)")
    print(f"  +16V      Ripple = {pp_ana:7.6f} mVp-p ({pp_ana*1e3:.3f} uVp-p | Total Atten = {atten_refl:.1f} dB)")
    ng.cmd("alter @i_buck_refl[sin] = [ 0 0 500k ]")

    print("\n" + "=" * 78)
    print("SUBCIRCUIT #1 (POWER) - TEST 3B: +5V SWITCHER OUTPUT RIPPLE ATTENUATION (@ 500 kHz)")
    print("=" * 78)
    # 500 kHz: 220u + 10uF + 100nF (~230uF) -> at 500 kHz Xc ≈ 1/(2*pi*500k*230u) = 1.38 mOhm -> ~18 Apk gives 50mVp-p on ideal C
    # Let's drive 0.5 Apk (2*pi*500k*10u = 31.4S => if 220u+10u parallel ideal C = 230u, Z = 1.38 mOhm, scale to exact 50 mVp-p equivalence)
    ng.cmd("alter @i_buck_5v[sin] = [ 0 18.0 500k ]")
    ng.cmd("tran 50n 300u 260u")
    t_5v = ng.vec_real("time")
    v_5v_buck = ng.vec_real("+5V_BUCK".lower())
    v_5v_out = ng.vec_real("+5V".lower())
    pp_5b = float(np.max(v_5v_buck) - np.min(v_5v_buck)) * 1e3
    pp_5o = float(np.max(v_5v_out) - np.min(v_5v_out)) * 1e3
    atten_5v = 20.0 * math.log10(max(pp_5b, 1e-9) / max(pp_5o, 1e-12))
    pp_5o_scaled_50mv = pp_5o * (50.0 / max(pp_5b, 1e-9))
    print(f"  +5V_BUCK Ripple = {pp_5b:6.2f} mVp-p | +5V Output Ripple = {pp_5o:.5f} mVp-p")
    print(f"  +5V Pi-Filter Attenuation @ 500 kHz = {atten_5v:.1f} dB (50 mVp-p -> {pp_5o_scaled_50mv:.4f} mVp-p)")
    ng.cmd("alter @i_buck_5v[sin] = [ 0 0 500k ]")

    print("\n" + "=" * 78)
    print("SUBCIRCUIT #1 (POWER) - TEST 4: 600 mA / 100 us +48V SURGE CLAMP ON +/-16V_BUS (SMBJ18CA)")
    print("=" * 78)
    ng.cmd("alter @i_surge_p[pulse] = [ 0 0.600 10u 1u 1u 100u 1m ]")
    ng.cmd("alter @i_surge_m[pulse] = [ 0 0.600 10u 1u 1u 100u 1m ]")
    ng.cmd("tran 500n 200u 0")
    t_s = ng.vec_real("time")
    v_s_p = ng.vec_real("+16V_BUS".lower())
    v_s_p_ana = ng.vec_real("+16V".lower())
    v_s_m = ng.vec_real("-16V_BUS".lower())
    p_max = float(np.max(v_s_p))
    pa_max = float(np.max(v_s_p_ana))
    m_min = float(np.min(v_s_m))
    print(f"  +16V_BUS Peak Clamp = {p_max:+6.3f} V (+16V Audio = {pa_max:+6.3f} V, Cap Max = 35 V)")
    print(f"  -16V_BUS Peak Clamp = {m_min:+6.3f} V (Cap Max = -35 V)")
    assert p_max < 30.0 and abs(m_min) < 30.0, "SMBJ18CA did not clamp safely below 30V!"

    # Plot 4-panel Subcircuit #1 verification chart
    W, H = 2400, 1500
    img = Image.new("RGB", (W, H), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    try:
        f_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 26)
        f_sub = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 21)
        f_mono = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 17)
    except Exception:
        f_title = f_sub = f_mono = ImageFont.load_default()

    draw.text((40, 22), "SUBCIRCUIT #1 (POWER) - IN-KICAD NGSPICE VERIFICATION (SMBJ18CA + PASSIVE LC+FB PI-FILTERS)", fill=(248, 250, 252), font=f_title)

    def draw_panel(px, py, pw, ph, title, xvals, yseries, ylim=None, xlog=False, hlines=None, xlabel="Time", ylabel="Level"):
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
            draw.text((px + 10, yy - 9), f"{yv:+6.2f}", fill=(148, 163, 184), font=f_mono)

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

    # Panel 1: AC Transfer
    draw_panel(
        40, 75, 1140, 680,
        f"Test 2: Rack-to-Audio Rejection (.ac, Max Peaking {max(peak_p16, peak_m16):+.2f} dB < +3 dB)",
        freqs,
        [
            ("+16V Analog Transfer (dB)", db_p16, (56, 189, 248), 4),
            ("-16V Analog Transfer (dB)", db_m16, (74, 222, 128), 3),
            ("+5V Digital Transfer (dB)", db_5v, (251, 191, 36), 3),
        ],
        ylim=(-120, 10),
        xlog=True,
        hlines=[(0.0, (148, 163, 184)), (3.0, (248, 113, 113))],
        xlabel="Frequency (Hz, Log 10 Hz - 10 MHz)",
    )

    # Panel 2: Buck 500kHz Reflected Ripple (AC component in mV)
    b_ac = (v_buck_in - np.mean(v_buck_in)) * 1e3
    a_ac = (v_ana_p16 - np.mean(v_ana_p16)) * 1e3
    t_rus = (t_refl - t_refl[0]) * 1e6
    draw_panel(
        1220, 75, 1140, 680,
        f"Test 3A: 150 mAp-p @ 500 kHz Buck Ripple Isolation ({atten_refl:.1f} dB)",
        t_rus,
        [
            (f"+16V_BUCK Ripple ({pp_buck:.2f} mVp-p)", b_ac, (251, 191, 36), 4),
            (f"+16V Audio x1000 ({pp_ana*1e3:.2f} uVp-p)", a_ac * 1000.0, (74, 222, 128), 3),
        ],
        xlabel="Time (us steady-state window)",
    )

    # Panel 3: +5V Buck Output Attenuation
    v5b_ac = (v_5v_buck - np.mean(v_5v_buck)) * 1e3
    v5o_ac = (v_5v_out - np.mean(v_5v_out)) * 1e3
    t_5us = (t_5v - t_5v[0]) * 1e6
    draw_panel(
        40, 790, 1140, 680,
        f"Test 3B: +5V Switcher Pi-Filter Attenuation ({atten_5v:.1f} dB @ 500 kHz)",
        t_5us,
        [
            (f"+5V_BUCK ({pp_5b:.1f} mVp-p)", v5b_ac, (251, 191, 36), 4),
            (f"+5V Filtered x100 ({pp_5o:.3f} mVp-p)", v5o_ac * 100.0, (56, 189, 248), 3),
        ],
        xlabel="Time (us steady-state window)",
    )

    # Panel 4: Surge Clamp
    t_sus = t_s * 1e6
    draw_panel(
        1220, 790, 1140, 680,
        f"Test 4: 600 mA / 100 us Rail Surge Clamp (D19/D20 SMBJ18CA -> {p_max:+.2f}V / {m_min:+.2f}V)",
        t_sus,
        [
            ("+16V_BUS Clamped (V)", v_s_p, (56, 189, 248), 4),
            ("-16V_BUS Clamped (V)", v_s_m, (74, 222, 128), 4),
        ],
        ylim=(-36.0, 36.0),
        hlines=[(35.0, (248, 113, 113)), (-35.0, (248, 113, 113))],
        xlabel="Time (us)",
    )

    img.save(PLOT_OUT)
    print(f"\nSaved Subcircuit #1 plot: {PLOT_OUT}")


if __name__ == "__main__":
    main()
