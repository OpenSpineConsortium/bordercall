# Naming a vertebra from its neighbours: results

**Status: done, synthetic.** This is the answer to `docs/NEIGHBOUR_IDENTITY_STUDY.md`, the brief.
Source: the thread "Finish CNS slides with junction predictor", 2026-10-26, the owner's ask of
05:44 UTC. Everything below is drawn from columns synthesized from Panjabi's published means and
spreads (`bordercall/reference/panjabi_full_spine.csv`). No CT, no label, no corpus, no data
access was used. The code is `bordercall/neighbour.py` and `bordercall/neighbour_figures.py`;
the records are under `records/neighbour-2026-10-26/`; the tests are `tests/test_neighbour.py`.

Every number here is in one of three files, written by the three commands below, run from
`bordercall/`:

```
python run.py neighbour --outdir ../records/neighbour-2026-10-26
python run.py neighbour-enumerate --arm flank --shard 0 --of 1 --out ../records/neighbour-2026-10-26/enumerate-shard0.json
python run.py neighbour-enumerate --gather ../records/neighbour-2026-10-26/enumerate-shard0.json --out ../records/neighbour-2026-10-26/enumerate.json
python run.py neighbour-figures --json ../records/neighbour-2026-10-26/neighbour.json --enumerate-json ../records/neighbour-2026-10-26/enumerate.json --outdir ../records/neighbour-2026-10-26/figures
```

The first writes `neighbour.json` (the whole study, 93 s on this container) and `models.json`
(the fitted weights of every cell). The second and third write `enumerate.json` (all 127 subsets
of the seven measures; the shard file is deleted once gathered). The fourth draws the nine figures
and writes `figures/FIGURES.md`, with the sha256 of each record and each code file, and a CSV
beside every figure holding the numbers drawn. Beside each table below is the file and the key
the numbers come from.

## The four verdicts

1. **The mathematics.** A vertebra can be named from its neighbours alone, far above chance,
   and a monotone scalar index exists, but the index cannot name a vertebra. With both
   neighbours visible and all seven measures (the `flank` arm, regime `both`), the neighbour-only
   classifier names the body exactly in 52.2% of windows on typical columns (95% interval 50.7 to
   53.8, column-clustered) and within one level in 84.0%; chance is 5.0% exact and 14.5% within
   one. The first linear discriminant of the neighbour features is monotone down the column
   (no sign change, Spearman 1.00) and carries 80% of the between-class separation, so there is a
   formula, written out in section 1.3; but it names only 28.6% exactly, because its flattest
   adjacent step (L3 to L4) is 0.08 within-class standard deviations. Five directions are needed
   to reach 48%, and the curve is flat from eight on. The deliverable is a classifier with the
   index as its leading term, not an equation. Verdict on the strong result the brief asked for
   (a scalar formula, in one plane, naming a vertebra, holding across transitional anatomy):
   **no**, on the first clause already.

2. **Anomalous spines.** It holds in the same way on five of the six phenotypes and fails
   systematically on the sixth, exactly as the brief said to look for. Ranked by the worst
   phenotype, every one of the 15 arm-by-regime cells is worst on `t13`: 45.8% exact (44.3 to
   47.3) against 52.2% typical, and below the thirteenth rib-bearing body the model names every
   lumbar vertebra one level too cranial on average (mean signed offset L3 -1.04, L4 -1.24,
   L5 -1.55 levels). The shift is not scatter and is not removed by fitting on all six
   phenotypes or by abstaining on low confidence. It is a convention, not a shape failure:
   scored against the rib reading rather than the count from C2, `t13` names 51.7%, the same as
   typical. `six_lumbar` shows the shift at one body only (L5, -1.34), since L6 is not a class
   the typical-fitted model can say. `four_lumbar`, `lumbar_rib` and `no_rib_t12` are within one
   point of typical against the count.

3. **Latency.** Naming is not the latency problem. One window costs 0.018 ms through the
   classifier, 0.013 ms through the scalar index and 0.016 ms through the published-means rule,
   on one core of this container; a whole study of 15 cells, a sweep, a normalisation ladder and
   a mixed fit runs in 93 s, and the 127-subset enumeration in about a minute of fitting. A
   budget of tens of milliseconds a frame goes to segmentation and, since the answer is 3-D, to
   the registration that reads the missing axis.

