"""The between-measure covariance: what is knowable, what is not, and how to stay honest.

    python run.py covariance --report          # what the literature can and cannot supply
    python run.py covariance --sweep           # accuracy as a function of the assumption

THE HIDDEN ASSUMPTION. `panjabi.py` draws a column as

    value = s * (mu + sd * (rho * z[m] + sqrt(1 - rho^2) * e[m][i])) + n[m][i]

with `draws["offset"] = {m: rng.normal() for m in measures}` -- one patient offset per
measure, drawn INDEPENDENTLY. Beyond the single size factor `s`, the generator therefore
assumes the measures are uncorrelated within a patient. That is not a neutral default. It is
the choice that makes a feature vector carry the most independent information, so a
classifier scored on these columns reads HIGH. Everything the synthetic study reports at
r = 0 is an UPPER BOUND, not an estimate.

WHAT PANJABI PUBLISHED, AND WHY IT CANNOT SUPPLY THE NUMBER. Each table gives a mean and a
standard error per measure per level. There is no correlation matrix, no paired scatter and
no specimen-level table in any of the three papers. The ratio rows look like they might carry
it -- EPWu/EPDu, SCW/SCD, PDHr/PDWr -- but they do not: a mean of per-specimen ratios would
encode the correlation, a ratio of means would not, and every published ratio reproduces
mean(a)/mean(b) to within rounding (largest residual 0.0044 on the lumbar rows, which are
printed to two decimals). They are ratios of means. Tested, not assumed:
`run.py covariance --report` reruns that check.

Two further reasons his data could not settle it even in principle. n = 12: a correlation
estimated from twelve specimens has a 95 % interval running from about 0.00 to 0.84 at
r = 0.5, which is no constraint on anything. And the specimens are embalmed cadaveric spines
measured with a morphometer, so a covariance from them would carry that preparation.

WHAT THE LINEAGE PUBLISHED, READ FROM THE PAPER RATHER THAN FROM AN ABSTRACT. Kunkel et al.
(J Anat 2010;216:320) take Panjabi's own 1991 and 1992 tables and regress each vertebral
parameter ON ANOTHER PARAMETER -- posterior vertebral body height, VBHp, chosen as the
predictor "based on the level of correlation with the other parameters and ease of
measurement on lateral X-rays". So this IS a published between-parameter relationship built
from Panjabi's data, which is the nearest thing in the literature to what is wanted here:

    EPWS, EPWI, EPDS, EPDI, VBW, VBD     R^2 0.970-0.982   (third-order polynomial)
    PHL, PHR, PTIL, SCW, SCD             R^2 0.693-0.964
    EPIS, EPII, PWL, PWR, PTIR, SPL, TPW R^2 0.514-0.693

AND IT STILL CANNOT SET r_between, for one reason that is easy to miss: "each data point
represents the mean value in different vertebral levels of 12 cadavers". The regression runs
over SIXTEEN LEVEL MEANS, T1-T12 and L1-L4, not over individuals. R^2 = 0.98 for EPWS on
VBHp says their CAUDAL PROFILES track each other down the column. It does not say that a
patient with a tall posterior body has a wide end-plate. Those are different quantities, and
reading the second from the first is the ecological fallacy: a correlation between group
means need not hold, in sign or size, within groups.

The generator already reproduces every one of those profile relationships exactly, because it
draws each level from that level's own published mean. Kunkel's R^2 is therefore already in
the model and adds nothing to r_between.

Searches of Panjabi's collaborators (Oxland, Goel, Crisco, Takata, Krag, White) found no
published within-patient between-measure covariance for vertebral morphometry either.

SO THE NUMBER DOES NOT EXIST, and inventing one would be the bias this package exists to
avoid. What replaces it is a sensitivity analysis: the result is reported as a function of
the assumption, with the value at which the conclusion changes named. An unmeasurable
nuisance parameter becomes a stated range rather than a hidden constant.

THE ONE OUTSIDE ANCHOR, used to place the sweep and not to pick an answer: 125 dry lumbar
vertebrae give Spearman rho = 0.800 between the anteroposterior and laterolateral diameters
of the vertebral body (BMC Musculoskelet Disord 2026). Dry bone, as Panjabi's was, but a
different cohort, method and continent, and not his lineage. It says the plausible range runs
to 0.8 for two dimensions of the same structure, not that 0.8 is the value here.

THE STRUCTURE SWEPT. One number r for every pair, the exchangeable form

    R = (1 - r) I + r 11'

which is a valid correlation matrix for r in [-1/(k-1), 1]. A full matrix would need k(k-1)/2
numbers and nothing supplies even one of them; one parameter that can be swept end to end is
the honest shape of the ignorance.
"""
from __future__ import annotations

