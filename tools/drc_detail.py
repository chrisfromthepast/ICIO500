import json, sys

filename = sys.argv[1] if len(sys.argv) > 1 else 'build/icio500/drc_fixed.json'
with open(filename, encoding='utf-8') as f:
    report = json.load(f)

violations = report.get('violations', [])

by_type = {}
for v in violations:
    t = v.get('type', 'unknown')
    by_type.setdefault(t, []).append(v)

for vtype, vlist in sorted(by_type.items(), key=lambda x: -len(x[1])):
    print(f'\n{"="*60}')
    print(f'{vtype.upper()} ({len(vlist)} violations)')
    print(f'{"="*60}')
    for v in vlist:
        print(f'  {v.get("description", "")}')
        for item in v.get('items', []):
            desc = item.get('description', '')
            pos = item.get('pos', {})
            x = pos.get('x', 0)
            y = pos.get('y', 0)
            print(f'    -> {desc}  @ ({x:.2f}, {y:.2f})')
