import pcbnew
import json
import sys

board_path = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\icio500.kicad_pcb"
env_path = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\routing_env.json"

# Industry Standard Widths
STD_SIGNAL_WIDTH = int(0.254 * 1e6)  # 10 mil
STD_POWER_WIDTH = int(0.508 * 1e6)   # 20 mil

POWER_NETS = ["+16V", "-16V", "+48V", "v_plus", "v_minus"]

try:
    board = pcbnew.LoadBoard(board_path)
    
    # Do not rip up existing tracks! (Preserve user's manual routing)
    
    print("Adding inter-module tracks without clearing existing ones.")

    # 2. Load the previously calculated routing points
    with open(env_path, "r") as f:
        routing_data = json.load(f)
    
    # 3. Apply Standard Tracks
    track_count = 0
    for item in routing_data:
        if item.get("type") == "track":
            net_name = item.get("net", "")
            sx, sy = item["sx"], item["sy"]
            ex, ey = item["ex"], item["ey"]
            layer_name = item.get("layer", "F.Cu")
            
            net_code = 0
            net_item = board.FindNet(net_name)
            if net_item:
                try:
                    net_code = int(net_item.GetNetCode())
                except AttributeError:
                    pass
                    
            # Skip GND tracks because we are doing full copper pours
            if net_name.lower() in ["gnd", "chassis_gnd"]:
                continue

            track = pcbnew.PCB_TRACK(board)
            track.SetStart(pcbnew.VECTOR2I(int(sx * 1e6), int(sy * 1e6)))
            track.SetEnd(pcbnew.VECTOR2I(int(ex * 1e6), int(ey * 1e6)))
            
            layer_id = board.GetLayerID(layer_name)
            if layer_id != pcbnew.UNDEFINED_LAYER:
                track.SetLayer(layer_id)
            else:
                track.SetLayer(pcbnew.F_Cu)

            width = STD_SIGNAL_WIDTH
            if any(p.lower() in net_name.lower() for p in POWER_NETS):
                width = STD_POWER_WIDTH
                
            track.SetWidth(width)
            if net_code != 0:
                try:
                    track.SetNetCode(int(net_code))
                except Exception:
                    pass
            
            board.Add(track)
            track_count += 1

    board.Save(board_path)
    print(f"Successfully routed {track_count} standard tracks! Board saved.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
