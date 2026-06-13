EESchema Schematic File Version 4
LIBS:ICIO 3-cache
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text Notes 750  7550 0    50   ~ 0
corrections since V2:\nReconnected net: U3A feedback loop, and added path to ground for -input\nisolate power ground from audio\nconnect c11 to chassis\nchanged U3b’s input network, made feedback loop more flexible\nU3A: changed input impedance, added buss feed, 
$Comp
L ICIO-3-rescue:CONN_01X15-ICIO-2-rescue-ICIO-2-rescue-ICIO-2.1-rescue-ICIO-2.1-colour-rescue J2
U 1 1 59C1B6C4
P 6200 2900
F 0 "J2" H 6200 3700 50  0000 C CNN
F 1 "Edge 30" H 6350 2050 50  0001 C CNN
F 2 "500 serires api stds:Edge 30LG" H 6200 2900 50  0001 C CNN
F 3 "" H 6200 2900 50  0001 C CNN
	1    6200 2900
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:C-device-ICIO-2.1-colour-rescue DNP1
U 1 1 59C1B6D9
P 7000 950
F 0 "DNP1" H 7025 1050 50  0000 L CNN
F 1 "1n" H 7025 850 50  0000 L CNN
F 2 "Capacitors_THT:C_Rect_L13.0mm_W8.0mm_P10.00mm_FKS3_FKP3_MKS4" H 7038 800 50  0001 C CNN
F 3 "" H 7000 950 50  0001 C CNN
	1    7000 950 
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:THAT1246-ICIO-2-rescue-ICIO-2-rescue-ICIO-2.1-rescue-ICIO-2.1-colour-rescue U2
U 1 1 59C1B73E
P 3900 3650
F 0 "U2" H 3950 3900 50  0000 L CNN
F 1 "THAT1246" H 3950 3800 50  0000 L CNN
F 2 "Housings_DIP:DIP-8_W7.62mm_LongPads" H 3950 3700 50  0001 C CNN
F 3 "" H 3950 3800 50  0001 C CNN
	1    3900 3650
	-1   0    0    -1  
$EndComp
$Comp
L power:GNDA #PWR05
U 1 1 59C1B740
P 3700 4650
F 0 "#PWR05" H 3700 4400 50  0001 C CNN
F 1 "GNDA" H 3700 4500 50  0000 C CNN
F 2 "" H 3700 4650 50  0001 C CNN
F 3 "" H 3700 4650 50  0001 C CNN
	1    3700 4650
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:C_Small-device-ICIO-2.1-colour-rescue C9
U 1 1 59C1B741
P 5450 2750
F 0 "C9" V 5550 2750 50  0000 C CNN
F 1 "470p" V 5650 2750 50  0000 C CNN
F 2 "Capacitors_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 5488 2600 50  0001 C CNN
F 3 "" H 5450 2750 50  0001 C CNN
	1    5450 2750
	0    -1   1    0   
$EndComp
Wire Wire Line
	5950 2300 6000 2300
Wire Wire Line
	6150 3800 6000 3800
Wire Wire Line
	6000 3800 6000 3600
Wire Wire Line
	3600 3950 3800 3950
$Comp
L ICIO-3-rescue:C_Small-device-ICIO-2.1-colour-rescue C12
U 1 1 59C1B742
P 5150 3100
F 0 "C12" V 4921 3100 50  0000 C CNN
F 1 "470p" V 5012 3100 50  0000 C CNN
F 2 "Capacitors_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 5188 2950 50  0001 C CNN
F 3 "" H 5150 3100 50  0001 C CNN
	1    5150 3100
	0    -1   1    0   
$EndComp
$Comp
L ICIO-3-rescue:C-device-ICIO-2.1-colour-rescue C4
U 1 1 59C1B743
P 5700 1850
F 0 "C4" H 5725 1950 50  0000 L CNN
F 1 "100p" H 5725 1750 50  0000 L CNN
F 2 "Capacitors_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 5738 1700 50  0001 C CNN
F 3 "" H 5700 1850 50  0001 C CNN
	1    5700 1850
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:C_Small-device-ICIO-2.1-colour-rescue C7
U 1 1 59C1B744
P 5550 2350
F 0 "C7" H 5400 2450 50  0000 L CNN
F 1 "100p" H 5350 2300 50  0000 L CNN
F 2 "Capacitors_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 5588 2200 50  0001 C CNN
F 3 "" H 5550 2350 50  0001 C CNN
	1    5550 2350
	-1   0    0    1   
$EndComp
$Comp
L ICIO-3-rescue:C_Small-device-ICIO-2.1-colour-rescue C11
U 1 1 59C1B746
P 4900 2900
F 0 "C11" V 4750 2900 50  0000 C CNN
F 1 "47p" V 4600 2900 50  0000 C CNN
F 2 "Capacitors_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 4938 2750 50  0001 C CNN
F 3 "" H 4900 2900 50  0001 C CNN
	1    4900 2900
	0    1    -1   0   
$EndComp
Wire Wire Line
	5350 2750 5000 2750
Wire Wire Line
	5950 2000 5950 2300
$Comp
L ICIO-3-rescue:C_Small-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue C10
U 1 1 59C1B74C
P 4100 4200
F 0 "C10" H 4008 4154 50  0000 R CNN
F 1 "100n" H 4008 4245 50  0000 R CNN
F 2 "Capacitors_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 4100 4200 50  0001 C CNN
F 3 "" H 4100 4200 50  0001 C CNN
	1    4100 4200
	-1   0    0    1   
$EndComp
$Comp
L ICIO-3-rescue:VEE-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue #PWR06
U 1 1 59C1B74D
P 4150 3950
F 0 "#PWR06" H 4150 3800 50  0001 C CNN
F 1 "VEE" V 4167 4078 50  0000 L CNN
F 2 "" H 4150 3950 50  0001 C CNN
F 3 "" H 4150 3950 50  0001 C CNN
	1    4150 3950
	0    1    1    0   
