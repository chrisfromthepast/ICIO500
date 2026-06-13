import pcbnew
import sys

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

r3 = board.FindFootprintByReference("R3")
r3_p1 = r3.FindPadByNumber("1")
net_audio = r3_p1.GetNetCode()

c26 = board.FindFootprintByReference("C26")
c26_p2 = c26.FindPadByNumber("2")
net_gnd = c26_p2.GetNetCode()

r3_pos = r3_p1.GetPosition()
c26_pos = c26_p2.GetPosition()

to_delete = []

for track in board.Tracks():
    if track.GetNetCode() == net_audio:
        to_delete.append(track)

via4_pos_x = int(170.0 * 1e6)
via4_pos_y = int(92.225 * 1e6)

c26_x = c26_pos.x
c26_y = c26_pos.y

for track in board.Tracks():
    if track.GetNetCode() == net_gnd:
        start_x, start_y = track.GetStart().x, track.GetStart().y
        end_x, end_y = track.GetEnd().x, track.GetEnd().y
        
        if (abs(start_x - via4_pos_x) < 1000 and abs(start_y - via4_pos_y) < 1000) or \
           (abs(end_x - via4_pos_x) < 1000 and abs(end_y - via4_pos_y) < 1000) or \
           (abs(start_x - c26_x) < 1000 and abs(start_y - c26_y) < 1000) or \
           (abs(end_x - c26_x) < 1000 and abs(end_y - c26_y) < 1000):
            to_delete.append(track)
            
        via3_x = int(157.0 * 1e6)
        if abs(start_x - via3_x) < 1000 or abs(end_x - via3_x) < 1000:
            to_delete.append(track)

# deduplicate by m_Uuid
unique_items = {}
for item in to_delete:
    unique_items[item.m_Uuid.AsString()] = item

print(f"Deleting {len(unique_items)} items...")

for uuid, item in unique_items.items():
    board.Remove(item)

pcbnew.SaveBoard(board_path, board)
print("Saved pristine board.")
