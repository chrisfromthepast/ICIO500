"""
Parametric 3D CAD Generator for the ICIO500 "Capstan Vernier" Encoder Knob.
Geometric Ship's Wheel design matching the active faceplate reticle (EncoderGraphicGeometric).
Optimized & toleranced for JLC3DP / JLCPCB MJF PA12 Nylon (Dyed Black).

Outputs:
  - fabrication/in_production/jlc3dp_knob/icio500_capstan_knob.stl  (Watertight binary STL for MJF printing)
  - fabrication/in_production/jlc3dp_knob/icio500_capstan_knob.step (ISO-10303-21 AP214 STEP with MANIFOLD_SOLID_BREP)
"""

import math
import os
import struct
import numpy as np


# -----------------------------------------------------------------------------
# Exact Dimensional Parameters (mm) — Matched to Bourns PEC11R-4020F-S0024
# -----------------------------------------------------------------------------
SPOKE_SKIRT_R = 9.50         # Ø19.00 mm projecting 8 spoke tips at skirt base (Z = 0..1 mm)
SPOKE_BARREL_R = 8.40        # Ø16.80 mm projecting 8 spoke blades along shaft (Z = 5.0..19.15 mm)
SKIRT_VALLEY_BOT_R = 8.15    # Octagram light-channel floor at skirt base (1.35 mm inside spokes)
SKIRT_VALLEY_TOP_R = 7.50    # Skirt valley at Z = 5.00 mm (1.20 mm solid wall over Ø12.6 mm M7 pocket)
VALLEY_MIN_R_BARREL = 5.55   # Deep axial light channel floor (2.85 mm relief below spoke blades)

SKIRT_VERT_Z = 1.00          # Base skirt flare knee
SKIRT_TOP_Z = 5.80           # Clears internal M7 pocket shoulder (Z = 5.00 mm) by >= 1.25 mm 3D
VALLEY_TRANS_TOP_Z = 7.20    # Taper from skirt valley to deep barrel flute above M7 cone
BARREL_TOP_Z = 19.15         # Outer bevel base around 8-spoked octagram planform
TOP_Z = 19.50                # Total knob height (2.50 mm solid crown above Z = 17.00 mm shaft tip)

# Top Crown Open-Rim Ship's Wheel 3D Relief (scaled to mirror EncoderGraphicGeometric)
WHEEL_HUB_R = 2.15           # Raised center hub disk
WHEEL_RING_IN_R = 4.65       # Raised inner wheel ring (mirrors R = 10.00 faceplate circle)
WHEEL_RING_HALF_W = 0.55     # 1.10 mm wide inner ring (>= 1.0 mm Nylon DFM)
WHEEL_SQUARE_HALF_W = 0.55   # 1.10 mm wide overlapping square / octagram star chords
WHEEL_SPOKE_HALF_W = 0.58    # 1.16 mm wide projecting spoke blades (matches barrel spokes 1:1)
WHEEL_SPOKE_12_HALF_W = 1.55 # 3.10 mm wide 12 o'clock (+90°) spoke (>= 1.05 mm walls flanking groove)
WHEEL_POCKET_DEPTH = 1.20    # 1.20 mm deep recessed crown windows & valleys (floor Z = 18.30 mm)
WHEEL_BEVEL_W = 0.20         # Crisp linear bevel width on crown pockets

# Cross-Sectional Spoke & Octagram Flute Angles (relative to nearest k*45° spoke)
SPOKE_FLAT_DEG = 4.0         # Non-pointer spoke flat blade half-angle (>= 1.17 mm at R=8.4)
SPOKE_BEVEL_DEG = 6.8        # Non-pointer spoke side bevel outer angle
SPOKE_12_FLAT_DEG = 10.7     # Widened +90° spoke flat blade half-angle (1.56 mm half-width at R=8.4)
SPOKE_12_BEVEL_DEG = 13.5    # Widened +90° spoke side bevel outer angle
OCT_SHOULDER_DEG = 15.5      # Octagram square facet transition into central light flute
OCT_FLUTE_FLOOR_DEG = 18.0   # Deep central axial light flute shoulder (to 22.5° midpoint)

