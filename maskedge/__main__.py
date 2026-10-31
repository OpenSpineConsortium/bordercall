"""python -m maskedge measure | summary | disc | disc-summary (the package's docstring and disc.py's
say what each does)."""
from __future__ import annotations

import argparse
import csv
import math
import sys
from typing import List

from . import disc as D
from . import edge as E

DISC_COLUMNS = ["study", "disc", "region", "lines", "masks_lines", "read", "masks_gap", "ct_height", "difference",
                "difference_q25", "difference_q75", "contrast"]
COLUMNS = ["study", "level", "region", "points", "edges", "offset_median", "offset_q25", "offset_q75",
           "contrast_median", "note"]


def write_rows(rows, path: str, columns=COLUMNS) -> None:
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: round(r[k], 3) if isinstance(r.get(k), float) else r.get(k, "") for k in columns})


def read_rows(paths: List[str]):
    rows = []
    for p in paths:
        with open(p, newline="") as fh:
            rows += list(csv.DictReader(fh))
    return rows


def cmd_measure(a) -> None:
    rows = E.measure_study(a.ct, a.labels, a.scheme, a.study)
    write_rows(rows, a.out)
    print("%d rows to %s" % (len(rows), a.out))


def mm(x: float) -> str:
    return "%+.2f" % x if math.isfinite(x) else "-"


def cmd_summary(a) -> None:
    got = E.summary(read_rows(a.rows))
    print("| region | vertebrae | median offset (mm) | quartiles |")
    print("| --- | ---: | ---: | --- |")
    for name in E.REGIONS:
        if name in got:
            g = got[name]
            print("| %s | %d | %s | %s to %s |" % (name, g["vertebrae"], mm(g["median"]), mm(g["q25"]), mm(g["q75"])))
    imp = got["implied"]
    print("\nWhat the offsets make of a measure (mm; negative offset is a mask beyond the bone): height %s, disc %s, "
          "width %s, depth %s" % (mm(imp["height"]), mm(imp["disc"]), mm(imp["width"]), mm(imp["depth"])))


def cmd_disc(a) -> None:
    rows = D.measure_study(a.ct, a.labels, a.scheme, a.study)
    write_rows(rows, a.out, DISC_COLUMNS)
    print("%d rows to %s" % (len(rows), a.out))


def cmd_disc_summary(a) -> None:
    got = D.summary(read_rows(a.rows))
    print("| region | discs | masks' gap (mm) | CT's disc (mm) | difference (mm) | quartiles |")
    print("| --- | ---: | ---: | ---: | ---: | --- |")
    for region, g in got.items():
        print("| %s | %d | %.2f | %.2f | %s | %s to %s |" % (region, g["discs"], g["masks_gap"], g["ct_height"],
                                                           mm(g["difference"]), mm(g["q25"]), mm(g["q75"])))


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="python -m maskedge")
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure", help="offsets of one study's mask from its CT's bone edges")
    m.add_argument("--ct", required=True)
    m.add_argument("--labels", required=True)
    m.add_argument("--scheme", required=True)
    m.add_argument("--study", required=True)
    m.add_argument("--out", required=True)
    s = sub.add_parser("summary", help="the offsets by region over rows files")
    s.add_argument("--rows", nargs="+", required=True)
    d = sub.add_parser("disc", help="each disc's height in the CT against the gap the masks leave")
    for name in ("--ct", "--labels", "--scheme", "--study", "--out"):
        d.add_argument(name, required=True)
    ds = sub.add_parser("disc-summary", help="the disc readings by region over rows files")
    ds.add_argument("--rows", nargs="+", required=True)
    a = p.parse_args(argv)
    {"measure": cmd_measure, "summary": cmd_summary, "disc": cmd_disc, "disc-summary": cmd_disc_summary}[a.cmd](a)


if __name__ == "__main__":
    main(sys.argv[1:])
