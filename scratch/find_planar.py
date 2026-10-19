# Find valid planar assignment for U6 to U5 routing with ZERO crossings on F.Cu and B.Cu
from itertools import combinations

# Signals and their (U6_y, U5_y, name, u6_pin, u5_pin)
# U6 pins:
# 17: y=100.155 (X=56.00) -> U5 pin 1 (y=90.00)
# 16: y=102.695 (X=53.46) -> U5 pin 6 (y=102.70)
# 15: y=102.695 (X=56.00) -> U5 pin 7 (y=105.24)
# 14: y=105.235 (X=53.46) -> U5 pin 8 (y=107.78)
# 13: y=105.235 (X=56.00) -> U5 pin 9 (y=110.32)
# 12: y=107.775 (X=53.46) -> U5 pin 10 (y=112.86)
# 11: y=107.775 (X=56.00) -> U5 pin 18 (y=133.18)
# 10: y=110.315 (X=53.46) -> U5 pin 17 (y=130.64)
# 9 : y=110.315 (X=56.00) -> U5 pin 16 (y=128.10)
# 8 : y=112.855 (X=53.46) -> U5 pin 13 (y=120.48)
# 6 : y=115.395 (X=53.46) -> U5 pin 11 (y=115.40)
# 4 : y=117.935 (X=53.46) -> U5 pin 12 (y=117.94)

signals = [
    ('gpio_disp_res', 17, 1, 100.155, 90.00, 56.00),
    ('gpio_disp_dc',  16, 6, 102.695, 102.70, 53.46),
    ('spi1_cs',       15, 7, 102.695, 105.24, 56.00),
    ('spi1_sck',      14, 8, 105.235, 107.78, 53.46),
    ('spi1_miso',     13, 9, 105.235, 110.32, 56.00),
    ('spi1_mosi',     12, 10, 107.775, 112.86, 53.46),
    ('gpio_enc_sw',   11, 18, 107.775, 133.18, 56.00),
    ('gpio_enc_b',    10, 17, 110.315, 130.64, 53.46),
    ('d14',            9, 16, 110.315, 128.10, 56.00),
    ('d13',            8, 13, 112.855, 120.48, 53.46),
    ('i2c1_scl',       6, 11, 115.395, 115.40, 53.46),
    ('i2c1_sda',       4, 12, 117.935, 117.94, 53.46),
]

def crosses(s1, s2):
    # s1: (name, u6_pin, u5_pin, u6_y, u5_y, u6_x)
    # two nets cross if (u6_y1 - u6_y2) * (u5_y1 - u5_y2) < 0
    # or if u6_y are identical, check u6_x
    y1_src, y1_dst = s1[3], s1[4]
    y2_src, y2_dst = s2[3], s2[4]
    if y1_src == y2_src:
        # Same Y at U6! One is X=53.46, one is X=56.00.
        # The one at X=53.46 has to cross the one at X=56.00 if both exit right at same Y!
        return True
    return (y1_src < y2_src and y1_dst > y2_dst) or (y1_src > y2_src and y1_dst < y2_dst)

# Find an assignment to F.Cu and B.Cu with 0 crossings
n = len(signals)
valid_assignments = []
for k in range(1, n):
    for subset in combinations(range(n), k):
        set_f = set(subset)
        set_b = set(range(n)) - set_f
        
        # Check F crossings
        f_cross = False
        f_list = [signals[i] for i in set_f]
        for i in range(len(f_list)):
            for j in range(i+1, len(f_list)):
                if crosses(f_list[i], f_list[j]):
                    f_cross = True
                    break
            if f_cross: break
        if f_cross: continue
        
        # Check B crossings
        b_cross = False
        b_list = [signals[i] for i in set_b]
        for i in range(len(b_list)):
            for j in range(i+1, len(b_list)):
                if crosses(b_list[i], b_list[j]):
                    b_cross = True
                    break
            if b_cross: break
        if b_cross: continue
        
        valid_assignments.append((set_f, set_b))

print(f"Total valid planar assignments found: {len(valid_assignments)}")
if valid_assignments:
    f_set, b_set = valid_assignments[0]
    print("\n--- Solution 1 ---")
    print("F.Cu nets:")
    for i in sorted(f_set, key=lambda idx: signals[idx][3]):
        s = signals[i]
        print(f"  {s[0]:15s} : U6 Pin {s[1]:2d} (Y={s[3]:6.2f}) -> U5 Pin {s[2]:2d} (Y={s[4]:6.2f})")
    print("\nB.Cu nets:")
    for i in sorted(b_set, key=lambda idx: signals[idx][3]):
        s = signals[i]
        print(f"  {s[0]:15s} : U6 Pin {s[1]:2d} (Y={s[3]:6.2f}) -> U5 Pin {s[2]:2d} (Y={s[4]:6.2f})")
