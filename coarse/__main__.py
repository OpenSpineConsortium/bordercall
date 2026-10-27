"""python -m coarse --outdir DIR [--columns N]"""
from __future__ import annotations

import argparse
import sys

from . import study as S


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="python -m coarse")
    p.add_argument("--outdir", required=True)
    p.add_argument("--columns", type=int, default=S.S.N_COLUMNS)
    a = p.parse_args(argv)
    record = S.run(a.columns)
    record["command"] = ["python", "-m", "coarse"] + list(sys.argv[1:] if argv is None else argv)
    S.write(a.outdir, record)
    print(S.table(record))


if __name__ == "__main__":
    main()