$EndComp
$Comp
L ICIO-3-rescue:VCC-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue #PWR07
U 1 1 59C1B74E
P 4000 3350
F 0 "#PWR07" H 4000 3200 50  0001 C CNN
F 1 "VCC" H 4000 3500 50  0000 C CNN
F 2 "" H 4000 3350 50  0001 C CNN
F 3 "" H 4000 3350 50  0001 C CNN
	1    4000 3350
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:C_Small-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue C6
U 1 1 59C1B74F
P 3550 3250
F 0 "C6" V 3321 3250 50  0000 C CNN
F 1 "100n" V 3412 3250 50  0000 C CNN
F 2 "Capacitors_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 3550 3250 50  0001 C CNN
F 3 "" H 3550 3250 50  0001 C CNN
	1    3550 3250
	0    1    1    0   
$EndComp
Wire Wire Line
	3300 3400 3300 3250
Wire Wire Line
	3300 3250 3450 3250
Wire Wire Line
	3650 3250 3950 3250
Wire Wire Line
	3950 3250 3950 3350
Wire Wire Line
	3950 3350 4000 3350
$Comp
L ICIO-3-rescue:C_Small-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue C1
U 1 1 59C1B750
P 3750 1050
F 0 "C1" V 3521 1050 50  0000 C CNN
F 1 "100n" V 3612 1050 50  0000 C CNN
F 2 "Capacitors_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 3750 1050 50  0001 C CNN
F 3 "" H 3750 1050 50  0001 C CNN
	1    3750 1050
	0    1    1    0   
$EndComp
$Comp
L ICIO-3-rescue:VCC-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue #PWR08
U 1 1 59C1B751
P 3450 1050
F 0 "#PWR08" H 3450 900 50  0001 C CNN
F 1 "VCC" H 3450 1200 50  0000 C CNN
F 2 "" H 3450 1050 50  0001 C CNN
F 3 "" H 3450 1050 50  0001 C CNN
	1    3450 1050
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:C_Small-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue C8
U 1 1 59C1B752
P 3550 2600
F 0 "C8" H 3642 2554 50  0000 L CNN
F 1 "100n" H 3642 2645 50  0000 L CNN
F 2 "Capacitors_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 3550 2600 50  0001 C CNN
F 3 "" H 3550 2600 50  0001 C CNN
	1    3550 2600
	-1   0    0    1   
$EndComp
$Comp
L ICIO-3-rescue:VEE-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue #PWR09
U 1 1 59C1B754
P 3550 2350
F 0 "#PWR09" H 3550 2200 50  0001 C CNN
F 1 "VEE" V 3568 2477 50  0000 L CNN
F 2 "" H 3550 2350 50  0001 C CNN
F 3 "" H 3550 2350 50  0001 C CNN
	1    3550 2350
	0    -1   -1   0   
$EndComp
Wire Wire Line
	3550 2700 3550 2800
Wire Wire Line
	3450 1050 3550 1050
Wire Wire Line
	3850 1050 3950 1050
$Comp
L ICIO-3-rescue:that1646-ICIO-2-rescue-ICIO-2-rescue-ICIO-2.1-rescue-ICIO-2.1-colour-rescue U1
U 1 1 59C1C3C7
P 3550 1900
F 0 "U1" H 3700 2200 50  0000 L CNN
F 1 "THAT1646" H 3700 1600 50  0000 L CNN
F 2 "Housings_DIP:DIP-8_W7.62mm_LongPads" H 3550 1800 50  0001 C CNN
F 3 "" H 3550 1800 50  0001 C CNN
	1    3550 1900
	1    0    0    -1  
$EndComp
Wire Wire Line
	4200 2200 4050 2100
Wire Wire Line
	3550 1600 3550 1050
Connection ~ 3550 1050
$Comp
L ICIO-3-rescue:C_Small-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue C3
U 1 1 59C1BDC3
P 4000 1500
F 0 "C3" V 3771 1500 50  0000 C CNN
F 1 "10u" V 3862 1500 50  0000 C CNN
F 2 "Capacitors_THT:C_Rect_L13.0mm_W8.0mm_P10.00mm_FKS3_FKP3_MKS4" H 4000 1500 50  0001 C CNN
F 3 "" H 4000 1500 50  0001 C CNN
	1    4000 1500
	0    1    1    0   
$EndComp
$Comp
L ICIO-3-rescue:C_Small-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue C5
U 1 1 59C1BE0E
P 3800 2350
F 0 "C5" V 3937 2350 50  0000 C CNN
F 1 "10u" V 4028 2350 50  0000 C CNN
F 2 "Capacitors_THT:C_Rect_L13.0mm_W8.0mm_P10.00mm_FKS3_FKP3_MKS4" H 3800 2350 50  0001 C CNN
F 3 "" H 3800 2350 50  0001 C CNN
	1    3800 2350
	0    1    1    0   
$EndComp
Wire Wire Line
	3700 1600 3700 1500
Wire Wire Line
	3650 2200 3700 2350
Wire Wire Line
	5750 2600 6000 2600
$Comp
L ICIO-3-rescue:Ferrite_Bead_Small-device-ICIO-2.1-colour-rescue L1
U 1 1 59C1CEAB
P 4950 2000
F 0 "L1" V 4850 2050 50  0000 C CNN
F 1 "Ferrite Bead" V 5050 2000 50  0000 C CNN
F 2 "Diodes_THT:D_A-405_P7.62mm_Horizontal" V 4880 2000 50  0001 C CNN
F 3 "" H 4950 2000 50  0001 C CNN
	1    4950 2000
	0    1    1    0   
$EndComp
$Comp
L ICIO-3-rescue:Ferrite_Bead_Small-device-ICIO-2.1-colour-rescue L2
U 1 1 59C1CF91
P 5300 2200
F 0 "L2" V 5200 2250 50  0000 C CNN
F 1 "Ferrite Bead" V 5400 2150 50  0000 C CNN
F 2 "Diodes_THT:D_A-405_P7.62mm_Horizontal" V 5230 2200 50  0001 C CNN
F 3 "" H 5300 2200 50  0001 C CNN
	1    5300 2200
	0    1    1    0   
$EndComp
Wire Wire Line
	5850 2500 5850 2200
