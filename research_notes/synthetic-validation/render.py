"""Drawings of synthetic vertebrae in Benzel's manner, beside Panjabi's means.

    python3 -I render.py --out figures

Benzel's drawings are line art: black outlines on white, the canal hatched, a scale bar, no
shading but where a third dimension needs it. Three figures are drawn here, each from people the
generator draws at its own settings with a fixed seed (SEED), so that what a quality indicator
counts (qi.py) can be seen on one vertebra:

- render1_axial: L3 seen from above, at Panjabi's means, for a synthetic person that passes every
  indicator, for one whose canal is larger than the rectangle of its own width and depth (box),
  and for one whose end-plate is under half of its own (convex);
- render2_column: the lumbar column from in front, Panjabi's means beside two synthetic people,
  each body flagged by any indicator marked;
- render3_solid: the same columns as solids, shaded in grey from one light.

A section is drawn as the superellipse whose width, depth and area are the measures: of every
convex shape with those extents it is the one family that spans the whole range the area allows,
from the diamond (half of width times depth) to the rectangle (all of it). Where the area passes
the rectangle no shape exists; the rectangle is drawn dashed and the excess written beside it.
The tables hold no lamina, no pedicle length and no process thickness: those are drawn at
fixed sizes (FIXED_MM), as a drawing must, and carry no number. Each pedicle runs from the
lamina up under the body's posterior outline (pedicle_top), so no gap opens between them.
Panjabi's spinous length runs from the centre of the upper end-plate, his origin, to the tip of
the process (panjabi1992 p. 302, the reread's note), so the tip is drawn that far behind the
end-plate's centre, as if the process were level; it slopes down in life, so its true reach from
above is shorter. (schwingcheck's mnemonics.py starts it at the canal's posterior wall; the note
and the paper start it at the end-plate.)
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from typing import Dict, List, Optional, Tuple

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [REPO, HERE]

from schwingcheck import LEVELS  # noqa: E402
from schwingcheck import measures as MS  # noqa: E402
from synthval import house as H  # noqa: E402
from synthval import qi as Q  # noqa: E402
from synthval.population import GENERATOR, draw  # noqa: E402

SEED = 2029
PEOPLE = 4000
LUMBAR = ("L1", "L2", "L3", "L4", "L5")
DISC_MM = 5.0
FIXED_MM = {"lamina": 6.0, "pedicle_length_share": 0.55, "process_thickness": 7.0, "spinous_height_share": 0.8}
HATCH = "/////"
KEYS = ("endplate", "endplate_depth", "endplate_area", "endplate_lower", "endplate_lower_depth", "endplate_lower_area",
        "h_post", "canal_w", "canal_ap", "canal_area", "pedicle", "pedicle_h", "spinous_length", "transverse_width")


# ----- shapes ----------------------------------------------------------------------------------

def area_share(n: float) -> float:
    """The area of the superellipse |x/a|^n + |y/b|^n = 1 over that of its bounding rectangle."""
    return math.exp(2 * math.lgamma(1 + 1 / n) - math.lgamma(1 + 2 / n))


def exponent_for(share: float) -> Optional[float]:
    """The superellipse exponent whose area is `share` of the rectangle, or None where no shape
    of those extents holds that area (share of one or more)."""
    if not 0.05 < share < 0.999:
        return None
    lo, hi = 0.2, 400.0
    for _ in range(80):
        mid = math.sqrt(lo * hi)
        if area_share(mid) < share:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def outline(width: float, depth: float, area: float, centre: Tuple[float, float], points: int = 240):
    """The section's outline as (x, y) arrays, and its exponent (None: the rectangle, impossible)."""
    n = exponent_for(area / (width * depth))
    t = np.linspace(0, 2 * np.pi, points)
    a, b = width / 2, depth / 2
    if n is None:
        x = np.array([-a, a, a, -a, -a])
        y = np.array([-b, -b, b, b, -b])
    else:
        c, s = np.cos(t), np.sin(t)
        x = a * np.sign(c) * np.abs(c) ** (2 / n)
        y = b * np.sign(s) * np.abs(s) ** (2 / n)
    return x + centre[0], y + centre[1], n


