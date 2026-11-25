# ICIO500 JLC Carrier Board (Rev 1) — Hardware Issues & Bring-Up Guide

> [!CAUTION]
> **DO NOT PLUG THIS REV-1 BOARD INTO A 500-SERIES RACK AS-RECEIVED.**
> Even with `U2` and `U4` unpopulated, **`C3` and `C27` (`220 µF / 25 V`) are installed backwards on the `-16 V` rail** and will suffer `16 V` reverse bias on power-up.
> **DO NOT SOLDER `THAT1200S08-U` ONTO `U2` OR `THAT1646S08-U` ONTO `U4`.** Both SOIC-8 footprints on the carrier PCB have scrambled pinouts relative to the official THAT Corporation datasheets.

This document records every defect, BOM/package caveat, and bring-up check found in an exhaustive audit of the locked Rev-1 JLCPCB fabrication pack ([carrier_bom.csv](carrier_bom.csv), [carrier_cpl.csv](carrier_cpl.csv), [carrier_gerbers.zip](carrier_gerbers.zip)), [icio500.kicad_pcb](../../../kicad/icio500.kicad_pcb), and [icio500.kicad_sch](../../../kicad/icio500.kicad_sch). None of the fabrication files in this folder have been altered.

---

## 1. Critical / Board-Destroying Defects (Must Fix Before Power-Up)

### 1.1 `U4` (`THAT1646S08-U`, LCSC `C5290156`) — 7 of 8 Pins Scrambled

