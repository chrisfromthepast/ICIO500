import json

with open('build/icio500/drc_final.json', encoding='utf-8') as f:
    report = json.load(f)

for v in report.get('violations', []):
    vtype = v.get('type', '')
    if vtype in ('shorting_items', 'tracks_crossing', 'clearance'):
        print(vtype + ': ' + v.get('description', ''))
        for item in v.get('items', []):
            desc = item.get('description', '')
            pos = item.get('pos', {})
            x = pos.get('x', 0)
            y = pos.get('y', 0)
            print(f'  {desc}  @ ({x:.4f}, {y:.4f})')
        print()
