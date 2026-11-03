import json
import sys

fn = sys.argv[1] if len(sys.argv) > 1 else 'temp_drc_fp_curr.json'
d = json.load(open(fn))
print(f"=== UNCONNECTED ITEMS ({len(d.get('unconnected_items', []))}) ===")
for u in d.get('unconnected_items', []):
    print("Unconnected:", u.get('description'))
    for it in u.get('items', []):
        print("  -", it.get('description'), "at", it.get('pos'))

print(f"\n=== ELECTRICAL / PHYSICAL VIOLATIONS ({len(d.get('violations', []))}) ===")
non_mask = 0
for v in d.get('violations', []):
    vt = v.get('type')
    if vt in ['solder_mask_bridge', 'silk_overlap', 'silk_over_copper', 'lib_footprint_mismatch']:
        continue
    non_mask += 1
    print(f"[{vt}] {v.get('description')}")
    for it in v.get('items', []):
        print(f"   {it.get('description')} at {it.get('pos')}")
print(f"Total non-mask violations: {non_mask}")
