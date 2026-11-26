# ICIO500 Hardware & PCB Verification Rules

These rules apply unconditionally across the entire repository for all agents and tools.

## 1. Never Author IC Pinouts or Footprints from Memory
- **NEVER** type IC pin assignments (`pin 1..N`), symbol definitions, or footprint pads from memory or web-search summaries into Python or `.kicad_sym`.
- Every IC symbol and footprint MUST come from KiCad's vetted built-in libraries, SnapEDA/UltraLibrarian, or LCSC/EasyEDA, **OR** be cross-checked pin-for-pin (`1..N`) directly from the manufacturer's official datasheet PDF saved locally under `docs/datasheets/`.

## 2. Schematic-First Workflow Only
- **NEVER** generate a `.kicad_sch` to match an existing `.kicad_pcb` (reverse-generating a schematic destroys the single source of truth).
- **NEVER** create or modify electrical signal/power nets, pad numbers, or pinouts inside `.kicad_pcb` using Python or regex scripts.
- All electrical changes MUST flow strictly **Schematic -> ERC -> Forward-Annotate (`F8` / KiCad Update PCB from Schematic) -> PCB Layout**.

## 3. Mandatory Signed Polarity Audit (Every Polarized Cap & Diode)
- For every polarized capacitor and diode, verify **signed voltage** `V(Pad 1) - V(Pad 2)` across all operating and fault conditions (`+16V`, `-16V`, `+5V`, `+3.3V`, `+48V`).
- **NEVER** copy-paste a positive-rail capacitor template (`rail ~ .p1; .p2 ~ GND`) onto a negative rail. On negative rails (`-16V`), **Pad 1 (`+` / chamfered anode) MUST connect to `GND`**, and **Pad 2 (`-` / cathode stripe) MUST connect to the negative rail**.

## 4. Pre-Routing & Pre-Fab BOM, Fit, Rotation & Stock Gate
- Upload and check the draft BOM on JLCPCB/LCSC **before** finalizing routing, and re-verify before generating fabrication zips:
  - **Live availability & lifecycle:** Reject `EOL`, `NRND`, or `0`-stock parts unless the user explicitly approves an alternative or manual sourcing.
  - **Voltage & dielectric derating:** Verify every capacitor rating (`>= 2x` worst-case steady voltage, and able to withstand exposed I/O faults such as `+24 dBu` peaks and `+48V` phantom power). Keep small-case `X5R` MLCCs out of series audio paths.
  - **Mechanical & pin fit:** Verify real component package `Ø x H` against PCB land patterns, and match connector/socket contact style to mating pins (e.g., `0.64 mm` square headers need box/pin-header female sockets, not stamped DIP IC sockets).
  - **CPL orientations:** Verify Pick-and-Place (`*_cpl.csv`) rotations against JLCPCB's visual 3D preview and actual `0°` tape-and-reel reference — never assume raw KiCad angles match JLC assembly.

## 5. Signal Chain Headroom, In-KiCad SPICE Simulation & Rail Isolation
- Compute and tabulate `dBu`, `Vrms`, `Vpp`, phase polarity, and DC bias at every analog and ADC/DAC node before tapeout.
- Run **KiCad's built-in `ngspice` simulator directly on the real `.kicad_sch`** (not a separate hand-transcribed schematic) using vendor `.lib`/`.cir` SPICE models whose `Sim.Pins` mappings are verified against the raw datasheet PDFs:
  - **Transient (`.tran`) sweeps** at nominal and peak levels (e.g., `+4 dBu` and `+20 dBu` / `+24 dBu`) to verify gain, phase, headroom/clip thresholds, and clamp behavior at every stage and ADC/DAC boundary.
  - **DC operating point (`.op`) checks** across all rails, diodes, and capacitors to confirm diode polarity, `V(Pad 1) - V(Pad 2) > 0` on every polarized cap, and `>= 2×` voltage-rating margin *(ideal SPICE capacitor models do not simulate reverse-bias or overvoltage failure on their own)*.
- **NEVER** attach a `0 V`-referenced Schottky clamp (`GND` to `+3.3V`, e.g. `BAT54S`) to a `0 V`-centered AC-coupled bipolar audio line (such as Daisy Seed `Audio In` / `Audio Out`), which hard-clips the negative half-wave at `-0.3 V`.
- Keep analog (`3V3_A`) and digital (`3V3_D`) reference rails isolated; power faceplate/peripheral logic from `3V3_D` only.
- Verify every MCU/DSP physical header pin against the official pinout table and ensure PCB net names match the real GPIO/peripheral name (e.g., Daisy Seed Physical Pin 22 is `D15 / A0`, not `D14`).

## 6. KiCad DRC Is Not Electrical Verification
- **NEVER** claim a board is "mathematically verified", "production-ready", or a "100% clean pass" based on KiCad DRC (`0` errors / `0` unconnected items) or matching PCB-to-schematic parity alone.
- Before generating any Gerber/BOM/CPL zip for fabrication, run and present:
  1. Raw PDF pin-by-pin (`1..N`) comparison against actual `.kicad_pcb` pad nets for every IC (plus `Sim.Pins` check).
  2. Signed polarity check for every electrolytic and diode.
  3. Live BOM stock, lifecycle, voltage-rating, dielectric, and package check.
  4. In-KiCad `ngspice` `.tran` (nominal + peak gain/phase/headroom/clamp) and `.op` (rail/capacitor voltage) results on the real `.kicad_sch`.
- Explicitly list anything not verified directly from primary sources.

## 7. Respect User Part Choices & Locked Fabrication Packs
- **NEVER** silently substitute user-chosen chips or alter locked files under `fabrication/in_production/` unless the user explicitly instructs you to. Flag electrical or supply-chain risks directly and let the user choose.
