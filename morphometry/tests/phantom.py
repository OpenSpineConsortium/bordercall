"""Synthetic labelled spines whose every morphometric is known, for the tests: no scan, no patient.

scanimport's phantom (scanimport/tests/phantom.py) draws a vertebra as a body, a ring round the
canal and two bars, which is enough for Panjabi's seven chords. The measures this package adds
need the parts a real vertebra has: two pedicles with a width, a height and two angles; laminae
that slope back as they descend, so the canal's midline depth is least at its cranial end, as
Eisenstein found on dry bone; articular pillars carrying a superior and an inferior articular
process at a facet angle, joined by a pars; transverse processes of a set height; a spinous
process at a set inclination; a body that may be wedged, concave at its end-plates or waisted at
mid-height. A column chains such vertebrae with known disc heights, segmental angles, slips and
turns, and a pelvis adds a sacrum with a set S1 end-plate and two hip bones with spherical sockets
round known centres, so the pelvic incidence is known.

Every vertebra is drawn in its own frame: x to the patient's right, y anterior, z cranial, the
body's posterior wall at y = 0 and its mid-height at z = 0. A voxel is labelled when its centre
falls inside a part, as a mask's voxel is labelled when its centre is bone. The truths are
written once, in `truth`, from the parameters alone.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from scanimport.tests.phantom import grid_about, rotation


@dataclass
class Vert:
    """One vertebra's parameters, lumbar-sized by default (about an L3)."""
    # the body: end-plate width and depth, posterior and anterior heights (a wedge where they
    # differ), each end-plate's central depression, and the outline's scale at mid-height
    W: float = 46.0
    D: float = 34.0
    Hp: float = 27.0
    Ha: float = 27.0
    concavity: float = 0.0
    waist: float = 1.0
    # the pedicles: the gap between their medial walls at the isthmus, their width and height
    # there, the isthmus centre's height and its distance behind the body's posterior wall, the
    # axis's transverse (medial) and sagittal angles in degrees, and how fast the pedicle swells
    # away from its isthmus (a fraction of its size per mm squared, up to SWELL_MAX)
    canal_w: float = 22.0
    ped_w: float = 9.0
    ped_h: float = 15.0
    ped_z: float = 3.0
    ped_back: float = 5.0
    ped_t: float = 0.0
    ped_s: float = 0.0
    ped_waist: float = 0.0
    # a block against each pedicle's side at the isthmus over its free length, as the lateral
    # mass stands against a cervical pedicle: its width out from there and its height, 0 for
    # none; and the foramen transversarium, a vertical hole of this diameter through the block
    # whose medial edge lies a millimetre inside the pedicle's side at the isthmus, 0 for none,
    # so that beside the isthmus the pedicle's side is the foramen's wall, as the real one is,
    # and in front of and behind the foramen the block joins it
    mass_w: float = 0.0
    mass_h: float = 0.0
    foramen_d: float = 0.0
    # the articular pillars: centre across and front to back; each runs from the pedicle's back
    # end to the lamina, between the inferior and the superior articular process
    pil_x: float = 17.0
    pil_y: float = -13.0
    # the laminae: thickness front to back, the canal's midline depth at the laminae's top, how
    # steeply their front surface runs back as it descends (degrees), and their top and bottom
    lam_t: float = 5.0
    lam_ap_top: float = 15.0
    lam_slope: float = 20.0
    lam_top: float = 9.0
    lam_bot: float = -12.0
    # the superior and inferior articular processes: their centres, length along the facet line,
    # thickness across it, the facet line's angle to the sagittal plane (degrees), the SAP's top
    # and the IAP's bottom
    sap_x: float = 19.0
    sap_y: float = -14.0
    sap_len: float = 12.0
    sap_thk: float = 5.0
    sap_top: float = 24.0
    iap_x: float = 14.0
    iap_y: float = -19.0
    iap_len: float = 12.0
    iap_thk: float = 5.0
    iap_bot: float = -24.0
    facet: float = 40.0
    # the transverse processes: tip to tip, front-to-back centre (at the pillar, the junction
    # of the pedicle and the lamina, where a lumbar transverse process springs) and thickness,
    # centre height and craniocaudal height
    TP: float = 78.0
    tp_y: float = -13.0
    tp_thk: float = 6.0
    tp_z: float = 2.0
    tp_h: float = 10.0
    # the spinous process: length along its axis from its root, inclination below the transverse
    # plane (degrees), half-width across and half-height
    LS: float = 28.0
    sp_angle: float = 20.0
    sp_hw: float = 3.0
    sp_hh: float = 4.5


