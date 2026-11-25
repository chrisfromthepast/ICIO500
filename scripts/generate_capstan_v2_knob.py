"""
Parametric 3D CAD Generator for the ICIO500 "Wide-Skirt Capstan v2" Encoder Knob.
Features a sleek solid closed-cap 8-fluted studio grip with subtle concave push-click
thumb dish and bold 12 o'clock pointer trench, flaring smoothly into a Ø25.20 mm circular
light-shielding hood (+1.40 mm radial overhang past D11..D16 LED ports) with a 45-degree
internal light-bounce cone and a zero-shim D-bore matched to Bourns PEC11R-4020F-S0024.

Outputs:
  - fabrication/satellite_faceplate/jlc3dp_knob_v2/icio500_capstan_v2_knob.stl
  - fabrication/satellite_faceplate/jlc3dp_knob_v2/icio500_capstan_v2_knob.step
"""

import math
import os
import struct
import numpy as np


# -----------------------------------------------------------------------------
# Exact Dimensional Parameters (mm) — Bourns PEC11R-4020F-S0024 (20 mm Shaft)
# Zero bore shim over: 0.80 mm Sat PCB + 0.15 mm Diffuser + 3.20 mm Walnut = 4.15 mm
# Exposed shaft = 15.85 mm -> 1.50 mm hover gap (1.00 mm clicked) -> D_BORE_TOP_Z = 14.35 mm
# -----------------------------------------------------------------------------
SKIRT_BASE_R = 12.60         # Ø25.20 mm light-shielding hood (+1.40 mm past D11..D16 R=11.20 rims)
SKIRT_CHAMFER_R = 12.40      # Subtle 0.20 mm bottom edge break at Z = 0.00 mm
SKIRT_CHAMFER_Z = 0.25       # Bottom edge bevel height
SKIRT_APR_TOP_Z = 1.50       # Top of pure circular hood apron (Z = 0.25..1.50 mm)
SKIRT_FLARE_TOP_Z = 6.20     # Smooth sweeping flare merges into Ø16.80 mm fluted barrel
SPOKE_BARREL_R = 8.40        # Ø16.80 mm upper fluted grip envelope (Z = 6.20..18.65 mm)
VALLEY_MIN_R_BARREL = 6.20   # Fuller 2.20 mm axial flutes along barrel perimeter

BARREL_TOP_Z = 18.65         # Outer top chamfer base around fluted planform
TOP_Z = 19.00                # Outer flat bezel deck (4.20 mm solid center wall over bore)
DISH_R = 4.60                # Ø9.20 mm central push-click concave thumb dish
DISH_DEPTH = 0.45            # Center sits at Z = 18.55 mm (>= 3.85 mm solid nylon over bore)

# Cross-Sectional Spoke & Flute Angles (relative to nearest k*45° rib)
SPOKE_FLAT_DEG = 4.0         # Non-pointer rib flat half-angle
SPOKE_BEVEL_DEG = 6.8        # Non-pointer rib side bevel outer angle
SPOKE_12_FLAT_DEG = 10.7     # Widened +90° pointer rib flat half-angle
SPOKE_12_BEVEL_DEG = 13.5    # Widened +90° pointer rib side bevel outer angle
OCT_SHOULDER_DEG = 15.5      # Flute facet transition angle
OCT_FLUTE_FLOOR_DEG = 18.0   # Central axial flute floor angle

GROOVE_HALF_W_RIM = 0.50     # 1.00 mm wide flared light-catching top rim
GROOVE_HALF_W_FLR = 0.30     # 0.60 mm flat white indicator bottom
GROOVE_DEPTH_CROWN = 0.95    # 0.95 mm deep sight trench across closed top cap (R >= 2.20)
GROOVE_DEPTH_WALL = 1.05     # 1.05 mm deep sight trench down +90° rib & upper flare

# Under-Skirt 45° Optical Reflector Cavity & Zero-Shim D-Bore
REFLECTOR_OUTER_R = 11.25    # Bottom inner rim (1.15 mm solid base wall >= 1.0 mm PA12 DFM)
REFLECTOR_INNER_R = 7.20     # Top of 45° light-bounce cone (clears Ø12.60 mm M7 hex nut)
REFLECTOR_TOP_Z = 4.20       # Deflects upward LED light radially out through 1.50 mm gap
COLLAR_R = 3.15              # Ø6.30 mm clearance around unflatted 6 mm shaft collar
COLLAR_BOT_Z = 5.20          # Conical transition 4.20 -> 5.20 mm
D_BORE_LEADIN_Z = 5.50       # 0.30 mm entry chamfer into D-shaft interference fit
D_BORE_TOP_Z = 14.35         # Exact zero-shim stop for 20 mm PEC11R over 4.15 mm stackup
D_BORE_R = 3.03              # Ø6.06 mm base bore for MJF PA12 press fit
D_FLAT_Y = 1.50              # 4.50 mm across flat (Y = +1.50 mm, aligned to +Y pointer)
CRUSH_RIB_ANGLES_DEG = (-90.0, -35.0, -145.0)
CRUSH_RIB_PROTRUSION = 0.12  # 0.12 mm inward crush rib (peaks at R = 2.91 mm)
CRUSH_RIB_HALF_WIDTH = 0.25  # 0.50 mm wide rib


