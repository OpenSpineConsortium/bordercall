"""Cut the snapshot of the reread's series again, or say whether it still matches.

    python3 -I snapshot.py --check                         # the snapshot against data/SOURCE.json
    python3 -I snapshot.py --check path/to/series.csv      # and its rows against a copy of series.csv
    python3 -I snapshot.py --write 401aaee                 # cut it from the reread's branch at a commit

The snapshot holds the rows of the pool's 32 measures, as series.csv spells them, each with its
cohort's species and count of people (synthval/literature.py, write_snapshot). Cutting it needs a
clone that holds the reread's branch; checking it needs nothing but this folder.
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [REPO, HERE]

from schwingcheck import measures as MS  # noqa: E402
from synthval import literature as L  # noqa: E402


def pool_keys():
    return sorted({L.measure_key(m.key) for m in MS.pool()})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", nargs="?", const="", metavar="SERIES_CSV")
    ap.add_argument("--write", metavar="REF")
    args = ap.parse_args(argv)
    if args.write:
        info = L.write_snapshot(REPO, args.write, pool_keys())
        print("cut %d of %d rows at %s" % (info["rows_kept"], info["rows_in_source"], info["commit"][:7]))
    if args.check is not None:
        problems = L.check_snapshot(args.check or None)
        for p in problems:
            print(p)
        if args.check and not os.path.exists(args.check):
            print("no file %s; only the digest was checked" % args.check)
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
