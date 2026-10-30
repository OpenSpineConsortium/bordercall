"""Knowing the patient's sex while naming a short field: what the information is worth.

greg's words of 2026-10-30: "i think its total reasonable to expect to know the sex of the patient
you are imaging". So sex is an input the rule is given at inference, never something it predicts,
and the question is how much naming a field of one, two or three bodies at an unknown offset gains
when the rule reads the table of the person's own sex in place of the sexless table. Two readings,
each paired, the same simulated persons named by every rule on the same fields:

(a) Synthetic, the value of the information alone. A lumbar table of the selection (select.py's
    plain table: the papers pooled by random effects, the within-person SD) is split into two
    sexes, every cell's mean moved by +d/2 within-sex SDs for men and -d/2 for women, the within-sex
    SD sd / sqrt(1 + d^2/4), so that half men and half women keep the table's mean and SD at every
    cell. Persons are drawn half and half from the two tables by the generator's own model. Rule A
    reads the sexless table, as every rule of this note has; rule B reads the person's sex's table;
    both are the generator's exact rule otherwise (the size integrated out, the same errors and
    powers, temperature 1), so B minus A is what knowing the sex is worth and nothing else. A', the
    equal mixture of the two sexes' tables, is the exact rule that does not know the sex, so B minus
    A' is the information itself and A' minus A what a single Gaussian loses on a population that
    is a mixture. B minus A' is never below zero in log score in expectation over persons (it is
    the mutual information of the place and the sex given the field, the log score being proper);
    a finite draw's difference can fall below zero by chance, and its SE says how far. d is swept
    over D_GRID in two shapes: the same shift at every cell, a common size offset, the case an
    unknown offset most readily mistakes for a place; and a shift whose size follows the level
    profile the records print, with the same mean d. The profile is each paper one vote: a paper's
    sex contrasts of one measure at every lumbar level over their own mean there, averaged over the
    paper's measures, then over the papers (level_profile; Bach 2019's disc and foramen contrasts
    fall caudally, Twomey 1985's and Eisenstein 1977's do not, and each paper's own profile is
    recorded beside the mean). Two arms read g from the records: each measure's pooled g
    (records/covariates/effects.csv) at every level of it and 0 for a measure no paper prints apart,
    and each cell's pooled g where a paper prints the cell apart, else its measure's.

(b) Held out on the papers' own rows. For each paper P that prints both sexes of a stratum of
    adults (covariates.sex_contrasts over the full snapshot's rows and the sexes' snapshot's, the
    men and women the reread's series.py pooled away: one technique and one set of people per
    cohort, measure and level, the whole cohort before its strata, each stratum's own count and at
    least covariates.MIN_PER_SEX of each sex, each sex's SD as printed or, for a paper printing
    means alone, the within-sex SD its difference was read against, said in sd_from), persons are
    drawn half and half from P's own
    men's and women's tables, a sex's strata at one cell (its age bands, its groups) joined as
    strata.Stratum joins a paper's cohorts, on every measure P prints for both sexes at every lumbar
    level that the selection's cells hold and the other papers pool at every level: where P is a
    population of the selection, the measures it names P's population with (strata.paper_measures),
    on the technique P's stratum reads; where P prints the measure only apart (Eisenstein 1977,
    Ahmed 2019's and the Campobasso MRIs' canals, Amonoo-Kuofi 1985's mid-body depth), the cells'
    measure itself, and where some of each (Abbas 2021), both, labelled so (population_of). Half
    and half so that every population weighs the sexes alike, as reading (a)'s split does (a table
    split by sex keeps its mean and SD only for half men and half women); P's own counts by sex
    weigh its strata within a sex where they are joined, and are recorded. Rule A is the selected
    rule as select.py builds it for P: the plain table of the other papers, tempered at P's own
    temperature per width,
    chosen by select.inner_choice on the other papers alone with P dropped from every pool and fold
    (on select.py's own seed and measures where P is a population of the selection, so Bach 2019's
    is 1.4 at every width as records/select/choices.csv holds; where no other paper gives a fold,
    select.inner_choice's fallback of T = 1, which the records name as a fallback and not as an
    inner choice, inner_t_from); and, beside it, at the fixed T = 2
    that a rule carried without its own inner choice would use, and at T = 1, the exact posterior.
    Rule B is that table with each cell moved by +-g/2 within-sex SDs and its SD narrowed to the
    within-sex SD, g the other papers' (covariates.transfer: the same cell pooled over them, else
    the measure, else none and no shift), read from contrasts made with P left out of every SD a
    means-only contrast borrows, at the same temperature as A. P's own rows enter neither table, nor
    g, nor the temperature. Beside them, labelled as ceilings and never a rule: P's own sexless
    table (its two sexes' tables pooled half and half, the exact sexless Gaussian of the persons
    drawn), P's own two sexes' tables, and A moved by P's own g, which is what B would be had the
    other papers printed P's effect. Where P prints means alone and no SD of its own, its persons'
    spread is the other papers' pooled SD of its modality class, which the rule's table also reads,
    so its persons' spread is the rule's own by construction and its scores are synthetic: such a
    paper is flagged (synthetic_persons, persons_sd) and kept out of the headline, which pools the
    papers whose persons' SDs are printed, with the pool over every paper beside it.

Every score is select.scores's on the same fields: named right (the top choice correct), the share
answered at the 0.99 claim (naming.CLAIM) and the share of those right, the log score (the mean log
posterior of the true place in nats; minus it is the log loss), and the calibration error of the
top probability over ten bins. A difference is read field by field, and its SE is over persons:
clustered by person for the rates and the log score (score.clustered_se), and for the precision at
0.99 and the calibration error, which are no means over fields, the SD over a bootstrap of persons,
men and women resampled apart, the same draws for both rules. Pooled over populations, each one
equal weight, the headline SE is between them, their SD over sqrt(k) as select.py's _mean_se reads
it, since a new population differs from these as they differ from each other and their persons'
SE, sqrt(sum se^2) / k, leaves that out; both are recorded (d_*_se_between, d_*_se_persons), and
one population's own is its persons'.

Seeds: each reading's seed starts a numpy SeedSequence spawned once per unit (a table of reading
(a), a paper of reading (b)) and each unit's once per stream (STREAMS: the men, the women, the
bootstrap, and the inner choice of a paper that is no population of the selection), so no two
draws of the study share a stream; every arm of one table reads the same men's and women's
streams, the common random numbers its paired differences need.
"""
from __future__ import annotations

