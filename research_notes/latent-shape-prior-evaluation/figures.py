"""The two figures of this plan, drawn from the CSVs beside them, so a figure and the README's tables cannot disagree.

    python3 -I figures.py --out figures

fig1_design draws the design matrix: the arms down the side, what each is scored on across the top, a filled mark where
the score applies to the arm and an open one where it is reported but not scored. fig2_stages draws the stages as a
ladder with the jobs each needs (a white bar asks for none) and the decision each informs. Black ink, serif type, lettered panels, as the
house format of schwingcheck/figures.py draws; matplotlib alone, since the plan's folder imports nothing of the
packages. FIGURES.md lists each file with its sha256.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.edgecolor": "black", "text.color": "black",
                     "axes.labelcolor": "black", "xtick.color": "black", "ytick.color": "black"})


def rows_of(name):
    with open(os.path.join(HERE, name), newline="") as f:
        return list(csv.DictReader(f))


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def design(out):
    rows = rows_of("fig1_design.csv")
    arms = []
    metrics = []
    for r in rows:
        if r["arm"] not in arms:
            arms.append(r["arm"])
        if r["metric"] not in metrics:
            metrics.append(r["metric"])
    fig, ax = plt.subplots(figsize=(9.0, 4.0))
    for r in rows:
        x, y = metrics.index(r["metric"]), arms.index(r["arm"])
        if r["mark"] == "scored":
            ax.plot(x, y, "s", color="black", markersize=9)
        elif r["mark"] == "reported":
            ax.plot(x, y, "s", markerfacecolor="white", markeredgecolor="black", markersize=9)
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(metrics, rotation=25, ha="right")
    ax.set_yticks(range(len(arms)))
    ax.set_yticklabels(arms)
    ax.set_ylim(len(arms) - 0.5, -0.5)
    ax.set_xlim(-0.5, len(metrics) - 0.5)
    ax.set_title("A  Scored on (filled) and reported beside it (open), by arm", loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, "fig1_design." + ext), dpi=200, bbox_inches="tight")
    plt.close(fig)


def stages(out):
    rows = rows_of("fig2_stages.csv")
    fig, ax = plt.subplots(figsize=(9.0, 0.9 * len(rows) + 1.2))
    for i, r in enumerate(rows):
        y = len(rows) - 1 - i
        jobs = int(r["jobs"])
        ax.barh(y, max(jobs, 0.15), color="black" if jobs > 0 else "white", edgecolor="black", height=0.5)
        words = "%s (%s): %s" % (r["stage"], r["where"], r["decides"])
        ax.text(max(jobs, 0.15) + 0.1, y, textwrap.fill(words, 92), va="center", fontsize=7.0)
    ax.set_yticks([])
    ax.set_xlabel("grid jobs the stage asks for (white: a container or the flow's own step, no job)")
    ax.set_xlim(0, 8)
    ax.set_title("B  The stages, in order, with the jobs each needs and the decision it informs", loc="left")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, "fig2_stages." + ext), dpi=200, bbox_inches="tight")
    plt.close(fig)


def index(out):
    lines = ["# Figures", "", "Drawn by `python3 -I figures.py --out figures` from fig1_design.csv and fig2_stages.csv beside this file;",
             "each figure's caption is its .caption.txt. Nothing here is a result: the figures draw the plan itself.", ""]
    for name in ("fig1_design", "fig2_stages"):
        lines += ["## " + name, ""]
        with open(os.path.join(HERE, name + ".caption.txt")) as f:
            lines += [f.read().strip(), ""]
        for ext in ("caption.txt", "csv", "pdf", "png"):
            p = os.path.join(out if ext in ("pdf", "png") else HERE, name + "." + ext)
            lines.append("- %s.%s, sha256 %s" % (name, ext, sha256(p)))
        lines.append("")
    with open(os.path.join(out, "FIGURES.md"), "w") as f:
        f.write("\n".join(lines))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=os.path.join(HERE, "figures"))
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    design(a.out)
    stages(a.out)
    index(a.out)


if __name__ == "__main__":
    main()