4. **Dimensionality.** Statistically, five to eight discriminant directions; one is a formula
   that cannot name. Projectively, **3-D**: `both` beats the better single plane by 8.1 to 9.2
   points of exact naming over the whole grid of the unidentified correlation r (Imbens-Manski
   interval 7.2 to 10.0 points, 15 standard errors at the worst r), and beats the lateral plane
   by 14.2 to 15.3 points (13.3 to 16.2). The single-plane arms are an upper bound on an image,
   so the real gap is at least this. The route to the missing axis, registration as a
   measurement device and not as a localiser, is specified in section 4.3 and is not built.

The assumptions every number rests on are listed in section 5; what could not be settled, in
section 8.

## 0 How it was done

**The generator.** `panjabi.synthesize` with `rho` 0.5 (a patient's offsets correlated across
measures within a level), `scale_sd` 0.07 (a patient's overall size), `noise_mm` 1.0
(measurement noise per value), `blend` 0.5 (how far a transitional body takes its neighbour's
shape), `r_between` 0 in the main run and swept in section 4.2. Each column is one patient with
every level from C3 to L5 of the published table, altered by its phenotype: `four_lumbar` drops
L5, `six_lumbar` appends L6, `t13` inserts a thirteenth rib-bearing body before L1, `lumbar_rib`
and `no_rib_t12` blend the body at the junction.

**The truth.** The count from C2, as the package's `Column.cut` counts it: in `t13` the
thirteenth rib-bearing body is named L1, so what the shape says is T12 the count calls L1, and
every lumbar body below is one further. The rib reading is reported beside it where it differs
(`rib_ordinals`, held to `Column.cut` by `tests/test_neighbour.py`). The 22 named classes are
C3 to L5; L6 is an ordinal the typical-fitted model never says. The brief wrote 23 levels; the
generator has 22, since C2 has no end-plate row, and T13 and L6 exist only as a phenotype's
extra body (section 9).

**The feature.** For target i and offset d in the arm's set, the feature is log(v[i+d] / den_m)
for each measure m: `below1` d = +1, `above1` d = -1, `flank` d = -1 and +1, `flank2` d = -2, -1,
+1, +2, `with_target` d = -2 to +2 including 0 (the reference arm). The denominator den_m is
the external constant, the geometric mean of the published means of measure m over the levels,
fixed before any column is drawn, so the feature carries no position. The visible-median
normalisation of the brief's trap 2 is run as its own ladder (section 6.2). A window is eligible
when every body the arm needs exists in the column, so the marginal over true levels is uniform
over the names the arm can see, 20 for `flank` (C4 to L4), 21 for the single-neighbour arms, 18
for the five-body arms, 200 columns per phenotype each.

**Seeds and sizes.** Fit on 300 typical columns (seed 11); choose thresholds and the winning
subset on 150 columns per phenotype (seed 23); score on 200 columns per phenotype (seed 97),
4,000 windows per phenotype for `flank` (3,800 for `four_lumbar`, 4,200 for `six_lumbar` and
`t13`). Intervals are Wilson on the window count and, where the brief asks for a difference, the
column-clustered standard error, which is the honest one since windows of one column share its
offsets (0.009 for a phenotype's exact rate, 0.004 pooled over six).

**The solutions.** A: the first Fisher discriminant of the neighbour features, nearest class
mean along it. B: the published means with no fitting, a profiled Mahalanobis distance (one free
log-size per window, pooled relative variances), the independent check. C: a multinomial
logistic regression fitted by Newton's method with L2 1e-3, reusing `border.py`'s grouped
out-of-fold machinery (its binary fit agrees with `border.fit_logreg` to 0.02 in the test). D and
E: every subset of the seven measures chosen on the selection seed and scored on the scoring
seed, with the two single-plane sets named. F: C abstaining below a confidence chosen on the
selection seed for a target coverage. `LDA_full`, all discriminant directions, is drawn beside A
to show what the rest of the spectrum buys.

## 1 The mathematics

### 1.1 One table

Exact naming by solution C on typical columns, the worst phenotype's exact rate, and the worst
phenotype's within-one rate. The worst phenotype is `t13` in every cell. From
`neighbour.json`, `cells[].solutions.C`, drawn in `figures/neighbour_arms.csv`.

| arm | visible | lateral: typical / worst / worst within one | ap | both |
|---|---|---|---|---|
| below1 | i+1 | 0.262 / 0.236 / 0.528 | 0.320 / 0.290 / 0.638 | 0.393 / 0.345 / 0.717 |
| above1 | i-1 | 0.244 / 0.224 / 0.509 | 0.299 / 0.286 / 0.593 | 0.369 / 0.333 / 0.677 |
| flank | i-1, i+1 | 0.369 / 0.330 / 0.653 | 0.437 / 0.385 / 0.769 | 0.522 / 0.458 / 0.815 |
| flank2 | i-2 to i+2, not i | 0.499 / 0.427 / 0.750 | 0.584 / 0.513 / 0.871 | 0.671 / 0.577 / 0.900 |
| with_target | i-2 to i+2 | 0.538 / 0.464 / 0.774 | 0.592 / 0.539 / 0.877 | 0.702 / 0.605 / 0.906 |

Chance (section 6.3): 0.050 exact and 0.145 within one for `flank`, 0.048 and 0.138 for the
single-neighbour arms, 0.056 and 0.160 for the five-body arms. Wilson intervals on the typical
rates are plus or minus 0.015; the column-clustered standard errors are 0.006 to 0.014.

Two bodies below beat one body on either side by 15 points; the body below is worth two points
more than the body above in every regime (the lower end-plate of i+1 and the upper of i-1 both
abut i, and the lower end-plates are the wider ones in the table). Withholding the target from
the five-body window costs three points (`flank2` against `with_target`), so the target's own
shape is worth less than its second neighbours.

The other solutions on the `flank` arm (`cells[].solutions.A`, `.B`, `.LDA_full`):

| regime | A, the scalar index: typical / worst | B, published means, nothing fitted | B agrees with C on | LDA_full |
|---|---|---|---|---|
| lateral | 0.234 / 0.206 (six_lumbar) | 0.274 / 0.256 (t13) | 49% of windows | 0.374 / 0.335 |
| ap | 0.281 / 0.250 (six_lumbar) | 0.344 / 0.333 (t13) | 53% | 0.438 / 0.400 |
| both | 0.286 / 0.260 (six_lumbar) | 0.476 / 0.422 (t13) | 64% | 0.526 / 0.458 |

B, which fits nothing, is within five points of C in every regime with the same ordering
lateral < ap < both, which is the outside check on C (section 7). LDA_full matches C, so the
classifier is doing nothing a linear rule cannot.

### 1.2 Where it fails, level by level

Exact naming by true level, typical columns, `flank`, solution C (`figures/neighbour_levels.csv`):

| regime | C4 | C5 | C6 | C7 | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| both | .70 | .68 | .73 | .81 | .79 | .69 | .59 | .54 | .36 | .39 | .27 | .26 | .33 | .38 | .42 | .54 | .34 | .50 | .42 | .71 |
| ap | .72 | .63 | .56 | .74 | .59 | .64 | .45 | .32 | .33 | .30 | .27 | .23 | .33 | .30 | .42 | .42 | .23 | .33 | .30 | .61 |
| lateral | .54 | .54 | .66 | .58 | .61 | .40 | .38 | .39 | .17 | .34 | .17 | .17 | .15 | .24 | .18 | .42 | .20 | .43 | .26 | .55 |

The cervicothoracic junction and the lower lumbar bodies are named; the mid-thoracic bodies,
T5 to T9, are the floor at a quarter to a third, because the published end-plate widths there are
flat (24.5 to 24.9 mm from T2 to T5) and the neighbours of T7 look like the neighbours of T8.
L1 is low in every regime because its neighbour above, T12, is the one body the count and the
shape disagree about in two phenotypes, and because the T12/L1 step is small beside the L4/L5
step, which the package's junction work already found.

### 1.3 The formula

The first discriminant direction, in weights on the raw log-millimetre values of the
neighbours, with (+1) the body below and (-1) the body above, every index oriented to increase
down the column (the sign of an eigenvector is free; the AP weights are the negative of the
recorded ones). From `cells[].formula.weights` for `flank`; the class means and spreads of each
index are `figures/neighbour_formula.csv`.

All seven measures:

```
index_both = 2.20 log EPWu(+1) + 2.25 log EPWu(-1) + 1.71 log EPWl(+1) + 2.27 log EPWl(-1)
           + 1.10 log EPDu(+1) + 1.48 log EPDu(-1) + 0.43 log EPDl(+1) + 1.32 log EPDl(-1)
           + 0.47 log VBHp(+1) + 0.63 log VBHp(-1)
           - 1.16 log SCW(+1) - 1.93 log SCW(-1) - 0.78 log SCD(+1) - 0.87 log SCD(-1) + c
```

The AP plane:

```
index_ap = 2.86 log EPWu(+1) + 2.84 log EPWu(-1) + 2.22 log EPWl(+1) + 2.84 log EPWl(-1)
         + 0.76 log VBHp(+1) + 0.92 log VBHp(-1) - 1.13 log SCW(+1) - 1.94 log SCW(-1) + c
```

The lateral plane:

```
index_lat = 2.22 log EPDu(+1) + 2.64 log EPDu(-1) + 1.47 log EPDl(+1) + 2.65 log EPDl(-1)
          + 0.96 log VBHp(+1) + 1.32 log VBHp(-1) - 0.76 log SCD(+1) - 0.89 log SCD(-1) + c
```

EPWu and EPWl are the upper and lower end-plate widths, EPDu and EPDl their depths, VBHp the
posterior body height, SCW and SCD the canal width and depth; c is a constant that moves no name.
The signs match the table: end-plates and heights grow down the column, the canal narrows from
the cervical enlargement to the mid-thoracic and the weights on it are negative. The body above
weighs more than the body below in every measure, which is the asymmetry of 1.1.

What the index does and does not do (`cells[].formula.check`, `cells[].dimensionality`,
`figures/neighbour_formula_dims.csv`):

| regime | monotone in level | Spearman | share of separation in direction 1 | flattest adjacent step, in within-class SD | exact with 1 direction, typical / worst | with 2 | with 3 | with 5 | with 8 | all |
|---|---|---|---|---|---|---|---|---|---|---|
| both | yes, 0 sign changes | 1.000 | 0.80 (then 0.11, 0.04, 0.02) | 0.084 (L3 to L4) | 0.286 / 0.260 | 0.385 / 0.356 | 0.418 / 0.388 | 0.479 / 0.431 | 0.516 / 0.456 | 0.527 / 0.458 (14) |
| ap | yes, 0 | 1.000 | 0.84 (then 0.09, 0.03, 0.02) | 0.071 (T3 to T4) | 0.281 / 0.250 | 0.347 / 0.312 | 0.400 / 0.367 | 0.434 / 0.412 | 0.438 / 0.400 (8) | same |
| lateral | no, 1 sign change (C4 to C5) | 0.995 | 0.91 (then 0.04, 0.02) | 0.050 (C4 to C5) | 0.234 / 0.206 | 0.265 / 0.255 | 0.307 / 0.292 | 0.338 / 0.313 | 0.374 / 0.335 (8) | same |

A formula exists in the two planes that include the AP widths and it is monotone; but its
adjacent class means are 0.07 to 0.08 within-class standard deviations apart at the flattest
step and under 0.6 across most of the thoracic column (`step_over_within_sd` in the record), so
reading a level off it is a coin toss between neighbours over most of the spine. The second
direction, 11% of the separation in `both`, adds ten points; the fifth is still adding three. The
honest deliverable is the classifier, whose leading term is the index above.

## 2 Anomalous spines

### 2.1 Per phenotype, with the signed offsets

`flank`, regime `both`, solution C, 200 scoring columns per phenotype, against the count from C2
(`cells[].solutions.C.per_phenotype`, drawn in `figures/neighbour_offsets.csv`). The offset is
the named ordinal minus the true one: negative is a name too cranial.

| phenotype | n windows | exact (Wilson 95%) | within one | mean signed offset, levels | share at -2 / -1 / 0 / +1 / +2 | exact against the rib reading |
|---|---|---|---|---|---|---|
| typical | 4,000 | 0.522 (0.507 to 0.538) | 0.840 | -0.03 | .053 / .170 / .522 / .148 / .044 | 0.522 |
| four_lumbar | 3,800 | 0.499 (0.483 to 0.515) | 0.834 | +0.09 | .047 / .158 / .499 / .176 / .054 | 0.499 |
| six_lumbar | 4,200 | 0.489 (0.474 to 0.504) | 0.839 | -0.02 | .049 / .191 / .489 / .159 / .046 | 0.489 |
| t13 | 4,200 | 0.458 (0.443 to 0.473) | 0.815 | -0.17 | .073 / .224 / .458 / .134 / .046 | 0.517 |
| lumbar_rib | 4,000 | 0.523 (0.507 to 0.538) | 0.836 | -0.03 | .062 / .161 / .523 / .152 / .041 | 0.475 |
| no_rib_t12 | 4,000 | 0.519 (0.504 to 0.534) | 0.839 | +0.01 | .050 / .154 / .519 / .167 / .042 | 0.439 |

Beyond two levels either way is 4 to 6% in every phenotype; the largest offset seen is 12. The
same table for the two single planes is in the record (`flank`/`ap`: typical 0.437, worst `t13`
0.385, mean offset -0.20; `flank`/`lateral`: 0.369, 0.330, -0.08).

### 2.2 The one-level shift, found where the brief said to look

Mean signed offset by true level (`cells[].solutions.C.per_phenotype[].mean_offset_by_level`,
drawn in `figures/neighbour_shift.csv`):

| phenotype | T11 | T12 | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|---|---|
| typical | -0.01 | -0.21 | +0.29 | -0.10 | -0.25 | -0.56 | (not eligible) |
| six_lumbar | +0.09 | +0.07 | +0.31 | +0.03 | -0.19 | -0.47 | -1.34 |
| t13 | +0.10 | +0.03 | +0.33 | -0.40 | -1.04 | -1.24 | -1.55 |
| lumbar_rib | -0.01 | -0.12 | +0.12 | -0.09 | -0.34 | -0.50 | |
| no_rib_t12 | +0.23 | +0.04 | +0.43 | -0.07 | -0.39 | -0.48 | |

In `t13` the count names the thirteenth rib-bearing body L1 and everything below it one further
than its shape; the model, which reads only shape, follows the shape, and from L3 down its calls
sit one level cranial of the count's truth on average, with the bulk of the mass at exactly -1
(22% of all `t13` windows against 17% in typical). The brief called this the failure that makes
a level-naming device dangerous, confident and systematic; it is here, and it was predicted by
hand before the run (section 7). In `six_lumbar` the same shift appears at L5 alone, the one
body whose neighbour below is L6, a shape the model has no name for. Every phenotype drifts
cranial at L4 (-0.5), the last body the `flank` arm can name, because a name beyond L4 is rare
in the fit; that drift is a composition effect of the arm, not of the anatomy.

Against the rib reading the `t13` column is named at 51.7%, within one point of typical, and
`lumbar_rib` and `no_rib_t12` fall to 0.475 and 0.439: the model names the shape, and which
convention is right is not a question shape can answer. This is the finding to carry to any
device: a neighbour-only namer must be told which convention it is scored against, and on a
spine with a thirteenth rib it will be one level off the count unless the rib is read.

### 2.3 What does not remove it

- **Fitting on all six phenotypes** (`mixed_fit`, 50 columns of each, 6,050 fit rows): C names
  typical 0.516 and `t13` 0.454, with the shift unchanged (L3 -1.08, L4 -1.47, L5 -1.73), because
  the same pair of neighbour shapes is now labelled L2 in a typical column and L3 in a `t13` one,
  and the model splits the difference. A and B do not move either (0.262; 0.476 / 0.422).
- **Abstaining** (solution F, `cells[].selective`, `figures/neighbour_coverage.csv`): at 50%
  coverage `both` names typical 0.693 and `t13` 0.606 exactly, within one 0.94 in both; at 90%
  coverage 0.553 against 0.483. The gap between typical and `t13` is 6 to 9 points at every
  coverage, so confidence does not find the shifted calls; they are confident.
- **More context** does not close it either: `flank2` is worst on `t13` by 9 points
  (0.671 against 0.577) and `with_target` by 10.

## 3 Latency

Measured on this container (`latency` in the record; Linux, 4 CPUs, Python 3.13.17, numpy
2.5.3), single target, the median of repeated calls:

| operation | time | rate |
|---|---|---|
| name one window, solution C (softmax) | 0.018 ms | 56,000 /s |
| name one window, solution A (scalar index) | 0.013 ms | 80,000 /s |
| name one window, solution B (published means) | 0.016 ms | 63,000 /s |
| synthesize one column | 0.37 ms | 2,700 /s |
| fit C, 120 columns (2,400 windows) | 0.33 s | |
| fit C, 300 columns (6,000 windows) | 0.74 s | |
| fit C, 600 columns (12,000 windows) | 1.73 s | |
| fit A, 120 / 300 / 600 columns | 2.1 / 3.6 / 6.1 ms | |
| one cell of the study (fit C on 300 columns, score 1,200 columns, A, B, LDA, shuffle test) | 0.25 to 2.9 s | |
| the whole study, 15 cells, the r sweep, the normalisation ladder, the mixed fit | 93 s | |
| the enumeration, 127 fits of C | 0.5 to 2.8 s each, about a minute in all | |

The handoff's 0.40 ms per window for junction placement was on a Windows workstation; naming a
level from its neighbours is twenty times cheaper than that here because the feature is a
fourteen-number log vector and the model a 14-by-22 matrix. Whatever the clinical budget, it is
not spent here: SPINEPS segmentation of a volume is seconds to minutes, and the registration
step section 4.3 specifies is the only part of a 3-D answer with a latency of its own. Training
is cheap enough to refit per convention, per phenotype or per field of view at will.

## 4 Dimensionality

### 4.1 Statistical

Section 1.3's table: one direction is a monotone formula that names 28.6%; five reach 47.9%;
the curve is flat within one standard error from eight directions on (0.516 at 8, 0.527 at all
14, `figures/neighbour_formula_dims.csv`). So the information occupies five to eight directions
of the fourteen-dimensional neighbour space, and the brief's rule gives the classifier.

### 4.2 Projective: 3-D

The three regimes on the `flank` arm over all six phenotypes pooled, the unidentified
within-patient correlation r between measures swept over the grid 0, 0.2, 0.4, 0.6, 0.8, 0.9
(`r_sweep`, `identified`, `sign`, `profile_in_r`; drawn in `figures/neighbour_r.csv`). Column
clustered standard errors 0.0037 to 0.0039 at every point.

| regime | exact at r = 0 | at r = 0.9 | identified set over the grid | Imbens-Manski 95% |
|---|---|---|---|---|
| lateral | 0.359 | 0.366 | [0.359, 0.366] | [0.353, 0.372] |
| ap | 0.420 | 0.427 | [0.420, 0.427] | [0.414, 0.434] |
| both | 0.501 | 0.519 | [0.501, 0.519] | [0.495, 0.525] |

Every profile rises with r and none is informative: the largest gap across the grid is 0.86
standard errors (`profile_in_r`), so r is left as the set and never pointed.

| difference | over the grid | Imbens-Manski 95% | sign constant over the grid | margin at the worst r |
|---|---|---|---|---|
| both minus ap | [+0.081, +0.092] | [+0.072, +0.100] | yes | 15.4 se |
| both minus lateral | [+0.142, +0.153] | [+0.133, +0.162] | yes | 26.3 se |
| ap minus lateral | [+0.060, +0.063] | [+0.051, +0.073] | yes | 11.1 se |

The brief's decision rule: if one plane reaches `both` within the margin, 2-D. Neither does, at
any r, by eleven standard errors or more; and since a projection as a clean selection of
in-plane measures is an optimistic idealisation (no magnification, obliquity, cone-beam
distortion or superimposition is modelled), a real radiograph in one plane yields at most the
single-plane number. **The discriminating information is 3-D.** The AP plane is the better
single plane by six points, and the AP widths carry the leading direction of the formula
(section 1.3), so if only one shot can be had it is the AP; it names 42% of bodies from their
neighbours in this idealised form and 38.5% on `t13`.

The enumeration (solutions D and E, `enumerate.json`, `figures/neighbour_subsets.csv`) says the
same from the other side. All 127 subsets of the seven measures, `flank`, chosen by the worst
phenotype on the selection seed and scored on the scoring seed:

| k | chosen on the selection seed | scored, worst phenotype | best on the scoring seed, for reference |
|---|---|---|---|
| 1 | EPWu | 0.259 (four_lumbar) | the same |
| 2 | EPWu, EPDl | 0.338 (t13) | the same |
| 3 | EPWu, EPWl, EPDl | 0.388 (t13) | the same |
| 4 | EPWu, EPWl, EPDu, EPDl (the four end-plates, two planes mixed) | 0.409 (t13) | EPWu, EPWl, EPDl, SCW 0.412 |
| 5 | EPWu, EPWl, EPDl, VBHp, SCW | 0.425 (t13) | 0.427 |
| 6 | EPWu, EPWl, EPDu, VBHp, SCW, SCD | 0.435 (t13) | 0.448 |
| 7 | all seven | 0.458 (t13) | the same |
| | the AP set (EPWu, EPWl, VBHp, SCW) | 0.385 (t13) | |
| | the lateral set (EPDu, EPDl, VBHp, SCD) | 0.330 (t13) | |

The full set wins on both seeds; no superset scores worse than any of its subsets by two
standard errors (`n_supersets_worse_by_2se` 0), so adding a measure never hurt here. The best
set of four is not a plane: it is the four end-plate measures, two from each plane, 2.4 points
above the AP set and 8 above the lateral. A single width, EPWu of the two neighbours, already
names 26%, five times chance. The selection seed and the scoring seed agree to within 1.5 points
on every row, so the enumeration has not overfitted its choice.

### 4.3 The route to the third axis, specified and not built

Since `both` beats each plane, the missing in-plane measures of a fluoroscopic shot are to be
read from a preoperative CT through registration. The claim is narrow and must stay narrow:
registration here is a **measurement device** for the out-of-plane measures of the few visible
bodies, not a localiser; it needs to be locally right over two to five bodies, never globally
right over the column, and it names nothing. Registration-based level localisation, which needs
a globally correct correspondence, peaks near 73% naming accuracy in the published work, and
that number is not this route's.

The sequence, each stage synthetic first, each with a test that absolute position cannot reach
the next stage:

1. **Segment the CT** with SPINEPS (the owner's production segmenter; MOOSE only when
   replicating FleXray's own data) and measure the seven quantities per visible level with
   `measure_levels.py`, as this package does now; the per-level values are the 3-D truth for
   that patient.
2. **Project**: from the fluoroscopic pose, the in-plane four (AP: EPWu, EPWl, VBHp, SCW;
   lateral: EPDu, EPDl, VBHp, SCD) are measured on the image; the first synthetic version is the
   clean selection used here, the second adds magnification and obliquity as a scale and a
   cosine per body, the third superimposition as noise on the canal measures.
3. **Register locally**: align the CT's two to five visible bodies to the image by the in-plane
   measures and the inter-body distances, a rigid or piecewise-rigid fit over a window, and read
   each visible body's out-of-plane three (AP shot: EPDu, EPDl, SCD) from the CT at the matched
   body. The quantity to measure for this stage is the error of those three values at the
   matched body, in millimetres, against the CT's own measurement, as a function of the
   registration's precision; a window that matches the wrong body by one level is the failure
   that matters, and it must be reported as an offset distribution, as section 2.1 does.
4. **Name**: the seven measures of each neighbour into the classifier of section 1, under the
   convention the device is scored against (section 2.2).

What decides whether the route is worth building is stage 3's number: if the out-of-plane
measures come back with errors of the order of the 1 mm noise used here, the `both` rates of
section 1.1 apply; if they come back at the level of the between-level differences (2 to 3 mm
for the end-plate depths across the thoracic column), the route buys nothing over the AP shot.
That measurement has not been made.

## 5 Assumptions every number rests on

- The published means and spreads are the whole truth of a level's shape; a patient is a
  shared size (7%), a shared offset across measures within a level (rho 0.5), and 1 mm of
  noise per value. None of rho, scale_sd, noise_mm or blend is given by the literature; rho and
  noise were chosen as the package's existing synthetic corpus uses them, and the r sweep
  shows the rates move by under two points across the whole range of r.
- Adjacent levels of one patient are correlated only through the shared size and offsets; a
  patient's own gradient down the column (a long thorax, a short lumbar spine) is not modelled,
  and it is the thing a neighbour-only rule would be most exposed to.
- The transitional bodies are blends at 0.5 between the two shapes; a real transitional body may
  be neither.
- A projection is a clean selection of in-plane measures (section 4.2), an upper bound.
- The classes are the 22 of the table; L6 is never named.
- The fit is on typical columns only, except where the mixed fit says otherwise.

## 6 The three traps

### 6.1 Position never reaches the model

`shuffle_invariance`: for each of 50 trials the target's neighbourhood is moved to another
place in a reshuffled column and the prediction compared. Every cell of the study, every rung of
the normalisation ladder and the mixed fit report 50 of 50 identical (`cells[].shuffle`,
`normalisation[].shuffle`, `mixed_fit.shuffle`). The unit test `TestPosition` holds the features
themselves identical under the move for every arm and every normalisation over 20 trials, and
the three fitted solutions invariant over 30. The grouped out-of-fold rate on the fit seed
(`oof_typical_exact_rate`: lateral 0.344, ap 0.431, both 0.510) is within two points of the
fresh-seed rate, so the fit is not memorising columns.

### 6.2 The visible median leaks position, and it buys nothing

The brief's trap 2, run as a ladder: each measure divided by its median over the k bodies on
either side of the target, the target excluded, clipped at the ends of the column
(`normalisation`, `figures/neighbour_normalisation.csv`); `flank`, `both`, solution C:

| bodies in the median | exact, typical | exact, worst (t13) |
|---|---|---|
| 2 | 0.274 | 0.236 |
| 4 | 0.371 | 0.295 |
| 6 | 0.420 | 0.338 |
| 10 | 0.495 | 0.401 |
| the whole column | 0.610 | 0.515 |
| the external constant (no median) | 0.522 | 0.458 |

A median over ten bodies or fewer is worse than a fixed constant, because the median removes
the between-level signal along with the patient's size; the whole-column median adds nine
points over the constant, which is the most that removing the patient's size can be worth, and
is also the most that a normalisation could smuggle in as position. The shuffle test is 50 of 50
on every rung, so the median arm carries no absolute position either; what it carries is the
column's composition, which a limited field of view does not have. The constant is the right
arm for a device.

### 6.3 Chance is stated

The marginal over true levels is uniform over the names the arm can see (section 0), 200
columns per phenotype each; so chance is 1/20 = 0.050 exact for `flank`, and within one
(3k - 2)/k^2 = 0.145; 1/21 and 0.138 for the single-neighbour arms; 1/18 and 0.160 for the
five-body arms (`chance` in the record). The majority rule gives the same. Every exact rate in
this report is at least five times chance and every within-one rate at least three times.

## 7 Checks outside the computation

- Solution B fits nothing: it is the published means and spreads read as a distance. It names
  within five points of the fitted classifier in every regime with the same ordering of the
  regimes, and agrees with it on 64% of windows; the fitted model is not finding something the
  table does not hold.
- The formula's signs are the table's trends: end-plates and heights grow down the column, the
  canal narrows to the mid-thoracic. The level-by-level floor at T5 to T9 is where the printed
  end-plate widths are flat to 0.4 mm.
- The one-level shift in `t13` was written down as the expected finding before the run (the
  brief's last section) and appears at the predicted levels with the predicted sign.
- The binary case of the Newton softmax agrees with the package's existing `fit_logreg` to
  0.02 (`TestFit`), and the noise-free column at the published means is named exactly at every
  level by B for every arm and regime (`TestPublished`).
- Chance is computed from the marginal, not assumed.

## 8 What could not be settled

- The absolute rates depend on rho, scale_sd, noise_mm and blend, which no published source
  gives; the study shows the ordering of arms, regimes and phenotypes is stable under r, and
  nothing more about the other three.
- A patient's own gradient down the column is not in the generator, and a neighbour-only rule
  is the one most exposed to it; whether it helps (a consistent patient) or hurts (a patient
  whose thoracic bodies run large) is not known.
- The projection is idealised; the 2-D rates are upper bounds and nothing here says how far
  above an image they sit.
- The registration route's deciding number, the millimetre error of the out-of-plane measures
  read at the matched body, is unmeasured.
- L6 cannot be named by a model fitted on the 22 classes, and the choice between the count's
  convention and the rib reading on a spine with a thirteenth rib is not a shape question.
- The enumeration ran on this container as one shard; the sharded grid run the command
  supports was not needed and was not sent.

## 9 Found on the way, written down, not fixed

- The brief says 23 levels, C2 to L5 as the table's canal rows run; C2 carries no end-plate row
  (the dens occupies it), so `panjabi.py` and this study carry 22 (C3 to L5), and T13 and L6
  arise only inside a phenotype.
- `HANDOFF.md` expects 70 tests with one matplotlib error from `python -m unittest discover -s
  tests`; this container ran 78 and all passed before this study, 89 with it.
- The handoff's latency table is from a Windows workstation and reads three to four times
  slower than this container; neither is the device.
- The first build of this study's own figures printed a doubled percent sign in two captions;
  fixed here, since the file is this study's.

## 10 Figures

All under `records/neighbour-2026-10-26/figures/`, drawn by `bordercall/neighbour_figures.py`
from `neighbour.json` (and `enumerate.json` for the last), each as PDF with the type embedded
and no date, PNG at 300 dpi, a CSV of the numbers drawn and its caption; `FIGURES.md` carries the
sha256 of every input. Captions are under sixty words; the argument is in the text above.

| figure | what it shows | section |
|---|---|---|
| neighbour_arms | exact naming by arm and regime; typical, worst phenotype, worst within one | 1.1 |
| neighbour_levels | exact naming by true level, three regimes | 1.2 |
| neighbour_formula | the index by level with its spread; exact against directions kept; the share per direction | 1.3, 4.1 |
| neighbour_offsets | the signed offset distribution per phenotype | 2.1 |
| neighbour_shift | the mean signed offset by level and phenotype | 2.2 |
| neighbour_normalisation | exact against the number of bodies in the median, with the constant as the line | 6.2 |
| neighbour_coverage | exact against coverage for the abstaining rule | 2.3 |
| neighbour_r | the r sweep with the identified sets and Imbens-Manski intervals | 4.2 |
| neighbour_subsets | every subset's worst-phenotype rate against its size | 4.2 |

## 11 Files

- `bordercall/neighbour.py`: the study; `bordercall/neighbour_figures.py`: the figures;
  `bordercall/run.py`: the commands `neighbour`, `neighbour-enumerate`, `neighbour-figures`.
- `tests/test_neighbour.py`: eleven tests, the position test among them.
- `records/neighbour-2026-10-26/neighbour.json`, `models.json`, `enumerate.json`, `figures/`.
- `docs/NEIGHBOUR_IDENTITY_STUDY.md`: the brief this answers.