GROOVE_HALF_W_RIM = 0.50     # 1.00 mm wide flared light-catching top rim (>= 1.05 mm side walls)
GROOVE_HALF_W_FLR = 0.30     # 0.60 mm flat white indicator bottom
GROOVE_DEPTH_CROWN = 1.20    # 1.20 mm deep trench on top spoke (floor Z = 18.30 mm)
GROOVE_DEPTH_WALL = 1.05     # 1.05 mm deep sight trench down +90° spoke & skirt (>= 1.05 mm wall)

# Internal Bore (Z = 0 is bottom of skirt, sitting 1.00 mm above faceplate front)
M7_POCKET_R = 6.30           # Ø12.60 mm clearance pocket for M7 hex nut & exposed bushing
M7_POCKET_TOP_Z = 5.00
COLLAR_BOT_Z = 5.80          # Conical transition 5.00 -> 5.80 mm
COLLAR_TOP_Z = 7.50
COLLAR_R = 3.10              # Ø6.20 mm clearance around unflatted 6 mm shaft collar
D_BORE_LEADIN_Z = 7.80       # 0.30 mm entry chamfer into D-shaft interference fit
D_BORE_TOP_Z = 17.00         # Shaft tip seating plane -> fixes exact 1.00 mm click gap
D_BORE_R = 3.03              # Ø6.06 mm base bore for MJF PA12 press fit
D_FLAT_Y = 1.50              # 4.50 mm across flat (Y = +1.50 mm, aligned to +Y pointer)
CRUSH_RIB_ANGLES_DEG = (-90.0, -35.0, -145.0)
CRUSH_RIB_PROTRUSION = 0.12  # 0.12 mm inward crush rib (peaks at R = 2.91 mm)
CRUSH_RIB_HALF_WIDTH = 0.25  # 0.50 mm wide rib


