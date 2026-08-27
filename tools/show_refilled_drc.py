import json
from collections import Counter

with open('build/icio500/drc_final2.json', encoding='utf-8') as f:
    report = json.load(f)

types = Counter(v.get('type') for v in report['violations'])
print('=== DRC REFILLED RESULT ===')
print('Total:', len(report['violations']), 'violations')
for t, c in types.most_common():
    print(f'  {t}: {c}')

print()
print('Electrical / structural violations (non-padstack, non-silk):')
ignore = ('padstack', 'silk_overlap', 'silk_over_copper', 'lib_footprint_issues',
          'lib_footprint_mismatch')
for v in report['violations']:
    t = v.get('type', '')
    if t not in ignore:
        desc = v.get('description', '')
        print(f'  [{t}]: {desc}')
        for item in v.get('items', []):
            pos = item.get('pos', {})
            x = round(pos.get('x', 0), 2)
            y = round(pos.get('y', 0), 2)
            print(f'    {item.get("description","")}  @ ({x},{y})')
