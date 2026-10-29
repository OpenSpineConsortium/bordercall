"""Join our heights on VerSe's masks with the readers' Genant grades (Riedel's reference table)
and write the aggregates: per grade the spread of each height and ratio, how well the smaller
ratio finds a fracture (ROC AUC, with a bootstrap over patients), what Genant's 0.80 cut gives,
the agreement of the grade the ratio implies with the readers', and why a graded vertebra had
no reading.

    python -I verse_genant.py ROWS.csv GRADES.csv SERIES.json OUT.jsonl OUTDIR

Rules fixed before the join was looked at:
- A grade is a cell of the table holding 0, 1, 2 or 3; a cell holding anything else (the table
  holds 5 and 8, which Genant's scale does not have and the table does not define) is no grade,
  counted and left out.
- A vertebra is a patient's level: where two series of one patient are graded at one level, the
  reading taken is the series where more ratios read, then the one whose mask holds more of the
  level's voxels, then the lower series id; the other is counted as a duplicate.
- The smaller ratio is the least of body_index_ant_post and body_index_mid_post that read; a
  vertebra where neither reads has no reading, and the reason is the level's own flags.
- A lower ratio means a fracture. The AUC counts a tie as half. Genant's cut: a vertebra whose
  smaller ratio is under 0.80 is called fractured. The grade the ratio implies is 0 at 0.80 or
  more, 1 from 0.75, 2 from 0.60, 3 under 0.60 (Genant's 20, 25 and 40 per cent).
"""
import csv
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

MEASURES = ("h_ant", "h_mid", "h_post_inset", "body_index_ant_post", "body_index_mid_post")
RATIOS = ("body_index_ant_post", "body_index_mid_post")
GRADES = ("0", "1", "2", "3")
THORACIC = tuple("T%d" % i for i in range(1, 14))
GENANT_RANGE = tuple("T%d" % i for i in range(4, 13)) + ("L1", "L2", "L3", "L4")
BOOT = 2000
SEED = 20261029


def read_grades(path):
    rows = list(csv.reader(open(path, newline=""), delimiter=";"))
    head = [h.strip() for h in rows[0]]
    cells = []
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        for level, v in zip(head[1:], r[1:]):
            if v.strip():
                cells.append({"series": "verse" + r[0].strip(), "level": level, "code": v.strip()})
    return cells


def read_measures(path):
    """{(series, level): {key: value}}, {(series, level): [flag notes]}, {series: {study key: value}},
    {(series, level): {key: the note an unread measure carries}}, and the levels that have rows."""
    vals, flags, study, notes, seen = defaultdict(dict), defaultdict(list), defaultdict(dict), defaultdict(dict), {}
    for r in csv.DictReader(open(path, newline="")):
        s, lv, k = r["study"], r["level"], r["key"]
        if lv == "study":
            study[s][k] = r["value"] if r["value"] else r["note"]
            if k.startswith("flag"):
                flags[(s, "study")].append(r["note"])
            continue
        seen[(s, lv)] = True
        if k.startswith("flag"):
            flags[(s, lv)].append(r["note"])
        elif k in MEASURES and r["value"]:
            v = float(r["value"])
            if math.isfinite(v):
                vals[(s, lv)][k] = v
        elif k in MEASURES:
            notes[(s, lv)][k] = r["note"]
    return vals, flags, study, notes, seen


def why_unread(s, lv, study, held, seen, notes, flags):
    """Why neither ratio read: the ratio's own note, then its heights' notes; a level's other flags
    (pedicles, facets) are kept beside it in joined.csv but never taken for the reason."""
    if s not in study:
        return "series not measured"
    if lv not in held[s]["levels"]:
        return "level not in the mask"
    if (s, lv) not in seen:
        return "no row for the level" + ("; " + flags[(s, "study")][0] if flags.get((s, "study")) else "")
    for k in RATIOS + ("h_post_inset", "h_ant", "h_mid"):
        if notes[(s, lv)].get(k):
            return notes[(s, lv)][k]
    return "the heights did not read and the code left no note"


def smaller_ratio(v):
    got = [v[k] for k in RATIOS if k in v]
    return min(got) if got else None


def implied_grade(r):
    return 0 if r >= 0.80 else 1 if r >= 0.75 else 2 if r >= 0.60 else 3


