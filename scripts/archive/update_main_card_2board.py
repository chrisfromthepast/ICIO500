"""
Main card update for the 2-board architecture (2.0 mm active faceplate).

1. Front ears X 55.390 -> 54.175, recess X 57.390 -> 56.175  (VPR depth 5.938" preserved)
2. MH1/MH2 X 58.390 -> 57.175 (3.00 mm behind faceplate rear face = Wurth bracket hole axis)
3. U6: replace mis-drawn footprint (straight-header graphics + 0.5x-scaled model) with the true
   KiCad PinHeader_2x10_P2.54mm_Horizontal (identical pad pattern), model at 1:1 scale.
4. U6: move pad 1 from X 68.000 -> 70.000 so the collar clears the 8.5 mm socket by 0.75 mm.
   Tracks/vias are moved with a continuous point warp (every point maps deterministically,
   so all connections are preserved).
"""
import pcbnew

PCB = 'build/icio500/icio500.kicad_pcb'
b = pcbnew.LoadBoard(PCB)
MM = 1e6
def nm(v): return int(round(v * MM))

# ---------- 1. Edge cuts ----------
remap = {55.39: 54.175, 57.39: 56.175}
for d in b.GetDrawings():
    if d.GetLayerName() != 'Edge.Cuts' or not hasattr(d, 'GetStart'):
        continue
    s, e = d.GetStart(), d.GetEnd()
    def fx(x):
        for k, v in remap.items():
            if abs(x / MM - k) < 0.01:
                return nm(v)
        return x
    d.SetStart(pcbnew.VECTOR2I(fx(s.x), s.y))
    d.SetEnd(pcbnew.VECTOR2I(fx(e.x), e.y))

# ---------- 2. Mounting holes ----------
for ref in ('MH1', 'MH2'):
    fp = b.FindFootprintByReference(ref)
    p = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(nm(57.175), p.y))

# ---------- 3. U6 footprint swap ----------
old = b.FindFootprintByReference('U6')
old_pos = old.GetPosition()
old_rot = old.GetOrientation()
netmap = {p.GetNumber(): p.GetNet() for p in old.Pads()}
fields = {f.GetName(): f.GetText() for f in old.GetFields()}
libdir = r'C:\Program Files\KiCad\10.0\share\kicad\footprints\Connector_PinHeader_2.54mm.pretty'
new = pcbnew.FootprintLoad(libdir, 'PinHeader_2x10_P2.54mm_Horizontal')
new.SetReference('U6')
new.SetValue('2541WR-2x10P')
for k, v in fields.items():
    if k not in ('Reference', 'Value', 'Footprint', 'Datasheet', 'Description') and v:
        new.SetField(k, v)
new.SetPosition(old_pos)
new.SetOrientation(old_rot)
for p in new.Pads():
    if p.GetNumber() in netmap:
        p.SetNet(netmap[p.GetNumber()])
for m in new.Models():
    m.m_Filename = '${KICAD10_3DMODEL_DIR}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_2x10_P2.54mm_Horizontal.step'
    m.m_Scale = pcbnew.VECTOR3D(1, 1, 1)
b.Remove(old)
b.Add(new)
u6 = new

# ---------- 4. Move U6 +2.0 mm with continuous warp ----------
DX = 2.0
def ramp(v, full_lo, full_hi, fade):
    if full_lo <= v <= full_hi:
        return 1.0
    if v < full_lo:
        return max(0.0, 1 - (full_lo - v) / fade)
    return max(0.0, 1 - (v - full_hi) / fade)
def warp_x(x, y):
    xm, ym = x / MM, y / MM
    fx = 1.0 if xm <= 70.5 else max(0.0, 1 - (xm - 70.5) / 16.0)   # fade out by X=86.5
    fy = ramp(ym, 97.0, 125.5, 6.0)
    return x + nm(DX * fx * fy)

u6.SetPosition(pcbnew.VECTOR2I(old_pos.x + nm(DX), old_pos.y))
moved = 0
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        p = t.GetPosition()
        nx = warp_x(p.x, p.y)
        if nx != p.x:
            t.SetPosition(pcbnew.VECTOR2I(nx, p.y)); moved += 1
    else:
        s, e = t.GetStart(), t.GetEnd()
        ns, ne = warp_x(s.x, s.y), warp_x(e.x, e.y)
        if ns != s.x or ne != e.x:
            t.SetStart(pcbnew.VECTOR2I(ns, s.y)); t.SetEnd(pcbnew.VECTOR2I(ne, e.y)); moved += 1
print('tracks/vias warped:', moved)

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
print('U6 pad1 now at', [(p.GetNumber(), p.GetPosition().x / MM, p.GetPosition().y / MM) for p in u6.Pads() if p.GetNumber() in ('1', '2')])
print('MH1', b.FindFootprintByReference('MH1').GetPosition().x / MM)
