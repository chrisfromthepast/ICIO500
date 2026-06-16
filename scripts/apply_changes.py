import pcbnew
import re
from collections import defaultdict

PCB_PATH = 'build/icio500/icio500.kicad_pcb'
NET_PATH = 'build/default.net'

b = pcbnew.LoadBoard(PCB_PATH)

# 1. Remove duplicates (C5, C6, U1 DC-DC ISO)
ref_map = defaultdict(list)
for fp in b.GetFootprints():
    ref_map[fp.GetReference()].append(fp)

for ref, fps in ref_map.items():
    if len(fps) > 1:
        fps_sorted = sorted(fps, key=lambda f: (
            'DC-DC' in f.GetValue(),
            f.GetPosition().x
        ))
        for fp in fps_sorted[1:]:
            b.Remove(fp)
            print('Removed duplicate:', ref)

# 2. Move scaling block between U4 (Y=70) and U2 (Y=105)
SCALING = {'U3', 'C15', 'C16', 'C17', 'C18', 'R3', 'R4', 'R5', 'R6'}
sfps = [f for f in b.GetFootprints() if f.GetReference() in SCALING]
xs = [f.GetPosition().x for f in sfps]
ys = [f.GetPosition().y for f in sfps]
cx = (min(xs) + max(xs)) // 2
cy = (min(ys) + max(ys)) // 2
dx = int(155e6) - cx
dy = int(87e6) - cy
for f in sfps:
    p = f.GetPosition()
    f.SetPosition(pcbnew.VECTOR2I(p.x + dx, p.y + dy))
print(f'Scaling moved: center now X=155 Y=87')

# 3. Clear all tracks
n = 0
for t in list(b.Tracks()):
    b.Remove(t)
    n += 1
print(f'Cleared {n} tracks')

b.BuildConnectivity()
pcbnew.SaveBoard(PCB_PATH, b)
print('Saved OK')