import csv
import math
from dataclasses import replace
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from schwingcheck import LEVELS
from schwingcheck import score as S

from . import covariates as CV
from . import literature as L
from . import papers_table as PT
from . import select as SEL
from . import strata as ST
from .all_measures import LUMBAR
from .naming import CLAIM
from .papers_table import Table
from .population import GENERATOR, Population, Settings, draw_table

SEED_SYNTHETIC = 4107
SEED_HELD_OUT = 4108
STREAMS = ("men", "women", "bootstrap", "inner")
D_GRID = (0.0, 0.3, 0.8, 1.5)
PERSONS = 1000                 # a population, half men and half women
FIXED_T = 2.0                  # the temperature a rule carried without its own inner choice reads
RESAMPLES = 200                # of persons, for the SE of the precision and the calibration error
NO_SHIFT = ({}, float("nan"))  # strata.others_table's borrowed medians, unread by a plain table

COMMON, BY_LEVEL = "the same shift at every cell", "the shift by level, the records' profile"
PER_MEASURE, PER_CELL = "the records' g, per measure", "the records' g, per cell"
RULE_A, RULE_MIX, RULE_B = "A: the sexless table", "A': the two sexes mixed, sex unknown", "B: the person's sex's table"
SYNTHETIC_COMPARISONS = ((RULE_A, ""), (RULE_MIX, RULE_A), (RULE_B, RULE_A), (RULE_B, RULE_MIX))

A_IN, B_IN = "A: the others' plain table, P's inner T", "B: A moved by the others' g, P's inner T"
A_T2, B_T2 = "A: the others' plain table, T = 2", "B: A moved by the others' g, T = 2"
A_T1, B_T1 = "A: the others' plain table, T = 1", "B: A moved by the others' g, T = 1"
OWN_G = "ceiling: A moved by P's own g, P's inner T"
OWN_SEXLESS, OWN_BY_SEX = "ceiling: P's own sexless table, T = 1", "ceiling: P's own tables by sex, T = 1"
HELD_OUT_COMPARISONS = ((A_IN, ""), (B_IN, A_IN), (OWN_G, A_IN), (A_T2, ""), (B_T2, A_T2), (A_T1, ""), (B_T1, A_T1),
                        (OWN_SEXLESS, A_T1), (OWN_BY_SEX, A_T1), (OWN_BY_SEX, OWN_SEXLESS))
SELECTION_POPULATION = "a population of the selection: its measures and technique there"
APART_ONLY = "no population of the selection on these measures: its sexes alone"
PARTLY = ("a population of the selection on some of these measures and its sexes alone on the rest: an inner choice "
          "of its own on them")


# ---- seeds ------------------------------------------------------------------------------------------

def streams(seed: int, units: int) -> List[Dict[str, np.random.SeedSequence]]:
    """`units` independent units of one reading, each with its own stream per name of STREAMS."""
    return [dict(zip(STREAMS, unit.spawn(len(STREAMS)))) for unit in np.random.SeedSequence(seed).spawn(units)]


def integer_seed(stream: np.random.SeedSequence) -> int:
    """A stream as the integer seed select.inner_choice takes."""
    return int(stream.generate_state(1)[0])


# ---- the two sexes of a table ----------------------------------------------------------------------

def within_sd(sd: np.ndarray, g: np.ndarray) -> np.ndarray:
    """The within-sex SD that, with the sexes g of it apart, gives a half-and-half SD of `sd`."""
    return np.asarray(sd, float) / np.sqrt(1.0 + 0.25 * np.asarray(g, float) ** 2)


def split_by_sex(table: Table, g) -> Tuple[Table, Table]:
    """The men's and the women's tables: each cell's mean moved by +-g/2 within-sex SDs and its SD
    narrowed to the within-sex SD, so that half of each keeps the table's mean and SD."""
    g = np.broadcast_to(np.asarray(g, float), table.mu.shape)
    sw = within_sd(table.sd, g)
    half = 0.5 * g * sw
    return (replace(table, name="%s, men" % table.name, mu=table.mu + half, sd=sw),
            replace(table, name="%s, women" % table.name, mu=table.mu - half, sd=sw))


def half_and_half(men: Table, women: Table, name: str) -> Table:
    """The two sexes' tables pooled half and half: the mean of the means, and the SD of the mixture."""
    var = 0.5 * (men.sd ** 2 + women.sd ** 2) + 0.25 * (men.mu - women.mu) ** 2
    return replace(men, name=name, mu=0.5 * (men.mu + women.mu), sd=np.sqrt(var))


def same_table(a: Table, b: Table) -> bool:
    return bool(np.array_equal(a.mu, b.mu, equal_nan=True) and np.array_equal(a.sd, b.sd, equal_nan=True))


# ---- the shifts ----------------------------------------------------------------------------------------

def common_shift(table: Table, d: float) -> np.ndarray:
    return np.full(table.mu.shape, float(d))


def level_shift(table: Table, d: float, profile: Dict[str, float]) -> np.ndarray:
    """d at every measure, scaled at each level by the profile (mean 1 over the run)."""
    return float(d) * np.broadcast_to(np.array([profile[lv] for lv in table.levels]), table.mu.shape).copy()


def measure_shift(table: Table, base_of: Dict[str, str], g_measure: Dict[str, float]) -> np.ndarray:
    """Each measure's pooled g at every level of it, 0 for a measure no paper prints apart."""
    g = np.array([g_measure.get(base_of[k], 0.0) for k in table.keys], float)
    return np.repeat(g[:, None], len(table.levels), 1)


def cell_shift(table: Table, base_of: Dict[str, str], g_cell: Dict[Tuple[str, str], float],
               g_measure: Dict[str, float]) -> np.ndarray:
    """Each cell's pooled g where a paper prints the cell apart, else its measure's, else 0."""
    out = np.zeros(table.mu.shape)
    for j, k in enumerate(table.keys):
        for i, lv in enumerate(table.levels):
            out[j, i] = g_cell.get((base_of[k], lv), g_measure.get(base_of[k], 0.0))
    return out


