# Check intersections between all segments in 2D
def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A, B, C, D):
    # check if segment AB intersects segment CD
    # endpoints sharing is allowed
    if A == C or A == D or B == C or B == D:
        return False
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def check_layer_crossings(segments, layer_name):
    crossings = []
    for i in range(len(segments)):
        for j in range(i+1, len(segments)):
            s1 = segments[i]
            s2 = segments[j]
            if intersect(s1[0], s1[1], s2[0], s2[1]):
                crossings.append((s1, s2))
    print(f"Layer {layer_name}: {len(segments)} segments, {len(crossings)} crossings.")
    for c in crossings:
        print(f"  Crossing: {c[0][2]} vs {c[1][2]}")
    return len(crossings) == 0

# Let's test our planned geometry!
f_segs = []
b_segs = []

def add_trace(pts, layer, net):
    target = f_segs if layer == "F.Cu" else b_segs
    for i in range(len(pts)-1):
        target.append((pts[i], pts[i+1], net))

# --- F.Cu Traces ---
# 1. gpio_disp_res: U6(17) -> U5(5)
add_trace([(56.0, 100.155), (95.0, 100.16)], "F.Cu", "gpio_disp_res")

# 2. spi1_cs: U6(15) -> U5(7)
add_trace([(56.0, 102.695), (58.545, 105.24), (95.0, 105.24)], "F.Cu", "spi1_cs")

# 3. spi1_miso: U6(13) -> U5(9)
add_trace([(56.0, 105.235), (61.085, 110.32), (95.0, 110.32)], "F.Cu", "spi1_miso")

# 4. i2c1_scl: U6(6) -> U5(11)
# Pin 6 is at (53.46, 115.395), exit right between Pin 7 and Pin 5 (Y=114.13)
add_trace([(53.46, 115.395), (54.73, 114.13), (57.27, 114.13), (58.54, 115.40), (95.0, 115.40)], "F.Cu", "i2c1_scl")

# 5. i2c1_sda: U6(4) -> U5(12)
# Pin 4 is at (53.46, 117.935), exit right between Pin 5 and Pin 3 (Y=116.67)
add_trace([(53.46, 117.935), (54.73, 116.67), (57.27, 116.67), (58.54, 117.94), (95.0, 117.94)], "F.Cu", "i2c1_sda")

# 6. gpio_enc_b: U6(10) -> U5(17)
# Pin 10 is at (53.46, 110.315), exit right between Pin 11 and Pin 9 (Y=109.05)
# then go down to Y=130.64
add_trace([(53.46, 110.315), (54.73, 109.05), (57.27, 109.05), (78.86, 130.64), (95.0, 130.64)], "F.Cu", "gpio_enc_b")

# 7. gpio_enc_sw: U6(11) -> U5(18)
# Pin 11 is at (56.0, 107.775), exit right to X=81.405, down to Y=133.18
add_trace([(56.0, 107.775), (81.405, 133.18), (95.0, 133.18)], "F.Cu", "gpio_enc_sw")

# --- B.Cu Traces ---
# 8. gpio_disp_dc: U6(16) -> U5(6)
add_trace([(53.46, 102.695), (54.73, 101.43), (57.27, 101.43), (58.54, 102.70), (95.0, 102.70)], "B.Cu", "gpio_disp_dc")

# 9. spi1_sck: U6(14) -> U5(8)
add_trace([(53.46, 105.235), (54.73, 103.97), (57.27, 103.97), (61.08, 107.78), (95.0, 107.78)], "B.Cu", "spi1_sck")

# 10. spi1_mosi: U6(12) -> U5(10)
add_trace([(53.46, 107.775), (54.73, 106.51), (57.27, 106.51), (63.62, 112.86), (95.0, 112.86)], "B.Cu", "spi1_mosi")

# 11. d13: U6(8) -> U5(15)
add_trace([(53.46, 112.855), (54.73, 111.59), (57.27, 111.59), (71.24, 125.56), (95.0, 125.56)], "B.Cu", "d13")

# 12. d14: U6(9) -> U5(16)
add_trace([(56.0, 110.315), (73.785, 128.10), (95.0, 128.10)], "B.Cu", "d14")

check_layer_crossings(f_segs, "F.Cu")
check_layer_crossings(b_segs, "B.Cu")
