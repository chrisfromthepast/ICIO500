# Subcircuit Verification Playbook (`ICIO500 / october_surprise` Methodology)

> Reusable operator handbook for designing, simulating, fault-hardening, and locking analog/mixed-signal audio hardware **one subcircuit at a time** before moving to the next block or tapeout.

---

## 1. Operator Workflow (6-Step Subcircuit-Lock Method)

Every subcircuit is evaluated, hardened, simulated in isolation, and locked on silkscreen before touching the next block:

1. **Schematic-First Isolation & ERC (`kicad-cli sch erc --severity-all`):**
   - Author and edit the subcircuit strictly in the schematic (`kicad/october_surprise.kicad_sch` via `scripts/build_october_surprise_sch.py`). Never back-annotate or patch nets directly in `.kicad_pcb`.
   - Require **`0` ERC errors and `0` warnings** before any simulation or forward annotation.
2. **Untouched Netlist Export (`kicad-cli sch export netlist --format spice`):**
   - Export the real schematic netlist directly via `kicad-cli` (no hand-transcribed copies).
   - Attach only external bench supplies, loads, and fault stimuli in Python around the untouched netlist body.
3. **Isolated Subcircuit `ngspice` Suite + 4-Panel Verification Chart:**
   - Run the block-specific simulation suite (`sim_power_subcircuit.py`, `sim_input_subcircuit.py`, `sim_output_subcircuit.py`) covering `.op` + capacitor derating, `.ac` transfer/peaking, `.noise` (`20 Hz–20 kHz`), `.tran` linearity/stress loads, and `+48 V` phantom fault survivability.
   - Render and visually inspect the dark-mode 4-panel PNG under `docs/` (`subcircuit1_power_spice.png`, `subcircuit2_input_spice.png`, `subcircuit3_output_spice.png`).
4. **Live BOM, Derating, Socket & Package Gate:**
   - Verify live distributor stock (LCSC), active lifecycle, dielectric class (`C0G/NP0` and film in signal/compensation paths; no under-rated small-case `X5R`/`Y5V`), `>= 2×` voltage derating against both steady rails and `+48 V` faults, and machined `DIP-8` socket fit on exposed analog silicon (`U2`, `U7`).
5. **`F.SilkS` Zone Lock & KiCad PCB DRC:**
   - Forward-annotate / sync via `build_october_surprise_pcb_template.py` / `F8`, lock the subcircuit inside its own non-overlapping `F.SilkS` box + label clear of `J_DAISY_R1` (`x > 117.79 mm`) and `J1` (`x < 177.62 mm`), and run `kicad-cli pcb drc --severity-all` (`0` footprint errors, `0` unconnected pads).
6. **Full-Board Integration Regression (`scripts/sim_october_surprise.py`):**
   - Re-run the full signal-chain regression (`IN_P/N` -> `DAISY_AUDIO_IN` -> `DAISY_AUDIO_OUT` -> `OUT_P/N`) after every subcircuit lock to verify end-to-end gain, phase, headroom, and stability.

---

## 2. Complete Case-by-Case Test Enumeration

