import json
from collections import Counter

with open('build/icio500/drc_report2.json', encoding='utf-8') as f:
    report = json.load(f)

violations = report.get('violations', [])
types = Counter(v.get('type', 'unknown') for v in violations)
print('=== BY TYPE ===')
for t, count in types.most_common():
    print(f'  {t}: {count}')

print()
print('=== REMAINING SHORTS ===')
for v in violations:
    if v.get('type') == 'shorting_items':
        desc = v.get('description', '')
        print(f'  {desc}')
        for item in v.get('items', []):
            d = item.get('description', '')
            pos = item.get('pos', {})
            print(f'    {d} at ({pos.get("x",0):.2f}, {pos.get("y",0):.2f})')

print()
print('=== TRACK CROSSINGS ===')
for v in violations:
    if v.get('type') == 'tracks_crossing':
        for item in v.get('items', []):
            d = item.get('description', '')
            pos = item.get('pos', {})
            print(f'    {d} at ({pos.get("x",0):.2f}, {pos.get("y",0):.2f})')
        print()
