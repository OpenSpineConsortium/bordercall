# Copied for the cadaver-power note from the reviewers' verify-published-tables/definitions.py, 2026-10-28.
# Changed: the absolute paths became the command-line arguments below; it imports the note's shift_profile.py, of which it used an identical copy.
#     python3 -I verify/definitions.py between_studies.json
"""Apply the papers' own attributions of disagreements to definitions, and redo parts B and the split.

Left out, each where Panjabi's own text names a different definition:
  cervical p868: Liu's depths "probably measured at the centrum midheight" (EPDl, Liu);
  cervical p868: end-plate areas, Liu's "probably" with the uncovertebral area, Francis's the
                 ellipse of his own depth and width (EPAl, all);
  thoracic p898: Scoles's and Cotterill's depths "may be at the body mid-height" (EPDl, T levels).
"""
import json, math, os, statistics, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shift_profile as SP
cells = json.load(open(sys.argv[1]))["cells"]

def drop(cs, rules):
    out = []
    for c in cs:
        means = dict(c["means"])
        for measure, region, study in rules:
            if c["measure"] == measure and (region is None or c["level"][0] == region):
                if study is None:
                    means = {}
                else:
                    means.pop(study, None)
        if len(means) < 3:
            continue
        sd = c["sd"]
        s_b = statistics.stdev(means.values())
        out.append(dict(c, means=means, studies=len(means), s_b=s_b, f_obs=s_b / sd,
                        f_low=math.sqrt(max(0.0, s_b * s_b - sd * sd / 12)) / sd))
    return out

def part_b(cs, label):
    fl = [c["f_low"] for c in cs]
    pooled = math.sqrt(max(0, np.mean([c["f_obs"] ** 2 - 1 / 12 for c in cs])))
    print("%-58s cells %2d  median f_low %.3f  quartiles %s  above 0.3 %.2f  pooled %.3f" % (
        label, len(cs), statistics.median(fl), [round(x, 2) for x in statistics.quantiles(fl, n=4)],
        sum(x > 0.3 for x in fl) / len(fl), pooled))

def split(cs, label, measures=None):
    if measures:
        cs = [c for c in cs if c["measure"] in measures]
    out, ss, df = {}, 0.0, 0.0
    for (m, region), g in sorted(SP.groups(cs).items()):
        r = SP.fit(g)
        if r is None:
            continue
        out["%s %s" % (m, region)] = r
        ss += r["ms_level_by_level"] * r["df"]; df += r["df"]
    ms = ss / df
    shift = float(np.median([r["shift_sd"] for r in out.values()]))
    tl = SP.thoracic_lumbar(out)
    print("%-58s groups %2d  median shift %.3f (sampling out %.3f)  level-by-level %.3f to %.3f  T-L corr %s over %d" % (
        label, len(out), shift, math.sqrt(max(0, shift ** 2 - 1 / 12)), math.sqrt(max(0, ms - 1 / 12)), math.sqrt(ms),
        None if tl["correlation"] is None else round(tl["correlation"], 3), tl["pairs"]))

LIU = [("EPDl", "C", "Liu (1986)")]
AREAS = [("EPAl", None, None)]
MID_T = [("EPDl", "T", "Scoles (1988)"), ("EPDl", "T", "Cotterill (1986)")]
FIVE = {"EPDl", "EPWl", "VBHp", "SCD", "SCW"}
part_b(cells, "as published")
part_b(drop(cells, AREAS), "without the areas")
part_b(drop(cells, AREAS + LIU), "without the areas and Liu's depths")
part_b(drop(cells, AREAS + LIU + MID_T), "... and Scoles's and Cotterill's thoracic depths")
split(cells, "split, all ten, as published")
split(drop(cells, AREAS), "split, without the areas")
split(drop(cells, AREAS + LIU + MID_T), "split, all three attributions")
split(cells, "split, the five, as published", FIVE)
split(drop(cells, LIU + MID_T), "split, the five, without the midheight depths", FIVE)
