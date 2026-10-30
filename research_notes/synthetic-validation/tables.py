"""The README's tables, written from the records run.py wrote.

    python3 -I tables.py --records records --write README.md    # rewrite every marked table
    python3 -I tables.py --records records --check README.md    # fail when one differs

A table sits in README.md between `<!-- table NAME -->` and `<!-- end NAME -->`; each NAME is
one function below. The prose around the tables quotes their numbers and is checked by hand; the
tables themselves are never typed.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
from typing import Callable, Dict, List, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = ("generator", "size_removed", "nearest the papers")
LUMBAR = ("L1", "L2", "L3", "L4", "L5")


def read_csv(records: str, name: str) -> List[dict]:
    with open(os.path.join(records, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def read_json(records: str, name: str):
    with open(os.path.join(records, name), encoding="utf-8") as fh:
        return json.load(fh)


def num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def f(x, digits: int = 2) -> str:
    x = num(x)
    return "-" if not math.isfinite(x) else "%.*f" % (digits, x)


def pct(x, digits: int = 1) -> str:
    x = num(x)
    return "-" if not math.isfinite(x) else "%.*f" % (digits, 100 * x)


def pct_fine(x, digits: int = 1) -> str:
    """pct, with the digits a small share needs to show as more than nothing."""
    x = num(x)
    if math.isfinite(x) and 0 < 100 * x < 10 ** -digits:
        digits = 1 - math.floor(math.log10(100 * x))
    return pct(x, digits)


def span(low, high, digits: int = 2) -> str:
    """'low to high', or the one value where the two are the same."""
    a, b = f(low, digits), f(high, digits)
    return a if a == b else "%s to %s" % (a, b)


def median(xs: Sequence[float]) -> float:
    xs = sorted(x for x in xs if math.isfinite(x))
    if not xs:
        return float("nan")
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2


def table(head: Sequence[str], rows: Sequence[Sequence[str]], right: int = 1, text: Sequence[int] = ()) -> str:
    """A Markdown table, the first `right` columns and those named in `text` left-aligned, the rest right-aligned.
    A cell holding a bar is refused, since GitHub would read it as a column's edge and drop the table."""
    left = set(range(right)) | set(text)
    for c in list(head) + [c for r in rows for c in r]:
        if "|" in str(c):
            raise ValueError("a table cell holds a bar: %r" % c)
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(" --- " if i in left else " ---: " for i in range(len(head))) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


# ----- the tables ------------------------------------------------------------------------------

MODALITY = {"bone": "bone", "ct": "CT", "mri": "MRI", "film": "film"}


def t_selection(rec: str) -> str:
    s = read_json(rec, "selection.json")
    rows = [["rows of the 32 measures in the snapshot", s["rows"]], ["series formed", s["series"]],
            ["series with a mean, an SD and a count of two or more", s["usable"]]]
    rows += [["  of them %s" % MODALITY.get(k, k), v] for k, v in sorted(s["usable_by_modality"].items())]
    rows += [["  of them with a count this note sets from the cohort file or the paper (%s)" % "; ".join(
        "%s %d" % (k, v) for k, v in sorted(s["n_notes"].items())), s["n_from_cohort"]],
             ["  of them with Tan's uncertain SDs (weighting the means, left out of the published SD)", s["sd_uncertain"]],
             ["  of them one sex only", s["one_sex_only"]], ["papers behind the usable series", s["papers"]]]
    kept = {k: v for k, v in s["left_out"].items() if k.startswith("kept ")}
    rows += [["series %s (no row left out)" % k, v] for k, v in sorted(kept.items())]
    rows += [["rows left out: %s" % k, v] for k, v in sorted(s["left_out"].items(), key=lambda kv: (-kv[1], kv[0]))
             if k not in kept]
    return table(["what", "count"], rows)