# ---- the records -----------------------------------------------------------------------------------------

def _float(s: str) -> float:
    return float(s) if s not in ("", None) else float("nan")


CONTRAST_NAMES = ("paper", "cohort", "measure", "level", "group")
CONTRAST_NUMBERS = ("mean_male", "sd_male", "n_male", "mean_female", "sd_female", "n_female", "g", "var_g")


def load_contrasts(path: str) -> List[dict]:
    """records/covariates/contrasts.csv's rows, the numbers as floats (an SD a stratum does not
    print is NaN): the record the run's own contrasts are held to before anything is drawn."""
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return [dict({k: r[k] for k in CONTRAST_NAMES}, **{k: _float(r[k]) for k in CONTRAST_NUMBERS}) for r in rows]


def contrast_differs(record: dict, c: CV.Contrast) -> bool:
    """Whether a row of contrasts.csv is not this contrast: its names, or its g and var_g."""
    names = (c.paper, c.cohort, c.base_key, c.level, c.group)
    return (tuple(record[k] for k in CONTRAST_NAMES) != names
            or not math.isclose(record["g"], c.g, rel_tol=1e-9, abs_tol=1e-12)
            or not math.isclose(record["var_g"], c.var_g, rel_tol=1e-9, abs_tol=1e-12))


def load_effects(path: str, variable: str = "sex") -> Dict[str, float]:
    """records/covariates/effects.csv: each measure's pooled effect of one covariate."""
    with open(path, encoding="utf-8") as fh:
        return {r["measure"]: float(r["mean"]) for r in csv.DictReader(fh) if r["variable"] == variable}


def placed(contrasts: Sequence[CV.Contrast]) -> Dict[Tuple[str, str, str], Tuple[float, float, int]]:
    """covariates.by_paper_cell with each printed level put where the tables place it (a disc
    between L1 and L2 at L1), a level no table places kept as printed, so a measure's cells pool as
    covariates pools them and a cell meets the table's cell at the same level."""
    out = {}
    for (paper, key, level), value in CV.by_paper_cell(contrasts).items():
        at = PT.place(key, level, paper) or level
        if (paper, key, at) in out:
            raise ValueError("two printed levels of %s's %s are placed at %s" % (paper, key, at))
        out[paper, key, at] = value
    return out


def cell_effects(cells_g: Dict[Tuple[str, str, str], Tuple[float, float, int]]) -> Dict[Tuple[str, str], float]:
    """Each placed cell's g pooled over every paper that prints it apart."""
    out = {}
    for key, level in sorted({(k, lv) for _, k, lv in cells_g}):
        got = CV.pooled(CV.paper_values(cells_g, key, level))
        out[key, level] = got["mean"]
    return out


def level_profile(cells_g: Dict[Tuple[str, str, str], Tuple[float, float, int]],
                  levels: Sequence[str] = LUMBAR) -> Tuple[Dict[str, float], Dict[str, dict]]:
    """The records' level profile of the sex shift, each paper one vote: each of a paper's measures
    printed apart at every level of the run over its own mean there (a series whose mean g is not
    above zero gives none), averaged over the paper's measures, then over the papers; and each
    paper's own profile with the series it came from."""
    per: Dict[str, List[Tuple[str, np.ndarray]]] = {}
    for paper, key in sorted({(p, k) for p, k, _ in cells_g}):
        g = [cells_g.get((paper, key, lv)) for lv in levels]
        if any(x is None for x in g):
            continue
        g = np.array([x[0] for x in g])
        if g.mean() > 0:
            per.setdefault(paper, []).append((key, g / g.mean()))
    if not per:
        return {lv: 1.0 for lv in levels}, {}
    papers = {p: np.mean([r for _, r in series], 0) for p, series in per.items()}
    profile = np.mean(list(papers.values()), 0)
    by_paper = {p: {"series": [k for k, _ in per[p]], "profile": dict(zip(levels, (float(x) for x in papers[p])))}
                for p in sorted(papers)}
    return dict(zip(levels, (float(x) for x in profile))), by_paper


# ---- persons, evidence and the rules ---------------------------------------------------------------------

def draw_sexes(men: Table, women: Table, settings: Settings, persons: int,
               seeds: Dict[str, np.random.SeedSequence]) -> Tuple[Population, Population]:
    """Half the persons men from the men's table on the men's stream, the rest women on the women's."""
    half = persons // 2
    return draw_table(men, settings, half, seeds["men"]), draw_table(women, settings, persons - half, seeds["women"])


def persons_of(pops: Sequence[Population]) -> np.ndarray:
    """1 for a man, 0 for a woman, the men numbered first as evidence numbers them."""
    return np.concatenate([np.ones(pops[0].measured.shape[0], bool), np.zeros(pops[1].measured.shape[0], bool)])


def evidence(pops: Sequence[Population], tables: Sequence[Table], width: int, settings: Settings):
    """log p(field | place) for every field of the men under tables[0] and of the women under
    tables[1], the truth and the person, the women numbered after the men."""
    men = SEL.log_evidence(pops[0], tables[0], width, settings)
    women = SEL.log_evidence(pops[1], tables[1], width, settings)
    group = np.concatenate([men[2], women[2] + pops[0].measured.shape[0]])
    return np.concatenate([men[0], women[0]]), np.concatenate([men[1], women[1]]), group


def rule_evidence(pops, sexless: Table, men: Table, women: Table, width: int, settings: Settings,
                  shortcut: bool = True) -> Tuple[Dict[str, np.ndarray], np.ndarray, np.ndarray]:
    """The log evidence of A, A' and B on the same fields, the truth and the person: A reads the
    sexless table for everyone, B each person's own sex's table, A' the equal mixture of the two
    sexes' tables, log((p_men + p_women) / 2). With `shortcut`, where both sexes' tables are the
    sexless one, B and A' take A's evidence itself, which they equal in exact arithmetic; without
    it every evidence is computed, so that a test can hold the arithmetic itself to zero."""
    ev_a, truth, group = evidence(pops, (sexless, sexless), width, settings)
    if shortcut and same_table(men, sexless) and same_table(women, sexless):
        return {RULE_A: ev_a, RULE_MIX: ev_a, RULE_B: ev_a}, truth, group
    mm, fm = (SEL.log_evidence(pops[0], t, width, settings)[0] for t in (men, women))
    mf, ff = (SEL.log_evidence(pops[1], t, width, settings)[0] for t in (men, women))
    mixed = np.concatenate([SEL.mixture_evidence([mm, fm]), SEL.mixture_evidence([mf, ff])])
    return {RULE_A: ev_a, RULE_MIX: mixed, RULE_B: np.concatenate([mm, ff])}, truth, group


