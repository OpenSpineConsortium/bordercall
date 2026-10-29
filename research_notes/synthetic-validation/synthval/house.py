"""The house format for line graphs, and Benzel's for drawings of the anatomy.

schwingcheck/figures.py holds the house format the build-up study draws in (the owner's words of
28 October 2026, 22:54 UTC, "use it much more, as the default for line graph plotting, of course
for anatomical type graphs use Benzel format graphs"): lettered panels, black ink, serif type, thin
lines, no grid and no colour, a series told apart by line and marker. This file takes it from
there and adds only what this note needs beside it:

- GREY, for a published series behind the generator's line, and SERIES_STYLE, seven line and marker
  pairs for series that are not counts of bodies (schwingcheck's WIDTH_STYLE is for those);
- rcParams for patches and hatches, which the renders use;
- save refuses a caption over CAPTION_WORDS, which schwingcheck's leaves to its caller;
- write_csv takes every column any row has, where schwingcheck's takes the first row's, since the
  rows of one figure's panels differ.

Every figure is written as PDF (no date inside), PNG at 300 dpi, the CSV of every number drawn and
its caption; FIGURES.md names the records and the code by sha256 (figures.write_index).
"""
from __future__ import annotations

import csv
import os
from typing import List

from schwingcheck import figures as F
from schwingcheck.figures import CAPTION_WORDS, INK, PNG_DPI, SERIF, WIDTH_STYLE, letter, sha256  # noqa: F401

GREY = "#808080"
SERIES_STYLE = [dict(linestyle="-", marker="o", markerfacecolor=INK),
                dict(linestyle="--", marker="s", markerfacecolor="white"),
                dict(linestyle=":", marker="^", markerfacecolor="white"),
                dict(linestyle="-.", marker="D", markerfacecolor="white"),
                dict(linestyle="-", marker="v", markerfacecolor="white"),
                dict(linestyle="--", marker="o", markerfacecolor="white"),
                dict(linestyle=":", marker="s", markerfacecolor=INK)]


def style():
    """schwingcheck's house rcParams, with the patch and hatch settings the renders use."""
    plt = F.style()
    plt.rcParams.update({"patch.linewidth": 0.8, "patch.edgecolor": INK, "hatch.linewidth": 0.5, "hatch.color": INK})
    return plt


def save(fig, outdir: str, name: str, caption: str) -> List[str]:
    """schwingcheck's save, refusing a caption longer than the house allows."""
    if F.words(caption) > CAPTION_WORDS:
        raise ValueError("the caption of %s has %d words, more than %d" % (name, F.words(caption), CAPTION_WORDS))
    return F.save(fig, outdir, name, caption)


def write_csv(outdir: str, name: str, rows: List[dict]) -> str:
    """Every number drawn, one row a point, floats to six significant figures, every column any row has."""
    path = os.path.join(outdir, name + ".csv")
    cols: List[str] = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    with open(path, "w", encoding="ascii", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: format(v, ".6g") if isinstance(v, float) else v for k, v in r.items()})
    return path