def t_means(rec: str) -> str:
    vs = read_json(rec, "validation_summary.json")
    p, nt = vs["panjabi"], vs["panjabi_without_tan2004"]
    def per_k(x):
        return ", ".join("%s: %d" % (k, v) for k, v in sorted(x["series_per_pooled_cell"].items(), key=lambda kv: int(kv[0])))
    rows = [["cells (measure, level) with a bone or CT series", p["cells"], nt["cells"]],
            ["  of them on Tan 2004 alone", p["cells_only_tan2004"], "-"],
            ["  with three series or more, so pooled with an interval", p["pooled_cells"], nt["pooled_cells"]],
            ["    cells by the number of series behind them", per_k(p), per_k(nt)],
            ["  Panjabi's mean outside the 95% prediction interval", p["outside_prediction_interval"],
             nt["outside_prediction_interval"]],
            ["    of the cells with five series or more (%d; %d)" % (p["pooled_cells_k5"], nt["pooled_cells_k5"]),
             p["outside_prediction_interval_k5"], nt["outside_prediction_interval_k5"]],
            ["  Panjabi's mean differs from the pooled mean, his twelve spines' SE taken in: z / t(k - 1)",
             "%d / %d" % (p["outside_mean_z"], p["outside_mean_t"]), "%d / %d" % (nt["outside_mean_z"], nt["outside_mean_t"])],
            ["    of them with Panjabi's mean above", "%d / %d" % (p["outside_mean_z_above"], p["outside_mean_t_above"]),
             "%d / %d" % (nt["outside_mean_z_above"], nt["outside_mean_t_above"])],
            ["    his mean taken as exact, as a stricter reading would", "%d (%d above)" % (p["outside_mean_exact"],
             p["outside_mean_exact_above"]), "%d (%d above)" % (nt["outside_mean_exact"], nt["outside_mean_exact_above"])],
            ["Panjabi - papers in his SDs, median (all cells)", f(p["d_median"]), f(nt["d_median"])],
            ["  share of cells where he is above", pct(p["d_above"], 0) + "%", pct(nt["d_above"], 0) + "%"],
            ["  the same, absolute", f(p["abs_d_median"]), f(nt["abs_d_median"])],
            ["  share of cells more than one of his SDs away", pct(p["d_over_one"], 0) + "%", pct(nt["d_over_one"], 0) + "%"],
            ["  absolute, in the papers' SD (cells with one)", f(p["abs_d_papers_sd_median"]), f(nt["abs_d_papers_sd_median"])],
            ["cells with a published SD: pooled from two series or more / one series / none (Tan's alone)",
             "%d / %d / %d" % (p["sd_cells_pooled"], p["sd_cells_one_series"], p["sd_cells_none"]),
             "%d / %d / %d" % (nt["sd_cells_pooled"], nt["sd_cells_one_series"], nt["sd_cells_none"])],
            ["Panjabi's SD over the papers' SD, quartiles (%d cells; %d)" % (p["sd_ratio_cells"], nt["sd_ratio_cells"]),
             " / ".join(f(x) for x in p["sd_ratio_quartiles"]), " / ".join(f(x) for x in nt["sd_ratio_quartiles"])]]
    t1 = table(["Panjabi's means and SDs against the papers (bone and CT)", "all series", "without Tan 2004"], rows)
    rows = []
    for g in vs["by_setting"]:
        rows.append([g["setting"], g["which"], g["cells"], f(g["median_abs_d"]), pct(g["d_over_one"], 0),
                     "%s (%s to %s)" % (f(g["sd_ratio_median"]), f(g["sd_ratio_q1"]), f(g["sd_ratio_q3"])),
                     "%d of %d" % (round(g["sd_inside"] * g["with_sd_interval"]), g["with_sd_interval"])
                     if g["with_sd_interval"] else "-"])
    t2 = table(["synthetic population", "values", "cells", "absolute d of its mean, median (Panjabi's SDs)", "absolute d over 1 (%)",
                "its SD over the papers', median (quartiles)", "SD inside the papers' SD interval"], rows, right=2)
    kinds = vs["sd_ratio_by_kind"]
    cols = ["panjabi", "generator, true", "generator, measured", "nearest the papers, true", "nearest the papers, measured"]
    with_sd = sd_cells_by_kind(rec)
    t3 = table(["SD over the papers', median", "cells with a published SD", "Panjabi's", "generator, true", "measured",
                "nearest point, true", "measured"], [[k, with_sd[k]] + [f(v[c]) for c in cols] for k, v in kinds.items()])
    return t1 + "\n\n" + t2 + "\n\n" + t3


SPINEPS_7 = ("endplate", "endplate_depth", "endplate_lower", "endplate_lower_depth", "h_post", "canal_w", "canal_ap")


