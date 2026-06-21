import pcbnew
import json
import sys

board_path = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\icio500.kicad_pcb"
env_path = r"C:\Users\Chris Williams\Documents\GitHub\ICIO500\build\icio500\routing_env.json"

CHUNKY_SIGNAL_WIDTH = int(0.8 * 1e6)
CHUNKY_POWER_WIDTH = int(1.5 * 1e6)

POWER_NETS = ["+16V", "-16V", "+48V", "GND", "v_plus", "v_minus", "gnd"]

try:
    board = pcbnew.LoadBoard(board_path)
    
    # 1. Rip up existing tracks
    for track in board.GetTracks():
        board.Remove(track)
        
    print("Cleared existing tracks.")

    # 2. Load the previously calculated routing points
    with open(env_path, "r") as f:
        routing_data = json.load(f)
        
    print(f"Loaded {len(routing_data)} routing elements.")
    
    # 3. Apply chunky tracks
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
                    print(f"Warning: No GetNetCode on {net_name}")
            else:
                print(f"Warning: Net {net_name} not found.")
                    
            # Create the track
            track = pcbnew.PCB_TRACK(board)
            track.SetStart(pcbnew.VECTOR2I(int(sx * 1e6), int(sy * 1e6)))
            track.SetEnd(pcbnew.VECTOR2I(int(ex * 1e6), int(ey * 1e6)))
            
            # Set Layer
            layer_id = board.GetLayerID(layer_name)
            if layer_id != pcbnew.UNDEFINED_LAYER:
                track.SetLayer(layer_id)
            else:
                track.SetLayer(pcbnew.F_Cu)

            # Set Chunky Width!
            width = CHUNKY_SIGNAL_WIDTH
            if any(p.lower() in net_name.lower() for p in POWER_NETS):
                width = CHUNKY_POWER_WIDTH
                
            track.SetWidth(width)
            if net_code != 0:
                track.SetNetCode(net_code)
            
            board.Add(track)
            track_count += 1

    board.Save(board_path)
    print(f"Successfully routed {track_count} extremely chunky tracks! Board saved.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
