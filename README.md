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
| [`kicad/`](kicad/) | Active KiCad PCBs, schematics, project files, symbols (`icio500.kicad_sym`), local footprint libraries (`Cards.pretty/`, `custom.pretty/`), `3d_models/`, 3D assemblies, and `archived_v1/`. |
| [`fabrication/`](fabrication/) | Ready-to-upload manufacturing packages separated into `in_production/` (locked), `satellite_faceplate/` (active), and `archived_v1_blind_slot/`. |
| [`firmware/`](firmware/) | Daisy Seed C++ DSP projects (`roomove/`, `cloudseed/`, `daisyverb/`, `covol/`, `funbox_reverbs/`) and shared pinout header `common/icio500_hw.h`. |
| [`scripts/`](scripts/) | Python CAD, KiCad PCB/3D assembly, DRC, and fab-export scripts (`archive/` holds historical one-off carrier/v1 scripts). |
| [`renders/`](renders/) | Verified high-resolution KiCad 3D renders of the modular satellite assemblies and rear PCB layout. |
| [`docs/`](docs/) | API VPR-500 mechanical spec (`api_vpr_500_spec.pdf`), schematics PDF (`icio500_schematic.pdf`), legacy `ICIO 3.sch`, guides, and `legacy_atopile/` sources (`ato.yaml`, `elec/`). |

---

## Board & Fabrication Status

| Subsystem | Design Files | Manufacturing Package | Status |
| :--- | :--- | :--- | :--- |
| **VPR-500 Carrier PCB** | `kicad/icio500.kicad_pcb`, `kicad/icio500.kicad_sch` | [`fabrication/in_production/jlcpcb_carrier/`](fabrication/in_production/jlcpcb_carrier/) | **IN PRODUCTION (Locked)** |
| **Encoder Daughtercard** | `kicad/encoder_board.kicad_pcb` | [`fabrication/in_production/jlcpcb_encoder/`](fabrication/in_production/jlcpcb_encoder/) | **IN PRODUCTION (Locked)** |
| **Capstan Vernier Knob** | [`scripts/generate_capstan_knob.py`](scripts/generate_capstan_knob.py) | [`fabrication/in_production/jlc3dp_knob/`](fabrication/in_production/jlc3dp_knob/) | **IN PRODUCTION (Locked)** |
| **0.8 mm Satellite Active PCB** | `kicad/faceplate_satellite.kicad_pcb`, `kicad/faceplate_logic.kicad_sch` | [`fabrication/satellite_faceplate/jlcpcb_satellite_pcb/`](fabrication/satellite_faceplate/jlcpcb_satellite_pcb/) | **ACTIVE (0.8 mm 2L FR4, Matte Black)** |
| **Swappable Front Panels** | [`scripts/generate_sendcutsend_faceplates.py`](scripts/generate_sendcutsend_faceplates.py) | [`fabrication/satellite_faceplate/sendcutsend_panels/`](fabrication/satellite_faceplate/sendcutsend_panels/) | **ACTIVE (SendCutSend/Ponoko DXFs + STEP + Preview)** |
| **v1.0 Blind-Slot Faceplate** | [`kicad/archived_v1/faceplate_front.kicad_pcb`](kicad/archived_v1/faceplate_front.kicad_pcb) | [`fabrication/archived_v1_blind_slot/`](fabrication/archived_v1_blind_slot/) | **ARCHIVED (`v1.0-jlc-blind-slot-faceplate`)** |

---

## Modular Satellite Stackup Notes
- **Hidden Satellite Inset:** `faceplate_satellite.kicad_pcb` (`35.10 × 113.35 mm`, `0.8 mm` 2-layer FR4, recommend **Matte Black** soldermask) sits inset `1.50 mm` left/right and `10.00 mm` top/bottom behind the `38.10 × 133.35 mm` front panel so only the single-layer wood/acrylic panel meets the 500-series rack rails.
- **No Blind Slots Required:** Reverse-mount gull-wing LEDs (`D1..D16`) mount on `B.Cu` over standard `1.92 × 1.68 mm` full NPTH oval slots.
- **Front Panel Diffuser Options:**
  - *Horizontal-Slot Wood (`0.125"` / `3.175 mm`):* `10×` `7.20 × 2.40 mm` horizontal stadium slots (`8.00 mm` pitch) + `6× Ø2.40 mm` knob-ring ports, backed by a flat sheet of translucent milky-white diffusion tape/film (e.g., `3M 3635-70` or Roscolux Tough Frost) sandwiched between the Satellite PCB and Wood.
  - *Dead-Front Smoked Acrylic (`0.118"` / `3.000 mm`):* Zero LED cutouts — all `16` LEDs shine directly through the translucent smoked panel.
- **Mechanical Mating:** `BR1/BR2` (`WP-SMRA-M3`), `J1` (`2x10` header), top `2× M2.5` screws, and the `PEC11R` `M7` bushing mate directly with the locked Carrier and Encoder PCBs. With `3.00–3.18 mm` front panels, place a `~1.8–2.0 mm` spacer inside the in-production Capstan Knob bore to maintain the `1.00 mm` click clearance.
