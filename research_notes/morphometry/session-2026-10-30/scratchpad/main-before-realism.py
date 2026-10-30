"""python -m morphoview render (the package's docstring says what it draws), and python -m
morphoview project, which carries the lines export onto a FleXray render (cmd_project says how)."""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import math
import os
import sys
from typing import Dict, List, Optional, Tuple

import numpy as np

from maskedge import edge as E
from morphometry import column as COL
from morphometry import measure as M
from scanimport import LEVELS
from scanimport import volume as V

from . import lines as LN
from . import projection as PJ
from . import render as R
from . import shapes as SH

COLUMNS = ["study", "level", "key", "rule", "panel", "value", "measured", "drawn", "status",
           "ax", "ay", "az", "bx", "by", "bz"]


def rows_measured(path: Optional[str], study: str) -> Optional[Dict[str, Dict[str, float]]]:
    """The run's rows for the study, level by level, where a rows file is given."""
    if not path:
        return None
    out: Dict[str, Dict[str, float]] = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["study"] != study or r["key"].startswith("flag:"):
                continue
            try:
                out.setdefault(r["level"], {})[r["key"]] = float(r["value"])
            except ValueError:
                continue
    return out


def neighbours(level: str, have: List[str], present) -> List[tuple]:
    """The discs above and below the level that the volume holds both bodies of."""
    order = [lv for lv in LEVELS if lv in have]
    i = order.index(level)
    out = []
    if i > 0 and M.adjacent(order[i - 1], level, present):
        out.append((order[i - 1], level))
    if i + 1 < len(order) and M.adjacent(level, order[i + 1], present):
        out.append((level, order[i + 1]))
    return out


def lines_for(vs, level: str, present, measured: Optional[Dict[str, Dict[str, float]]]) -> List[LN.Line]:
    v = vs[level]
    vals, _, ped = M.vertebra_values(v)
    places = LN.ROWS_PLACES if measured is not None else None
    got = LN.checked(LN.vertebra_lines(v, ped), measured.get(level, {}) if measured is not None else vals, places)
    for up, low in neighbours(level, list(vs), present):
        U, L = vs[up], vs[low]
        if U.touching[U.body].any() or L.touching[L.body].any():
            continue
        name = "%s-%s" % (up, low)
        ref = measured.get(name, {}) if measured is not None else COL.disc_heights(U, L)
        got += LN.checked(LN.discs(U, L), ref, places)
    return got


def csv_rows(study: str, lines: List[LN.Line]) -> List[dict]:
    rows = []
    for ln in lines:
        rows.append({"study": study, "level": ln.level, "key": ln.key, "rule": ln.rule, "panel": R.panel_of(ln),
                     "value": float(ln.value), "measured": float(ln.measured), "drawn": ln.drawn, "status": ln.status,
                     "ax": float(ln.a[0]), "ay": float(ln.a[1]), "az": float(ln.a[2]),
                     "bx": float(ln.b[0]), "by": float(ln.b[1]), "bz": float(ln.b[2])})
    return rows


def caption(study: str, level: str, lines: List[LN.Line]) -> str:
    drawn = sum(ln.status == "drawn" for ln in lines)
    held = sum(ln.status.startswith("withheld") for ln in lines)
    return ("Study %s, %s: %d measures drawn where morphometry takes them, each rebuilt and matched to its row; "
            "%d withheld. Calipers mark lengths, dashed lines the end-plates rim to rim, dotted lines Eisenstein's "
            "apex-to-apex line; (p) marks a projected line. Grey: the vertebra measured." % (study, level, drawn, held))


