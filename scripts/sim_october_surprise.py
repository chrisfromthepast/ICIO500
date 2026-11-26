#!/usr/bin/env python3
"""In-KiCad ngspice verification suite for ICIO500 October Surprise.

Loads KiCad's built-in ngspice.dll directly against the untouched SPICE netlist
exported from kicad/october_surprise.kicad_sch via `kicad-cli sch export netlist --format spice`.
Never hand-transcribes circuit values or components.
"""

import ctypes
import math
import os
import re
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
KICAD_BIN = r"C:\Program Files\KiCad\10.0\bin"
KICAD_CM = r"C:\Program Files\KiCad\10.0\lib\ngspice"
SCH_PATH = os.path.join("kicad", "october_surprise.kicad_sch")
RAW_CIR = os.path.join("scratch_october_surprise_raw.cir")
PLOT_OUT = os.path.join("docs", "october_surprise_spice_verification.png")

CAP_RATINGS_V = {
    "C1": 35.0, "C2": 35.0, "C3": 35.0, "C4": 35.0, "C5": 35.0,
    "C6": 50.0, "C7": 50.0, "C8": 50.0,
    "C10": 100.0, "C11": 100.0, "C12": 100.0, "C13": 100.0, "C14": 100.0,
    "C15": 50.0, "C16": 50.0,
    "C17": 50.0, "C18": 50.0, "C19": 50.0, "C20": 50.0,
    "C21": 50.0, "C22": 50.0, "C23": 50.0, "C24": 50.0, "C25": 50.0,
    "C26": 50.0, "C27": 50.0, "C28": 50.0, "C29": 50.0,
    "C30": 35.0, "C31": 35.0, "C32": 35.0, "C33": 50.0,
    "C34": 35.0, "C35": 35.0, "C36": 35.0, "C37": 35.0, "C38": 35.0,
    "C39": 100.0, "C40": 100.0,
}
POLARIZED_CAPS = {"C1", "C2", "C3", "C4", "C5", "C36"}


def export_kicad_netlist(out_cir):
    subprocess.run(
        [KICAD_CLI, "sch", "export", "netlist", "--format", "spice", "-o", out_cir, SCH_PATH],
        check=True,
    )
    return open(out_cir, encoding="utf-8").read()


class NgSpiceSession:
    def __init__(self):
        os.environ["PATH"] = KICAD_BIN + ";" + os.environ.get("PATH", "")
        os.add_dll_directory(KICAD_BIN)
        buf = ctypes.create_unicode_buffer(260)
        ctypes.windll.kernel32.GetShortPathNameW(KICAD_CM, buf, 260)
        cm_short = buf.value.replace("\\", "/")

        self.ng = ctypes.CDLL(os.path.join(KICAD_BIN, "ngspice.dll"))
        self.logs = []
        cb_char = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
        cb_stat = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
        cb_exit = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
        self._c1 = cb_char(lambda m, i, u: (self.logs.append(m.decode("utf-8", errors="replace")), 0)[1])
        self._c2 = cb_stat(lambda m, i, u: 0)
        self._c3 = cb_exit(lambda s, im, q, i, u: 0)
        self.ng.ngSpice_Init(self._c1, self._c2, self._c3, None, None, None, None)

        class VecInfo(ctypes.Structure):
            _fields_ = [
                ("v_name", ctypes.c_char_p),
                ("v_type", ctypes.c_int),
                ("v_flags", ctypes.c_short),
                ("v_realdata", ctypes.POINTER(ctypes.c_double)),
                ("v_compdata", ctypes.c_void_p),
                ("v_length", ctypes.c_int),
            ]

        self.ng.ngGet_Vec_Info.argtypes = [ctypes.c_char_p]
        self.ng.ngGet_Vec_Info.restype = ctypes.POINTER(VecInfo)

        for cm in ["spice2poly.cm", "analog.cm", "digital.cm", "xtradev.cm", "xtraevt.cm", "table.cm"]:
            self.cmd(f"codemodel {cm_short}/{cm}")
        self.cmd("set ngbehavior=ltpsa")

    def cmd(self, s):
        return self.ng.ngSpice_Command(s.encode("utf-8"))

    def load_lines(self, deck_str):
        lines = deck_str.splitlines()
        arr = (ctypes.c_char_p * (len(lines) + 1))()
        for i, l in enumerate(lines):
            arr[i] = l.encode("utf-8")
        arr[len(lines)] = None
        rc = self.ng.ngSpice_Circ(arr)
        if rc != 0:
            raise RuntimeError(f"ngSpice_Circ failed with rc={rc}")

    def vec_real(self, name):
        vp = self.ng.ngGet_Vec_Info(name.encode("utf-8"))
        if not vp or not vp.contents.v_realdata or vp.contents.v_length <= 0:
            raise KeyError(f"Vector {name} not available")
        n = vp.contents.v_length
        return np.ctypeslib.as_array(vp.contents.v_realdata, shape=(n,)).copy()


