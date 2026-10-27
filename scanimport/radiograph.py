"""A radiograph's corner annotation to a column: the chords four corners give, in millimetres.

    python -m scanimport ingest-xr --xr lateral.json --xr ap.json --study f0001 --source aasce \
        --out imports/aasce

The annotation is SchwingNet's X-ray format, "schwingnet-spine-xr/1" (SchwingNet
docs/research/xr-annotation-format.md): one JSON per image, four corners per body in the order
superior-left, superior-right, inferior-right, inferior-left as the image is shown head up,
each with its visibility, and the body's level as one of the 27 names. Four corners give, by
view:

- AP: the superior and inferior end-plate lines, EPWu and EPWl (corner 1 to 2, corner 4 to 3).
- lateral: the same lines as depths, EPDu and EPDl, and the posterior height VBHp, from the
  superior to the inferior corner of the posterior side, which needs to know which side of the
  image is anterior: the image's `anterior` field ("left" or "right"), or --anterior. With
  neither, VBHp is not taken and the flag says so; the depths need no side.

The canal is not in four corners. A body may carry, beside its corners, an optional `chords`
object naming a measure and two points, {"canal_w": [[x1, y1], [x2, y2]]} for the
interpedicular distance on an AP or {"canal_ap": [...]} for the depth of the canal on a lateral
(the posterior body wall to the spinolaminar line); this is the one addition to version 1 the
importer reads, and an annotation without it loses nothing.

A corner that is null or marked not visible gives no chord, never a guessed one. C1, C2 and the
sacrum are named and kept, never measured, as on a CT: the rule's column runs from C3 to L5. A
body named "?" keeps its place in its view, top down by the mean height of its corners on the
image as shown head up, with its chords and no name. A level named twice on one view is a
mistake the importer cannot settle, so both bodies are kept as "?" and the study says why.

MILLIMETRES, AND THE MAGNIFICATION. A film's pixel is a length at the detector, `pixel_mm`; the
body sits nearer the source, so its shadow is magnified by m = source-to-image distance over
source-to-object distance, 1.1 to 1.3 for a spine film and more on a C-arm. A chord in
millimetres is pixels times pixel_mm over m. m is rarely recorded, so it enters the rule as what
it is, a scale on every chord at once, which the rule already integrates over as the patient's
size (archive/bordercall/exact.py): the chords are divided by a nominal m0 and the study carries
the spread of log m, which bridge.py adds to the size spread. The defaults, m0 = 1.15 and a
spread of 0.08 in log m (m from 0.98 to 1.35 within two spreads), are a choice stated here and
recorded in every study, to be replaced by the image's own geometry where its header has it
(`--magnification`, `--magnification-sd`). An image with no pixel_mm has no millimetres at all:
its chords stay in pixels, the study says its scale is unknown, and the rule names it from the
chords' proportions alone (bridge.py, a flat prior on the scale).

Two views of one study (an AP and a lateral of the same patient on one day) are merged by level
into one column, each measure from the view that shows it. Views that disagree on whether they
have a pixel size cannot share one scale and are refused, and so are two views that both lack
one, since each image's pixel is a unit of its own.

Who drew the corners is the caller's statement (`--annotation`), never inferred; a reader id the
format marks as a model's ("model:<run id>") beside a statement of human is refused.
"""
from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import LEVELS, MEASURES, NOT_MEASURED, PLANES, SEVEN
from .column import Body, Column, facts_from_levels

FORMAT = "schwingnet-spine-xr/1"
NAMES = set(LEVELS) | {"?"}
VIEWS = ("ap", "pa", "lateral")
M0, M_LOG_SD = 1.15, 0.08
FROM_CORNERS = ("endplate", "endplate_lower", "endplate_depth", "endplate_lower_depth", "h_post")


def read(path: str) -> dict:
    with open(path) as fh:
        d = json.load(fh)
    if d.get("format") != FORMAT:
        raise SystemExit("%s is not a %s annotation (format %r)" % (path, FORMAT, d.get("format")))
    return d


