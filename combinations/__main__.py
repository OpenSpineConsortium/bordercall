"""python -m combinations study|pymc-check --outdir DIR"""
from __future__ import annotations

import argparse
import sys

from . import study as S


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="python -m combinations")
    p.add_argument("command", choices=("study", "pymc-check"))
    p.add_argument("--outdir", required=True)
    p.add_argument("--columns", type=int, default=S.N_COLUMNS)
    a = p.parse_args(argv)
    if a.command == "study":
        record = S.run(a.columns)
        record["command"] = ["python", "-m", "combinations"] + list(sys.argv[1:] if argv is None else argv)
        S.write(a.outdir, record)
        print(S.table(record))
    else:
        from . import pymc_check as Q
        record = Q.check()
        Q.write(a.outdir, record)
        for f in record["fields"]:
            print(f)


if __name__ == "__main__":
    main()
