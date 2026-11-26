# ICIO500

Transformerless line-in and line-out prototyping platform for the **API VPR-500** 500-series modular rack (`1.500" × 5.250"`), powered by a Daisy Seed DSP carrier card, a vertical rotary-encoder daughtercard, and a modular **0.8 mm Satellite PCB + Swappable Front Panel** faceplate stackup.

---

## Quick Start: View the Full 3D Module in KiCad
1. Open either full 3D assembly in KiCad 10 PCB Editor:
   - **Walnut / Stained Wood Horizontal Slots + Diffuser Film:** [`kicad/icio500_satellite_wood_3d.kicad_pcb`](kicad/icio500_satellite_wood_3d.kicad_pcb)
   - **Dead-Front Smoked Acrylic:** [`kicad/icio500_satellite_acrylic_3d.kicad_pcb`](kicad/icio500_satellite_acrylic_3d.kicad_pcb)
2. Press **`Alt + 3`** to orbit the full stackup (`Carrier PCB` + `Encoder Daughtercard` + inset `0.8 mm Satellite PCB` + `Front Panel` + `Capstan Knob`).
3. Browse pre-rendered views directly in [`renders/`](renders/).

---

## Repository Structure

| Folder | Contents |
| :--- | :--- |
| [`kicad/`](kicad/) | Active KiCad PCBs, schematics (`october_surprise.kicad_sch` + `october_surprise.kicad_pcb`), local footprint libraries (`Cards.pretty/`, `custom.pretty/`), `spice_models/`, `3d_models/`, and 3D assemblies. |
| [`fabrication/`](fabrication/) | Ready-to-upload manufacturing packages separated into `in_production/` (locked) and `satellite_faceplate/` (active). |
| [`firmware/`](firmware/) | Daisy Seed C++ DSP projects (`roomove/`, `cloudseed/`, `daisyverb/`, `covol/`, `funbox_reverbs/`) and shared pinout header `common/icio500_hw.h`. |
| [`scripts/`](scripts/) | Python CAD, KiCad schematic/PCB builder, in-KiCad `ngspice` verification, BOM export, DRC, and fab-export scripts. |
| [`renders/`](renders/) | Verified high-resolution KiCad 3D renders of the modular satellite assemblies and rear PCB layout. |
| [`docs/`](docs/) | API VPR-500 mechanical spec (`api_vpr_500_spec.pdf`), raw manufacturer PDFs (`datasheets/`), `october_surprise_schematic.pdf`, draft BOM, and `ngspice` verification plots. |
| [`archive/`](archive/) | Archived Rev-1 carrier reference (`archive/rev1_bad_carrier/`), preserved strictly as mechanical salvage reference. |

---

## Board & Fabrication Status

| Subsystem | Design Files | Manufacturing Package | Status |
| :--- | :--- | :--- | :--- |
| **VPR-500 Carrier PCB (`October Surprise` Rev 2)** | `kicad/october_surprise.kicad_sch`, `kicad/october_surprise.kicad_pcb` | *(Pre-routing — Subcircuit #1 `POWER` verified)* | **IN DESIGN (Schematic-First + In-KiCad `ngspice`)** |
| **Encoder Daughtercard** | `kicad/encoder_board.kicad_pcb` | [`fabrication/in_production/jlcpcb_encoder/`](fabrication/in_production/jlcpcb_encoder/) | **IN PRODUCTION (Locked)** |
| **Capstan Vernier Knob** | [`scripts/generate_capstan_v2_knob.py`](scripts/generate_capstan_v2_knob.py) | [`fabrication/in_production/jlc3dp_knob_v2/`](fabrication/in_production/jlc3dp_knob_v2/) | **IN PRODUCTION (Locked)** |
| **0.8 mm Satellite Active PCB** | `kicad/faceplate_satellite.kicad_pcb`, `kicad/faceplate_logic.kicad_sch` | [`fabrication/satellite_faceplate/jlcpcb_satellite_pcb/`](fabrication/satellite_faceplate/jlcpcb_satellite_pcb/) | **ACTIVE (0.8 mm 2L FR4, Matte Black)** |
| **Swappable Front Panels** | [`scripts/generate_sendcutsend_faceplates.py`](scripts/generate_sendcutsend_faceplates.py) | [`fabrication/satellite_faceplate/sendcutsend_panels/`](fabrication/satellite_faceplate/sendcutsend_panels/) | **ACTIVE (SendCutSend/Ponoko DXFs + STEP + Preview)** |

---

## Modular Satellite Stackup Notes
- **Hidden Satellite Inset:** `faceplate_satellite.kicad_pcb` (`35.10 × 113.35 mm`, `0.8 mm` 2-layer FR4, recommend **Matte Black** soldermask) sits inset `1.50 mm` left/right and `10.00 mm` top/bottom behind the `38.10 × 133.35 mm` front panel so only the single-layer wood/acrylic panel meets the 500-series rack rails.
- **No Blind Slots Required:** Reverse-mount gull-wing LEDs (`D1..D16`) mount on `B.Cu` over standard `1.92 × 1.68 mm` full NPTH oval slots.
- **Front Panel Diffuser Options:**
  - *Horizontal-Slot Wood (`0.125"` / `3.175 mm`):* `10×` `7.20 × 2.40 mm` horizontal stadium slots (`8.00 mm` pitch) + `6× Ø2.40 mm` knob-ring ports, backed by a flat sheet of translucent milky-white diffusion tape/film (e.g., `3M 3635-70` or Roscolux Tough Frost) sandwiched between the Satellite PCB and Wood.
  - *Dead-Front Smoked Acrylic (`0.118"` / `3.000 mm`):* Zero LED cutouts — all `16` LEDs shine directly through the translucent smoked panel.
- **Mechanical Mating:** `BR1/BR2` (`WP-SMRA-M3`), `J1` (`2x10` header), top `2× M2.5` screws, and the `PEC11R` `M7` bushing mate directly with the locked Carrier and Encoder PCBs. With `3.00–3.18 mm` front panels, place a `~1.8–2.0 mm` spacer inside the in-production Capstan Knob bore to maintain the `1.00 mm` click clearance.
