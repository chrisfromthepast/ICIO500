import math

# Let's inspect U6 absolute pin locations:
# U6 at (56, 120.475, 180)
# Footprint rotation 180:
# X_abs = 56 - px
# Y_abs = 120.475 - py

u6_pins = [
    (1, 0.00, 0.00, 'daisy_5v_power'),
    (2, 2.54, 0.00, 'audio_in_r'),
    (3, 0.00, 2.54, 'gnd'),
    (4, 2.54, 2.54, 'i2c1_sda'),
    (5, 0.00, 5.08, 'gnd'),
    (6, 2.54, 5.08, 'i2c1_scl'),
    (7, 0.00, 7.62, 'gnd'),
    (8, 2.54, 7.62, 'd13'),
    (9, 0.00, 10.16, 'd14'),
    (10, 2.54, 10.16, 'gpio_enc_b'),
    (11, 0.00, 12.70, 'gpio_enc_sw'),
    (12, 2.54, 12.70, 'spi1_mosi'),
    (13, 0.00, 15.24, 'spi1_miso'),
    (14, 2.54, 15.24, 'spi1_sck'),
    (15, 0.00, 17.78, 'spi1_cs'),
    (16, 2.54, 17.78, 'gpio_disp_dc'),
    (17, 0.00, 20.32, 'gpio_disp_res'),
]

print("=== U6 ABSOLUTE PIN POSITIONS ===")
u6_abs = {}
for num, lx, ly, net in u6_pins:
    ax = 56.0 - lx
    ay = 120.475 - ly
    u6_abs[net] = (ax, ay, num)
    print(f"  U6 pin {num:2d} ({net:18s}): abs=({ax:6.2f}, {ay:6.2f})")

# Now let's test U5:
# In DIP-40 socket:
# local coords:
# pin 1: (0, 0), pin 6: (0, 12.7), pin 7: (0, 15.24), ... pin 18: (0, 43.18), pin 19: (0, 45.72)
# pin 38: (15.24, 5.08), pin 39: (15.24, 2.54), pin 40: (15.24, 0.0)

# If U5 is at (X_u5, Y_u5) with rot:
# Currently U5 was at (130.92, 112.51, -90).
# User said: "turn the daisy 90 degrees ccw"
# -90 deg + 90 deg CCW = 0 deg!
print("\n=== U5 at rot = 0 ===")
# If rot = 0:
# X_abs = X_u5 + lx
# Y_abs = Y_u5 + ly
# Notice: pins 1..18 will be at X_abs = X_u5, and Y_abs = Y_u5 + ly.
# Since lx = 0 for pins 1..18, and lx = 15.24 for pins 21..40:
# Pins 1..18 are on the LEFT row (facing U6 at X=56)!
# Pins 21..40 are on the RIGHT row (X_u5 + 15.24)!
# And what should X_u5 and Y_u5 be so that the pins line up horizontally with U6?
# In U6, pins 17 down to 4 have Y_abs from 100.155 to 117.935.
# In U5, pin 1 (gpio_disp_res) is at ly = 0.
# If we want pin 1 to align with U6 pin 17 (gpio_disp_res at Y_abs = 100.155):
# Y_u5 should be ~ 100.155!
# Then:
# Pin 1 (ly=0.0): Y_abs = 100.155 (matches U6 pin 17 at 100.155!)
# Pin 6 (ly=12.7): Y_abs = 112.855 (U6 pin 16 is at 102.695)
# Let's inspect all Y differences if Y_u5 is chosen to center it!