import json
import math
import os
import sys
from typing import Dict, List, Optional, Sequence

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# the anchor, for placing the sweep only
# The r grid every sweep in this module runs on. 0.0 is the generator's own default and the
# optimistic end; 0.8 is where the one outside anchor sits; 0.9 is past it on purpose.
R_GRID = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9]

EXTERNAL = {"pair": "vertebral body AP vs LL diameter", "rho": 0.800, "n": 125,
            "material": "dry bone",
            "source": "BMC Musculoskelet Disord 2026, 125 dry lumbar vertebrae",
            "lineage": "not Panjabi's"}

# Panjabi's published ratio rows, to re-test the claim that they carry no covariance
RATIO_ROWS = [
    ("thoracic EPWu/EPDu",
     [24.5, 24.9, 24.6, 24.5, 24.9, 26.2, 27.8, 29.5, 30.6, 31.9, 34.9, 39.0],
     [18.5, 19.6, 22.7, 23.3, 24.3, 26.0, 27.4, 27.9, 29.3, 30.5, 31.9, 32.8],
     [1.3, 1.3, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.1, 1.2], 1),
    ("lumbar EPWu/EPDu", [41.2, 42.6, 44.1, 46.6, 47.3], [34.1, 34.6, 35.2, 35.5, 34.7],
     [1.21, 1.23, 1.25, 1.31, 1.36], 2),
    ("lumbar EPWl/EPDl", [43.3, 45.5, 48.0, 49.5, 49.4], [35.3, 34.9, 34.8, 33.9, 33.2],
     [1.23, 1.30, 1.38, 1.46, 1.49], 2),
    ("lumbar SCW/SCD", [23.7, 23.8, 24.3, 25.4, 27.1], [19.0, 18.2, 17.5, 18.6, 19.7],
     [1.25, 1.31, 1.39, 1.37, 1.38], 2),
]


def exchangeable(k: int, r: float) -> np.ndarray:
    """R = (1-r)I + r 11', the only shape one number can honestly describe."""
    lo = -1.0 / (k - 1) if k > 1 else -1.0
    if not (lo - 1e-12 <= r <= 1.0):
        raise SystemExit("r = %.3f is not a correlation for %d measures; "
                         "the exchangeable form needs %.4f <= r <= 1" % (r, k, lo))
    R = np.full((k, k), float(r))
    np.fill_diagonal(R, 1.0)
    return R


def offset_factor(k: int, r: float) -> np.ndarray:
    """Cholesky factor L with L L' = R, so L @ iid normals has the wanted correlation."""
    if abs(r) < 1e-12:
        return np.eye(k)
    R = exchangeable(k, r)
    # jitter only if the matrix sits exactly on the boundary and loses positive-definiteness
    try:
        return np.linalg.cholesky(R)
    except np.linalg.LinAlgError:
        return np.linalg.cholesky(R + 1e-10 * np.eye(k))


