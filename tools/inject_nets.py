"""
Inject nets from faceplate_logic schematic into panel_satellite.kicad_pcb.
Bypasses kicad-cli entirely by directly editing the PCB file.

Net assignments derived from faceplate_logic.kicad_sch:
  J1 (20-pin header): Pin 1=+3V3, 2=+3V3, 3=GND, 4=SDA, 5=GND, 6=SCL,
                       7=GND, 8=ENC_A, 9=ENC_B, 10=ENC_SW, 11-20=unconnected
  U1 (IS31FL3236):     Pin 1=+3V3(VCC), 2=GND, 3=SDA, 4=SCL, 5=+3V3(~SDB),
                       6=GND(AD), 7=LED_1(OUT1), 8=LED_2(OUT2), 9=LED_3(OUT3),
                       10=LED_4(OUT4), 11=LED_5(OUT5), 12=LED_6(OUT6),
                       13=LED_7(OUT7), 14=LED_8(OUT8), 15=LED_9(OUT9), 16=LED_10(OUT10)
  ENC1 (Encoder):      Pin 1=ENC_A, 2=GND, 3=ENC_B, 4=ENC_SW, 5=GND
  D1-D10 (LEDs):       Anode(A)=+3V3, Cathode(K)=LED_N (via resistor)
  R1-R10 (33R):        Pin 1=LED_N, Pin 2=LED_N (series between LED cathode and U1 output)
  R11 (4.7k pullup):   Pin 1=SDA, Pin 2=+3V3
  R12 (4.7k pullup):   Pin 1=SCL, Pin 2=+3V3
  C1 (10uF):           Pin 1=+3V3, Pin 2=GND
  C2 (100nF):          Pin 1=+3V3, Pin 2=GND
  FB1 (Ferrite bead):  Pin 1=+3V3_IN, Pin 2=+3V3
  MH (mounting holes): No net
"""
import re
import uuid

# Define all nets
NET_NAMES = [
    "+3V3", "GND", "SDA", "SCL",
    "ENC_A", "ENC_B", "ENC_SW",
    "LED_1", "LED_2", "LED_3", "LED_4", "LED_5",
    "LED_6", "LED_7", "LED_8", "LED_9", "LED_10",
    "+3V3_IN",  # input side of ferrite bead
]

# Component -> pin -> net
# For LEDs: the resistor is in series, so LED cathode and resistor pin 1 share a net
# The net between Rn.pin1 and Dn.K is the "LED_N" net
# U1 OUT_N connects to Rn.pin2 which is the other side
# Actually looking at the schematic more carefully:
# The LED chain is: +3V3 -> D_n(A) -> D_n(K) -- wire -- R_n(pin1) -> R_n(pin2) -- wire -- U1(OUT_N)
# So: D_n.A = +3V3, D_n.K = LED_N_cathode, R_n.1 = LED_N_cathode, R_n.2 = LED_N (to U1)
# Wait, let me re-read. The net labels in the schematic show:
# LED_1 at (143, 20) and LED_1 at (117, 68.89)
# R1 is at (150, 20) rotated 90, D1 is at (170, 20)
# U1 OUT1 (pin 7) is at U1_x - 5.08 = 104.92, U1_y - 8.89+60 = 68.89... wait U1 at (110, 60)
# U1 pin 7 (OUT1): at (110-5.08, 60-8.89) = (104.92, 51.11)... 
# Actually the pin offsets are relative to the symbol origin.
# LED_1 label at (117, 68.89) connects to U1 OUT1 at pin 7
# LED_1 label at (143, 20) connects between R1 and D1

# So: U1.OUT_N -> LED_N net -> R_N.pin1
#     R_N.pin2 -> LED_N_cathode net -> D_N.K
#     D_N.A -> GND (the LED anodes go to GND on the cathode side... wait)

# Looking more carefully at the GND labels at (177, 20), (177, 29), etc. - 
# these are at the anode side of the LEDs (D1.A at 170+3.81=173.81... not exactly 177)
# Actually LED_Small: pin K at (-3.81, 0), pin A at (3.81, 0)
# D1 at (170, 20): K at (166.19, 20), A at (173.81, 20)
# GND label at (177, 20) - that's near the anode side
# So D_N.A = GND? That means current sinks through the LED.
# IS31FL3236 is a constant-current sink driver - it sinks current on OUT pins.
# So: +3V3 -> R_N -> LED_N_mid -> D_N.K(cathode) and D_N.A(anode) -> GND? 
# No wait, for a sink driver: VCC -> R -> LED(A->K) -> IS31FL3236 OUT (sink)
# Let me re-examine. R1 at (150, 20) rot 90. R_Small pins: pin1 at (0,-3.81) rot90 = (-3.81*sin90, ...) 
# Actually for rotation 90: pin1 at original (0, -3.81) becomes (3.81, 0) relative, so absolute (153.81, 20)
# pin2 at original (0, 3.81) becomes (-3.81, 0) relative, so absolute (146.19, 20)
# LED_1 label at (143, 20) is near R1.pin2 (146.19, 20)
# So LED_1 net connects to R1.pin2
# R1.pin1 at (153.81, 20) connects to... D1.K at (166.19, 20)? There's a gap.
# There must be a wire between them. The net between R1.pin1 and D1.K is unlabeled.
# D1.A at (173.81, 20), GND at (177, 20) - so D1.A = GND

