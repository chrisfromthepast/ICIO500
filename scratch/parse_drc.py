import json

with open('scratch/drc_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

violations = report.get('violations', [])
unconnected = report.get('unconnected_items', [])

print(f"Total violations: {len(violations)}")
print(f"Total unconnected: {len(unconnected)}")

# Group violations by type
by_type = {}
for v in violations:
    t = v.get('type', 'unknown')
    by_type[t] = by_type.get(t, 0) + 1

for t, count in by_type.items():
    print(f"  {t}: {count}")

print("\n--- Unconnected items ---")
for u in unconnected:
    desc = u.get('description', '')
    items = [it.get('description', '') for it in u.get('items', [])]
    print(f"  {desc} : {items}")

print("\n--- Sample clearance / short violations ---")
for v in violations[:10]:
    desc = v.get('description', '')
    t = v.get('type', '')
    items = [it.get('description', '') for it in v.get('items', [])]
    print(f"  [{t}] {desc} : {items}")