def correlated_offsets(rng, measures: Sequence[str], r: float) -> Dict[str, float]:
    """One patient offset per measure, correlated r with every other. r = 0 reproduces
    the independent draw exactly, so a run at r = 0 matches the recorded runs."""
    ms = list(measures)
    e = rng.normal(size=len(ms))
    if abs(r) < 1e-12:
        return {m: float(v) for m, v in zip(ms, e)}
    z = offset_factor(len(ms), r) @ e
    return {m: float(v) for m, v in zip(ms, z)}


def ratio_test(tol_per_dp=(0.05, 0.005)):
    """Do the published ratios encode a covariance? -> (verdict, rows).

    THE VERDICT RESTS ON THE TWO-DECIMAL ROWS ONLY. A ratio printed to one decimal
    discriminates nothing: mean(a)/mean(b) and a mean of per-specimen ratios differ by far
    less than 0.05 for quantities this strongly related, so a one-decimal row is consistent
    with both and is reported as uninformative rather than counted either way. The thoracic
    row is printed to one decimal and has one cell (T8, 29.5/27.9 = 1.057 against a printed
    1.0) outside even that; at this precision that is a rounding or typesetting question,
    not evidence of a covariance, and it is not allowed to carry the verdict.
    """
    rows = []
    for name, a, b, pub, dp in RATIO_ROWS:
        d = max(abs(x / y - p) for x, y, p in zip(a, b, pub))
        tol = tol_per_dp[0] if dp == 1 else tol_per_dp[1]
        rows.append((name, d, tol, d <= tol + 1e-9, dp))
    decisive = [r for r in rows if r[4] >= 2]
    return (bool(decisive) and all(r[3] for r in decisive)), rows


def report():
    print("CAN THE LITERATURE SUPPLY THE BETWEEN-MEASURE COVARIANCE?\n")
    print("1. Panjabi's own tables")
    ok, rows = ratio_test()
    print("   The ratio rows are the only place a covariance could hide. A mean of")
    print("   per-specimen ratios would carry it; a ratio of means would not.\n")
    print("   %-24s %4s %10s %10s  %s"
          % ("ratio row", "d.p.", "max resid", "rounding", "ratio of means?"))
    for name, d, tol, within, dp in rows:
        verdict = ("yes" if within else "NO") if dp >= 2 else "uninformative at 1 d.p."
        print("   %-24s %4d %10.4f %10.4f  %s" % (name, dp, d, tol, verdict))
    print("\n   verdict: %s" % ("the two-decimal rows are ratios of MEANS to within "
                                "0.0044, so the tables carry no covariance" if ok else
                                "a two-decimal row is NOT a ratio of means -- look again"))
    print("   Also: n = 12. At r = 0.5 the 95 % interval on a correlation runs about")
    print("   0.00 to 0.84, so his cohort could not constrain it even if the rows did")
    print("   carry it.")

    print("\n2. His lineage -- Kunkel, which looks like the answer and is not")
    print("   Kunkel et al. (J Anat 2010;216:320) fit prediction equations to Panjabi's")
    print("   1991/1992 thoracic and lumbar tables, and unlike the rest of the lineage")
    print("   they regress each parameter ON ANOTHER PARAMETER -- posterior vertebral")
    print("   body height, VBHp -- which is the shape of relation this study needs.")
    print("   R^2 reach 0.970-0.982 for the end-plate widths and depths, VBW and VBD;")
    print("   0.693-0.964 for pedicle heights, PTIL, SCW and SCD; 0.514-0.693 for the")
    print("   rest.")
    print("   Those coefficients cannot be used here. Their methods state that each data")
    print("   point is the MEAN value at one vertebral level across the 12 cadavers, so")
    print("   every fit runs over SIXTEEN LEVEL MEANS -- T1-T12 and L1-L4 -- not over")
    print("   individuals. An R^2 of 0.98 between level means says the two measures grow")
    print("   down the spine together, which the generator already reproduces by drawing")
    print("   each level from its own published mean. Reading a within-patient")
    print("   correlation out of it is the ecological fallacy, and an aggregate")
    print("   correlation is the one quantity guaranteed to be inflated relative to the")
    print("   individual one it would stand in for.")
    print("   No between-measure covariance over individuals was found for Oxland, Goel,")
    print("   Crisco, Takata, Krag or White either.")

    print("\n3. The one outside anchor, for placing the sweep only")
    print("   %s: rho = %.2f (n = %d, %s, %s lineage)."
          % (EXTERNAL["pair"], EXTERNAL["rho"], EXTERNAL["n"], EXTERNAL["material"],
             EXTERNAL["lineage"]))
    print("   Two dimensions of the SAME structure reach 0.8 on dry bone. That bounds")
    print("   where the sweep has to go; it is not this study's value.")

    print("\nCONCLUSION. The number does not exist and will not be invented. The result is")
    print("reported as a function of r, with the value at which the conclusion changes")
    print("named. r = 0, the generator's current default, is the OPTIMISTIC end: it gives")
    print("each measure the most independent information it could have, so every accuracy")
    print("recorded at r = 0 is an upper bound.")
    return 0


