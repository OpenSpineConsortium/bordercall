"""Draw the blind re-read sample of the readings: the same cells for anyone who runs it.

The owner asked on 2026-10-29 for extensive validation that the measures' data are of good quality. The first
check is a blind re-read: a reader who has not seen the recorded value reads the cell again from the page image,
and the two are compared, so the readings' transcription error rate is measured with an interval rather than
assumed. This draws the cells with a fixed seed, twelve per paper, from the cells printed by the paper itself with
a page to read, and writes two folders: tasks/<paper>.csv, the locators a blind reader is given (table, page, row,
column, level, side, sex, group, statistic, never the value), and hidden/<paper>.csv, the recorded values the
comparison reads afterwards. A cell is named <paper>:<line of data/readings/<paper>.csv>.

    python3 tools/validation_sample.py data/readings <out folder> [--seed 2026] [--per-paper 12]
"""
import argparse
import csv
import glob
import os
import random

LOCATORS = ["cell", "paper", "table", "pdf_page", "journal_page", "row_label", "column_label", "measure_label",
            "level", "side", "sex", "group", "statistic"]
HIDDEN = ["cell", "printed_as", "value", "units", "legibility", "source_of_values", "key", "canonical_value",
          "canonical_units", "factor", "note", "check", "check_note"]
STATISTICS = ("mean", "sd", "n", "single", "se", "median", "min", "max", "range_low", "range_high")


def printed_by_the_paper(row):
    """A cell a blind reader can read from the page: the paper's own number, with a page, printed as a number."""
    return (row["pdf_page"].strip() and row["source_of_values"] == "this paper"
            and row["statistic"] in STATISTICS and row["printed_as"].strip())


def page_number(row):
    return int(row["pdf_page"]) if row["pdf_page"].isdigit() else 0


def draw(readings, out, seed, per_paper):
    rng = random.Random(seed)
    os.makedirs(os.path.join(out, "tasks"), exist_ok=True)
    os.makedirs(os.path.join(out, "hidden"), exist_ok=True)
    total = 0
    for path in sorted(glob.glob(os.path.join(readings, "*.csv"))):
        paper = os.path.basename(path)[:-4]
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        candidates = [(i, r) for i, r in enumerate(rows) if printed_by_the_paper(r)]
        picked = rng.sample(candidates, min(per_paper, len(candidates)))
        picked.sort(key=lambda t: (page_number(t[1]), t[0]))
        write(os.path.join(out, "tasks", paper + ".csv"), LOCATORS, paper, picked)
        write(os.path.join(out, "hidden", paper + ".csv"), HIDDEN, paper, picked)
        total += len(picked)
    return total


def write(path, columns, paper, picked):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for i, row in picked:
            # line i + 2: the header is line 1 and the first row line 2
            w.writerow({"cell": "%s:%d" % (paper, i + 2), **{c: row[c] for c in columns[1:]}})


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("readings")
    p.add_argument("out")
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--per-paper", type=int, default=12)
    a = p.parse_args()
    print("cells drawn:", draw(a.readings, a.out, a.seed, a.per_paper))


if __name__ == "__main__":
    main()
