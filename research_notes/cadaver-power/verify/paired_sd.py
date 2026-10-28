# Copied for the cadaver-power note from the reviewers' verify-published-tables/paired_sd.py, 2026-10-28.
# Unchanged: it already took its input as an argument.
#     python3 -I verify/paired_sd.py between_studies.json
"""Sensitivity of the median f_low to how a side-paired measure's person SD is formed."""
import json, math, statistics, sys
cells = json.load(open(sys.argv[1]))["cells"]
PAIRED = {"PDH", "PDW", "PDIs", "Ss"}
def med(rho, units):
    fs = []
    for c in cells:
        sd, s_b = c["sd"], c["s_b"]
        sd_b = sd * math.sqrt((1 + rho) / 2) if c["measure"] in PAIRED else sd
        denom = sd if units == "single" else sd_b
        fs.append(math.sqrt(max(0.0, s_b ** 2 - sd_b ** 2 / 12)) / denom)
    return statistics.median(fs), sum(f > 0.3 for f in fs) / len(fs)
print("paired cells:", sum(c["measure"] in PAIRED for c in cells), "of", len(cells))
for rho in (1.0, 0.8, 0.5):
    for units in ("single", "bilateral"):
        m, share = med(rho, units)
        print("left-right correlation %.1f, f in units of the %-9s SD: median f_low %.3f, share above 0.3 %.3f" % (rho, units, m, share))
