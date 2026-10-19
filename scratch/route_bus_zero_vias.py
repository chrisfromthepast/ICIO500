import math

# Define pad locations for U6 and U5
# U6 is at (56.0, 120.475, rot=180)
# U5 will be at (95.0, 90.0, rot=0)

X_U6_ODD  = 56.00
X_U6_EVEN = 53.46

X_U5_ROW1 = 95.00
X_U5_ROW2 = 95.00 + 15.24  # 110.24
Y_U5_BASE = 90.00

def get_u6_pad(pin):
    # pin 1..20
    # odd pins at X=56.00, even at X=53.46
    x = X_U6_ODD if (pin % 2 != 0) else X_U6_EVEN
    row_idx = (pin - 1) // 2
    y = 120.475 - row_idx * 2.54
    return (round(x, 3), round(y, 3))

def get_u5_pad(pin):
    # pin 1..40
    # pins 1..20 on Row 1 (X=95)
    # pins 21..40 on Row 2 (X=110.24)
    if pin <= 20:
        x = X_U5_ROW1
        y = Y_U5_BASE + (pin - 1) * 2.54
    else:
        x = X_U5_ROW2
        y = Y_U5_BASE + (40 - pin) * 2.54
    return (round(x, 3), round(y, 3))

# Nets to route:
# 1. gpio_disp_res: U6 pin 17 -> U5 pin 1
# 2. gpio_disp_dc:  U6 pin 16 -> U5 pin 6
# 3. spi1_cs:       U6 pin 15 -> U5 pin 7
# 4. spi1_sck:      U6 pin 14 -> U5 pin 8
# 5. spi1_miso:     U6 pin 13 -> U5 pin 9
# 6. spi1_mosi:     U6 pin 12 -> U5 pin 10
# 7. i2c1_scl:      U6 pin 6  -> U5 pin 11
# 8. i2c1_sda:      U6 pin 4  -> U5 pin 12
# 9. d13:           U6 pin 8  -> U5 pin 13
# 10. d14:          U6 pin 9  -> U5 pin 16
# 11. gpio_enc_b:   U6 pin 10 -> U5 pin 17
# 12. gpio_enc_sw:  U6 pin 11 -> U5 pin 18
# 13. daisy_5v_power: U6 pin 1 -> U5 pin 39
# 14. audio_in_r:   U6 pin 2  -> U5 pin 38

net_specs = [
    ('gpio_disp_res', 17,  1, 'F.Cu'),
    ('gpio_disp_dc',  16,  6, 'B.Cu'),
    ('spi1_cs',       15,  7, 'F.Cu'),
    ('spi1_sck',      14,  8, 'B.Cu'),
    ('spi1_miso',     13,  9, 'F.Cu'),
    ('spi1_mosi',     12, 10, 'B.Cu'),
    ('i2c1_scl',       6, 11, 'B.Cu'),
    ('i2c1_sda',       4, 12, 'B.Cu'),
    ('d13',            8, 13, 'B.Cu'),
    ('d14',            9, 16, 'F.Cu'),
    ('gpio_enc_b',    10, 17, 'B.Cu'),
    ('gpio_enc_sw',   11, 18, 'F.Cu'),
    ('daisy_5v_power', 1, 39, 'F.Cu'),
    ('audio_in_r',     2, 38, 'B.Cu'),
]

print("=== NET ENDPOINTS ===")
for name, p_u6, p_u5, layer in net_specs:
    src = get_u6_pad(p_u6)
    dst = get_u5_pad(p_u5)
    print(f"{name:16s} ({layer}): U6 pin {p_u6:2d} {src} -> U5 pin {p_u5:2d} {dst}")
