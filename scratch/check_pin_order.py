# Let's check U6 pins and U5 pins to see if they can connect on F.Cu without crossings:
# U6 has two rows:
# Left row (X = 53.46):
#   Pin 20: p20 (Y=97.61)
#   Pin 18: p18 (Y=100.16)
#   Pin 16: gpio_disp_dc (Y=102.69)
#   Pin 14: spi1_sck (Y=105.23)
#   Pin 12: spi1_mosi (Y=107.77)
#   Pin 10: gpio_enc_b (Y=110.31)
#   Pin 8 : d13 (Y=112.85)
#   Pin 6 : i2c1_scl (Y=115.39)
#   Pin 4 : i2c1_sda (Y=117.93)
#   Pin 2 : audio_in_r (Y=120.47)
#
# Right row (X = 56.00):
#   Pin 19: p19 (Y=97.61)
#   Pin 17: gpio_disp_res (Y=100.16)
#   Pin 15: spi1_cs (Y=102.69)
#   Pin 13: spi1_miso (Y=105.23)
#   Pin 11: gpio_enc_sw (Y=107.77)
#   Pin 9 : d14 (Y=110.31)
#   Pin 7 : gnd (Y=112.85)
#   Pin 5 : gnd (Y=115.39)
#   Pin 3 : gnd (Y=117.93)
#   Pin 1 : daisy_5v_power (Y=120.47)

# Now on U5 (with rot = 0):
# Row 1 (X = X_u5, facing U6):
#   Pin 1 : gpio_disp_res (ly = 0.00)
#   Pin 6 : gpio_disp_dc  (ly = 12.70)
#   Pin 7 : spi1_cs       (ly = 15.24)
#   Pin 8 : spi1_sck      (ly = 17.78)
#   Pin 9 : spi1_miso     (ly = 20.32)
#   Pin 10: spi1_mosi     (ly = 22.86)
#   Pin 11: i2c1_scl      (ly = 25.40)
#   Pin 12: i2c1_sda      (ly = 27.94)
#   Pin 13: d13           (ly = 30.48)
#   Pin 16: d14           (ly = 38.10)
#   Pin 17: gpio_enc_b    (ly = 40.64)
#   Pin 18: gpio_enc_sw   (ly = 43.18)

# Notice: On U6, pins alternate between Right row (X=56) and Left row (X=53.46)!
# Can the Right row of U6 exit directly to the right (+X) towards U5?
# YES! The right row is at X=56, so nothing is to the right of it!
# Can the Left row of U6 exit?
# Left row is at X=53.46. It can exit between the pins of the Right row, OR exit to the left, or on another layer (like B.Cu or In1.Cu)!
# Wait, can we use 2 layers: F.Cu for one row, B.Cu for the other row?
# Through-hole pins exist on ALL copper layers!
# Since U6 and U5 are through-hole, you can route directly on F.Cu AND B.Cu with ZERO vias!
print("Through-hole pins connect directly on F.Cu and B.Cu without ANY vias!")
