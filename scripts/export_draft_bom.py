#!/usr/bin/env python3
"""Export grouped draft BOM from kicad/october_surprise.kicad_sch."""

import csv
import os
import re
from collections import defaultdict

SCH_PATH = os.path.join("kicad", "october_surprise.kicad_sch")
BOM_OUT = os.path.join("docs", "october_surprise_draft_bom.csv")

# Verified live JLCPCB stock & unit price captured 2026-11-25 via JLCPCB API
LCSC_CATALOG = {
    "C1849431": ("6149", "1.2422", "TI OPA1656IDR SOIC-8 FET-input Audio Op-Amp"),
    "C53183920": ("640", "5.5022", "Traco Power TSR 1-2450 5V 1A Buck SIP-3"),
    "C2480": ("1078075", "0.0192", "SS14 40V 1A SMA Schottky Barrier Diode (Basic)"),
    "C81598": ("4255009", "0.0123", "1N4148W 100V Fast Switching SOD-123 (Basic)"),
    "C970697": ("43580", "0.0747", "220uF 35V SMD Electrolytic D8xL10.2mm"),
    "C2840662": ("19871", "0.1832", "KNSCHA MEB105J100V 1uF 100V ±5% Metallized Polyester Film P=5mm"),
    "C95204": ("2016998", "0.0238", "Yageo RT0603BRD0710KL 10k 0.1% 25ppm Thin Film 0603"),
    "C723585": ("1003232", "0.0285", "Yageo RT0603BRD0730KL 30k 0.1% 25ppm Thin Film 0603"),
    "C705741": ("305119", "0.0316", "Yageo RT0603BRD071K5L 1.5k 0.1% 25ppm Thin Film 0603"),
    "C860418": ("3607", "0.036", "Yageo RT0603BRB074K22L 4.22k 0.1% Thin Film 0603"),
    "C861434": ("47661", "0.0377", "Yageo RT0603BRD0749R9L 49.9R 0.1% 25ppm Thin Film 0603"),
    "C728678": ("3206", "0.0871", "Yageo RT1206BRE0749R9L 49.9R 200V 250mW ±0.1% 50ppm Thin Film 1206"),
    "C326725": ("14655", "0.0388", "Yageo RT0603BRD0747KL 47k 0.1% 25ppm Thin Film 0603"),
    "C122538": ("1360587", "0.0208", "Yageo RT0603BRD07100KL 100k 0.1% 25ppm Thin Film 0603"),
    "C21190": ("38153010", "0.0015", "UNI-ROYAL 0603WAF1001T5E 1k 1% 0603 (Basic)"),
    "C22775": ("12286586", "0.0017", "UNI-ROYAL 0603WAF1000T5E 100R 1% 0603 (Basic)"),
    "C22859": ("stock>10M", "0.0017", "UNI-ROYAL 0603WAF100JT5E 10R 5% 0603 (Basic)"),
    "C14663": ("43599463", "0.0047", "Yageo CC0603KRX7R9BB104 100nF 50V X7R 0603 (Basic)"),
    "C27675": ("126020", "0.0087", "Samsung CL10C221JB8NNNC 220pF 50V C0G 0603"),
    "C14858": ("2806683", "0.0084", "Samsung CL10C101JB8NNNC 100pF 50V C0G 0603 (Basic)"),
    "C1671": ("1036109", "0.0053", "Samsung CL10C470JB8NNNC 47pF 50V C0G 0603 (Basic)"),
    "C1653": ("2604895", "0.0089", "Samsung CL10C220JB8NNNC 22pF 50V C0G 0603 (Basic)"),
    "C124410": ("2080", "0.3763", "Ckmtw B-2200S20P-A120 1x20P 2.54mm Female Brass Square Socket"),
    "C5383093": ("427", "0.0824", "2541WR-2x10P 2.54mm Right-Angle 2x10 Male Shrouded Header"),
    "C32713264": ("14881", "0.0460", "HX PZ2.54-1x5P WZ 2.54mm Right-Angle 1x5 Male Header"),
    "C78413": ("479019", "0.0540", "SMBJ18CA/TR13 18V 600W Bidirectional TVS DO-214AA (SMB)"),
    "C82401": ("2391", "0.0640", "Sunlord SWPA4020S220MT 22uH 1.05A 455mOhm Shielded Inductor"),
    "C6808084": ("44664", "0.0470", "ANR4018T100M 10uH 1.2A 215mOhm Shielded Inductor"),
    "C1017": ("681488", "0.0150", "GZ2012D601TF 600R@100MHz 500mA 0805 Ferrite Bead (Basic)"),
    "C76666": ("11484", "0.2710", "TDK C3216X7R1V106KT000E 10uF 35V X7R 1206 MLCC"),
    "C113819": ("76133", "0.0134", "Yageo CC0805JRNPO0BN221 220pF 100V ±5% C0G 0805"),
    "C107033": ("938429", "0.0073", "Yageo CC0603JRNPO0BN101 100pF 100V ±5% C0G 0603"),
    "C319961": ("5548", "0.0545", "Viking AR06BTCV1000 100R 200V 250mW ±0.1% 25ppm Thin Film 1206"),
    "C110776": ("837615", "0.0275", "Yageo RT0603BRD071KL 1k 75V ±0.1% 25ppm Thin Film 0603"),
    "C113947": ("635226", "0.0138", "BAV21W 200V/250Vrrm 200mA High-Voltage Switching Diode SOD-123"),
    "C2874007": ("52310", "0.2022", "XFCN IC254V-12-08-0743 Machined Round-Pin DIP-8 Socket (for socketed U2)"),
}