def sd_cells_by_kind(rec: str) -> Dict[str, int]:
    """The cells behind each median of run.sd_ratio_by_kind that hold a published SD: the record
    counts every cell of the kind, and a cell with no published SD gives no ratio. SPINEPS_7 is
    schwingcheck.measures.SPINEPS_7, spelt out so that tables.py reads the records alone."""
    cells = {(r["measure"], r["level"]): r for r in read_csv(rec, "validation_cells.csv")
             if r["modalities"] == "bone_ct" and r["setting"] == "generator" and r["which"] == "true"}
    has_sd = [r for r in cells.values() if math.isfinite(num(r["lit_sd"]))]
    return {"lengths and areas": sum(1 for r in has_sd if r["kind"] in ("length", "area")),
            "angles": sum(1 for r in has_sd if r["kind"] == "angle"),
            "the seven SPINEPS measures": sum(1 for r in has_sd if r["measure"] in SPINEPS_7)}


def t_by_measure(rec: str) -> str:
    cells = [r for r in read_csv(rec, "validation_cells.csv") if r["modalities"] == "bone_ct" and r["which"] == "measured"]
    no_tan = read_json(rec, "validation_summary.json")["panjabi_by_measure"]
    measures = sorted({r["measure"] for r in cells}, key=lambda m: (-sum(1 for r in cells if r["measure"] == m), m))
    out = []
    for m in measures:
        gen = [r for r in cells if r["measure"] == m and r["setting"] == "generator"]
        d = [num(r["d_panjabi"]) for r in gen]
        nt = no_tan.get(m, {})
        row = [m, len(gen), sum(1 for r in gen if int(r["k"]) >= 3), sum(1 for r in gen if math.isfinite(num(r["lit_sd"]))),
               f(median(d)), f(median([abs(x) for x in d])),
               "%s (%d)" % (f(nt.get("d_median_without_tan2004")), nt.get("cells_without_tan2004", 0))]
        row.append(f(median([num(r["panjabi_sd_ratio"]) for r in gen])))
        for s in SETTINGS:
            row.append(f(median([num(r["sd_ratio"]) for r in cells if r["measure"] == m and r["setting"] == s])))
        out.append(row)
    return table(["measure", "cells", "pooled (3 series or more)", "with a published SD", "Panjabi - papers (his SDs)",
                  "same, absolute", "Panjabi - papers, Tan left out (cells)", "Panjabi's SD over the papers'",
                  "measured SD over the papers': generator",
                  "size taken out", "nearest point"], out)


def t_structure(rec: str) -> str:
    st = read_json(rec, "structure.json")
    rows = []
    for g in st["griffith"]:
        r = {s: next(x for x in st["correlations"][s] if x["pair"] == g["pair"])["synthetic"] for s in SETTINGS}
        rows.append([g["pair"].replace("_", " "), f(g["men"]), f(g["women"]), f(g["sexes_together"])]
                    + [f(r[s]) for s in SETTINGS])
    t1 = table(["correlation of subject means, L1-L5", "Griffith, men", "women", "sexes together", "generator",
                "size taken out", "nearest point"], rows)
    iso = [[r["measure"], r["cells"], r["equal_means"], f(r["loading"]),
            "%s to %s" % (f(r["q1"] / r["body_unit"]), f(r["q3"] / r["body_unit"])), f(r["generator_loading"], 0),
            r["papers"]] for r in st["isometry"]]
    t2 = table(["measure", "cells", "printed equal", "share of the body's sex difference", "quartiles", "generator",
                "papers (cells)"], iso, text=(6,))
    unit = st["isometry"][0]
    names = {"endplate": "upper end-plate width", "endplate_depth": "upper end-plate depth", "h_post": "posterior height"}
    measures = [names.get(k, k) for k in unit["body_unit_measures"].split(";") if k]
    return t1 + "\n\n" + t2 + "\n\nThe body's unit, log(men/women) = %s, is the median over the pairs of the %s (%s)," \
        " one population's; the rows for those measures are the unit itself." % (
            f(unit["body_unit"], 3), " and the ".join(measures), unit["body_unit_papers"])


QI_COLUMNS = ("sign", "inside", "sign or inside", "box", "convex", "any but floor", "floor", "any")


