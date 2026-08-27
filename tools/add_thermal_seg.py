import uuid as uuid_mod

seg_uuid = str(uuid_mod.uuid4())
new_seg = (
    '\t(segment\r\n'
    '\t\t(start 159.5 78)\r\n'
    '\t\t(end 160.7 79.2)\r\n'
    '\t\t(width 0.25)\r\n'
    '\t\t(layer "F.Cu")\r\n'
    '\t\t(net "gnd")\r\n'
    '\t\t(uuid "' + seg_uuid + '")\r\n'
    '\t)'
)

pcb = open('build/icio500/icio500.kicad_pcb', encoding='utf-8').read()
insert_pos = pcb.rfind('\n)')
pcb = pcb[:insert_pos] + '\n' + new_seg + pcb[insert_pos:]
open('build/icio500/icio500.kicad_pcb', 'w', encoding='utf-8').write(pcb)
print('Added GND segment: C19 pad2 (159.5,78) -> GND via (160.7,79.2)')
print(f'UUID: {seg_uuid}')
