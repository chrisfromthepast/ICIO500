"""Replace bad GND segment with 3-segment south-jog route around C19 v_plus pad."""
import uuid as uuid_mod, re

PCB_PATH = 'build/icio500/icio500.kicad_pcb'

def seg(sx, sy, ex, ey, net='gnd', width=0.25, layer='F.Cu'):
    return (
        '\t(segment\r\n'
        f'\t\t(start {sx} {sy})\r\n'
        f'\t\t(end {ex} {ey})\r\n'
        f'\t\t(width {width})\r\n'
        f'\t\t(layer "{layer}")\r\n'
        f'\t\t(net "{net}")\r\n'
        f'\t\t(uuid "{uuid_mod.uuid4()}")\r\n'
        '\t)'
    )

pcb = open(PCB_PATH, encoding='utf-8').read()

# Remove the bad direct segment (159.5,78) -> (160.7,79.2)
bad_uuid = 'ac3f7133-c424-445b-a403-e6f1c5e1feca'
bad_pattern = re.compile(
    r'\t\(segment\r?\n'
    r'\t\t\(start 159\.5 78\)\r?\n'
    r'\t\t\(end 160\.7 79\.2\)\r?\n'
    r'\t\t\(width 0\.25\)\r?\n'
    r'\t\t\(layer "F\.Cu"\)\r?\n'
    r'\t\t\(net "gnd"\)\r?\n'
    r'\t\t\(uuid "' + re.escape(bad_uuid) + r'"\)\r?\n'
    r'\t\)\r?\n'
)

m = bad_pattern.search(pcb)
if m:
    pcb = pcb[:m.start()] + pcb[m.end():]
    print('Removed bad direct segment.')
else:
    print('WARNING: bad segment not found by UUID — searching by coords...')
    # Fallback: search by start/end coords
    alt = re.search(
        r'\t\(segment\r?\n\t\t\(start 159\.5 78\)\r?\n\t\t\(end 160\.7 79\.2\)\r?\n.*?\t\)\r?\n',
        pcb, re.DOTALL
    )
    if alt:
        pcb = pcb[:alt.start()] + pcb[alt.end():]
        print('Removed bad segment by coords.')
    else:
        print('ERROR: could not find segment to remove!')

# Insert 3-segment south jog:
# (159.5, 78.0) -> (159.5, 79.5) [south, clear of audio diagonal]
# (159.5, 79.5) -> (160.7, 79.5) [east]
# (160.7, 79.5) -> (160.7, 79.2) [north, meets GND via at (160.7, 79.2)]
new_segs = '\n'.join([
    seg(159.5, 78.0, 159.5, 79.5),
    seg(159.5, 79.5, 160.7, 79.5),
    seg(160.7, 79.5, 160.7, 79.2),
])

insert_pos = pcb.rfind('\n)')
pcb = pcb[:insert_pos] + '\n' + new_segs + pcb[insert_pos:]

open(PCB_PATH, 'w', encoding='utf-8').write(pcb)
print('Added 3-segment south-jog GND route from C19 pad2 to GND via at (160.7, 79.2).')
