# Check planar assignment for U6 <-> U5 connections
# All pads on U6 and U5 are through-hole, so each trace can be assigned to either F.Cu or B.Cu with ZERO vias!

# Nets to route:
# Net: (U6_pin, U5_pin)
# 1. gpio_disp_res: (17, 1)
# 2. gpio_disp_dc: (16, 6)
# 3. spi1_cs: (15, 7)
# 4. spi1_sck: (14, 8)
# 5. spi1_miso: (13, 9)
# 6. spi1_mosi: (12, 10)
# 7. i2c1_scl: (6, 11)
# 8. i2c1_sda: (4, 12)
# 9. d13: (8, 13)
# 10. d14: (9, 16)
# 11. gpio_enc_b: (10, 17)
# 12. gpio_enc_sw: (11, 18)
# 13. daisy_5v_power: (1, 39)
# 14. audio_in_r: (2, 38)

# Let's inspect the U6 Y-order and U5 Y-order:
# On U6:
# Pin 17: Y = 100.155 (X = 56.00)
# Pin 16: Y = 102.695 (X = 53.46)
# Pin 15: Y = 102.695 (X = 56.00)
# Pin 14: Y = 105.235 (X = 53.46)
# Pin 13: Y = 105.235 (X = 56.00)
# Pin 12: Y = 107.775 (X = 53.46)
# Pin 11: Y = 107.775 (X = 56.00)
# Pin 10: Y = 110.315 (X = 53.46)
# Pin 9 : Y = 110.315 (X = 56.00)
# Pin 8 : Y = 112.855 (X = 53.46)
# Pin 6 : Y = 115.395 (X = 53.46)
# Pin 4 : Y = 117.935 (X = 53.46)
# Pin 2 : Y = 120.475 (X = 53.46)
# Pin 1 : Y = 120.475 (X = 56.00)

# On U5:
# Pin 1 : Y_u5 + 0.00
# Pin 6 : Y_u5 + 12.70
# Pin 7 : Y_u5 + 15.24
# Pin 8 : Y_u5 + 17.78
# Pin 9 : Y_u5 + 20.32
# Pin 10: Y_u5 + 22.86
# Pin 11: Y_u5 + 25.40
# Pin 12: Y_u5 + 27.94
# Pin 13: Y_u5 + 30.48
# Pin 16: Y_u5 + 38.10
# Pin 17: Y_u5 + 40.64
# Pin 18: Y_u5 + 43.18
# Pin 38: Y_u5 + 5.08  (X_u5 + 15.24)
# Pin 39: Y_u5 + 2.54  (X_u5 + 15.24)

print("Analysis of pin ordering and layer splitting:")
