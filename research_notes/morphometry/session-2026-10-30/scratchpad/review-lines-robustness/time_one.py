"""Time one study's measuring and drawing, and its peak memory, in a fresh process.

    python time_one.py MASK SCHEME lines|plain [--per-builder]
"""
import resource
import sys
import time
from collections import defaultdict

from morphometry import __main__ as RUN
from morphometry import measure as M


def main():
    path, scheme, mode = sys.argv[1:4]
    per_builder = "--per-builder" in sys.argv
    kept = {}
    t0 = time.time()
    rows = M.measure_file(path, scheme, "x", keep=kept if mode == "lines" else None)
    t1 = time.time()
    rss1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print("measure %.1f s, %d rows, peak rss %.0f MB" % (t1 - t0, len(rows), rss1 / 1024.0))
    if mode != "lines":
        return
    if per_builder:
        from morphoview import lines as LN
        cost = defaultdict(float)
        for lv, v in kept["verts"].items():
            for build in (LN.heights, LN.wedge, LN.waist, LN.panjabi_plates, LN.least_depth, LN.lateral_film,
                          LN.spinous, LN.tp_span):
                s = time.time()
                try:
                    build(v)
                except Exception as e:
                    print("  %s %s raised %s: %s" % (lv, build.__name__, type(e).__name__, e))
                cost[build.__name__] += time.time() - s
            s = time.time()
            LN.pedicles(v, kept["peds"][lv], kept["values"][lv])
            cost["pedicles(reused)"] += time.time() - s
            s = time.time()
            LN.interpedicular(v, kept["peds"][lv])
            cost["interpedicular"] += time.time() - s
        for (a, b) in kept["discs"]:
            s = time.time()
            LN.discs(kept["verts"][a], kept["verts"][b])
            cost["discs"] += time.time() - s
        for k, c in sorted(cost.items(), key=lambda kv: -kv[1]):
            print("  %-20s %.2f s" % (k, c))
    t2 = time.time()
    lines, frames, flags = RUN.study_lines("x", kept)
    t3 = time.time()
    rss2 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print("draw %.1f s (%.0f%% of the measuring), %d line rows, %d frames, %d flags, peak rss %.0f MB"
          % (t3 - t2, 100 * (t3 - t2) / (t1 - t0), len(lines), len(frames), len(flags), rss2 / 1024.0))
    for f in flags:
        print("  flag", f["level"], f["note"][:200])
    status = defaultdict(int)
    for r in lines:
        if r["part"] == "":
            status[r["status"].split(":")[0]] += 1
    print("  statuses", dict(status))


if __name__ == "__main__":
    main()