def synthetic_rules(pops, sexless: Table, men: Table, women: Table, width: int, settings: Settings,
                    shortcut: bool = True) -> Dict[str, dict]:
    """A, A' and B on the same fields, each scored at temperature 1."""
    ev, truth, group = rule_evidence(pops, sexless, men, women, width, settings, shortcut)
    return {name: score_rule(e, truth, group) for name, e in ev.items()}


# ---- scores and paired differences ---------------------------------------------------------------------

def score_rule(logev: np.ndarray, truth: np.ndarray, group: np.ndarray, temperature: float = 1.0) -> dict:
    """select.scores with the answers at the claim and the temperature kept for the record."""
    sc = SEL.scores(logev, truth, group, temperature)
    sc["_ans"] = (sc["_top"] >= CLAIM).astype(float)
    sc["temperature"] = float(temperature)
    return sc


def metrics(sc: dict) -> dict:
    """The rule's own scores, for the record."""
    keys = ("fields", "exact", "exact_se", "log_score", "log_score_se", "answered", "n_answered", "errors", "precision",
            "precision_se", "ece", "mean_top", "temperature")
    return dict({k: sc[k] for k in keys}, persons=int(len(np.unique(sc["_group"]))))


def tallies(sc: dict, persons: int, bins: int = SEL.BINS) -> Dict[str, np.ndarray]:
    """Per person: the fields, top probabilities and hits in each bin of the top probability, the
    answers at the claim and the right ones, so that any weighting of persons gives the
    calibration error and the precision at once."""
    edges = np.linspace(0.0, 1.0, bins + 1)
    which = np.clip(np.searchsorted(edges, sc["_top"], side="right") - 1, 0, bins - 1)
    idx = sc["_group"] * bins + which

    def per_bin(weights=None):
        return np.bincount(idx, weights=weights, minlength=persons * bins).reshape(persons, bins).astype(float)
    return {"n": per_bin(), "top": per_bin(sc["_top"]), "hit": per_bin(sc["_hit"]),
            "ans": np.bincount(sc["_group"], weights=sc["_ans"], minlength=persons),
            "right": np.bincount(sc["_group"], weights=sc["_ans"] * sc["_hit"], minlength=persons)}


def ece_of(t: Dict[str, np.ndarray], w: np.ndarray) -> np.ndarray:
    """The calibration error under each row of person weights: sum over bins of |hits - top| over the fields."""
    return np.abs(w @ t["hit"] - w @ t["top"]).sum(1) / (w @ t["n"]).sum(1)


def precision_of(t: Dict[str, np.ndarray], w: np.ndarray) -> np.ndarray:
    """The share right of the answers at the claim under each row of person weights."""
    ans = w @ t["ans"]
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(ans > 0, (w @ t["right"]) / ans, np.nan)


def resample_weights(male: np.ndarray, resamples: int, rng: np.random.Generator) -> np.ndarray:
    """(resamples, persons) counts of a bootstrap of persons, men and women resampled apart."""
    w = np.zeros((resamples, len(male)))
    for part in (np.flatnonzero(male), np.flatnonzero(~male)):
        if part.size:
            w[:, part] = rng.multinomial(part.size, np.full(part.size, 1.0 / part.size), size=resamples)
    return w


def paired(a: dict, b: dict, weights: np.ndarray) -> dict:
    """b minus a on the same fields: the rates and the log score field by field with the SE
    clustered by person, the precision and the calibration error with the bootstrap's SD."""
    out = {}
    for name, key in (("exact", "_hit"), ("log_score", "_lp"), ("answered", "_ans")):
        diff = b[key] - a[key]
        out["d_" + name], out["d_%s_se" % name] = float(diff.mean()), S.clustered_se(diff, a["_group"])
    persons = weights.shape[1]
    ta, tb = tallies(a, persons), tallies(b, persons)
    one = np.ones((1, persons))
    for name, fn in (("precision", precision_of), ("ece", ece_of)):
        boots = fn(tb, weights) - fn(ta, weights)
        ok = np.isfinite(boots)
        out["d_" + name] = float((fn(tb, one) - fn(ta, one))[0])
        out["d_%s_se" % name] = float(np.std(boots[ok], ddof=1)) if ok.sum() > 1 else float("nan")
    return out


def compare(scored: Dict[str, dict], comparisons: Sequence[Tuple[str, str]], weights: np.ndarray) -> List[dict]:
    """One row per (rule, rule it is read against): the rule's scores and, against another, the
    paired differences."""
    rows = []
    for rule, against in comparisons:
        row = dict(metrics(scored[rule]), rule=rule, against=against)
        if against:
            row.update(paired(scored[against], scored[rule], weights))
        rows.append(row)
    return rows


# ---- (a) synthetic ---------------------------------------------------------------------------------------

def selection_tables(cells: Sequence[ST.Cell], vocabulary: Dict[str, dict],
                     levels: Sequence[str] = LUMBAR) -> List[Tuple[str, str, Table]]:
    """The tables the selection names with: every measure it uses pooled over every paper, then,
    for each paper it holds out, the plain table of the other papers on that paper's measures, as
    select.py builds it. Each as (reading, the paper held out or "", table)."""
    folds, union = [], set()
    for paper in sorted({s.paper for c in cells for s in c.strata}):
        keys = ST.paper_measures(cells, paper, vocabulary, levels)
        if keys:
            union |= set(keys)
            folds.append(("each held-out paper's measures", paper,
                          ST.others_table(cells, paper, keys, vocabulary, NO_SHIFT, False, levels)))
    every = ST.others_table(cells, None, sorted(union), vocabulary, NO_SHIFT, False, levels)
    return [("every measure the selection uses", "", every)] + folds