def build_base_angles():
    """
    Create sorted base angles in degrees across [0, 360), combining a 2.0-degree base
    grid with exact feature pins for all 8 spoke blades, octagram shoulders, light flute
    corners, D-flat tangent corners, 3 crush ribs, and the 11-point pointer stencil [80.5°, 99.5°].
    """
    protected = []

    # 11-point pointer stencil spanning [90-SPOKE_12_BEVEL_DEG, 90+SPOKE_12_BEVEL_DEG] across the widened +90° spoke
    # Offsets relative to idx_90 (-5..+5):
    # -5: 90-d1, -4: 90-d0, -3: 90-a_rim, -2: 90-a_flr, -1: 90-0.5*a_flr,
    #  0: 90.0, +1: 90+0.5*a_flr, +2: 90+a_flr, +3: 90+a_rim, +4: 90+d0, +5: 90+d1
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

    # Exact D-flat tangent corners + chord samples outside (80.5, 99.5)
    flat_ang = math.degrees(math.asin(D_FLAT_Y / D_BORE_R))
    protected.extend([flat_ang, 180.0 - flat_ang])
    for a in [35.0, 42.0, 138.0, 145.0]:
        protected.append(a)

    # Dense exact samples across the 3 crush ribs (at 215°, 270°, 325°)
    rib_half_deg = math.degrees(CRUSH_RIB_HALF_WIDTH / D_BORE_R)
    for center_deg in CRUSH_RIB_ANGLES_DEG:
        c = center_deg % 360.0
        for frac in (-1.0, -0.6, -0.25, 0.0, 0.25, 0.6, 1.0):
            protected.append(c + frac * rib_half_deg)

    # Exact spoke edges, octagram facets, and light channel floor corners across all 8 octants
    for k in range(8):
        sc = k * 45.0
        protected.append(sc)
        if k == 2:
            # 12 o'clock (+90°) already pins [s12_lo, s12_hi]; pin its outer light flute corners
            for d in (-OCT_SHOULDER_DEG, -OCT_FLUTE_FLOOR_DEG, OCT_SHOULDER_DEG, OCT_FLUTE_FLOOR_DEG):
                protected.append((sc + d) % 360.0)
        else:
            for d in (-SPOKE_FLAT_DEG, SPOKE_FLAT_DEG, -SPOKE_BEVEL_DEG, SPOKE_BEVEL_DEG,
                      -OCT_SHOULDER_DEG, OCT_SHOULDER_DEG, -OCT_FLUTE_FLOOR_DEG, OCT_FLUTE_FLOOR_DEG):
                ang = (sc + d) % 360.0
                if not (s12_lo - 0.01 <= ang <= s12_hi + 0.01):
                    protected.append(ang)
        protected.append((22.5 + k * 45.0) % 360.0)

    # Sort and merge exact near-identical protected angles (< 0.02°)
    protected = [p % 360.0 for p in protected]
    protected.sort()
    clean_prot = []
    for p in protected:
        if not clean_prot or abs(p - clean_prot[-1]) > 0.02:
            clean_prot.append(p)
    if clean_prot and clean_prot[-1] > 359.98:
        clean_prot.pop()

    # Add 2.0-degree base grid points where clear (>= 0.45°) of all protected pins
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
    """Outer envelope radius of the 8 projecting spoke blades from skirt base to crown rim."""
    if z <= SKIRT_VERT_Z:
        return SPOKE_SKIRT_R
    elif z <= SKIRT_TOP_Z:
        t = (z - SKIRT_VERT_Z) / (SKIRT_TOP_Z - SKIRT_VERT_Z)
        return SPOKE_SKIRT_R + t * (SPOKE_BARREL_R - SPOKE_SKIRT_R)
    else:
        return SPOKE_BARREL_R


def r_valley_env(z):
    """Core floor envelope of the 8 unobstructed axial light flutes (keeps >= 1.20 mm wall)."""
    if z <= SKIRT_VERT_Z:
        return SKIRT_VALLEY_BOT_R
    elif z <= SKIRT_TOP_Z:
        t = (z - SKIRT_VERT_Z) / (SKIRT_TOP_Z - SKIRT_VERT_Z)
        return SKIRT_VALLEY_BOT_R + t * (SKIRT_VALLEY_TOP_R - SKIRT_VALLEY_BOT_R)
    elif z <= VALLEY_TRANS_TOP_Z:
        t = (z - SKIRT_TOP_Z) / (VALLEY_TRANS_TOP_Z - SKIRT_TOP_Z)
        return SKIRT_VALLEY_TOP_R + t * (VALLEY_MIN_R_BARREL - SKIRT_VALLEY_TOP_R)
    else:
        return VALLEY_MIN_R_BARREL


def barrel_wheel_r(theta_deg, z):
    """
    Non-cylindrical 3D ship's-wheel / octagram shaft & skirt profile.
    Combines 8 projecting spoke blades, crisp octagram square shoulders, and
    deep unobstructed top-to-bottom axial light flutes.
    """
    r_sp = r_spoke_env(z)
    r_val = r_valley_env(z)
    r_oct_corner = r_val + 0.62 * (r_sp - r_val)
    r_mid = r_val + 0.28 * (r_sp - r_val)

    # Distance in degrees to the nearest 45° spoke centerline
    nearest_spoke_idx = round(theta_deg / 45.0) % 8
    delta = abs(((theta_deg - nearest_spoke_idx * 45.0) + 180.0) % 360.0 - 180.0)

    if nearest_spoke_idx == 2:  # Widened 12 o'clock (+90°) spoke
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