### Subcircuit #1: `POWER` (`scripts/sim_power_subcircuit.py`)
*Silkscreen Lock:* `(140, 122) -> (176, 157)` | *Chart:* [subcircuit1_power_spice.png](file:///c:/Users/Chris%20Williams/Documents/GitHub/ICIO500/docs/subcircuit1_power_spice.png)

| Case ID | Analysis & Stimulus | Pass Criteria | Verified Result (`october_surprise`) |
| :--- | :--- | :--- | :--- |
| **Test 1** | **Loaded `.op` & Cap Audit:** `+16V_RAW = +16.0 V`, `-16V_RAW = -16.0 V`, `+5V` load `150 mA`, `±16V` loads `40 mA` each | All `15` `POWER` caps pass signed polarity `V(Pad 1) - V(Pad 2) > 0` (for polarized caps `C1..C5, C36`) and `>= 2.0×` voltage rating | `+16V = +15.689 V`, `-16V = -15.689 V`, `+5V = +4.915 V`; all `15` caps pass (`>= 2.2×`) |
| **Test 2** | **`.ac` Rack Noise Rejection & LC Q-Damping:** `10 Hz – 10 MHz` AC sweep from `±16V_RAW` to `±16V` & `+5V` | LC resonance peaking `< +3.0 dB` (well-damped), strong HF attenuation at buck/rack frequencies | `0.00 dB` max LC peaking; `-106.9 dB @ 100 kHz`, `-178.3 dB @ 500 kHz` |
| **Test 3A** | **Buck Reflected Input Ripple:** `150 mAp-p @ 500 kHz` current injection at `+16V_BUCK` (`TSR 1-2450` switching noise) | Minimal ripple back-propagating onto clean analog `+16V` rail | `+16V` ripple `0.861 µVp-p` (`47.7 dB` isolation) |
| **Test 3B** | **Buck `+5V` Output Pi-Filter Attenuation:** `500 kHz` ripple driven at `+5V_BUCK` measured at `+5V` | Strong switching ripple attenuation across `L2` / filter stage | `31.1 dB` attenuation `@ 500 kHz` |
| **Test 4** | **`600 mA / 100 µs` Rail Surge Clamp:** `PULSE(0 -> 0.6 A, 10 us delay, 100 us width)` onto `+16V_BUS` / `-16V_BUS` | `D19/D20` (`SMBJ18CA`) clamp `±16V_BUS` safely `< 30 V` (below `35 V` cap rating) | Clamped at `+15.876 V` / `-15.913 V` |

---

### Subcircuit #2: `BALANCED INPUT` (`scripts/sim_input_subcircuit.py`)
*Silkscreen Lock:* `(124, 94) -> (176, 118)` | *Chart:* [subcircuit2_input_spice.png](file:///c:/Users/Chris%20Williams/Documents/GitHub/ICIO500/docs/subcircuit2_input_spice.png)

| Case ID | Analysis & Stimulus | Pass Criteria | Verified Result (`october_surprise`) |
| :--- | :--- | :--- | :--- |
| **Test 1** | **`.op` & `+48 V` Input Cap Derating:** `±16 V` rails active, `13.6 kΩ` `DAISY_AUDIO_IN` load | All `11` Zone 2 caps (`C10..C20`) `>= 2.0×` over worst-case `+48 V` / `±11 V` fault | `C10..C13` (`100 V` vs `48 V`) `2.1×`, `C14` (`100 V` vs `11 V`) `9.1×` — all **PASS** |
| **Test 2** | **`.ac` Diff Gain & CMRR:** `20 Hz – 10 MHz` diff sweep + `20 Hz – 20 kHz` common-mode sweep | Nominal `-16.48 dB` (`±0.3 dB`) flat gain; clean common-mode rejection (`0.1%` resistors) | `-16.55 dB`, `0.027 dB` flatness (`20 Hz–20 kHz`); `~60–66 dB` worst-case `0.1%` CMRR |
| **Test 3** | **`.tran` Linearity & `20 Hz–20 kHz` Noise:** `1 kHz` at `+4, +18.7, +20, +24 dBu` + dedicated `.noise` pass | Clean linearity up to `+20 dBu`, soft clamp at `+24 dBu`, ADC safe `<< ±3.3 V` | `7.96 µVrms` (`-99.8 dBu`) input-referred noise; **`118.5 dB` DR** rel. `+18.7 dBu` |
| **Case 4A** | **Phantom Hot-Plug & Cap Discharge (IEC 61938):** `+48 V` via `6.81 kΩ` applied to `IN_P` at `0.5 ms`, slammed to `0 V` at `10 ms` (`12 ms` run) | `BAV21W` (`D3..D6`) clips clamp node to `±16 V`, `\|I_in(U2)\| < 10.0 mA`, `\|DAISY_AUDIO_IN\| < 3.0 V` | `max\|I_in(U2)\| = 2.26 mA << 10 mA`; `DAISY_AUDIO_IN` within `[-2.270, +1.995 V]` |
| **Case 4B** | **Worst-Case Low-Z `+48 V` Slam (`10 Ω`):** Direct `+48 V` via `10 Ω` to `IN_P` at `0.5 ms`, slammed to `0 V` at `4.0 ms` (`6 ms` run) | `R1` (`100 Ω 1206`) & `BAV21W` (`1 s I_FSM = 1000 mA`) survive pulse, `\|I_in(U2)\| < 10.0 mA`, `\|DAISY_AUDIO_IN\| < 3.0 V` | `max\|I_in(U2)\| = 2.76 mA << 10 mA`; `DAISY_AUDIO_IN` within `[-2.270, +1.995 V]` |

---

### Subcircuit #3: `OUTPUT / CCOS` / `LINE DRIVER` (`scripts/sim_output_subcircuit.py`)
*Silkscreen Lock:* `(124, 54) -> (176, 90)` | *Chart:* [subcircuit3_output_spice.png](file:///c:/Users/Chris%20Williams/Documents/GitHub/ICIO500/docs/subcircuit3_output_spice.png)

| Case ID | Analysis & Stimulus | Pass Criteria | Verified Result (`october_surprise`) |
| :--- | :--- | :--- | :--- |
| **Test 1** | **`.op` & Back-Feed Cap Derating:** `1.0 Vrms` DAC model (`100 Ω` Zout), `10 kΩ` output load | All `10` Zone 4 caps (`C21, C22, C24..C29, C39, C40`) pass `>= 2.0×` derating (`48 V` at `OUT_P/N`) | `+16V = +15.7334 V`, `-16V = -15.7349 V`; `C39/C40` `2.1×`, bypass `3.2×`, comp `50.0×` |
| **Test 2** | **`.ac` Gain (`10 Hz–10 MHz`) & `10 nF` Cable Stability:** Diff sweep with `1 pF` nominal & `10 nF` capacitive cable load | Flat audio passband (`~+16.47 dB`), `10 nF` capacitive load peaking `< +3.0 dB` | `+16.468 / +16.467 / +16.435 dB` (`20 Hz–20 kHz`); `10 nF` peaking `+0.00 dB` |
| **Test 3** | **`.tran` Drive, CCOS Short, `10 nF` & `.noise`:** `+18.7 / +20 dBu` into `10 kΩ`, `600 Ω`, `OUT_N -> GND (1 Ω)`, `10 nF`, plus `20 Hz–20 kHz` `.noise` | Floating CCOS preserves differential level within `0.15 dB` on single-leg ground short; zero ringing on `10 nF` | `10 kΩ +20 dBu`: `7.724 Vrms`; `600 Ω`: `7.169 Vrms` (`16.9 mA` pk); `OUT_N->GND`: `-0.032 dB`; `10 nF`: `-0.000 dB`; Noise: `9.00 µVrms` (`-98.7 dBu`, **`117.4 dB` DR**) |
| **Case 4A** | **Output Back-Feed Phantom (`IEC 61938 +48 V / 6.81 kΩ` Both Legs):** Output accidentally patched into a live phantom-powered balanced preamp (`5 ms`) | `BAV21W` clamps `OUT_P/N` cleanly; `+16V < 25 V`; `R19/R25` (`49.9 Ω 1206 250 mW`) stay well within steady thermal rating | `OUT_P/N = [+0.07, +15.83 V]`; `+16V max = +15.73 V`; `R19` max `2.4 mA` / **`0.3 mW << 250 mW`** |
| **Case 4B** | **Miswired Unbalanced Back-Feed (`IEC +48 V / 6.81 kΩ OUT_P` + `OUT_N -> GND`):** Output patched to live phantom hot leg while cold leg shorts to ground (`5 ms`) | CCOS holds output low / protects stage; `+16V < 25 V`; `R19/R25 < 250 mW` | `OUT_P = [+0.00, +0.36 V]`; `+16V max = +15.73 V`; `R19` max `6.9 mA` / **`2.4 mW << 250 mW`** |
| **Case 4C** | **Stiff Transient Back-Feed Surge (`7× IEC +48 V / 1 kΩ` `2 ms` Surge → `0 V`):** Non-standard `1 kΩ` stiff `+48 V` fault (`6.8×` stiffer than IEC `6.81 kΩ`) pulsing `0.5 ms -> 2.5 ms -> 0 V` (`5 ms` run) | `BAV21W` + `R19/R25` survive pulse and recover cleanly to `0 V` bias without latch-up; `+16V < 25 V`; `R19 < 250 mW` | `OUT_P = [+0.03, +16.47 V]`, `OUT_N = [+0.03, +15.51 V]`; `+16V max = +15.74 V`; `R19` max `19.2 mA` / **`18.3 mW << 250 mW`** |

> [!NOTE]
> **Why Case 4C uses `1 kΩ` (and what a `100 Ω` dead fault taught us):** An earlier `100 Ω` `+48 V` dead-short run (`0.48 A` source limit — far beyond phantom power) pushed `U7` into `99.6 mA` short-circuit current and `495.3 mW` pulse power in `R19` (exceeding its `250 mW` continuous rating) while hitting piecewise discontinuities inside TI's `OPA1656.LIB` clamp tables (`VCC_CLP`/`CLAW_CLAMP`). That extreme test directly validated specifying **`200 V / 250 mW 1206`** build-out resistors (`R19/R25`) and a **machined `DIP-8` socket** on `U7`. For transient back-feed simulation up to `7×` IEC phantom (`1 kΩ`), setting `.options reltol=0.005 trtol=7 method=gear maxord=1 itl4=200` with a `1 µs` step avoids the `0.519 ms` Gear-order/timestep stall at the clamping knee.

---

### Full-Board End-to-End Regression (`scripts/sim_october_surprise.py`)
*Chart:* [october_surprise_spice_verification.png](file:///c:/Users/Chris%20Williams/Documents/GitHub/ICIO500/docs/october_surprise_spice_verification.png)

| Case ID | Analysis & Stimulus | Verified Full-Chain Result (`IN_P/N` -> `OUT_P/N`) |
| :--- | :--- | :--- |
| **Test A** | **`.op` & `26`-Cap Polarity/Derating Audit** | `+16V = +15.73342 V`, `-16V = -15.73491 V`, `+5V = +5.00000 V`, `OUT_P = +0.13605 V`, `OUT_N = +0.12994 V`; all `26` caps **PASS** (`>= 2.1×`) |
| **Test B** | **`.tran` Gain, Phase & Headroom (`10 kΩ Bal`, `1 kHz`)** | `+4 dBu`: `-0.083 dB` (`0.38°`); `+18.7 dBu`: `-0.085 dB` (`0.35°`, `DAISY_IN = 0.991 Vrms`); `+20 dBu`: `-0.089 dB` (`0.35°`); `+24 dBu`: `-0.352 dB` (`11.779 Vrms` soft-clamp) |
| **Tests C / D / E** | **`600 Ω` (`+20 dBu`), `OUT_N->GND` Short (`+18.7`), `10 nF` (`+18.7`)** | `600 Ω`: `7.110 Vrms` (`-0.737 dB`, `16.8 mA` pk); `OUT_N->GND`: `6.573 Vrms` (`Delta = -0.032 dB`); `10 nF`: `6.598 Vrms` (`-0.085 dB`, zero ringing) |
| **Test F** | **`.ac` Frequency Response (`10 Hz – 1 MHz`)** | `20 Hz`: `-0.110 dB` \| `1 kHz`: `-0.083 dB` \| `19.95 kHz`: `-0.123 dB` \| `100 kHz`: `-1.057 dB` |

### Subcircuit #4: `DIGITAL / DAISY` *(Reserved — Next Block)*
- Pending user approval to lock Subcircuit #3 (`OUTPUT / CCOS`) and begin Subcircuit #4 (`3V3_A`/`3V3_D` separation, `J_DAISY_L1`/`J_DAISY_R1` physical pin verification, encoder `J_ENC1`, `J_OLED`/`U6`, and `F.SilkS` box).

---

## 3. Reusable `ngspice` Operator Checklist & Known Gotchas

When adapting this verification flow to future KiCad audio hardware:
- **Reuse one `NgSpiceSession` per Python process:** Embedded `ngspice.dll` holds global circuit state; call `destroy all` followed by `remcirc` before loading a second bench deck in the same script.
- **Normalize `.include` paths on Windows:** Pass `.lib`/`.cir` paths through `GetShortPathNameW` (8.3 short paths) and push `cwd` to `kicad/spice_models` during `ngSpice_Circ` so nested `.include "OPA1656.LIB"` statements resolve reliably even when folder paths contain spaces.
- **TI macro `.noise` (`R_NOISELESS` / `T_ABS=-273.15`) workaround:** `ngspice` ignores PSpice `T_ABS=-273.15` inside TI op-amp subcircuits and evaluates internal `MΩ` behavioral resistors at `27 °C`. Always run `.noise` in a fresh deck (`noise ... dec 50 20 20k 1`, `setplot noise1`), integrate only external schematic resistor contributions (`onoise_r*`), and RSS with the datasheet broadband input noise density (`2.9 nV/√Hz` per `OPA1656` weighted by stage noise gain).
- **Steep fault-edge convergence (Case 4C):** High-voltage switching knees into behavioral op-amp clamps (`OPA1656.LIB`) benefit from `.options reltol=0.005 trtol=7 method=gear maxord=1 itl4=200` and a `1 µs` transient step (`tran 1u ... 0`), alongside an explicit `assert float(t[-1]) >= t_end * 0.99` so an early solver abort can never silently pass.
- **Never skip real-world derating checks in code:** Ideal SPICE `C` models do not simulate overvoltage or reverse polarity — always parse every `C*` line directly from the exported `.cir`, apply signed `V(Pad 1) - V(Pad 2) > 0` for polarized parts, and enforce `Rating / Worst_Case_Voltage >= 2.0` against `+48 V` fault conditions.
