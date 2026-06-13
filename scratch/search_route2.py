import os
import shutil
import subprocess
import pcbnew
import re

BOARD_CLEAN = 'build/icio500/icio500_clean.kicad_pcb'
BOARD_TEST = 'build/icio500/icio500.kicad_pcb'

def add_track(board, start, end, layer, net, width=0.25):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(pcbnew.VECTOR2I(int(start[0]*1e6), int(start[1]*1e6)))
    track.SetEnd(pcbnew.VECTOR2I(int(end[0]*1e6), int(end[1]*1e6)))
    track.SetWidth(pcbnew.FromMM(width))
    track.SetLayer(layer)
    track.SetNetCode(net)
    board.Add(track)

def add_via(board, pos, net):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(int(pos[0]*1e6), int(pos[1]*1e6)))
    via.SetWidth(pcbnew.FromMM(0.6))
    via.SetDrill(pcbnew.FromMM(0.3))
    via.SetNetCode(net)
    board.Add(via)

def check_drc():
    cmd = [
        r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe",
        "pcb", "drc",
        "--output", "drc_temp.txt",
        "icio500.kicad_pcb"
    ]
    if os.path.exists("build/icio500/drc_temp.txt"):
        os.remove("build/icio500/drc_temp.txt")
        
    subprocess.run(cmd, cwd="build/icio500", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    with open("build/icio500/drc_temp.txt", "r", encoding="utf-8") as f:
        content = f.read()
        
    v_match = re.search(r"Found (\d+) DRC violations", content)
    u_match = re.search(r"Found (\d+) unconnected", content)
    v = int(v_match.group(1)) if v_match else 999
    u = int(u_match.group(1)) if u_match else 999
    return v, u

def test_offsets(audio_y_offset, zobel_y_offset):
    shutil.copy(BOARD_CLEAN, BOARD_TEST)
    board = pcbnew.LoadBoard(BOARD_TEST)
    
    c26 = board.FindFootprintByReference("C26")
    c26_p2 = c26.FindPadByNumber("2")
    net_gnd = c26_p2.GetNetCode()
    add_via(board, (c26_p2.GetPosition().x/1e6, c26_p2.GetPosition().y/1e6), net_gnd)
    
    # Actually, we don't need to manually route the GND via to another pad!
    # Because dropping a via at C26 pad 2 and 174.3 DOES connect to the inner ground planes!
    # Wait, the inner ground plane isn't updated unless we refill!
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    
    r3 = board.FindFootprintByReference("R3")
    u2 = board.FindFootprintByReference("U2")
    r3_p1 = r3.FindPadByNumber("1")
    u2_p7 = u2.FindPadByNumber("7")
    net_audio = r3_p1.GetNetCode()
    
    r3_pos = (r3_p1.GetPosition().x/1e6, r3_p1.GetPosition().y/1e6)
    u2_pos = (u2_p7.GetPosition().x/1e6, u2_p7.GetPosition().y/1e6)
    
    if audio_y_offset is not None:
        v1 = (r3_pos[0], r3_pos[1] + audio_y_offset)
        v2 = (u2_pos[0] + 1.2, u2_pos[1])
        add_track(board, r3_pos, v1, pcbnew.F_Cu, net_audio)
        add_via(board, v1, net_audio)
        add_track(board, u2_pos, v2, pcbnew.F_Cu, net_audio)
        add_via(board, v2, net_audio)
        pts1 = [v1, (164.5, v1[1]), (164.5, v2[1]), v2]
        for i in range(3): add_track(board, pts1[i], pts1[i+1], pcbnew.B_Cu, net_audio)

    c26_p1 = c26.FindPadByNumber("1")
    r8 = board.FindFootprintByReference("R8")
    r8_p2 = r8.FindPadByNumber("2")
    net_zobel = c26_p1.GetNetCode()
    
    c26_pos = (c26_p1.GetPosition().x/1e6, c26_p1.GetPosition().y/1e6)
    r8_pos = (r8_p2.GetPosition().x/1e6, r8_p2.GetPosition().y/1e6)
    
    if zobel_y_offset is not None:
        v3 = (c26_pos[0], c26_pos[1] + zobel_y_offset)
        v4 = (r8_pos[0] + 1.2, r8_pos[1])
        add_track(board, c26_pos, v3, pcbnew.F_Cu, net_zobel)
        add_via(board, v3, net_zobel)
        add_track(board, r8_pos, v4, pcbnew.F_Cu, net_zobel)
        add_via(board, v4, net_zobel)
        pts2 = [v3, (168.0, v3[1]), (168.0, v4[1]), v4]
        for i in range(3): add_track(board, pts2[i], pts2[i+1], pcbnew.B_Cu, net_zobel)
    
    pcbnew.SaveBoard(BOARD_TEST, board)
    return check_drc()

def main():
    board = pcbnew.LoadBoard(BOARD_CLEAN)
    pcbnew.SaveBoard(BOARD_TEST, board)
    
    base_v, base_u = check_drc()
    print(f"Baseline: {base_v} violations, {base_u} unconnected")
    
    best_audio = None
    best_audio_v = 999
    
    # We know from find_channels that ~ -2.0 is 84.0 (since R3 is at 86.0)
    audio_offsets = [i*0.5 for i in range(-5, 6)]
    for ao in audio_offsets:
        v, u = test_offsets(ao, None)
        print(f"Testing audio {ao}: {v} violations")
        if v < best_audio_v:
            best_audio_v = v
            best_audio = ao
            if v <= base_v: break
            
    print(f"Best audio offset: {best_audio} -> {best_audio_v} violations")
    
    if best_audio is None:
        return
        
    best_zobel = None
    best_zobel_v = 999
    
    zobel_offsets = [i*0.5 for i in range(-5, 6)]
    for zo in zobel_offsets:
        v, u = test_offsets(best_audio, zo)
        print(f"Testing zobel {zo}: {v} violations")
        if v < best_zobel_v:
            best_zobel_v = v
            best_zobel = zo
        if v <= base_v and u == 0:
            print("Found PERFECT route!")
            break
            
    print(f"Final routing with Audio: {best_audio}, Zobel: {best_zobel}")
    v, u = test_offsets(best_audio, best_zobel)
    print(f"Final DRC: {v} violations, {u} unconnected")

if __name__ == '__main__':
    main()