$Comp
L ICIO-3-rescue:D_Small-device-ICIO-2.1-colour-rescue D4
U 1 1 59C1D9F1
P 4500 2500
F 0 "D4" H 4350 2550 50  0000 L CNN
F 1 "1n4004" H 4350 2420 50  0000 L CNN
F 2 "Diodes_THT:D_DO-41_SOD81_P10.16mm_Horizontal" V 4500 2500 50  0001 C CNN
F 3 "" V 4500 2500 50  0001 C CNN
	1    4500 2500
	0    1    1    0   
$EndComp
Wire Wire Line
	2300 1750 3100 1750
$Comp
L power:GNDA #PWR010
U 1 1 5A79EA5E
P 5750 2600
F 0 "#PWR010" H 5750 2350 50  0001 C CNN
F 1 "GNDA" H 5750 2450 50  0000 C CNN
F 2 "" H 5750 2600 50  0001 C CNN
F 3 "" H 5750 2600 50  0001 C CNN
	1    5750 2600
	1    0    0    -1  
$EndComp
Wire Wire Line
	7000 800  6800 800 
$Comp
L ICIO-3-rescue:GNDPWR-power-ICIO-2.1-colour-rescue #PWR012
U 1 1 5A79D844
P 6800 800
F 0 "#PWR012" H 6800 550 50  0001 C CNN
F 1 "GNDPWR" H 6800 650 50  0000 C CNN
F 2 "" H 6800 800 50  0001 C CNN
F 3 "" H 6800 800 50  0001 C CNN
	1    6800 800 
	0    1    1    0   
$EndComp
$Comp
L power:Earth #PWR017
U 1 1 5A79DB59
P 7000 1100
F 0 "#PWR017" H 7000 850 50  0001 C CNN
F 1 "Earth" H 7000 950 50  0000 C CNN
F 2 "" H 7000 1100 50  0001 C CNN
F 3 "" H 7000 1100 50  0001 C CNN
	1    7000 1100
	1    0    0    -1  
$EndComp
$Comp
L power:Earth #PWR019
U 1 1 5A79DC69
P 5350 1700
F 0 "#PWR019" H 5350 1450 50  0001 C CNN
F 1 "Earth" H 5350 1550 50  0001 C CNN
F 2 "" H 5350 1700 50  0001 C CNN
F 3 "" H 5350 1700 50  0001 C CNN
	1    5350 1700
	1    0    0    -1  
$EndComp
Wire Wire Line
	6000 2200 6000 2050
Wire Wire Line
	6000 2050 6350 2050
$Comp
L power:Earth #PWR020
U 1 1 5A79E19C
P 6350 2050
F 0 "#PWR020" H 6350 1800 50  0001 C CNN
F 1 "Earth" H 6350 1900 50  0001 C CNN
F 2 "" H 6350 2050 50  0001 C CNN
F 3 "" H 6350 2050 50  0001 C CNN
	1    6350 2050
	1    0    0    -1  
$EndComp
Wire Wire Line
	3550 1050 3650 1050
Wire Wire Line
	5850 2500 6000 2500
$Comp
L ICIO-3-rescue:OPA2134PA-dk_Linear-Amplifiers-Instrumentation-OP-Amps-Buffer-Amps-ICIO-2.1-colour-rescue U3
U 1 1 5D60EF34
P 2000 1750
F 0 "U3" H 2300 1800 60  0000 L CNN
F 1 "2134" H 2300 1700 60  0000 L CNN
F 2 "digikey-footprints:DIP-8_W7.62mm" H 2200 1950 60  0001 L CNN
F 3 "http://www.ti.com/lit/ds/symlink/opa134.pdf" H 2200 2050 60  0001 L CNN
F 4 "OPA2134PA-ND" H 2200 2150 60  0001 L CNN "Digi-Key_PN"
F 5 "OPA2134PA" H 2200 2250 60  0001 L CNN "MPN"
F 6 "Integrated Circuits (ICs)" H 2200 2350 60  0001 L CNN "Category"
F 7 "Linear - Amplifiers - Instrumentation, OP Amps, Buffer Amps" H 2200 2450 60  0001 L CNN "Family"
F 8 "http://www.ti.com/lit/ds/symlink/opa134.pdf" H 2200 2550 60  0001 L CNN "DK_Datasheet_Link"
F 9 "/product-detail/en/texas-instruments/OPA2134PA/OPA2134PA-ND/254686" H 2200 2650 60  0001 L CNN "DK_Detail_Page"
F 10 "IC OPAMP AUDIO 8MHZ 8DIP" H 2200 2750 60  0001 L CNN "Description"
F 11 "Texas Instruments" H 2200 2850 60  0001 L CNN "Manufacturer"
F 12 "Active" H 2200 2950 60  0001 L CNN "Status"
	1    2000 1750
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:C_Small-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue C17
U 1 1 5D61DFBB
P 2150 2050
F 0 "C17" V 2287 2050 50  0000 C CNN
F 1 "100n" V 2378 2050 50  0000 C CNN
F 2 "Capacitors_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 2150 2050 50  0001 C CNN
F 3 "" H 2150 2050 50  0001 C CNN
	1    2150 2050
	0    1    1    0   
$EndComp
$Comp
L ICIO-3-rescue:VEE-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue #PWR0101
U 1 1 5D61DFC5
P 1900 2050
F 0 "#PWR0101" H 1900 1900 50  0001 C CNN
F 1 "VEE" H 1918 2223 50  0000 C CNN
F 2 "" H 1900 2050 50  0001 C CNN
F 3 "" H 1900 2050 50  0001 C CNN
	1    1900 2050
	-1   0    0    1   
$EndComp
Wire Wire Line
	1900 2050 2000 2050
Wire Wire Line
	2250 2050 2350 2050
Connection ~ 2000 2050
Wire Wire Line
	2000 2050 2050 2050
Wire Wire Line
	2000 1950 2000 2050
$Comp
L ICIO-3-rescue:C_Small-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue C15
U 1 1 5D622BD3
P 2550 1200
F 0 "C15" V 2321 1200 50  0000 C CNN
F 1 "100n" V 2412 1200 50  0000 C CNN
F 2 "Capacitors_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 2550 1200 50  0001 C CNN
F 3 "" H 2550 1200 50  0001 C CNN
	1    2550 1200
	0    1    1    0   
