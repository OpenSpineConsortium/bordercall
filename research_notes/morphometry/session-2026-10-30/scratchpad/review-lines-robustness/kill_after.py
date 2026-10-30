"""Run `python -m morphometry run` in-process, the worker dying (os._exit, as a kill would) right
after it writes the first per-study file whose path holds PART, between one_study's writes.

    python kill_after.py PART run --masks ... --out ... --workers 1 --lines
"""
import os
import sys

from morphometry import __main__ as RUN

PART = sys.argv[1]
real = RUN.write_atomic


def dying(rows, path, fields=RUN.FIELDS):
    real(rows, path, fields)
    if PART in path:
        os._exit(137)


RUN.write_atomic = dying
RUN.main(sys.argv[2:])