def view_of(image: dict) -> str:
    """ap or lateral; a PA film shows what an AP does."""
    v = str(image.get("view", "")).lower()
    if v not in VIEWS:
        raise SystemExit("the image's view is %r; the importer reads ap, pa or lateral" % v)
    return "ap" if v == "pa" else v


def corner(body: dict, i: int) -> Optional[np.ndarray]:
    """Corner i of a body when it is given and visible, else None."""
    cs = body.get("corners") or []
    vis = body.get("visible") or [True] * 4
    if i >= len(cs) or cs[i] is None or (i < len(vis) and vis[i] is False):
        return None
    return np.asarray(cs[i], float)


def span(a: Optional[np.ndarray], b: Optional[np.ndarray]) -> float:
    return float(np.linalg.norm(b - a)) if a is not None and b is not None else math.nan


def corner_chords(body: dict, view: str, anterior: Optional[str]) -> Tuple[Dict[str, float], Dict[str, str]]:
    """The chords one body's corners and its optional `chords` give on a view, in pixels, and
    why any was not taken."""
    sl, sr, ir, il = (corner(body, i) for i in range(4))
    vals: Dict[str, float] = {}
    flags: Dict[str, str] = {}
    if view == "ap":
        vals["endplate"], vals["endplate_lower"] = span(sl, sr), span(il, ir)
    else:
        vals["endplate_depth"], vals["endplate_lower_depth"] = span(sl, sr), span(il, ir)
        if anterior == "left":
            vals["h_post"] = span(sr, ir)
        elif anterior == "right":
            vals["h_post"] = span(sl, il)
        else:
            vals["h_post"] = math.nan
            flags["h_post"] = "which side is anterior is not recorded (the image's anterior field, or --anterior)"
    for name, pts in (body.get("chords") or {}).items():
        if name not in MEASURES or name in FROM_CORNERS or view not in PLANES[name]:
            flags[name] = "a %s chord on a %s view is not read (corners give the body's chords)" % (name, view)
            continue
        if pts is None or len(pts) != 2 or any(p is None for p in pts):
            continue
        vals[name] = span(np.asarray(pts[0], float), np.asarray(pts[1], float))
    for k, v in vals.items():
        if not np.isfinite(v):
            flags.setdefault(k, "a corner is missing or hidden")
    return vals, flags


def annotation_of(reader: dict) -> str:
    """machine for a reader id the format marks as a model's ("model:<run id>"), else unknown:
    whether a person drew the corners is the caller's statement, never read from the file."""
    return "machine" if str(reader.get("id", "")).startswith("model:") else "unknown"


def mean_height(body: dict) -> float:
    """The mean image row of a body's given corners, for its order on the view; NaN with none."""
    ys = [c[1] for c in (corner(body, i) for i in range(4)) if c is not None]
    return float(np.mean(ys)) if ys else math.nan


def view_bodies(doc: dict, view: str) -> Tuple[List[Tuple[str, dict]], List[str]]:
    """One view's bodies top down, each with the level it may be keyed by: its name, or "?" for
    an unnamed body, a body with a name outside the 27 and both bodies of a level named twice."""
    bodies = list(doc.get("bodies", []))
    problems = []
    names = []
    for i, b in enumerate(bodies):
        level = str(b.get("level", "?"))
        if level not in NAMES:
            problems.append("body %d of the %s view is named %r, not one of the 27 names; read as ?" % (i, view, level))
            level = "?"
        names.append(level)
    for lv in sorted({n for n in names if n != "?" and names.count(n) > 1}):
        problems.append("%s is named %d times on the %s view; those bodies are read as ?" % (lv, names.count(lv), view))
        names = ["?" if n == lv else n for n in names]
    order = sorted(range(len(bodies)), key=lambda i: (math.isnan(mean_height(bodies[i])), mean_height(bodies[i]), i))
    return [(names[i], bodies[i]) for i in order], problems