def top_wheel_z(r, theta_deg):
    """
    Open-rim 3D top relief reproducing EncoderGraphicGeometric without a circular outer dam:
    raised hub, inner ring, overlapping squares (octagram), and 8 projecting spokes at 19.50 mm;
    recessed sector windows and open star valleys drop 1.40 mm to 18.10 mm into the shaft flutes.
    """
    th_rad = math.radians(theta_deg)
    x = r * math.cos(th_rad)
    y = r * math.sin(th_rad)

    phi_mod = theta_deg % 90.0
    delta = math.radians(min(phi_mod, 90.0 - phi_mod))
    u = r * math.cos(delta)
    v = r * math.sin(delta)
    inv_sqrt2 = 1.0 / math.sqrt(2.0)

    # 1. Raised center hub disk
    d_hub = r - WHEEL_HUB_R
    # 2. Inner wheel circle
    d_ring_in = abs(r - WHEEL_RING_IN_R) - WHEEL_RING_HALF_W
    # 3. 8 Projecting radial spokes (widened on +90° for the illuminated sight trench)
    d_spoke = min(r * math.sin(delta), r * math.sin(0.25 * math.pi - delta)) - WHEEL_SPOKE_HALF_W
    if y > 0.0 and abs(theta_deg - 90.0) <= 45.0:
        d_spoke = min(d_spoke, abs(x) - WHEEL_SPOKE_12_HALF_W)
    # 4. Overlapping axis-aligned & 45°-rotated square chords from R_in to R_in*sqrt(2)
    dist_sq1 = math.hypot(u - WHEEL_RING_IN_R, max(0.0, v - WHEEL_RING_IN_R))
    s_sum = (u + v) * inv_sqrt2
    s_diff = (u - v) * inv_sqrt2
    dist_sq2 = math.hypot(s_sum - WHEEL_RING_IN_R, max(0.0, s_diff - WHEEL_RING_IN_R))
    d_sq = min(dist_sq1, dist_sq2) - WHEEL_SQUARE_HALF_W

    sdf = min(d_hub, d_ring_in, d_spoke, d_sq)
    if sdf <= 0.0:
        return TOP_Z
    elif sdf >= WHEEL_BEVEL_W:
        return TOP_Z - WHEEL_POCKET_DEPTH
    else:
        return TOP_Z - (sdf / WHEEL_BEVEL_W) * WHEEL_POCKET_DEPTH


def inner_bore_radius(theta_deg, r_cyl, use_d_flat, rib_weight):
    """Exact inner bore polar radius at angle theta_deg (handles D-flat at Y=+1.50 and 3 crush ribs)."""
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
                # Smooth semi-elliptical / raised-cosine interference rib profile
                u = d / rib_half_deg
                protrusion = CRUSH_RIB_PROTRUSION * math.sqrt(max(0.0, 1.0 - u * u))
                r -= rib_weight * protrusion
    return r


