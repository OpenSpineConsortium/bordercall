import re, sys
path = sys.argv[1]
src = open(path).read()

def swap(old, new, count=1):
    global src
    assert src.count(old) == count, (old[:60], src.count(old))
    src = src.replace(old, new)

# the typing import gains Callable, for the builders' list
swap("from typing import Dict, List, Optional, Tuple\n", "from typing import Callable, Dict, List, Optional, Tuple\n")

# Panjabi's posterior height, after the plates
swap('''        out.append(Line(name + "_depth", v.level, y1 - v.wall_y0, a, b, "length", "sagittal"))
    return out


# ---- the canal ''', '''        out.append(Line(name + "_depth", v.level, y1 - v.wall_y0, a, b, "length", "sagittal"))
    return out


def panjabi_height(v: A.Vertebra) -> List[Line]:
    """Panjabi's posterior height (h_post) as scanimport.geometry.body_chords takes it on the body
    anatomy.panjabi_body reads it from, with y measured from the wall line: the median, over the
    cells of a grid across the column, of the height surface to surface of the body's points
    within POSTERIOR_SHARE of its depth from the wall and a quarter of its width from its middle
    (column_height). Drawn in the cell whose height is nearest the median, at the cell's mean
    place across and up the wall line, so the ends lie the cell's height apart along z."""
    if v.touching[v.body].any() or v.body.sum() < G.MIN_BODY_VOXELS:
        return []
    Q = A.square_to_wall(v, v.body_pts)
    depth = G.surface(Q[:, 1], True, v.fy) - v.wall_y0
    width = G.extent(Q[:, 0], v.fx)
    xm = 0.5 * (Q[:, 0].min() + Q[:, 0].max())
    post = Q[(Q[:, 1] <= v.wall_y0 + G.POSTERIOR_SHARE * depth) & (np.abs(Q[:, 0] - xm) <= 0.25 * width)]
    value = G.column_height(post, v.pixel, v.fz)
    if not np.isfinite(value):
        return []
    order, starts, ends = G.cells(post, v.pixel)
    P = post[order]
    runs = [(P[a:b], G.surface(P[a:b, 2], False, v.fz), G.surface(P[a:b, 2], True, v.fz))
            for a, b in zip(starts, ends) if b - a >= 2]
    cell, lo, hi = min(runs, key=lambda r: abs((r[2] - r[1]) - value))
    x, y = float(cell[:, 0].mean()), float(cell[:, 1].mean())
    a, b = v.points_world(np.array([from_wall(v, x, y, lo), from_wall(v, x, y, hi)]))
    return [Line("h_post", v.level, value, a, b, "median", "sagittal")]


# ---- the canal ''')

