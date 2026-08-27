import json
from collections import Counter

with open('build/icio500/drc_final.json', encoding='utf-8') as f:
    report = json.load(f)

types = Counter(v.get('type') for v in report['violations'])
print('=== DRC CLEAN RESULT ===')
print('Total:', len(report['violations']), 'violations')
for t, c in types.most_common():
    print(f'  {t}: {c}')

print()
print('Electrical / structural violations:')
elec = ('shorting_items','tracks_crossing','clearance','via_dangling',
        'starved_thermal','hole_clearance','isolated_copper')
for v in report['violations']:
    t = v.get('type','')
    if t in elec:
        print(f'  [{t}]: {v.get("description","")}')
        for item in v.get('items',[]):
            pos = item.get('pos', {})
            x = round(pos.get('x', 0), 2)
            y = round(pos.get('y', 0), 2)
            print(f'    {item.get("description","")}  @ ({x},{y})')
