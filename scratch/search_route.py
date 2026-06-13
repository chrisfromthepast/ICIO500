import subprocess
import re
import os
import pcbnew
import shutil

offsets = [round(x * 0.5, 1) for x in range(-16, 17)]

board_path = 'build/icio500/icio500.kicad_pcb'
backup_path = 'build/icio500/icio500.kicad_pcb.bak'

# force fresh backup
if os.path.exists(backup_path):
    os.remove(backup_path)
shutil.copy(board_path, backup_path)

def route_with_offset(y_offset_r3, y_offset_c26):
    shutil.copy(backup_path, board_path)
    board = pcbnew.LoadBoard(board_path)
    
    def add_track(start, end, layer, net, width=0.25):
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I(int(start[0]*1e6), int(start[1]*1e6)))
        track.SetEnd(pcbnew.VECTOR2I(int(end[0]*1e6), int(end[1]*1e6)))
        track.SetWidth(pcbnew.FromMM(width))
        track.SetLayer(layer)
        track.SetNetCode(net)
        board.Add(track)

    def add_via(pos, net):
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pcbnew.VECTOR2I(int(pos[0]*1e6), int(pos[1]*1e6)))
        via.SetWidth(pcbnew.FromMM(0.6))
        via.SetDrill(pcbnew.FromMM(0.3))
        via.SetNetCode(net)
        board.Add(via)

    r3 = board.FindFootprintByReference("R3")
    u2 = board.FindFootprintByReference("U2")
    r3_p1 = r3.FindPadByNumber("1")
    u2_p7 = u2.FindPadByNumber("7")
    net_audio = r3_p1.GetNetCode()
    
    r3_pos = (r3_p1.GetPosition().x/1e6, r3_p1.GetPosition().y/1e6)
    u2_pos = (u2_p7.GetPosition().x/1e6, u2_p7.GetPosition().y/1e6)
    
    via1_pos = (r3_pos[0], r3_pos[1] + y_offset_r3)
    via2_pos = (u2_pos[0] + 1.2, u2_pos[1])
    
    add_track(r3_pos, via1_pos, pcbnew.F_Cu, net_audio)
    add_track(u2_pos, via2_pos, pcbnew.F_Cu, net_audio)
    
    add_via(via1_pos, net_audio)
    add_via(via2_pos, net_audio)
    
    pts_audio = [via1_pos, (164.5, via1_pos[1]), (164.5, via2_pos[1]), via2_pos]
    for i in range(len(pts_audio)-1):
        add_track(pts_audio[i], pts_audio[i+1], pcbnew.B_Cu, net_audio)
        
    c26 = board.FindFootprintByReference("C26")
    c26_p2 = c26.FindPadByNumber("2")
    net_gnd = c26_p2.GetNetCode()
    
    c26_pos = (c26_p2.GetPosition().x/1e6, c26_p2.GetPosition().y/1e6)
    via3_pos = (c26_pos[0], c26_pos[1] + y_offset_c26)
    via4_pos = (170.0, 92.225)
    
    add_track(c26_pos, via3_pos, pcbnew.F_Cu, net_gnd)
    
    add_via(via3_pos, net_gnd)
    add_via(via4_pos, net_gnd)
    
    pts_gnd = [via3_pos, (161.0, via3_pos[1]), (161.0, via4_pos[1]), via4_pos]
    for i in range(len(pts_gnd)-1):
        add_track(pts_gnd[i], pts_gnd[i+1], pcbnew.B_Cu, net_gnd)

    pcbnew.SaveBoard(board_path, board)

def check_drc():
    if os.path.exists("build/icio500/drc_report.txt"):
        os.remove("build/icio500/drc_report.txt")
        
    cmd = [
        r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe",
        "pcb", "drc",
        "--output", "drc_report.txt",
        "icio500.kicad_pcb" # FIXED: Path relative to cwd
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd="build/icio500")
    
    violations = 999
    unconnected = 999
    
    try:
        with open("build/icio500/drc_report.txt", "r") as f:
            content = f.read()
            v_match = re.search(r"Found (\d+) DRC violations", content)
            u_match = re.search(r"Found (\d+) unconnected pads", content)
            if v_match: violations = int(v_match.group(1))
            if u_match: unconnected = int(u_match.group(1))
    except:
        pass
    
    return violations, unconnected

print("Starting automated routing search...")
shutil.copy(backup_path, board_path)
v_base, u_base = check_drc()
print(f"Baseline: {v_base} violations, {u_base} unconnected")

best_r3 = 0
best_v = 999
print("Searching R3 offsets...")
for y in offsets:
    if -0.8 < y < 0.8: continue
    route_with_offset(y, 10.0)
    v, u = check_drc()
    if v < best_v:
        best_v = v
        best_r3 = y
    if v <= v_base + 1:
        best_r3 = y
        break

print(f"Best R3 offset: {best_r3}")

best_c26 = 0
best_v = 999
print("Searching C26 offsets...")
for y in offsets:
    if -0.8 < y < 0.8: continue
    route_with_offset(best_r3, y)
    v, u = check_drc()
    if v < best_v:
        best_v = v
        best_c26 = y
    if v <= v_base and u == 0:
        best_c26 = y
        print(f"Found perfect offset! R3: {best_r3}, C26: {best_c26}")
        break

print(f"\nFinal routing with R3: {best_r3}, C26: {best_c26}")
route_with_offset(best_r3, best_c26)
v, u = check_drc()
print(f"Final DRC: {v} violations, {u} unconnected")