def build_knob_mesh():
    """
    Construct a watertight closed 2-manifold triangle mesh of the Ship's-Wheel Knob.
    Returns:
      vertices: (V, 3) float64 numpy array
      faces:    (F, 3) int32 numpy array (CCW outward winding)
      face_tags: list of 'body' | 'groove' per face for STEP color styling
    """
    base_angles, idx_left, idx_90, idx_right = build_base_angles()
    N = len(base_angles)
    crown_warp_r0 = WHEEL_RING_IN_R + WHEEL_RING_HALF_W + WHEEL_BEVEL_W  # 5.12 mm

    # Profile stations from center hub across open-rim ship's wheel crown, down octagram shaft & skirt to Z=0
    # Format: (kind, param, z_val, groove_mode)
    outer_profile = [
        # Center raised hub disk (R <= 2.15 mm)
        ('pole_top', 0.00, TOP_Z, 'none'),
        ('crown', 1.00, None, 'none'),
        ('crown', 1.90, None, 'none'),
        # 12 o'clock groove starts at R = 2.00 mm, then cuts open across top wheel windows
        ('crown', 2.00, None, 'groove_top'),
        ('crown', WHEEL_HUB_R, None, 'groove_top'),
        ('crown', WHEEL_HUB_R + WHEEL_BEVEL_W, None, 'groove_top'),
        ('crown', 2.90, None, 'groove_top'),
        ('crown', 3.40, None, 'groove_top'),
        ('crown', 3.70, None, 'groove_top'),
        ('crown', WHEEL_RING_IN_R - WHEEL_RING_HALF_W - WHEEL_BEVEL_W, None, 'groove_top'),
        # Inner wheel ring (R = 4.40 .. 4.90) & outer bevel to 5.12
        ('crown', WHEEL_RING_IN_R - WHEEL_RING_HALF_W, None, 'groove_top'),
        ('crown', WHEEL_RING_IN_R, None, 'groove_top'),
        ('crown', WHEEL_RING_IN_R + WHEEL_RING_HALF_W, None, 'groove_top'),
        ('crown', crown_warp_r0, None, 'groove_top'),
        # Open-rim warped octagram crown out to shaft perimeter (no circular outer dam)
        ('crown_warp', 0.18, None, 'groove_top'),
        ('crown_warp', 0.36, None, 'groove_top'),
        ('crown_warp', 0.54, None, 'groove_top'),
        ('crown_warp', 0.72, None, 'groove_top'),
        ('crown_warp', 0.88, None, 'groove_top'),
        ('crown_warp', 1.00, None, 'groove_top'),
        # Top perimeter bevel -> full-height octagram shaft & unobstructed light flutes -> flared skirt
        ('wall_bevel', None, BARREL_TOP_Z, 'groove_wall'),
        ('wall', None, 17.50, 'groove_wall'),
        ('wall', None, 12.00, 'groove_wall'),
        ('wall', None, VALLEY_TRANS_TOP_Z, 'groove_wall'),
        ('wall', None, SKIRT_TOP_Z, 'groove_wall'),
        ('skirt', None, 3.00, 'groove_wall'),
        ('skirt', None, SKIRT_VERT_Z, 'groove_wall'),
        ('skirt', None, 0.00, 'groove_wall'),
    ]

    inner_profile = [
        # Bottom entry of M7 nut pocket (Z=0.00)
        ('bore', M7_POCKET_R, 0.00, False, 0.0),
        ('bore', M7_POCKET_R, M7_POCKET_TOP_Z, False, 0.0),
        # Conical transition 5.00 -> 5.80 mm
        ('bore', COLLAR_R, COLLAR_BOT_Z, False, 0.0),
        # Collar clearance 5.80 -> 7.50 mm
        ('bore', COLLAR_R, COLLAR_TOP_Z, False, 0.0),
        # 0.30 mm chamfered lead-in to D-flat & crush ribs
        ('bore', D_BORE_R, D_BORE_LEADIN_Z, True, 1.0),
        # 9.20 mm D-shaft engagement bore up to Z = 17.00 mm
        ('bore', D_BORE_R, D_BORE_TOP_Z, True, 1.0),
        # Inner ceiling pole
        ('pole_ceil', 0.00, D_BORE_TOP_Z, True, 0.0),
    ]

    rings = []
    ring_groove_masks = []
    top_pole = None
    ceil_pole = None

    def make_ring_angles(r_rim_ref, r_flr_ref, mode):
        """Return (angles_deg_array, groove_quad_mask_indices) for a ring."""
        ang = base_angles.copy()
        if mode == 'none':
            return ang, set()

        # Angle boundaries for the 1.40 mm flared outer rim & 0.80 mm flat white floor inside [80.5°, 99.5°]
        a_rim = math.degrees(math.asin(min(0.95, GROOVE_HALF_W_RIM / max(2.00, r_rim_ref))))
        a_flr = math.degrees(math.asin(min(0.90, GROOVE_HALF_W_FLR / max(1.80, r_flr_ref))))

        # Fill indices [idx_left .. idx_right] = [90-SPOKE_12_BEVEL_DEG .. 90+SPOKE_12_BEVEL_DEG] strictly monotonically
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

        # Active groove faces span quad indices [idx_90-3 .. idx_90+2] (from groove_rim_R to groove_rim_L)
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
                z_pt = top_wheel_z(r_pt, th)
                if gmode == 'groove_top' and in_groove_floor:
                    z_pt = TOP_Z - GROOVE_DEPTH_CROWN
            elif kind == 'crown_warp':
                r_top_edge = max(5.30, barrel_wheel_r(th, BARREL_TOP_Z) - 0.35)
                r_pt = crown_warp_r0 + param * (r_top_edge - crown_warp_r0)
                z_pt = top_wheel_z(r_pt, th)
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

    # Assemble vertex buffer & closed manifold triangle index list
    # Vertex layout:
    #   [0 .. N-1]               : ring 0
    #   [N .. 2N-1]              : ring 1
    #   ...
    #   [M*N]                    : top_pole
    #   [M*N + 1]                : ceil_pole
    M = len(rings)
    vertices = np.vstack(rings + [top_pole.reshape(1, 3), ceil_pole.reshape(1, 3)])
    top_pole_idx = M * N
    ceil_pole_idx = M * N + 1

    faces = []
    face_tags = []

    # Verify outward winding on top fan:
    # Center boss ring 0 runs CCW (increasing theta). Outward normal on top is +Z.
    # For triangle (top_pole, v0_i, v0_{i+1}): (v0_i - top) x (v0_{i+1} - top) points +Z -> OUTWARD!
    for i in range(N):
        ni = (i + 1) % N
        faces.append([top_pole_idx, i, ni])
        face_tags.append('body')

    # Strip between ring m (earlier in path: top -> outside -> bottom -> up bore) and ring m+1:
    # Consider cylindrical outer wall: ring m has larger Z (top), ring m+1 has smaller Z (bottom).
    # v_top_i -> v_bot_i -> v_bot_{i+1}:
    # (v_bot_i - v_top_i) points -Z; (v_bot_{i+1} - v_top_i) points +theta.
    # (-Z) x (+theta) = +r (OUTWARD!).
    # Wait: check inner bore strip!
    # Moving UP the bore: ring m has smaller Z, ring m+1 has larger Z.
    # (v_m+1 - v_m) points +Z; (v_m+1_{i+1} - v_m_i) points +theta.
    # (+Z) x (+theta) = -r (pointing INWARD toward bore axis, which IS OUTWARD from the solid plastic!).
    # And check bottom annulus (ring outer_last at r=9.3 -> ring inner_0 at r=6.3, Z=0):
    # (inner - outer) points -r; (+theta). (-r) x (+theta) = -Z (pointing DOWNWARD, OUTWARD from plastic!).
    # The EXACT SAME quad winding works consistently across the ENTIRE topological sphere!
    for m in range(M - 1):
        base_a = m * N
        base_b = (m + 1) * N
        g_mask_a = ring_groove_masks[m]
        g_mask_b = ring_groove_masks[m + 1]
        is_groove_strip = (m < num_outer_rings - 1) and bool(g_mask_a or g_mask_b)
        active_g = g_mask_a & g_mask_b if (g_mask_a and g_mask_b) else (g_mask_a | g_mask_b)

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

    # Inner bore ceiling pole (at Z = 17.00, plastic is ABOVE the ceiling -> outward normal points -Z):
    # Ring last runs CCW (+theta). (ceil - v_last_i) is -r; (+theta).
    # Wait: (v_last_i -> v_last_{i+1} -> ceil) gives (+theta) x (-r) = +Z (wrong!).
    # (v_last_{i+1} -> v_last_i -> ceil) gives (-theta) x (-r) = -Z (OUTWARD from plastic!).
    last_base = (M - 1) * N
    for i in range(N):
        ni = (i + 1) % N
        faces.append([last_base + ni, last_base + i, ceil_pole_idx])
        face_tags.append('body')

    faces = np.array(faces, dtype=np.int32)
    return vertices, faces, face_tags