def t_quality(rec: str) -> str:
    qi = read_json(rec, "qi.json")
    rows = []
    for t in qi["typical"]:
        rows.append(["%s, %s" % (t["setting"], "all 32 measures" if t["measures"] == "pool" else "the seven SPINEPS measures")]
                    + ["%s / %s" % (pct_fine(t["vertebra " + k]), pct_fine(t["person " + k], 0))
                       for k in QI_COLUMNS])
    t1 = table(["setting (% of vertebrae / % of people)"] + list(QI_COLUMNS), rows)
    cur = [[s, c["kept"], c["dropped"], c["sign"], c["inside"]] for s, c in qi["curation"].items()]
    t2 = table(["setting", "people kept", "dropped", "for sign", "for inside"], cur)
    return t1 + "\n\n" + t2


def t_state_space(rec: str) -> str:
    rows = []
    for r in read_csv(rec, "state_space.csv"):
        g = [num(r[k]) for k in r if k.startswith("griffith ")]
        held = "%s (%s)" % (r["clipped"], r["clipped_size_passes"]) if r["clipped"] != "0" else "0"
        rows.append([r["name"], f(r["sd_ratio_true"]), f(r["sd_ratio_measured"]), f(r["neighbour_r"]), f(sum(g) / len(g)),
                     pct_fine(r["qi vertebra sign or inside"]), pct(r["qi vertebra any but floor"]),
                     pct(r["qi person any but floor"], 0), held])
    return table(["point", "SD ratio, true", "SD ratio, measured", "neighbour r", "mean Griffith-pair r",
                  "sign or inside (% vertebrae)", "any but floor (% vertebrae)", "any but floor (% people)",
                  "cells held at a tenth of the SD (the size alone passing it)"], rows)