def cmd_render(a) -> None:
    from schwingcheck import figures as FIG
    os.makedirs(a.out, exist_ok=True)
    vol, grid, names, _, _ = V.read_labels(a.labels, a.scheme)
    vs = E.vertebrae(vol, grid, names)
    present = set(names.values())
    measured = rows_measured(a.rows, a.study)
    for level in a.levels:
        if level not in vs:
            print("%s: not held whole by the volume, or not usable" % level)
            continue
        got = lines_for(vs, level, present, measured)
        name = "render-%s-%s" % (a.study, level)
        fig = R.figure(vs[level], vol, R.mine_of(names, level), got, a.study)
        cap = caption(a.study, level, got)
        assert FIG.words(cap) <= FIG.CAPTION_WORDS, FIG.words(cap)
        FIG.save(fig, a.out, name, cap)
        FIG.write_csv(a.out, name, csv_rows(a.study, got))
        held = [ln for ln in got if ln.status.startswith("withheld")]
        print("%s: %d lines, %d drawn, %d withheld%s" % (name, len(got), sum(ln.status == "drawn" for ln in got),
                                                        len(held), "".join("\n  %s %s" % (h.key, h.status) for h in held)))
    write_index(a)


def code_files() -> List[str]:
    here = os.path.dirname(os.path.abspath(__file__))
    return sorted(glob.glob(os.path.join(here, "*.py")))


