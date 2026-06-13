import json

with open('build/icio500/routing_env.json') as f:
    env = json.load(f)

print("Tracks on B.Cu:")
for o in env:
    if o['type'] == 'track' and o['layer'] == 'B.Cu':
        print(f"Track from ({o['sx']:.1f}, {o['sy']:.1f}) to ({o['ex']:.1f}, {o['ey']:.1f})")
