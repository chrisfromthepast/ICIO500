import pcbnew
import sys

board_path = 'build/icio500/icio500.kicad_pcb'
board = pcbnew.LoadBoard(board_path)

bbox = board.GetBoardEdgesBoundingBox()
bbox.Inflate(pcbnew.FromMM(1))

# Create rule area to prevent routing on In1.Cu
rule_area = pcbnew.ZONE(board)
rule_area.SetLayer(pcbnew.In1_Cu)
rule_area.SetIsRuleArea(True)
rule_area.SetDoNotAllowTracks(True)
rule_area.SetDoNotAllowVias(False)
rule_area.SetDoNotAllowZoneFills(False)
rule_area.SetDoNotAllowPads(False)
rule_area.SetDoNotAllowFootprints(False)

poly = pcbnew.SHAPE_POLY_SET()
poly.NewOutline()
poly.Append(bbox.GetX(), bbox.GetY())
poly.Append(bbox.GetRight(), bbox.GetY())
poly.Append(bbox.GetRight(), bbox.GetBottom())
poly.Append(bbox.GetX(), bbox.GetBottom())

rule_area.AddPolygon(poly.Outline(0))

board.Add(rule_area)

# Also let's unfill the ground plane again just in case
for zone in board.Zones():
    if not zone.GetIsRuleArea():
        zone.UnFill()

pcbnew.SaveBoard(board_path, board)
print("Added trace keepout to In1.Cu")
