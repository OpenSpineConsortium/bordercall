"""Flag the series values a reader should check on the page: the plausibility arm of the validation
the owner asked for on 2026-10-29 (research_notes/clinical-reread/HANDOFF.md, step 2b).

Four flags, each by code over data/series.csv and the cohorts files, none a verdict: a value a flag
names is checked against the paper's own page, and the record is corrected only where the page says
the record is wrong.

- outlier: a series' mean beyond four scaled median absolute deviations of the other papers' means
  for the same measure and level, among series whose definition stands to Panjabi's the same way
  (same or close against the rest), with at least four other papers to judge by.
- sd_above_mean: an SD above the mean of a length, area or volume, where a spread wider than the
  size itself is more often a misread column than a population.
- n_above_people: a count above its cohort's people, which a count of pedicles, sides or end-plates
  read as people gives.
- reversal: a step between neighbouring levels in the opposite direction to the other papers' at
  the same two levels, where at least four other papers agree on the direction four times in five
  and this paper's step is at least half the size of their median step; a level misread as its
  neighbour shows this way.

    python3 -I tools/plausibility.py data/series.csv data/cohorts tools/vocabulary.csv <flags.csv>
"""
import argparse
import collections
import csv
import glob
import json
import os
import statistics

LEVELS = ["C2", "C3", "C4", "C5", "C6", "C7"] + ["T%d" % i for i in range(1, 13)] + ["L%d" % i for i in range(1, 6)]
SIZES = {"length", "area", "volume"}
COLUMNS = ["flag", "paper", "cohort", "technique", "source_of_values", "key", "level", "sex", "group", "value",
           "reference", "detail"]


def number(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def read_series(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["mean"], r["sd"], r["n"] = number(r["mean"]), number(r["sd"]), number(r["n"])
    return rows


def read_people(folder):
    """{(paper, cohort): n_people} from the cohorts files, where the file gives a number."""
    out = {}
    for path in sorted(glob.glob(os.path.join(folder, "*.cohorts.json"))):
        record = json.load(open(path))
        for c in record.get("cohorts", []):
            n = number(c.get("n_people"))
            if n is not None:
                out[(record["paper"], c["cohort"])] = n
    return out


def read_kinds(path):
    with open(path, newline="") as f:
        return {r["key"]: r["kind"] for r in csv.DictReader(f)}


def ident(r):
    return (r["paper"], r["cohort"], r["technique"], r["source_of_values"], r["key"], r["sex"], r["group"])


def flag(kind, r, value, reference, detail):
    return {"flag": kind, "paper": r["paper"], "cohort": r["cohort"], "technique": r["technique"],
            "source_of_values": r["source_of_values"], "key": r["key"], "level": r["level"], "sex": r["sex"],
            "group": r["group"], "value": value, "reference": reference, "detail": detail}


def stratum(r):
    return "panjabi" if r["vs_panjabi"] in ("same", "close") else "other"


def outliers(series):
    """Means four scaled MADs from the other papers' means at the same measure, level and stratum."""
    by_cell = collections.defaultdict(list)
    for r in series:
        if r["mean"] is not None and r["level"] in LEVELS:
            by_cell[(r["key"], r["level"], stratum(r))].append(r)
    out = []
    for cell, rows in by_cell.items():
        for r in rows:
            others = [o["mean"] for o in rows if o["paper"] != r["paper"]]
            if len({o["paper"] for o in rows if o["paper"] != r["paper"]}) < 4:
                continue
            median = statistics.median(others)
            mad = 1.4826 * statistics.median(abs(o - median) for o in others)
            if mad == 0:
                continue
            distance = abs(r["mean"] - median) / mad
            if distance > 4:
                out.append(flag("outlier", r, "%g" % r["mean"], "median %g, MAD %g" % (median, mad),
                                "%.1f scaled MADs from %d other papers' means" % (distance, len(others))))
    return out


def sd_above_mean(series, kinds):
    return [flag("sd_above_mean", r, "%g" % r["sd"], "mean %g" % r["mean"], "an SD above the size it spreads")
            for r in series
            if r["sd"] is not None and r["mean"] is not None and kinds.get(r["key"]) in SIZES and r["sd"] > abs(r["mean"])]


def n_above_people(series, people):
    out = []
    for r in series:
        limit = people.get((r["paper"], r["cohort"]))
        if r["n"] is not None and limit is not None and r["n"] > limit:
            out.append(flag("n_above_people", r, "%g" % r["n"], "cohort's people %g" % limit,
                            "n_from " + r["n_from"]))
    return out


def steps_of(series):
    """{series id: {(level, next level): step}} over neighbouring levels a series gives both of."""
    means = collections.defaultdict(dict)
    rows = {}
    for r in series:
        if r["mean"] is not None and r["level"] in LEVELS:
            means[ident(r)][r["level"]] = r["mean"]
            rows[ident(r) + (r["level"],)] = r
    steps = {}
    for sid, by_level in means.items():
        for a, b in zip(LEVELS, LEVELS[1:]):
            if a in by_level and b in by_level:
                steps[sid + ((a, b),)] = by_level[b] - by_level[a]
    return steps, rows


def reversals(series):
    steps, rows = steps_of(series)
    by_pair = collections.defaultdict(list)
    for key, step in steps.items():
        sid, pair = key[:-1], key[-1]
        by_pair[(sid[4], pair)].append((sid, step))
    out = []
    for (measure, pair), entries in by_pair.items():
        for sid, step in entries:
            others = [s for o, s in entries if o[0] != sid[0]]
            papers = {o[0] for o, s in entries if o[0] != sid[0]}
            if len(papers) < 4 or step == 0:
                continue
            same = sum(1 for s in others if (s > 0) == (step > 0))
            agree = max(same, len(others) - same) / len(others)
            majority_sign = 1 if sum(1 for s in others if s > 0) > len(others) / 2 else -1
            median_size = statistics.median(abs(s) for s in others)
            if agree >= 0.8 and (step > 0) != (majority_sign > 0) and abs(step) >= 0.5 * median_size:
                r = rows[sid + (pair[1],)]
                out.append(flag("reversal", r, "%+g from %s to %s" % (step, pair[0], pair[1]),
                                "%d of %d other papers step %s, median size %g"
                                % (max(same, len(others) - same), len(others), "up" if majority_sign > 0 else "down",
                                   median_size), "a step against the other papers' direction"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("series")
    ap.add_argument("cohorts")
    ap.add_argument("vocabulary")
    ap.add_argument("out")
    args = ap.parse_args()
    series = read_series(args.series)
    flags = (outliers(series) + sd_above_mean(series, read_kinds(args.vocabulary))
             + n_above_people(series, read_people(args.cohorts)) + reversals(series))
    flags.sort(key=lambda f: (f["flag"], f["paper"], f["key"], LEVELS.index(f["level"]) if f["level"] in LEVELS else 99))
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(flags)
    counts = collections.Counter(f["flag"] for f in flags)
    print("%d flags over %d series: %s" % (len(flags), len(series),
                                           ", ".join("%s %d" % kv for kv in sorted(counts.items()))))


if __name__ == "__main__":
    main()