def binomial_se(p, n):
    return math.sqrt(max(p * (1 - p), 1e-12) / n) if n else float("nan")


def sweep(fn, r_values=None, label="accuracy"):
    """Run fn(r) -> (value, n) over a grid and report the curve and the breakdown point.

    fn must draw FRESH columns for each r; reusing one draw would make the curve a
    property of that draw.
    """
    r_values = list(r_values if r_values is not None else R_GRID)
    print("\n%-7s %10s %10s   %s" % ("r", label, "MC s.e.", "note"))
    out = []
    for r in r_values:
        v, n = fn(r)
        se = binomial_se(v, n)
        note = "generator's current default, OPTIMISTIC" if r == 0 else ""
        if abs(r - EXTERNAL["rho"]) < 1e-9:
            note = "the outside anchor's order"
        print("%-7.2f %10.4f %10.4f   %s" % (r, v, se, note))
        out.append({"r": r, "value": v, "n": n, "se": se})
    if len(out) >= 2:
        first, last = out[0]["value"], out[-1]["value"]
        print("\n  r = %.2f -> %.2f moves %s by %+.4f (%.1f MC s.e.)"
              % (out[0]["r"], out[-1]["r"], label, last - first,
                 abs(last - first) / max(out[0]["se"], 1e-9)))
        if abs(last - first) < 2 * max(out[0]["se"], 1e-12):
            print("  The whole sweep moves it by less than two Monte Carlo standard errors,")
            print("  so on this evidence the conclusion does not depend on the assumption.")
        else:
            print("  The assumption matters. Quote the range, not the r = 0 figure.")
    return out


# ---------------------------------------------------------------------------
# the measure-set sweep
# ---------------------------------------------------------------------------
# Every measure this package can take downstream of a SPINEPS segmentation. The pedicle
# measures are excluded on purpose: SPINEPS labels the whole neural arch as 41 and never
# isolates the pedicle, so PDW and PDH cannot be read off one. See SPINEPS_MAPPING.md.
SPINEPS_7 = ["endplate", "endplate_depth", "endplate_lower", "endplate_lower_depth",
             "h_post", "canal_w", "canal_ap"]
BASELINE_3 = ["endplate", "h_post", "canal_w"]

JUNCTIONS = {"ct": "cervico-thoracic C7/T1", "tl": "thoraco-lumbar T12/L1"}

# Selection and scoring use DIFFERENT seeds. The winner of a search over k measure subsets
# is optimistically biased if it is scored on the draw that chose it; synthetic columns are
# free, so there is no excuse for scoring on the selection draw.
FIT_SEED = 11
EVAL_SEED = 97