def ingest(paths: Sequence[str], study_id: str, source: str, annotation: str, subject_id: Optional[str] = None,
           anterior: Optional[str] = None, magnification: Optional[float] = None,
           magnification_sd: Optional[float] = None) -> Column:
    if annotation not in ("human", "machine"):
        raise SystemExit("--annotation must say who drew the corners: human or machine")
    docs = [read(p) for p in paths]
    views = [view_of(d["image"]) for d in docs]
    if len(set(views)) != len(views):
        raise SystemExit("two annotations of the same view (%s); one per view per study" % ", ".join(views))
    scaled = [d["image"].get("pixel_mm") is not None for d in docs]
    if len(set(scaled)) > 1:
        raise SystemExit("one view has a pixel size and another has none; they cannot share one scale")
    if len(docs) > 1 and not any(scaled):
        raise SystemExit("no view has a pixel size, and each image's pixel is a unit of its own; "
                         "give pixel_mm or ingest each view as a study of its own")
    readers = [d.get("reader", {}) for d in docs]
    if annotation == "human" and any(annotation_of(r) == "machine" for r in readers):
        raise SystemExit("--annotation human, but a reader id says a model drew the corners (%s)"
                         % ", ".join(str(r.get("id")) for r in readers))
    known = scaled[0]
    m0 = float(magnification) if magnification else M0
    msd = float(magnification_sd) if magnification_sd is not None else (M_LOG_SD if not magnification else 0.02)
    order: List[str] = []
    bodies: Dict[str, Body] = {}
    problems: List[str] = []
    for d, view in zip(docs, views):
        side = anterior or d["image"].get("anterior")
        mm = float(d["image"]["pixel_mm"]) / m0 if known else 1.0
        listed, found = view_bodies(d, view)
        problems += found
        for i, (level, b) in enumerate(listed):
            key = level if level != "?" else "?%s%d" % (view, i)
            if key not in bodies:
                bodies[key] = Body(level=level)
                order.append(key)
            if level in NOT_MEASURED:
                bodies[key].flags["all"] = "named, not measured: %s" % (
                    "the sacrum carries no row" if level == "sacrum" else "the rule's column starts at C3")
                continue
            vals, flags = corner_chords(b, view, side)
            for m, v in vals.items():
                bodies[key].values[m] = v * mm if np.isfinite(v) else math.nan
                bodies[key].methods[m] = "%s view, %s" % (view, "corners" if m in FROM_CORNERS else "chord points")
            bodies[key].flags.update(flags)
    named = sorted((k for k in order if not k.startswith("?")), key=LEVELS.index)
    keys = named + [k for k in order if k.startswith("?")] if named else order
    col_bodies = [bodies[k] for k in keys]
    levels = [b.level for b in col_bodies]
    calls = [d.get("column", {}) for d in docs if d.get("column")]
    expresses = {"L6": True, "T13": True, "ribs": any(c.get("ribs") for c in calls)}
    study = {"study_id": study_id, "subject_id": subject_id or study_id, "source": source,
             "modality": str(docs[0]["image"].get("modality", "film")), "views": views, "annotation": annotation,
             "made_by": ",".join(sorted({str(r.get("id", "")) for r in readers})), "scheme": FORMAT,
             "expresses": expresses, "pixel_mm": [d["image"].get("pixel_mm") for d in docs],
             "magnification": m0 if known else None, "scale_known": bool(known),
             "scale_log_mean": 0.0, "scale_log_sd": msd if known else None,
             "reader_call": [c.get("call") for c in calls], "problems": problems,
             "plane_of": {m: "/".join(PLANES[m]) for m in MEASURES},
             "measured": sorted(m for m in SEVEN if any(np.isfinite(b.values.get(m, math.nan)) for b in col_bodies))}
    study.update(facts_from_levels(levels, expresses))
    return Column(study=study, bodies=col_bodies)


def ingest_one(path: str, **kw) -> Column:
    return ingest([path], **kw)
