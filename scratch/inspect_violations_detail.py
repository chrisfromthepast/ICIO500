import json

with open('scratch/drc_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

print("=== ALL CROSSINGS AND SHORTS WITH COORDINATES ===")
for v in report.get('violations', []):
    t = v.get('type', '')
    if t in ['tracks_crossing', 'shorting_items']:
        desc = v.get('description', '')
        items = [it.get('description', '') for it in v.get('items', [])]
        pos = v.get('pos', {})
        print(f"\n[{t}] {desc}")
        print(f"  At: ({pos.get('x', 0):.2f}, {pos.get('y', 0):.2f})")
        for it in items:
            print(f"    - {it}")