def build_base_angles():
    """
    Create sorted base angles in degrees across [0, 360), combining a 2.0-degree base
    grid with exact feature pins for all 8 spoke blades, octagram shoulders, light flute
    corners, D-flat tangent corners, 3 crush ribs, and the 11-point pointer stencil.
    """
    protected = []

    s12_lo = 90.0 - SPOKE_12_BEVEL_DEG
    s12_hi = 90.0 + SPOKE_12_BEVEL_DEG
    s12_f0 = 90.0 - SPOKE_12_FLAT_DEG
    s12_f1 = 90.0 + SPOKE_12_FLAT_DEG
    protected.extend([
        s12_lo, s12_f0,
        90.0 - 0.75 * SPOKE_12_FLAT_DEG, 90.0 - 0.50 * SPOKE_12_FLAT_DEG, 90.0 - 0.25 * SPOKE_12_FLAT_DEG,
        90.0,
        90.0 + 0.25 * SPOKE_12_FLAT_DEG, 90.0 + 0.50 * SPOKE_12_FLAT_DEG, 90.0 + 0.75 * SPOKE_12_FLAT_DEG,
        s12_f1, s12_hi,
    ])

    flat_ang = math.degrees(math.asin(D_FLAT_Y / D_BORE_R))
    protected.extend([flat_ang, 180.0 - flat_ang])
    for a in [35.0, 42.0, 138.0, 145.0]:
        protected.append(a)

    rib_half_deg = math.degrees(CRUSH_RIB_HALF_WIDTH / D_BORE_R)
    for center_deg in CRUSH_RIB_ANGLES_DEG:
        c = center_deg % 360.0
        for frac in (-1.0, -0.6, -0.25, 0.0, 0.25, 0.6, 1.0):
            protected.append(c + frac * rib_half_deg)

    for k in range(8):
        sc = k * 45.0
        protected.append(sc)
        if k == 2:
            for d in (-OCT_SHOULDER_DEG, -OCT_FLUTE_FLOOR_DEG, OCT_SHOULDER_DEG, OCT_FLUTE_FLOOR_DEG):
                protected.append((sc + d) % 360.0)
        else:
            for d in (-SPOKE_FLAT_DEG, SPOKE_FLAT_DEG, -SPOKE_BEVEL_DEG, SPOKE_BEVEL_DEG,
                      -OCT_SHOULDER_DEG, OCT_SHOULDER_DEG, -OCT_FLUTE_FLOOR_DEG, OCT_FLUTE_FLOOR_DEG):
                ang = (sc + d) % 360.0
                if not (s12_lo - 0.01 <= ang <= s12_hi + 0.01):
                    protected.append(ang)
        protected.append((22.5 + k * 45.0) % 360.0)

    protected = [p % 360.0 for p in protected]
    protected.sort()
    clean_prot = []
    for p in protected:
        if not clean_prot or abs(p - clean_prot[-1]) > 0.02:
            clean_prot.append(p)
    if clean_prot and clean_prot[-1] > 359.98:
        clean_prot.pop()

    angles = list(clean_prot)
    for a in np.arange(0.0, 360.0, 2.0):
        if s12_lo - 0.01 <= a <= s12_hi + 0.01:
            continue
        if min(abs(((a - p) + 180.0) % 360.0 - 180.0) for p in clean_prot) >= 0.45:
            angles.append(float(a))

    angles.sort()
    idx_left = min(range(len(angles)), key=lambda i: abs(angles[i] - s12_lo))
    idx_90 = min(range(len(angles)), key=lambda i: abs(angles[i] - 90.0))
    idx_right = min(range(len(angles)), key=lambda i: abs(angles[i] - s12_hi))
    assert idx_90 - idx_left == 5 and idx_right - idx_90 == 5, (
        f"Stencil mismatch: idx_left={idx_left}, idx_90={idx_90}, idx_right={idx_right}"
    )

    return np.array(angles, dtype=np.float64), idx_left, idx_90, idx_right


def r_spoke_env(z):
    """Outer envelope radius of the 8 spoke blades blending smoothly into Ø25.20 mm circular hood."""
    if z <= 1e-6:
        return SKIRT_CHAMFER_R
    elif z <= SKIRT_CHAMFER_Z:
        t = z / SKIRT_CHAMFER_Z
        return SKIRT_CHAMFER_R + t * (SKIRT_BASE_R - SKIRT_CHAMFER_R)
    elif z <= SKIRT_APR_TOP_Z:
        return SKIRT_BASE_R
    elif z < SKIRT_FLARE_TOP_Z:
        t = (SKIRT_FLARE_TOP_Z - z) / (SKIRT_FLARE_TOP_Z - SKIRT_APR_TOP_Z)
        s = t * t * (3.0 - 2.0 * t)
        return SPOKE_BARREL_R + s * (SKIRT_BASE_R - SPOKE_BARREL_R)
    else:
        return SPOKE_BARREL_R


