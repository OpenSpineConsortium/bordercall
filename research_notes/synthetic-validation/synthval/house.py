"""The house format for line graphs, and Benzel's for drawings of the anatomy.

A copy of schwingcheck/figures.py as the chain of levels' branch holds it (claude/project-thread-
tkihxo at 30887cb, not yet on main), so that this note draws as the build-up study does: the
owner's words of 28 October 2026, 22:54 UTC, "use it much more, as the default for line graph
plotting, of course for anatomical type graphs use Benzel format graphs". Lettered panels, black
ink, serif type, thin lines, no grid and no colour; a series told apart by line and marker. Once
that module is on main this file gives way to it.

Every figure is written as PDF (no date inside), PNG at 300 dpi, the CSV of every number drawn
and its caption, under sixty words.
"""
from __future__ import annotations

import csv
import os
from typing import List

INK = "#000000"
GREY = "#808080"
SERIF = ["Liberation Serif", "Times New Roman", "Nimbus Roman", "DejaVu Serif"]
PNG_DPI = 300
CAPTION_WORDS = 60
WIDTH_STYLE = {1: dict(linestyle=":", marker="^", markerfacecolor="white"),
               3: dict(linestyle="--", marker="s", markerfacecolor="white"),
               9: dict(linestyle="-", marker="o", markerfacecolor=INK)}
SERIES_STYLE = [dict(linestyle="-", marker="o", markerfacecolor=INK),
                dict(linestyle="--", marker="s", markerfacecolor="white"),
                dict(linestyle=":", marker="^", markerfacecolor="white"),
                dict(linestyle="-.", marker="D", markerfacecolor="white"),
                dict(linestyle="-", marker="v", markerfacecolor="white"),
                dict(linestyle="--", marker="o", markerfacecolor="white")]


def style():
    """pyplot with the house rcParams set, on the Agg backend."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "font.family": "serif", "font.serif": SERIF, "font.size": 9.5, "mathtext.fontset": "dejavuserif",
        "text.color": INK, "axes.edgecolor": INK, "axes.labelcolor": INK, "axes.linewidth": 0.8,
        "axes.titlesize": 9.5, "axes.titleweight": "normal", "axes.labelsize": 9,
        "xtick.color": INK, "ytick.color": INK, "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.width": 0.8, "ytick.major.width": 0.8, "xtick.major.size": 3.5, "ytick.major.size": 3.5,
        "xtick.labelsize": 8, "ytick.labelsize": 8,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
        "legend.frameon": True, "legend.edgecolor": INK, "legend.fancybox": False, "legend.framealpha": 1.0,
        "legend.fontsize": 7.5, "legend.title_fontsize": 7.5,
        "lines.linewidth": 1.1, "lines.markersize": 4.5, "lines.markeredgewidth": 0.9, "lines.color": INK,
        "errorbar.capsize": 2.5, "figure.dpi": 100, "savefig.dpi": PNG_DPI,
        "patch.linewidth": 0.8, "patch.edgecolor": INK, "hatch.linewidth": 0.5, "hatch.color": INK,
        "axes.prop_cycle": matplotlib.cycler(color=[INK]),
    })
    return plt


def letter(ax, text: str, title: str = ""):
    """A panel's letter, bold, above its top left corner, and its title beside it."""
    ax.annotate(text, xy=(0, 1), xycoords="axes fraction", xytext=(-6, 5), textcoords="offset points",
                fontsize=12, fontweight="bold", ha="left", va="bottom")
    if title:
        ax.annotate(title, xy=(0, 1), xycoords="axes fraction", xytext=(10, 5), textcoords="offset points",
                    fontsize=9, ha="left", va="bottom")


def save(fig, outdir: str, name: str, caption: str) -> List[str]:
    """The figure as PDF and PNG, and its caption beside them; the paths written."""
    import matplotlib.pyplot as plt
    if len(caption.split()) > CAPTION_WORDS:
        raise ValueError("the caption of %s has %d words, more than %d" % (name, len(caption.split()), CAPTION_WORDS))
    paths = [os.path.join(outdir, name + ".pdf"), os.path.join(outdir, name + ".png")]
    fig.savefig(paths[0], bbox_inches="tight", facecolor="white", metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(paths[1], bbox_inches="tight", facecolor="white")
    plt.close(fig)
    p = os.path.join(outdir, name + ".caption.txt")
    with open(p, "w", encoding="ascii", newline="\n") as fh:
        fh.write(caption.strip() + "\n")
    return paths + [p]


def write_csv(outdir: str, name: str, rows: List[dict]) -> str:
    """Every number drawn, one row a point, floats to six significant figures."""
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
