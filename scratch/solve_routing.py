import math

# Let's write an exact routing generator for U6 <-> U5 with ZERO vias
# U6 is at (56.0, 120.475, rot=180)
# U6 pads:
# Odd pins (Row 1, X = 56.00):
#   Pin 17: (56.00, 100.155) - gpio_disp_res
#   Pin 15: (56.00, 102.695) - spi1_cs
#   Pin 13: (56.00, 105.235) - spi1_miso
#   Pin 11: (56.00, 107.775) - gpio_enc_sw
#   Pin 9 : (56.00, 110.315) - d14
#   Pin 7 : (56.00, 112.855) - gnd
#   Pin 5 : (56.00, 115.395) - gnd
#   Pin 3 : (56.00, 117.935) - gnd
#   Pin 1 : (56.00, 120.475) - daisy_5v_power

# Even pins (Row 2, X = 53.46):
#   Pin 16: (53.46, 102.695) - gpio_disp_dc
#   Pin 14: (53.46, 105.235) - spi1_sck
#   Pin 12: (53.46, 107.775) - spi1_mosi
#   Pin 10: (53.46, 110.315) - gpio_enc_b
#   Pin 8 : (53.46, 112.855) - d13
#   Pin 6 : (53.46, 115.395) - i2c1_scl
#   Pin 4 : (53.46, 117.935) - i2c1_sda
#   Pin 2 : (53.46, 120.475) - audio_in_r

# U5 DIP-40 socket with rot = 0:
# Row 1 (Pins 1..20, X = X_u5):
#   Pin 1 : (X_u5, Y_u5 + 0.00)  - gpio_disp_res
#   Pin 6 : (X_u5, Y_u5 + 12.70) - gpio_disp_dc
#   Pin 7 : (X_u5, Y_u5 + 15.24) - spi1_cs
#   Pin 8 : (X_u5, Y_u5 + 17.78) - spi1_sck
#   Pin 9 : (X_u5, Y_u5 + 20.32) - spi1_miso
#   Pin 10: (X_u5, Y_u5 + 22.86) - spi1_mosi
#   Pin 11: (X_u5, Y_u5 + 25.40) - i2c1_scl
#   Pin 12: (X_u5, Y_u5 + 27.94) - i2c1_sda
#   Pin 13: (X_u5, Y_u5 + 30.48) - d13
#   Pin 16: (X_u5, Y_u5 + 38.10) - d14
#   Pin 17: (X_u5, Y_u5 + 40.64) - gpio_enc_b
#   Pin 18: (X_u5, Y_u5 + 43.18) - gpio_enc_sw
#   Pin 19: (X_u5, Y_u5 + 45.72) - audio_in_from_daisy_plus

# Row 2 (Pins 21..40, X = X_u5 + 15.24):
#   Pin 36: (X_u5 + 15.24, Y_u5 + 10.16) - audio_out_r
#   Pin 37: (X_u5 + 15.24, Y_u5 + 7.62)  - daisy_audio_in
#   Pin 38: (X_u5 + 15.24, Y_u5 + 5.08)  - audio_in_r
#   Pin 39: (X_u5 + 15.24, Y_u5 + 2.54)  - daisy_5v_power
#   Pin 40: (X_u5 + 15.24, Y_u5 + 0.00)  - gnd

# Let's test X_u5 = 95.0, Y_u5 = 90.0:
X_u5 = 95.0
Y_u5 = 90.0

print(f"Testing U5 at ({X_u5}, {Y_u5}) rot=0")