def r_valley_env(z):
    """Core floor envelope of the 8 axial light flutes feathering out into Ø25.20 mm circular hood."""
    if z <= 1e-6:
        return SKIRT_CHAMFER_R
    elif z <= SKIRT_CHAMFER_Z:
        t = z / SKIRT_CHAMFER_Z
        return SKIRT_CHAMFER_R + t * (SKIRT_BASE_R - SKIRT_CHAMFER_R)
    elif z <= SKIRT_APR_TOP_Z:
        return SKIRT_BASE_R
    elif z < SKIRT_FLARE_TOP_Z:
        t = (SKIRT_FLARE_TOP_Z - z) / (SKIRT_FLARE_TOP_Z - SKIRT_APR_TOP_Z)
        s = t ** 0.85
        return VALLEY_MIN_R_BARREL + s * (SKIRT_BASE_R - VALLEY_MIN_R_BARREL)
    else:
        return VALLEY_MIN_R_BARREL


def barrel_wheel_r(theta_deg, z):
    """3D ship's-wheel octagram tower flaring seamlessly into circular Ø25.20 mm hood skirt."""
    r_sp = r_spoke_env(z)
    r_val = r_valley_env(z)
    if abs(r_sp - r_val) <= 1e-7:
        return r_sp

    r_oct_corner = r_val + 0.62 * (r_sp - r_val)
    r_mid = r_val + 0.28 * (r_sp - r_val)

    nearest_spoke_idx = round(theta_deg / 45.0) % 8
    delta = abs(((theta_deg - nearest_spoke_idx * 45.0) + 180.0) % 360.0 - 180.0)

    if nearest_spoke_idx == 2:
        d0, d1 = SPOKE_12_FLAT_DEG, SPOKE_12_BEVEL_DEG
    else:
        d0, d1 = SPOKE_FLAT_DEG, SPOKE_BEVEL_DEG

    if delta <= d0:
        return r_sp
    elif delta <= d1:
        t = (delta - d0) / (d1 - d0)
        return r_sp + t * (r_oct_corner - r_sp)
    elif delta <= OCT_SHOULDER_DEG:
        t = (delta - d1) / (OCT_SHOULDER_DEG - d1)
        return r_oct_corner + t * (r_mid - r_oct_corner)
    elif delta <= OCT_FLUTE_FLOOR_DEG:
        t = (delta - OCT_SHOULDER_DEG) / (OCT_FLUTE_FLOOR_DEG - OCT_SHOULDER_DEG)
        return r_mid + t * (r_val - r_mid)
    else:
        return r_val


def top_cap_z(r):
    """Solid closed architectural top deck with subtle central concave push-click thumb dish."""
    if r >= DISH_R:
        return TOP_Z
    u = r / DISH_R
    return TOP_Z - DISH_DEPTH * (1.0 - u * u)


def inner_bore_radius(theta_deg, r_cyl, use_d_flat, rib_weight):
    """Exact inner bore polar radius at angle theta_deg (D-flat at Y=+1.50 and 3 crush ribs)."""
    r = r_cyl
    if use_d_flat:
        s = math.sin(math.radians(theta_deg))
        if s > 1e-6:
            r_flat = D_FLAT_Y / s
            if r_flat < r:
                r = r_flat

    if rib_weight > 0.0:
        rib_half_deg = math.degrees(CRUSH_RIB_HALF_WIDTH / D_BORE_R)
        for center_deg in CRUSH_RIB_ANGLES_DEG:
            d = abs(((theta_deg - center_deg) + 180.0) % 360.0 - 180.0)
            if d < rib_half_deg:
                u = d / rib_half_deg
                protrusion = CRUSH_RIB_PROTRUSION * math.sqrt(max(0.0, 1.0 - u * u))
                r -= rib_weight * protrusion
    return r