SWELL_MAX = 0.5          # a pedicle swells to at most this much more than its isthmus


def lumbar(**kw) -> Vert:
    return replace(Vert(), **kw)


# ---- one vertebra -------------------------------------------------------------------------------

def body_inside(q: np.ndarray, v: Vert) -> np.ndarray:
    x, y, z = q[:, 0], q[:, 1], q[:, 2]
    zt = v.Hp / 2 + (v.Ha - v.Hp) / 2 * (y / v.D)
    zb = -zt
    f = 1.0 - (1.0 - v.waist) * np.clip(1.0 - (2.0 * z / v.Hp) ** 2, 0.0, 1.0)
    a, b = v.W * f / 2, v.D * f / 2
    rho2 = (x / (v.W / 2)) ** 2 + ((y - v.D / 2) / (v.D / 2)) ** 2
    dip = v.concavity * np.clip(1.0 - rho2, 0.0, 1.0)
    return ((x / a) ** 2 + ((y - b) / b) ** 2 <= 1.0) & (z <= zt - dip) & (z >= zb + dip)


def pedicle_axis(v: Vert, side: int) -> Tuple[np.ndarray, np.ndarray]:
    """The isthmus centre and the unit axis pointing posteriorly, for side +1 (right) or -1."""
    c = np.array([side * (v.canal_w / 2 + v.ped_w / 2), -v.ped_back, v.ped_z])
    d = np.array([side * math.tan(math.radians(v.ped_t)), -1.0, math.tan(math.radians(v.ped_s))])
    return c, d / np.linalg.norm(d)