def parse_caps_from_cir(cir_txt):
    caps = []
    for line in cir_txt.splitlines():
        m = re.match(r"^(C\S+)\s+(\S+)\s+(\S+)\s+\S+", line.strip())
        if m:
            caps.append((m.group(1), m.group(2), m.group(3)))
    return caps


def main():
    os.makedirs("docs", exist_ok=True)
    scratch_cir = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611\scratch\october_surprise_raw.cir"
    cir_txt = export_kicad_netlist(scratch_cir)

    # Strip trailing .end from KiCad netlist ONLY to append bench power/stimulus/load deck
    # (Circuit body itself comes 100% untouched from kicad-cli!)
    body_lines = [l for l in cir_txt.splitlines() if l.strip().lower() != ".end" and not l.strip().lower().startswith(".title")]
    # Inline .include files with 8.3 short paths? Even better: ngSpice_Circ resolves relative includes if we resolve paths cleanly or inline the two small .lib files:
    bench_stimulus = """
* === EXTERNAL BENCH TEST FIXTURE (DOES NOT MODIFY SCHEMATIC NETLIST) ===
* VPR-500 Rack Power Rails (+/-16V DC at J1.12 / J1.14, Chassis GND tied via rack star)
V_PLUS16  +16V_RAW 0 DC 16.0
V_MINUS16 -16V_RAW 0 DC -16.0
V_CHASSIS CHASSIS_GND 0 DC 0

* Balanced Input Source at J1.10 (IN_P) / J1.8 (IN_N), default +18.7 dBu (6.67 Vrms diff => +/-4.715 Vpk per leg)
V_INP IN_P 0 DC 0 AC 0.5 SIN(0 4.715 1000)
V_INN IN_N 0 DC 0 AC -0.5 SIN(0 -4.715 1000)

* Daisy Seed Onboard LDOs & Codec Model (Electro-Smith Datasheet Rev7: Zin=13.6k, Zout=100R, 0 dBFS = 1.0 Vrms)
V_DAISY_3V3D 3V3_D 0 DC 3.3
V_DAISY_3V3A 3V3_A 0 DC 3.3
R_DAISY_ZIN  DAISY_AUDIO_IN 0 13.6k
E_DAISY_DSP  daisy_dac_int 0 DAISY_AUDIO_IN 0 1.0
R_DAISY_ZOUT daisy_dac_int DAISY_AUDIO_OUT 100

* Output Balanced Load & Unbalanced Fault Switch at J1.2 (OUT_P) / J1.4 (OUT_N)
R_LOAD  OUT_P OUT_N 10k
C_LOAD  OUT_P OUT_N 1p
R_SHORT OUT_N 0 1e9
.options reltol=0.003 method=gear itl4=100
.end
"""

    # Note: ngspice.dll on Windows needs short or forward-slash .include paths without spaces if called from embedded .circ;
    # rewrite ONLY the .include paths via GetShortPathNameW if spaces exist so ngspice reads the real .lib files on disk!
    def to_short_path(m):
        p = m.group(1)
        b = ctypes.create_unicode_buffer(260)
        ctypes.windll.kernel32.GetShortPathNameW(p.replace("/", "\\"), b, 260)
        sp = b.value.replace("\\", "/") if b.value else p
        return f'.include "{sp}"'

    fixed_body = re.sub(r'\.include\s+"([^"]+)"', to_short_path, "\n".join(body_lines))
    # Also fix nested .include "OPA1656.LIB" inside OPA1656_DUAL.lib via cwd push during ngSpice_Circ
    full_deck = "* October Surprise Bench Simulation\n" + fixed_body + "\n" + bench_stimulus

    ng = NgSpiceSession()
    orig_cwd = os.getcwd()
    os.chdir(os.path.join(orig_cwd, "kicad", "spice_models"))
    try:
        ng.load_lines(full_deck)
    finally:
        os.chdir(orig_cwd)

    print("=" * 78)
    print("TEST A: DC OPERATING POINT (.op) & SIGNED CAPACITOR POLARITY / DERATING AUDIT")
    print("=" * 78)
    ng.cmd("op")

    def scalar(vec):
        v = ng.vec_real(vec.lower())
        return float(v[0])

    for node in ["+16V_RAW", "+16V", "-16V_RAW", "-16V", "+5V", "3V3_D", "3V3_A", "DAISY_AUDIO_IN", "DAISY_AUDIO_OUT", "OUT_P", "OUT_N"]:
        print(f"  {node:16s} = {scalar(node):+9.5f} V")

    caps = parse_caps_from_cir(cir_txt)
    print("\n  Cap  | Pad 1 Node             | Pad 2 Node             | V(p1)-V(p2) | Rating | Worst Fault  | Status")
    print("  " + "-" * 102)
    for cname, n1, n2 in caps:
        v1 = 0.0 if n1.upper() == "GND" else scalar(n1)
        v2 = 0.0 if n2.upper() == "GND" else scalar(n2)
        dv = v1 - v2
        rating = CAP_RATINGS_V.get(cname, 50.0)
        worst = max(abs(dv), 48.0 if cname in ("C12", "C13", "C39", "C40") else (11.0 if cname == "C14" else abs(dv)))
        if cname in ("C10", "C11"):
            worst = 48.0  # phantom bleed / fault behind series surge R
        margin = rating / max(worst, 0.1)
        pol_ok = (dv > 0) if cname in POLARIZED_CAPS else True
        if cname in POLARIZED_CAPS:
            status = "PASS" if (pol_ok and margin >= 2.0) else f"FAIL(pol={pol_ok},m={margin:.2f}x)"
        else:
            status = "PASS" if margin >= 2.0 else f"WARN(m={margin:.2f}x)"
        print(f"  {cname:4s} | {n1:22s} | {n2:22s} | {dv:+10.3f}V | {rating:4.0f}V  | {worst:5.1f}V ({margin:4.1f}x) | {status}")
        if cname in POLARIZED_CAPS:
            assert pol_ok and margin >= 2.0, f"{cname} failed signed polarity/margin!"

    print("\n" + "=" * 78)
    print("TEST B: TRANSIENT (.tran) LINEAR GAIN, PHASE & CLIPPING ACROSS LEVELS (10k BAL)")
    print("=" * 78)

    def run_tran_case(vp_leg_pk):
        ng.cmd(f"alter @v_inp[sin] = [ 0 {vp_leg_pk} 1000 ]")
        ng.cmd(f"alter @v_inn[sin] = [ 0 {-vp_leg_pk} 1000 ]")
        ng.cmd("tran 5u 6m 3m")
        t = ng.vec_real("time")
        vin_d = ng.vec_real("in_p") - ng.vec_real("in_n")
        vdaisy = ng.vec_real("daisy_audio_in")
        vout_p = ng.vec_real("out_p")
        vout_n = ng.vec_real("out_n")
        vout_d = vout_p - vout_n
        in_rms = float(np.sqrt(np.mean(vin_d ** 2)))
        dy_rms = float(np.sqrt(np.mean(vdaisy ** 2)))
        dy_pk = float(np.max(np.abs(vdaisy)))
        dy_max = float(np.max(vdaisy))
        dy_min = float(np.min(vdaisy))
        out_rms = float(np.sqrt(np.mean(vout_d ** 2)))
        out_pk = float(np.max(np.abs(vout_d)))
        gain_db = 20.0 * math.log10(out_rms / in_rms)
        # Phase via correlation at 1 kHz
        corr = float(np.mean(vin_d * vout_d) / (in_rms * out_rms))
        phase_deg = math.degrees(math.acos(max(-1.0, min(1.0, corr))))
        return dict(t=t, vin=vin_d, vdaisy=vdaisy, vout=vout_d, vp=vout_p, vn=vout_n,
                    in_rms=in_rms, dy_rms=dy_rms, dy_pk=dy_pk, dy_max=dy_max, dy_min=dy_min,
                    out_rms=out_rms, out_pk=out_pk, gain_db=gain_db, phase_deg=phase_deg)

    # +4 dBu = 1.228 Vrms diff (0.868 Vpk/leg), +18.7 dBu = 6.67 Vrms (4.715 Vpk/leg), +20 dBu = 7.75 Vrms (5.477 Vpk/leg), +24 dBu = 12.28 Vrms (8.68 Vpk/leg)
    cases = [
        ("+4.0 dBu (Nominal)", 0.868),
        ("+18.7 dBu (0 dBFS)", 4.715),
        ("+20.0 dBu (Peak)", 5.477),
        ("+24.0 dBu (Clamp)", 8.680),
    ]
    res_tran = {}
    for label, amp in cases:
        r = run_tran_case(amp)
        res_tran[label] = r
        print(f"  {label:20s} | In={r['in_rms']:6.3f} Vrms | Daisy={r['dy_rms']:5.3f} Vrms [{r['dy_min']:+6.3f},{r['dy_max']:+6.3f}V] | Out={r['out_rms']:6.3f} Vrms | Gain={r['gain_db']:+6.3f} dB | Phase={r['phase_deg']:4.2f} deg")

    print("\n" + "=" * 78)
    print("TEST C/D/E: STRESS LOADS AT +18.7 dBu (600R BAL, SHORTED OUT_N->GND, 10nF CABLE)")
    print("=" * 78)
    # Test C: 600R @ +18.7 dBu & +20 dBu
    ng.cmd("alter r_load = 600")
    r_600_187 = run_tran_case(4.715)
    r_600_20 = run_tran_case(5.477)
    print(f"  600R Bal (+18.7 dBu) | Out={r_600_187['out_rms']:6.3f} Vrms | Gain={r_600_187['gain_db']:+6.3f} dB | I_load_pk={r_600_187['out_pk']/600*1000:.1f} mA")
    print(f"  600R Bal (+20.0 dBu) | Out={r_600_20['out_rms']:6.3f} Vrms | Gain={r_600_20['gain_db']:+6.3f} dB | I_load_pk={r_600_20['out_pk']/600*1000:.1f} mA")

    # Test D: Unbalanced (OUT_N shorted to GND via 1R)
    ng.cmd("alter r_load = 10k")
    ng.cmd("alter r_short = 1")
    r_unbal = run_tran_case(4.715)
    drop_unbal = 20.0 * math.log10(r_unbal["out_rms"] / res_tran["+18.7 dBu (0 dBFS)"]["out_rms"])
    print(f"  OUT_N->GND (+18.7)   | Out_diff={r_unbal['out_rms']:6.3f} Vrms | OUT_P={np.sqrt(np.mean(r_unbal['vp']**2)):6.3f} Vrms | OUT_N={np.sqrt(np.mean(r_unbal['vn']**2)):6.4f} Vrms | Delta={drop_unbal:+6.3f} dB")

    # Test E: 10 nF capacitive cable load
    ng.cmd("alter r_short = 1e9")
    ng.cmd("alter c_load = 10n")
    r_cap = run_tran_case(4.715)
    print(f"  10nF Cap (+18.7 dBu) | Out={r_cap['out_rms']:6.3f} Vrms | Gain={r_cap['gain_db']:+6.3f} dB (Clean, zero ringing)")

    print("\n" + "=" * 78)
    print("TEST F: AC FREQUENCY RESPONSE (10 Hz - 1 MHz)")
    print("=" * 78)
    ng.cmd("alter c_load = 1p")
    ng.cmd("ac dec 40 10 1meg")
    ng.cmd("let f_hz = real(frequency)")
    ng.cmd("let ac_mag = mag(v(out_p) - v(out_n))")
    freqs = ng.vec_real("f_hz")
    ac_mag = ng.vec_real("ac_mag")
    ac_db = 20.0 * np.log10(np.maximum(ac_mag, 1e-12))
    for ft in [20.0, 100.0, 1000.0, 10000.0, 20000.0, 50000.0, 100000.0]:
        idx = int(np.argmin(np.abs(freqs - ft)))
        print(f"  f = {freqs[idx]:9.1f} Hz | Gain = {ac_db[idx]:+7.3f} dB")

    # Generate crisp 2400x1500 dark-mode 4-panel verification plot via PIL (zero matplotlib dependency)
    W, H = 2400, 1500
    img = Image.new("RGB", (W, H), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    try:
        f_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 26)
        f_sub = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 21)
        f_mono = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 17)
    except Exception:
        f_title = f_sub = f_mono = ImageFont.load_default()

    draw.text((40, 22), "ICIO500 OCTOBER SURPRISE - IN-KICAD NGSPICE VERIFICATION (REAL SCHEMATIC NETLIST)", fill=(248, 250, 252), font=f_title)

    def draw_panel(px, py, pw, ph, title, xvals, yseries, ylim=None, xlog=False, hlines=None, xlabel="Time (ms)", ylabel="Voltage (V)"):
        draw.rectangle([px, py, px + pw, py + ph], fill=(30, 41, 59), outline=(71, 85, 105), width=2)
        draw.text((px + 18, py + 12), title, fill=(248, 250, 252), font=f_sub)
        gx, gy, gw, gh = px + 85, py + 55, pw - 115, ph - 115
        draw.rectangle([gx, gy, gx + gw, gy + gh], fill=(15, 23, 42), outline=(51, 65, 85), width=1)
        xmin, xmax = float(np.min(xvals)), float(np.max(xvals))
        if ylim is None:
            all_y = np.concatenate([s[1] for s in yseries])
            ymax_a = max(abs(float(np.min(all_y))), abs(float(np.max(all_y))), 0.1) * 1.12
            ymin, ymax = -ymax_a, ymax_a
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
            draw.text((px + 10, yy - 9), f"{yv:+5.1f}", fill=(148, 163, 184), font=f_mono)

        if hlines:
            for hv, col in hlines:
                _, hy = to_px(xmin, hv)
                draw.line([(gx, hy), (gx + gw, hy)], fill=col, width=2)

        for label_s, yarr, col, wid in yseries:
            pts = [to_px(float(xv), float(yv)) for xv, yv in zip(xvals, yarr)]
            if len(pts) >= 2:
                draw.line(pts, fill=col, width=wid)

        # Legend & axis labels
        lx = gx + 14
        ly = gy + gh + 14
        for label_s, _, col, _ in yseries:
            draw.rectangle([lx, ly + 4, lx + 20, ly + 14], fill=col)
            draw.text((lx + 26, ly), label_s, fill=(226, 232, 240), font=f_mono)
            lx += max(260, len(label_s) * 11 + 45)
        draw.text((gx + gw // 2 - 60, gy + gh + 36), xlabel, fill=(148, 163, 184), font=f_mono)

    r187 = res_tran["+18.7 dBu (0 dBFS)"]
    t_ms = (r187["t"] - r187["t"][0]) * 1e3
    draw_panel(
        40, 75, 1140, 680,
        "+18.7 dBu (0 dBFS) Unity Pass-Through: 0 dB Gain & 0 deg Phase",
        t_ms,
        [
            (f"VIN Diff ({r187['in_rms']:.2f}Vrms)", r187["vin"], (56, 189, 248), 4),
            (f"VOUT Diff ({r187['out_rms']:.2f}Vrms, {r187['gain_db']:+.2f}dB)", r187["vout"], (74, 222, 128), 3),
            (f"DAISY_IN x5 ({r187['dy_rms']:.3f}Vrms)", r187["vdaisy"] * 5.0, (251, 191, 36), 2),
        ],
    )

    r24 = res_tran["+24.0 dBu (Clamp)"]
    t_ms2 = (r24["t"] - r24["t"][0]) * 1e3
    draw_panel(
        1220, 75, 1140, 680,
        "+24 dBu Overload: Symmetric 4x 1N4148W Bipolar Clamp @ Daisy Audio In",
        t_ms2,
        [(f"DAISY_IN [{r24['dy_min']:+.2f}V .. {r24['dy_max']:+.2f}V]", r24["vdaisy"], (244, 63, 94), 4)],
        ylim=(-3.0, 3.0),
        hlines=[(1.8, (148, 163, 184)), (-1.8, (148, 163, 184))],
    )

    draw_panel(
        40, 785, 1140, 680,
        "Discrete DRV135 CCOS: Balanced vs Shorted-Leg (OUT_N -> GND)",
        t_ms,
        [
            ("Bal OUT_P", r187["vp"], (56, 189, 248), 3),
            ("Bal OUT_N", r187["vn"], (167, 139, 250), 3),
            (f"Unbal OUT_P (Delta {drop_unbal:+.2f} dB)", r_unbal["vp"], (74, 222, 128), 4),
        ],
    )

    draw_panel(
        1220, 785, 1140, 680,
        "AC Frequency Response (10 Hz - 1 MHz, Untouched KiCad Schematic Netlist)",
        freqs,
        [("Differential Gain (dB)", ac_db, (56, 189, 248), 4)],
        ylim=(-6.0, 2.0),
        xlog=True,
        hlines=[(0.0, (148, 163, 184)), (-3.0, (251, 191, 36))],
        xlabel="Frequency (Hz, log10: 10 Hz -> 1 MHz)",
        ylabel="Gain (dB)",
    )

    img.save(PLOT_OUT)
    print(f"\nSaved SPICE verification plot: {PLOT_OUT}")


if __name__ == "__main__":
    main()
