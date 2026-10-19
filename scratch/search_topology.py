# Search for clean zero-crossing paths across F.Cu and B.Cu
from verify_geometry import intersect

# Endpoints:
# (name, U6_pin, U5_pin, src, dst)
nets = [
    ('gpio_disp_res', 17,  5, (56.00, 100.155), (95.00, 100.160)),
    ('gpio_disp_dc',  16,  6, (53.46, 102.695), (95.00, 102.700)),
    ('spi1_cs',       15,  7, (56.00, 102.695), (95.00, 105.240)),
    ('spi1_sck',      14,  8, (53.46, 105.235), (95.00, 107.780)),
    ('spi1_miso',     13,  9, (56.00, 105.235), (95.00, 110.320)),
    ('spi1_mosi',     12, 10, (53.46, 107.775), (95.00, 112.860)),
    ('i2c1_scl',       6, 11, (53.46, 115.395), (95.00, 115.400)),
    ('i2c1_sda',       4, 12, (53.46, 117.935), (95.00, 117.940)),
    ('d13',            8, 15, (53.46, 112.855), (95.00, 125.560)),
    ('d14',            9, 16, (56.00, 110.315), (95.00, 128.100)),
    ('gpio_enc_b',    10, 17, (53.46, 110.315), (95.00, 130.640)),
    ('gpio_enc_sw',   11, 18, (56.00, 107.775), (95.00, 133.180)),
]

# Even pins on U6 pass through gap at Y_mid:
even_gaps = {
    16: 101.43,
    14: 103.97,
    12: 106.51,
    10: 109.05,
    8:  111.59,
    6:  114.13,
    4:  116.67,
}

# For each net, define its route given a turn_x
def make_net_route(net_tuple, turn_x):
    name, p6, p5, src, dst = net_tuple
    if p6 in even_gaps:
        ym = even_gaps[p6]
        # exit U6 through gap: src -> (54.73, ym) -> (57.27, ym)
        # then 45 deg to dst Y at turn_x, then straight to dst
        p1 = (54.73, ym)
        p2 = (57.27, ym)
        dy = dst[1] - ym
        p3 = (turn_x, dst[1])
        return [src, p1, p2, p3, dst]
    else:
        # odd pin: src -> (turn_x, dst[1]) -> dst
        return [src, (turn_x, dst[1]), dst]

def get_segments(pts, name):
    return [(pts[i], pts[i+1], name) for i in range(len(pts)-1)]

# Let's test layer configurations
from itertools import product

best_sol = None
for layers in product([0, 1], repeat=12):
    # layers: 0=F.Cu, 1=B.Cu
    # Let's set turn_x for each net to avoid parallel trace collisions:
    # 12 nets, spaced by 2mm between X=60 and X=84:
    f_segs = []
    b_segs = []
    
    # Sort nets on each layer so outer ones have larger turn_x
    valid = True
    for l_val in [0, 1]:
        l_nets = [nets[i] for i in range(12) if layers[i] == l_val]
        # Assign turn_x based on dst Y order
        l_nets.sort(key=lambda n: n[4][1]) # sort by dst Y
        segs = []
        for idx, n in enumerate(l_nets):
            tx = 60.0 + idx * 3.0
            route = make_net_route(n, tx)
            s_list = get_segments(route, n[0])
            # check self-layer crossings
            for s_new in s_list:
                for s_old in segs:
                    if intersect(s_new[0], s_new[1], s_old[0], s_old[1]):
                        valid = False
                        break
                if not valid: break
                segs.append(s_new)
            if not valid: break
        if not valid: break
        if l_val == 0: f_segs = segs
        else: b_segs = segs
        
    if valid:
        best_sol = layers
        print("FOUND ZERO-CROSSING SOLUTION!")
        break

if best_sol:
    print("\nLayer assignments:")
    for i, n in enumerate(nets):
        l_name = "F.Cu" if best_sol[i] == 0 else "B.Cu"
        print(f"  {n[0]:15s}: {l_name}")
else:
    print("No simple solution with monotonic turn_x, searching general topology...")
