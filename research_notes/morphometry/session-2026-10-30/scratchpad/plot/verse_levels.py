"""Plot the verse report's per-level medians: VerSe against TotalSegmentator."""
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

text = open(sys.argv[1]).read()
parts = re.split(r"- (VerSe|TotalSegmentator) per level", text)
sets = {}
for name, body in zip(parts[1::2], parts[2::2]):
    rows = re.findall(r"\| (\w+) \| (\d+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|", body)
    sets[name] = {r[0]: tuple(float(x) for x in r[1:]) for r in rows}
order = [lv for lv in sets["VerSe"] if lv in sets["TotalSegmentator"]]
x = range(len(order))
fig, (a, b) = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)
style = {"VerSe": dict(color="#2a6fdb", marker="o"), "TotalSegmentator": dict(color="#d9822b", marker="s")}
for name, d in sets.items():
    a.plot(x, [d[lv][1] for lv in order], label=name + ", anterior", ls="-", ms=4, **style[name])
    a.plot(x, [d[lv][2] for lv in order], label=name + ", posterior", ls="--", ms=4, mfc="none", **style[name])
    b.plot(x, [d[lv][3] for lv in order], label=name, ms=4, **style[name])
a.set_ylabel("median body height, mm")
a.legend(fontsize=8, ncol=2, frameon=False)
b.axhline(1.0, color="0.6", lw=0.8)
b.set_ylabel("anterior / posterior height")
b.legend(fontsize=8, frameon=False)
b.set_xticks(list(x))
b.set_xticklabels(order, fontsize=8)
for ax in (a, b):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="0.92")
fig.suptitle("Morphometry verse run (job 40877151): per-level medians, VerSe 374 masks, TotalSegmentator 159", fontsize=10)
fig.tight_layout()
fig.savefig(sys.argv[2], dpi=150)
