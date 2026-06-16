import pcbnew
from collections import defaultdict

b = pcbnew.LoadBoard('build/icio500/icio500.kicad_pcb')

# Find duplicate refs and remove the OLD DC-DC ISO ones
# The OLD ones are: U1 DC-DC ISO at 154.27, 146.75
#                   C5 at 90.91, 115.25
#                   C6 at 96.92, 115.25

refs = defaultdict(list)
for fp in b.GetFootprints():
    refs[fp.GetReference()].append(fp)

to_remove = []

for ref, fps in refs.items():
    if len(fps) > 1:
        print(f"Duplicate ref: {ref}")
        for fp in fps:
            pos = fp.GetPosition()
            val = fp.GetValue()
            lib = fp.GetFPID().GetLibItemName().c_str()
            print(f"  X={pos.x/1e6:.2f} Y={pos.y/1e6:.2f}  val={val}  lib={lib}")
            
            # Remove the OLD DC-DC ISO U1
            if ref == 'U1' and val == 'DC-DC ISO':
                to_remove.append(fp)
            # Remove the OLD C5 (the one near X=90)
            if ref == 'C5' and pos.x/1e6 < 100:
                to_remove.append(fp)
            # Remove the OLD C6 (the one near X=96)
            if ref == 'C6' and pos.x/1e6 < 100:
                to_remove.append(fp)

print(f"\nRemoving {len(to_remove)} duplicate components...")
for fp in to_remove:
    pos = fp.GetPosition()
    print(f"  Removing {fp.GetReference()} at X={pos.x/1e6:.2f} Y={pos.y/1e6:.2f} val={fp.GetValue()}")
    b.Remove(fp)

b.BuildConnectivity()
pcbnew.SaveBoard('build/icio500/icio500.kicad_pcb', b)
print("Done.")
