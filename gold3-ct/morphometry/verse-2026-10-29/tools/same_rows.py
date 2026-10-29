"""Measure a mask as published and as its int16 copy and say whether the rows are the same.

    python same_rows.py BORDERCALL_ROOT SERIES SRC INT16_COPY
"""
import sys
import time


def main(root, series, src, copy):
    sys.path.insert(0, root)
    from morphometry import measure as M
    t = time.time()
    a = M.measure_file(src, "verse", series)
    ta = time.time() - t
    t = time.time()
    b = M.measure_file(copy, "verse", series)
    tb = time.time() - t
    norm = lambda rows: [(r["study"], r["level"], r["key"], repr(r["value"]), r["note"]) for r in rows]
    same = norm(a) == norm(b)
    print("%s rows %d %d same %s seconds %.0f %.0f" % (series, len(a), len(b), same, ta, tb), flush=True)
    if not same:
        diff = [x for x in zip(norm(a), norm(b)) if x[0] != x[1]][:5]
        print(diff)


if __name__ == "__main__":
    main(*sys.argv[1:5])