# the canal's two side walls, from one section, shared by the width and the interpedicular fallback
swap('''def across_walls(v: A.Vertebra, s: A.CanalSlab) -> Optional[Tuple[float, float, float]]:
    """The canal's two side walls through the hole's middle in one slab, as
    scanimport.geometry.canal_walls reads the width: (left, right, y)."""
    for sec in G.sections(v.loc, v.fz, v.pixel, as_hole=True):
        if sec.canal is None or abs(sec.w - s.z) > 1e-9:
            continue
        c, p = sec.canal, sec.pts
        xm, ym = 0.5 * (c[:, 0].min() + c[:, 0].max()), 0.5 * (c[:, 1].min() + c[:, 1].max())
        across = p[np.abs(p[:, 1] - ym) <= 0.75 * v.pixel]
        right, left = across[across[:, 0] > xm, 0], across[across[:, 0] < xm, 0]
        if len(right) and len(left):
            return G.surface(left, True, v.fx), G.surface(right, False, v.fx), ym
    return None
''', '''def section_walls(sec: G.Section, pixel: float, fx: float) -> Optional[Tuple[float, float, float]]:
    """The canal's two side walls through the hole's middle in one section, where
    scanimport.geometry.canal_walls reads the width: (left, right, y)."""
    c, p = sec.canal, sec.pts
    xm, ym = 0.5 * (c[:, 0].min() + c[:, 0].max()), 0.5 * (c[:, 1].min() + c[:, 1].max())
    across = p[np.abs(p[:, 1] - ym) <= 0.75 * pixel]
    right, left = across[across[:, 0] > xm, 0], across[across[:, 0] < xm, 0]
    if not (len(right) and len(left)):
        return None
    return G.surface(left, True, fx), G.surface(right, False, fx), ym


def across_walls(v: A.Vertebra, s: A.CanalSlab) -> Optional[Tuple[float, float, float]]:
    """The canal's two side walls in the section of one of anatomy's slabs: (left, right, y)."""
    for sec in G.sections(v.loc, v.fz, v.pixel, as_hole=True):
        if sec.canal is not None and abs(sec.w - s.z) <= 1e-9:
            walls = section_walls(sec, v.pixel, v.fx)
            if walls is not None:
                return walls
    return None


def canal_reading(v: A.Vertebra) -> Optional[Tuple[List[G.Section], Tuple[float, float], Dict[str, float]]]:
    """The sections, the band along z and the canal scanimport.geometry.chords_from reads
    Panjabi's canal and the spinous length from: the band the middle half of the body cut at the
    canal's median wall, or every section where that band holds no canal it can read."""
    secs = G.sections(v.loc, v.fz, v.pixel, as_hole=True)
    first = G.canal_chords(secs, v.pixel, (-np.inf, np.inf), v.fx, v.fy)
    if not first:
        return None
    body = v.loc[G.connected_front(v.idx, v.loc, first["wall_anterior"], v.grid.shape)]
    band = (-np.inf, np.inf)
    if len(body) >= G.MIN_BODY_VOXELS:
        z0, z1 = float(body[:, 2].min()), float(body[:, 2].max())
        band = (z0 + 0.25 * (z1 - z0), z1 - 0.25 * (z1 - z0))
    canal = G.canal_chords(secs, v.pixel, band, v.fx, v.fy)
    if not canal:
        return secs, (-np.inf, np.inf), first
    return secs, band, canal


def panjabi_canal(v: A.Vertebra) -> List[Line]:
    """Panjabi's canal width and depth (canal_w, canal_ap) as scanimport.geometry.chords_from
    takes them: each the median, over the sections of the band canal_reading gives, of one
    section's reading (canal_walls). Each is drawn in the section whose reading is nearest the
    median, the width through the hole's middle and the depth down its midline, so neither
    drawn length need equal the median."""
    got = canal_reading(v)
    if got is None:
        return []
    secs, band, canal = got
    rows = [(s, G.canal_walls(s, v.pixel, v.fx, v.fy)) for s in secs
            if s.canal is not None and band[0] <= s.w <= band[1]]
    rows = [(s, r) for s, r in rows if r is not None]
    out = []
    s, _ = min(rows, key=lambda sr: abs(sr[1][0] - canal["canal_w"]))
    walls = section_walls(s, v.pixel, v.fx)
    if walls is not None:
        x0, x1, ym = walls
        out.append(Line("canal_w", v.level, canal["canal_w"], *world(v, (x0, ym, s.w), (x1, ym, s.w)), "median",
                        "axial_canal"))
    _, (_, _, wa, wp, xm, z) = min(rows, key=lambda sr: abs(sr[1][1] - canal["canal_ap"]))
    out.append(Line("canal_ap", v.level, canal["canal_ap"], *world(v, (xm, wp, z), (xm, wa, z)), "median", "sagittal"))
    return out
''')

# spinous reads the same canal
swap('''    if v.touching.any():
        return []
    secs = G.sections(v.loc, v.fz, v.pixel, as_hole=True)
    first = G.canal_chords(secs, v.pixel, (-np.inf, np.inf), v.fx, v.fy)
    if not first:
        return []
    body = v.loc[G.connected_front(v.idx, v.loc, first["wall_anterior"], v.grid.shape)]
    band = (-np.inf, np.inf)
    if len(body) >= G.MIN_BODY_VOXELS:
        z0, z1 = float(body[:, 2].min()), float(body[:, 2].max())
        band = (z0 + 0.25 * (z1 - z0), z1 - 0.25 * (z1 - z0))
    canal = G.canal_chords(secs, v.pixel, band, v.fx, v.fy) or first
    back = ''', '''    if v.touching.any():
        return []
    got = canal_reading(v)
    if got is None:
        return []
    canal = got[2]
    back = ''')

