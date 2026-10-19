import json

with open('scratch/drc_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

for v in report.get('violations', []):
    t = v.get('type', '')
    if t in ['shorting_items', 'tracks_crossing', 'clearance']:
        desc = v.get('description', '')
        items = [it.get('description', '') for it in v.get('items', [])]
        pos = v.get('pos', {})
        print(f"[{t:15s}] {desc}")
        print(f"   Pos: ({pos.get('x', 0):.2f}, {pos.get('y', 0):.2f})")
        for it in items:
            print(f"     - {it}")