$EndComp
$Comp
L ICIO-3-rescue:VCC-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue #PWR0103
U 1 1 5D622BDD
P 2250 1200
F 0 "#PWR0103" H 2250 1050 50  0001 C CNN
F 1 "VCC" H 2250 1350 50  0000 C CNN
F 2 "" H 2250 1200 50  0001 C CNN
F 3 "" H 2250 1200 50  0001 C CNN
	1    2250 1200
	1    0    0    -1  
$EndComp
Wire Wire Line
	2250 1200 2350 1200
Wire Wire Line
	2650 1200 2750 1200
Connection ~ 2350 1200
Wire Wire Line
	2350 1200 2450 1200
Wire Wire Line
	2150 3850 2100 3850
Connection ~ 2100 3850
Wire Wire Line
	2100 3850 1450 3850
Wire Wire Line
	2350 1200 2350 1550
$Comp
L ICIO-3-rescue:C_Small-device-ICIO-2.1-colour-rescue C16
U 1 1 5D656B66
P 1800 1400
F 0 "C16" V 1571 1400 50  0000 C CNN
F 1 "0" V 1662 1400 50  0000 C CNN
F 2 "500 serires api stds:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 1800 1400 50  0001 C CNN
F 3 "do not place" H 1800 1400 50  0001 C CNN
	1    1800 1400
	0    1    1    0   
$EndComp
$Comp
L ICIO-3-rescue:R_Small-device-ICIO-2.1-colour-rescue R1
U 1 1 5D657DE5
P 1800 1050
F 0 "R1" V 1604 1050 50  0000 C CNN
F 1 "0R" V 1695 1050 50  0000 C CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" H 1800 1050 50  0001 C CNN
F 3 "" H 1800 1050 50  0001 C CNN
	1    1800 1050
	0    1    1    0   
$EndComp
Wire Wire Line
	1700 1050 1700 1400
Connection ~ 1700 1400
Wire Wire Line
	1900 1050 1900 1400
Connection ~ 1900 1400
Wire Wire Line
	1900 1400 2300 1400
$Comp
L ICIO-3-rescue:C_Small-device-ICIO-2.1-colour-rescue C19
U 1 1 5D69E49A
P 2300 3500
F 0 "C19" V 2071 3500 50  0000 C CNN
F 1 "22p" V 2162 3500 50  0000 C CNN
F 2 "500 serires api stds:C_Disc_D5.0mm_W2.5mm_P2.50mm" H 2300 3500 50  0001 C CNN
F 3 "" H 2300 3500 50  0001 C CNN
	1    2300 3500
	0    1    1    0   
$EndComp
Wire Wire Line
	2100 3500 2100 3850
Wire Wire Line
	2400 3500 2750 3500
Wire Wire Line
	2750 3500 2750 3750
$Comp
L ICIO-3-rescue:R_Small-device-ICIO-2.1-colour-rescue R3
U 1 1 5D6AB202
P 2750 2950
F 0 "R3" V 2554 2950 50  0000 C CNN
F 1 "1.2K" V 2645 2950 50  0000 C CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" H 2750 2950 50  0001 C CNN
F 3 "" H 2750 2950 50  0001 C CNN
	1    2750 2950
	-1   0    0    1   
$EndComp
Wire Wire Line
	2100 3150 2100 3500
Wire Wire Line
	2750 3050 2750 3150
Text GLabel 800  3850 0    50   Output ~ 0
send
Text GLabel 800  1550 1    50   Input ~ 0
return
Wire Wire Line
	1100 3850 800  3850
Connection ~ 1100 3850
Wire Wire Line
	1100 3900 1100 3850
Wire Wire Line
	1250 3850 1100 3850
$Comp
L power:GNDA #PWR0109
U 1 1 5D6DDAEB
P 1100 4100
F 0 "#PWR0109" H 1100 3850 50  0001 C CNN
F 1 "GNDA" H 1105 3927 50  0000 C CNN
F 2 "" H 1100 4100 50  0001 C CNN
F 3 "" H 1100 4100 50  0001 C CNN
	1    1100 4100
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:R_Small-device-ICIO-2.1-colour-rescue DNP2
U 1 1 5D6DD975
P 1100 4000
F 0 "DNP2" H 900 3950 50  0000 L CNN
F 1 "0R" H 1159 3955 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" H 1100 4000 50  0001 C CNN
F 3 "" H 1100 4000 50  0001 C CNN
	1    1100 4000
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:R_Small-device-ICIO-2.1-colour-rescue R5
U 1 1 5D6DB345
P 1350 3850
F 0 "R5" V 1250 3850 50  0000 C CNN
F 1 "0R" V 1450 3850 50  0000 C CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" H 1350 3850 50  0001 C CNN
F 3 "" H 1350 3850 50  0001 C CNN
	1    1350 3850
	0    1    1    0   
$EndComp
Wire Wire Line
	1400 1850 1250 1850
Connection ~ 1400 1850
Wire Wire Line
	1400 1900 1400 1850
$Comp
L power:GNDA #PWR0110
U 1 1 5D6F7BA9
P 1400 2100
F 0 "#PWR0110" H 1400 1850 50  0001 C CNN
F 1 "GNDA" H 1405 1927 50  0000 C CNN
F 2 "" H 1400 2100 50  0001 C CNN
F 3 "" H 1400 2100 50  0001 C CNN
	1    1400 2100
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:R_Small-device-ICIO-2.1-colour-rescue R2
U 1 1 5D6F7BB3
P 1400 2000
F 0 "R2" H 1550 1950 50  0000 R CNN
F 1 "10M" H 1650 1800 50  0000 R CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" H 1400 2000 50  0001 C CNN
F 3 "" H 1400 2000 50  0001 C CNN
	1    1400 2000
	1    0    0    -1  
$EndComp
Wire Wire Line
	4250 1700 4500 2000
Connection ~ 5700 2000
Wire Wire Line
	5700 2000 5950 2000
NoConn ~ 6000 2400
NoConn ~ 6000 2700
NoConn ~ 6000 2800
NoConn ~ 6000 3000
$Comp
L power:VEE #PWR024
U 1 1 5D690FBF
P 4500 2600
F 0 "#PWR024" H 4500 2450 50  0001 C CNN
F 1 "VEE" H 4518 2773 50  0000 C CNN
F 2 "" H 4500 2600 50  0001 C CNN
F 3 "" H 4500 2600 50  0001 C CNN
	1    4500 2600
	-1   0    0    1   
