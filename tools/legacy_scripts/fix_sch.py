import re

with open('build/icio500/faceplate_logic.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('Local:IS31FL3236', 'Driver_LED:IS31FL3236-TQ')
text = text.replace('Local:C', 'Device:C_Small')
text = text.replace('Local:R', 'Device:R_Small')
text = text.replace('Local:LED', 'Device:LED_Small')
text = text.replace('Local:Ferrite_Bead', 'Device:Ferrite_Bead_Small')
text = text.replace('Local:JST_SH_8', 'Connector_Generic:Conn_01x08')
text = text.replace('Local:EC11E_Encoder', 'Device:RotaryEncoder_Switch')

with open('build/icio500/faceplate_logic.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(text)
    
print("Replaced all Local libraries with KiCad standard libraries in schematic!")