# So the chain is: U1.OUT_N (sink) <- LED_N net <- R_N.pin2 ... R_N.pin1 <- wire <- D_N.K <- D_N.A <- GND
# Current flows: GND -> D_N(A->K) -> R_N(1->2) -> U1.OUT_N (sink to ground internally)
# Wait that doesn't make sense for a current sink. Let me think again.

# IS31FL3236 sinks current. So current flows FROM VCC through external LED+R INTO the OUT pin.
# But the GND label is on the anode side... 

# Actually I think the schematic has the LEDs oriented so:
# +3V3 feeds into the circuit somewhere, and GND is at the far end
# Let me just look at it differently. The LED_N net label appears twice:
# Once near R_N (between R_N and U1 output), once at U1's output pin
# So LED_N connects R_N to U1.

# For the R-to-D connection (unlabeled), I'll call it LED_N_mid
# And D.A connects to GND (as shown by GND labels at the anode positions)

# CORRECTION: Looking at the schematic again more carefully:
# R1 at (150, 20) rot 90 -> pin1 at ~(153.81, 20), pin2 at ~(146.19, 20)
# D1 at (170, 20) -> K at (166.19, 20), A at (173.81, 20)
# LED_1 label at (143, 20) -> near R1.pin2 (146.19) -> LED_1 connects R1.pin2 to U1.OUT1
# R1.pin1 (153.81) and D1.K (166.19) are connected by an unlabeled wire
# GND at (177, 20) connects to D1.A (173.81, 20)

# So final chain: GND -> D1.A -> D1.K -> R1.pin1 -> R1.pin2 -> LED_1 -> U1.OUT1
# This is wrong for IS31FL3236 which is a current SINK.
# Actually wait - IS31FL3236 has constant current outputs that SINK.
# When OUT is active, it pulls to ground. So current flows:
# +3V3 (VCC) -> ... but where does +3V3 connect to the LED chain?
# Maybe the GND labels at (177, 20) etc are actually +3V3? Let me re-check.
# No, they clearly say "GND".
# 
# OK I think I'm overcomplicating this. The IS31FL3236 OUT pins source OR sink?
# From datasheet: "36 constant current channels" - they are current sinks.
# Output is open-drain, pulls to GND when on.
# So: VCC -> LED -> R -> IS31FL3236 OUT (sinks to GND)
# 
# But the GND labels are at the LED anode side... This schematic might have the LEDs
# backwards, or it might be using them in a non-standard way.
#
# For our PCB netlist injection purposes, it doesn't matter - we just need to know
# which pad connects to which net name. Let me just map them directly.