def build_knob_mesh():
    """
    Construct a watertight closed 2-manifold triangle mesh of the Wide-Skirt Capstan v2 Knob.
    Returns (vertices, faces, face_tags).
    """
    base_angles, idx_left, idx_90, idx_right = build_base_angles()
    N = len(base_angles)
    crown_warp_r0 = 5.20

    outer_profile = [
        # Closed solid central push-click thumb dish (R <= 4.60 mm)
        ('pole_top', 0.00, TOP_Z - DISH_DEPTH, 'none'),
        ('crown', 0.80, None, 'none'),
        ('crown', 1.60, None, 'none'),
        ('crown', 2.00, None, 'none'),
        # 12 o'clock sight-line pointer trench starts cleanly at R = 2.20 mm on closed cap
        ('crown', 2.20, None, 'groove_top'),
        ('crown', 2.90, None, 'groove_top'),
        ('crown', 3.70, None, 'groove_top'),
        ('crown', DISH_R, None, 'groove_top'),
        # Flat closed bezel ring from R = 4.60 out to 5.20 mm, warping cleanly to perimeter chamfer
        ('crown', crown_warp_r0, None, 'groove_top'),
        ('crown_warp', 0.35, None, 'groove_top'),
        ('crown_warp', 0.70, None, 'groove_top'),
        ('crown_warp', 1.00, None, 'groove_top'),
        # Top bevel -> 8-fluted barrel (18.65 -> 6.20) -> dense flared skirt (5.20 -> 0.00)
        ('wall_bevel', None, BARREL_TOP_Z, 'groove_wall'),
        ('wall', None, 17.00, 'groove_wall'),
        ('wall', None, 11.50, 'groove_wall'),
        ('wall', None, SKIRT_FLARE_TOP_Z, 'groove_wall'),
        ('skirt', None, 5.20, 'groove_wall'),
        ('skirt', None, 4.20, 'groove_wall'),
        ('skirt', None, 3.30, 'groove_wall'),
        ('skirt', None, 2.40, 'groove_wall'),
        ('skirt', None, SKIRT_APR_TOP_Z, 'none'),
        ('skirt', None, SKIRT_CHAMFER_Z, 'none'),
        ('skirt', None, 0.00, 'none'),
    ]

    inner_profile = [
        # Bottom outer reflector edge (Z=0.00, 1.15 mm solid rim wall inside 12.40 chamfer)
        ('bore', REFLECTOR_OUTER_R, 0.00, False, 0.0),
        # 45-degree under-skirt optical light-bounce dome up to (R=7.20, Z=4.20 mm)
        ('bore', REFLECTOR_INNER_R, REFLECTOR_TOP_Z, False, 0.0),
        # Conical transition up to collar clearance (4.20 -> 5.20 mm)
        ('bore', COLLAR_R, COLLAR_BOT_Z, False, 0.0),
        # 0.30 mm chamfered lead-in to D-flat & crush ribs (5.20 -> 5.50 mm)
        ('bore', D_BORE_R, D_BORE_LEADIN_Z, True, 1.0),
        # 8.85 mm D-shaft engagement bore up to zero-shim ceiling Z = 14.35 mm
        ('bore', D_BORE_R, D_BORE_TOP_Z, True, 1.0),
        # Inner ceiling pole
        ('pole_ceil', 0.00, D_BORE_TOP_Z, True, 0.0),
    ]

    rings = []
    ring_groove_masks = []
    ring_groove_modes = []
    top_pole = None
    ceil_pole = None

    def make_ring_angles(r_rim_ref, r_flr_ref, mode):
        ang = base_angles.copy()
        if mode == 'none':
            assert np.all(np.diff(ang) > 0.01), "Non-monotonic base angles"
            return ang, set()

        a_rim = math.degrees(math.asin(min(0.95, GROOVE_HALF_W_RIM / max(2.00, r_rim_ref))))
        a_flr = math.degrees(math.asin(min(0.90, GROOVE_HALF_W_FLR / max(1.80, r_flr_ref))))

        a_rim = min(a_rim, SPOKE_12_FLAT_DEG + 1.0)
        a_flr = min(a_flr, a_rim - 0.35)
        left_shoulder = 90.0 - SPOKE_12_FLAT_DEG
        right_shoulder = 90.0 + SPOKE_12_FLAT_DEG
        s12_lo = 90.0 - SPOKE_12_BEVEL_DEG
        s12_hi = 90.0 + SPOKE_12_BEVEL_DEG
        ang[idx_90 - 5] = s12_lo
        ang[idx_90 - 4] = left_shoulder if (90.0 - a_rim) >= (left_shoulder + 0.35) else 0.5 * (s12_lo + (90.0 - a_rim))
        ang[idx_90 - 3] = 90.0 - a_rim
        ang[idx_90 - 2] = 90.0 - a_flr
        ang[idx_90 - 1] = 90.0 - 0.5 * a_flr
        ang[idx_90] = 90.0
        ang[idx_90 + 1] = 90.0 + 0.5 * a_flr
        ang[idx_90 + 2] = 90.0 + a_flr
        ang[idx_90 + 3] = 90.0 + a_rim
        ang[idx_90 + 4] = right_shoulder if (90.0 + a_rim) <= (right_shoulder - 0.35) else 0.5 * ((90.0 + a_rim) + s12_hi)
        ang[idx_90 + 5] = s12_hi

        assert np.all(np.diff(ang) > 0.01), f"Non-monotonic ring angles at r_rim_ref={r_rim_ref:.2f}"
        g_quads = set(range(idx_90 - 3, idx_90 + 3))
        return ang, g_quads

    groove_wall_r_top = SPOKE_BARREL_R - GROOVE_DEPTH_WALL - 0.05  # 7.30 mm

    for kind, param, z_val, gmode in outer_profile:
        if kind == 'pole_top':
            top_pole = np.array([0.0, 0.0, z_val], dtype=np.float64)
            continue

        if kind == 'crown':
            r_rim_ref = param
            r_flr_ref = param - 0.40
        elif kind == 'crown_warp':
            r_rim_ref = crown_warp_r0 + param * ((SPOKE_BARREL_R - 0.35) - crown_warp_r0)
            r_flr_ref = crown_warp_r0 + param * (groove_wall_r_top - crown_warp_r0)
        else:
            r_rim_ref = r_spoke_env(z_val)
            r_flr_ref = r_rim_ref - GROOVE_DEPTH_WALL

        ang_arr, g_quads = make_ring_angles(r_rim_ref, r_flr_ref, gmode)
        pts = np.zeros((N, 3), dtype=np.float64)
        prev_ring = rings[-1] if rings else None

        for i in range(N):
            th = ang_arr[i]
            th_rad = math.radians(th)
            in_groove_floor = (idx_90 - 2 <= i <= idx_90 + 2)

            if kind == 'crown':
                r_pt = param
                z_pt = top_cap_z(r_pt)
                if gmode == 'groove_top' and in_groove_floor:
                    z_pt -= GROOVE_DEPTH_CROWN
            elif kind == 'crown_warp':
                r_top_edge = max(5.40, barrel_wheel_r(th, BARREL_TOP_Z) - 0.35)
                r_pt = crown_warp_r0 + param * (r_top_edge - crown_warp_r0)
                z_pt = TOP_Z
                if in_groove_floor:
                    r_pt = crown_warp_r0 + param * (groove_wall_r_top - crown_warp_r0)
                    z_pt = TOP_Z - GROOVE_DEPTH_CROWN
            elif kind in ('wall_bevel', 'wall', 'skirt'):
                r_f = barrel_wheel_r(th, z_val)
                z_pt = z_val
                if kind == 'wall_bevel' and prev_ring is not None:
                    z_pt = min(z_val, float(prev_ring[i, 2]) - 0.25)
                if gmode == 'groove_wall' and in_groove_floor:
                    r_sp = r_spoke_env(z_val)
                    a_flr_deg = 90.0 - ang_arr[idx_90 - 2]
                    y_flr = (r_sp - GROOVE_DEPTH_WALL) * math.cos(math.radians(a_flr_deg))
                    r_pt = min(r_f, y_flr / math.sin(th_rad))
                else:
                    r_pt = r_f
            pts[i] = [r_pt * math.cos(th_rad), r_pt * math.sin(th_rad), z_pt]

        rings.append(pts)
        ring_groove_masks.append(g_quads if gmode != 'none' else set())
        ring_groove_modes.append(gmode)

    num_outer_rings = len(rings)

    for kind, r_fixed, z_val, use_flat, rib_w in inner_profile:
        if kind == 'pole_ceil':
            ceil_pole = np.array([0.0, 0.0, z_val], dtype=np.float64)
            continue

        ang_arr = base_angles.copy()
        pts = np.zeros((N, 3), dtype=np.float64)
        for i in range(N):
            th = ang_arr[i]
            th_rad = math.radians(th)
            r_pt = inner_bore_radius(th, r_fixed, use_flat, rib_w)
            pts[i] = [r_pt * math.cos(th_rad), r_pt * math.sin(th_rad), z_val]
        rings.append(pts)
        ring_groove_masks.append(set())
        ring_groove_modes.append('none')

    M = len(rings)
    vertices = np.vstack(rings + [top_pole.reshape(1, 3), ceil_pole.reshape(1, 3)])
    top_pole_idx = M * N
    ceil_pole_idx = M * N + 1

    faces = []
    face_tags = []

    for i in range(N):
        ni = (i + 1) % N
        faces.append([top_pole_idx, i, ni])
        face_tags.append('body')

    for m in range(M - 1):
        base_a = m * N
        base_b = (m + 1) * N
        g_mask_a = ring_groove_masks[m]
        g_mask_b = ring_groove_masks[m + 1]
        # Paint groove white only where both bounding rings carry an active groove
        is_groove_strip = (m < num_outer_rings - 1) and bool(g_mask_a and g_mask_b)
        active_g = g_mask_a & g_mask_b

        for i in range(N):
            ni = (i + 1) % N
            a0 = base_a + i
            a1 = base_a + ni
            b0 = base_b + i
            b1 = base_b + ni
            tag = 'groove' if (is_groove_strip and i in active_g) else 'body'
            faces.append([a0, b0, b1])
            face_tags.append(tag)
            faces.append([a0, b1, a1])
            face_tags.append(tag)

    last_base = (M - 1) * N
    for i in range(N):
        ni = (i + 1) % N
        faces.append([last_base + ni, last_base + i, ceil_pole_idx])
        face_tags.append('body')

    faces = np.array(faces, dtype=np.int32)
    return vertices, faces, face_tags