$EndComp
$Comp
L ICIO-3-rescue:D_Small-device-ICIO-2.1-colour-rescue D1
U 1 1 59C1D4D8
P 4800 1700
F 0 "D1" H 4750 1800 50  0000 L CNN
F 1 "1n4004" H 4650 1620 50  0000 L CNN
F 2 "Diodes_THT:D_DO-41_SOD81_P10.16mm_Horizontal" V 4800 1700 50  0001 C CNN
F 3 "" V 4800 1700 50  0001 C CNN
	1    4800 1700
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR022
U 1 1 5D6EA096
P 4800 1600
F 0 "#PWR022" H 4800 1450 50  0001 C CNN
F 1 "VCC" H 4817 1773 50  0000 C CNN
F 2 "" H 4800 1600 50  0001 C CNN
F 3 "" H 4800 1600 50  0001 C CNN
	1    4800 1600
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:D_Small-device-ICIO-2.1-colour-rescue D2
U 1 1 59C1D686
P 4750 2400
F 0 "D2" H 4700 2480 50  0000 L CNN
F 1 "1n4004" H 4600 2300 50  0000 L CNN
F 2 "Diodes_THT:D_DO-41_SOD81_P10.16mm_Horizontal" V 4750 2400 50  0001 C CNN
F 3 "" V 4750 2400 50  0001 C CNN
	1    4750 2400
	0    -1   -1   0   
$EndComp
Wire Wire Line
	4500 2000 4500 1800
Connection ~ 4500 2000
$Comp
L power:VCC #PWR023
U 1 1 5D772F17
P 4750 2500
F 0 "#PWR023" H 4750 2350 50  0001 C CNN
F 1 "VCC" H 4768 2673 50  0000 C CNN
F 2 "" H 4750 2500 50  0001 C CNN
F 3 "" H 4750 2500 50  0001 C CNN
	1    4750 2500
	-1   0    0    1   
$EndComp
$Comp
L ICIO-3-rescue:D_Small-device-ICIO-2.1-colour-rescue D5
U 1 1 5D77A2EF
P 5050 3750
F 0 "D5" V 5150 3500 50  0000 L CNN
F 1 "1n4004" V 5050 3400 50  0000 L CNN
F 2 "500 serires api stds:D_DO-41_SOD81_P10.16mm_Horizontal" V 5050 3750 50  0001 C CNN
F 3 "" V 5050 3750 50  0001 C CNN
	1    5050 3750
	0    -1   -1   0   
$EndComp
$Comp
L ICIO-3-rescue:D_Small-device-ICIO-2.1-colour-rescue D6
U 1 1 5D78C5D8
P 5850 3850
F 0 "D6" V 5750 3700 50  0000 L CNN
F 1 "1n4004" V 5850 3500 50  0000 L CNN
F 2 "500 serires api stds:D_DO-41_SOD81_P10.16mm_Horizontal" V 5850 3850 50  0001 C CNN
F 3 "" V 5850 3850 50  0001 C CNN
	1    5850 3850
	0    1    1    0   
$EndComp
$Comp
L power:Earth #PWR0102
U 1 1 5DE269FF
P 5550 2450
F 0 "#PWR0102" H 5550 2200 50  0001 C CNN
F 1 "Earth" H 5550 2300 50  0001 C CNN
F 2 "" H 5550 2450 50  0001 C CNN
F 3 "~" H 5550 2450 50  0001 C CNN
	1    5550 2450
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:GNDPWR-power-ICIO-2.1-colour-rescue #PWR0104
U 1 1 5DE3263C
P 4100 4400
F 0 "#PWR0104" H 4100 4200 50  0001 C CNN
F 1 "GNDPWR" H 4350 4350 50  0000 C CNN
F 2 "" H 4100 4350 50  0001 C CNN
F 3 "" H 4100 4350 50  0001 C CNN
	1    4100 4400
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:VCC-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue #PWR02
U 1 1 59C1B71B
P 5050 4200
F 0 "#PWR02" H 5050 4050 50  0001 C CNN
F 1 "VCC" H 5050 4350 50  0000 C CNN
F 2 "" H 5050 4200 50  0001 C CNN
F 3 "" H 5050 4200 50  0001 C CNN
	1    5050 4200
	0    -1   -1   0   
$EndComp
$Comp
L ICIO-3-rescue:CP-device-ICIO-2.1-colour-rescue C14
U 1 1 59C1B6D8
P 5650 4200
F 0 "C14" V 5800 4100 50  0000 L CNN
F 1 "100u 50v" V 5500 3950 50  0000 L CNN
F 2 "Capacitors_THT:CP_Radial_D10.0mm_P5.00mm" H 5688 4050 50  0001 C CNN
F 3 "" H 5650 4200 50  0001 C CNN
	1    5650 4200
	0    -1   -1   0   
$EndComp
$Comp
L ICIO-3-rescue:CP-device-ICIO-2.1-colour-rescue C13
U 1 1 59C1B6D7
P 5250 4200
F 0 "C13" V 5400 4150 50  0000 L CNN
F 1 "100 U 50V" V 5100 4150 50  0000 L CNN
F 2 "Capacitors_THT:CP_Radial_D10.0mm_P5.00mm" H 5288 4050 50  0001 C CNN
F 3 "" H 5250 4200 50  0001 C CNN
	1    5250 4200
	0    -1   -1   0   
$EndComp
$Comp
L power:+48V #PWR01
U 1 1 59C1B6C7
P 6150 3800
F 0 "#PWR01" H 6150 3650 50  0001 C CNN
F 1 "+48V" H 6150 3750 50  0000 C CNN
F 2 "" H 6150 3800 50  0001 C CNN
F 3 "" H 6150 3800 50  0001 C CNN
	1    6150 3800
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:VEE-4_ch_smd-cache-2018-08-12-13-16-54-ICIO-2.1-rescue-ICIO-2.1-colour-rescue #PWR03
U 1 1 59C1B71C
P 5850 4200
F 0 "#PWR03" H 5850 4050 50  0001 C CNN
F 1 "VEE" H 5850 4350 50  0000 C CNN
F 2 "" H 5850 4200 50  0001 C CNN
F 3 "" H 5850 4200 50  0001 C CNN
	1    5850 4200
	0    1    1    0   
