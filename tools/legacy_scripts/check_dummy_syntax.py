import re

with open('build/icio500/icio500_3d_assembly.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

# Check if DUMMY footprint has a UUID
dummy_block = pcb[pcb.find('footprint "DUMMY"'):]
dummy_block = dummy_block[:dummy_block.find('\n  )\n') + 5]
print("DUMMY footprint block:")
print(dummy_block)
print()

# Check a normal footprint for comparison
normal = pcb[pcb.find('footprint "lib:R0603"'):]
normal = normal[:300]
print("Normal footprint (first 300 chars):")
print(normal)