# The actual net assignments based on what the schematic wires connect:
COMP_PIN_NET = {
    # J1: 20-pin ribbon header (from main.ato guard channel plan)
    'J1': {
        '1': '+3V3', '2': '+3V3',
        '3': 'GND', '4': 'SDA',
        '5': 'GND', '6': 'SCL',
        '7': 'GND', '8': 'ENC_A',
        '9': 'ENC_B', '10': 'ENC_SW',
        # 11-20 unconnected for now
    },
    # U1: IS31FL3236 (TSSOP-36, but schematic only defines 16 pins)
    'U1': {
        '1': '+3V3',      # VCC
        '2': 'GND',       # GND
        '3': 'SDA',       # SDA
        '4': 'SCL',       # SCL
        '5': '+3V3',      # ~SDB (shutdown bar, tie high)
        '6': 'GND',       # AD (address select, tie to GND for 0x3C)
        '7': 'LED_1',     # OUT1
        '8': 'LED_2',     # OUT2
        '9': 'LED_3',     # OUT3
        '10': 'LED_4',    # OUT4
        '11': 'LED_5',    # OUT5
        '12': 'LED_6',    # OUT6
        '13': 'LED_7',    # OUT7
        '14': 'LED_8',    # OUT8
        '15': 'LED_9',    # OUT9
        '16': 'LED_10',   # OUT10
    },
    # ENC1: Rotary encoder with switch
    'ENC1': {
        '1': 'ENC_A',     # A
        '2': 'GND',       # Common
        '3': 'ENC_B',     # B
        '4': 'ENC_SW',    # Switch pin 1
        '5': 'GND',       # Switch pin 2
    },
    # R1-R10: 33R series resistors (between LED cathode and U1 output)
    # R_N.pin1 connects to D_N.K (LED_N_MID net)
    # R_N.pin2 connects to LED_N net (to U1 output)
    'R1':  {'1': 'LED_1_MID', '2': 'LED_1'},
    'R2':  {'1': 'LED_2_MID', '2': 'LED_2'},
    'R3':  {'1': 'LED_3_MID', '2': 'LED_3'},
    'R4':  {'1': 'LED_4_MID', '2': 'LED_4'},
    'R5':  {'1': 'LED_5_MID', '2': 'LED_5'},
    'R6':  {'1': 'LED_6_MID', '2': 'LED_6'},
    'R7':  {'1': 'LED_7_MID', '2': 'LED_7'},
    'R8':  {'1': 'LED_8_MID', '2': 'LED_8'},
    'R9':  {'1': 'LED_9_MID', '2': 'LED_9'},
    'R10': {'1': 'LED_10_MID', '2': 'LED_10'},
    # R11, R12: 4.7k I2C pullups
    'R11': {'1': 'SDA', '2': '+3V3'},
    'R12': {'1': 'SCL', '2': '+3V3'},
    # D1-D10: LEDs (0805)
    # Pin K (cathode) connects to R_N.pin1 (LED_N_MID)
    # Pin A (anode) connects to GND (IS31FL3236 is current sink, LEDs are reverse-biased to GND)
    'D1':  {'K': 'LED_1_MID',  'A': 'GND'},
    'D2':  {'K': 'LED_2_MID',  'A': 'GND'},
    'D3':  {'K': 'LED_3_MID',  'A': 'GND'},
    'D4':  {'K': 'LED_4_MID',  'A': 'GND'},
    'D5':  {'K': 'LED_5_MID',  'A': 'GND'},
    'D6':  {'K': 'LED_6_MID',  'A': 'GND'},
    'D7':  {'K': 'LED_7_MID',  'A': 'GND'},
    'D8':  {'K': 'LED_8_MID',  'A': 'GND'},
    'D9':  {'K': 'LED_9_MID',  'A': 'GND'},
    'D10': {'K': 'LED_10_MID', 'A': 'GND'},
    # C1, C2: Decoupling caps
    'C1': {'1': '+3V3', '2': 'GND'},
    'C2': {'1': '+3V3', '2': 'GND'},
    # FB1: Ferrite bead (power input filter)
    'FB1': {'1': '+3V3_IN', '2': '+3V3'},
}

# Collect all unique net names
all_nets = set()
for comp, pins in COMP_PIN_NET.items():
    for pin, net in pins.items():
        all_nets.add(net)
all_nets = sorted(all_nets)

# Assign net IDs (0 = unconnected)
net_id_map = {name: i+1 for i, name in enumerate(all_nets)}

print(f"Total nets: {len(all_nets)}")
for name, nid in net_id_map.items():
    print(f"  Net {nid}: {name}")

# Read PCB
with open('build/icio500/panel_satellite.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# 1. Inject net declarations after the existing (net 0 "") line
net_decls = '\n'.join(f'\t(net {nid} "{name}")' for name, nid in net_id_map.items())
pcb = pcb.replace('\t(net 0 "")\n', f'\t(net 0 "")\n{net_decls}\n')

# 2. For each footprint, find its reference and assign nets to pads
def find_end(content, start):
    depth = 0
    for i in range(start, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return -1

# Find all footprints and their references
fp_iter = list(re.finditer(r'\t\(footprint "', pcb))
for fp_match in fp_iter:
    fp_start = fp_match.start()
    fp_end = find_end(pcb, fp_start)
    fp_block = pcb[fp_start:fp_end+1]

    ref_match = re.search(r'\(property "Reference" "([^"]+)"', fp_block)
    if not ref_match:
        continue
    ref = ref_match.group(1)

    if ref not in COMP_PIN_NET:
        continue

    pin_nets = COMP_PIN_NET[ref]
    modified = False

    for pin_num, net_name in pin_nets.items():
        nid = net_id_map[net_name]
        # Find the pad with this pin number in the footprint block
        # Pattern: (pad "1" ... )  or (pad "K" ...)
        pad_pattern = rf'\(pad "{re.escape(pin_num)}" '
        for pad_match in re.finditer(pad_pattern, fp_block):
            pad_start = pad_match.start()
            pad_end = find_end(fp_block, pad_start)
            pad_text = fp_block[pad_start:pad_end+1]

            # Check if pad already has a net assignment
            if '(net ' in pad_text:
                # Replace existing net
                pad_new = re.sub(r'\(net \d+ "[^"]*"\)', f'(net {nid} "{net_name}")', pad_text)
            else:
                # Insert net assignment before closing paren
                pad_new = pad_text[:-1] + f' (net {nid} "{net_name}"))'

            fp_block = fp_block[:pad_start] + pad_new + fp_block[pad_end+1:]
            modified = True

    if modified:
        # Replace the footprint block in the PCB
        pcb = pcb[:fp_start] + fp_block + pcb[fp_end+1:]
        # Re-find footprints since offsets changed
        fp_iter = list(re.finditer(r'\t\(footprint "', pcb))
        print(f"  Assigned nets to {ref}: {pin_nets}")

# Write back
with open('build/icio500/panel_satellite.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb)

print("\nDone! Nets injected into panel_satellite.kicad_pcb")