def base_keys(cells: Sequence[ST.Cell]) -> Dict[str, str]:
    """Each table key's reread key, which the covariate records name a measure by."""
    return {c.measure: c.base_key for c in cells}


def arms_for(table: Table, base_of: Dict[str, str], profile: Dict[str, float], g_measure: Dict[str, float],
             g_cell: Dict[Tuple[str, str], float], d_grid: Sequence[float] = D_GRID) -> List[Tuple[str, float, np.ndarray]]:
    """Every arm's g over the table's cells: each d of the grid in both shapes, then the records' two."""
    out = []
    for shape in (COMMON, BY_LEVEL):
        for d in d_grid:
            out.append((shape, float(d), common_shift(table, d) if shape == COMMON else level_shift(table, d, profile)))
    out.append((PER_MEASURE, float("nan"), measure_shift(table, base_of, g_measure)))
    out.append((PER_CELL, float("nan"), cell_shift(table, base_of, g_cell, g_measure)))
    return out


def synthetic_table(reading: str, paper: str, table: Table, arms, widths: Sequence[int], settings: Settings,
                    persons: int, seeds: Dict[str, np.random.SeedSequence], resamples: int) -> List[dict]:
    """Every arm on one table: the same persons' streams for every arm (common random numbers), the
    three rules on the same fields at every width."""
    rows = []
    for arm, d, g in arms:
        men, women = split_by_sex(table, g)
        pops = draw_sexes(men, women, settings, persons, seeds)
        weights = resample_weights(persons_of(pops), resamples, np.random.default_rng(seeds["bootstrap"]))
        for w in widths:
            scored = synthetic_rules(pops, table, men, women, w, settings)
            for row in compare(scored, SYNTHETIC_COMPARISONS, weights):
                rows.append(dict(row, reading=reading, paper_held_out=paper, table=table.name, n_measures=len(table.keys),
                                 measures=";".join(table.keys), arm=arm, d=d, g_mean=float(np.mean(g)),
                                 g_max=float(np.max(np.abs(g))), cells_shifted=int((g != 0).sum()), cells=int(g.size), width=w))
    return rows


def synthetic(cells: Sequence[ST.Cell], vocabulary: Dict[str, dict], profile: Dict[str, float], g_measure: Dict[str, float],
              g_cell: Dict[Tuple[str, str], float], widths: Sequence[int] = (1, 2, 3), settings: Settings = GENERATOR,
              persons: int = PERSONS, seed: int = SEED_SYNTHETIC, resamples: int = RESAMPLES,
              d_grid: Sequence[float] = D_GRID, levels: Sequence[str] = LUMBAR, log=None) -> List[dict]:
    """Reading (a) on every table of selection_tables, table i on unit i of streams(seed)."""
    base_of = base_keys(cells)
    tables = selection_tables(cells, vocabulary, levels)
    rows = []
    for (reading, paper, table), seeds in zip(tables, streams(seed, len(tables))):
        if log:
            log("synthetic: %s (%d measures)" % (paper or reading, len(table.keys)))
        arms = arms_for(table, base_of, profile, g_measure, g_cell, d_grid)
        rows += synthetic_table(reading, paper, table, arms, widths, settings, persons, seeds, resamples)
    return rows


# ---- (b) held out on the papers' own rows -------------------------------------------------------------------

def _sex_series(c: CV.Contrast, sex: str) -> L.Series:
    """One sex of a contrast as a series: its mean and count, its printed SD or the within-sex SD
    its means were read against."""
    mean, sd, n = (c.mean_m, c.sd_m, c.n_m) if sex == "male" else (c.mean_f, c.sd_f, c.n_f)
    return L.Series(paper=c.paper, cohort=c.cohort, technique=c.technique, modality=c.modality, group=c.group, sex=sex,
                    key=c.key, level=c.level, mean=mean, sd=sd if math.isfinite(sd) else c.within, n=n, vs_panjabi="",
                    flag="sex apart", n_note=c.count_from)


def own_contrasts(contrasts: Sequence[CV.Contrast], cells: Sequence[ST.Cell], paper: str,
                  levels: Sequence[str] = LUMBAR) -> Dict[Tuple[str, str], List[CV.Contrast]]:
    """P's contrasts at every placed cell of `levels` the cells hold; where P is a population of the
    cell, on the technique its stratum reads."""
    to_panjabi, by = PT._reread_to_panjabi(), ST.cells_by_key(cells)
    out: Dict[Tuple[str, str], List[CV.Contrast]] = {}
    seen = set()
    for c in contrasts:
        if c.paper != paper:
            continue
        at = PT.place(c.key, c.level, paper)
        cell = by.get((to_panjabi.get(c.key, c.key), at))
        if cell is None or at not in levels:
            continue
        own = cell.stratum(paper)
        if own is not None and c.technique not in {s.technique for s in own.series}:
            continue
        stratum = (cell.measure, at, c.cohort, c.group)
        if stratum in seen:
            raise ValueError("%s prints %s at %s for %s %s twice" % (paper, cell.measure, at, c.cohort, c.group))
        seen.add(stratum)
        out.setdefault((cell.measure, at), []).append(c)
    return {k: out[k] for k in sorted(out)}


def own_sex_strata(contrasts: Sequence[CV.Contrast], cells: Sequence[ST.Cell], paper: str,
                   levels: Sequence[str] = LUMBAR) -> Dict[Tuple[str, str], Dict[str, ST.Stratum]]:
    """P's own men's and women's populations at every placed cell of `levels` the cells hold, from
    its contrasts (covariates.sex_contrasts, through own_contrasts); a sex's strata at one cell
    joined as strata.Stratum joins cohorts."""
    return {cell: {sex: ST._stratum(paper, [_sex_series(c, sex) for c in cs]) for sex in ("male", "female")}
            for cell, cs in own_contrasts(contrasts, cells, paper, levels).items()}


PERSONS_PRINTED = "printed: each sex's SD as the paper prints it"
PERSONS_OWN_SEXLESS = "the paper's own SD of the sexes together, their pooling inverted"
PERSONS_BORROWED = ("borrowed: the other papers' pooled SD, which rule A's table reads too, so the persons' spread is "
                    "the rule's own by construction and the scores are synthetic")