def pedicle_frame(d: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """The pedicle's width direction (horizontal, across the axis) and height direction."""
    ew = np.cross(d, [0.0, 0.0, 1.0])
    ew /= np.linalg.norm(ew)
    eh = np.cross(ew, d)
    return ew, eh / np.linalg.norm(eh)


def pedicle_inside(q: np.ndarray, v: Vert, side: int) -> np.ndarray:
    c, d = pedicle_axis(v, side)
    ew, eh = pedicle_frame(d)
    r = q - c
    t = r @ d
    g = 1.0 + np.minimum(v.ped_waist * t ** 2, SWELL_MAX)
    u, w = (r @ ew) / (g * v.ped_w / 2), (r @ eh) / (g * v.ped_h / 2)
    # from inside the body to the pillar: anteriorly to 12 mm in front of the isthmus, posteriorly
    # to the pillar's centre line
    t_back = (v.ped_back + (-v.pil_y - v.ped_back)) / max(abs(d[1]), 1e-6)
    return (u ** 2 + w ** 2 <= 1.0) & (t >= -(v.ped_back + 12.0) / abs(d[1])) & (t <= t_back)


def mass_start(v: Vert) -> float:
    """Where the block beside a pedicle begins: at the pedicle's side at the isthmus."""
    return v.canal_w / 2 + v.ped_w


def foramen_centre(v: Vert, side: int) -> Tuple[float, float]:
    """The foramen transversarium's centre in (x, y): its medial edge a millimetre inside the
    block's start, so that no sliver of the block stands beside the isthmus."""
    return side * (mass_start(v) - 1.0 + v.foramen_d / 2), -v.ped_back


def foramen_inside(q: np.ndarray, v: Vert, side: int) -> np.ndarray:
    cx, cy = foramen_centre(v, side)
    return (q[:, 0] - cx) ** 2 + (q[:, 1] - cy) ** 2 <= (v.foramen_d / 2) ** 2


def box_along(q: np.ndarray, cx: float, cy: float, along: np.ndarray, half_len: float, half_thk: float,
              z0: float, z1: float) -> np.ndarray:
    """A box standing on the transverse plane, its long side along the unit vector `along` in (x, y)."""
    across = np.array([-along[1], along[0]])
    r = q[:, :2] - np.array([cx, cy])
    return (np.abs(r @ along) <= half_len) & (np.abs(r @ across) <= half_thk) & (q[:, 2] >= z0) & (q[:, 2] <= z1)


def facet_line(v: Vert, side: int) -> np.ndarray:
    """The facet line in (x, y): posteriorly it runs laterally, at `facet` degrees to the sagittal plane."""
    f = math.radians(v.facet)
    return np.array([side * math.sin(f), -math.cos(f)])


def lamina_front(x: np.ndarray, z: np.ndarray, v: Vert) -> np.ndarray:
    ym_top = -v.lam_ap_top
    return ym_top - (v.lam_top - z) * math.tan(math.radians(v.lam_slope)) + (np.abs(x) / v.pil_x) * (v.pil_y - ym_top)


def parts_inside(q: np.ndarray, v: Vert) -> Dict[str, np.ndarray]:
    """Which local points (N, 3) fall in each part of the phantom vertebra."""
    x, y, z = q[:, 0], q[:, 1], q[:, 2]
    out = {"body": body_inside(q, v)}
    for side, name in ((1, "right"), (-1, "left")):
        out["pedicle_" + name] = pedicle_inside(q, v, side)
        sx = side * x
        back = lamina_front(np.full(len(q), v.pil_x), z, v) - v.lam_t
        pil = ((sx >= v.pil_x - 3.5) & (sx <= v.pil_x + 3.5) & (y <= v.pil_y + 3.5) & (y >= back)
               & (z >= v.lam_bot + 2.0) & (z <= v.ped_z + v.ped_h / 2))
        out["pillar_" + name] = pil
        line = facet_line(v, side)
        out["sap_" + name] = box_along(q, side * v.sap_x, v.sap_y, line, v.sap_len / 2, v.sap_thk / 2,
                                       v.ped_z + v.ped_h / 2 - 3.0, v.sap_top)
        out["iap_" + name] = box_along(q, side * v.iap_x, v.iap_y, line, v.iap_len / 2, v.iap_thk / 2,
                                       v.iap_bot, v.lam_bot + 4.0)
        out["tp_" + name] = ((sx >= v.pil_x) & (sx <= v.TP / 2) & (np.abs(y - v.tp_y) <= v.tp_thk / 2)
                             & (np.abs(z - v.tp_z) <= v.tp_h / 2))
        if v.mass_w > 0 and v.mass_h > 0:
            x_in = mass_start(v)
            mass = ((sx >= x_in) & (sx <= x_in + v.mass_w) & (y <= -1.0) & (y >= -(v.ped_back + 6.0))
                    & (np.abs(z - v.ped_z) <= v.mass_h / 2))
            if v.foramen_d > 0:
                mass &= ~foramen_inside(q, v, side)
            out["mass_" + name] = mass
    front = lamina_front(x, z, v)
    out["lamina"] = (np.abs(x) <= v.pil_x) & (y <= front) & (y >= front - v.lam_t) & (z >= v.lam_bot) & (z <= v.lam_top)
    b = math.radians(v.sp_angle)
    d = np.array([0.0, -math.cos(b), -math.sin(b)])
    e = np.array([0.0, -math.sin(b), math.cos(b)])
    zr = 0.5 * (v.lam_top + v.lam_bot)
    p0 = np.array([0.0, float(lamina_front(np.zeros(1), np.array([zr]), v)[0]) - v.lam_t / 2, zr])
    r = q - p0
    t = r @ d
    out["spinous"] = (np.abs(x) <= v.sp_hw) & (t >= 0.0) & (t <= v.LS) & (np.abs(r @ e) <= v.sp_hh)
    return out


def solid(q: np.ndarray, v: Vert) -> np.ndarray:
    m = np.zeros(len(q), bool)
    for part in parts_inside(q, v).values():
        m |= part
    return m


def reach(v: Vert) -> float:
    """A radius from the vertebra's centre that holds every part."""
    return math.sqrt((v.TP / 2) ** 2 + (v.D + 60.0) ** 2 + (max(v.sap_top, -v.iap_bot) + 5) ** 2)


# ---- the truths of one vertebra -----------------------------------------------------------------

def truth(v: Vert) -> Dict[str, float]:
    """Every measure the phantom fixes, from its parameters alone."""
    t = {}
    t["endplate"], t["endplate_depth"] = v.W, v.D
    t["endplate_lower"], t["endplate_lower_depth"] = v.W, v.D
    # Panjabi's posterior height at the wall itself; the others where body.py reads them, 2.5 mm
    # inside the anterior surface and the posterior wall and half-way between
    t["h_post"] = v.Hp
    t["h_ant"], t["h_post_inset"], t["h_mid"] = height_at(v, v.D - 2.5), height_at(v, 2.5), height_at(v, v.D / 2)
    t["body_index_ant_post"] = t["h_ant"] / t["h_post_inset"]
    t["body_index_mid_post"] = t["h_mid"] / t["h_post_inset"]
    t["body_w_mid"], t["body_d_mid"] = v.W * v.waist, v.D * v.waist
    t["endplate_area"] = t["endplate_lower_area"] = math.pi * v.W * v.D / 4.0
    tilt = math.degrees(math.atan((v.Ha - v.Hp) / (2.0 * v.D)))
    t["endplate_incl"] = -tilt                      # positive where the plate descends anteriorly
    t["endplate_lower_incl"] = tilt
    t["wedge"] = 2.0 * tilt                         # positive where the body is taller in front
    # the centre (the median within a quarter of the half-axes, rho^2 = 1/32) below the
    # least-squares plane through the rim between 85 and 95 per cent of them (mean rho^2 0.8125)
    t["endplate_concavity"] = t["endplate_lower_concavity"] = v.concavity * (0.8125 - 1.0 / 32.0)
    t["canal_ap_min"] = v.lam_ap_top
    t["canal_ap_min_z"] = v.lam_top
    t["pedicle_w"], t["pedicle_h"] = v.ped_w, v.ped_h
    t["pedicle_area"] = math.pi * v.ped_w * v.ped_h / 4.0
    t["pedicle_angle_transverse"], t["pedicle_angle_sagittal"] = v.ped_t, v.ped_s
    t["pedicle_chord"] = chord_length(v, 1)
    t["interpedicular"] = interpedicular_at(v, v.ped_z)
    t["interpedicular_max"] = interpedicular_at(v, v.ped_z + v.ped_h / 4.0)
    t["transverse_length"] = v.TP / 2.0
    t["transverse_width"], t["tp_half"] = v.TP, v.TP / 2.0
    t["transverse_h"] = v.tp_h
    # across the lamina in the transverse plane: its front and back run at the same slant
    t["lamina_thickness"] = v.lam_t * math.cos(math.atan((v.pil_y + v.lam_ap_top) / v.pil_x))
    t["lamina_angle"] = math.degrees(2.0 * math.atan(v.pil_x / (v.pil_y + v.lam_ap_top)))
    t["spinous_angle"] = v.sp_angle
    t["facet_angle_axial"] = v.facet
    t["sap_apex_y"], t["sap_apex_z"] = v.sap_y, v.sap_top
    t["iap_apex_y"], t["iap_apex_z"] = v.iap_y, v.iap_bot
    # Eisenstein's lateral construction: the line from the SAP's apex to the IAP's inverted apex,
    # read at the centre of the body's cephalad half, measured from the body's posterior wall
    ze = 0.25 * v.Hp
    yl = v.sap_y + (v.iap_y - v.sap_y) * (v.sap_top - ze) / (v.sap_top - v.iap_bot)
    t["canal_ap_lateral_film"] = -yl
    t["interfacet_w_sup"], t["interfacet_w_inf"] = 2.0 * v.sap_x, 2.0 * v.iap_x
    return t


def dip(v: Vert, x: float, y: float) -> float:
    rho2 = (x / (v.W / 2)) ** 2 + ((y - v.D / 2) / (v.D / 2)) ** 2
    return v.concavity * max(1.0 - rho2, 0.0)


def height_at(v: Vert, y: float, x: float = 0.0) -> float:
    """The body's height between its end-plates at (x, y) of its own frame."""
    return v.Hp + (v.Ha - v.Hp) * y / v.D - 2.0 * dip(v, x, y)


def section(v: Vert, z: float, step: float = 0.05) -> Optional[Dict[str, float]]:
    """The canal in the transverse plane at height z, on a raster finer than any scan: its width
    through its middle, its midline depth, its depth at three quarters of its half-width out
    from the midline (the mean of the sides), and its area. None where the arch does not close."""
    from scipy import ndimage
    xs, ys = np.arange(-35.0, 35.0, step), np.arange(-45.0, 15.0, step)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    q = np.column_stack([X.ravel(), Y.ravel(), np.full(X.size, z)])
    bone = solid(q, v).reshape(X.shape)
    hole = ndimage.binary_fill_holes(bone) & ~bone
    lab, n = ndimage.label(hole)
    if n == 0:
        return None
    k = 1 + int(np.argmax(np.bincount(lab.ravel())[1:]))
    hx, hy = X[lab == k], Y[lab == k]
    xm, ym = 0.5 * (hx.min() + hx.max()), 0.5 * (hy.min() + hy.max())
    across = hx[np.abs(hy - ym) <= 0.5 * step]
    down = hy[np.abs(hx - xm) <= 0.5 * step]
    half = 0.5 * (hx.max() - hx.min())
    lat = []
    for side in (1, -1):
        col = hy[np.abs(hx - (xm + side * 0.75 * half)) <= 0.5 * step]
        lat.append(col.max() - col.min() + step)
    return {"width": across.max() - across.min() + step, "ap": down.max() - down.min() + step,
            "lateral": float(np.mean(lat)), "area": float((lab == k).sum()) * step * step}


def canal_profile(v: Vert, step_z: float = 0.25) -> Dict[str, float]:
    """The least of each canal measure over the heights where the arch closes."""
    rows = [s for s in (section(v, z) for z in np.arange(-v.Hp / 2, v.Hp / 2, step_z)) if s is not None]
    return {"canal_ap_lateral": min(r["lateral"] for r in rows), "canal_area_min": min(r["area"] for r in rows)}


def canal_ap_at(v: Vert, z: float) -> float:
    """The canal's midline depth at height z: from the body's posterior wall to the laminae."""
    return -float(lamina_front(np.zeros(1), np.array([z]), v)[0])


def interpedicular_at(v: Vert, z: float) -> float:
    """The gap between the pedicles' medial walls at height z in the plane of their isthmus,
    where a waisted pedicle has swollen by nothing. The plane cuts the pedicle's elliptic
    cylinder on the slant of its angles, so the section is the ellipse stretched by the
    secant of each: a across, b up."""
    a = (v.ped_w / 2) / math.cos(math.radians(v.ped_t))
    b = (v.ped_h / 2) / math.cos(math.radians(v.ped_s))
    s = (z - v.ped_z) / b
    if abs(s) >= 1.0:
        return float("nan")
    return v.canal_w + v.ped_w - 2.0 * a * math.sqrt(1.0 - s * s)


def chord_length(v: Vert, side: int, step: float = 0.01) -> float:
    """Along the pedicle's axis through its isthmus, the length of bone from where the line enters
    the posterior elements to where it leaves the body's anterior cortex, marched on the parts."""
    c, d = pedicle_axis(v, side)
    ts = np.arange(-120.0, 80.0, step)
    pts = c + ts[:, None] * d
    m = solid(pts, v)
    k = int(np.argmin(np.abs(ts)))
    if not m[k]:
        return float("nan")
    lo = k
    while lo > 0 and m[lo - 1]:
        lo -= 1
    hi = k
    while hi + 1 < len(m) and m[hi + 1]:
        hi += 1
    return float(ts[hi] - ts[lo] + step)


# ---- a column and a pelvis ----------------------------------------------------------------------

@dataclass
class Joint:
    """How the vertebra below sits under the one above: the disc's height at the centre of the
    lower vertebra's upper end-plate, along the lower vertebra's axis; the lower frame turned
    against the upper by a sagittal angle (positive opens the disc in front, as lordosis does),
    a coronal angle (about the upper's y axis) and an axial turn (about its z axis), in degrees;
    and a slip of the upper vertebra forward on the lower, in mm along the lower's y axis."""
    gap: float = 10.0
    sagittal: float = 0.0
    coronal: float = 0.0
    axial: float = 0.0
    slip: float = 0.0


@dataclass
class Placed:
    level: str
    v: Vert
    R: np.ndarray            # columns are the vertebra's x, y, z in the world
    c: np.ndarray            # its local origin in the world


def plate_centre(v: Vert, top: bool) -> np.ndarray:
    z = (v.Hp + v.Ha) / 4.0 - v.concavity
    return np.array([0.0, v.D / 2, z if top else -z])


def chain(levels: Sequence[str], verts: Dict[str, Vert], joints: Dict[str, Joint],
          R0: np.ndarray = None, c0: Sequence[float] = (0.0, 0.0, 0.0)) -> List[Placed]:
    """The vertebrae top down, each placed under the one above by the joint named for the lower
    level. The disc's height is set between the two end-plates' centres; where the end-plates are
    concave the centre is their deepest point."""
    R = np.eye(3) if R0 is None else np.asarray(R0, float)
    c = np.asarray(c0, float)
    out = [Placed(levels[0], verts[levels[0]], R, c)]
    for lv in levels[1:]:
        up = out[-1]
        j = joints.get(lv, Joint())
        v = verts[lv]
        Rl = (up.R @ rotation((0, 0, 1), j.axial) @ rotation((0, 1, 0), j.coronal)
              @ rotation((1, 0, 0), -j.sagittal))
        p_up = up.c + up.R @ (plate_centre(up.v, False) - np.array([0.0, up.v.D / 2, 0.0]))
        p_up = p_up + up.R @ np.array([0.0, up.v.D / 2, 0.0])
        p_low = p_up - Rl @ np.array([0.0, j.slip, j.gap])
        cl = p_low - Rl @ plate_centre(v, True)
        out.append(Placed(lv, v, Rl, cl))
    return out


@dataclass
class Pelvis:
    """A sacrum under the lowest vertebra and two hip bones. The sacrum is S1's body, an elliptic
    cylinder whose top is the S1 end-plate, tilted against the lowest vertebra's frame by `s1_tilt`
    degrees (positive tips its front down, as the lumbosacral angle does) at a disc height of
    `gap`; the hip bones are shells round spherical sockets of radius `socket` centred at
    (+-half_width, hip_y, hip_z) in the S1 end-plate's own frame, each with a wing rising to its
    crest at crest_z."""
    gap: float = 11.0
    s1_tilt: float = 10.0
    s1_w: float = 50.0
    s1_d: float = 36.0
    s1_h: float = 30.0
    socket: float = 24.0
    shell: float = 6.0
    half_width: float = 85.0
    hip_y: float = 45.0
    hip_z: float = -95.0
    crest_z: float = 45.0


def pelvis_frame(low: Placed, p: Pelvis) -> Tuple[np.ndarray, np.ndarray]:
    """S1's frame: its origin at the end-plate's centre, z normal to the end-plate."""
    Rs = low.R @ rotation((1, 0, 0), -p.s1_tilt)
    p_up = low.c + low.R @ plate_centre(low.v, False)
    origin = p_up - Rs @ np.array([0.0, 0.0, p.gap])
    return Rs, origin


def pelvis_parts(q_s1: np.ndarray, p: Pelvis) -> Dict[str, np.ndarray]:
    """Points in S1's frame (origin at the end-plate's centre): the sacrum and each hip bone."""
    x, y, z = q_s1[:, 0], q_s1[:, 1], q_s1[:, 2]
    sac = ((x / (p.s1_w / 2)) ** 2 + (y / (p.s1_d / 2)) ** 2 <= 1.0) & (z <= 0.0) & (z >= -p.s1_h)
    ala = (np.abs(x) <= p.s1_w / 2 + 22.0) & (y >= -p.s1_d / 2) & (y <= 0.2 * p.s1_d) & (z <= -4.0) & (z >= -p.s1_h + 4)
    out = {"sacrum": sac | ala}
    for side, name in ((1, "right"), (-1, "left")):
        h = np.array([side * p.half_width, p.hip_y, p.hip_z])
        r = q_s1 - h
        dist = np.linalg.norm(r, axis=1)
        opening = np.array([side * 0.75, 0.2, -0.63])
        opening /= np.linalg.norm(opening)
        cosang = (r @ opening) / np.maximum(dist, 1e-9)
        cup = (dist >= p.socket) & (dist <= p.socket + p.shell) & (cosang <= 0.25)
        # the wing: a plate from above the socket up to the crest, lateral of the sacrum
        wing = ((np.abs(side * x - (p.half_width - 8.0)) <= 4.0) & (np.abs(y - (p.hip_y - 25.0)) <= 30.0)
                & (z >= p.hip_z + p.socket) & (z <= p.crest_z))
        out["hip_" + name] = cup | wing
    return out


def pelvis_truth(low: Placed, p: Pelvis) -> Dict[str, object]:
    """The pelvic incidence and its points, in the world."""
    Rs, o = pelvis_frame(low, p)
    hips = {name: o + Rs @ np.array([side * p.half_width, p.hip_y, p.hip_z]) for side, name in ((1, "right"), (-1, "left"))}
    mid = 0.5 * (hips["right"] + hips["left"])
    lr = Rs[:, 0]
    n = Rs[:, 2]
    to_hip = mid - o
    proj = lambda u: u - (u @ lr) * lr
    a, b = proj(-n), proj(to_hip)
    pi = math.degrees(math.acos(float(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))))
    return {"pelvic_incidence": pi, "hip_right": hips["right"], "hip_left": hips["left"], "s1_centre": o,
            "s1_normal": n, "crest_z_world": None}


