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
    """A Markdown table, the first `right` columns and those named in `text` left-aligned, the rest right-aligned."""
    left = set(range(right)) | set(text)
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
    rows += [["  of them with the cohort's count of people", s["n_from_cohort"]],
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
            ["  Panjabi's mean outside the 95% CI of the pooled mean", p["outside_pooled_mean_ci"], nt["outside_pooled_mean_ci"]],
            ["    of them with Panjabi's mean above", p["outside_pooled_mean_ci_above"], nt["outside_pooled_mean_ci_above"]],
            ["median distance from the papers' mean, in Panjabi's SDs (all cells)", f(p["abs_d_median"]), f(nt["abs_d_median"])],
            ["  share of cells more than one of his SDs away", pct(p["d_over_one"], 0) + "%", pct(nt["d_over_one"], 0) + "%"],
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
    t2 = table(["synthetic population", "values", "cells", "|d| of its mean, median (Panjabi's SDs)", "|d| over 1 (%)",
                "its SD over the papers', median (quartiles)", "SD inside the papers' SD interval"], rows, right=2)
    return t1 + "\n\n" + t2


def t_by_measure(rec: str) -> str:
    cells = [r for r in read_csv(rec, "validation_cells.csv") if r["modalities"] == "bone_ct" and r["which"] == "measured"]
    measures = sorted({r["measure"] for r in cells}, key=lambda m: (-sum(1 for r in cells if r["measure"] == m), m))
    out = []
    for m in measures:
        gen = [r for r in cells if r["measure"] == m and r["setting"] == "generator"]
        d = [num(r["d_panjabi"]) for r in gen]
        row = [m, len(gen), sum(1 for r in gen if int(r["k"]) >= 3), sum(1 for r in gen if math.isfinite(num(r["lit_sd"]))),
               f(median(d)), f(median([abs(x) for x in d]))]
        row.append(f(median([num(r["panjabi_sd_ratio"]) for r in gen])))
        for s in SETTINGS:
            row.append(f(median([num(r["sd_ratio"]) for r in cells if r["measure"] == m and r["setting"] == s])))
        out.append(row)
    return table(["measure", "cells", "pooled (3 series or more)", "with a published SD", "Panjabi - papers (his SDs)",
                  "same, absolute", "Panjabi's SD over the papers'", "measured SD over the papers': generator",
                  "size taken out", "nearest point"], out)


def t_structure(rec: str) -> str:
    st = read_json(rec, "structure.json")
    rows = []
    for g in st["griffith"]:
        r = {s: next(x for x in st["correlations"][s] if x["pair"] == g["pair"])["synthetic"] for s in SETTINGS}
        rows.append([g["pair"].replace("_", " "), f(g["men"]), f(g["women"])] + [f(r[s]) for s in SETTINGS])
    t1 = table(["correlation of subject means, L1-L5", "Griffith, men", "women", "generator", "size taken out",
                "nearest point"], rows)
    iso = [[r["measure"], r["cells"], r["equal_means"], f(r["loading"]),
            "%s to %s" % (f(r["q1"] / r["body_unit"]), f(r["q3"] / r["body_unit"])), f(r["generator_loading"], 0),
            r["papers"]] for r in st["isometry"]]
    t2 = table(["measure", "cells", "printed equal", "share of the body's sex difference", "quartiles", "generator",
                "papers (cells)"], iso, text=(6,))
    unit = st["isometry"][0]
    return t1 + "\n\n" + t2 + "\n\nThe body's unit, log(men/women) = %s, is the median over the end-plate widths and depths" \
        " and the posterior heights (%s)." % (f(unit["body_unit"], 3), unit["body_unit_papers"])


def t_quality(rec: str) -> str:
    qi = read_json(rec, "qi.json")
    rows = []
    for t in qi["typical"]:
        rows.append(["%s, %s" % (t["setting"], "all 32 measures" if t["measures"] == "pool" else "the seven SPINEPS measures")]
                    + ["%s / %s" % (pct_fine(t["vertebra " + k]), pct_fine(t["person " + k], 0))
                       for k in ("sign", "floor", "box", "convex", "inside", "any")])
    t1 = table(["setting (% of vertebrae / % of people)", "sign", "floor", "box", "convex", "inside", "any"], rows)
    cur = [[s, c["kept"], c["dropped"], c["sign"], c["inside"]] for s, c in qi["curation"].items()]
    t2 = table(["setting", "people kept", "dropped", "for sign", "for inside"], cur)
    return t1 + "\n\n" + t2


def t_state_space(rec: str) -> str:
    rows = []
    for r in read_csv(rec, "state_space.csv"):
        g = [num(r[k]) for k in r if k.startswith("griffith ")]
        rows.append([r["name"], f(r["sd_ratio_true"]), f(r["sd_ratio_measured"]), f(r["neighbour_r"]), f(sum(g) / len(g)),
                     pct(r["qi vertebra box"]), pct(r["qi vertebra any"]), pct(r["qi person any"], 0), r["clipped"]])
    return table(["point", "SD ratio, true", "SD ratio, measured", "neighbour r", "mean Griffith-pair r",
                  "box (% vertebrae)", "any (% vertebrae)", "any (% people)", "cells held at a tenth of the SD"], rows)


def t_grid(rec: str) -> str:
    grid = read_csv(rec, "grid.csv")
    rows = []
    for r in grid[:8]:
        rows.append([f(r["scale_sd"], 3), f(r["sd_scale"]), f(r["rho"]), f(r["r_between"]), f(r["sd_ratio_true"]),
                     f(r["neighbour_r"]), pct(r["qi vertebra any"]), f(r["distance"], 3)])
    return table(["scale_sd", "sd_scale", "rho", "r_between", "SD ratio, true", "neighbour r", "any (% vertebrae)",
                  "distance"], rows, right=0) + "\n\n%d points searched; the eight nearest shown." % len(grid)


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
             "", "", "", ""]]
    for name, s in pw["spread"].items():
        a, cal = s["all"], pw["calibrated_median_f"][name]
        rows.append(["39 papers, %s" % name, a["f_panjabi"]["cells"],
                     "%s (%s to %s)" % (f(a["f_panjabi"]["median"]), f(a["f_panjabi"]["q1"]), f(a["f_panjabi"]["q3"])),
                     f(cal["panjabi"]["calibrated_median"]), f(a["f_literature"]["median"]),
                     f(cal["literature"]["calibrated_median"]),
                     "%s (%s)" % (f(a["worth_scans"]["median"], 1), f(cal["panjabi"]["worth_scans_at_calibrated"], 1))])
    t1 = table(["spread between series", "cells", "tau / Panjabi's SD, median (quartiles)", "calibrated",
                "tau / papers' SD", "calibrated", "worth in scans (at the calibrated median)"], rows)
    sp = [[k, v["series_measures"], v["distances"], "%s (%s)" % (f(v["shift_sd"]), f(v["shift_sd_calibrated"])),
           "%s (%s)" % (f(v["level_sd"]), f(v["level_sd_calibrated"])), "%s (%s)" % (f(v["total"]), f(v["total_calibrated"]))]
          for k, v in pw["split"].items()]
    t2 = table(["split of the spread", "series x measure", "distances", "shift, whole measure (calibrated)",
                "level by level (calibrated)", "total (calibrated)"], sp)
    rc = pw["split_recovery"]
    m, se = rc["mean"], rc["standard_error"]
    check = ("Drawn with a shift of %s and a rest of %s, %d sets of series laid out as the papers' give the moments"
             " %s and %s and the calibrated pair %s (SE %s) and %s (SE %s)." % (
                 f(rc["truth"]["shift_sd"]), f(rc["truth"]["level_sd"]), rc["trials"], f(m["shift_sd"]), f(m["level_sd"]),
                 f(m["shift_sd_calibrated"]), f(se["shift_sd_calibrated"], 3), f(m["level_sd_calibrated"]),
                 f(se["level_sd_calibrated"], 3)))
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
    return table(["persons", "least mean shift found, one cell (SD)", "one cell of 154, Bonferroni (SD)",
                  "least SD ratio found", "half-width of a neighbour r of 0.5"]
                 + [k.replace("expected: ", "").split(" (")[0] for k in keys], rows, right=0)


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


TABLES: Dict[str, Callable[[str], str]] = {
    "selection": t_selection, "means": t_means, "by_measure": t_by_measure, "structure": t_structure,
    "quality": t_quality, "state_space": t_state_space, "grid": t_grid, "naming": t_naming, "spread": t_spread,
    "part_c": t_part_c, "gold": t_gold, "assumptions": t_assumptions}
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
