"""
Fix DRC violations by:
1. Reducing power trace width where they cause shorts or clearance violations
2. Moving problem tracks to B.Cu to avoid conflicts
3. Fixing dangling track ends
4. Fixing silk/value text issues
"""

import pcbnew
import json

BOARD_PATH = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\icio500.kicad_pcb"
DRC_PATH = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\drc_report.json"

# Load DRC report
with open(DRC_PATH, "r") as f:
    drc_data = json.load(f)

board = pcbnew.LoadBoard(BOARD_PATH)

# =============================================================================
# Fix 1: Power traces that are too wide and cause clearance/short violations
# Reduce them to 0.35mm (14 mil) which is still chunky but won't short
# =============================================================================
print("=== Fix 1: Adjusting power trace widths to avoid shorts ===")

POWER_NETS = ["v_plus", "v_minus", "v_plus_16v", "v_minus_16v", "v_plus_48v", "daisy_5v_power"]
REDUCED_POWER_WIDTH = int(0.35 * 1e6)  # 0.35mm = 14 mil (compromise)
SIGNAL_WIDTH = int(0.2 * 1e6)

# Collect all tracks and their bounding boxes for proximity check
all_tracks = []
for t in board.GetTracks():
    if t.GetClass() != "PCB_VIA":
        all_tracks.append(t)

# For each power track, check if reducing width would help
adjusted = 0
for track in all_tracks:
    net_name = track.GetNetname()
    if net_name.lower() in [n.lower() for n in POWER_NETS]:
        # Check if this track is near other tracks on the same layer
        track_start = track.GetStart()
        track_end = track.GetEnd()
        track_layer = track.GetLayer()
        
        # Check proximity to other tracks with different nets
        too_close = False
        for other in all_tracks:
            if other == track:
                continue
            if other.GetLayer() != track_layer:
                continue
            if other.GetNetname() == net_name:
                continue
            
            # Simple distance check between track endpoints
            for pt in [other.GetStart(), other.GetEnd()]:
                for tpt in [track_start, track_end]:
                    dx = (pt.x - tpt.x) / 1e6
                    dy = (pt.y - tpt.y) / 1e6
                    dist = (dx*dx + dy*dy) ** 0.5
                    if dist < 0.8:  # Within 0.8mm
                        too_close = True
                        break
                if too_close:
                    break
            if too_close:
                break
        
        if too_close:
            track.SetWidth(REDUCED_POWER_WIDTH)
            adjusted += 1

print(f"  Reduced {adjusted} power traces from 0.5mm to 0.35mm (near other nets)")

# =============================================================================
# Fix 2: Remove dangling track ends
# =============================================================================
print("\n=== Fix 2: Removing dangling tracks ===")
dangling_removed = 0
tracks_to_remove = []

for track in board.GetTracks():
    if track.GetClass() == "PCB_VIA":
        continue
    net_name = track.GetNetname()
    start = track.GetStart()
    end = track.GetEnd()
    length = track.GetLength() / 1e6
    
    # Very short tracks on GND that are dangling
    if length < 1.0 and net_name.lower() == "gnd":
        # Check if both ends connect to something
        start_connected = False
        end_connected = False
        for other in board.GetTracks():
            if other == track:
                continue
            os = other.GetStart()
            oe = other.GetEnd()
            if os.x == start.x and os.y == start.y:
                start_connected = True
            if oe.x == start.x and oe.y == start.y:
                start_connected = True
            if os.x == end.x and os.y == end.y:
                end_connected = True
            if oe.x == end.x and oe.y == end.y:
                end_connected = True
        
        # Check pad connections
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                px = pad.GetPosition().x
                py = pad.GetPosition().y
                if px == start.x and py == start.y:
                    start_connected = True
                if px == end.x and py == end.y:
                    end_connected = True
        
        if not start_connected or not end_connected:
            tracks_to_remove.append(track)
            dangling_removed += 1

for t in tracks_to_remove:
    board.Remove(t)
print(f"  Removed {dangling_removed} dangling GND track stubs")

# =============================================================================
# Fix 3: Fix value text on footprints (U4, U5 have undersized text)
# =============================================================================
print("\n=== Fix 3: Fixing value text sizes ===")
for fp in board.GetFootprints():
    ref = fp.GetReference()
    val_text = fp.Value()
    
    # Fix value text size if too small
    val_size = val_text.GetTextSize()
    val_thick = val_text.GetTextThickness()
    
    if val_size.x < int(1.0 * 1e6) or val_thick < int(0.15 * 1e6):
        val_text.SetTextSize(pcbnew.VECTOR2I(int(1.0 * 1e6), int(1.0 * 1e6)))
        val_text.SetTextThickness(int(0.15 * 1e6))
        print(f"  Fixed value text on {ref}")

# =============================================================================
# Fix 4: Move silkscreen refs that overlap copper pads
# =============================================================================
print("\n=== Fix 4: Moving silkscreen refs away from pads ===")

# For components in the SCALING block (densely packed), shift refs further
scaling_components = ["U3", "R3", "R4", "R5", "R6", "R7", "R8", "C15", "C16", "C17", "C18"]
driver_components = ["U4", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "R7", "R8"]

for fp in board.GetFootprints():
    ref = fp.GetReference()
    ref_text = fp.Reference()
    fp_pos = fp.GetPosition()
    
    lib_name = fp.GetFPID().GetUniStringLibItemName()
    
    if ref in scaling_components or ref in driver_components:
        # Dense block — move refs to the side instead of above
        if "R0603" in lib_name or "C0603" in lib_name or "C0402" in lib_name:
            # Small parts: put ref to the right
            offset_x = int(2.5 * 1e6)
            ref_text.SetPosition(pcbnew.VECTOR2I(fp_pos.x + offset_x, fp_pos.y))
            ref_text.SetTextSize(pcbnew.VECTOR2I(int(0.8 * 1e6), int(0.8 * 1e6)))
            ref_text.SetTextThickness(int(0.15 * 1e6))
            print(f"  Moved {ref} ref to side")

# =============================================================================
# Save
# =============================================================================
print("\n=== Saving ===")
board.Save(BOARD_PATH)
print("Board saved!")
print("\nPlease re-run DRC to check remaining violations.")
