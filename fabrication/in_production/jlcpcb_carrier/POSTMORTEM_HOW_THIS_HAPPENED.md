# Post-Mortem: How the Hell Did This Happen to the Rev-1 Carrier Board?

If you open [carrier_rev1_rework_visual_guide.png](carrier_rev1_rework_visual_guide.png) or [CARRIER_BOARD_ISSUES_GUIDE.md](CARRIER_BOARD_ISSUES_GUIDE.md), the obvious question isn't just *"how do we dead-bug this on the bench?"* It's: **how does a board go through five months of work, ~60 commits, "0 DRC errors," an exported schematic PDF, and JLCPCB DFM submission with 7 of 8 pins wrong on `U4`, 3 pins shifted on `U2`, both `-16 V` electrolytics soldered backwards, a Schottky diode clipping half the audio wave off, `10 V` ceramics on a `±16 V` / `+48 V` balanced input, and two End-of-Life chips?**

This isn't one bug. The git history of this repo tells the exact story of how it actually happened — and exposes a handful of traps that happen whenever LLMs, code-defined hardware, and KiCad automation interact without an independent human/datasheet firewall.

---

## Part I — How It Actually Happened (Forensic Timeline from Git History)

Every defect on the Rev-1 carrier board traces directly to specific commits in `git log`. Here is the exact chain of events:

### Act 1: Eight Minutes on Day 1 (`2026-06-04`) — Hallucinated Foundations
Everything fatal on the power and analog I/O side was written in an **8-minute burst** on June 4, 2026 when the original Atopile (`.ato`) modules were created:

