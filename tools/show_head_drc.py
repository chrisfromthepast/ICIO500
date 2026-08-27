import json
from collections import Counter

with open('build/icio500/drc_head.json', encoding='utf-8') as f:
    r = json.load(f)

types = Counter(v.get('type') for v in r['violations'])
print('HEAD baseline (43 violations):')
for t, c in types.most_common():
    print(f'  {t}: {c}')

print()
for v in r['violations']:
    t = v.get('type', '')
    if t in ('isolated_copper', 'starved_thermal', 'via_dangling'):
        print(f'  [{t}]: {v.get("description","")}')