def auc(neg, pos):
    """P(a fractured vertebra's ratio is below a sound one's), ties counted half."""
    neg, pos = np.asarray(neg, float), np.asarray(pos, float)
    if not len(neg) or not len(pos):
        return float("nan")
    allv = np.concatenate([pos, neg])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv))
    sv = allv[order]
    i = 0
    while i < len(sv):
        j = i
        while j + 1 < len(sv) and sv[j + 1] == sv[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1
        i = j + 1
    # rank of the negatives among all, high ratio = sound: AUC = P(neg ratio > pos ratio)
    r_neg = ranks[len(pos):].sum()
    return (r_neg - len(neg) * (len(neg) + 1) / 2) / (len(neg) * len(pos))


def boot_auc(items, positive):
    """95 per cent interval of the AUC by resampling patients with replacement."""
    by_patient = defaultdict(list)
    for it in items:
        by_patient[it["patient"]].append(it)
    pats = sorted(by_patient)
    rng = np.random.default_rng(SEED)
    out = []
    for _ in range(BOOT):
        pick = rng.integers(0, len(pats), len(pats))
        neg, pos = [], []
        for p in pick:
            for it in by_patient[pats[p]]:
                (pos if positive(it["grade"]) else neg).append(it["ratio"])
        a = auc(neg, pos)
        if math.isfinite(a):
            out.append(a)
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))] if out else [None, None]


def quartiles(xs):
    if not xs:
        return None
    q = np.percentile(xs, [25, 50, 75])
    return {"n": len(xs), "q1": round(float(q[0]), 4), "median": round(float(q[1]), 4), "q3": round(float(q[2]), 4)}


def weighted_kappa(a, b, k=4):
    m = np.zeros((k, k))
    for x, y in zip(a, b):
        m[x, y] += 1
    n = m.sum()
    w = np.array([[(i - j) ** 2 for j in range(k)] for i in range(k)], float) / (k - 1) ** 2
    exp = np.outer(m.sum(1), m.sum(0)) / n
    return float(1 - (w * m).sum() / (w * exp).sum()), m.astype(int).tolist()


def detect(items, label):
    neg = [it["ratio"] for it in items if it["grade"] == 0]
    pos1 = [it["ratio"] for it in items if it["grade"] >= 1]
    pos2 = [it["ratio"] for it in items if it["grade"] >= 2]
    sub2 = [it for it in items if it["grade"] != 1]
    below = lambda xs: sum(1 for x in xs if x < 0.80)
    rate = lambda k, n: round(k / n, 4) if n else None
    out = {"stratum": label, "vertebrae": len(items), "patients": len({it["patient"] for it in items}),
           "grade0": len(neg), "grade1plus": len(pos1), "grade2plus": len(pos2),
           "auc_grade1plus": round(auc(neg, pos1), 4) if pos1 and neg else None,
           "auc_grade2plus": round(auc(neg, pos2), 4) if pos2 and neg else None,
           "sens_grade1plus_at_0.80": rate(below(pos1), len(pos1)),
           "sens_grade2plus_at_0.80": rate(below(pos2), len(pos2)),
           "spec_at_0.80": rate(len(neg) - below(neg), len(neg)),
           "grade0_below_0.80": rate(below(neg), len(neg)),
           "grade0_below_0.80_count": below(neg)}
    if label == "all":
        out["auc_grade1plus_ci95"] = boot_auc(items, lambda g: g >= 1)
        out["auc_grade2plus_ci95"] = boot_auc(sub2, lambda g: g >= 2)
    return out


