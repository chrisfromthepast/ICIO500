"""Verify the PCB after restoration."""
import pcbnew

BOARD_PATH = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\icio500.kicad_pcb"
board = pcbnew.LoadBoard(BOARD_PATH)

# Track width distribution
widths = {}
via_count = 0
for t in board.GetTracks():
    if t.GetClass() == "PCB_VIA":
        via_count += 1
        continue
    w = t.GetWidth() / 1e6
    net = t.GetNetname()
    key = f"{w:.2f}mm"
    if key not in widths:
        widths[key] = {"count": 0, "nets": set()}
    widths[key]["count"] += 1
    widths[key]["nets"].add(net)

print("=== Track Width Distribution ===")
for w in sorted(widths.keys()):
    info = widths[w]
    nets_preview = ", ".join(sorted(list(info["nets"]))[:5])
    if len(info["nets"]) > 5:
        nets_preview += f" ... (+{len(info['nets'])-5} more)"
    print(f"  {w}: {info['count']} tracks")
    print(f"    Nets: {nets_preview}")

print(f"\n  Vias: {via_count}")

# Zones
print(f"\n=== Zones: {len(board.Zones())} ===")
for z in board.Zones():
    net = z.GetNetname()
    layer = board.GetLayerName(z.GetLayer())
    clearance = z.GetLocalClearance() / 1e6
    min_width = z.GetMinThickness() / 1e6
    print(f"  {layer}: net={net}, clearance={clearance:.2f}mm, min_width={min_width:.2f}mm")

# Silkscreen check - verify text sizes
print("\n=== Silkscreen Verification ===")
ok_count = 0
bad_count = 0
for fp in board.GetFootprints():
    ref = fp.GetReference()
    ref_text = fp.Reference()
    h = ref_text.GetTextSize().x / 1e6
    w = ref_text.GetTextSize().y / 1e6
    thick = ref_text.GetTextThickness() / 1e6
    if abs(h - 1.0) < 0.01 and abs(thick - 0.15) < 0.01:
        ok_count += 1
    else:
        bad_count += 1
        print(f"  WARNING: {ref} text size {h:.2f}x{w:.2f}mm, thickness {thick:.2f}mm")

print(f"  {ok_count} refs OK, {bad_count} refs need attention")

print("\n=== Board Summary ===")
print(f"  Footprints: {len(board.GetFootprints())}")
tracks = [t for t in board.GetTracks() if t.GetClass() != "PCB_VIA"]
print(f"  Track segments: {len(tracks)}")
print(f"  Vias: {via_count}")
print(f"  Zones: {len(board.Zones())}")
print(f"  Nets: {board.GetNetCount()}")