PERSONS_SD = {CV.PRINTED_SD: PERSONS_PRINTED, CV.OWN_SEXLESS_SD: PERSONS_OWN_SEXLESS, CV.OTHERS_POOLED_SD: PERSONS_BORROWED}


def persons_sd(scored: Sequence[CV.Contrast]) -> Tuple[str, bool]:
    """Where the spread of P's persons comes from, over the strata scored, and whether it is the
    rule's own (any stratum's SD borrowed from the other papers' pool): such a paper's scores are
    synthetic and stay out of the headline."""
    kinds = sorted({PERSONS_SD[c.sd_from] for c in scored})
    return "; ".join(kinds), PERSONS_BORROWED in kinds


def population_of(cells: Sequence[ST.Cell], paper: str, keys: Sequence[str], vocabulary: Dict[str, dict],
                  levels: Sequence[str] = LUMBAR) -> str:
    """Whether P's scored measures are those the selection names its population with, measures P
    prints only apart, or some of each (Abbas 2021's canal depth and area beside its canal width)."""
    selection = set(ST.paper_measures(cells, paper, vocabulary, levels))
    if keys and set(keys) <= selection:
        return SELECTION_POPULATION
    return PARTLY if set(keys) & selection else APART_ONLY


def held_out_measures(cells: Sequence[ST.Cell], strata: Dict[Tuple[str, str], Dict[str, ST.Stratum]], paper: str,
                      vocabulary: Dict[str, dict], levels: Sequence[str] = LUMBAR) -> List[str]:
    """The measures P prints for both sexes at every level that the cells hold and the other papers
    pool at every level, of a kind with a modelled error: where P is a population of a cell of the
    measure, only the selection's measures of P (strata.paper_measures)."""
    by = ST.cells_by_key(cells)
    selection = set(ST.paper_measures(cells, paper, vocabulary, levels))
    out = []
    for key in sorted({k for k, _ in strata}):
        mine = [by.get((key, lv)) for lv in levels]
        if any((key, lv) not in strata for lv in levels) or any(c is None for c in mine):
            continue
        if any(c.stratum(paper) is not None for c in mine):
            if key in selection:
                out.append(key)
            continue
        if vocabulary[mine[0].base_key]["kind"] in CV.KINDS and all(ST.pooled_without(c, paper) is not None for c in mine):
            out.append(key)
    return out


def own_tables_by_sex(cells: Sequence[ST.Cell], strata, paper: str, keys: Sequence[str], vocabulary: Dict[str, dict],
                      levels: Sequence[str] = LUMBAR) -> Tuple[Table, Table]:
    """P's own men's and women's tables: each sex's mean and SD at every cell (own_sex_strata)."""
    by = ST.cells_by_key(cells)
    out = []
    for sex in ("male", "female"):
        mu = np.array([[strata[k, lv][sex].mean for lv in levels] for k in keys], float)
        sd = np.array([[strata[k, lv][sex].sd for lv in levels] for k in keys], float)
        out.append(Table(name="%s's own %s" % (paper, "men" if sex == "male" else "women"), keys=list(keys),
                         kinds=ST._kinds(keys, by, vocabulary, levels), mu=mu, sd=sd, sources=[paper] * len(keys),
                         levels=list(levels)))
    return out[0], out[1]


def effect_grid(table: Table, base_of: Dict[str, str], cells_g, paper: str, own: bool) -> Tuple[np.ndarray, List[List[str]]]:
    """g at every cell of the table and where it came from: with `own` False the other papers'
    (covariates.transfer, P left out: the cell, else the measure, else none and 0); with `own`
    True P's own, the cell's, else P's mean over its cells of the measure, else 0."""
    g = np.zeros(table.mu.shape)
    scope = [["none"] * len(table.levels) for _ in table.keys]
    source, left_out = ({k: v for k, v in cells_g.items() if k[0] == paper}, "") if own else (cells_g, paper)
    for j, key in enumerate(table.keys):
        for i, lv in enumerate(table.levels):
            value, came = CV.transfer(source, left_out, base_of[key], lv)
            if came != "none":
                g[j, i], scope[j][i] = value, came
    return g, scope


def others_effects(rows: Sequence[dict], vocabulary: Dict[str, dict], paper: str) -> Dict[Tuple[str, str, str], tuple]:
    """The other papers' placed sex effects with P left out of every SD a means-only contrast
    borrows, so that nothing of P reaches the g rule B reads."""
    return placed([c for c in CV.sex_contrasts(rows, vocabulary, without=(paper,)) if c.paper != paper])


def rule_tables(cells: Sequence[ST.Cell], cells_g_others, paper: str, keys: Sequence[str], vocabulary: Dict[str, dict],
                levels: Sequence[str] = LUMBAR) -> dict:
    """Rule A's table for P (the others' plain table, as select.py's PLAIN), rule B's two (A moved
    by the others' g), and the g with its scope: nothing of P enters any of them."""
    plain = ST.others_table(cells, paper, keys, vocabulary, NO_SHIFT, False, levels)
    g, scope = effect_grid(plain, base_keys(cells), cells_g_others, paper, own=False)
    men, women = split_by_sex(plain, g)
    return {"A": plain, "B_men": men, "B_women": women, "g": g, "scope": scope}


def held_out_tables(cells: Sequence[ST.Cell], rows: Sequence[dict], contrasts: Sequence[CV.Contrast], paper: str,
                    vocabulary: Dict[str, dict], levels: Sequence[str] = LUMBAR) -> Optional[dict]:
    """Every table reading (b) needs for P, or None where P prints both sexes of no measure it can
    be scored on (held_out_measures). `contrasts` are every paper's (P's own persons and ceilings
    read them); the others' g is made again from `rows` with P left out (others_effects)."""
    strata = own_sex_strata(contrasts, cells, paper, levels)
    keys = held_out_measures(cells, strata, paper, vocabulary, levels)
    if not keys:
        return None
    tables = rule_tables(cells, others_effects(rows, vocabulary, paper), paper, keys, vocabulary, levels)
    g_own, _ = effect_grid(tables["A"], base_keys(cells), placed([c for c in contrasts if c.paper == paper]), paper, own=True)
    tables["G_men"], tables["G_women"] = split_by_sex(tables["A"], g_own)
    tables["g_own"] = g_own
    tables["own_men"], tables["own_women"] = own_tables_by_sex(cells, strata, paper, keys, vocabulary, levels)
    tables["own"] = half_and_half(tables["own_men"], tables["own_women"], "%s's own, the sexes half and half" % paper)
    tables["keys"] = list(keys)
    tables["counts"] = {sex: float(np.mean([strata[k, lv][sex].n for k in keys for lv in levels])) for sex in ("male", "female")}
    joined = own_contrasts(contrasts, cells, paper, levels)
    scored = [c for k in keys for lv in levels for c in joined[k, lv]]
    tables["sd_from"] = sorted({c.sd_from for c in scored})
    tables["count_from"] = sorted({c.count_from for c in scored})
    tables["persons_sd"], tables["synthetic_persons"] = persons_sd(scored)
    tables["strata_scored"] = len(scored)
    return tables