def inner_reflector_r_at_z(z):
    """Exact inner bore/reflector dome radius at height Z (mm)."""
    if z <= 0.0:
        return REFLECTOR_OUTER_R
    elif z <= REFLECTOR_TOP_Z:
        t = z / REFLECTOR_TOP_Z
        return REFLECTOR_OUTER_R + t * (REFLECTOR_INNER_R - REFLECTOR_OUTER_R)
    elif z <= COLLAR_BOT_Z:
        t = (z - REFLECTOR_TOP_Z) / (COLLAR_BOT_Z - REFLECTOR_TOP_Z)
        return REFLECTOR_INNER_R + t * (COLLAR_R - REFLECTOR_INNER_R)
    elif z <= D_BORE_LEADIN_Z:
        t = (z - COLLAR_BOT_Z) / (D_BORE_LEADIN_Z - COLLAR_BOT_Z)
        return COLLAR_R + t * (D_BORE_R - COLLAR_R)
    else:
        return D_BORE_R


def verify_manifold_and_stats(vertices, faces):
    """Run strict topological manifold, bounding box, and DFM wall-thickness checks."""
    edge_counts = {}
    edge_undir = {}
    signed_vol = 0.0
    zero_area_tris = 0

    for tri in faces:
        i0, i1, i2 = int(tri[0]), int(tri[1]), int(tri[2])
        v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]
        cross = np.cross(v1 - v0, v2 - v0)
        area = 0.5 * np.linalg.norm(cross)
        if area < 1e-10:
            zero_area_tris += 1
        signed_vol += np.dot(v0, np.cross(v1, v2)) / 6.0

        for u, v in ((i0, i1), (i1, i2), (i2, i0)):
            edge_counts[(u, v)] = edge_counts.get((u, v), 0) + 1
            key = (u, v) if u < v else (v, u)
            edge_undir[key] = edge_undir.get(key, 0) + 1

    boundary_edges = sum(1 for (u, v), c in edge_counts.items() if c != 1 or edge_counts.get((v, u), 0) != 1)
    non_manifold_edges = sum(1 for c in edge_undir.values() if c != 2)
    euler = len(vertices) - len(edge_undir) + len(faces)

    mins = vertices.min(axis=0)
    maxs = vertices.max(axis=0)
    dims = maxs - mins
    vol_cm3 = signed_vol / 1000.0
    mass_g = vol_cm3 * 1.01

    # Verify minimum radial wall thickness along skirt & reflector cone (including +90° groove)
    min_wall = 1e9
    for z in (0.0, 0.25, 1.50, 2.40, 3.30, 4.20, 5.20, 6.20):
        r_in = inner_reflector_r_at_z(z)
        for th in range(0, 360, 5):
            r_out = barrel_wheel_r(float(th), z)
            if th == 90 and 2.40 <= z <= 6.20:
                r_out = r_spoke_env(z) - GROOVE_DEPTH_WALL
            wall = r_out - r_in
            if wall < min_wall:
                min_wall = wall

    crown_min_wall = (TOP_Z - DISH_DEPTH) - D_BORE_TOP_Z
    groove_min_wall = (top_cap_z(2.20) - GROOVE_DEPTH_CROWN) - D_BORE_TOP_Z

    print(f"Mesh vertices   : {len(vertices)}")
    print(f"Mesh triangles  : {len(faces)}")
    print(f"Zero-area tris  : {zero_area_tris}")
    print(f"Boundary edges  : {boundary_edges}")
    print(f"Non-manifold    : {non_manifold_edges}")
    print(f"Euler char V-E+F: {euler}")
    print(f"Bounding Box    : {dims[0]:.2f} x {dims[1]:.2f} x {dims[2]:.2f} mm")
    print(f"Min Skirt Wall  : {min_wall:.2f} mm | Crown Wall : {crown_min_wall:.2f} mm | Groove Crown Wall : {groove_min_wall:.2f} mm")
    print(f"Signed Volume   : {vol_cm3:.3f} cm^3")
    print(f"Est. PA12 Mass  : {mass_g:.2f} g (at 1.01 g/cm^3)")

    assert zero_area_tris == 0, f"Found {zero_area_tris} degenerate triangles!"
    assert boundary_edges == 0, f"Mesh is not watertight ({boundary_edges} boundary edges)!"
    assert non_manifold_edges == 0, f"Mesh has {non_manifold_edges} non-manifold edges!"
    assert euler == 2, f"Unexpected Euler characteristic {euler} != 2!"
    assert signed_vol > 0.0, f"Inverted normals: signed volume {signed_vol} <= 0!"
    assert abs(dims[0] - 25.20) <= 0.05 and abs(dims[1] - 25.20) <= 0.05 and abs(dims[2] - 19.00) <= 0.05, (
        f"Unexpected bounding box: {dims}"
    )
    assert min_wall >= 1.15, f"Skirt/groove wall {min_wall:.3f} mm < 1.15 mm!"
    assert crown_min_wall >= 3.50, f"Crown wall {crown_min_wall:.3f} mm < 3.50 mm!"
    assert groove_min_wall >= 3.00, f"Groove crown wall {groove_min_wall:.3f} mm < 3.00 mm!"
    print("Watertight manifold & DFM check: PASS (0 non-manifold edges, 0 boundary edges)")
    return vol_cm3, mass_g, dims


