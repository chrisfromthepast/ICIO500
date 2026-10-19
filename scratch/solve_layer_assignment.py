# Let's test the layer assignment where each net starts and ends on its assigned layer with ZERO vias.

# On U6, pins at X=53.46 (even) are in the left column.
# To exit to the right towards U5 (X=95), an even pin's trace can exit:
# Option A: Between odd pins (gap is 2.54 - 1.60 = 0.94mm, trace is 0.25mm + 2*0.2mm clearance = 0.65mm) -> easily fits!
# Option B: Exit left/top/bottom around the header.
#
# But wait! Even simpler:
# If an even pin exits on B.Cu, does it collide with an odd pin's pad?
# The odd pin's pad on B.Cu has diameter 1.6mm.
# The gap between odd pin pads on B.Cu is 0.94mm.
# So a trace on B.Cu can pass between the odd pin pads!

# Let's find an assignment of the 14 nets to layers:
# Nets:
# 1. gpio_disp_res: U6(17) -> U5(1)
# 2. gpio_disp_dc:  U6(16) -> U5(6)
# 3. spi1_cs:       U6(15) -> U5(7)
# 4. spi1_sck:      U6(14) -> U5(8)
# 5. spi1_miso:     U6(13) -> U5(9)
# 6. spi1_mosi:     U6(12) -> U5(10)
# 7. i2c1_scl:      U6(6)  -> U5(11)
# 8. i2c1_sda:      U6(4)  -> U5(12)
# 9. d13:           U6(8)  -> U5(13)
# 10. d14:          U6(9)  -> U5(16)
# 11. gpio_enc_b:   U6(10) -> U5(17)
# 12. gpio_enc_sw:  U6(11) -> U5(18)
# 13. daisy_5v_power: U6(1) -> U5(39)
# 14. audio_in_r:   U6(2)  -> U5(38)

# Notice: daisy_5v_power and audio_in_r go to pins 39 and 38 on U5 (Row 2, X = 95 + 15.24 = 110.24).
# They can easily route along the bottom (Y > 135) or top (Y < 85) to reach pins 38 and 39!

# Let's inspect the 12 digital bus nets (all go to U5 Row 1, X = 95):
# Destination Y order on U5 (from top to bottom):
# 1.  gpio_disp_res (U5 pin 1)  : y=90.00
# 2.  gpio_disp_dc  (U5 pin 6)  : y=102.70
# 3.  spi1_cs       (U5 pin 7)  : y=105.24
# 4.  spi1_sck      (U5 pin 8)  : y=107.78
# 5.  spi1_miso     (U5 pin 9)  : y=110.32
# 6.  spi1_mosi     (U5 pin 10) : y=112.86
# 7.  i2c1_scl      (U5 pin 11) : y=115.40
# 8.  i2c1_sda      (U5 pin 12) : y=117.94
# 9.  d13           (U5 pin 13) : y=120.48
# 10. d14           (U5 pin 16) : y=128.10
# 11. gpio_enc_b    (U5 pin 17) : y=130.64
# 12. gpio_enc_sw   (U5 pin 18) : y=133.18

# Source Y order on U6 (from top to bottom):
# y=100.155: Pin 17 (gpio_disp_res)
# y=102.695: Pin 16 (gpio_disp_dc), Pin 15 (spi1_cs)
# y=105.235: Pin 14 (spi1_sck),     Pin 13 (spi1_miso)
# y=107.775: Pin 12 (spi1_mosi),    Pin 11 (gpio_enc_sw)
# y=110.315: Pin 10 (gpio_enc_b),   Pin 9  (d14)
# y=112.855: Pin 8  (d13)
# y=115.395: Pin 6  (i2c1_scl)
# y=117.935: Pin 4  (i2c1_sda)

print("Look at the source and destination order!")