$EndComp
Wire Wire Line
	5850 3500 6000 3500
Wire Wire Line
	5850 3950 5850 4200
Wire Wire Line
	5800 4200 5850 4200
Wire Wire Line
	5400 4200 5450 4200
Wire Wire Line
	5100 4200 5050 4200
Connection ~ 5050 4200
Wire Wire Line
	5450 3300 5050 3650
Wire Wire Line
	6000 3400 5600 3400
Wire Wire Line
	5450 3400 5450 4200
Connection ~ 5450 4200
Wire Wire Line
	5450 4200 5500 4200
$Comp
L ICIO-3-rescue:GNDPWR-power-ICIO-2.1-colour-rescue #PWR0105
U 1 1 5DED8654
P 5600 3400
F 0 "#PWR0105" H 5600 3200 50  0001 C CNN
F 1 "GNDPWR" H 5500 3250 50  0000 L CNN
F 2 "" H 5600 3350 50  0001 C CNN
F 3 "" H 5600 3350 50  0001 C CNN
	1    5600 3400
	1    0    0    -1  
$EndComp
Connection ~ 5600 3400
Wire Wire Line
	5600 3400 5450 3400
$Comp
L power:Earth #PWR0106
U 1 1 5DEE7D61
P 4750 3000
F 0 "#PWR0106" H 4750 2750 50  0001 C CNN
F 1 "Earth" H 4750 2850 50  0001 C CNN
F 2 "" H 4750 3000 50  0001 C CNN
F 3 "~" H 4750 3000 50  0001 C CNN
	1    4750 3000
	-1   0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:GNDPWR-power-ICIO-2.1-colour-rescue #PWR0107
U 1 1 5DEF438B
P 2750 1200
F 0 "#PWR0107" H 2750 1000 50  0001 C CNN
F 1 "GNDPWR" H 2754 1274 50  0000 C CNN
F 2 "" H 2750 1150 50  0001 C CNN
F 3 "" H 2750 1150 50  0001 C CNN
	1    2750 1200
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:GNDPWR-power-ICIO-2.1-colour-rescue #PWR0108
U 1 1 5DEF99C6
P 2350 2050
F 0 "#PWR0108" H 2350 1850 50  0001 C CNN
F 1 "GNDPWR" H 2437 2010 50  0000 L CNN
F 2 "" H 2350 2000 50  0001 C CNN
F 3 "" H 2350 2000 50  0001 C CNN
	1    2350 2050
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:GNDPWR-power-ICIO-2.1-colour-rescue #PWR0111
U 1 1 5DEFFCB8
P 3950 1100
F 0 "#PWR0111" H 3950 900 50  0001 C CNN
F 1 "GNDPWR" H 3954 1174 50  0000 C CNN
F 2 "" H 3950 1050 50  0001 C CNN
F 3 "" H 3950 1050 50  0001 C CNN
	1    3950 1100
	1    0    0    -1  
$EndComp
Wire Wire Line
	3950 1100 3950 1050
$Comp
L ICIO-3-rescue:GNDPWR-power-ICIO-2.1-colour-rescue #PWR0112
U 1 1 5DF0A87D
P 3550 2800
F 0 "#PWR0112" H 3550 2600 50  0001 C CNN
F 1 "GNDPWR" V 3550 2350 50  0000 L CNN
F 2 "" H 3550 2750 50  0001 C CNN
F 3 "" H 3550 2750 50  0001 C CNN
	1    3550 2800
	0    1    1    0   
$EndComp
Wire Wire Line
	3600 3650 3600 3950
Wire Wire Line
	3400 3950 3600 3950
$Comp
L ICIO-3-rescue:R_Small-device-ICIO-2.1-colour-rescue R4
U 1 1 5D6BEB8C
P 2950 4150
F 0 "R4" V 3146 4150 50  0000 C CNN
F 1 "100k" V 3055 4150 50  0000 C CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" H 2950 4150 50  0001 C CNN
F 3 "" H 2950 4150 50  0001 C CNN
	1    2950 4150
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:OPA2134PA-dk_Linear-Amplifiers-Instrumentation-OP-Amps-Buffer-Amps-ICIO-2.1-colour-rescue U3
U 2 1 5D5FF41C
P 2450 3850
F 0 "U3" H 2794 3903 60  0000 L CNN
F 1 "2134" H 2794 3797 60  0000 L CNN
F 2 "digikey-footprints:DIP-8_W7.62mm" H 2650 4050 60  0001 L CNN
F 3 "http://www.ti.com/lit/ds/symlink/opa134.pdf" H 2650 4150 60  0001 L CNN
F 4 "OPA2134PA-ND" H 2650 4250 60  0001 L CNN "Digi-Key_PN"
F 5 "OPA2134PA" H 2650 4350 60  0001 L CNN "MPN"
F 6 "Integrated Circuits (ICs)" H 2650 4450 60  0001 L CNN "Category"
F 7 "Linear - Amplifiers - Instrumentation, OP Amps, Buffer Amps" H 2650 4550 60  0001 L CNN "Family"
F 8 "http://www.ti.com/lit/ds/symlink/opa134.pdf" H 2650 4650 60  0001 L CNN "DK_Datasheet_Link"
F 9 "/product-detail/en/texas-instruments/OPA2134PA/OPA2134PA-ND/254686" H 2650 4750 60  0001 L CNN "DK_Detail_Page"
F 10 "IC OPAMP AUDIO 8MHZ 8DIP" H 2650 4850 60  0001 L CNN "Description"
F 11 "Texas Instruments" H 2650 4950 60  0001 L CNN "Manufacturer"
F 12 "Active" H 2650 5050 60  0001 L CNN "Status"
	2    2450 3850
	-1   0    0    -1  
$EndComp
Wire Wire Line
	2100 3500 2200 3500
Connection ~ 2750 3500
Connection ~ 2100 3500
Connection ~ 5850 4200
Wire Wire Line
	5850 3750 5850 3500