def verify_manifold_and_stats(vertices, faces):
    """Run strict topological manifold checks & physical property calculations."""
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
    mass_g = vol_cm3 * 1.01  # HP MJF PA12 Nylon density ~ 1.01 g/cm^3

    print(f"Mesh vertices   : {len(vertices)}")
    print(f"Mesh triangles  : {len(faces)}")
    print(f"Zero-area tris  : {zero_area_tris}")
    print(f"Boundary edges  : {boundary_edges}")
    print(f"Non-manifold    : {non_manifold_edges}")
    print(f"Euler char V-E+F: {euler}")
    print(f"Bounding Box    : {dims[0]:.2f} x {dims[1]:.2f} x {dims[2]:.2f} mm")
    print(f"Signed Volume   : {vol_cm3:.3f} cm^3")
    print(f"Est. PA12 Mass  : {mass_g:.2f} g (at 1.01 g/cm^3)")

    assert zero_area_tris == 0, f"Found {zero_area_tris} degenerate triangles!"
    assert boundary_edges == 0, f"Mesh is not watertight ({boundary_edges} boundary edges)!"
    assert non_manifold_edges == 0, f"Mesh has {non_manifold_edges} non-manifold edges!"
    assert euler == 2, f"Unexpected Euler characteristic {euler} != 2!"
    assert signed_vol > 0.0, f"Inverted normals: signed volume {signed_vol} <= 0!"
    print("Watertight manifold check: PASS (0 non-manifold edges, 0 boundary edges)")
    return vol_cm3, mass_g, dims


