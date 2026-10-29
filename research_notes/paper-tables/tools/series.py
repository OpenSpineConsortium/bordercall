"""Turn the mapped readings of the papers' tables into series: one mean, SD and count per measure
and level for each set of subjects, technique, sex and subgroup a paper prints.

Usage: python3 -I series.py <mapped folder> <cohorts folder> <out.csv>

A paper prints a measure as a mean with an SD, an SE or a variance, for each sex or both, each side
or their mean, in one table or several. The comparison between papers, and the naming of one
paper's fields by another paper's table, need one mean and one population SD per measure and
level of each set of subjects, so this file decides, in code that can be read, how each is made:

- the SD is the printed SD; else an SE times the root of its count; else the root of a printed
  variance; a series with no way to an SD keeps its mean and an empty SD. A meta-analysis's SE
  (technique meta_pool) is the uncertainty of a random-effects pooled mean, not the spread of the
  people behind it, so it gives no SD: Bonczar 2024's SEs times the root of its 1,481 subjects
  made SDs of 30 to 180 mm and deg;
- the count is the n printed for that cell, else the n printed for that measure and subgroup
  elsewhere in the paper, else the cohort's number of people from its cohorts file, and the
  series says which (n_from);
- the sides: a value printed for both sides or their mean is taken as it is; a right and a left
  only are averaged, mean with mean and SD with SD (sides "averaged"). Where a paper prints the
  two sides of one angle with opposite signs, its left is negated first (MIRRORED_LEFT), as its
  mapping note says, since a plain mean would cancel the angle: Tan 2004's pedicle angles, left
  -42.9 and right 39.6 at C3, averaged to -1.65 against Panjabi's 42.25;
- the sexes: a value printed for both sexes is taken as it is; a male and a female only, each
  with its count, are pooled into one series with the pooled SD, which takes in the difference
  between the sexes' means (sex "pooled"); without both counts they stay two series;
- subgroups (age bands, patients and controls, modalities) stay series of their own, since
  whether pooling them is right depends on what they are.

Values a table quotes from another study are series of that study's subjects, not of the paper's,
and keep the study's name in source_of_values.
"""

import collections
import csv
import json
import math
import os
import re
import sys

POOLED_MEANS = {"meta_pool"}
# (paper, key) whose left side is printed with the opposite sign to the right and to Panjabi's
# convention; the mapping note of each reading says to reverse the left (readings/tan2004.csv).
MIRRORED_LEFT = {("tan2004", "pedicle_incl_sag")}
NOT_MEASURES = {"subject_age", "subject_height", "subject_weight", "subject_bmi", "subject_count", "prevalence",
                "reliability", "other"}
PLAIN_SIDES = ("", "both", "mean of sides")
COLUMNS = ["paper", "cohort", "technique", "source_of_values", "key", "level", "sex", "group", "side", "mean", "sd",
           "n", "sd_from", "n_from", "units", "vs_panjabi", "definition", "tables", "pages"]
VERTEBRA = re.compile(r"^(C[1-7]|T(1[0-3]|[1-9])|L[1-6]|S[1-5])(-(C[1-7]|T(1[0-3]|[1-9])|L[1-6]|S[1-5]))?$")


