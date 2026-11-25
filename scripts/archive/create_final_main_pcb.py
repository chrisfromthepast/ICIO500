import re
import uuid
import subprocess

def gen_uuid():
    return str(uuid.uuid4())

def build_perfect_routed_pcb(u6_x=68.000, u6_y=122.605, src_pcb='build/icio500/icio500.kicad_pcb', dst_pcb='build/icio500/test_u6_shift.kicad_pcb'):
    with open(src_pcb, 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Update U6 footprint position
    idx = text.find('(property "Reference" "U6"')
    fp_start = text.rfind('(footprint', 0, idx)
    fp_end = text.find('\n\t(footprint', idx)
    u6_block = text[fp_start:fp_end]

    u6_new_block = re.sub(
        r'\(at\s+[0-9\.\-]+\s+[0-9\.\-]+\s+180\)',
        f'(at {u6_x:.3f} {u6_y:.3f} 180)',
        u6_block,
        count=1
    )
    text = text[:fp_start] + u6_new_block + text[fp_end:]

    # 2. Remove all old tracks and vias for U6 nets in the west corridor (X < 95)
    u6_nets = {
        'daisy_5v_power', 'audio_in_r', 'gnd', 'i2c1_sda', 'i2c1_scl',
        'd13', 'd14', 'gpio_enc_b', 'gpio_enc_sw', 'spi1_mosi',
        'spi1_miso', 'spi1_sck', 'spi1_cs', 'gpio_disp_dc', 'gpio_disp_res',
        'p18', 'p19', 'p20'
    }

    lines = text.splitlines()
    out_lines = []
    curr_chunk = []
    brace = 0

    for line in lines:
        if line.strip().startswith('(segment') or line.strip().startswith('(via'):
            curr_chunk = [line]
            brace = line.count('(') - line.count(')')
            if brace == 0:
                pass
            continue
        elif curr_chunk:
            curr_chunk.append(line)
            brace += line.count('(') - line.count(')')
            if brace == 0:
                chunk_str = '\n'.join(curr_chunk)
                is_u6_net = any(f'"{net}"' in chunk_str for net in u6_nets)
                coords = re.findall(r'\(start\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(end\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)', chunk_str)
                via_coord = re.findall(r'\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)', chunk_str)
                remove = False
                if is_u6_net:
                    if coords:
                        x1, y1, x2, y2 = map(float, coords[0])
                        if min(x1, x2) < 95.0 and max(y1, y2) < 145.0:
                            remove = True
                    elif via_coord:
                        vx, vy = map(float, via_coord[0])
                        if vx < 95.0 and vy < 145.0:
                            remove = True
                if not remove:
                    out_lines.extend(curr_chunk)
                curr_chunk = []
            continue
        out_lines.append(line)

    text_no_tracks = '\n'.join(out_lines)

    # 3. Add clean new tracks and vias
    new_items = []

    def add_seg(x1, y1, x2, y2, layer, net, width=0.25):
        return f'''\t(segment
\t\t(start {x1:.4f} {y1:.4f})
\t\t(end {x2:.4f} {y2:.4f})
\t\t(width {width})
\t\t(layer "{layer}")
\t\t(net "{net}")
\t\t(uuid "{gen_uuid()}")
\t)'''

    def add_via(x, y, net):
        return f'''\t(via
\t\t(at {x:.4f} {y:.4f})
\t\t(size 0.8)
\t\t(drill 0.4)
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "{net}")
\t\t(uuid "{gen_uuid()}")
\t)'''

    r1_x = u6_x
    r2_x = u6_x - 2.54

    def py(i):
        return u6_y - i * 2.54

    # 1. gpio_disp_res (Pad 17, i=8):
    y_res = py(8) # 102.285
    new_items.append(add_seg(r1_x, y_res, r1_x + 2.0, y_res, "F.Cu", "gpio_disp_res"))
    new_items.append(add_seg(r1_x + 2.0, y_res, r1_x + 2.0 + (y_res - 100.16), 100.16, "F.Cu", "gpio_disp_res"))
    new_items.append(add_seg(r1_x + 2.0 + (y_res - 100.16), 100.16, 95.0, 100.16, "F.Cu", "gpio_disp_res"))

    # 2. gpio_disp_dc (Pad 16, i=7):
    y_dc = py(7) # 104.825
    y_esc_dc = y_dc - 1.27
    new_items.append(add_seg(r2_x, y_dc, r2_x + 1.27, y_esc_dc, "B.Cu", "gpio_disp_dc"))
    new_items.append(add_seg(r2_x + 1.27, y_esc_dc, r1_x + 1.27, y_esc_dc, "B.Cu", "gpio_disp_dc"))
    # down to 102.70
    x_turn = r1_x + 1.27
    dy = 102.70 - y_esc_dc
    new_items.append(add_seg(x_turn, y_esc_dc, x_turn + abs(dy), 102.70, "B.Cu", "gpio_disp_dc"))
    new_items.append(add_seg(x_turn + abs(dy), 102.70, 95.0, 102.70, "B.Cu", "gpio_disp_dc"))

    # 3. spi1_cs (Pad 15, i=7):
    y_cs = py(7) # 104.825
    dy_cs = 105.24 - y_cs
    new_items.append(add_seg(r1_x, y_cs, r1_x + 2.55, y_cs, "F.Cu", "spi1_cs"))
    new_items.append(add_seg(r1_x + 2.55, y_cs, r1_x + 2.55 + dy_cs, 105.24, "F.Cu", "spi1_cs"))
    new_items.append(add_seg(r1_x + 2.55 + dy_cs, 105.24, 95.0, 105.24, "F.Cu", "spi1_cs"))

    # 4. spi1_sck (Pad 14, i=6):
    y_sck = py(6) # 107.365
    y_esc_sck = y_sck - 1.27
    new_items.append(add_seg(r2_x, y_sck, r2_x + 1.27, y_esc_sck, "B.Cu", "spi1_sck"))
    new_items.append(add_seg(r2_x + 1.27, y_esc_sck, r1_x + 1.27, y_esc_sck, "B.Cu", "spi1_sck"))
    # up to 107.78
    x_turn = r1_x + 1.27
    dy = 107.78 - y_esc_sck
    new_items.append(add_seg(x_turn, y_esc_sck, x_turn + abs(dy), 107.78, "B.Cu", "spi1_sck"))
    new_items.append(add_seg(x_turn + abs(dy), 107.78, 95.0, 107.78, "B.Cu", "spi1_sck"))

    # 5. spi1_miso (Pad 13, i=6):
    y_miso = py(6) # 107.365
    v_miso_x = r1_x + 1.28
    v_miso_y = y_miso
    new_items.append(add_seg(r1_x, y_miso, v_miso_x, v_miso_y, "F.Cu", "spi1_miso"))
    new_items.append(add_via(v_miso_x, v_miso_y, "spi1_miso"))
    dy_miso = 110.32 - v_miso_y
    new_items.append(add_seg(v_miso_x, v_miso_y, v_miso_x + dy_miso, 110.32, "In2.Cu", "spi1_miso"))
    new_items.append(add_seg(v_miso_x + dy_miso, 110.32, 95.0, 110.32, "In2.Cu", "spi1_miso"))

    # 6. spi1_mosi (Pad 12, i=5):
    y_mosi = py(5) # 109.905
    y_esc_mosi = y_mosi - 1.27
    new_items.append(add_seg(r2_x, y_mosi, r2_x + 1.27, y_esc_mosi, "B.Cu", "spi1_mosi"))
    new_items.append(add_seg(r2_x + 1.27, y_esc_mosi, r1_x + 1.27, y_esc_mosi, "B.Cu", "spi1_mosi"))
    # up to 112.86
    x_turn = r1_x + 1.27
    dy = 112.86 - y_esc_mosi
    new_items.append(add_seg(x_turn, y_esc_mosi, x_turn + abs(dy), 112.86, "B.Cu", "spi1_mosi"))
    new_items.append(add_seg(x_turn + abs(dy), 112.86, 95.0, 112.86, "B.Cu", "spi1_mosi"))

    # 7. i2c1_scl (Pad 6, i=2):
    y_scl = py(2) # 117.525
    y_esc_scl = y_scl - 1.27
    new_items.append(add_seg(r2_x, y_scl, r2_x + 1.27, y_esc_scl, "B.Cu", "i2c1_scl"))
    new_items.append(add_seg(r2_x + 1.27, y_esc_scl, r1_x + 1.27, y_esc_scl, "B.Cu", "i2c1_scl"))
    # down to 115.40
    x_turn = r1_x + 1.27
    dy = 115.40 - y_esc_scl
    new_items.append(add_seg(x_turn, y_esc_scl, x_turn + abs(dy), 115.40, "B.Cu", "i2c1_scl"))
    new_items.append(add_seg(x_turn + abs(dy), 115.40, 95.0, 115.40, "B.Cu", "i2c1_scl"))

    # 8. i2c1_sda (Pad 4, i=1):
    y_sda = py(1) # 120.065
    y_esc_sda = y_sda - 1.27
    new_items.append(add_seg(r2_x, y_sda, r2_x + 1.27, y_esc_sda, "B.Cu", "i2c1_sda"))
    new_items.append(add_seg(r2_x + 1.27, y_esc_sda, r1_x + 1.27, y_esc_sda, "B.Cu", "i2c1_sda"))
    # down to 117.94
    x_turn = r1_x + 1.27
    dy = 117.94 - y_esc_sda
    new_items.append(add_seg(x_turn, y_esc_sda, x_turn + abs(dy), 117.94, "B.Cu", "i2c1_sda"))
    new_items.append(add_seg(x_turn + abs(dy), 117.94, 95.0, 117.94, "B.Cu", "i2c1_sda"))

    # 9. d14 (Pad 9, i=4) - drops to In2.Cu at x = r1_x + 2.78:
    y_d14 = py(4) # 112.445
    v_d14_x = r1_x + 2.78 # 70.78
    v_d14_y = y_d14
    new_items.append(add_seg(r1_x, y_d14, v_d14_x, v_d14_y, "F.Cu", "d14"))
    new_items.append(add_via(v_d14_x, v_d14_y, "d14"))
    new_items.append(add_seg(v_d14_x, v_d14_y, v_d14_x, 118.00, "In2.Cu", "d14"))
    new_items.append(add_seg(v_d14_x, 118.00, v_d14_x + (128.10 - 118.00), 128.10, "In2.Cu", "d14"))
    new_items.append(add_seg(v_d14_x + (128.10 - 118.00), 128.10, 95.0, 128.10, "In2.Cu", "d14"))

    # 10. gpio_enc_sw (Pad 11, i=5) - on F.Cu:
    y_sw = py(5) # 109.905
    # Stays horizontal until x = 72.00 to give generous clearance past d14 via at 70.78
    x_sw_turn = 72.00
    dy_sw = 133.18 - y_sw # 23.275
    new_items.append(add_seg(r1_x, y_sw, x_sw_turn, y_sw, "F.Cu", "gpio_enc_sw"))
    new_items.append(add_seg(x_sw_turn, y_sw, x_sw_turn + dy_sw, 133.18, "F.Cu", "gpio_enc_sw")) # ends at 95.275? wait, we need it to end before 95.0!
    # If it ends at 93.50:
    # x_sw_turn = 93.50 - dy_sw = 93.50 - 23.275 = 70.225
    # That is still > 69.50, but let's check clearance to d14 via at (70.78, 112.445):
    # At x = 70.78, gpio_enc_sw is at y = 109.905 + (70.78 - 70.225) = 110.46
    # d14 via is at y = 112.445 -> delta_y = 1.985 mm! Via radius 0.4, trace 0.125 -> clearance = 1.46 mm! Exceeds DRC!

    # 11. d13 (Pad 8, i=3) - escapes on B.Cu, via to In2.Cu, runs south, via back to B.Cu:
    y_d13 = py(3) # 114.985
    y_esc_d13 = y_d13 - 1.27 # 113.715
    new_items.append(add_seg(r2_x, y_d13, r2_x + 1.27, y_esc_d13, "B.Cu", "d13"))
    v1_d13_x = r1_x + 1.78 # 69.78
    v1_d13_y = y_esc_d13   # 113.715
    new_items.append(add_seg(r2_x + 1.27, y_esc_d13, v1_d13_x, v1_d13_y, "B.Cu", "d13"))
    new_items.append(add_via(v1_d13_x, v1_d13_y, "d13"))
    new_items.append(add_seg(v1_d13_x, v1_d13_y, v1_d13_x, 122.00, "In2.Cu", "d13"))
    v2_d13_x = v1_d13_x + 2.0 # 71.78
    new_items.append(add_seg(v1_d13_x, 122.00, v2_d13_x, 122.00, "In2.Cu", "d13"))
    new_items.append(add_via(v2_d13_x, 122.00, "d13"))
    # from v2 back on B.Cu to 125.56:
    dy_d13 = 125.56 - 122.00 # 3.56
    new_items.append(add_seg(v2_d13_x, 122.00, v2_d13_x + dy_d13, 125.56, "B.Cu", "d13"))
    new_items.append(add_seg(v2_d13_x + dy_d13, 125.56, 95.0, 125.56, "B.Cu", "d13"))

    # 12. gpio_enc_b (Pad 10, i=4) - escapes on B.Cu, via to In2.Cu, runs south, via back to B.Cu:
    y_enc_b = py(4) # 112.445
    y_esc_b = y_enc_b - 1.27 # 111.175
    new_items.append(add_seg(r2_x, y_enc_b, r2_x + 1.27, y_esc_b, "B.Cu", "gpio_enc_b"))
    v1_b_x = r2_x + 1.32 # 66.78
    v1_b_y = y_esc_b     # 111.175
    new_items.append(add_seg(r2_x + 1.27, y_esc_b, v1_b_x, v1_b_y, "B.Cu", "gpio_enc_b"))
    new_items.append(add_via(v1_b_x, v1_b_y, "gpio_enc_b"))
    v2_b_y = 125.00
    new_items.append(add_seg(v1_b_x, v1_b_y, v1_b_x, v2_b_y, "In2.Cu", "gpio_enc_b"))
    v2_b_x = v1_b_x      # 66.78
    new_items.append(add_via(v2_b_x, v2_b_y, "gpio_enc_b"))
    dy_b = 130.64 - v2_b_y # 5.64
    new_items.append(add_seg(v2_b_x, v2_b_y, v2_b_x + dy_b, 130.64, "B.Cu", "gpio_enc_b"))
    new_items.append(add_seg(v2_b_x + dy_b, 130.64, 95.0, 130.64, "B.Cu", "gpio_enc_b"))

    # Fix gpio_enc_sw turn:
    x_sw_turn = 70.225
    new_items.append(add_seg(r1_x, y_sw, x_sw_turn, y_sw, "F.Cu", "gpio_enc_sw"))
    new_items.append(add_seg(x_sw_turn, y_sw, x_sw_turn + dy_sw, 133.18, "F.Cu", "gpio_enc_sw"))
    new_items.append(add_seg(x_sw_turn + dy_sw, 133.18, 95.0, 133.18, "F.Cu", "gpio_enc_sw"))

    # 13. daisy_5v_power (Pad 1, i=0):
    new_items.append(add_seg(r1_x, py(0), r1_x, 140.0, "F.Cu", "daisy_5v_power", 0.5))
    new_items.append(add_seg(r1_x, 140.0, 122.0, 140.0, "F.Cu", "daisy_5v_power", 0.5))

    # 14. audio_in_r (Pad 2, i=0):
    new_items.append(add_seg(r2_x, py(0), r2_x, 142.5, "B.Cu", "audio_in_r", 0.3))
    new_items.append(add_seg(r2_x, 142.5, 105.0, 142.5, "B.Cu", "audio_in_r", 0.3))

    insert_idx = text_no_tracks.rfind(')')
    final_text = text_no_tracks[:insert_idx] + '\n' + '\n'.join(new_items) + '\n)'

    with open(dst_pcb, 'w', encoding='utf-8') as f:
        f.write(final_text)
    print(f"Generated clean routed PCB at ({u6_x}, {u6_y}) -> {dst_pcb}")

if __name__ == '__main__':
    build_perfect_routed_pcb()
