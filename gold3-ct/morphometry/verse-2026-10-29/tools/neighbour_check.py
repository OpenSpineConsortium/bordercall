"""Quick test of one explanation for the missed grade 2 and 3 vertebrae: a crush lowers all three
heights, so a ratio inside one vertebra cannot see it. Compare each vertebra's posterior height
with the median posterior height of its two neighbours in the same series.

    python neighbour_check.py joined.csv
"""
import csv
import statistics
import sys

ORDER = ["T%d" % i for i in range(1, 14)] + ["L%d" % i for i in range(1, 7)]


def main(path):
    rows = list(csv.DictReader(open(path)))
    by = {(r["series"], r["level"]): r for r in rows}
    out = {}
    for r in rows:
        if not r["smaller_ratio"] or r["level"] not in ORDER:
            continue
        i = ORDER.index(r["level"])
        nb = [by.get((r["series"], ORDER[j])) for j in (i - 1, i + 1) if 0 <= j < len(ORDER)]
        hs = [float(n["h_post_inset"]) for n in nb if n and n["h_post_inset"] and n["grade"] == "0"]
        if not hs or not r["h_post_inset"]:
            continue
        rel = float(r["h_post_inset"]) / statistics.median(hs)
        missed = float(r["smaller_ratio"]) >= 0.80
        out.setdefault((r["grade"], missed), []).append(rel)
    for (g, missed), xs in sorted(out.items()):
        xs.sort()
        print("grade", g, "ratio missed" if missed else "ratio caught", "n", len(xs),
              "median post/neighbours %.3f" % statistics.median(xs),
              "share under 0.80 %.2f" % (sum(x < 0.80 for x in xs) / len(xs)))


if __name__ == "__main__":
    main(sys.argv[1])