Wire Wire Line
	5050 3850 5050 4200
Wire Wire Line
	5450 3300 6000 3300
Connection ~ 4000 3350
Wire Wire Line
	5000 2750 5000 2900
Wire Wire Line
	5000 3100 5000 2900
Connection ~ 5000 2900
Wire Wire Line
	4800 2900 4750 2900
Wire Wire Line
	4750 2900 4750 3000
Connection ~ 3600 3950
$Comp
L ICIO-3-rescue:GNDPWR-power-ICIO-2.1-colour-rescue #PWR0113
U 1 1 5E06CF12
P 3300 3400
F 0 "#PWR0113" H 3300 3200 50  0001 C CNN
F 1 "GNDPWR" H 3300 3250 50  0000 C CNN
F 2 "" H 3300 3350 50  0001 C CNN
F 3 "" H 3300 3350 50  0001 C CNN
	1    3300 3400
	1    0    0    -1  
$EndComp
Connection ~ 4100 3950
Wire Wire Line
	4100 3950 4150 3950
Wire Wire Line
	4000 3950 4100 3950
Wire Wire Line
	4100 3950 4100 4100
Wire Wire Line
	4100 4300 4100 4400
Wire Wire Line
	5300 3250 4900 3600
Wire Wire Line
	4900 3600 4900 3750
Wire Wire Line
	4900 3750 4200 3750
Wire Wire Line
	4600 3550 4200 3550
Wire Wire Line
	5050 3100 5000 3100
Wire Wire Line
	6000 2900 5650 2900
Wire Wire Line
	5550 2900 5550 2750
Wire Wire Line
	5300 3250 5300 3100
Wire Wire Line
	5250 3100 5300 3100
Connection ~ 5300 3100
Wire Wire Line
	5300 3100 6000 3100
Wire Wire Line
	5650 2900 5650 2650
Connection ~ 5650 2900
Wire Wire Line
	5650 2900 5550 2900
Wire Wire Line
	4600 2850 4600 3550
Wire Wire Line
	5050 2650 5650 2650
Wire Wire Line
	4600 2850 5050 2650
Wire Wire Line
	4050 1700 4100 1700
Wire Wire Line
	3700 1500 3900 1500
Wire Wire Line
	4100 1500 4100 1700
Connection ~ 4100 1700
Wire Wire Line
	4100 1700 4250 1700
Wire Wire Line
	3550 2350 3550 2500
Wire Wire Line
	3550 2200 3550 2350
Connection ~ 3550 2350
Wire Wire Line
	3900 2350 4100 2350
Wire Wire Line
	4100 2350 4200 2200
Connection ~ 4200 2200
Wire Wire Line
	4750 2300 4750 2200
Connection ~ 4750 2200
Wire Wire Line
	4200 2200 4500 2200
Wire Wire Line
	4500 2400 4500 2200
Connection ~ 4500 2200
Wire Wire Line
	4500 2200 4750 2200
Wire Wire Line
	4800 1800 4800 2000
Wire Wire Line
	4500 2000 4800 2000
Wire Wire Line
	5350 1700 5700 1700
Connection ~ 5550 2200
Wire Wire Line
	5550 2250 5550 2200
Wire Wire Line
	5550 2200 5850 2200
Wire Wire Line
	5050 2000 5700 2000
Wire Wire Line
	5400 2200 5550 2200
Wire Wire Line
	4850 2000 4800 2000
Connection ~ 4800 2000
Wire Wire Line
	4750 2200 5200 2200
Wire Wire Line
	1700 1400 1700 1650
Wire Wire Line
	2300 1400 2300 1550
NoConn ~ 2300 1550
$Comp
L ICIO-3-rescue:GNDPWR-power-ICIO-2.1-colour-rescue #PWR0114
U 1 1 5E2B70E7
P 3150 2050
F 0 "#PWR0114" H 3150 1850 50  0001 C CNN
F 1 "GNDPWR" H 3100 1900 50  0000 C CNN
F 2 "" H 3150 2000 50  0001 C CNN
F 3 "" H 3150 2000 50  0001 C CNN
	1    3150 2050
	1    0    0    -1  
$EndComp
Wire Wire Line
	3150 2050 3250 2050
Text Notes 900  6950 0    50   ~ 0
Bodge corrections over last batch:\nReconnected net: U3A feedback loop
Connection ~ 2300 1750
Wire Wire Line
	2300 1550 2300 1750
Wire Wire Line
	2000 1550 2350 1550
Wire Wire Line
	3700 4650 3700 4500
$Comp
L ICIO-3-rescue:CP1_Small-device-ICIO-2.1-colour-rescue C18
U 1 1 5DE81B88
P 3300 3950
F 0 "C18" V 3072 3950 50  0000 C CNN
F 1 "10u" V 3163 3950 50  0000 C CNN
F 2 "Capacitors_THT:CP_Radial_D10.0mm_P5.00mm" H 3300 3950 50  0001 C CNN
F 3 "" H 3300 3950 50  0001 C CNN
	1    3300 3950
	0    1    1    0   
$EndComp
Wire Wire Line
	2750 3950 2950 3950
Wire Wire Line
	2950 3950 2950 4050
Connection ~ 2950 3950
Wire Wire Line
	2950 3950 3200 3950
Wire Wire Line
	2950 4250 2950 4350
$Comp
L power:GNDA #PWR0116
U 1 1 5DE911DA
P 2950 4350
F 0 "#PWR0116" H 2950 4100 50  0001 C CNN
F 1 "GNDA" H 2955 4177 50  0000 C CNN
F 2 "" H 2950 4350 50  0001 C CNN
F 3 "" H 2950 4350 50  0001 C CNN
	1    2950 4350
	1    0    0    -1  
$EndComp
$Comp
L power:GNDA #PWR0117
U 1 1 5DEA066C
P 2750 2800
F 0 "#PWR0117" H 2750 2550 50  0001 C CNN
F 1 "GNDA" H 2755 2627 50  0000 C CNN
F 2 "" H 2750 2800 50  0001 C CNN
F 3 "" H 2750 2800 50  0001 C CNN
	1    2750 2800
	-1   0    0    1   
