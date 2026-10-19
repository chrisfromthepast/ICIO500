# Find a partition of all 12 digital nets into F.Cu and B.Cu such that:
# Both layers have strictly monotonic source Y and destination Y (meaning 0 crossings)!

# List of 12 nets: (name, u6_pin, u5_pin, u6_y, u5_y, u6_x)
nets = [
    ('gpio_disp_res', 17,  1, 100.155,  90.00, 56.00),
    ('gpio_disp_dc',  16,  6, 102.695, 102.70, 53.46),
    ('spi1_cs',       15,  7, 102.695, 105.24, 56.00),
    ('spi1_sck',      14,  8, 105.235, 107.78, 53.46),
    ('spi1_miso',     13,  9, 105.235, 110.32, 56.00),
    ('spi1_mosi',     12, 10, 107.775, 112.86, 53.46),
    ('gpio_enc_sw',   11, 18, 107.775, 133.18, 56.00),
    ('gpio_enc_b',    10, 17, 110.315, 130.64, 53.46),
    ('d14',            9, 16, 110.315, 128.10, 56.00),
    ('d13',            8, 13, 112.855, 120.48, 53.46),
    ('i2c1_scl',       6, 11, 115.395, 115.40, 53.46),
    ('i2c1_sda',       4, 12, 117.935, 117.94, 53.46),
]

# Note: Pin 11 (X=56.00) and Pin 12 (X=53.46) have the same Y=107.775.
# If one is on F.Cu and one is on B.Cu, they don't conflict at all!
# Same for (15, 16), (13, 14), (9, 10).

from itertools import product

def is_strictly_monotonic(net_list):
    # Sort by source Y (and X if same Y)
    # If two nets have same source Y on same layer, they conflict!
    for i in range(len(net_list)):
        for j in range(i+1, len(net_list)):
            n1 = net_list[i]
            n2 = net_list[j]
            # same source Y on same layer?
            if n1[3] == n2[3]:
                return False
            # Crossing?
            if (n1[3] < n2[3] and n1[4] >= n2[4]) or (n1[3] > n2[3] and n1[4] <= n2[4]):
                return False
    return True

# Search all 2^12 = 4096 layer assignments
solutions = []
for p in product([0, 1], repeat=len(nets)):
    f_nets = [nets[i] for i in range(len(nets)) if p[i] == 0]
    b_nets = [nets[i] for i in range(len(nets)) if p[i] == 1]
    
    if is_strictly_monotonic(f_nets) and is_strictly_monotonic(b_nets):
        solutions.append((f_nets, b_nets))

print(f"Total strictly monotonic non-crossing solutions: {len(solutions)}")

if solutions:
    # Pick a balanced solution (roughly 6 on F, 6 on B)
    solutions.sort(key=lambda s: abs(len(s[0]) - len(s[1])))
    best_f, best_b = solutions[0]
    print(f"\nBest balanced solution ({len(best_f)} on F.Cu, {len(best_b)} on B.Cu):")
    print("--- F.Cu ---")
    for n in sorted(best_f, key=lambda x: x[3]):
        print(f"  {n[0]:15s}: U6 Pin {n[1]:2d} (Y={n[3]:6.2f}) -> U5 Pin {n[2]:2d} (Y={n[4]:6.2f})")
    print("--- B.Cu ---")
    for n in sorted(best_b, key=lambda x: x[3]):
        print(f"  {n[0]:15s}: U6 Pin {n[1]:2d} (Y={n[3]:6.2f}) -> U5 Pin {n[2]:2d} (Y={n[4]:6.2f})")