def and_join(items: List[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def t_grid(rec: str) -> str:
    grid = read_csv(rec, "grid.csv")
    rows = []
    for r in grid[:8]:
        rows.append([f(r["scale_sd"], 3), f(r["sd_scale"]), f(r["rho"]), f(r["r_between"]), f(r["sd_ratio_true"]),
                     f(r["neighbour_r"]), pct(r["qi vertebra any"]), f(r["distance"], 3)])
    edges = read_csv(rec, "grid_edges.csv")
    best = grid[0]
    on_edge = sorted({e["axis"] for e in edges}, key=list(best).index)
    note = "%d points searched; the eight nearest shown." % len(grid)
    if edges:
        note += (" The nearest sits on the grid's edge in %s; past it, with the other axes held, %s." % (
            and_join(["%s (%s)" % (a, f(best[a], 3 if a == "scale_sd" else 2)) for a in on_edge]),
            ", ".join("%s %s reads %s" % (e["axis"], f(e[e["axis"]], 3 if e["axis"] == "scale_sd" else 2),
                                           f(e["distance"], 3)) for e in edges)))
    return table(["scale_sd", "sd_scale", "rho", "r_between", "SD ratio, true", "neighbour r", "any (% vertebrae)",
                  "distance"], rows, right=0) + "\n\n" + note


def t_naming(rec: str) -> str:
    rows = read_csv(rec, "naming.csv")
    settings = []
    for r in rows:
        if r["setting"] not in settings:
            settings.append(r["setting"])
    out = []
    for s in settings:
        line = [s]
        for rule in ("generator's rule", "rule matched"):
            for w in ("1", "3", "9"):
                got = [r for r in rows if r["setting"] == s and r["rule"] == rule and r["width"] == w]
                line.append(pct(got[0]["exact"]) if got else "")
        out.append(line)
    return table(["point", "1 body", "3", "9", "rule matched: 1", "3", "9"], out)


def t_spread(rec: str) -> str:
    pw = read_json(rec, "power.json")
    rows = [["part B before (Panjabi's comparison tables)", pw["old_part_b"]["cells"], f(pw["old_part_b"]["median_f"]),
             "", "", "", "", ""]]
    for name, s in pw["spread"].items():
        a, cal = s["all"], pw["calibrated_median_f"][name]
        rows.append(["39 papers, %s" % name, a["f_panjabi"]["cells"],
                     "%s (%s to %s)" % (f(a["f_panjabi"]["median"]), f(a["f_panjabi"]["q1"]), f(a["f_panjabi"]["q3"])),
                     f(cal["panjabi"]["calibrated_median"]), f(a["f_literature"]["median"]),
                     f(cal["literature"]["calibrated_median"]),
                     "%s (%s)" % (f(cal["literature"]["worth_scans_observed"], 1),
                                  f(cal["literature"]["worth_scans_at_calibrated"], 1)),
                     "%s (%s)" % (f(cal["panjabi"]["worth_scans_observed"], 1),
                                  f(cal["panjabi"]["worth_scans_at_calibrated"], 1))])
    t1 = table(["spread between series", "cells", "tau / Panjabi's SD, median (quartiles)", "calibrated",
                "tau / papers' SD", "calibrated", "worth in scans, the papers' SD (calibrated)",
                "the same, Panjabi's SD (calibrated)"], rows)
    sp = [[k, v["series_measures"], v["distances"], "%s (%s)" % (f(v["shift_sd"]), f(v["shift_sd_calibrated"])),
           "%s (%s)" % (f(v["level_sd"]), f(v["level_sd_calibrated"])), "%s (%s)" % (f(v["total"]), f(v["total_calibrated"]))]
          for k, v in pw["split"].items()]
    t2 = table(["split of the spread", "series x measure", "distances", "shift, whole measure (calibrated)",
                "level by level (calibrated)", "total (calibrated)"], sp)
    rc = pw["split_recovery"]
    m, se, one = rc["mean"], rc["standard_error"], rc["sd_of_one_estimate"]
    check = ("Drawn with a shift of %s and a rest of %s, %d sets of series laid out as the papers' give the moments"
             " %s and %s and the calibrated pair %s (SE of the mean %s) and %s (SE %s); one set's calibrated pair, as"
             " the papers' is, varies by an SD of %s and %s." % (
                 f(rc["truth"]["shift_sd"]), f(rc["truth"]["level_sd"]), rc["trials"], f(m["shift_sd"]), f(m["level_sd"]),
                 f(m["shift_sd_calibrated"]), f(se["shift_sd_calibrated"], 3), f(m["level_sd_calibrated"]),
                 f(se["level_sd_calibrated"], 3), f(one["shift_sd_calibrated"], 3), f(one["level_sd_calibrated"], 3)))
    return t1 + "\n\n" + t2 + "\n\n" + check


def t_part_c(rec: str) -> str:
    rows = read_csv(rec, "power_naming.csv")
    arms = []
    for r in rows:
        if r["arm"] not in arms:
            arms.append(r["arm"])
    out = []
    for a in arms:
        line = [a, "%s / %s" % (f(next(r for r in rows if r["arm"] == a)["shift"]), f(next(r for r in rows if r["arm"] == a)["level"]))]
        for w in ("1", "3", "9"):
            got = [r for r in rows if r["arm"] == a and r["width"] == w]
            exact = sum(num(r["exact"]) for r in got) / len(got)
            loss = sum(num(r["loss"]) for r in got) / len(got)
            prec = [num(r["precision"]) for r in got if math.isfinite(num(r["precision"]))]
            line.append("%s (%s; %s)" % (pct(exact), f(loss, 1), pct(sum(prec) / len(prec)) if prec else "-"))
        out.append(line)
    return table(["the rule's table", "shift / level (SD)", "1 body: exact (loss; right at 0.99)", "3 bodies", "9 bodies"],
                 out) + ("\n\nEach moved row is the mean over %d tables of the same %s columns; the own-table row is the"
                         " one table itself." % (max(int(num(r["table"])) for r in rows) + 1, rows[0]["columns"]))


def t_gold(rec: str) -> str:
    gold = read_json(rec, "power.json")["gold"]
    keep = [g for g in gold if g["persons"] in (17, 142, 159, 300, 1000)]
    order = [p["state"] for p in read_json(rec, "references.json")["prevalence"]]
    keys = sorted((k for k in gold[0] if k.startswith("expected: ")), key=lambda k: order.index(k[len("expected: "):]))
    rows = [[g["persons"], f(g["least_mean_shift_one_cell"]), f(g["least_mean_shift_154_cells"]), f(g["least_sd_ratio"]),
             f(g["neighbour_r_half_width"])] + [f(g[k], 1) for k in keys] for g in keep]
    t1 = table(["persons", "least mean shift found, one cell (SD)", "one cell of 154, Bonferroni (SD)",
                "least SD ratio found", "half-width of a neighbour r of 0.5"]
               + [k.replace("expected: ", "").split(" (")[0] for k in keys], rows, right=0)
    rows = [[g["persons"], f(g["least_mean_shift_one_cell"]), f(g["against_panjabi_12_least_mean_shift"]),
             f(g["least_sd_ratio"]), f(g["against_panjabi_12_least_sd_ratio"])] for g in keep]
    t2 = table(["persons", "least mean shift: the table exact (SD)", "against Panjabi's 12 as a sample, Welch (SD)",
                "least SD ratio: the table exact", "against his 12, F"], rows, right=0)
    return t1 + "\n\n" + t2 + ("\n\nIn the second table Panjabi's SD is %s times the gold persons', the papers' median"
                               " (records/power.json)." % f(read_json(rec, "power.json")["panjabi_sd_ratio"]))


def t_assumptions(rec: str) -> str:
    ref = read_json(rec, "references.json")
    rows = [[e["what"], e["modality"], "%s %s" % (span(e["low"], e["high"]), e["unit"]), e["source"]] for e in ref["errors"]]
    t1 = table(["error of one reading", "modality", "range", "source"], rows, right=2, text=(3,))
    ge = {}
    for g in ref["generator_errors"]:
        ge.setdefault(g["kind"], []).append(g)
    rows = [[k, len(v), span(min(x["error"] for x in v), max(x["error"] for x in v)),
             f(median([x["error_over_sd_l3"] for x in v]))] for k, v in sorted(ge.items())]
    t2 = table(["the generator's error, by kind", "measures", "error", "median error / SD at L3"], rows)
    rows = [[p["state"], pct(p["generator_share"]) if p["generator_share"] is not None else "-",
             pct(p["chain_weight"]) if p["chain_weight"] is not None else "-",
             "%s (%s to %s)" % (pct(p["papers"], 2), pct(p["low"], 2), pct(p["high"], 2)) if p["papers"] is not None else "no count",
             p["source"]] for p in ref["prevalence"]]
    t3 = table(["state", "model.py (%)", "chain (%)", "papers (%)", "source"], rows, text=(4,))
    return "\n\n".join((t1, t2, t3))


def t_tan(rec: str) -> str:
    """Tan 2004 apart from the rest (synthval/tan.py; records/tan-strata, written by tan_strata.py): the
    spread, the rule's loss by arm and the prediction for one more population."""
    ts = read_json(os.path.join(rec, "tan-strata"), "tan_strata.json")
    rows = []
    for group, label in (("all", "every matched cell"), ("seven", "the seven's cells")):
        g = ts["matched_spread"][group]
        d = g["tan_distance_panjabi_sd"]
        rows.append([label, g["f_panjabi_pooled"]["cells"],
                     "%s to %s" % (f(g["f_panjabi_pooled"]["median"]), f(g["f_panjabi_apart"]["median"])),
                     "%s to %s" % (f(g["f_literature_pooled"]["median"]), f(g["f_literature_apart"]["median"])),
                     "%s to %s" % (f(g["worth_scans_pooled"]["median"], 1), f(g["worth_scans_apart"]["median"], 1)),
                     f(g["variance_ratio_pooled_over_apart"]["median"]),
                     "%s (%s to %s)" % (f(d["median"]), f(d["q1"]), f(d["q3"])), g["tan_above_rest"]])
    t1 = table(["spread between populations, Tan pooled in to Tan apart", "cells", "tau / Panjabi's SD, median",
                "tau / papers' SD, median", "worth in scans, the papers' SD", "variance pooled / apart, median",
                "Tan's distance from the rest (Panjabi's SD), median (quartiles)", "cells with Tan above"], rows)
    sp = ts["split"]
    split = ("The calibrated split of the spread is a shift of %s and a rest of %s with Tan pooled in (%d series by"
             " measure, %d distances), %s and %s for the rest alone (%d, %d)." % (
                 f(sp["pooled"]["shift_sd_calibrated"]), f(sp["pooled"]["level_sd_calibrated"]), sp["pooled"]["series_measures"],
                 sp["pooled"]["distances"], f(sp["rest"]["shift_sd_calibrated"]), f(sp["rest"]["level_sd_calibrated"]),
                 sp["rest"]["series_measures"], sp["rest"]["distances"]))
    out = []
    for arm in [r["arm"] for r in ts["naming"] if r["width"] == 1]:
        line = [arm]
        for w in (1, 3, 9):
            r = next(x for x in ts["naming"] if x["arm"] == arm and x["width"] == w)
            line.append("%s (%s; %s)" % (pct(r["exact"]), f(r["loss_mean"], 1), pct(r["precision"])))
        line.append("%s / %s / %s" % tuple(f(next(x for x in ts["naming"] if x["arm"] == arm and x["width"] == w)
                                             ["loss_sd_between_tables"], 1) for w in (1, 3, 9)))
        out.append(line)
    t2 = table(["the rule's table", "1 body: exact (loss; right at 0.99)", "3 bodies", "9 bodies",
                "SD of the loss between tables, 1 / 3 / 9"], out)
    tables = max(r["tables"] for r in ts["naming"])
    paired = ", ".join("%s (SE %s) at %d" % (f(r["paired_difference_mean"], 1), f(r["paired_difference_se"], 1), r["width"])
                       for r in ts["naming"] if r["arm"] == "after: the rest without Tan")
    gold = ts["gold_against_tan"]
    found = next(g for g in gold if g["persons"] == 12)
    note = ("Each moved row is the mean over %d tables of the same %d columns, the before and after tables of one"
            " index drawn from the same standard draws; the rest's tables lose, paired with the pooled, %s bodies."
            " Tan's row is his one table (%s filled where he prints no value), and the own-table row is the"
            " generator's. Tan's median distance over the seven's %d matched cells is %s of Panjabi's SD; 12 persons"
            " find a shift of %s in one cell, so a population as far off as Tan's shows in %s%% of those cells from"
            " twelve gold persons." % (
                tables, ts["columns"], paired, " and ".join(ts["tan_table_filled"]) or "nothing", found["cells"],
                f(abs(found["tan_median_distance"])), f(found["least_mean_shift_one_cell"]),
                pct(found["share_of_seven_cells_found"], 0)))
    rows = []
    for group, label in (("all", "every matched cell"), ("seven", "the seven's cells")):
        g = ts["prediction"][group]
        rows.append([label, g["cells"],
                     "%s to %s" % (f(g["half_width_merged_sd"]["median"]), f(g["half_width_rest_sd"]["median"])),
                     "%s to %s" % (f(g["half_width_merged_plug_sd"]["median"]), f(g["half_width_rest_plug_sd"]["median"])),
                     f(g["half_width_mixture_sd"]["median"]), "%d / %d" % (g["tan_inside_rest"], g["tan_inside_rest_plug"]),
                     "%d in %d" % (g["series_held_out"], g["cells_held_out"]),
                     "%s / %s / %s" % (pct(g["coverage_merged"], 0), pct(g["coverage_rest"], 0), pct(g["coverage_mixture"], 0)),
                     "%s / %s" % (pct(g["coverage_merged_plug"], 0), pct(g["coverage_rest_plug"], 0))])
    t3 = table(["prediction for one more population, Tan pooled in to Tan apart", "cells",
                "half-width, t on k - 2 (Panjabi's SD), median", "the same, the spread taken as known (z)",
                "the two strata as a mixture, t", "cells with Tan inside the rest's, t / z", "series held out",
                "held-out series covered, t: merged / rest / mixture", "z: merged / rest"], rows)
    return t1 + "\n\n" + split + "\n\n" + t2 + "\n\n" + note + "\n\n" + t3


OTHER_VARIABLES = ("ancestry", "specimen", "region", "modality", "age_band", "decade")


def t_subgroups(rec: str) -> str:
    """The subgroup meta-analysis by every population variable (synthval/subgroups.py, the variables
    of synthval/register.py and data/populations.csv; records/subgroups, written by subgroups_run.py):
    the test and the share per variable, each paper and each value against the rest, the
    within-paper contrasts."""
    sg = read_json(os.path.join(rec, "subgroups"), "subgroups.json")
    rows = []
    for v, groups in sg["analysis"].items():
        g = groups["all"]
        rows.append([v, g["cells"], f(g["groups_per_cell"]["median"], 0), "%d of %d" % (g["cells_below_alpha"], g["cells_tested"]),
                     "%s (%d)" % (f(g["r2"]["median"]), g["r2"]["cells"]) if g["r2"]["cells"] else "none",
                     "%s to %s" % (f(g["f_total"]["median"]), f(g["f_within"]["median"])) if g["f_within"]["cells"] else f(g["f_total"]["median"]),
                     f(g["widest_gap_sd"]["median"])])
    t1 = table(["variable", "cells", "subgroups a cell, median", "cells whose test is below 0.05",
                "share of the spread it accounts for, median (cells read)",
                "spread, the whole cell to within the subgroups, median", "widest gap between subgroups, median (Panjabi's SD)"], rows)

    def against(items):
        out = []
        for name, s in sorted(items, key=lambda kv: kv[1]["all"]["distance_sd"]["median"]):
            g = s["all"]
            d = g["distance_sd"]
            out.append([name, g["cells"], g["series"], "%s (%s to %s)" % (f(d["median"]), f(d["q1"]), f(d["q3"])), g["above_rest"],
                        "%d / %d" % (g["inside_rest_t"], g["inside_rest_z"]), f(g["variance_ratio_pooled_over_apart"]["median"])])
        return out
    head = ["cells", "series", "distance from the rest's pooled mean (Panjabi's SD), median (quartiles)", "cells above",
            "cells inside the rest's interval, t / z", "variance pooled / apart, median"]
    t2 = table(["each paper against the rest"] + head, against(sg["against_rest"]["paper"].items()))
    t3 = table(["each value against the rest"] + head,
               against(("%s: %s" % (v, val), s) for v in OTHER_VARIABLES for val, s in sg["against_rest"][v].items()))
    rows = []
    for pair, s in sg["contrasts"].items():
        for group, label in (("all", "every cell"), ("seven", "the seven's")):
            g = s[group]
            if not g["cells"]:
                continue
            d = g["difference_sd"]
            rows.append([pair, label, g["cells"], f(g["pairs_per_cell"]["median"], 0),
                         "%s (%s to %s)" % (f(d["median"]), f(d["q1"]), f(d["q3"])), g["above_zero"], g["below_alpha"],
                         ", ".join(k for k in s if k not in ("all", "seven"))])
    t4 = table(["within-paper contrast", "over", "cells", "pairs a cell, median", "difference, median (quartiles), Panjabi's SD",
                "cells above zero", "cells below 0.05", "measures"], rows)
    contrasts = read_csv(os.path.join(rec, "subgroups"), "contrasts.csv")
    within = {}
    for r in contrasts:
        within.setdefault(r["pair"], set()).update(w.split("/")[0] for w in r["within"].split(";"))
    reg = sg["register"]
    note = ("The register holds %d cohorts, every one a usable series names; %d usable series under the main selection,"
            " %d with the strata apart (%d of them a sex printed apart). A value's row pools every cell where the value"
            " has a series and the rest hold three or more, and a value with fewer than %d such cells is left out. The"
            " contrasts come from %s." % (
                reg["cohorts"], reg["usable"], reg["apart_usable"], reg["sex_apart_series"], sg["least_cells"],
                "; ".join("%s from %s" % (pair, " and ".join(sorted(ws))) for pair, ws in sorted(within.items()))))
    return "\n\n".join((t1, t2, t3, t4, note))


TABLES: Dict[str, Callable[[str], str]] = {
    "selection": t_selection, "means": t_means, "by_measure": t_by_measure, "structure": t_structure,
    "quality": t_quality, "state_space": t_state_space, "grid": t_grid, "naming": t_naming, "spread": t_spread,
    "part_c": t_part_c, "gold": t_gold, "assumptions": t_assumptions, "tan": t_tan, "subgroups": t_subgroups}
MARK = re.compile(r"(<!-- table (\w+) -->\n)(.*?)(<!-- end \2 -->)", re.S)


def render(text: str, records: str) -> str:
    def one(m):
        if m.group(2) not in TABLES:
            raise SystemExit("README names a table %r that tables.py does not write" % m.group(2))
        return m.group(1) + TABLES[m.group(2)](records) + "\n" + m.group(4)
    return MARK.sub(one, text)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--records", default=os.path.join(HERE, "records"))
    ap.add_argument("--write")
    ap.add_argument("--check")
    ap.add_argument("--print", dest="show", action="store_true")
    args = ap.parse_args(argv)
    if args.show:
        for name, fn in TABLES.items():
            print("## %s\n\n%s\n" % (name, fn(args.records)))
    for path, write in ((args.write, True), (args.check, False)):
        if not path:
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        new = render(text, args.records)
        if write:
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(new)
        elif new != text:
            print("%s: a table differs from the records" % path)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