def number(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def read_mapped(folder):
    rows = []
    for name in sorted(os.listdir(folder)):
        if name.endswith(".csv"):
            rows += list(csv.DictReader(open(os.path.join(folder, name), newline="")))
    return rows


def cohort_people(folder):
    people = {}
    for name in sorted(os.listdir(folder)):
        if name.endswith(".cohorts.json"):
            data = json.load(open(os.path.join(folder, name)))
            for c in data.get("cohorts", []):
                people[(data["paper"], c.get("cohort"))] = c.get("n_people")
    return people


def cell_key(row):
    return (row["paper"], row["cohort"], row["technique"], row["source_of_values"], row["key"], row["level"],
            row["sex"], row["group"], row["side"])


def gather(rows):
    """{cell: {statistic: [values], ...}} for the measure rows that name one vertebra or one disc."""
    cells = collections.defaultdict(lambda: collections.defaultdict(list))
    meta = {}
    for row in rows:
        if row["key"] in NOT_MEASURES or not VERTEBRA.match(row["level"]):
            continue
        value = number(row["canonical_value"])
        if value is None:
            continue
        k = cell_key(row)
        cells[k][row["statistic"]].append(value)
        m = meta.setdefault(k, {"units": row["canonical_units"], "vs_panjabi": row["vs_panjabi"],
                                "definition": row["definition"], "tables": set(), "pages": set()})
        m["tables"].add(row["table"])
        m["pages"].add(row["pdf_page"])
    return cells, meta


def printed_counts(rows):
    """The n a paper prints for a measure and subgroup at no particular cell, to stand in for a
    cell that prints none: {(paper, cohort, key, sex, group): n} where one n is printed, and
    {(paper, cohort, sex, group): n} for a count printed for the subgroup as a whole."""
    by_measure, by_group = collections.defaultdict(set), collections.defaultdict(set)
    for row in rows:
        value = number(row["canonical_value"]) if row["canonical_value"] else number(row["value"])
        if value is None or row["statistic"] not in ("n", "count"):
            continue
        if row["key"] == "subject_count":
            by_group[(row["paper"], row["cohort"], row["sex"], row["group"])].add(value)
        elif row["key"] not in NOT_MEASURES:
            by_measure[(row["paper"], row["cohort"], row["key"], row["sex"], row["group"])].add(value)
    single = lambda d: {k: next(iter(v)) for k, v in d.items() if len(v) == 1}
    return single(by_measure), single(by_group)


def first(values):
    return values[0] if values else None


def one_series(k, stats, people, by_measure, by_group):
    paper, cohort, technique, _, key, _, sex, group, _ = k
    mean = first(stats.get("mean", [])) if stats.get("mean") else first(stats.get("single", []))
    if mean is None:
        return None
    n, n_from = first(stats.get("n", [])), "cell"
    if n is None:
        n, n_from = by_measure.get((paper, cohort, key, sex, group)), "measure"
    if n is None:
        n, n_from = by_group.get((paper, cohort, sex, group)), "subgroup"
    if n is None and sex in ("all", "not stated"):
        n, n_from = people.get((paper, cohort)), "cohort"
    if n is None:
        n_from = ""
    sd, sd_from = first(stats.get("sd", [])), "sd"
    if sd is None and stats.get("sem") and n and technique not in POOLED_MEANS:
        sd, sd_from = stats["sem"][0] * math.sqrt(n), "sem x root n"
    if sd is None and stats.get("variance"):
        sd, sd_from = math.sqrt(stats["variance"][0]), "root of variance"
    if sd is None:
        sd_from = ""
    return {"mean": mean, "sd": sd, "n": n, "sd_from": sd_from, "n_from": n_from}


def merge_sides(found, mirrored=False):
    """found: {side: series}. One series for the measure: a plain side as it is, else the mean of
    a right and a left, the left's sign reversed first where the paper prints the sides mirrored."""
    for side in PLAIN_SIDES:
        if side in found:
            return side, found[side]
    if "right" in found and "left" in found:
        r, l = found["right"], found["left"]
        if mirrored:
            l = dict(l, mean=-l["mean"])
        sd = (r["sd"] + l["sd"]) / 2 if r["sd"] is not None and l["sd"] is not None else None
        n = min(x for x in (r["n"], l["n"]) if x) if (r["n"] or l["n"]) else None
        return "averaged", dict(r, mean=(r["mean"] + l["mean"]) / 2, sd=sd, n=n,
                                sd_from=r["sd_from"] if sd is not None else "")
    side = sorted(found)[0]
    return side, found[side]


def pool_sexes(m, f):
    """A male and a female series with counts and SDs pooled into one, the SD taking in the
    difference between the means."""
    n = m["n"] + f["n"]
    mean = (m["n"] * m["mean"] + f["n"] * f["mean"]) / n
    within = (m["n"] - 1) * m["sd"] ** 2 + (f["n"] - 1) * f["sd"] ** 2
    between = m["n"] * f["n"] / n * (m["mean"] - f["mean"]) ** 2
    return dict(m, mean=mean, sd=math.sqrt((within + between) / (n - 1)), n=n,
                sd_from="pooled from the sexes", n_from="sum of the sexes")


def poolable(s):
    return s is not None and s["n"] and s["n"] > 1 and s["sd"] is not None


def build(rows, people):
    cells, meta = gather(rows)
    by_measure, by_group = printed_counts(rows)
    sides = collections.defaultdict(dict)
    for k, stats in cells.items():
        s = one_series(k, stats, people, by_measure, by_group)
        if s is not None:
            s.update(meta[k])
            sides[k[:8]][k[8]] = s
    sexes = collections.defaultdict(dict)
    for k, found in sides.items():
        side, s = merge_sides(found, (k[0], k[4]) in MIRRORED_LEFT)
        sexes[k[:6] + k[7:8]][k[6]] = (side, s)
    out = []
    for k, found in sexes.items():
        paper, cohort, technique, source, key, level, group = k
        plain = [x for x in ("all", "not stated", "") if x in found]
        if plain:
            picks = [(plain[0], found[plain[0]])]
        elif "male" in found and "female" in found and poolable(found["male"][1]) and poolable(found["female"][1]):
            side = found["male"][0] if found["male"][0] == found["female"][0] else "mixed"
            picks = [("pooled", (side, pool_sexes(found["male"][1], found["female"][1])))]
        else:
            picks = sorted(found.items())
        for sex, (side, s) in picks:
            out.append({"paper": paper, "cohort": cohort, "technique": technique, "source_of_values": source,
                        "key": key, "level": level, "sex": sex, "group": group, "side": side,
                        "mean": s["mean"], "sd": s["sd"], "n": s["n"], "sd_from": s["sd_from"], "n_from": s["n_from"],
                        "units": s["units"], "vs_panjabi": s["vs_panjabi"], "definition": s["definition"],
                        "tables": "; ".join(sorted(s["tables"])), "pages": "; ".join(sorted(s["pages"], key=int))})
    return sorted(out, key=lambda r: tuple(str(r[c]) for c in COLUMNS[:9]))


def fmt(value):
    if value is None:
        return ""
    if isinstance(value, float):
        return "%.6g" % value
    return str(value)


def main():
    mapped, cohorts, out_path = sys.argv[1:4]
    series = build(read_mapped(mapped), cohort_people(cohorts))
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLUMNS)
        for s in series:
            w.writerow([fmt(s[c]) for c in COLUMNS])
    print("%d series from %s" % (len(series), mapped))


if __name__ == "__main__":
    main()