1. **`522e0ce` (`14:40` EDT, `copilot-swe-agent[bot]` — `that1200_stage.ato`):**
   - When asked to create `That1200Stage`, the AI agent wrote `component That1200` ([that1200_stage.ato](../../../docs/legacy_atopile/elec/src/that1200_stage.ato#L5-L15)) from memory instead of opening THAT Corporation's `Doc 600033` PDF:
     - It knew classic 8-pin single op-amps have `V+` on Pin 8, `V-` on Pin 4, `IN-` on Pin 2, `IN+` on Pin 3 — so it pattern-matched `THAT1200` into `5: Sm, 6: Cm, 7: Out, 8: V_Plus`.
     - In reality, THAT1200 puts `5: CM In`, `6: Vout`, `7: Vcc`, `8: CM Out`. Because Pins 1–4 matched generic op-amps by luck, the mistake looked totally plausible at a glance.
   - It also specified `c_ac_plus` and `c_ac_minus` (`C12`, `C13`) simply as `value = 10uF` with zero voltage rating or dielectric constraint.

2. **`669d823` (`14:44` EDT — `that1600_stage.ato`):**
   - Four minutes later, `component That1646` ([that1600_stage.ato](../../../docs/legacy_atopile/elec/src/that1600_stage.ato#L5-L15)) was written as:
     `1: Out_Plus, 2: V_Minus, 3: Out_Minus, 4: GND, 5: In, 6: V_Plus, 7: Sense_Minus, 8: Sense_Plus`.
   - Almost every single pin was invented (only Pin 6 `V+` happened to match `Doc 600078 Rev 07`: `1: Out-, 2: Sns-, 3: Gnd, 4: In, 5: Vee, 6: Vcc, 7: Sns+, 8: Out+`).

3. **`b3ce656` (`14:45` EDT — `level_shifter.ato`):**
   - One minute later, `DaisyActiveScaling` ([level_shifter.ato](../../../docs/legacy_atopile/elec/src/level_shifter.ato#L44-L83)) set `U3A` (`R3 = 22k`, `R4 = 10k`, `-6.85 dB`) and designed `U3B` explicitly for a differential DAC (`# Half B: Output Gain Stage (True Differential Receiver)`, meant for `Seed2DFM` in [seed2dfm.ato](../../../docs/legacy_atopile/elec/src/seed2dfm.ato)).
   - Later that hour (`1278ea2` / `main.ato`), when targeting the standard single-ended Daisy Seed (`Pin 18`), `Audio_In_From_Daisy_Minus` was simply tied to `GND` ([main.ato](../../../docs/legacy_atopile/elec/src/main.ato#L109)). No one recalculated whether `-6.85 dB` actually protected a `~1.0 Vrms` (`~2.8 Vpp`) codec from `+20 dBu` (`7.75 Vrms`), or noticed the net `+6.0 dB` gain + `180°` phase inversion through `U4`.

4. **`5206470` (`14:46` EDT — `psu.ato`) & `main.ato`:**
   - One minute after that, [psu.ato](../../../docs/legacy_atopile/elec/src/psu.ato#L37-L50) imported `generics/capacitors.ato`, which only exposes **unpolarized** pins `.p1` and `.p2`.
   - For the `+16 V` rail, it wrote `V_Plus_Analog ~ c_bulk_p_elec.p1; c_bulk_p_elec.p2 ~ GND_Audio`. Then for `-16 V`, it copy-pasted the pattern: **`V_Minus_Analog ~ c_bulk_m_elec.p1; c_bulk_m_elec.p2 ~ GND_Audio`** (`C3`). [main.ato](../../../docs/legacy_atopile/elec/src/main.ato#L174-L178) repeated the exact same copy-paste for the local bulk cap (`C27`).
   - Because `.ato` had no polarity type on capacitors, attaching `CP_Elec_6.3x5.4` (where Pin `1` is always `+` and Pin `2` is always `-`) silently guaranteed `16 V` of reverse voltage across both `-16 V` electrolytics.

---

### Act 2: Five Months of Mechanical & Layout Tunnel Vision (`2026-06-05` → `2026-10-31`)
Over 50 commits (`084b62f` through `fc8b14d`) poured massive effort into routing the carrier board, rotating the Daisy Seed, battling KiCad's notorious GUI-vs-CLI 3D viewer offset bug (`0370ea3` → `05a0d51`), getting the VPR-500 card depth and EDAC notch right, mating `U6` to the faceplate `J1`, and eliminating copper DRC errors.

Every commit treated the right-hand analog section (`X > 140 mm` — `U2`, `U4`, `C3`, `C27`) as **"already solved hardware from June."** No commit ever opened a THAT Corp datasheet to check if the pads on `U2` and `U4` matched physical silicon.

---

### Act 3: Blind LCSC Mapping (`2026-11-02`, commits `5f900e2`, `2ea4ab4`)
In [make_jlcpcb_boms.py](../../../scripts/archive/make_jlcpcb_boms.py), LCSC `C`-numbers were assigned by generic value/package rather than circuit role:
- Every `10uF 0603` capacitor (`C5` on `5 V`, `C12`/`C13` on balanced audio inputs, `C14` on `THAT1200` bootstrap) was mapped to a single SKU: **`C19702`** (Samsung `CL10A106KP8NNNC`, **10 V, X5R**). Nobody checked that `C12`/`C13` sit upstream of the input clamps where `+24 dBu` peaks (`±17.4 V`) or `+48 V` phantom power can appear.
- `U5` (Daisy Seed) was mapped to `C2332` (`IC-40P`, a cheap stamped IC socket meant for thin IC pins, not `0.64 mm` square header pins).
- `C21`/`C22` (`CP_Elec_5x5.4` pads) were mapped to `C1984751` (`UUP1E100MCL1GS`, `Ø6.3 × 5.8 mm`).
- `U2` and `U4` were assigned `C3202799` (`1200S08-U`) and `C5290156` (`THAT1646S08-U`) without live stock or PCN/EOL checks — missing that THAT Corporation had shut down its 4-inch dielectric-isolation wafer fab and placed both families End-of-Life (Last-Time Buy ended Sept 30, 2026).
- `carrier_cpl.csv` manually overrode rotations only for `U1, U5, U6, J_ENC`, exporting raw KiCad angles for every SMD diode, capacitor, and op-amp.

---

### Act 4: The Inverted "Mathematically Verified" Blueprint Trap (`2026-11-11`, commit `9b88e05`)
This commit is the single most deceptive moment in the repo's history, and explains how the bugs acquired an ironclad veneer of legitimacy:

- **Generating the schematic *from* the broken PCB:** [generate_carrier_schematic.py](../../../scripts/archive/generate_carrier_schematic.py) — whose own docstring proudly calls it *"the production-grade, mathematically verified schematic blueprint"* — did **not** pull pins from official THAT Corporation symbols. Instead, its author hardcoded the exact wrong `that1200_stage.ato` / `that1600_stage.ato` pinouts into `SYM_PINS["THAT1200"]` (lines 98–107) and `SYM_PINS["THAT1646"]` (lines 108–117) so the new KiCad schematic would match the existing `.kicad_pcb` (`0` schematic parity errors!).
- **Adding `D11` (`BAT54S`):** To "protect the Daisy codec," [sync_pcb_blueprint.py](../../../scripts/archive/sync_pcb_blueprint.py) and `generate_carrier_schematic.py` added `R11 = 1k`, `C15 = 100pF`, and `D11 = BAT54S` (`Anode -> GND`, `Cathode -> +3.3V`) on `daisy_audio_in` (`U5.16`). Whoever added it treated `Audio_In_L` like a `0..3.3 V` unipolar STM32 ADC GPIO instead of an **AC-coupled bipolar audio input centered around `0 V`**, instantly adding a `-0.3 V` negative-half-wave clipper.
- **Shorting `3V3_A` to `3V3_D` and baking in `d14`:** `sync_pcb_blueprint.py` (lines 109–113) wired both `U5.21` (`3V3_A`) and `U5.38` (`3V3_D`) to `+3.3V`, and cemented the misnamed `d14` net on Physical Pin 22 (`D15 / A0`).
- **Stamping Pin 1 dots onto wrong pins:** `apply_prominent_pin1_silkscreen.py` added bold Pin 1 dots onto `U2` and `U4` (`Pad 1`), visually reinforcing the illusion that the footprints were vetted.
- **`verify_vpr_compliance.py` declared `100% CLEAN PASS`:** Because KiCad DRC only checks clearances and PCB-vs-netlist connectivity, a totally backwards board reported zero errors.

---

### Act 5: Production Lock-In & Accidental Discovery (`2026-11-20` → `2026-11-25`)
In commit `0d10c50`, the carrier Gerbers/BOM/CPL were moved into `fabrication/in_production/jlcpcb_carrier/` and explicitly marked **locked / byte-for-byte frozen**, while active engineering shifted entirely to the modular satellite faceplate, wood/acrylic panels, diffuser, and Capstan v2 knob. Every downstream session respected that lock — *no one looks inside an "in-production" folder until something breaks*.

What finally blew the cover off was **JLCPCB failing to source `THAT1200S08-U` and `THAT1646S08-U`**, prompting a check of drop-in TI equivalents (`INA134` / `DRV135`), which forced opening the raw `thatcorp.com` datasheets and cross-checking `icio500.kicad_pcb` pad-by-pad.

---

## Part II — How the Hell *Could* This Happen? (Structural Failure Modes)

Looking past the commit dates, six systemic traps made this failure almost inevitable once those first 8 minutes happened:

1. **Code-as-hardware makes pin hallucinations look clean.**
   In Python or `.ato`, writing `signal Out_Plus ~ pin 1` looks just as tidy, typed, and deterministic as the true datasheet pinout. Nothing throws a syntax error when Pin 2 is `-16 V` instead of `Sns-`. Worse: **even web-search AI summaries hallucinate pinouts** — during this very audit, Google Search summaries returned two *different* contradictory SOIC-8 pinouts for `THAT1200` and `THAT1646` depending on query phrasing! Only downloading and parsing the manufacturer's actual PDF (`Doc 600033` and `Doc 600078`) revealed ground truth.

2. **Unpolarized abstractions hide negative-rail math.**
   Atopile's `.p1` / `.p2` capacitor interface treats every cap like a non-polarized MLCC. Saying `V_Minus_Analog ~ cap.p1; cap.p2 ~ GND` "reads" naturally (`signal -> p1, p2 -> GND`), yet for `GND = 0 V` and `V_Minus = -16 V`, `p1` is at a *lower* potential than `p2`. Unless a schematic ERC or human checks `V(pad1) > V(pad2)`, a backwards negative-rail cap silently survives to Gerber export.

3. **Reverse-generating the schematic destroyed the Single Source of Truth.**
   Normally, you draw a schematic from vetted datasheet symbols, verify ERC, and drive the PCB from the schematic. Here, `generate_carrier_schematic.py` was written 5 months *after* the PCB existed specifically to match the PCB. That turned circular self-consistency into a polished schematic PDF that looked like an independent verification when it was really an echo of Day-1 bugs.

4. **"0 DRC violations" is a dangerous false security metric.**
   KiCad's DRC checks trace-to-trace clearance, drill sizes, courtyard overlaps, and whether `Segment A` touches `Pad B` of the same net name. **DRC has zero concept of**:
   - Datasheet pinouts
   - Positive vs. negative rail polarity
   - Capacitor voltage ratings (`10 V` cap on a `48 V` line)
   - Op-amp signal levels vs. ADC clip voltage
   - Whether a `0 V`-centered AC audio pin can tolerate a Schottky diode to `GND`
   - Whether a chip's wafer fab still exists

5. **Confident docstrings induce automation bias.**
   Phrases in scripts like `"production-grade, mathematically verified"` and `verify_vpr_compliance.py`'s `"100% CLEAN PASS"` act as social engineering on both humans and later AI agents. Later passes read `"verified"` and skip opening the primary datasheet.

6. **Siloed iteration creates blind spots.**
   Once attention shifted to solving real mechanical/3D/optical headaches (KiCad 3D viewer coordinate bugs, blind LED pockets, Capstan v2 knob clearance, Ponoko wood slots), those parts received intense scrutiny and visual inspection — while the carrier board's analog stage sat untouched since June 4.

---

## Part III — The Non-Negotiable Rev-2 Pre-Tapeout Gate

Before a single Rev-2 carrier Gerber ever goes to JLCPCB:

1. **Raw PDF Pin-by-Pin Audit (Every Semiconductor):** Download the manufacturer's actual datasheet PDF (never trust memory, web summaries, or existing scripts) and verify a pad-by-pad table (`Pin 1..N` name, function, and actual `.kicad_pcb` net) for `U1`, `U2`, `U3`, `U4`, `U5`, and `D1`–`D11`.
2. **Signed Voltage Polarity Table (Every Polarized Part & Diode):** Compute `V(Pad 1) - V(Pad 2)` across worst-case DC/phantom/fault conditions for every diode and electrolytic (`C1, C3, C21, C22, C25, C26, C27`). On `-16 V`, `Pad 1 (+)` MUST go to `GND` and `Pad 2 (-)` to `-16 V`.
3. **BOM Derating & Live Lifecycle Check:** Check every BOM capacitor's **voltage rating (`≥ 2×` worst-case including `+48 V` fault on exposed I/O)** and dielectric (`X5R`/`X7R` kept out of series audio paths), match package sizes (`Ø × H`) to footprint land patterns, and check **real distributor stock + lifecycle** (not just cached LCSC IDs).
4. **Schematic-First Workflow:** Any Rev-2 KiCad edits start from true datasheet symbols in the schematic (`F8` forward-annotate to PCB), never by copying PCB netlists back into a schematic generator.
5. **End-to-End Gain, Headroom & Clamp Audit:** Write out RMS / peak voltages in `dBu` and `Vpp` at input, `U2`, `U3A` (`~-15` to `-18 dB` target into Daisy codec), symmetric clamp threshold (`> codec clip`, not `-0.3 V`), Daisy DAC out, `U3B`, and `U4` — checking both clip point (`+18..+22 dBu = 0 dBFS`) and net polarity (`0°`, not `180°`).
6. **Separated `3V3_A` / `3V3_D` & True Pin Labels:** Keep `U5.21` (`3V3_A`) off the digital faceplate rail (`U5.38`), rename `d14` on `U5.22` to `enc_a_d15`, and swap `C2332` for proper square-pin female headers (`1×20`).
7. **Pick-and-Place Visual Overlay + Current-Limited Bench Bring-Up:** Visually inspect every Pin-1/cathode/anode mark on the JLCPCB assembly preview, and always power Rev-2 on a current-limited `±16 V` bench supply before touching a 500-series rack.
