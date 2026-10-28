# Copied for the cadaver-power note from the third fix's scratch folder, adv-round3/epal_share.py, 2026-10-28.
# Changed: it took the note's folder as its one argument and read between_studies.json and seven/part_a.json
# inside it; it now takes the two files as its arguments. It scores no rule, so it runs in a second.
#     python3 -I verify/epal_share.py between_studies.json seven/part_a.json > verify/epal_share.log
"""EPAl's share of the pooled spread, and what the pooled spread without EPAl is worth."""
import json, math, sys
import numpy as np

d = json.load(open(sys.argv[1]))
cells = d["cells"]
df = np.array([c["studies"] - 1 for c in cells], float)
f2 = np.array([c["f_obs"] ** 2 for c in cells])
epal = np.array([c["measure"] == "EPAl" for c in cells])
print("cells", len(cells), "EPAl cells", int(epal.sum()))
print("df total", df.sum(), "EPAl df", df[epal].sum(), "share %.4f" % (df[epal].sum() / df.sum()))
W = (df * f2).sum()
print("df-weighted sum of f_obs^2: %.4f; EPAl's %.4f, share %.4f" % (W, (df * f2)[epal].sum(), (df * f2)[epal].sum() / W))
above = df * (f2 - 1 / 12)
print("part above 1/12: total %.4f, EPAl %.4f, share %.4f" % (above.sum(), above[epal].sum(), above[epal].sum() / above.sum()))
pooled = math.sqrt(W / df.sum() - 1 / 12)
pooled_wo = math.sqrt((df * f2)[~epal].sum() / df[~epal].sum() - 1 / 12)
print("pooled weighted %.4f, without EPAl %.4f" % (pooled, pooled_wo))
print("json without EPAl", d["summary"]["definitions_left_out"][0]["pooled"]["weighted_by_df"])
# What a pooled spread is worth, r / f^2, as the median over the 704 cells (part_a.json's factor)
a = json.load(open(sys.argv[2]))
fac = a["by_kind"]["all"]["factor"]
print("factor over 704 cells", fac)
fac7 = a["by_kind"]["seven"]["factor"]
print("factor over the seven's 154 cells", fac7)
for f in (pooled, pooled_wo, 0.55, 0.48, 0.479, 0.53, 0.529):
    print("f %.4f: worth %s (all), %s (seven)" % (f, {k: round(v / f ** 2, 2) for k, v in fac.items()},
                                                 {k: round(v / f ** 2, 2) for k, v in fac7.items()}))
