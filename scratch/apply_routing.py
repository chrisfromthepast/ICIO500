import re
import uuid
import subprocess
import shutil
from test_autoroute import routed_results, get_u6_pad, get_u5_pad

print(f"Loaded {len(routed_results)} zero-via routed paths from autoroute.")

def format_track(start, end, layer, net, width=0.25):
    u = str(uuid.uuid4())
    return f'''\t(segment
\t\t(start {start[0]} {start[1]})
\t\t(end {end[0]} {end[1]})
\t\t(width {width})
\t\t(layer "{layer}")
\t\t(net "{net}")
\t\t(uuid "{u}")
\t)
'''

# Let's inspect the tracks generated
new_tracks = []
for name, (pts, layer_num) in routed_results.items():
    layer = "F.Cu" if layer_num == 0 else "B.Cu"
    width = 0.5 if name == 'daisy_5v_power' else 0.25
    for i in range(len(pts) - 1):
        new_tracks.append(format_track(pts[i], pts[i+1], layer, name, width=width))

print(f"Generated {len(new_tracks)} track segments for the 14 zero-via nets.")