def write_index(a) -> None:
    """FIGURES.md beside the figures: the mask and the rows they were drawn from and the code that
    drew them, each by sha256."""
    from schwingcheck import figures as FIG
    path = os.path.join(a.out, "FIGURES.md")
    lines = ["# Renders of the measures on their slices", "",
             "Drawn by `python -m morphoview render`; every line rebuilt from the measuring code and matched to "
             "its row (morphoview/__init__.py).", "", "## Records", ""]
    lines.append("- study %s: %s, sha256 %s" % (a.study, os.path.basename(a.labels), FIG.sha256(a.labels)))
    if a.rows:
        lines.append("- rows: %s, sha256 %s" % (os.path.basename(a.rows), FIG.sha256(a.rows)))
    lines += ["", "## Code", ""]
    lines += ["- morphoview/%s %s" % (os.path.basename(p), FIG.sha256(p)) for p in code_files()]
    lines += ["", "## Figures", ""]
    lines += ["- %s" % os.path.basename(p) for p in sorted(glob.glob(os.path.join(a.out, "render-*.png")))]
    with open(path, "w", encoding="ascii", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


# ---- python -m morphoview project ---------------------------------------------------------------

# a projected line: its place on the render at each end (u along a row, v down the image, in the
# render's pixels), its depth along the beam, whether the render's beam sampled it and whether it
# lies in what the render was made of, the CT's slices the view rendered (empty where the CT's
# grid is not given), the line's length on the render, each end's magnification and the ends on
# FleXray's canvas
PROJECTED = ["study", "level", "key", "part", "status", "a_end", "au", "av", "a_depth", "a_in_beam", "a_in_volume",
             "b_end", "bu", "bv", "b_depth", "b_in_beam", "b_in_volume", "length_px", "a_magnification",
             "b_magnification", "a_canvas_u", "a_canvas_v", "b_canvas_u", "b_canvas_v"]
# with --labels: how far each end and the midpoint lie from the shadow of the line's level on the render,
# in pixels, none where they fall on it
LANDING = ["a_off_px", "b_off_px", "mid_off_px"]
# a projected frame: its origin and the tips of its three axes drawn AXIS_MM long
FRAMES_PROJECTED = ["study", "level", "axis", "ou", "ov", "o_depth", "o_in_beam", "o_in_volume", "xu", "xv", "yu",
                    "yv", "zu", "zv"]
COLUMN_PROJECTED = ["study", "point", "u", "v", "depth", "in_beam", "in_volume"]
AXIS_MM = 10.0
VIEW_FIELDS = ("rot_deg", "xyz_mm", "isocentre_mm", "sdd", "delx", "height", "width", "dely", "x0", "y0",
               "orthographic", "orientation")
GRID_MM = 1e-3                  # how far two affines' entries may differ for one grid, in mm


def sha256_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def read_json(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def view_from(a) -> Tuple[PJ.View, Optional[PJ.Crop], dict, int]:
    """The view to project onto, the crop of the CT it rendered (none where the record names none:
    the whole CT), the record of where it was read, and the samples a ray the render took: a view
    file of View's fields and a crop, or a row of SchwingNet's render manifest named by its image
    file, its crop, and the detector and the ray samples its blocks record."""
    if a.view:
        doc = read_json(a.view)
        view = PJ.View(**{k: doc[k] for k in VIEW_FIELDS if k in doc})
        source = {"view": os.path.basename(a.view), "sha256": sha256_of(a.view)}
        return view, PJ.Crop.from_record(doc.get("crop")), source, int(doc.get("n_samples", a.samples))
    manifest = read_json(a.manifest)
    row = next((r for r in manifest.get("views", []) if r.get("file") == a.file), None)
    if row is None:
        raise SystemExit("%s holds no view of the file %s" % (a.manifest, a.file))
    blocks = manifest.get("blocks", {})
    view = PJ.View.from_manifest(row, int(blocks["detector"]))
    source = {"manifest": os.path.basename(a.manifest), "sha256": sha256_of(a.manifest), "file": a.file,
              "subject": row.get("subject"), "blocks": blocks}
    return view, PJ.Crop.from_record(row.get("crop")), source, int(blocks.get("ray_samples", a.samples))


def study_to_carry(a, studies: List[str], source: dict) -> Tuple[str, str]:
    """The one study whose lines go onto the render, and how it was chosen: --study, else the
    lines' only study, else the study the manifest's row names as its subject. A render shows one
    subject, and another's lines drawn on it would land on bone they were not measured on."""
    if not studies:
        raise SystemExit("%s holds no line" % a.lines)
    if a.study:
        if a.study not in studies:
            raise SystemExit("%s holds no line of the study %s" % (a.lines, a.study))
        return a.study, "--study"
    if len(studies) == 1:
        return studies[0], "the lines' only study"
    subject = source.get("subject")
    if subject in studies:
        return subject, "the manifest row's subject"
    raise SystemExit("%s holds the lines of %d studies; name the render's with --study%s"
                     % (a.lines, len(studies), " (the row's subject is %s)" % subject if subject else ""))


def read_mask(labels: str, scheme: str):
    """The mask the lines were measured on, as morphometry reads it: its labels, its grid and the
    level each value names."""
    vol, grid, names, _, _ = V.read_labels(labels, scheme)
    return vol, grid, names


def ct_grid(a, mask) -> Optional[Tuple[np.ndarray, Tuple[int, int, int], str]]:
    """The grid of the CT the render was made from, its affine and shape, and where it was read:
    the header of --ct, which the mask must share, or else the mask's own, since SchwingNet puts a
    rendered subject's masks on its CT's grid; none where neither is given."""
    if a.ct:
        import nibabel as nib
        img = nib.load(a.ct)
        affine, shape = np.asarray(img.affine, float), tuple(int(n) for n in img.shape[:3])
        if mask is not None:
            grid = mask[1]
            if tuple(grid.shape[:3]) != shape or not np.allclose(grid.affine, affine, rtol=0, atol=GRID_MM):
                raise SystemExit("%s is not on the grid of %s; the labels the lines were measured on must be"
                                 % (a.labels, a.ct))
        return affine, shape, "ct"
    if mask is not None:
        return np.asarray(mask[1].affine, float), tuple(int(n) for n in mask[1].shape[:3]), "labels"
    return None


def in_volume(grid, crop: Optional[PJ.Crop]):
    """Whether places lie in what the render was made of, in words: among the slices of the CT the
    view's crop names, the whole CT where it names none; no word where the CT's grid is not
    known."""
    if grid is None:
        return lambda points: [""] * len(points)
    affine, shape, _ = grid
    if crop is not None and crop.z_stop > shape[2]:
        raise SystemExit("the view's crop runs to slice %d, past the CT's %d" % (crop.z_stop, shape[2]))
    region = crop or PJ.Crop(0, shape[2])
    return lambda points: [str(bool(x)) for x in region.holds(points, affine, shape)]


def end_of(row: dict, end: str) -> Optional[np.ndarray]:
    try:
        p = np.array([float(row[end + axis]) for axis in "xyz"])
    except (KeyError, ValueError):
        return None
    return p if np.isfinite(p).all() else None


def whole(x) -> str:
    return repr(float(x))


def place(cam: PJ.Camera, p: Optional[np.ndarray], prefix: str, canvas: int, inside) -> dict:
    v = cam.view
    if p is None:
        return {prefix + k: "" for k in ("u", "v", "_depth", "_in_beam", "_in_volume", "_magnification", "_canvas_u",
                                         "_canvas_v")}
    got = cam.project(p[None])
    uv, depth = got.uv[0], float(got.depth[0])
    on = PJ.to_canvas(uv, v.height, v.width, canvas)[0]
    return {prefix + "u": whole(uv[0]), prefix + "v": whole(uv[1]), prefix + "_depth": whole(depth),
            prefix + "_in_beam": str(bool(got.in_beam[0])), prefix + "_in_volume": inside(p[None])[0],
            prefix + "_magnification": whole(cam.magnification(depth)),
            prefix + "_canvas_u": whole(on[0]), prefix + "_canvas_v": whole(on[1])}


def projected_line(row: dict, cam: PJ.Camera, canvas: int, inside) -> dict:
    a, b = end_of(row, "a"), end_of(row, "b")
    out = {k: row.get(k, "") for k in ("study", "level", "key", "part", "status", "a_end", "b_end")}
    out.update(place(cam, a, "a", canvas, inside))
    out.update(place(cam, b, "b", canvas, inside))
    length = ""
    if a is not None and b is not None:
        uv = cam.project(np.stack([a, b])).uv
        length = whole(np.linalg.norm(uv[1] - uv[0]))
    out["length_px"] = length
    return out


def shadows(mask, crop: Optional[PJ.Crop], cam: PJ.Camera, levels, n_samples: int) -> Dict[str, np.ndarray]:
    """Each named level's shadow on the render as FleXray samples its rays: every voxel of the
    level in the mask the lines were measured on, as the scheme reads it (a SPINEPS vertebra with
    its end-plates), among the slices of the view's crop. It is FleXray's support of the level
    where the render's labels are the same, and none where the crop holds nothing of it."""
    vol, grid, names = mask
    if crop is not None:
        vol = crop.cut(vol)
    out = {}
    for level in sorted(set(levels)):
        values = [v for v, n in names.items() if n == level]
        if not values:
            continue
        if not np.isin(vol, values).any():
            out[level] = np.zeros((cam.view.height, cam.view.width), bool)
            continue
        out[level] = SH.Volume.from_labels(vol, grid.affine, values, largest=False).silhouette(cam, n_samples=n_samples)
    return out


def distance_maps(shade: Dict[str, np.ndarray]):
    """For a line's level, how far each pixel of the render lies from the level's shadow, a disc's
    from its two vertebrae's together, in pixels between centres; None where a level has no shadow
    or an empty one. Each map is made once, since a level has many lines and a render of 1024
    pixels a map of a million."""
    from scipy import ndimage
    made: Dict[str, Optional[np.ndarray]] = {}

    def of(level: str) -> Optional[np.ndarray]:
        if level not in made:
            parts = [shade.get(lv) for lv in level.split("-")]
            shadow = np.logical_or.reduce(parts) if all(s is not None for s in parts) else None
            made[level] = ndimage.distance_transform_edt(~shadow) if shadow is not None and shadow.any() else None
        return made[level]
    return of


def distance_to(far: Optional[np.ndarray], uv: np.ndarray) -> str:
    """How far, in pixels, the pixel of a place on the render lies from the shadow whose distance
    map is `far`: the distance between pixel centres, none on the shadow, empty off the detector or
    where no shadow is."""
    if far is None or not np.isfinite(uv).all():
        return ""
    r, c = int(math.floor(uv[1])), int(math.floor(uv[0]))
    if not (0 <= r < far.shape[0] and 0 <= c < far.shape[1]):
        return ""
    return whole(far[r, c])


def landing(row: dict, cam: PJ.Camera, far) -> dict:
    """The line's ends and midpoint against its level's shadow, a disc's against its two
    vertebrae's together, far giving each level's distance map."""
    shadow = far(row["level"])
    a, b = end_of(row, "a"), end_of(row, "b")
    out = {}
    for name, p in (("a_off_px", a), ("b_off_px", b), ("mid_off_px", None if a is None or b is None else 0.5 * (a + b))):
        out[name] = "" if p is None else distance_to(shadow, cam.project(p[None]).uv[0])
    return out


def projected_frames(rows: List[dict], cam: PJ.Camera, inside) -> List[dict]:
    out = []
    for r in rows:
        try:
            o = np.array([float(r["o" + k]) for k in "xyz"])
            axes = [np.array([float(r["e%s%s" % (e, k)]) for k in "xyz"]) for e in "xyz"]
        except (KeyError, ValueError):
            continue
        got = cam.project(np.stack([o] + [o + AXIS_MM * e for e in axes]))
        row = {"study": r["study"], "level": r["level"], "axis": r.get("axis", ""),
               "ou": whole(got.uv[0, 0]), "ov": whole(got.uv[0, 1]), "o_depth": whole(got.depth[0]),
               "o_in_beam": str(bool(got.in_beam[0])), "o_in_volume": inside(o[None])[0]}
        for i, e in enumerate("xyz", start=1):
            row[e + "u"], row[e + "v"] = whole(got.uv[i, 0]), whole(got.uv[i, 1])
        out.append(row)
    return out


def projected_column(rows: List[dict], cam: PJ.Camera, inside) -> List[dict]:
    """The column's curve on the render: the centripetal spline through each study's vertebrae's
    origins in the order of the levels, sampled within shapes.TOLERANCE_MM."""
    out = []
    for study in sorted({r["study"] for r in rows}):
        mine = sorted((r for r in rows if r["study"] == study), key=lambda r: LEVELS.index(r["level"]))
        pts = np.array([[float(r["o" + k]) for k in "xyz"] for r in mine])
        if len(pts) < 2:
            continue
        curve = SH.spline(pts).project(cam)
        held = inside(curve.world)
        for k in range(len(curve.uv)):
            out.append({"study": study, "point": str(k), "u": whole(curve.uv[k, 0]), "v": whole(curve.uv[k, 1]),
                        "depth": whole(curve.depth[k]), "in_beam": str(bool(curve.in_beam[k])),
                        "in_volume": held[k]})
    return out


def write_table(path: str, fields: List[str], rows: List[dict]) -> None:
    with open(path + ".part", "w", newline="", encoding="ascii") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    os.replace(path + ".part", path)


def read_table(path: str, study: Optional[str]) -> List[dict]:
    with open(path, newline="") as fh:
        return [r for r in csv.DictReader(fh) if not study or r["study"] == study]


def cmd_project(a) -> None:
    """The lines export (lines.csv, and frames.csv where given) of one study carried onto one
    FleXray render: each line's ends at their pixels through FleXray's own camera
    (morphoview.projection), written as lines2d.csv, with whether each lies in what the render was
    made of, the slices of the CT its crop names; each frame's origin and axes as frames2d.csv, and
    the column's curve through the origins as column2d.csv; with the mask the lines were measured
    on, how far each end lies from its level's shadow on the render as FleXray samples it.
    VIEW.json records the view, its crop, the study, where each was read and the code that
    projected it."""
    view, crop, source, n_samples = view_from(a)
    cam = PJ.Camera(view)
    every = read_table(a.lines, None)
    study, chosen = study_to_carry(a, sorted({r["study"] for r in every}), source)
    rows = [r for r in every if r["study"] == study]
    mask = read_mask(a.labels, a.scheme) if a.labels else None
    grid = ct_grid(a, mask)
    inside = in_volume(grid, crop)
    shade = shadows(mask, crop, cam, (lv for r in rows for lv in r["level"].split("-")), n_samples) if mask else None
    far = distance_maps(shade) if shade is not None else None
    os.makedirs(a.out, exist_ok=True)
    out = []
    for r in rows:
        line = projected_line(r, cam, a.canvas, inside)
        if far is not None:
            line.update(landing(r, cam, far))
        out.append(line)
    write_table(os.path.join(a.out, "lines2d.csv"), PROJECTED + (LANDING if shade is not None else []), out)
    if a.frames:
        frames = read_table(a.frames, study)
        write_table(os.path.join(a.out, "frames2d.csv"), FRAMES_PROJECTED, projected_frames(frames, cam, inside))
        write_table(os.path.join(a.out, "column2d.csv"), COLUMN_PROJECTED, projected_column(frames, cam, inside))
    record = {"view": view.as_record(), "crop": crop.as_record() if crop else None, "from": source,
              "n_samples": n_samples, "canvas": a.canvas, "to_world": cam.to_world.tolist(),
              "intrinsics": cam.intrinsics.tolist(),
              "lines": {"file": os.path.basename(a.lines), "sha256": sha256_of(a.lines), "study": study,
                        "chosen_by": chosen},
              "labels": {"file": os.path.basename(a.labels), "sha256": sha256_of(a.labels), "scheme": a.scheme}
              if a.labels else None,
              "ct_grid": {"from": grid[2], "file": os.path.basename(a.ct) if grid[2] == "ct" else os.path.basename(a.labels),
                          "shape": list(grid[1]), "affine": grid[0].tolist()} if grid else None,
              "code": {"morphoview/%s" % os.path.basename(p): sha256_of(p) for p in code_files()}}
    with open(os.path.join(a.out, "VIEW.json"), "w", encoding="ascii", newline="\n") as fh:
        json.dump(record, fh, indent=1)
        fh.write("\n")
    print(summary(a.out, study, out, grid is not None, shade is not None))


def summary(out_dir: str, study: str, out: List[dict], placed: bool, shaded: bool) -> str:
    """One line of what was carried: a line is on the render where both its ends are in the beam
    and in what the render was made of, as far as the CT's grid tells."""
    drawn = [line for line in out if line["status"] == "drawn"]
    seen = sum(all(line[e + "_in_beam"] == "True" and line[e + "_in_volume"] != "False" for e in "ab")
               for line in drawn)
    said = "%s: %d lines of %s, %d drawn, %d of them with both ends on the render" % (out_dir, len(out), study,
                                                                                       len(drawn), seen)
    if not placed:
        said += " as far as the beam goes, the CT's grid not given"
    if shaded:
        on = sum(line["a_off_px"] == "0.0" and line["b_off_px"] == "0.0" for line in drawn)
        said += ", %d with both ends on their level's shadow" % on
    return said


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="python -m morphoview")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render", help="each measure drawn on its vertebra's slices")
    r.add_argument("--labels", required=True)
    r.add_argument("--scheme", default="enhance")
    r.add_argument("--study", required=True)
    r.add_argument("--levels", nargs="+", required=True)
    r.add_argument("--rows", default="", help="the run's rows.csv, whose values the lines must match")
    r.add_argument("--out", required=True)
    q = sub.add_parser("project", help="the lines export carried onto a FleXray render")
    q.add_argument("--lines", required=True, help="the run's lines.csv (python -m morphometry run --lines)")
    q.add_argument("--frames", default="", help="the run's frames.csv")
    q.add_argument("--study", default="", help="the study whose lines to carry; where not given, the lines' only "
                   "study, or the manifest row's subject")
    where = q.add_mutually_exclusive_group(required=True)
    where.add_argument("--view", default="", help="a JSON file of the view's fields (morphoview.projection.View)")
    where.add_argument("--manifest", default="", help="SchwingNet's render manifest.json, with --file")
    q.add_argument("--file", default="", help="the render's file as the manifest names it, images/<stem>_v<NN>.png")
    q.add_argument("--labels", default="", help="the mask the lines were measured on, to measure where each lands")
    q.add_argument("--ct", default="", help="the CT the render was made from, read for its grid alone, on which "
                   "the view's crop is placed; the labels' grid where not given")
    q.add_argument("--scheme", default="enhance")
    q.add_argument("--samples", type=int, default=500, help="the samples a ray FleXray took, where the view does not say")
    q.add_argument("--canvas", type=int, default=PJ.CANVAS, help="the side of FleXray's inference canvas")
    q.add_argument("--out", required=True)
    a = p.parse_args(argv)
    if a.cmd == "project" and a.manifest and not a.file:
        p.error("--manifest takes --file, the render's file as the manifest names it")
    {"render": cmd_render, "project": cmd_project}[a.cmd](a)


if __name__ == "__main__":
    main(sys.argv[1:])