def write_binary_stl(filepath, vertices, faces):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    header = b"ICIO500 Wide-Skirt Capstan v2 Knob - MJF PA12 Nylon (mm)".ljust(80, b"\x00")
    with open(filepath, "wb") as f:
        f.write(header)
        f.write(struct.pack("<I", len(faces)))
        for i0, i1, i2 in faces:
            v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]
            n = np.cross(v1 - v0, v2 - v0)
            norm_len = np.linalg.norm(n)
            n = n / norm_len if norm_len > 1e-12 else np.array([0.0, 0.0, 1.0])
            f.write(struct.pack("<12fH",
                                float(n[0]), float(n[1]), float(n[2]),
                                float(v0[0]), float(v0[1]), float(v0[2]),
                                float(v1[0]), float(v1[1]), float(v1[2]),
                                float(v2[0]), float(v2[1]), float(v2[2]),
                                0))
    print(f"Exported STL    : {filepath} ({os.path.getsize(filepath):,} bytes)")


def write_step_ap214(filepath, vertices, faces, face_tags):
    """Export ISO-10303-21 AP214 MANIFOLD_SOLID_BREP STEP with charcoal body + off-white groove."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    lines = []
    eid = 1

    def add(expr):
        nonlocal eid
        idx = eid
        lines.append(f"#{idx}={expr};")
        eid += 1
        return idx

    app_ctx = add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
    add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#{app_ctx})")
    prod_ctx = add(f"PRODUCT_CONTEXT('',#{app_ctx},'mechanical')")
    prod = add(f"PRODUCT('ICIO500_Capstan_v2_Knob','ICIO500 Wide-Skirt Capstan v2 Knob (MJF PA12 Nylon)','',(#{prod_ctx}))")
    prod_form = add(f"PRODUCT_DEFINITION_FORMATION('','',#{prod})")
    prod_def_ctx = add(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx},'design')")
    prod_def = add(f"PRODUCT_DEFINITION('design','',#{prod_form},#{prod_def_ctx})")
    prod_shape = add(f"PRODUCT_DEFINITION_SHAPE('','',#{prod_def})")

    len_unit = add("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
    ang_unit = add("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
    sol_unit = add("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
    uncert = add(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-04),#{len_unit},'distance_accuracy_value','confusion accuracy')")
    geom_ctx = add(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{uncert}))GLOBAL_UNIT_ASSIGNED_CONTEXT((#{len_unit},#{ang_unit},#{sol_unit}))REPRESENTATION_CONTEXT('NONE','WORKSPACE'))")

    origin_pt = add("CARTESIAN_POINT('',(0.,0.,0.))")
    z_dir = add("DIRECTION('',(0.,0.,1.))")
    x_dir = add("DIRECTION('',(1.,0.,0.))")
    origin_ax = add(f"AXIS2_PLACEMENT_3D('',#{origin_pt},#{z_dir},#{x_dir})")

    sdr_id = add("PLACEHOLDER")
    abrep_id = add("PLACEHOLDER")
    msb_id = add("PLACEHOLDER")
    shell_id = add("PLACEHOLDER")

    v_pt_ids = []
    vp_ids = []
    for vx, vy, vz in vertices:
        cp = add(f"CARTESIAN_POINT('',({vx:.6f},{vy:.6f},{vz:.6f}))")
        vp = add(f"VERTEX_POINT('',#{cp})")
        v_pt_ids.append(cp)
        vp_ids.append(vp)

    edge_map = {}
    for tri in faces:
        i0, i1, i2 = int(tri[0]), int(tri[1]), int(tri[2])
        for u, v in ((i0, i1), (i1, i2), (i2, i0)):
            a, b = (u, v) if u < v else (v, u)
            if (a, b) not in edge_map:
                dvec = vertices[b] - vertices[a]
                dlen = np.linalg.norm(dvec)
                d = dvec / dlen
                d_id = add(f"DIRECTION('',({d[0]:.8f},{d[1]:.8f},{d[2]:.8f}))")
                vec_id = add(f"VECTOR('',#{d_id},{dlen:.6f})")
                ln_id = add(f"LINE('',#{v_pt_ids[a]},#{vec_id})")
                ec_id = add(f"EDGE_CURVE('',#{vp_ids[a]},#{vp_ids[b]},#{ln_id},.T.)")
                edge_map[(a, b)] = ec_id

    face_ids = []
    groove_face_ids = []
    for fidx, tri in enumerate(faces):
        i0, i1, i2 = int(tri[0]), int(tri[1]), int(tri[2])
        v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]
        e01 = v1 - v0
        e02 = v2 - v0
        n = np.cross(e01, e02)
        n = n / np.linalg.norm(n)
        ref = e01 / np.linalg.norm(e01)

        n_id = add(f"DIRECTION('',({n[0]:.8f},{n[1]:.8f},{n[2]:.8f}))")
        r_id = add(f"DIRECTION('',({ref[0]:.8f},{ref[1]:.8f},{ref[2]:.8f}))")
        ax_id = add(f"AXIS2_PLACEMENT_3D('',#{v_pt_ids[i0]},#{n_id},#{r_id})")
        pl_id = add(f"PLANE('',#{ax_id})")

        oe_ids = []
        for u, v in ((i0, i1), (i1, i2), (i2, i0)):
            a, b = (u, v) if u < v else (v, u)
            sense = ".T." if u < v else ".F."
            oe = add(f"ORIENTED_EDGE('',*,*,#{edge_map[(a, b)]},{sense})")
            oe_ids.append(f"#{oe}")

        el_id = add(f"EDGE_LOOP('',({','.join(oe_ids)}))")
        fob_id = add(f"FACE_OUTER_BOUND('',#{el_id},.T.)")
        af_id = add(f"ADVANCED_FACE('',(#{fob_id}),#{pl_id},.T.)")
        face_ids.append(af_id)
        if face_tags[fidx] == 'groove':
            groove_face_ids.append(af_id)

    face_refs = ",".join(f"#{fid}" for fid in face_ids)
    lines[sdr_id - 1] = f"#{sdr_id}=SHAPE_DEFINITION_REPRESENTATION(#{prod_shape},#{abrep_id});"
    lines[abrep_id - 1] = f"#{abrep_id}=ADVANCED_BREP_SHAPE_REPRESENTATION('CapstanV2Knob',(#{origin_ax},#{msb_id}),#{geom_ctx});"
    lines[msb_id - 1] = f"#{msb_id}=MANIFOLD_SOLID_BREP('CapstanV2Knob',#{shell_id});"
    lines[shell_id - 1] = f"#{shell_id}=CLOSED_SHELL('',({face_refs}));"

    col_body = add("COLOUR_RGB('',0.14,0.145,0.155)")
    fasc_body = add(f"FILL_AREA_STYLE_COLOUR('',#{col_body})")
    fas_body = add(f"FILL_AREA_STYLE('',(#{fasc_body}))")
    ssfa_body = add(f"SURFACE_STYLE_FILL_AREA(#{fas_body})")
    sss_body = add(f"SURFACE_SIDE_STYLE('',(#{ssfa_body}))")
    ssu_body = add(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss_body})")
    psa_body = add(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu_body}))")
    si_body = add(f"STYLED_ITEM('',(#{psa_body}),#{msb_id})")
    styled_items = [f"#{si_body}"]

    if groove_face_ids:
        col_grv = add("COLOUR_RGB('',0.92,0.92,0.90)")
        fasc_grv = add(f"FILL_AREA_STYLE_COLOUR('',#{col_grv})")
        fas_grv = add(f"FILL_AREA_STYLE('',(#{fasc_grv}))")
        ssfa_grv = add(f"SURFACE_STYLE_FILL_AREA(#{fas_grv})")
        sss_grv = add(f"SURFACE_SIDE_STYLE('',(#{ssfa_grv}))")
        ssu_grv = add(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss_grv})")
        psa_grv = add(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu_grv}))")
        for gfid in groove_face_ids:
            si_g = add(f"STYLED_ITEM('',(#{psa_grv}),#{gfid})")
            styled_items.append(f"#{si_g}")

    add(f"MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',({','.join(styled_items)}),#{geom_ctx})")

    header = f"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('STEP AP214 - ICIO500 Wide-Skirt Capstan v2 Knob (MJF PA12 Nylon)'),'2;1');
FILE_NAME('{os.path.basename(filepath)}','2026-11-25T14:55:00',('Chris Williams'),('SeaDubs / ICIO500'),'ICIO500 Parametric Generator','Python Numpy CAD','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN {{ 1 0 10303 214 1 1 1 1 }}'));
ENDSEC;
DATA;
"""
    footer = "ENDSEC;\nEND-ISO-10303-21;\n"

    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write(header)
        f.write("\n".join(lines))
        f.write("\n" + footer)
    print(f"Exported STEP   : {filepath} ({os.path.getsize(filepath):,} bytes)")


def main():
    print("=== ICIO500 WIDE-SKIRT CAPSTAN V2 KNOB (MJF PA12 NYLON) ===")
    vertices, faces, face_tags = build_knob_mesh()
    verify_manifold_and_stats(vertices, faces)

    stl_path = os.path.normpath("fabrication/satellite_faceplate/jlc3dp_knob_v2/icio500_capstan_v2_knob.stl")
    step_path = os.path.normpath("fabrication/satellite_faceplate/jlc3dp_knob_v2/icio500_capstan_v2_knob.step")

    write_binary_stl(stl_path, vertices, faces)
    write_step_ap214(step_path, vertices, faces, face_tags)
    print("=== WIDE-SKIRT CAPSTAN V2 KNOB GENERATION COMPLETE ===")


if __name__ == "__main__":
    main()