INNER_CHOICE = "inner choice: select.inner_choice on the other papers' folds"
FALLBACK_T = ("fallback, no inner choice: no other paper of the selection prints these measures at every level, so "
              "select.inner_choice has no fold and returns T = 1")


def inner_temperatures(cells: Sequence[ST.Cell], paper: str, keys: Sequence[str], vocabulary: Dict[str, dict],
                       widths: Sequence[int], settings: Settings, columns: int, stream: np.random.SeedSequence,
                       levels: Sequence[str] = LUMBAR) -> dict:
    """P's own temperature per width, select.inner_choice's on the other papers alone with P
    dropped: where P is a population of the selection, on select.py's seed (strata.SEED_COLUMNS +
    P's index among the papers of the cells) and select.py's measures of P (strata.paper_measures),
    so that it is the temperature select.py's rule for P reads whichever of them P prints apart;
    else on P's inner stream and the measures scored. Where no other paper gives a fold the
    temperature is select.inner_choice's fallback, T = 1, and t_from says so."""
    papers = sorted({s.paper for c in cells for s in c.strata})
    selection = ST.paper_measures(cells, paper, vocabulary, levels)
    of_selection = population_of(cells, paper, keys, vocabulary, levels) == SELECTION_POPULATION
    measures = selection if of_selection else list(keys)
    seed = ST.SEED_COLUMNS + papers.index(paper) if paper in papers else integer_seed(stream)
    choice = SEL.inner_choice(cells, paper, measures, vocabulary, widths, settings, columns, seed, levels=levels)
    return {"t": {w: float(choice["t"][w]) for w in widths}, "k": choice["k"], "inner_folds": len(choice["folds"]),
            "t_from": INNER_CHOICE if choice["folds"] else FALLBACK_T, "inner_measures": list(measures),
            "inner_columns": columns, "seed": int(seed), "seed_from": "select.py's" if paper in papers else "the paper's inner stream"}


def held_out_rules(pops, tables: dict, width: int, settings: Settings, t_inner: float, shortcut: bool = True) -> Dict[str, dict]:
    """Every rule and ceiling of reading (b) on the same fields of P's persons."""
    ev_a, truth, group = evidence(pops, (tables["A"], tables["A"]), width, settings)

    def ev(men, women):
        if shortcut and same_table(men, tables["A"]) and same_table(women, tables["A"]):
            return ev_a
        return evidence(pops, (men, women), width, settings)[0]
    ev_b, ev_g = ev(tables["B_men"], tables["B_women"]), ev(tables["G_men"], tables["G_women"])
    ev_own = evidence(pops, (tables["own"], tables["own"]), width, settings)[0]
    ev_by_sex = evidence(pops, (tables["own_men"], tables["own_women"]), width, settings)[0]

    def at(e, t):
        return score_rule(e, truth, group, t)
    return {A_IN: at(ev_a, t_inner), B_IN: at(ev_b, t_inner), OWN_G: at(ev_g, t_inner),
            A_T2: at(ev_a, FIXED_T), B_T2: at(ev_b, FIXED_T), A_T1: at(ev_a, 1.0), B_T1: at(ev_b, 1.0),
            OWN_SEXLESS: at(ev_own, 1.0), OWN_BY_SEX: at(ev_by_sex, 1.0)}


def contrast_papers(contrasts: Sequence[CV.Contrast]) -> List[str]:
    return sorted({c.paper for c in contrasts})


def coverage(cells: Sequence[ST.Cell], contrasts: Sequence[CV.Contrast], vocabulary: Dict[str, dict],
             levels: Sequence[str] = LUMBAR) -> List[dict]:
    """For every paper printing both sexes of a stratum of adults: the measures and placed levels
    it prints them at, the measures complete over the run, the measures reading (b) scores, and
    why none where none."""
    cells_g = placed(contrasts)
    out = []
    for paper in contrast_papers(contrasts):
        printed: Dict[str, List[str]] = {}
        for p, key, lv in sorted(cells_g, key=lambda k: (k[1], LEVELS.index(k[2]) if k[2] in LEVELS else 99, k[2])):
            if p == paper:
                printed.setdefault(key, []).append(lv)
        strata = own_sex_strata(contrasts, cells, paper, levels)
        complete = sorted({k for k, _ in strata if all((k, lv) in strata for lv in levels)})
        scored = held_out_measures(cells, strata, paper, vocabulary, levels)
        if scored:
            why = ""
        elif not complete:
            why = "prints both sexes at every level of %s to %s on no measure the cells hold" % (levels[0], levels[-1])
        else:
            why = "prints both sexes at every level of %s to %s only on %s, which no other paper pools there" % (
                levels[0], levels[-1], ", ".join(complete))
        mine = [c for c in contrasts if c.paper == paper]
        out.append({"paper": paper, "printed_apart": "; ".join("%s at %s" % (k, ",".join(v)) for k, v in printed.items()),
                    "complete_over_the_run": ";".join(complete), "scored_measures": ";".join(scored), "scored": bool(scored),
                    "population": population_of(cells, paper, scored, vocabulary, levels) if scored else "", "sd_from": "; ".join(sorted({c.sd_from for c in mine})),
                    "count_from": "; ".join(sorted({c.count_from for c in mine})), "why_not": why})
    return out


