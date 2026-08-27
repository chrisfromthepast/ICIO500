import json

with open('build/icio500/drc_baseline.json', encoding='utf-8') as f:
    report = json.load(f)

for v in report.get('violations', []):
    if v.get('type') in ('shorting_items', 'tracks_crossing'):
        print(v.get('type'), ':', v.get('description', ''))
        for item in v.get('items', []):
            pos = item.get('pos', {})
            desc = item.get('description', '')
            x = pos.get('x', 0)
            y = pos.get('y', 0)
            print(f'  {desc}')
            print(f'    pos=({x:.4f}, {y:.4f})')
        print()
