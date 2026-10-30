"""profile_study.py MASK [MASK...]: measure each phantom mask with the engine on PYTHONPATH (scheme
enhance), timing every linear program the engine solves (count, constraint rows, seconds and the
status codes) and the top functions by cumulative time.
"""
import collections
import cProfile
import io
import pstats
import sys
import time

import scipy
import scipy.optimize as so

from morphometry import measure as M

calls = []
ORIGINAL = so.linprog


def timed_linprog(*args, **kw):
    t0 = time.perf_counter()
    res = ORIGINAL(*args, **kw)
    A = kw.get("A_ub")
    rows, cols = (A.shape if A is not None else (0, 0))
    caller = sys._getframe(1).f_code
    calls.append((rows, cols, time.perf_counter() - t0, int(res.status), "%s:%s" % (caller.co_filename.rsplit("/", 1)[-1], caller.co_name)))
    return res


def patch():
    import morphometry.body as B
    import morphometry.pedicle as PD
    so.linprog = timed_linprog
    for mod in (B, PD):
        if hasattr(mod, "linprog"):
            mod.linprog = timed_linprog


def main(paths):
    patch()
    print("scipy", scipy.__version__)
    for path in paths:
        del calls[:]
        prof = cProfile.Profile()
        t0 = time.time()
        prof.enable()
        rows = M.measure_file(path, "enhance", "phantom")
        prof.disable()
        wall = time.time() - t0
        levels = {r["level"] for r in rows if r["level"] and "-" not in r["level"] and r["level"] not in ("study", "pelvis")}
        errs = [r for r in rows if str(r["key"]).startswith("flag:error")]
        print("== %s: %.1f s (profiled), %d rows, %d levels, %d error rows" % (path, wall, len(rows), len(levels), len(errs)))
        if calls:
            st = collections.Counter(c[3] for c in calls)
            big = max(calls, key=lambda c: c[0])
            print("   linprog: %d calls, %.2f s total, largest A_ub %dx%d (%.3f s), statuses %s"
                  % (len(calls), sum(c[2] for c in calls), big[0], big[1], big[2], dict(st)))
            per = collections.defaultdict(list)
            for c in calls:
                per[c[4]].append(c)
            for where, cs in sorted(per.items()):
                print("     %-34s %4d calls %6.2f s  rows max %5d  statuses %s" % (where, len(cs), sum(c[2] for c in cs),
                      max(c[0] for c in cs), dict(collections.Counter(c[3] for c in cs))))
        s = io.StringIO()
        pstats.Stats(prof, stream=s).sort_stats("cumulative").print_stats(18)
        print("\n".join(line for line in s.getvalue().splitlines() if "morphometry" in line or "scanimport" in line
                        or "linprog" in line or "ncalls" in line)[:4000])


if __name__ == "__main__":
    main(sys.argv[1:])