$EndComp
Wire Wire Line
	2750 2850 2750 2800
$Comp
L ICIO-3-rescue:POT_Dual_Separate-device-ICIO-2.1-colour-rescue RV2
U 1 1 5DEA589B
P 2500 3150
F 0 "RV2" V 2385 3150 50  0000 C CNN
F 1 "10k A" V 2294 3150 50  0000 C CNN
F 2 "digikey:PinHeader_1x3_P2.54mm_Drill1.02mm" H 2500 3150 50  0001 C CNN
F 3 "" H 2500 3150 50  0001 C CNN
	1    2500 3150
	0    -1   -1   0   
$EndComp
Wire Wire Line
	2100 3150 2250 3150
Wire Wire Line
	2500 3000 2250 3000
Wire Wire Line
	2250 3000 2250 3150
Connection ~ 2250 3150
Wire Wire Line
	2250 3150 2350 3150
Wire Wire Line
	2650 3150 2750 3150
Connection ~ 2750 3150
Wire Wire Line
	2750 3150 2750 3500
$Comp
L ICIO-3-rescue:POT_Dual_Separate-device-ICIO-2.1-colour-rescue RV1
U 1 1 5DEB9DD9
P 800 1850
F 0 "RV1" H 731 1896 50  0000 R CNN
F 1 "100K A" H 731 1805 50  0000 R CNN
F 2 "digikey:PinHeader_1x3_P2.54mm_Drill1.02mm" H 800 1850 50  0001 C CNN
F 3 "" H 800 1850 50  0001 C CNN
	1    800  1850
	1    0    0    -1  
$EndComp
$Comp
L power:GNDA #PWR0118
U 1 1 5DEC57BE
P 800 2050
F 0 "#PWR0118" H 800 1800 50  0001 C CNN
F 1 "GNDA" H 805 1877 50  0000 C CNN
F 2 "" H 800 2050 50  0001 C CNN
F 3 "" H 800 2050 50  0001 C CNN
	1    800  2050
	1    0    0    -1  
$EndComp
Wire Wire Line
	800  2050 800  2000
Wire Wire Line
	800  1700 800  1550
Wire Wire Line
	1400 1850 1700 1850
$Comp
L ICIO-3-rescue:CP1_Small-device-ICIO-2.1-colour-rescue C2
U 1 1 5DEF1D41
P 1150 1850
F 0 "C2" V 1378 1850 50  0000 C CNN
F 1 "10u" V 1287 1850 50  0000 C CNN
F 2 "Capacitors_THT:C_Rect_L13.0mm_W8.0mm_P10.00mm_FKS3_FKP3_MKS4" H 1150 1850 50  0001 C CNN
F 3 "" H 1150 1850 50  0001 C CNN
	1    1150 1850
	0    -1   -1   0   
$EndComp
Wire Wire Line
	1050 1850 950  1850
Wire Wire Line
	3100 1750 3100 1500
Connection ~ 3100 1750
Wire Wire Line
	3100 1750 3250 1750
$Comp
L ICIO-3-rescue:R_Small-device-ICIO-2.1-colour-rescue R6
U 1 1 5DEFD301
P 3100 1400
F 0 "R6" H 3159 1446 50  0000 L CNN
F 1 "4k7" H 3159 1355 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" H 3100 1400 50  0001 C CNN
F 3 "" H 3100 1400 50  0001 C CNN
	1    3100 1400
	1    0    0    -1  
$EndComp
Text GLabel 3100 1200 1    50   Output ~ 0
BusFeed
Wire Wire Line
	3100 1300 3100 1200
Text GLabel 6000 3200 0    50   Output ~ 0
BusFeed
Wire Wire Line
	4500 1500 4500 1600
$Comp
L power:VEE #PWR021
U 1 1 5D7228CB
P 4500 1500
F 0 "#PWR021" H 4500 1350 50  0001 C CNN
F 1 "VEE" H 4517 1673 50  0000 C CNN
F 2 "" H 4500 1500 50  0001 C CNN
F 3 "" H 4500 1500 50  0001 C CNN
	1    4500 1500
	1    0    0    -1  
$EndComp
$Comp
L ICIO-3-rescue:D_Small-device-ICIO-2.1-colour-rescue D3
U 1 1 59C1D905
P 4500 1700
F 0 "D3" H 4450 1780 50  0000 L CNN
F 1 "1n4004" H 4350 1620 50  0000 L CNN
F 2 "Diodes_THT:D_DO-41_SOD81_P10.16mm_Horizontal" V 4500 1700 50  0001 C CNN
F 3 "" V 4500 1700 50  0001 C CNN
	1    4500 1700
	0    -1   -1   0   
$EndComp
Wire Wire Line
	3900 4500 3700 4500
Wire Wire Line
	3900 3950 3900 4500
Text Notes 6300 3650 0    50   ~ 0
15 +48VDC 
Text Notes 6300 3550 0    50   ~ 0
 14 -16VDC 
Text Notes 6300 3450 0    50   ~ 0
13 POWER SUPPLY COMMON
Text Notes 6300 3350 0    50   ~ 0
 12 +16VDC
Text Notes 6300 3250 0    50   ~ 0
11 GAIN TRIM RESISTOR\n
Text Notes 6350 3150 0    50   ~ 0
10 INPUT+ (+4 LEVEL)
Text Notes 6300 3050 0    50   ~ 0
9 INPUT+ (-2 LEVEL)\n
Text Notes 6350 2950 0    50   ~ 0
8 INPUT- (+4 LEVEL)
Text Notes 6300 2850 0    50   ~ 0
7 INPUT- (-2 LEVEL)
Text Notes 6350 2750 0    50   ~ 0
6 525 STEREO LINK
Text Notes 6300 2650 0    50   ~ 0
5 AUDIO COMMON
Text Notes 6300 2550 0    50   ~ 0
 4 OUTPUT -
Text Notes 6250 2450 0    50   ~ 0
 3 OUTPUT + (-2 LEVEL)
Text Notes 6350 2350 0    50   ~ 0
2 OUTPUT + (+4 LEVEL)
Text Notes 6300 2250 0    50   ~ 0
1 CHASSIS GROUND
$EndSCHEMATC