def _score(measures, r, fit_seed=FIT_SEED, eval_seed=EVAL_SEED,
           n_columns=600, n_eval=400):
    """Exact-placement rate over all phenotypes, at one r. Fresh columns at every call."""
    import junction as J
    import panjabi as P

    ref = P.load_reference(measures=measures)
    out = {}
    for key in JUNCTIONS:
        model = J.train(ref, key, measures=measures, n_columns=n_columns, seed=fit_seed,
                        rho=0.5, noise_mm=1.0, scale_sd=0.07, r_between=r)
        hits = tot = 0
        for ph in P.PHENOTYPES:
            s = J.evaluate(model, ref, ph, seed=eval_seed, n=n_eval,
                           rho=0.5, noise_mm=1.0, scale_sd=0.07, r_between=r)
            hits += s.exact
            tot += s.n
        out[key] = (hits / tot if tot else float("nan"), tot)
    return out


def measure_set_sweep(r_grid=None, out_json=None, n_columns=600, n_eval=400):
    """7 SPINEPS-measurable measures against 3, across the whole r grid. Synthetic only."""
    r_grid = list(R_GRID if r_grid is None else r_grid)
    print("SYNTHETIC ONLY. Columns are drawn from Panjabi's published means and spreads.")
    print("No cohort is read.\n")
    print("measures: %d SPINEPS-measurable (%s)" % (len(SPINEPS_7), ", ".join(SPINEPS_7)))
    print("excluded: pedicle width and height -- SPINEPS has no pedicle label\n")

    results = {"baseline_3": {}, "spineps_7": {}}
    for name, ms in (("baseline_3", BASELINE_3), ("spineps_7", SPINEPS_7)):
        print("=" * 72)
        print("%s  (%d measures)" % (name, len(ms)))
        for key, pretty in JUNCTIONS.items():
            print("\n  %s" % pretty)
            rows = []
            for r in r_grid:
                acc, n = _score(ms, r, n_columns=n_columns, n_eval=n_eval)[key]
                se = binomial_se(acc, n)
                note = "<- generator default, OPTIMISTIC" if r == 0 else (
                    "<- the outside anchor's order" if abs(r - EXTERNAL["rho"]) < 1e-9 else "")
                print("    r=%.2f  acc %.4f  MC s.e. %.4f  n=%d  %s"
                      % (r, acc, se, n, note))
                rows.append({"r": r, "acc": acc, "se": se, "n": n})
            results[name][key] = rows
            d = rows[-1]["acc"] - rows[0]["acc"]
            print("    r %.2f -> %.2f moves accuracy %+.4f (%.1f MC s.e.)"
                  % (rows[0]["r"], rows[-1]["r"], d, abs(d) / max(rows[0]["se"], 1e-9)))

    print("\n" + "=" * 72)
    print("7 MEASURES AGAINST 3, scored on columns neither fit saw")
    for key, pretty in JUNCTIONS.items():
        print("\n  %s" % pretty)
        for r in r_grid:
            a3 = [x for x in results["baseline_3"][key] if x["r"] == r][0]
            a7 = [x for x in results["spineps_7"][key] if x["r"] == r][0]
            d = a7["acc"] - a3["acc"]
            se = (a3["se"] ** 2 + a7["se"] ** 2) ** 0.5
            verdict = ("within noise" if abs(d) < 2 * se
                       else ("7 better" if d > 0 else "3 better"))
            print("    r=%.2f   3: %.4f   7: %.4f   diff %+.4f +/- %.4f   %s"
                  % (r, a3["acc"], a7["acc"], d, se, verdict))

    payload = {"grid": r_grid,
               "measures": {"spineps_7": SPINEPS_7, "baseline_3": BASELINE_3},
               "results": results,
               "design": {"fit_seed": FIT_SEED, "eval_seed": EVAL_SEED,
                          "n_columns": n_columns, "n_eval": n_eval,
                          "note": "selection and scoring use different seeds; "
                                  "synthetic columns only, no cohort is read"}}
    if out_json:
        os.makedirs(os.path.dirname(os.path.abspath(out_json)), exist_ok=True)
        with open(out_json, "w") as fh:
            json.dump(payload, fh, indent=2)
        print("\nwrote %s" % out_json)
    return payload
