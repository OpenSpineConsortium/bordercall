"""python -m morphoview render (the package's docstring says what it draws)."""
from __future__ import annotations

import argparse
import csv
import glob
import os
import sys
from typing import Dict, List, Optional

from maskedge import edge as E
from morphometry import column as COL
from morphometry import measure as M
from scanimport import LEVELS
from scanimport import volume as V

from . import lines as LN
from . import render as R

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
    a = p.parse_args(argv)
    {"render": cmd_render}[a.cmd](a)


if __name__ == "__main__":
    main(sys.argv[1:])