# side_reading reads again where the edge blanked the measure's values
swap('''    """One side's values and the reading they came from: pedicle.one_side read again, or, where
    the measure's own reading and values are given, those, since one_side is the measure itself
    and reading it again took two thirds of a study's drawing time on the phantom (8 of 11 s)."""
    if ped is None or vals is None:
''', '''    """One side's values and the reading they came from: pedicle.one_side read again, or, where
    the measure's own reading and values are given, those, since one_side is the measure itself
    and reading it again took two thirds of a study's drawing time on the phantom (8 of 11 s).
    On a vertebra the volume's edge touches the measure blanks its pedicles' values after
    reading them (measure.cut_by_the_edge, pedicle.measures), so the side is read again there
    and its lines carry the construction's values, every one of them not measured."""
    if ped is None or vals is None or v.touching.any():
''')

# the builders by name, so each is guarded on its own
swap('''def vertebra_lines(v: A.Vertebra, ped: Dict[str, dict], vals: Optional[Dict[str, float]] = None) -> List[Line]:
    """Every line of the vertebra; with the values morphometry.measure.vertebra_values gave, the
    pedicles' lines are drawn on the reading those values came from (side_reading)."""
    out: List[Line] = []
    for build in (heights, wedge, waist, panjabi_plates, least_depth, lateral_film, spinous, tp_span):
        out += build(v)
    out += pedicles(v, ped, vals)
    out += interpedicular(v, ped)
    return out
''', '''def vertebra_builders(v: A.Vertebra, ped: Dict[str, dict],
                      vals: Optional[Dict[str, float]] = None) -> List[Tuple[str, Callable[[], List[Line]]]]:
    """Each builder of the vertebra's lines by its name, as a call that draws its lines, so a
    caller can keep the lines of the others where one fails; with the values
    morphometry.measure.vertebra_values gave, the pedicles' lines are drawn on the reading those
    values came from (side_reading)."""
    out = [(f.__name__, (lambda f=f: f(v))) for f in (heights, wedge, waist, panjabi_plates, panjabi_height,
                                                      least_depth, panjabi_canal, lateral_film, spinous, tp_span)]
    out += [("pedicles", lambda: pedicles(v, ped, vals)), ("interpedicular", lambda: interpedicular(v, ped))]
    return out


def vertebra_lines(v: A.Vertebra, ped: Dict[str, dict], vals: Optional[Dict[str, float]] = None) -> List[Line]:
    """Every line of the vertebra, builder by builder (vertebra_builders)."""
    out: List[Line] = []
    for _, draw in vertebra_builders(v, ped, vals):
        out += draw()
    return out
''')

# the module's account of where the ends are taken
swap('''withholds what differs. The ends are taken where the measure takes them: a height between its two
plates' band surfaces (body.heights), a width between the surfaces scanimport.geometry.surface
reads beyond the outermost voxel centres, a depth from the canal's wall line (anatomy.square_to_wall)
to the body's front, a chord where the march along the pedicle's axis enters and leaves the bone.
"""''', '''withholds what differs. The ends are taken where the measure takes them: a height between its two
plates' band surfaces (body.heights), a width between the surfaces scanimport.geometry.surface
reads beyond the outermost voxel centres, a depth from the canal's wall line (anatomy.square_to_wall)
to the body's front, a chord where the march along the pedicle's axis enters and leaves the bone.
A measure that is a median over rows, cells or sections (rule "median") is drawn in the one
nearest the median, with the median as its value, so its drawn length need not equal it.
"""''')
open(path, "w").write(src)
print("ok")
