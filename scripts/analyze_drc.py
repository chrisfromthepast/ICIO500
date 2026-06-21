import json

with open(r"build\icio500\drc_report.json", "r") as f:
    data = json.load(f)

# Count violations by type
types = {}
severity = {}
for v in data.get("violations", []):
    t = v.get("type", "unknown")
    s = v.get("severity", "unknown")
    types[t] = types.get(t, 0) + 1
    severity[s] = severity.get(s, 0) + 1

print("=== Violations by Type ===")
for t in sorted(types.keys(), key=lambda x: types[x], reverse=True):
    print(f"  {t}: {types[t]}")

print()
print("=== Violations by Severity ===")
for s in sorted(severity.keys(), key=lambda x: severity[x], reverse=True):
    print(f"  {s}: {severity[s]}")

# Show first 3 of each type
print()
print("=== Sample Violations ===")
shown_types = {}
for v in data.get("violations", []):
    t = v.get("type", "unknown")
    if t not in shown_types:
        shown_types[t] = 0
    if shown_types[t] < 2:
        shown_types[t] += 1
        desc = v.get("description", "no description")
        items = v.get("items", [])
        print(f"  [{t}] {desc}")
        for item in items[:2]:
            item_desc = item.get("description", "")
            print(f"    -> {item_desc}")
        print()