def write_binary_stl(filepath, vertices, faces):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    header = b"ICIO500 Capstan Vernier Knob - MJF PA12 Nylon (mm)".ljust(80, b"\x00")
    with open(filepath, "wb") as f:
        f.write(header)
        f.write(struct.pack("<I", len(faces)))
        for i0, i1, i2 in faces:
            v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]
            n = np.cross(v1 - v0, v2 - v0)
            norm_len = np.linalg.norm(n)
            if norm_len > 1e-12:
                n = n / norm_len
            else:
                n = np.array([0.0, 0.0, 1.0])
            f.write(struct.pack("<12fH",
                                float(n[0]), float(n[1]), float(n[2]),
                                float(v0[0]), float(v0[1]), float(v0[2]),
                                float(v1[0]), float(v1[1]), float(v1[2]),
                                float(v2[0]), float(v2[1]), float(v2[2]),
                                0))
    print(f"Exported STL    : {filepath} ({os.path.getsize(filepath):,} bytes)")


def write_step_ap214(filepath, vertices, faces, face_tags):
    """
    Export a valid ISO-10303-21 AP214 MANIFOLD_SOLID_BREP STEP file with shared
    topological vertices/edges and dual surface styling (MJF PA12 charcoal + white pointer groove).
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    lines = []
    eid = 1

    def add(expr):
        nonlocal eid
        idx = eid
        lines.append(f"#{idx}={expr};")
        eid += 1
        return idx

    # AP214 Product & Unit Header Setup
    app_ctx = add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
    app_proto = add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#{app_ctx})")
    prod_ctx = add(f"PRODUCT_CONTEXT('',#{app_ctx},'mechanical')")
    prod = add(f"PRODUCT('ICIO500_Capstan_Knob','ICIO500 Capstan Vernier Knob (MJF PA12 Nylon)','',(#{prod_ctx}))")
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

    # Reserve IDs & list slots for SHAPE_DEFINITION_REPRESENTATION, ADVANCED_BREP, MANIFOLD_SOLID_BREP, CLOSED_SHELL
    sdr_id = add("PLACEHOLDER")
    abrep_id = add("PLACEHOLDER")
    msb_id = add("PLACEHOLDER")
    shell_id = add("PLACEHOLDER")

    # Emit shared CARTESIAN_POINT & VERTEX_POINT for every vertex
    v_pt_ids = []
    vp_ids = []
    for vx, vy, vz in vertices:
        cp = add(f"CARTESIAN_POINT('',({vx:.6f},{vy:.6f},{vz:.6f}))")
        vp = add(f"VERTEX_POINT('',#{cp})")
        v_pt_ids.append(cp)
        vp_ids.append(vp)

    # Emit unique undirected EDGE_CURVE for every edge (a < b)
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

    # Emit ADVANCED_FACE for each triangle
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

    # Patch reserved shell/solid/representation lines
    face_refs = ",".join(f"#{fid}" for fid in face_ids)
    lines[sdr_id - 1] = f"#{sdr_id}=SHAPE_DEFINITION_REPRESENTATION(#{prod_shape},#{abrep_id});"
    lines[abrep_id - 1] = f"#{abrep_id}=ADVANCED_BREP_SHAPE_REPRESENTATION('CapstanKnob',(#{origin_ax},#{msb_id}),#{geom_ctx});"
    lines[msb_id - 1] = f"#{msb_id}=MANIFOLD_SOLID_BREP('CapstanKnob',#{shell_id});"
    lines[shell_id - 1] = f"#{shell_id}=CLOSED_SHELL('',({face_refs}));"

    # Presentation Colors:
    # 1. Dark Charcoal MJF PA12 Nylon (Dyed Black): RGB (0.14, 0.145, 0.155)
    col_body = add("COLOUR_RGB('',0.14,0.145,0.155)")
    fasc_body = add(f"FILL_AREA_STYLE_COLOUR('',#{col_body})")
    fas_body = add(f"FILL_AREA_STYLE('',(#{fasc_body}))")
    ssfa_body = add(f"SURFACE_STYLE_FILL_AREA(#{fas_body})")
    sss_body = add(f"SURFACE_SIDE_STYLE('',(#{ssfa_body}))")
    ssu_body = add(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss_body})")
    psa_body = add(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu_body}))")
    si_body = add(f"STYLED_ITEM('',(#{psa_body}),#{msb_id})")
    styled_items = [f"#{si_body}"]

    # 2. Matte Off-White Sight-Line Paint Accent: RGB (0.92, 0.92, 0.90) on groove faces
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
FILE_DESCRIPTION(('STEP AP214 - ICIO500 Capstan Vernier Knob (MJF PA12 Nylon)'),'2;1');
FILE_NAME('{os.path.basename(filepath)}','2026-11-14T21:00:00',('Chris Williams'),('SeaDubs / ICIO500'),'ICIO500 Parametric Generator','Python Numpy CAD','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN {{ 1 0 10303 214 1 1 1 1 }}'));
ENDSEC;
DATA;
"""
    footer = "ENDSEC;\nEND-ISO-10303-21;\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(lines))
        f.write("\n" + footer)
    print(f"Exported STEP   : {filepath} ({os.path.getsize(filepath):,} bytes)")


def main():
    print("=== ICIO500 CAPSTAN VERNIER KNOB (MJF PA12 NYLON) ===")
    vertices, faces, face_tags = build_knob_mesh()
    verify_manifold_and_stats(vertices, faces)

    stl_path = os.path.normpath("fabrication/in_production/jlc3dp_knob/icio500_capstan_knob.stl")
    step_jlc_path = os.path.normpath("fabrication/in_production/jlc3dp_knob/icio500_capstan_knob.step")

    write_binary_stl(stl_path, vertices, faces)
    write_step_ap214(step_jlc_path, vertices, faces, face_tags)
    print("=== KNOB CAD GENERATION COMPLETE ===")


if __name__ == "__main__":
    main()
