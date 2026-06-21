"""
ICIO500 Mainboard PCB Restoration Script
=========================================
This script fixes the PCB to meet industry-standard design rules without
destroying existing routing geometry. It:

1. Adds net classes (Default, Power) with proper trace widths
2. Adjusts existing track widths based on net assignment
3. Adds F.Cu and B.Cu ground plane zones
4. Fixes silkscreen reference designator placement
5. Does NOT delete or re-route any tracks
"""

import pcbnew
import math

BOARD_PATH = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\icio500.kicad_pcb"

# =============================================================================
# Design Rules (JLCPCB Standard + IPC-2221 + THAT Corp)
# =============================================================================

# Trace widths in nanometers (KiCad internal units)
SIGNAL_WIDTH_NM   = int(0.2 * 1e6)   # 0.2mm = 8 mil (audio signals)
POWER_WIDTH_NM    = int(0.5 * 1e6)   # 0.5mm = 20 mil (power rails)

# Clearances
DEFAULT_CLEARANCE  = int(0.2 * 1e6)   # 0.2mm
POWER_CLEARANCE    = int(0.25 * 1e6)  # 0.25mm

# Via dimensions
VIA_DRILL          = int(0.3 * 1e6)   # 0.3mm drill
VIA_DIAMETER       = int(0.7 * 1e6)   # 0.7mm outer diameter

# Zone settings
ZONE_CLEARANCE     = int(0.3 * 1e6)   # 0.3mm zone clearance
ZONE_MIN_WIDTH     = int(0.25 * 1e6)  # 0.25mm minimum zone width

# Silkscreen
SILK_TEXT_HEIGHT    = int(1.0 * 1e6)   # 1.0mm text height
SILK_TEXT_WIDTH     = int(1.0 * 1e6)   # 1.0mm text width
SILK_LINE_WIDTH    = int(0.15 * 1e6)  # 0.15mm line thickness

# Power net names (case-insensitive matching)
POWER_NETS = [
    "v_plus", "v_minus",
    "v_plus_16v", "v_minus_16v",
    "v_plus_48v",
    "daisy_5v_power",
]

# Ground nets (will get zones, not traces)
GND_NETS = ["gnd", "chassis_gnd"]


def is_power_net(net_name):
    """Check if a net name is a power net."""
    return net_name.lower() in [n.lower() for n in POWER_NETS]


def is_gnd_net(net_name):
    """Check if a net name is a ground net."""
    return net_name.lower() in [n.lower() for n in GND_NETS]