def main():
    txt = open(SCH_PATH, encoding="utf-8").read()
    groups = defaultdict(set)
    idx = 0
    while True:
        pos = txt.find("  (symbol (", idx)
        if pos == -1:
            break
        d = 0
        for i in range(pos, len(txt)):
            if txt[i] == "(":
                d += 1
            elif txt[i] == ")":
                d -= 1
                if d == 0:
                    end = i + 1
                    break
        blk = txt[pos:end]
        idx = end
        if "(in_bom no)" in blk:
            continue
        def prop(k):
            m = re.search(rf'\(property "{k}" "([^"]*)"', blk)
            return m.group(1) if m else ""
        ref = prop("Reference")
        if ref.startswith("#"):
            continue
        key = (prop("Value"), prop("Footprint"), prop("MPN"), prop("LCSC"), prop("VoltageRating"))
        groups[key].add(ref)

    def ref_sort_key(r):
        m = re.match(r"([A-Za-z_]+?)(\d*)$", r)
        return (m.group(1), int(m.group(2)) if m and m.group(2) else 0)

    os.makedirs(os.path.dirname(BOM_OUT), exist_ok=True)
    with open(BOM_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Qty", "Designators", "Value", "Footprint", "MPN", "LCSC Part #", "Voltage Rating", "LCSC Live Stock", "Unit Price ($)", "Description"])
        total_bom = 0.0
        for (val, fp, mpn, lcsc, vr), refs in sorted(groups.items(), key=lambda kv: ref_sort_key(sorted(kv[1])[0])):
            srefs = sorted(refs, key=ref_sort_key)
            stk, price, desc = LCSC_CATALOG.get(lcsc, ("-", "-", "Card edge PCB fingers (no BOM part)" if not lcsc else ""))
            try:
                total_bom += float(price) * len(srefs)
            except Exception:
                pass
            w.writerow([len(srefs), ", ".join(srefs), val, fp, mpn, lcsc, vr, stk, price, desc])

    print(f"Wrote {BOM_OUT} ({len(groups)} unique lines, est. component subtotal ${total_bom:.2f}/board)")


if __name__ == "__main__":
    main()
