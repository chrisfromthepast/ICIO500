# ICIO500 "October Surprise" — Engineering & Marketing Cheat Sheet

> **Verification Legend (For Copywriting Accuracy)**
> - **[SPICE / CAD Verified]:** Measured directly from KiCad 10's built-in `ngspice` simulator running on the real exported schematic netlist ([october_surprise.kicad_sch](october_surprise.kicad_sch)), live JLCPCB API stock, and raw manufacturer PDFs.
> - **[Bench TBD — Rev 2 Hardware]:** Physical Audio Precision THD+N%, real-world rack chassis CMRR, and in-rack noise floor will be measured on assembled Rev 2 carrier hardware before publishing final spec sheets.

---

## Elevator Pitch
**Studio-grade VPR-500 transformerless balanced DSP carrier with customizable wood & dead-front acrylic faceplates.**  
Designed around the **Daisy Seed DSP** platform and TI's **OPA1656 SoundPlus™** op-amp architecture, *October Surprise* pairs passive low-noise power filtering, `+48 V` phantom-hardened instrumentation inputs with a **socketed `U2` input stage**, discrete cross-coupled "floating-style" balanced outputs, and a swappable `0.8 mm` modular faceplate system.

---

## 1. Whisper-Quiet Power Architecture (`POWER` — Locked & SPICE-Verified)
Most 500-series DSP cards leak switching regulator hash onto the analog rails or add linear regulator noise. *October Surprise* isolates the digital DSP power completely and keeps the `±16 V` audio rails purely passive:

- **Zero LDO Audio-Rail Noise [CAD/SPICE Verified]:** Audio `±16 V` rails use **passive shielded power inductors (`10 µH`, `ANR4018T100M`) + `600 Ω @ 100 MHz` ferrite bead Pi-filters + `220 µF / 35 V` + `10 µF / 35 V` banks** — zero active LDO self-noise or dropout thermal drift.
- **Massively Damped & Filtered Rails [SPICE Verified]:** `0.00 dB` LC resonance peaking (`10 Hz – 10 MHz`), rejecting rack power noise by **`-106.9 dB @ 100 kHz`** and **`-178.3 dB @ 500 kHz`**.
- **Isolated `500 kHz` Digital Buck Feeder [SPICE Verified]:** The Daisy Seed `+5 V` buck (`Traco TSR 1-2450`) is isolated behind an upstream `22 µH` shielded choke (`SWPA4020S220MT`) + `230 µF` input/output tank and downstream `10 µH + 600 Ω` Pi-filter, keeping simulated `500 kHz` (`150 mAp-p`) buck ripple on the analog `+16 V` rail down to **`0.86 µVp-p` (`47.7 dB` total attenuation)**.
- **Rack Surge & Reversed-Slot Armor [CAD/Datasheet Verified]:** Series `SS14` Schottkys protect against reversed power pins, backed by dual **`600 W` `SMBJ18CA` bidirectional TVS clamps** (`V_WM = 18 V`, clamping `<= 29.2 V @ 20.5 A` — safely below every `35 V` capacitor and `36 V` op-amp rating).

---

## 2. Studio-Grade, `+48 V` Phantom-Proof Input (`BALANCED INPUT` — Locked & SPICE-Verified)
Built to handle brutal studio patching accidents (`+48 V` phantom hot-plugs, shorted TRS cables, `+24 dBu` console overs) without compromising fidelity or locking you out of repairability:

- **True 3-Op-Amp Instrumentation Topology (`TI OPA1656`) [CAD Verified]:** High `200 kΩ` balanced input impedance prevents source-impedance CMRR loss regardless of what console, synth, or mic pre feeds the module (`124.4 dB` ideal CMRR @ `1 kHz`; **`~60–66 dB` worst-case CMRR** guaranteed with `0.1%` thin-film resistors).
- **Zero Class-II MLCCs in the Audio Path [CAD/Datasheet Verified]:** Audio coupling uses **`100 V` Metallized Polyester Film (`1 µF` `MEB105J100V`)** and RF filtering uses **`100 V` `C0G/NP0` ceramic (`220 pF` / `100 pF`)** — zero ferroelectric distortion or microphonics, `>= 2.1×` voltage margin over `+48 V` phantom power, and **`-23.9 dB @ 1 MHz` / `-47.0 dB @ 10 MHz`** RF rejection.
- **Whisper-Quiet Noise Floor [SPICE + Datasheet Verified]:** **`118.5 dB` front-end dynamic range** relative to `+18.7 dBu` (`0 dBFS`), with **`1.18 µVrms` total `20 Hz – 20 kHz` noise** at the codec (`7.96 µVrms` / `-99.8 dBu` input-referred) and **`0.027 dB` audio passband flatness (`20 Hz – 20 kHz`)**.
- **`+48 V` Hot-Plug & `-48 V` Cap-Discharge Slam Armor [SPICE Verified]:** `100 Ω 1206` (`200 V / 250 mW / 0.1%`) surge resistors + `250 V 0.5 pF` Vishay `BAV21W` rail clamps + `1.0 kΩ 0.1%` ESD stoppers hold worst-case op-amp pin current to **`2.76 mA`** (`3.6×` below `OPA1656`'s `10 mA` absolute maximum) even during a worst-case direct **`+48 V` (`10 Ω`) → `0 V` cap-discharge slam**.
- **Soft Symmetric Overdrive Protection (`+24 dBu` Safe) [SPICE Verified]:** Four series antiparallel `1N4148W` diodes per polarity protect the `0 V`-centered AC-coupled Daisy Seed ADC cleanly — completely invisible through `+20 dBu`, engaging gently above `±1.8 V` to clamp `+24 dBu` faults symmetrically at **`[-2.43 V, +2.42 V]`** (unlike `GND/+3.3 V` Schottky clamps that hard-clip negative audio swings).
- **Socketed Input Silicon (`U2` Machined DIP-8 Socket) [CAD/BOM Verified]:** Because `U2` is the frontline chip exposed to the outside world, it sits in a **machined round-pin DIP-8 socket (`C2874007`)** — field-serviceable in seconds without a soldering iron, and ready for drop-in op-amp rolling (`OPA1656IDR` on a `SOIC-8 → DIP-8` adapter, or classic dual DIP-8 audio chips like `OPA2134PA`, `LM4562NA`, `NE5532P`).

---

## 3. Floating Transformer-Like Output (`OUTPUT / CCOS` — Baseline Verified; Hardening Pass Next)
- **Discrete Cross-Coupled Output Stage (`DRV135` Topology, Zero EOL Silicon) [CAD/SPICE Verified]:** Built from `OPA1656` + `0.1%` `30 kΩ` thin-film resistors rather than hard-to-source specialty driver chips.
- **Automatic Unbalanced Load Compensation [SPICE Verified]:** Keeps true `0 dB` (`-0.071 dB`) unity gain and `0.41°` phase linearity through `+20 dBu`, and automatically shifts signal onto the hot leg with only a **`-0.025 dB`** differential level change when `OUT_N` is shorted straight to `GND` (TS/unbalanced patchbay safe).
- **Studio Line-Drive Brawn [SPICE Verified]:** Drives **`600 Ω` studio loads cleanly at `+20 dBu`** (`16.8 mA` peak) and handles **`10 nF` long-cable capacitance** with zero ringing.

---

## 4. Modular Mechanical & Faceplate System
- **Hidden `0.8 mm` Matte-Black Satellite PCB + Swappable Front Panels:** Clean `1.500" × 5.250"` VPR-500 module depth where `16` reverse-mount LEDs shine cleanly through interchangeable **Stained Wood** (horizontal stadium diffuser slots) or **Dead-Front Smoked Acrylic** front panels paired with our precision **Capstan Vernier Knob**.
- **Modular Silkscreen Subcircuit Architecture:** Every analog/power stage (`POWER`, `BALANCED INPUT`, etc.) is isolated inside labeled silkscreen zones on the carrier PCB for clean serviceability and probing.

---

## 5. Copy-Paste Spec Sheet Table (with Verification Status)

| Parameter | Spec Value | Verification Status |
| :--- | :--- | :--- |
| **Format & Rails** | API VPR-500 (`1.500" × 5.250"`), `±16 V` rack rails | Physical CAD / VPR spec verified |
| **Input Architecture** | Transformerless 3-op-amp INA (`TI OPA1656`), **DIP-8 socketed `U2`** | Verified in [october_surprise.kicad_sch](october_surprise.kicad_sch) |
| **Balanced Input Impedance** | `200 kΩ` differential (`R3/R4 = 100 kΩ 0.1%`) | CAD / datasheet verified |
| **Operating Headroom / Unity** | `+18.7 dBu` (`0 dBFS`), `+20 dBu` linear, `±2.42 V` clamp @ `+24 dBu` | **SPICE-verified** (real schematic netlist) |
| **Frequency Response (`20 Hz – 20 kHz`)** | `-0.096 dB` (`20 Hz`), `-0.069 dB` (`1 kHz`), `-0.127 dB` (`20 kHz`) | **SPICE-verified** (full chain unity) |
| **Input Stage Noise / Dynamic Range** | `7.96 µVrms` (`-99.8 dBu`) input-referred / **`118.5 dB` DR** (rel. `+18.7 dBu`) | **SPICE resistors + OPA1656 `2.9 nV/√Hz`** |
| **RF Filtering** | `-23.9 dB @ 1 MHz`, `-47.0 dB @ 10 MHz` (`100 V C0G`) | **SPICE-verified** (Input Stage `.ac`) |
| **`+48 V` Phantom Fault Survivability** | `max\|I_in(U2)\| = 2.76 mA` (`< 10 mA` limit) on `10 Ω` `+48 V → 0 V` slam | **SPICE-verified** (`6.0 ms` transient) |
| **Analog Power-Rail Rejection** | `0.00 dB` LC peaking; `-106.9 dB @ 100 kHz`, `-178.3 dB @ 500 kHz` | **SPICE-verified** (loaded `.ac`) |
| **Output Stage (`CCOS` Unbal Drop)** | `-0.025 dB` (`OUT_N → GND`); `+20 dBu` into `600 Ω` | **SPICE-verified** (baseline DRV135 discrete) |
| **System THD+N% & Rack CMRR** | Targeted `< 0.001%` / `>= 60 dB` (`0.1%` resistors) | **[Bench TBD — Rev 2 Hardware]** |