def held_out_paper(cells, rows, contrasts, paper, vocabulary, widths, settings, persons, seeds, resamples, inner_columns,
                   levels, log=None) -> Tuple[List[dict], Optional[dict]]:
    """Reading (b) on one paper: its rows at every width and its inner choice, or nothing."""
    tables = held_out_tables(cells, rows, contrasts, paper, vocabulary, levels)
    if tables is None:
        return [], None
    if log:
        log("held out: %s (%d measures)" % (paper, len(tables["keys"])))
    choice = inner_temperatures(cells, paper, tables["keys"], vocabulary, widths, settings, inner_columns, seeds["inner"], levels)
    pops = draw_sexes(tables["own_men"], tables["own_women"], settings, persons, seeds)
    weights = resample_weights(persons_of(pops), resamples, np.random.default_rng(seeds["bootstrap"]))
    shifted = tables["g"] != 0
    population = population_of(cells, paper, tables["keys"], vocabulary, levels)
    out = []
    for w in widths:
        for row in compare(held_out_rules(pops, tables, w, settings, choice["t"][w]), HELD_OUT_COMPARISONS, weights):
            out.append(dict(row, paper=paper, population=population, n_measures=len(tables["keys"]),
                            measures=";".join(tables["keys"]), width=w, inner_t=choice["t"][w],
                            cells=int(shifted.size), cells_with_others_g=int(shifted.sum()),
                            others_g_mean=float(tables["g"][shifted].mean()) if shifted.any() else float("nan"),
                            own_g_mean=float(tables["g_own"].mean()),
                            scope=";".join(sorted({s for r in tables["scope"] for s in r})),
                            own_men_per_cell=tables["counts"]["male"], own_women_per_cell=tables["counts"]["female"],
                            inner_t_from=choice["t_from"], persons_sd=tables["persons_sd"],
                            synthetic_persons=tables["synthetic_persons"], strata_scored=tables["strata_scored"],
                            sd_from="; ".join(tables["sd_from"]), count_from="; ".join(tables["count_from"])))
    return out, dict(choice, paper=paper, measures=tables["keys"], population=population, persons_sd=tables["persons_sd"],
                     synthetic_persons=tables["synthetic_persons"])


def held_out(cells: Sequence[ST.Cell], rows: Sequence[dict], contrasts: Sequence[CV.Contrast], vocabulary: Dict[str, dict],
             widths: Sequence[int] = (1, 2, 3), settings: Settings = GENERATOR, persons: int = PERSONS,
             seed: int = SEED_HELD_OUT, resamples: int = RESAMPLES, inner_columns: int = SEL.INNER_COLUMNS,
             levels: Sequence[str] = LUMBAR, log=None) -> Tuple[List[dict], List[dict]]:
    """Reading (b) for every paper printing both sexes, paper i (by name) on unit i of
    streams(seed): the rows and each scored paper's inner choice."""
    papers = contrast_papers(contrasts)
    out, choices = [], []
    for paper, seeds in zip(papers, streams(seed, len(papers))):
        got, choice = held_out_paper(cells, rows, contrasts, paper, vocabulary, widths, settings, persons, seeds, resamples,
                                     inner_columns, levels, log)
        out += got
        if choice is not None:
            choices.append(choice)
    return out, choices


# ---- summaries -------------------------------------------------------------------------------------------

DIFFS = ("exact", "log_score", "answered", "precision", "ece")


SE_BETWEEN = "between populations: their SD over sqrt(k), as select.py's _mean_se"
SE_PERSONS = "persons: one population's SE over its persons"


def _mean_and_person_se(rows: Sequence[dict], key: str) -> Tuple[float, float]:
    """The mean over independent populations and its SE over their persons, sqrt(sum se^2) / k:
    the SE were every population's own difference the one the rule makes on every population."""
    xs = [(r[key], r.get(key + "_se", float("nan"))) for r in rows if math.isfinite(r[key])]
    if not xs:
        return float("nan"), float("nan")
    k = len(xs)
    se = [s for _, s in xs]
    return float(np.mean([x for x, _ in xs])), float(math.sqrt(sum(s * s for s in se)) / k) if all(math.isfinite(s) for s in se) else float("nan")


def headline_se(rows: Sequence[dict], key: str) -> Tuple[float, float, float, str]:
    """The mean over populations with both SEs, and the one the headline reads: the between
    populations' SD over sqrt(k) (select._mean_se) from two populations on, since a new population
    differs from these as they differ from each other, which their persons' SE leaves out; the
    persons' SE for one population, which has no spread between populations to read."""
    mean, persons = _mean_and_person_se(rows, key)
    _, between = SEL._mean_se([r[key] for r in rows])
    k = sum(1 for r in rows if math.isfinite(r[key]))
    return mean, between, persons, (SE_BETWEEN if k > 1 else SE_PERSONS)


def summarise(rows: Sequence[dict], by: Sequence[str], reading: str) -> List[dict]:
    """Per group of `by`, over the populations in it, each one equal weight: each rule's mean
    scores, and each difference's mean with its headline SE (headline_se: between the populations
    from two on, the persons' for one) beside both SEs, and its least and greatest population."""
    groups: Dict[tuple, List[dict]] = {}
    for r in rows:
        groups.setdefault(tuple(r[k] if not (isinstance(r[k], float) and math.isnan(r[k])) else "" for k in by), []).append(r)
    out = []
    for key, rs in groups.items():
        row = dict(zip(by, key), reading=reading, populations=len(rs), fields=int(sum(r["fields"] for r in rs)))
        for m in ("exact", "log_score", "answered", "precision", "ece"):
            row[m] = _mean_and_person_se(rs, m)[0]
        if rs[0]["against"]:
            for m in DIFFS:
                mean, between, persons, which = headline_se(rs, "d_" + m)
                row["d_" + m] = mean
                row["d_%s_se" % m] = between if which == SE_BETWEEN else persons
                row["d_%s_se_between" % m], row["d_%s_se_persons" % m] = between, persons
                vals = [r["d_" + m] for r in rs if math.isfinite(r["d_" + m])]
                row["d_%s_least" % m] = float(min(vals)) if vals else float("nan")
                row["d_%s_most" % m] = float(max(vals)) if vals else float("nan")
            row["se_of_headline"] = SE_BETWEEN if len(rs) > 1 else SE_PERSONS
        out.append(row)
    return out
