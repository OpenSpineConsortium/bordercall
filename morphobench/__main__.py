"""python -m morphobench phantom | maskedge-phantom | maskedge-ct | disc-phantom | disc-ct | thicken |
canal-shape | figures (the package's docstring says what each does)."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List


def write(rows: List[dict], path: str) -> None:
    with open(path, "w", encoding="ascii", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: format(v, ".6g") if isinstance(v, float) else v for k, v in r.items()})
    print("%d rows to %s" % (len(rows), path))


def read(path: str) -> List[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def cmd_phantom(a) -> None:
    from . import bench as B
    write(B.phantom_truth(a.workers), a.out)


def cmd_maskedge_phantom(a) -> None:
    from . import bench as B
    write(B.maskedge_phantom(), a.out)


def cmd_maskedge_ct(a) -> None:
    """maskedge's rows from CTs, one file a study named by its stem, as aggregates by region."""
    import os
    from . import bench as B
    rows = []
    for path in a.rows:
        rows += B.maskedge_ct(read(path), os.path.basename(path).split(".")[0])
    write(rows, a.out)


def cmd_disc_phantom(a) -> None:
    from . import bench as B
    write(B.disc_phantom(), a.out)


def cmd_disc_ct(a) -> None:
    """maskedge disc rows from CTs, one file a study named by its stem, as aggregates by region."""
    import os
    from . import bench as B
    rows = []
    for path in a.rows:
        rows += B.disc_ct(read(path), os.path.basename(path).split(".")[0])
    write(rows, a.out)


def cmd_thicken(a) -> None:
    """morphometry thicken's rows, one file a study, as aggregates by measure and thickness."""
    from . import figures as F
    rows = []
    for path in a.rows:
        rows += read(path)
    write(F.thicken_summary(rows), a.out)


def cmd_canal_shape(a) -> None:
    """The canal's width where the measures read it against its widest in its front half, one
    labels file a study named by its stem."""
    import os
    from scanimport import volume as V
    from . import bench as B
    rows = []
    for path in a.labels:
        labels, grid, names, _, _ = V.read_labels(path, a.scheme)
        rows += B.canal_shape(labels, grid, names, os.path.basename(path).split(".")[0])
    write(rows, a.out)


def cmd_figures(a) -> None:
    from . import figures as F
    F.all_figures(a.records, a.out)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="python -m morphobench")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("phantom", help="every phantom measure against its truth over grids and tilts")
    s.add_argument("--out", required=True)
    s.add_argument("--workers", type=int, default=1)
    s = sub.add_parser("maskedge-phantom", help="the mask-edge reading of the exact, grown and shrunk phantom masks")
    s.add_argument("--out", required=True)
    s = sub.add_parser("maskedge-ct", help="maskedge rows from CTs as aggregates by region")
    s.add_argument("--rows", nargs="+", required=True)
    s.add_argument("--out", required=True)
    s = sub.add_parser("disc-phantom", help="the disc reading of the exact, grown and shrunk phantom masks")
    s.add_argument("--out", required=True)
    s = sub.add_parser("disc-ct", help="maskedge disc rows from CTs as aggregates by region")
    s.add_argument("--rows", nargs="+", required=True)
    s.add_argument("--out", required=True)
    s = sub.add_parser("thicken", help="morphometry thicken rows as aggregates by measure and thickness")
    s.add_argument("--rows", nargs="+", required=True)
    s.add_argument("--out", required=True)
    s = sub.add_parser("canal-shape", help="the canal's width where it is read against its widest in front")
    s.add_argument("--labels", nargs="+", required=True)
    s.add_argument("--scheme", default="enhance")
    s.add_argument("--out", required=True)
    s = sub.add_parser("figures", help="the benchmark figures from the records")
    s.add_argument("--records", required=True)
    s.add_argument("--out", required=True)
    a = p.parse_args(argv)
    {"phantom": cmd_phantom, "maskedge-phantom": cmd_maskedge_phantom, "maskedge-ct": cmd_maskedge_ct,
     "disc-phantom": cmd_disc_phantom, "disc-ct": cmd_disc_ct, "thicken": cmd_thicken,
     "canal-shape": cmd_canal_shape, "figures": cmd_figures}[a.cmd](a)


if __name__ == "__main__":
    main(sys.argv[1:])