# ---- drawing ------------------------------------------------------------------------------------

LEVEL_IDS = {**{"C%d" % i: i for i in range(1, 8)}, **{"T%d" % i: 7 + i for i in range(1, 13)},
             **{"L%d" % i: 19 + i for i in range(1, 7)}}
HIP_LEFT, HIP_RIGHT, SACRUM = 26, 27, 28       # ENHANCE.PET's vertebra group (scanimport/schemes.py)


def draw(placed: List[Placed], spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 7.0),
         pelvis: Optional[Pelvis] = None, margin: float = 6.0, dtype=np.uint8, strict: bool = True):
    """A label volume holding the placed vertebrae under ENHANCE.PET's ids, and the pelvis where
    given. Returns (labels, affine). Two structures that claim one voxel mean the phantom's
    neighbours collide, which a real mask never shows, so strict refuses it."""
    pts = [pl.c for pl in placed]
    rads = [reach(pl.v) for pl in placed]
    lo = np.min([p - r for p, r in zip(pts, rads)], axis=0) - margin
    hi = np.max([p + r for p, r in zip(pts, rads)], axis=0) + margin
    if pelvis is not None:
        Rs, o = pelvis_frame(placed[-1], pelvis)
        corners = np.array([[a, b, c] for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)], float)
        span = np.array([pelvis.half_width + pelvis.socket + pelvis.shell + 4, 110.0, 160.0])
        world = o + (corners * span) @ Rs.T
        lo, hi = np.minimum(lo, world.min(0) - margin), np.maximum(hi, world.max(0) + margin)
    A, shape_v, affine = grid_about(lo, hi, spacing, grid_turn)
    Ainv, origin = np.linalg.inv(A), affine[:3, 3]
    lab = np.zeros(shape_v, dtype)
    clash = [0]

    def fill(centre, radius, R, test, value_of):
        box = np.array([centre - radius, centre + radius])
        bc = np.array([[a, b, c] for a in box[:, 0] for b in box[:, 1] for c in box[:, 2]])
        bi = (bc - origin) @ Ainv.T
        b0 = np.maximum(np.floor(bi.min(0)).astype(int), 0)
        b1 = np.minimum(np.ceil(bi.max(0)).astype(int) + 1, np.array(shape_v))
        for k in range(b0[2], b1[2]):              # one slice at a time keeps the memory small
            g = np.stack(np.meshgrid(np.arange(b0[0], b1[0]), np.arange(b0[1], b1[1]), [k], indexing="ij"),
                         -1).reshape(-1, 3)
            if not len(g):
                continue
            world = g @ A.T + origin
            q = (world - centre) @ R
            for value, m in value_of(test(q)):
                sel = tuple(g[m].T)
                clash[0] += int(((lab[sel] != 0) & (lab[sel] != value)).sum())
                lab[sel] = value

    for pl in placed:
        fill(pl.c, reach(pl.v), pl.R, lambda q, v=pl.v: solid(q, v), lambda m, lv=pl.level: [(LEVEL_IDS[lv], m)])
    if pelvis is not None:
        Rs, o = pelvis_frame(placed[-1], pelvis)
        radius = float(np.linalg.norm([pelvis.half_width + pelvis.socket + pelvis.shell + 4, 110.0, 160.0]))
        fill(o, radius, Rs, lambda q: pelvis_parts(q, pelvis),
             lambda parts: [(SACRUM, parts["sacrum"]), (HIP_RIGHT, parts["hip_right"]), (HIP_LEFT, parts["hip_left"])])
    if strict and clash[0]:
        raise ValueError("%d voxels fall in two structures: the phantom's parts collide" % clash[0])
    return lab, affine


def straight(levels: Sequence[str], v: Optional[Vert] = None, joint: Optional[Joint] = None,
             tilt=((1.0, 0.3, 0.0), 18.0)) -> List[Placed]:
    """A column of identical vertebrae under identical joints, tilted against the scanner."""
    v = v or Vert()
    j = joint or Joint()
    return chain(levels, {lv: v for lv in levels}, {lv: j for lv in levels[1:]}, R0=rotation(*tilt))