# ----- the people drawn ------------------------------------------------------------------------

def table_means() -> Dict[str, Dict[str, float]]:
    ms = MS.pool()
    mu, _ = MS.arrays(ms, LEVELS)
    keys = [MS.archive_key(m) for m in ms]
    return {lv: {k: float(mu[keys.index(k), LEVELS.index(lv)]) for k in KEYS} for lv in LEVELS}


def person(pop, i: int) -> Dict[str, Dict[str, float]]:
    return {lv: {k: float(pop.true[i, pop.level_index(lv), pop.keys.index(k)]) for k in KEYS} for lv in LEVELS}


def shape_factors(pop, area: str, width: str, depth: str, level: str) -> np.ndarray:
    j = pop.level_index(level)
    return pop.true[:, j, pop.keys.index(area)] / (pop.true[:, j, pop.keys.index(width)] * pop.true[:, j, pop.keys.index(depth)])


def chosen_people(pop) -> Dict[str, int]:
    """Three people, chosen by rule and not by eye: the one whose L3 passes every indicator and
    sits nearest Panjabi's means (in his SDs, over the measures drawn); the one whose L3 canal
    passes its box by the median excess of all that do; the one whose L3 end-plate falls under
    the convex bound by the median shortfall."""
    fl = Q.flags(pop)
    j = pop.level_index("L3")
    ms = MS.pool()
    mu, sd = MS.arrays(ms, LEVELS)
    keys = [MS.archive_key(m) for m in ms]
    cols = [keys.index(k) for k in KEYS]
    z = (pop.true[:, j, :][:, [pop.keys.index(k) for k in KEYS]] - mu[cols, LEVELS.index("L3")]) / sd[cols, LEVELS.index("L3")]
    passes = ~fl.any()[:, j]
    typical = int(np.where(passes)[0][np.argmin((z[passes] ** 2).sum(1))])
    canal = shape_factors(pop, "canal_area", "canal_w", "canal_ap", "L3")
    over = np.where(canal > 1.0)[0]
    boxed = int(over[np.argsort(canal[over])[len(over) // 2]])
    plate = shape_factors(pop, "endplate_area", "endplate", "endplate_depth", "L3")
    under = np.where(plate < Q.CONVEX_LEAST)[0]
    concave = int(under[np.argsort(plate[under])[len(under) // 2]])
    return {"passes": typical, "box": boxed, "convex": concave}


def flagged_levels(pop, i: int) -> Dict[str, List[str]]:
    fl = Q.flags(pop)
    return {lv: [k for k, v in fl.by.items() if v[i, pop.level_index(lv)]] for lv in LEVELS}


# ----- figure 1: L3 from above -----------------------------------------------------------------

def draw_axial(ax, v: Dict[str, float]) -> List[str]:
    """One vertebra seen from above, anterior up: the body, the canal hatched, the pedicles, the
    laminae, the transverse and spinous processes, drawn back to front so that each part covers
    the lines of the parts behind it. Returns what could not be drawn."""
    from matplotlib.patches import Polygon, Rectangle
    notes = []
    cw, ca, pw = v["canal_w"], v["canal_ap"], v["pedicle"]
    plen = FIXED_MM["pedicle_length_share"] * ca
    lam = FIXED_MM["lamina"]
    th = FIXED_MM["process_thickness"]
    tip = spinous_tip(v)
    bx, by, bn = outline(v["endplate"], v["endplate_depth"], v["endplate_area"], (0, v["endplate_depth"] / 2))
    ax.add_patch(Polygon([(-3.5, -ca - lam / 2), (3.5, -ca - lam / 2), (1.5, tip), (-1.5, tip)], closed=True,
                         facecolor="white", edgecolor=H.INK, linewidth=0.8))
    for side in (-1, 1):
        outer, inner = side * (cw / 2 + pw), side * cw / 2
        tx = side * v["transverse_width"] / 2
        ax.add_patch(Rectangle((min(outer, tx), -plen - th / 2), abs(tx - outer), th, facecolor="white", edgecolor=H.INK,
                               linewidth=0.8))
        ax.add_patch(Polygon([(inner, -plen), (outer, -plen), (side * 3.5, -ca - lam), (0, -ca - lam), (0, -ca)],
                             closed=True, facecolor="white", edgecolor=H.INK, linewidth=0.8))
        top = pedicle_top(v["endplate"], v["endplate_depth"], bn, max(abs(inner), abs(outer)))
        ax.add_patch(Rectangle((min(inner, outer), -plen), pw, plen + top, facecolor="white", edgecolor=H.INK,
                               linewidth=0.8))
    cx, cy, cn = outline(cw, ca, v["canal_area"], (0, -ca / 2))
    ax.add_patch(Polygon(np.c_[cx, cy], closed=True, facecolor="white", edgecolor=H.INK, linewidth=0.9, hatch=HATCH,
                         linestyle="-" if cn is not None else "--"))
    if cn is None:
        notes.append("canal area %.0f%% of its box" % (100 * v["canal_area"] / (cw * ca)))
    ax.add_patch(Polygon(np.c_[bx, by], closed=True, facecolor="white", edgecolor=H.INK, linewidth=0.9,
                         linestyle="-" if bn is not None else "--"))
    if bn is None:
        notes.append("end-plate area %.0f%% of its box" % (100 * v["endplate_area"] / (v["endplate"] * v["endplate_depth"])))
    return notes


def spinous_tip(v: Dict[str, float]) -> float:
    """Where the spinous process ends, its length taken from the upper end-plate's centre, the
    body being drawn from y = 0 (its posterior wall) to y = depth."""
    return v["endplate_depth"] / 2 - v["spinous_length"]


def pedicle_top(width: float, depth: float, n: Optional[float], x: float, overlap: float = 1.0) -> float:
    """How far up a pedicle at |x| runs to meet the body: the body's posterior outline there, the
    superellipse y = b - b (1 - |x / a|^n)^(1 / n) above its posterior wall, and a millimetre more,
    held at the body's centre; the body, drawn last, covers the overlap."""
    a, b = width / 2, depth / 2
    if abs(x) >= a:
        return b
    rise = 0.0 if n is None else b - b * (1 - (abs(x) / a) ** n) ** (1 / n)
    return min(b, rise + overlap)


def scale_bar(ax, x: float, y: float, mm: float = 10.0):
    ax.plot([x, x + mm], [y, y], color=H.INK, linewidth=1.6, solid_capstyle="butt")
    ax.text(x + mm / 2, y - 2.5, "%g mm" % mm, ha="center", va="top", fontsize=7)


def axial_rows(name: str, v: Dict[str, float]) -> List[dict]:
    rows = []
    for k in KEYS:
        rows.append({"panel": name, "level": "L3", "measure": k, "value": v[k]})
    for area, w, d in (("endplate_area", "endplate", "endplate_depth"), ("canal_area", "canal_w", "canal_ap")):
        share = v[area] / (v[w] * v[d])
        rows.append({"panel": name, "level": "L3", "measure": area + " / (width x depth)", "value": share,
                     "exponent": exponent_for(share) if exponent_for(share) is not None else ""})
    return rows


def fig_axial(pop, chosen: Dict[str, int], out: str) -> List[str]:
    plt = H.style()
    means = table_means()
    panels = [("Panjabi's means", means["L3"]),
              ("a synthetic L3 that passes", person(pop, chosen["passes"])["L3"]),
              ("its canal passes its box", person(pop, chosen["box"])["L3"]),
              ("its end-plate under half its box", person(pop, chosen["convex"])["L3"])]
    fig, axes = plt.subplots(1, 4, figsize=(10.0, 4.6))
    rows = []
    deepest = min(spinous_tip(v) for _, v in panels) - 4
    for p, (ax, (title, v)) in enumerate(zip(axes, panels)):
        notes = draw_axial(ax, v)
        ax.set_aspect("equal")
        ax.set_xlim(-56, 56)
        ax.set_ylim(deepest - 8, 50)
        ax.axis("off")
        scale_bar(ax, 24, deepest)
        for i, note in enumerate(notes):
            ax.text(0, 44 - 6 * i, note, ha="center", va="bottom", fontsize=7, style="italic")
        H.letter(ax, chr(65 + p), title)
        rows += axial_rows(title, v)
    fig.tight_layout()
    H.write_csv(out, "render1_axial", rows)
    return H.save(fig, out, "render1_axial", (
        "The third lumbar vertebra from above, anterior up, drawn to its measures: Panjabi's means, then "
        "three synthetic people the generator draws (seed %d). Each section is the superellipse of its "
        "width, depth and area, dashed where none holds the area. The spinous process reaches its "
        "length from the end-plate's centre. Laminae and process thickness are fixed." % SEED))


# ----- figure 2: the column from in front -----------------------------------------------------

def draw_column(ax, col: Dict[str, Dict[str, float]], marks: Optional[Dict[str, List[str]]] = None) -> float:
    """The lumbar column from in front, to its measures: a box per body (end-plate width by
    posterior height), the canal hatched over it, the transverse span as a line at mid-body.
    A body any indicator flags is drawn with a heavier outline and its flags written beside it."""
    from matplotlib.patches import Rectangle
    y = 0.0
    for lv in LUMBAR:
        v = col[lv]
        w, h, c = v["endplate"], v["h_post"], v["canal_w"]
        flags = (marks or {}).get(lv, [])
        ax.add_patch(Rectangle((-w / 2, -(y + h)), w, h, facecolor="white", edgecolor=H.INK,
                               linewidth=2.0 if flags else 0.8))
        ax.add_patch(Rectangle((-c / 2, -(y + h)), c, h, facecolor="none", edgecolor=H.INK, hatch=HATCH, linewidth=0.3))
        t = v["transverse_width"] / 2
        ax.plot([-t, -w / 2], [-(y + h / 2)] * 2, color=H.INK, linewidth=0.7)
        ax.plot([w / 2, t], [-(y + h / 2)] * 2, color=H.INK, linewidth=0.7)
        ax.text(-58, -(y + h / 2), lv, ha="right", va="center", fontsize=7)
        if flags:
            ax.text(58, -(y + h / 2), ", ".join(flags), ha="left", va="center", fontsize=6.5, style="italic")
        y += h + DISC_MM
    return y


def fig_column(pop, chosen: Dict[str, int], out: str) -> List[str]:
    plt = H.style()
    from matplotlib.patches import Patch
    means = table_means()
    columns = [("Panjabi's means", means, None), ("synthetic, L3 passes", person(pop, chosen["passes"]),
                                                    flagged_levels(pop, chosen["passes"])),
               ("synthetic, L3 canal over its box", person(pop, chosen["box"]), flagged_levels(pop, chosen["box"]))]
    fig, axes = plt.subplots(1, 3, figsize=(10.0, 5.0))
    rows = []
    tallest = max(sum(col[lv]["h_post"] + DISC_MM for lv in LUMBAR) for _, col, _ in columns)
    for p, (ax, (title, col, marks)) in enumerate(zip(axes, columns)):
        draw_column(ax, col, marks)
        ax.set_aspect("equal")
        ax.set_xlim(-66, 92)
        ax.set_ylim(-tallest - 14, 6)
        ax.axis("off")
        scale_bar(ax, -50, -tallest - 4)
        H.letter(ax, chr(65 + p), title)
        for lv in LUMBAR:
            rows.append(dict({"panel": title, "level": lv, "flags": ";".join((marks or {}).get(lv, []))},
                             **{k: col[lv][k] for k in ("endplate", "h_post", "canal_w", "transverse_width")}))
    axes[0].legend([Patch(facecolor="white", edgecolor=H.INK), Patch(facecolor="none", edgecolor=H.INK, hatch=HATCH)],
                   ["body", "canal"], loc="upper right", fontsize=6.5, handlelength=1.2)
    fig.tight_layout()
    H.write_csv(out, "render2_column", rows)
    return H.save(fig, out, "render2_column", (
        "The lumbar column from in front, each body its end-plate width by its posterior height with the "
        "canal hatched over it and the transverse span as a line: Panjabi's means and two synthetic "
        "people. A heavy outline marks a body some quality indicator flags; the flags are named."))


# ----- figure 3: solids ------------------------------------------------------------------------

def prism(x0, y0, x1, y1, z0, z1):
    """The six faces of a box between two outlines, as lists of (x, y, z) corners."""
    return [[(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
            [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
            [(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]]


BOX_SHARE = 0.998     # an end-plate area at or past its box is lofted at this share of it


def plates_at_box(v: Dict[str, float]) -> List[str]:
    """The end-plates of one vertebra whose area passes BOX_SHARE of their box, drawn as nearly
    the box in the solid."""
    return [k for k, w, d in (("endplate_area", "endplate", "endplate_depth"),
                               ("endplate_lower_area", "endplate_lower", "endplate_lower_depth"))
            if v[k] > BOX_SHARE * v[w] * v[d]]


def body_faces(v: Dict[str, float], z_top: float, points: int = 48):
    """The body as a loft from its lower end-plate to its upper, each the superellipse of its
    measures; an area at or past its box (plates_at_box) is held at BOX_SHARE of it, since a loft
    needs points on a curve, and the drawing's CSV says which."""
    top = outline(v["endplate"], v["endplate_depth"], min(v["endplate_area"], BOX_SHARE * v["endplate"] * v["endplate_depth"]),
                  (0, v["endplate_depth"] / 2), points)
    low = outline(v["endplate_lower"], v["endplate_lower_depth"],
                  min(v["endplate_lower_area"], BOX_SHARE * v["endplate_lower"] * v["endplate_lower_depth"]),
                  (0, v["endplate_lower_depth"] / 2), points)
    z_low = z_top - v["h_post"]
    faces = [list(zip(top[0], top[1], [z_top] * points)), list(zip(low[0], low[1], [z_low] * points))]
    for i in range(points - 1):
        faces.append([(top[0][i], top[1][i], z_top), (top[0][i + 1], top[1][i + 1], z_top),
                      (low[0][i + 1], low[1][i + 1], z_low), (low[0][i], low[1][i], z_low)])
    return faces


def posterior_faces(v: Dict[str, float], z_top: float):
    """Pedicles, laminae and processes as boxes; the sizes the tables do not give are FIXED_MM."""
    cw, ca, pw, ph = v["canal_w"], v["canal_ap"], v["pedicle"], v["pedicle_h"]
    zc = z_top - v["h_post"] * 0.45
    plen = FIXED_MM["pedicle_length_share"] * ca
    th = FIXED_MM["process_thickness"]
    lam = FIXED_MM["lamina"]
    n = exponent_for(min(v["endplate_area"], BOX_SHARE * v["endplate"] * v["endplate_depth"])
                     / (v["endplate"] * v["endplate_depth"]))
    faces = []
    for side in (-1, 1):
        x0, x1 = sorted((side * cw / 2, side * (cw / 2 + pw)))
        top = pedicle_top(v["endplate"], v["endplate_depth"], n, max(abs(x0), abs(x1)))
        faces += prism(x0, -ca, x1, top, zc - ph / 2, zc + ph / 2)
        t0, t1 = sorted((side * (cw / 2 + pw), side * v["transverse_width"] / 2))
        faces += prism(t0, -plen, t1, -plen + th, zc - th / 2, zc + th / 2)
    faces += prism(-(cw / 2 + pw), -ca - lam, cw / 2 + pw, -ca, zc - ph / 2, zc + ph / 2)
    sh = FIXED_MM["spinous_height_share"] * ph
    faces += prism(-th / 4, spinous_tip(v), th / 4, -ca - lam, zc - sh / 2 - 3, zc + sh / 2 - 3)
    return faces


def shade(faces, light=(-0.45, 0.65, 0.6), base=0.35):
    """A grey for each face from Lambert's law with one light, the faces' normals taken from
    their first three corners and turned toward the light where they face away."""
    light = np.array(light) / np.linalg.norm(light)
    out = []
    for f in faces:
        p = np.array(f[:3], float)
        nrm = np.cross(p[1] - p[0], p[2] - p[0])
        norm = np.linalg.norm(nrm)
        lam = abs(float(nrm @ light)) / norm if norm > 0 else 0.0
        g = base + (1 - base) * lam
        out.append((g, g, g))
    return out


def draw_solid(ax, col: Dict[str, Dict[str, float]]):
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    z = 0.0
    faces = []
    for lv in LUMBAR:
        v = col[lv]
        faces += body_faces(v, z)
        faces += posterior_faces(v, z)
        z -= v["h_post"] + DISC_MM
    coll = Poly3DCollection(faces, facecolors=shade(faces), edgecolors=(0.15, 0.15, 0.15), linewidths=0.15)
    ax.add_collection3d(coll, autolim=False)
    ax.set_xlim(-50, 50)
    ax.set_ylim(-75, 45)
    ax.set_zlim(z, 0)
    ax.set_box_aspect((100, 140, -z))
    ax.view_init(elev=14, azim=-130)
    ax.set_axis_off()
    return -z


def fig_solid(pop, chosen: Dict[str, int], out: str) -> List[str]:
    plt = H.style()
    means = table_means()
    columns = [("Panjabi's means", means), ("synthetic, L3 passes", person(pop, chosen["passes"])),
               ("synthetic, L3 end-plate under half its box", person(pop, chosen["convex"]))]
    fig = plt.figure(figsize=(10.0, 5.2))
    rows = []
    for p, (title, col) in enumerate(columns):
        ax = fig.add_subplot(1, 3, p + 1, projection="3d")
        height = draw_solid(ax, col)
        ax.set_title("%s   %s" % (chr(65 + p), title), loc="left", fontsize=9, fontweight="normal")
        rows += [dict({"panel": title, "level": lv, "column_height": height,
                       "plates drawn at their box": ";".join(plates_at_box(col[lv]))}, **col[lv]) for lv in LUMBAR]
    fig.subplots_adjust(left=0.0, right=1.0, top=0.93, bottom=0.0, wspace=0.0)
    H.write_csv(out, "render3_solid", rows)
    return H.save(fig, out, "render3_solid", (
        "Lumbar columns as solids, seen from the left and behind, shaded grey from one light: Panjabi's "
        "means and two synthetic people of the first drawing. Bodies are lofted between the two "
        "end-plates' superellipses, an area past its box drawn as the box%s; pedicles, laminae and "
        "processes are boxes, their thicknesses fixed." % at_box(columns)))


def at_box(columns) -> str:
    """The caption's note of which panels' end-plates were drawn as their box."""
    found = ["%s's %s %s" % (chr(65 + p), lv, "lower plate" if k.startswith("endplate_lower") else "upper plate")
             for p, (_, col) in enumerate(columns) for lv in LUMBAR for k in plates_at_box(col[lv])]
    return " (%s)" % ", ".join(found) if found else ""


RENDERS = (fig_axial, fig_column, fig_solid)


def render_all(out: str) -> Dict[str, List[str]]:
    pop = draw(GENERATOR, PEOPLE, SEED, MS.pool())
    chosen = chosen_people(pop)
    written = {}
    for f in RENDERS:
        paths = f(pop, chosen, out)
        written[os.path.splitext(os.path.basename(paths[0]))[0]] = paths
    return written


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=os.path.join(HERE, "figures"))
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    for name, paths in render_all(args.out).items():
        print(name, len(paths))
    return 0


if __name__ == "__main__":
    sys.exit(main())
