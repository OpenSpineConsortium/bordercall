# Copied for the cadaver-power note from the reviewers' verify-published-tables/pooled_sd_split.py, 2026-10-28.
# Changed: the absolute paths became the command-line arguments below; it imports the note's shift_profile.py, of which it used an identical copy.
#     python3 -I verify/pooled_sd_split.py between_studies.json
"""The split with each group's levels scaled by one pooled SD instead of each level's own SD (from 12 specimens)."""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shift_profile as SP
cells = json.load(open(sys.argv[1]))["cells"]

def run(cs, label, pooled_sd):
    out, ss, df = {}, 0.0, 0.0
    for key, g in sorted(SP.groups(cs).items()):
        if pooled_sd:
            common = math.sqrt(np.mean([c["sd"] ** 2 for c in g]))
            g = [dict(c, sd=common) for c in g]
        r = SP.fit(g)
        if r is None:
            continue
        out["%s %s" % key] = r
        ss += r["ms_level_by_level"] * r["df"]; df += r["df"]
    ms = ss / df
    shift = float(np.median([r["shift_sd"] for r in out.values()]))
    print("%-34s level-by-level %.3f to %.3f  median shift %.3f  T-L %.3f" % (
        label, math.sqrt(max(0, ms - 1 / 12)), math.sqrt(ms), shift, SP.thoracic_lumbar(out)["correlation"]))
    return out

a = run(cells, "ten, each level's own SD", False)
b = run(cells, "ten, one SD per group", True)
for k in a:
    print("   %-8s own %.3f  pooled %.3f" % (k, math.sqrt(a[k]["ms_level_by_level"]), math.sqrt(b[k]["ms_level_by_level"])))
FIVE = {"EPDl", "EPWl", "VBHp", "SCD", "SCW"}
five = [c for c in cells if c["measure"] in FIVE]
run(five, "five, each level's own SD", False)
run(five, "five, one SD per group", True)
liu = [c for c in cells if c["measure"] == "EPAl"]
d = [c["means"]["Liu (1986)"] - c["means"]["present"] for c in liu]
print("EPAl Liu - present, mm2:", d, "SD %.1f" % np.std(d, ddof=1))
print("in each level's SD units:", [round(x / c["sd"], 2) for x, c in zip(d, liu)], "SD %.2f" % np.std([x / c["sd"] for x, c in zip(d, liu)], ddof=1))
print("Panjabi's EPAl SEM by level:", [round(c["sd"] / math.sqrt(12), 2) for c in liu])
