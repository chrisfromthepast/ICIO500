import json, sys
from collections import Counter

filename = sys.argv[1] if len(sys.argv) > 1 else 'build/icio500/drc_baseline.json'
with open(filename, encoding='utf-8') as f:
    report = json.load(f)

violations = report.get('violations', [])
types = Counter(v.get('type', 'unknown') for v in violations)
print(f'=== DRC REPORT: {filename} ===')
print(f'Total: {len(violations)} violations')
for t, count in types.most_common():
    print(f'  {t}: {count}')

shorts = [v for v in violations if v.get('type') == 'shorting_items']
print(f'\nShorts: {len(shorts)}')
for v in shorts:
    print('  ' + v.get('description', ''))