def main(rows_csv, grades_csv, series_json, out_jsonl, outdir):
    os.makedirs(outdir, exist_ok=True)
    cells = read_grades(grades_csv)
    patient = {x["series"]: x["patient"] for x in json.load(open(series_json))["series"]}
    held = {json.loads(l)["id"]: json.loads(l) for l in open(out_jsonl)}
    vals, flags, study, notes, seen = read_measures(rows_csv)

    counts = Counter()
    not_grades = Counter(c["code"] for c in cells if c["code"] not in GRADES)
    counts["cells"] = len(cells)
    counts["cells_not_a_grade"] = sum(not_grades.values())
    graded = [c for c in cells if c["code"] in GRADES]
    counts["cells_graded"] = len(graded)

    # one reading per patient's level
    groups = defaultdict(list)
    for c in graded:
        groups[(patient[c["series"]], c["level"])].append(c)
    joined, conflicts = [], []
    for (p, lv), cs in sorted(groups.items()):
        def key(c):
            v = vals.get((c["series"], lv), {})
            vox = held[c["series"]]["levels"].get(lv, {}).get("voxels", 0)
            return (-sum(1 for k in RATIOS if k in v), -vox, c["series"])
        cs = sorted(cs, key=key)
        if len({c["code"] for c in cs}) > 1:
            conflicts.append({"patient": p, "level": lv, "codes": [c["code"] for c in cs]})
        counts["duplicates_dropped"] += len(cs) - 1
        c = cs[0]
        s = c["series"]
        v = vals.get((s, lv), {})
        r = smaller_ratio(v)
        st = study.get(s, {})
        row = {"series": s, "patient": p, "level": lv, "grade": int(c["code"]),
               "region": "thoracic" if lv in THORACIC else "lumbar",
               "coarsest_mm": float(st["coarsest_mm"]) if st.get("coarsest_mm") else None,
               "slice_mm": float(st["slice_mm"]) if st.get("slice_mm") else None,
               "duplicate_series": [x["series"] for x in cs[1:]]}
        for k in MEASURES:
            row[k] = round(v[k], 4) if k in v else None
        row["smaller_ratio"] = round(r, 4) if r is not None else None
        row["ratios_read"] = sum(1 for k in RATIOS if k in v)
        if r is None:
            row["no_reading"] = [why_unread(s, lv, study, held, seen, notes, flags)] + flags.get((s, lv), [])
        joined.append(row)
    counts["vertebrae"] = len(joined)
    counts["conflicting_duplicates"] = len(conflicts)

    with open(os.path.join(outdir, "joined.csv"), "w", newline="") as f:
        fields = ["series", "patient", "level", "region", "grade"] + list(MEASURES) + [
            "smaller_ratio", "ratios_read", "coarsest_mm", "slice_mm", "duplicate_series", "no_reading"]
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for row in joined:
            w.writerow({**row, "duplicate_series": " ".join(row["duplicate_series"]),
                        "no_reading": " | ".join(row.get("no_reading", []))})

    read = [dict(row, ratio=row["smaller_ratio"]) for row in joined if row["smaller_ratio"] is not None]
    unread = [row for row in joined if row["smaller_ratio"] is None]
    agg = {"counts": dict(counts), "codes_not_a_grade": dict(not_grades), "conflicting_duplicates": conflicts}
    agg["per_grade"] = {}
    for g in range(4):
        rows_g = [row for row in joined if row["grade"] == g]
        agg["per_grade"][str(g)] = {
            "vertebrae": len(rows_g), "patients": len({row["patient"] for row in rows_g}),
            "read": sum(1 for row in rows_g if row["smaller_ratio"] is not None),
            **{k: quartiles([row[k] for row in rows_g if row[k] is not None]) for k in MEASURES + ("smaller_ratio",)}}
    strata = [("all", read),
              ("thoracic", [it for it in read if it["region"] == "thoracic"]),
              ("lumbar", [it for it in read if it["region"] == "lumbar"]),
              ("T4 to L4", [it for it in read if it["level"] in GENANT_RANGE]),
              ("coarsest at most 1.25 mm", [it for it in read if (it["coarsest_mm"] or 99) <= 1.25]),
              ("coarsest over 1.25 mm", [it for it in read if (it["coarsest_mm"] or 99) > 1.25]),
              ("both ratios read", [it for it in read if it["ratios_read"] == 2])]
    agg["detection"] = [detect(items, label) for label, items in strata]
    kappa, matrix = weighted_kappa([it["grade"] for it in read], [implied_grade(it["ratio"]) for it in read])
    agg["agreement"] = {"quadratic_weighted_kappa": round(kappa, 4),
                        "rows_readers_grade_cols_implied_grade": matrix,
                        "exact": round(sum(matrix[i][i] for i in range(4)) / len(read), 4)}
    why = Counter(row["no_reading"][0] for row in unread)
    agg["no_reading"] = {"vertebrae": len(unread),
                         "by_grade": dict(Counter(str(row["grade"]) for row in unread)),
                         "reasons": dict(why.most_common()),
                         "one_ratio_only": sum(1 for it in read if it["ratios_read"] == 1)}
    json.dump(agg, open(os.path.join(outdir, "aggregates.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps({k: agg[k] for k in ("counts", "codes_not_a_grade", "agreement", "no_reading")}, indent=1))
    for d in agg["detection"]:
        print(d)


if __name__ == "__main__":
    main(*sys.argv[1:6])