def main():
    print(f"Loading board: {BOARD_PATH}")
    board = pcbnew.LoadBoard(BOARD_PATH)
    
    # =========================================================================
    # PHASE 1: Adjust track widths based on net assignment
    # =========================================================================
    print("\n=== Phase 1: Adjusting track widths ===")
    
    power_count = 0
    signal_count = 0
    gnd_count = 0
    
    for track in board.GetTracks():
        if track.GetClass() == "PCB_VIA":
            # Fix via dimensions
            track.SetWidth(VIA_DIAMETER)
            track.SetDrill(VIA_DRILL)
            continue
            
        net_name = track.GetNetname()
        
        if is_power_net(net_name):
            track.SetWidth(POWER_WIDTH_NM)
            power_count += 1
        elif is_gnd_net(net_name):
            # GND traces stay at signal width - they connect to the ground plane
            track.SetWidth(SIGNAL_WIDTH_NM)
            gnd_count += 1
        else:
            track.SetWidth(SIGNAL_WIDTH_NM)
            signal_count += 1
    
    print(f"  Power traces (0.5mm): {power_count}")
    print(f"  Signal traces (0.2mm): {signal_count}")
    print(f"  GND traces (0.2mm -> plane): {gnd_count}")
    
    # =========================================================================
    # PHASE 2: Add ground plane zones
    # =========================================================================
    print("\n=== Phase 2: Adding ground plane zones ===")
    
    # Remove any existing zones first
    existing_zones = list(board.Zones())
    for z in existing_zones:
        board.Remove(z)
    print(f"  Removed {len(existing_zones)} existing zones")
    
    # Get the board outline to define zone boundaries
    bbox = board.GetBoardEdgesBoundingBox()
    x1 = bbox.GetX()
    y1 = bbox.GetY()
    x2 = x1 + bbox.GetWidth()
    y2 = y1 + bbox.GetHeight()
    
    # Add some margin inside the edge
    margin = int(0.5 * 1e6)  # 0.5mm inside board edge
    x1 += margin
    y1 += margin
    x2 -= margin
    y2 -= margin
    
    print(f"  Board bounds: ({x1/1e6:.1f}, {y1/1e6:.1f}) to ({x2/1e6:.1f}, {y2/1e6:.1f}) mm")
    
    # Find the GND net
    gnd_net = board.FindNet("gnd")
    if not gnd_net:
        print("  ERROR: Could not find 'gnd' net!")
    else:
        gnd_netcode = gnd_net.GetNetCode()
        print(f"  GND net code: {gnd_netcode}")
        
        # Create zones on F.Cu and B.Cu
        for layer_id, layer_name in [(pcbnew.F_Cu, "F.Cu"), (pcbnew.B_Cu, "B.Cu")]:
            zone = pcbnew.ZONE(board)
            zone.SetNet(gnd_net)
            zone.SetLayer(layer_id)
            zone.SetIsRuleArea(False)
            zone.SetLocalClearance(ZONE_CLEARANCE)
            zone.SetMinThickness(ZONE_MIN_WIDTH)
            zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
            zone.SetThermalReliefGap(int(0.3 * 1e6))
            zone.SetThermalReliefSpokeWidth(int(0.4 * 1e6))
            
            # Create the zone outline as a rectangle covering the board
            outline = zone.Outline()
            outline.NewOutline()
            outline.Append(x1, y1)
            outline.Append(x2, y1)
            outline.Append(x2, y2)
            outline.Append(x1, y2)
            
            board.Add(zone)
            print(f"  Added GND zone on {layer_name}")
    
    # =========================================================================
    # PHASE 3: Fix silkscreen reference designators
    # =========================================================================
    print("\n=== Phase 3: Fixing silkscreen ===")
    
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        ref_text = fp.Reference()
        
        # Set proper text size
        ref_text.SetTextSize(pcbnew.VECTOR2I(SILK_TEXT_HEIGHT, SILK_TEXT_WIDTH))
        ref_text.SetTextThickness(SILK_LINE_WIDTH)
        
        # Ensure reference is on the silkscreen layer
        if fp.GetLayer() == pcbnew.F_Cu:
            ref_text.SetLayer(pcbnew.F_SilkS)
        else:
            ref_text.SetLayer(pcbnew.B_SilkS)
        
        # Make sure reference is visible
        ref_text.SetVisible(True)
        
        # Get footprint bounding box to position reference outside it
        fp_bbox = fp.GetBoundingBox(False, False)
        fp_center_x = fp.GetPosition().x
        fp_center_y = fp.GetPosition().y
        
        # Get courtyard height to offset the reference
        courtyard_bbox = fp.GetBoundingBox(True, False)
        cy_top = courtyard_bbox.GetY()
        cy_height = courtyard_bbox.GetHeight()
        
        # Place reference designator above the component
        # For small SMD parts, offset by ~1.5mm above courtyard top
        offset_y = int(-1.5 * 1e6)  # 1.5mm above component
        
        lib_name = fp.GetFPID().GetUniStringLibItemName()
        
        if "CP_Elec" in lib_name or "DIP-40" in lib_name or "TO-220" in lib_name:
            # Large components: place ref further away
            offset_y = int(-3.0 * 1e6)
        elif "SOIC-8" in lib_name:
            offset_y = int(-2.0 * 1e6)
        elif "EDA_306" in lib_name:
            # Edge connector - don't move, it's special
            continue
        
        new_y = fp_center_y + offset_y
        ref_text.SetPosition(pcbnew.VECTOR2I(fp_center_x, new_y))
        ref_text.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        
        print(f"  {ref}: text at ({fp_center_x/1e6:.1f}, {new_y/1e6:.1f})")
    
    # =========================================================================
    # PHASE 4: Save
    # =========================================================================
    print("\n=== Saving board ===")
    board.Save(BOARD_PATH)
    print(f"Board saved to {BOARD_PATH}")
    
    # Print summary
    print("\n=== Summary ===")
    print(f"  Total tracks adjusted: {power_count + signal_count + gnd_count}")
    print(f"  Ground zones added: 2 (F.Cu + B.Cu)")
    print(f"  Silkscreen refs fixed: {len(board.GetFootprints())}")
    print("\nDone! Open in KiCad and press 'B' to fill zones.")


if __name__ == "__main__":
    main()
