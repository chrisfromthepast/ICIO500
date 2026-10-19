from grid_router import GridRouter

# Setup router with 0.25 mm grid
router = GridRouter(x_min=50.0, x_max=115.0, y_min=75.0, y_max=145.0, step=0.25)

X_U6_ODD  = 56.00
X_U6_EVEN = 53.46

X_U5_ROW1 = 95.00
X_U5_ROW2 = 95.00 + 15.24  # 110.24
Y_U5_BASE = 90.00

def get_u6_pad(pin):
    x = X_U6_ODD if (pin % 2 != 0) else X_U6_EVEN
    row_idx = (pin - 1) // 2
    y = 120.475 - row_idx * 2.54
    return (round(x, 3), round(y, 3))

# True U5 local pad locations:
# Left row: pins 1..20 at lx = 0.0, ly = (pin - 1) * 2.54
# Right row: pins 21..40 at lx = 15.24, ly = (40 - pin) * 2.54
def get_u5_pad(pin):
    if pin <= 20:
        x = X_U5_ROW1
        y = Y_U5_BASE + (pin - 1) * 2.54
    else:
        x = X_U5_ROW2
        y = Y_U5_BASE + (40 - pin) * 2.54
    return (round(x, 3), round(y, 3))

# True net-to-pad mappings:
true_nets_to_route = [
    # Top signals:
    ('gpio_disp_res', 17,  5, 0), # F.Cu: (56.0, 100.155) -> (95.0, 100.16) STRAIGHT!
    ('gpio_disp_dc',  16,  6, 1), # B.Cu: (53.46, 102.695) -> (95.0, 102.70) STRAIGHT!
    ('spi1_cs',       15,  7, 0), # F.Cu: (56.0, 102.695) -> (95.0, 105.24)
    ('spi1_sck',      14,  8, 1), # B.Cu: (53.46, 105.235) -> (95.0, 107.78)
    ('spi1_miso',     13,  9, 0), # F.Cu: (56.0, 105.235) -> (95.0, 110.32)
    ('spi1_mosi',     12, 10, 1), # B.Cu: (53.46, 107.775) -> (95.0, 112.86)
    # Middle:
    ('i2c1_scl',       6, 11, 1), # B.Cu: (53.46, 115.395) -> (95.0, 115.40) STRAIGHT!
    ('i2c1_sda',       4, 12, 1), # B.Cu: (53.46, 117.935) -> (95.0, 117.94) STRAIGHT!
    ('d13',            8, 15, 0), # F.Cu: (53.46, 112.855) -> (95.0, 125.56)
    # Bottom:
    ('d14',            9, 16, 0), # F.Cu: (56.0, 110.315) -> (95.0, 128.10)
    ('gpio_enc_b',    10, 17, 1), # B.Cu: (53.46, 110.315) -> (95.0, 130.64)
    ('gpio_enc_sw',   11, 18, 0), # F.Cu: (56.0, 107.775) -> (95.0, 133.18)
    # Power and audio in:
    ('daisy_5v_power', 1, 39, 0), # F.Cu: (56.0, 120.475) -> (110.24, 92.54)
    ('audio_in_r',     2, 38, 1), # B.Cu: (53.46, 120.475) -> (110.24, 95.08)
]

# Block all U6 and U5 pads
for layer in [0, 1]:
    for p in range(1, 21):
        px, py = get_u6_pad(p)
        router.block_circle(layer, px, py, radius=1.0)
    for p in range(1, 41):
        px, py = get_u5_pad(p)
        router.block_circle(layer, px, py, radius=1.0)

def simplify_path(pts):
    if len(pts) <= 2: return pts
    res = [pts[0]]
    for i in range(1, len(pts)-1):
        p_prev = res[-1]
        p_curr = pts[i]
        p_next = pts[i+1]
        dx1 = p_curr[0] - p_prev[0]
        dy1 = p_curr[1] - p_prev[1]
        dx2 = p_next[0] - p_curr[0]
        dy2 = p_next[1] - p_curr[1]
        len1 = (dx1**2 + dy1**2)**0.5
        len2 = (dx2**2 + dy2**2)**0.5
        if len1 > 0 and len2 > 0:
            if abs(dx1/len1 - dx2/len2) < 1e-4 and abs(dy1/len1 - dy2/len2) < 1e-4:
                continue
        res.append(p_curr)
    res.append(pts[-1])
    return res

true_routed_results = {}
for name, p_u6, p_u5, layer in true_nets_to_route:
    src = get_u6_pad(p_u6)
    dst = get_u5_pad(p_u5)
    
    gx_s, gy_s = router.to_grid(src[0], src[1])
    gx_d, gy_d = router.to_grid(dst[0], dst[1])
    
    for x in range(gx_s-4, gx_s+5):
        for y in range(gy_s-4, gy_s+5):
            if 0 <= x < router.nx and 0 <= y < router.ny:
                router.grid[layer][x][y] = False
    for x in range(gx_d-4, gx_d+5):
        for y in range(gy_d-4, gy_d+5):
            if 0 <= x < router.nx and 0 <= y < router.ny:
                router.grid[layer][x][y] = False
                
    path = router.route_net(src, dst, layer, clearance=0.4)
    if path:
        simple = simplify_path(path)
        true_routed_results[name] = (simple, layer)
        print(f"SUCCESS: Routed {name:16s} on layer {layer} with {len(simple)} points")
    else:
        print(f"FAILED to route {name:16s} on layer {layer}")

print(f"\nTotal routed: {len(true_routed_results)} / {len(true_nets_to_route)}")
