import pcbnew

board = pcbnew.LoadBoard('build/icio500/panel_satellite.kicad_pcb')
b_cu = board.GetLayerID('B.Cu')
f_cu = board.GetLayerID('F.Cu')

def add_track(start, end, layer, net_code):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(pcbnew.VECTOR2I_MM(start[0], start[1]))
    track.SetEnd(pcbnew.VECTOR2I_MM(end[0], end[1]))
    track.SetWidth(pcbnew.FromMM(0.3))
    track.SetLayer(layer)
    track.SetNetCode(net_code)
    board.Add(track)

def add_via(pos, net_code):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I_MM(pos[0], pos[1]))
    via.SetWidth(pcbnew.FromMM(0.8))
    via.SetDrill(pcbnew.FromMM(0.4))
    via.SetNetCode(net_code)
    board.Add(via)

def route_resistor_to_led(r_ref, d_ref, net_name):
    net = board.GetNetcodeFromNetname(net_name)
    if net <= 0:
        print(f"Net {net_name} not found")
        return
    
    r = board.FindFootprintByReference(r_ref)
    d = board.FindFootprintByReference(d_ref)
    
    r_pad = r.FindPadByNumber("1")
    d_pad = d.FindPadByNumber("2")
    
    rx = r_pad.GetPosition().x / 1000000.0
    ry = r_pad.GetPosition().y / 1000000.0
    
    dx = d_pad.GetPosition().x / 1000000.0
    dy = d_pad.GetPosition().y / 1000000.0
    
    via_x = dx - 1.5
    via_y = dy
    
    add_track((rx, ry), (rx, via_y), b_cu, net)
    add_track((rx, via_y), (via_x, via_y), b_cu, net)
    add_via((via_x, via_y), net)
    add_track((via_x, via_y), (dx, dy), f_cu, net)

# Route the LED MIDs
route_resistor_to_led("R6", "D6", "LED_6_MID")
route_resistor_to_led("R7", "D7", "LED_7_MID")
route_resistor_to_led("R8", "D8", "LED_8_MID")
route_resistor_to_led("R9", "D9", "LED_9_MID")
route_resistor_to_led("R10", "D10", "LED_10_MID")

# Route GND for D8 Pad 1 (D8 pad 1 to D7 pad 1 which is already GND)
d8 = board.FindFootprintByReference("D8")
d7 = board.FindFootprintByReference("D7")
gnd_net = board.GetNetcodeFromNetname("GND")
d8_p1 = d8.FindPadByNumber("1")
d7_p1 = d7.FindPadByNumber("1")
x1, y1 = d8_p1.GetPosition().x / 1e6, d8_p1.GetPosition().y / 1e6
x2, y2 = d7_p1.GetPosition().x / 1e6, d7_p1.GetPosition().y / 1e6
add_track((x1, y1), (x2, y2), f_cu, gnd_net)

pcbnew.SaveBoard('build/icio500/panel_satellite.kicad_pcb', board)
print("Routing completed.")

