"""Run `python -m morphometry run` in-process with the worker that measures study KILL dying as an
out-of-memory kill would (os._exit), so the pool breaks as it does on the grid.

    python kill_one.py KILL run --masks ... --out ... --workers 1 [--lines]
"""
import os
import sys

from morphometry import __main__ as RUN
from morphometry import measure as M

KILL = sys.argv[1]
real = M.measure_file


def dying(path, scheme, study, keep=None):
    if study == KILL:
        os._exit(137)
    return real(path, scheme, study, keep=keep)


M.measure_file = dying
try:
    RUN.main(sys.argv[2:])
    print("exit 0")
except SystemExit as e:
    print("exit", e.code)
