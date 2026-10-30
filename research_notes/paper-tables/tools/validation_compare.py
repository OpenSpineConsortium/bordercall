"""Compare the blind re-read with the record: the transcription error rate with its Wilson interval.

The sample is tools/validation_sample.py's: tasks/<paper>.csv went to the readers, hidden/<paper>.csv holds the
recorded cells. Each reader writes reads/<paper>.csv with the columns cell, read_value, legibility and note,
the value as printed on the page image and nothing taken from the record. This script sets each read beside
the record's value, the number it read from the cell as printed, numerically where both parse and as text otherwise, writes every mismatch to
mismatches.csv for the adjudicator, who re-reads each at a higher resolution and says in a column `record`
whether the record is wrong, the reader is wrong or neither can be read, and gives the rate: cells the record
got wrong over cells compared, with the Wilson 95 percent interval, by paper and overall. Until the
adjudicator has written the column, every mismatch counts against the record, the upper bound.

    python3 -I tools/validation_compare.py <sample folder> [--adjudicated mismatches.csv]
"""
import argparse
import csv
import glob
import math
import os
import re

MISMATCH = ["cell", "paper", "table", "pdf_page", "row_label", "column_label", "statistic", "recorded", "value", "read",
            "legibility", "reader_note", "record"]


def parse(text):
    """A printed number as a float, minus signs and thin spaces unified; None where it is not one."""
    t = (text or "").strip().replace("\u2212", "-").replace("\u2013", "-").replace(",", "")
    t = re.sub(r"\s+", "", t)
    try:
        return float(t)
    except ValueError:
        return None


def same(recorded, value, read):
    """The read against the record's number (value), else against the cell as printed (printed_as),
    which holds the whole printed string, "4.4 (1.0)", "+/-1.99", "17.6-30.54", "(42)" or "Ten", so
    a read of 4.4 for a mean is right where value says 4.4; a word is matched by number too."""
    b = parse(read)
    for recorded_text in (value, recorded):
        a = parse(recorded_text)
        if a is not None and b is not None and a == b:
            return True
    return (recorded or "").strip() == (read or "").strip() or (value or "").strip() == (read or "").strip()


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centre - half), min(1.0, centre + half))


def compare(folder):
    hidden = {}
    for path in sorted(glob.glob(os.path.join(folder, "hidden", "*.csv"))):
        for r in csv.DictReader(open(path, newline="")):
            hidden[r["cell"]] = r
    tasks = {}
    for path in sorted(glob.glob(os.path.join(folder, "tasks", "*.csv"))):
        for r in csv.DictReader(open(path, newline="")):
            tasks[r["cell"]] = r
    reads = {}
    for path in sorted(glob.glob(os.path.join(folder, "reads", "*.csv"))):
        for r in csv.DictReader(open(path, newline="")):
            reads[r["cell"]] = r
    rows = []
    for cell, h in hidden.items():
        t, r = tasks[cell], reads.get(cell)
        if r is None:
            continue
        rows.append({"cell": cell, "paper": t["paper"], "table": t["table"], "pdf_page": t["pdf_page"],
                     "row_label": t["row_label"], "column_label": t["column_label"], "statistic": t["statistic"],
                     "recorded": h["printed_as"], "value": h["value"], "read": r["read_value"], "legibility": r.get("legibility", ""),
                     "reader_note": r.get("note", ""), "record": "",
                     "match": same(h["printed_as"], h["value"], r["read_value"])})
    return rows, len(hidden)


def rates(rows, verdicts):
    """{paper or 'all': (record faults, compared, low, high)}, a mismatch counting against the record unless the
    adjudicator's verdict says the reader was wrong or neither could be read."""
    out = {}
    papers = sorted({r["paper"] for r in rows}) + ["all"]
    for paper in papers:
        mine = [r for r in rows if paper == "all" or r["paper"] == paper]
        faults = sum(1 for r in mine if not r["match"] and verdicts.get(r["cell"], "record") == "record")
        low, high = wilson(faults, len(mine))
        out[paper] = (faults, len(mine), low, high)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--adjudicated", help="mismatches.csv with the adjudicator's `record` column filled")
    args = ap.parse_args()
    rows, drawn = compare(args.folder)
    verdicts = {}
    if args.adjudicated:
        for r in csv.DictReader(open(args.adjudicated, newline="")):
            if r.get("record", "").strip():
                verdicts[r["cell"]] = r["record"].strip()
    mismatches = [r for r in rows if not r["match"]]
    out = os.path.join(args.folder, "mismatches.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MISMATCH, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for r in mismatches:
            w.writerow({**r, "record": verdicts.get(r["cell"], "")})
    print("%d of %d drawn cells read; %d mismatches written to %s" % (len(rows), drawn, len(mismatches), out))
    for paper, (faults, n, low, high) in rates(rows, verdicts).items():
        if faults or paper == "all":
            print("%-18s %3d of %3d  %.1f%% (%.1f to %.1f)" % (paper, faults, n, 100 * faults / n if n else 0,
                                                             100 * low, 100 * high))


if __name__ == "__main__":
    main()