**Root cause:** [that1600_stage.ato](../../../docs/legacy_atopile/elec/src/that1600_stage.ato#L5-L15) assigned the SOIC-8 pins incorrectly; those pin numbers propagated directly into symbol `icio500:THAT1646` in [icio500.kicad_sch](../../../kicad/icio500.kicad_sch#L2611-L2632) and footprint `U4` in [icio500.kicad_pcb](../../../kicad/icio500.kicad_pcb#L10379-L10450).

Comparison against the official THAT Corporation datasheet (**THAT 1606/1646 Doc 600078 Rev 07, Table 1, SO8 column**):

| SOIC-8 Pin | Datasheet (`THAT1646`, SO8) | Carrier PCB `U4` Net | Status |
| :---: | :--- | :--- | :--- |
| **1** | `Out-` | `out_plus_4dbu` | **WRONG** (Output− wired to J1 Out+) |
| **2** | `Sns-` | `v_minus` (`-16 V`) | **WRONG (`-16 V` rail directly into `Sns-`)** |
| **3** | `Gnd` | `out_minus` | **WRONG** |
| **4** | `In` | `gnd` | **WRONG** |
| **5** | `Vee` (`-16 V`) | `audio_out_to_1646` | **WRONG** (`Vee` gets no `-16 V` rail; tied to `U3.7` op-amp output) |
| **6** | `Vcc` (`+16 V`) | `v_plus` (`+16 V`) | OK *(only matching pin)* |
| **7** | `Sns+` | `sense_minus` | **WRONG** (swapped with `Sns-`, also tied to inverted output cap `C22`) |
| **8** | `Out+` | `sense_plus` | **WRONG** |

**Consequence:** Immediate IC destruction if populated directly onto the `U4` PCB pads and powered.

---

### 1.2 `U2` (`THAT1200S08-U` / `1200S08-U`, LCSC `C3202799`) — Pins 6, 7, 8 Shifted

**Root cause:** [that1200_stage.ato](../../../docs/legacy_atopile/elec/src/that1200_stage.ato#L5-L15) mis-numbered Pins 5–8 (`Sm` on 5, `Cm` on 6, `Out` on 7, `V_Plus` on 8); those pin numbers propagated directly into `icio500:THAT1200` in [icio500.kicad_sch](../../../kicad/icio500.kicad_sch#L2589-L2610) and `U2` in [icio500.kicad_pcb](../../../kicad/icio500.kicad_pcb#L13513-L13584).

Comparison against the official THAT Corporation datasheet (**THAT 1200-Series Doc 600033 Rev 01, Table 1, SO Pin column**):

| SOIC-8 Pin | Datasheet (`THAT1200`, SO8) | Carrier PCB `U2` Net | Status |
| :---: | :--- | :--- | :--- |
| **1** | `Ref` | `gnd` | OK |
| **2** | `In-` | `in_minus` | OK |
| **3** | `In+` | `in_plus` | OK |
| **4** | `Vee` (`-16 V`) | `v_minus` (`-16 V`) | OK |
| **5** | `CM In` | `sm` (`C14.2`) | OK *(connects to one side of `C14`)* |
| **6** | `Vout` | `cm` (`C14.1`) | **WRONG (`Vout` drives only bootstrap cap `C14`, disconnected from `R3`)** |
| **7** | `Vcc` (`+16 V`) | `audio_out` (`R3.1` to `U3`) | **WRONG (`Vcc` receives no `+16 V` power)** |
| **8** | `CM Out` | `v_plus` (`+16 V`) | **WRONG (`+16 V` rail directly into `CM Out`)** |

**Consequence:** `THAT1200S08-U` receives no `+16 V` supply, feeds `+16 V` directly into `CM Out`, cannot pass audio to `TL072`, and risks immediate damage on power-up if soldered directly onto `U2`.

---

### 1.3 `C3` and `C27` (`220 µF / 25 V` Electrolytics, LCSC `C4747974`) — Reverse-Polarized on `-16 V`

Both `C3` (rear `-16 V` bulk capacitor) and `C27` (local `-16 V` bulk capacitor near `U3`) use `Capacitor_SMD:CP_Elec_6.3x5.4`, where:
- **Pad 1 (`-2.8, 0`) = Anode (`+`)**, marked on `F.SilkS` with a `+` cross at `(-4.04, -1.85)` and chamfered base corner.
- **Pad 2 (`+2.8, 0`) = Cathode (`-`)**.

On `icio500.kicad_pcb`, **both `C3` and `C27`** are wired **Pad 1 (`+`) → `v_minus` (`-16 V`)** and **Pad 2 (`-`) → `gnd` (`0 V`)**.

Because `GND` (`0 V`) is **`+16 V` more positive** than `v_minus` (`-16 V`), an electrolytic filter capacitor on a negative supply rail **must** have its `+` terminal tied to `GND` and its `-` terminal tied to `v_minus`.

**Consequence:** As wired, `C3` and `C27` see **16 V reverse bias** across a `220 µF` aluminum electrolytic — leading to heavy leakage current, overheating, `-16 V` rail collapse, and capacitor venting/rupture.

*(Note: `C1` on `v_plus`, `C25` on `daisy_5v_power`, and `C26` on `v_plus` are positive-rail bulk caps with Pad 1 `+` on the positive rail and Pad 2 `-` on `gnd` — those three have correct net polarity.)*

---

## 2. Severe Audio & Circuit Defects

### 2.1 `D11` (`BAT54S` Clamp, LCSC `C2145`) Hard-Clips All Negative Audio at `-0.3 V`

On [icio500.kicad_pcb](../../../kicad/icio500.kicad_pcb), `U3A` (`TL072CDT` on `±16 V`) outputs a **`0 V`-centered bipolar audio signal** (`tl072_out1_raw`) through `R11` (`1 kΩ`) onto `daisy_audio_in` (`U5.16`, Daisy Seed `Audio In 1`).

`D11` (`BAT54S` dual series Schottky in `SOT-23`) is wired directly onto `daisy_audio_in`:
- `D11.1` (Anode 1) → `gnd` (`0 V`)
- `D11.2` (Cathode 2) → `+3.3V`
- `D11.3` (Common `C1/A2`) → `daisy_audio_in`

Because the Electro-Smith Daisy Seed's audio inputs are **already AC-coupled onboard** and accept a **`0 V`-centered bipolar line-level waveform** (`~1.0 Vrms` / `~2.8–3.0 Vpp` nominal full scale), clamping `daisy_audio_in` at `gnd - Vf_schottky` (`≈ -0.3 V`) slices off the entire negative half-cycle whenever `daisy_audio_in` drops below `-0.3 V` (roughly `-4.4 dBu` at the module input with the `0.455×` input stage).

- **Rev-1 bench fix:** Desolder/depopulate `D11` before audio testing.
- **Rev-2 fix:** Replace `D11` with a symmetric bipolar clamp centered on `0 V` (e.g., antiparallel stacked silicon diodes to `GND`, clamping around `±2.1 V` above codec full-scale) or bias/clamp ahead of DC blocking.

---

### 2.2 `C12` and `C13` (`10 µF 0603` X5R, LCSC `C19702`) — Under-Rated (`10 V`) and Non-Linear Dielectric

In [carrier_bom.csv](carrier_bom.csv#L6), `C12` and `C13` (plus `C14` and `C5`) use LCSC **`C19702`** (Samsung `CL10A106KP8NNNC`): **`10 µF, 10 V, X5R, 0603`**.

On `icio500.kicad_pcb`, `C12` (`receiver.r_rf_plus-vcc` → `in_plus`) and `C13` (`receiver.r_rf_minus-vcc` → `in_minus`) sit in series with the balanced input **upstream** of the input clamp diodes (`D3`–`D6`):
- Hot pro line signals (`+24 dBu` ≈ `±17.3 Vpk`) and especially accidental **`+48 V` phantom power** (`J1.15`) apply up to **`48 V DC`** across `C12` and `C13` — nearly **5× their `10 V` rating**, risking dielectric breakdown / short-circuit failure.
- Additionally, `0603` X5R ceramic MLCCs exhibit strong voltage-coefficient capacitance modulation and piezoelectric microphonics in the main audio path, degrading THD+N.

*(Note: `C5` is on the `5 V` rail so `10 V` is marginal but survivable as decoupling; `C12`/`C13` should be upgraded in Rev-2 to `≥ 50 V–63 V` non-polarized audio electrolytics or film caps, and `C14` to a non-microphonic `25 V+` cap if keeping `THAT1200`.)*

---

### 2.3 Gain Staging, Codec Headroom & `180°` Phase Inversion (`U3` + `U4`)

Tracing the assembled resistor values from [carrier_bom.csv](carrier_bom.csv) and `icio500.kicad_pcb`:

1. **Input receiver (`U2`, `THAT1200`):** `0 dB` (`1.0×`).
2. **ADC scaling (`U3A`, `TL072` inverting):** `R3 = 22 kΩ`, `R4 = 10 kΩ`, `C17 = 47 pF`:
   $$\text{Gain}_{U3A} = -\frac{R4}{R3} = -\frac{10\text{ k}\Omega}{22\text{ k}\Omega} = -0.4545 \quad (-6.85\text{ dB},\; 180^\circ\text{ inverted})$$
   - **Headroom issue:** At standard 500-series `+20 dBu` (`7.75 Vrms` / `10.96 Vpk`), `U3A` outputs `3.52 Vrms` / `4.98 Vpk` (`9.96 Vpp`). The Daisy Seed audio codec clips around `~1.0 Vrms` (`~2.8–3.0 Vpp`), so `+20 dBu` hits Daisy Seed at **~3.5× full-scale** (codec clips around `+9 dBu` at module input). For `~+20 dBu = 0 dBFS` headroom, `U3A` needs roughly **`-15` to `-18 dB`** (`~0.13×–0.18×`).
3. **DAC output scaling (`U3B`, `TL072` non-inverting):** `R7 = 10 kΩ` + `R8 = 22 kΩ` divider (`0.6875×`), followed by `R5 = 10 kΩ` + `R6 = 22 kΩ` non-inverting gain (`1 + 22/10 = 3.20×`):
   $$\text{Gain}_{U3B} = 0.6875 \times 3.20 = +2.20 \quad (+6.85\text{ dB})$$
4. **Line driver (`U4`, `THAT1646`):** `+6.02 dB` (`2.0×`) differential output.

**Net module loop (DSP at unity `1.0`):** `(-0.4545) × (+2.20) × (+2.0) = -2.0` → **`+6.0 dB` net analog boost** and **`180°` phase inversion** unless compensated in Daisy firmware (`output = -0.5 × processed`). *(Also verify whether the `2×` analog output scale causes `~1 Vrms` DAC full-scale from Daisy Seed to land below standard `+20 dBu` / `+22 dBu` 500-series peak output, since `1.0 Vrms × 2.20 × 2.0 = 4.4 Vrms ≈ +15.1 dBu`.)*

---

## 3. Minor Issues, BOM Caveats & Assembly Traps

### 3.1 `U5` (`Daisy Seed`) `3V3_A` (Pin 21) and `3V3_D` (Pin 38) Shorted Together
- On `icio500.kicad_pcb`, `U5.21` (`3V3 Analog`), `U5.38` (`3V3 Digital`), `D11.2`, and `U6.20` (satellite board `3.3 V` supply for OLED/LEDs) are all tied to the same net (`+3.3V`).
- This shorts the Daisy Seed's isolated analog codec `3.3 V` output (`Pin 21`) directly to the digital `3.3 V` rail (`Pin 38`) and feeds faceplate I2C / LED PWM transients straight back into the analog codec supply.
- **Rev-2 fix:** Leave `U5.21` isolated (or decoupled locally to `AGND`), and power `U6.20` exclusively from `U5.38` (`3V3_D`).

### 3.2 Misleading Net Name `d14` on `U5.22` (`J_ENC.5` / `ENC_A`)
- `J_ENC.5` (`ENC_A`) routes to **Physical Pin 22 (`U5.22`)** on the Daisy Seed DIP-40 footprint, even though the KiCad net is named **`d14`**.
- On the Electro-Smith Daisy Seed, **Physical Pin 22 is `D15 / A0`** (`PC0`), **not** `D14` (`D14` is Physical Pin 15).
- Also note **Physical Pin 24 (`D17 / A2`, `ENC_SW`) is 3.3 V tolerant only** (not 5 V tolerant) — safe here since the encoder only switches to `GND`, using the internal pull-up.
- **Verified Daisy Seed (`U5`) firmware mapping for this board:**

| Carrier Pin | Net Name on PCB | Daisy Seed Signal | Notes |
| :--- | :--- | :--- | :--- |
| `U5.12` | `i2c1_scl` | **`D11` / `I2C1_SCL`** | To `U6.15` (Faceplate OLED & LED driver) |
| `U5.13` | `i2c1_sda` | **`D12` / `I2C1_SDA`** | To `U6.17` |
| `U5.16` | `daisy_audio_in` | **`Audio In 1`** | Left / Mono ADC in (`D11` clamp bug on this net) |
| `U5.17` | `gnd` | **`Audio In 2`** | Tied to `GND` (unused right input) |
| `U5.18` | `audio_in_from_daisy_plus` | **`Audio Out 1`** | Left / Mono DAC out |
| `U5.20`, `U5.40` | `gnd` | **`AGND`, `DGND`** | Ground reference |
| `U5.21`, `U5.38` | `+3.3V` | **`3V3_A`, `3V3_D`** | Shorted together on Rev-1 |
| **`U5.22`** | **`d14` *(misnamed)*** | **`D15` (`A0`)** | **Use `D15` in libDaisy for `ENC_A`** |
| `U5.23` | `gpio_enc_b` | **`D16` (`A1`)** | Use `D16` in libDaisy for `ENC_B` |
| `U5.24` | `gpio_enc_sw` | **`D17` (`A2`)** | Use `D17` in libDaisy for `ENC_SW` |
| `U5.39` | `daisy_5v_power` | **`VIN` (`+5V`)** | Fed by `U1` (`TSR 1-2450`) |

### 3.3 `U5` Socket Choice (`C2332` `IC-40P`)
- LCSC `C2332` is a stamped-contact DIP-40 IC socket intended for flat `~0.25 × 0.45 mm` IC leadframes, not the Daisy Seed's `0.64 mm` (`0.025"`) square header pins.
- **Rev-1 impact:** Inserting a Daisy Seed can require high force and deform the stamped spring contacts (risking intermittent pin contact if plugged/unplugged repeatedly). Be careful seated-once or replace with two `1×20` `2.54 mm` female box headers (`Rev-2`).

### 3.4 Electrolytic Package / Footprint Dimension Mismatches
- **`C21`, `C22` (`C1984751`, Nichicon `UUP1E100MCL1GS`, `10 µF 25 V` bipolar):** Actual Nichicon package is **`Ø6.3 × 5.8 mm`**, placed on a `Capacitor_SMD:CP_Elec_5x5.4` footprint (`±2.2 mm` pad centers). It can usually sit across the pads for manual touch-up, but JLCPCB PnP / reflow fillet extension is tight.
- **`C1`, `C3`, `C25`, `C26`, `C27` (`C4747974`, KNSCHA `RST220UF25V019`):** Actual part is **`Ø6.3 × 7.7 mm`** on a `CP_Elec_6.3x5.4` footprint (pads match `Ø6.3 mm`, body is `2.3 mm` taller than the KiCad 3D model, still well within the 500-series `38.1 mm` slot width).

### 3.5 JLCPCB Pick-and-Place Rotation Check (`carrier_cpl.csv`)
- [carrier_cpl.csv](carrier_cpl.csv) uses KiCad's raw footprint angles without per-part JLC rotation offsets. Always visually inspect **Pin 1 / cathode / `+` orientation** on `D1`–`D11`, `C1`/`C25`/`C26` (plus rotated `C3`/`C27`), `U1`, `U3`, `J_ENC`, and `U6` on arrival against JLC's DFM preview and real part markings before applying power.

### 3.6 VPR-500 `+16 V` Current Budget Watch Item
- Per [api_vpr_500_spec.pdf](../../../docs/api_vpr_500_spec.pdf), each 500-series slot is specified for **`130 mA` max on `+16 V`** and **`130 mA` max on `-16 V`**.
- `U1` (`TSR 1-2450`) draws the entire Daisy Seed (`+5 V`) and faceplate OLED/LED (`+3.3 V`) load from **`+16 V` (`v_plus`)** alongside the `+16 V` analog stage (`U2`, `U3`, `U4`). Because switching down `16 V → 5 V` saves some current compared to a linear regulator, measure total `+16 V` rail draw on a bench supply at full LED brightness and verify margin below `130 mA`.

---

## 4. What Is Verified Good on Rev-1

- **Mechanical envelope & 500-series geometry:** `114.30 × 148.83 mm` (`4.500" × 5.859"` PCB + `3.20 mm` faceplate = `5.985"` total, within slot depth), `1.6 mm` 4-layer stackup (`F.Cu`, `In1.Cu GND`, `In2.Cu`, `B.Cu`), chamfered EDAC 306 edge fingers.
- **Electrical DRC & connectivity:** `0` unconnected items and `0` electrical/clearance DRC errors (`61` total DRC warnings are only KiCad library-mismatch and silkscreen-clip warnings).
- **`J1` VPR-500 edge connector pinout:** Verified Pin 1 (`CHASSIS_GND`) at top (`Y = 75.14 mm`) to Pin 15 (`+48V`) at bottom (`Y = 130.58 mm`), dual-sided `F.Cu`/`B.Cu` exposed pads with mask openings.
- **`U1` (`TSR 1-2450`) pinout:** `1 = +16 V (v_plus)`, `2 = GND`, `3 = +5 V (daisy_5v_power)`.
- **`U3` (`TL072CDT`) pinout:** Correct (`1: Out1, 2: In1-, 3: In1+, 4: Vee, 5: In2+, 6: In2-, 7: Out2, 8: Vcc`).
- **`D1`/`D2` (`SS14`) and `D3`–`D10` (`1N4148W`) PCB net polarity:** Pad 1 (cathode bar on silkscreen) and Pad 2 (anode) match reverse-polarity protection (`D1`/`D2`) and clamp polarity (`D3`–`D10`).
- **Interconnect alignment:** `U6` ↔ Satellite `J1` (`20/20` nets aligned) and `J_ENC` ↔ Encoder `P1` (`5/5` nets aligned).
- **Daisy Seed USB access:** Pin 1 at `(95, 90)` puts the Daisy Seed micro-USB/USB-C port facing the **top edge** (`Y = 45.7 mm`) with `~44 mm` clearance.

---

## 5. Bench Bring-Up Checklist (Testing Existing Rev-1 Boards Safely)

If JLCPCB ships the Rev-1 carrier boards unpopulated at `U2`/`U4`, you can still safely bring up power, Daisy Seed, firmware, encoder, OLED, and faceplate LEDs by following this order:

1. **Leave `U2` and `U4` empty.** Do not solder THAT chips onto the Rev-1 `U2`/`U4` pads.
2. **Fix `C3` and `C27` before any power:** Desolder `C3` and `C27`, rotate each **180°**, and resolder so the `+` chamfered end connects to `GND` and the `-` end connects to `v_minus` (`-16 V`). *(Optionally remove `C21`/`C22` if not needed while `U4` is unpopulated.)*
3. **Visually inspect assembled parts:** Confirm diode cathode bars (`D1`–`D10`), `C1`/`C25`/`C26` `+` ends, `U3` Pin 1 dot, and `U1` Pin 1 orientation.
4. **Remove `D11` (`BAT54S`)** before feeding bipolar audio into `U5.16`.
5. **First power-up on a current-limited bench PSU (`±16 V`, `150 mA` limit)** — never plug straight into a 500-series rack first:
   - Check `v_plus` (`≈ +15.6 V` after `D1`), `v_minus` (`≈ -15.6 V` after `D2`), `daisy_5v_power` (`+5.0 V` at `U1.3`), and `+3.3V` (`U5.38` with Daisy Seed seated).
6. **Digital/UI bring-up works natively on Rev-1:** Flash firmware using **`D15` for `ENC_A`** (`d14` net), `D16` for `ENC_B`, `D17` for `ENC_SW`, and `I2C1` (`D11`/`D12`) for the satellite faceplate OLED + `IS31FL3216A` LEDs. *(Analog audio I/O on Rev-1 would require ugly dead-bug breakout adapters for `U2`/`U4` + removing `D11`; cleaner to fix `U2`/`U4`/`C3`/`C27`/`D11`/`C12`/`C13`/`3V3` in a Rev-2 carrier spin.)*

---

## 6. Supply-Chain Note on `THAT1200S08-U` & `THAT1646S08-U`

THAT Corporation closed its internal 4-inch dielectric-isolation wafer fabrication facility and placed both the **`THAT 1200`** InGenius series and **`THAT 1606/1646`** OutSmarts series (along with 124x/128x/129x receivers, 2180/2181 VCAs, and 1510/1512 preamps) into **End-of-Life (EOL)**, with the official Last-Time Buy window closing **September 30, 2026**.

- **`THAT1200S08-U` (`C3202799`):** Still shows ~490 pcs remaining shelf stock at Mouser (`887-1200S08-U`, EOL/NCNR), out of stock at DigiKey/Newark/LCSC.
- **`THAT1646S08-U` (`C5290156`):** Out of shelf stock at Mouser, DigiKey, Newark, Farnell, and LCSC (only long-dated 2027 backorders or secondary/surplus brokers); Mouser still lists limited shelf stock in the wide `SOIC-16` (`1646W16-U`) package and synth DIY shops carry some `DIP-8` (`1646P08-U`) stock.

This fab shutdown is why JLCPCB/LCSC could not source `C3202799` or `C5290156`.
