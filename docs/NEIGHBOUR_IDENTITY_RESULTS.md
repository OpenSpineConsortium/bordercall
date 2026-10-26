# Naming a vertebra from its field of view: results

**Status: done, synthetic.** This is the answer to `docs/NEIGHBOUR_IDENTITY_STUDY.md`, the brief.
Source: the thread "Finish CNS slides with junction predictor", 2026-10-26, the owner's ask of
05:44 UTC, continued on the owner's word of 06:31 UTC that the problem carries no arbitrary
constraint: the body being named is measurable too. The first study withheld the target and
named a body from its neighbours; the continued study names a field of view as a whole, the
target in it, and keeps the neighbour-only arms as the obscured case. A review by four
independent readers of the first write-up, each told to refute one verdict against the records
and the code, corrected it in the places section 12 lists; every correction is in the text
below. Everything is drawn from columns synthesized from Panjabi's published means and spreads
(`bordercall/reference/panjabi_full_spine.csv`). No CT, no label, no corpus, no data access was
used. The code is `bordercall/neighbour.py`, `bordercall/neighbour_more.py` and
`bordercall/neighbour_figures.py`; the records are under `records/neighbour-2026-10-26/`; the
tests are `tests/test_neighbour.py`.

Every number here is in one of five files, written by the commands below, run from
`bordercall/`:

```
python run.py neighbour --outdir ../records/neighbour-2026-10-26
python run.py neighbour-enumerate --arm flank --shard 0 --of 1 --out ../records/neighbour-2026-10-26/enumerate-shard0.json
python run.py neighbour-enumerate --gather ../records/neighbour-2026-10-26/enumerate-shard0.json --out ../records/neighbour-2026-10-26/enumerate.json
python run.py neighbour-more --outdir ../records/neighbour-2026-10-26
python run.py neighbour-figures --json ../records/neighbour-2026-10-26/neighbour.json --enumerate-json ../records/neighbour-2026-10-26/enumerate.json --more-json ../records/neighbour-2026-10-26/neighbour_more.json --outdir ../records/neighbour-2026-10-26/figures
```

The first writes `neighbour.json` (the neighbour-only study, 93 s on this container) and
`models.json` (the fitted weights of every cell). The second and third write
`enumerate-shard0.json` (all 127 subsets of the seven measures with the time of every fit) and
`enumerate.json`, its gathered form; the gather deletes the shard file, so the shard was run
again afterwards and kept, since the gathered record carries no times. The fourth writes
`neighbour_more.json` (the field named as a whole, the nonlinear classifier, the size of the
fit, the r sweep per width, the latency; 567 s). The fifth draws the ten figures and writes
`figures/FIGURES.md`, with the sha256 of each record and each code file, and a CSV beside every
figure holding the numbers drawn. Beside each table below is the file and the key the numbers
come from.

## The four verdicts

1. **The mathematics.** With the target measurable, the problem is naming a field of view as
   a whole, and it is a classification over every visible body, not a formula. The direct
   classifier on the seven measures of each visible body (solution C on the field) names the
   target exactly in 37.0% of windows from its own body alone, 57.5% from three bodies, 70.2%
   from five, 77.4% from seven and 83.5% from nine, both planes, typical columns (within one
   level 70.2% to 98.7%; chance 4.5% to 7.1% exact, 13% to 20% within one), and the published
   means with nothing fitted reach 81.0% at nine bodies. Hiding the target from a nine-body
   field costs 1.6 points, so the field is what names a body, not any one neighbour. From the
   two flanking bodies alone (the obscured case, the first study) the rate is 52.2% (Wilson
   50.7 to 53.8; column-clustered 50.5 to 54.0) and within one level 84.0%. A monotone scalar
   index of the neighbours exists in `both` (Spearman 1.00, pooled over the six phenotypes; on
   typical columns alone its flattest step is 0.11 within-class SD, and the two single-plane
   indices each show two sign changes of under 0.05 SD) and names 28.6%; five to eight
   directions are needed. A one-hidden-layer network buys nothing over the linear classifier
   when the target is visible (+1.1, +1.2 and -0.3 points in the three regimes) and four to
   five points when it is not. Verdict on the strong result the brief asked for (a scalar
   formula, in one plane, naming a vertebra, holding across transitional anatomy): **no**, on
   the first clause already.

2. **Anomalous spines.** The classifier is worst on `t13` in every cell of both studies (the
   15 neighbour-only cells, the 15 field cells and the 12 obscured ones): on the field at five
   bodies 60.5% against 70.2% typical, at nine 72.6% against 83.5%; from the two flanking
   bodies 45.8% against 52.2%. Part of every deficit on a column with an extra body is an
   artefact of the fit that the review found: a classifier fitted on typical columns never
   learns the last name a longer column carries (L5 on `flank`, L4 at five bodies, L2 at nine),
   so one body in every `six_lumbar` and `t13` column is unnameable by construction. With that
   body excluded, `six_lumbar` is within one to two points of typical everywhere and `t13`
   stays four to six points below (`flank` 48.1% against 52.2%; five bodies 63.9% against
   70.2%; nine 77.8% against 83.5%). What remains in `t13` is the count convention, exactly as
   the brief said to look for: below the blended thirteenth rib-bearing body the model follows
   the shape and names one level cranial of the count (`flank`: mean signed offset L3 -1.04,
   L4 -1.24; five bodies: the count's L3 named exactly 28% with offset -0.82), and at the widest
   field the loss spreads to every level whose field holds the extra body. Scored against the
   rib reading instead of the count, `t13` names 51.7% on `flank` and 79.3% at nine bodies. A
   mixed fit, abstention and width do not remove it.

3. **Latency.** Naming is not the latency problem. One field costs 0.016 to 0.030 ms through
   the direct classifier and 0.04 to 0.27 ms through the factorised decoder; one window costs
   0.018 ms through the neighbour-only classifier, 0.013 ms through the scalar index and 0.016
   ms through the published-means rule; means of repeated calls on this container, thread
   count not pinned. The whole continued study runs in 567 s and the neighbour-only one in
   93 s. Whatever the clinical budget, it goes to segmentation and, since the answer is 3-D, to
   the registration that reads the missing axis.

4. **Dimensionality.** Statistically, five to eight discriminant directions of the neighbour
   features, and nothing nonlinear once the target is visible. Projectively, **3-D at every
   width**: `both` beats the AP plane by 5.9 to 6.8 points at one body, 9.0 to 9.7 at five and
   8.1 to 8.7 at nine over the grid 0 to 0.9 of the unidentified correlation r (Imbens-Manski
   intervals 5.2 to 7.5, 7.8 to 10.9 and 6.6 to 10.2; 9 to 16 standard errors at the worst r),
   and the lateral plane by 11.7 to 15.6 points (17 to 29 standard errors); from the flanking
   bodies alone by 8.1 to 9.2 (15 standard errors). The gap between the idealised `both` arm
   and a real single-plane image is at least this; whether a device reaches the `both` rate
   depends on the registration route's deciding number, which is unmeasured (section 4.3).

The assumptions every number rests on are listed in section 5; what could not be settled, in
section 8; what the review corrected, in section 12.

## 0 How it was done

**The generator.** `panjabi.synthesize` with `rho` 0.5 (a patient's offsets correlated across
measures within a level), `scale_sd` 0.07 (a patient's overall size), `noise_mm` 1.0
(measurement noise per value), `blend` 0.5 (how far a transitional body takes its neighbour's
shape), `r_between` 0 in the main runs and swept in section 4.2. Each column is one patient with
every level from C3 to L5 of the published table, altered by its phenotype: `four_lumbar` ends at
L4, `six_lumbar` appends L6, `t13` inserts a thirteenth rib-bearing body before L1 whose shape is
the 0.5 blend of T12 and L1, `lumbar_rib` and `no_rib_t12` blend the body at the junction.

**The truth.** The count from C2, as the package's `Column.cut` counts it: in `t13` the inserted
body is named L1 and every body below it one further than its shape. The rib reading is reported
beside it where it differs (`rib_ordinals`, held to `Column.cut` by `tests/test_neighbour.py`);
the inserted body has no rib name and is left out of the rib column. The 22 named classes are C3
to L5; the brief wrote 23 levels, but C2 has no end-plate row, so the generator carries 22
(section 9), and T13 and L6 exist only as a phenotype's extra body.

**The edge names.** A model fitted on typical columns has training rows only for the targets a
typical column gives the arm: on `flank` the names C4 to L4, on a field of five bodies C5 to
L3, of nine bodies C7 to L1. The fit never sees the names at either edge and the fitted
classifier never says them (reproduced from the saved weights: the named classes lead the
unseen ones by ten logits or more). A `six_lumbar` or `t13` column has one body more, so its
last target carries a name the fit never learnt and is wrong by construction, 200 windows per
cell; `four_lumbar` has one body fewer and loses a target instead. The review found this
(section 12); every anomalous rate below is given both as recorded and with that one body
excluded, and the fix, cutting the fit columns short at random so that every name is a label,
is left for the next run (section 9).

**The features.** For target i and offset d in the arm's set, the feature is log(v[i+d] / den_m)
for each measure m. The neighbour-only arms are `below1` d = +1, `above1` d = -1, `flank` d = -1
and +1, `flank2` d = -2, -1, +1, +2, `with_target` d = -2 to +2 including 0. The field arms of the
continued study are the bodies from -h to +h with the target (2h + 1 bodies, h from 0 to 4) and
without it (the obscured case, 2h bodies). The denominator den_m is the external constant, the
geometric mean of the published means of measure m over the levels, fixed before any column is
drawn, so the feature carries no position. The visible-median normalisation of the brief's trap
2 is run as its own ladder (section 6.2). A window is eligible when every body the arm needs
exists in the column, so the marginal over true levels is uniform over the names the arm can see
on a typical column: 22 for one body, 20 for `flank` and three bodies, 18 for five, 16 for seven,
14 for nine, 200 columns per phenotype each.

**Seeds and sizes.** Fit on 300 typical columns (seed 11); choose thresholds, the winning subset
and the hidden width on 150 columns per phenotype (seed 23); score on 200 columns per phenotype
(seed 97), 4,000 windows per phenotype for `flank` (3,800 for `four_lumbar`, 4,200 for
`six_lumbar` and `t13`), 2,800 at nine bodies. Intervals are Wilson on the window count and,
where the brief asks for a difference, the column-clustered standard error, which is the honest
one since windows of one column share its offsets (0.009 to 0.016 for a phenotype's exact rate,
0.003 to 0.007 pooled over six).

**The solutions.** A: the first Fisher discriminant of the neighbour features, nearest class
mean along it. B: the published means with no fitting, a profiled Mahalanobis distance (one free
log-size per window, pooled relative variances), the independent check. C: a multinomial
logistic regression fitted by Newton's method with L2 1e-3, reusing `border.py`'s grouped
out-of-fold machinery (its binary fit agrees with `border.fit_logreg` to 0.02 in the test),
run on the neighbour features in the first study and on the whole field in the continued one
(`C_field`). D and E: every subset of the seven measures chosen on the selection seed and scored
on the scoring seed, with the two single-plane sets named. F: C abstaining below a confidence
chosen on the selection seed for a target coverage. G: the field decoded, a 22-class model of a
body's own seven measures fitted once (`train_self`) and the product of its posteriors along the
field at the names a candidate implies, with `G_B` the same decoder on the published means and
nothing fitted. H: one hidden layer of tanh units on the same features as C, width 32, 64 or
128 chosen on the selection seed, full-batch Adam, 1,500 steps. `LDA_full`, all discriminant
directions, is drawn beside A to show what the rest of the spectrum buys.

## 1 The mathematics

### 1.1 Neighbours only, the obscured case: one table

Exact naming by solution C on typical columns, the worst phenotype's exact rate, and the lowest
within-one rate over the six phenotypes. `t13` is the worst phenotype on exact naming in every
cell; the lowest within-one rate is `t13`'s in nine cells and `six_lumbar`'s, `four_lumbar`'s or
`lumbar_rib`'s in the other six. From `neighbour.json`, `cells[].solutions.C`, drawn in
`figures/neighbour_arms.csv`.

| arm | visible | lateral: typical / worst / lowest within one | ap | both |
|---|---|---|---|---|
| below1 | i+1 | 0.262 / 0.236 / 0.528 | 0.320 / 0.290 / 0.638 | 0.393 / 0.345 / 0.717 |
| above1 | i-1 | 0.244 / 0.224 / 0.509 | 0.299 / 0.286 / 0.593 | 0.369 / 0.333 / 0.677 |
| flank | i-1, i+1 | 0.369 / 0.330 / 0.653 | 0.437 / 0.385 / 0.769 | 0.522 / 0.458 / 0.815 |
| flank2 | i-2 to i+2, not i | 0.499 / 0.427 / 0.750 | 0.584 / 0.513 / 0.871 | 0.671 / 0.577 / 0.900 |
| with_target | i-2 to i+2 | 0.538 / 0.464 / 0.774 | 0.592 / 0.539 / 0.877 | 0.702 / 0.605 / 0.906 |

Chance (section 6.3): 0.050 exact and 0.145 within one for `flank`, 0.048 and 0.138 for the
single-neighbour arms, 0.056 and 0.160 for the five-body arms. Wilson intervals on the typical
rates are plus or minus 0.013 to 0.016; the column-clustered standard errors are 0.006 to 0.014.

Two bodies on either side beat one body on either side by 13 to 15 points; the body below is
worth two points more than the body above in every regime (the record says that and no more;
the features read both end-plates of each neighbour, so the abutting plate is not what the model
sees). Withholding the target from the five-body window costs one to four points (`flank2`
against `with_target`: 3.9 lateral, 0.8 ap, 3.1 both), so the target's own shape is worth less
than its second neighbours; section 1.4 says what it is worth on wider fields.

The other solutions on the `flank` arm (`cells[].solutions.A`, `.B`, `.LDA_full`):

| regime | A, the scalar index: typical / worst | B, published means, nothing fitted | B agrees with C on | LDA_full |
|---|---|---|---|---|
| lateral | 0.234 / 0.206 (six_lumbar) | 0.274 / 0.256 (t13) | 49% of windows | 0.374 / 0.335 |
| ap | 0.281 / 0.250 (six_lumbar) | 0.344 / 0.333 (t13) | 53% | 0.438 / 0.400 |
| both | 0.286 / 0.260 (six_lumbar) | 0.476 / 0.422 (t13) | 64% | 0.527 / 0.458 |

B, which fits nothing, is within five points of C in `both` (4.6) and within ten in each single
plane (9.5 lateral, 9.3 ap), with the same ordering lateral < ap < both, which is the outside
check on C (section 7); on the field it comes within 2.5 points (section 1.4). LDA_full matches
C, so the classifier is doing nothing a linear rule cannot.

### 1.2 Where it fails, level by level

Exact naming by true level, typical columns, `flank`, solution C (`figures/neighbour_levels.csv`):

| regime | C4 | C5 | C6 | C7 | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| both | .70 | .68 | .73 | .81 | .79 | .69 | .59 | .54 | .36 | .39 | .27 | .26 | .33 | .38 | .42 | .54 | .34 | .50 | .42 | .71 |
| ap | .72 | .63 | .56 | .74 | .59 | .64 | .45 | .32 | .33 | .30 | .27 | .23 | .33 | .30 | .42 | .42 | .23 | .33 | .30 | .61 |
| lateral | .54 | .54 | .66 | .58 | .61 | .40 | .38 | .39 | .17 | .34 | .17 | .17 | .15 | .24 | .18 | .42 | .20 | .43 | .26 | .55 |

The cervicothoracic junction and the lower lumbar bodies are named; the mid-thoracic bodies,
T5 to T9, are the floor, 0.26 to 0.39 in `both` and 0.15 to 0.34 in the lateral plane. The
floor is not where the printed end-plate widths are flat: they are flat from T1 to T5 (24.5 to
24.9 mm), where naming is good, and rise 1.1 to 1.7 mm a level over T5 to T9. What the record
says is that the index steps between adjacent thoracic classes are 0.4 to 0.8 within-class
standard deviations (`step_over_within_sd`), against a population spread of about 2.4 mm and 1 mm
of noise, so neighbouring thoracic bodies overlap. L1 is low in every regime (0.34, 0.23, 0.20);
the record gives no cause, and the two the first write-up offered (a small T12/L1 step, the
phenotypes' disagreement about T12) are contradicted by it: the T12 to L1 step is 0.42
within-class SD, larger than the three lumbar steps below it, and this table is typical columns
only.

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
carries the larger weight in every measure but EPWu in the AP plane; a discriminant weight
reflects the within-class covariance as much as a neighbour's information, so nothing is read
into that.

What the index does and does not do (`cells[].formula.check`, `cells[].dimensionality`,
`figures/neighbour_formula_dims.csv`). The monotone check in the record is computed on the
scoring rows of all six phenotypes pooled, labelled by the count; the typical-column figures
beside it were recomputed by the review with the module's own functions (section 12):

| regime | monotone, pooled over phenotypes | Spearman | on typical columns alone | share of separation in direction 1 | flattest adjacent step, in within-class SD | exact with 1 direction, typical / worst | with 2 | with 3 | with 5 | with 8 | all |
|---|---|---|---|---|---|---|---|---|---|---|---|
| both | yes, 0 sign changes | 1.000 | monotone, flattest step 0.113 (L3 to L4) | 0.80 (then 0.11, 0.04, 0.02) | 0.084 (L3 to L4) | 0.286 / 0.260 | 0.385 / 0.356 | 0.418 / 0.388 | 0.479 / 0.431 | 0.516 / 0.456 | 0.527 / 0.458 (14) |
| ap | yes, 0 | 1.000 | 2 sign changes, T3 to T4 at -0.018 | 0.84 (then 0.09, 0.03, 0.02) | 0.071 (T3 to T4) | 0.281 / 0.250 | 0.347 / 0.312 | 0.400 / 0.367 | 0.434 / 0.412 | 0.438 / 0.400 (8) | same |
| lateral | no, 1 sign change (L3 to L4) | 0.995 | 2 sign changes, C4 to C5 at -0.047 and L3 to L4 at -0.070 | 0.91 (then 0.03, 0.02) | 0.050 (C4 to C5) | 0.234 / 0.206 | 0.265 / 0.255 | 0.307 / 0.292 | 0.338 / 0.313 | 0.374 / 0.335 (8) | same |

A monotone formula exists in `both`; in the two single planes the index is monotone up to steps
indistinguishable from zero (0.02 to 0.07 within-class SD), which is the same thing as not being
monotone for the purpose of reading a level off it. Its adjacent class means are under 0.6
within-class SD apart across most of the thoracic column (`step_over_within_sd`), so a level
read off the index is a coin toss between neighbours over most of the spine. The second
direction, 11% of the separation in `both`, adds ten points; the fifth is still adding three;
from eight to all fourteen the typical curve gains one more point (0.516 to 0.527, 1.2
column-clustered standard errors) and the worst-phenotype curve is flat (0.456 to 0.466). The
honest deliverable is the classifier, whose leading term is the index above.

### 1.4 The field named as a whole, the target in it: the main arm

The owner's word of 06:31 UTC removed the constraint of the first study. Here the field of view
is 2h + 1 bodies with the target in the middle, h from 0 to 4, every visible body contributing
its measures of the regime, and the question is how well the field as a whole names the body in
the middle. Three solutions on every field: the direct classifier C on the whole field
(`C_field`), the decoder G, which names each visible body from its own measures by a model
fitted once and multiplies the posteriors along the field at the names a candidate implies, and
`G_B`, the same decoder on the published means with nothing fitted. From `neighbour_more.json`,
`field[].arms.with_target`, drawn in `figures/neighbour_field.csv`.

Exact naming on typical columns, the worst phenotype's exact rate (always `t13`) and the typical
within-one rate, solution C on the field:

| bodies in the field | names it can say | lateral: typical / worst / within one | ap | both | chance exact / within one |
|---|---|---|---|---|---|
| 1, the target alone | 22 | 0.242 / 0.217 / 0.518 | 0.299 / 0.280 / 0.640 | 0.370 / 0.327 / 0.702 | 0.045 / 0.132 |
| 3 | 20 | 0.429 / 0.378 / 0.701 | 0.471 / 0.418 / 0.794 | 0.575 / 0.492 / 0.857 | 0.050 / 0.145 |
| 5 | 18 | 0.538 / 0.464 / 0.787 | 0.592 / 0.539 / 0.892 | 0.702 / 0.605 / 0.920 | 0.056 / 0.160 |
| 7 | 16 | 0.596 / 0.527 / 0.837 | 0.672 / 0.624 / 0.938 | 0.774 / 0.688 / 0.961 | 0.062 / 0.180 |
| 9 | 14 | 0.659 / 0.577 / 0.883 | 0.743 / 0.662 / 0.965 | 0.835 / 0.726 / 0.987 | 0.071 / 0.204 |

Wilson intervals on the typical rates are plus or minus 0.013 to 0.018; the column-clustered
standard errors are 0.006 to 0.018. The names a field can say shrink with its width because a
field must fit inside the column (a typical column has 22 bodies), so the rows are over
different sets of true levels and chance rises down the table; the rates are nonetheless far
apart. A body named from its own seven measures alone is right 37% of the time, eight times
chance; every pair of bodies added to the field adds 6 to 20 points, with the gain shrinking
from 20 at the first pair to 6 at the fourth.

The obscured case, the same fields with the target hidden (`field[].arms.obscured`, C on the
field; the two-body row is the `flank` arm of the first study on the same rows):

| bodies visible, target hidden | lateral: typical / worst | ap | both |
|---|---|---|---|
| 2 | 0.369 / 0.330 | 0.437 / 0.385 | 0.522 / 0.458 |
| 4 | 0.499 / 0.427 | 0.584 / 0.513 | 0.671 / 0.577 |
| 6 | 0.573 / 0.496 | 0.659 / 0.604 | 0.753 / 0.664 |
| 8 | 0.646 / 0.546 | 0.718 / 0.645 | 0.819 / 0.702 |

The target's own shape is worth 5.3 points when the field is three bodies, 3.1 at five, 2.1 at
seven and 1.6 at nine (`both`, typical, the row above against the row with one body more). A
device that has the target in view loses little by failing to measure it once it has four
bodies on either side; what names a body is the field.

The decoder beside the classifier, `both`, typical / worst (`field[].arms.with_target.G`, `.G_B`):

| bodies in the field | C on the field | G, the fitted decoder | G_B, the published means decoded, nothing fitted |
|---|---|---|---|
| 1 | 0.370 / 0.327 | 0.370 / 0.327 | 0.314 / 0.292 |
| 3 | 0.575 / 0.492 | 0.548 / 0.479 | 0.535 / 0.462 |
| 5 | 0.702 / 0.605 | 0.645 / 0.570 | 0.666 / 0.579 |
| 7 | 0.774 / 0.688 | 0.699 / 0.621 | 0.744 / 0.658 |
| 9 | 0.835 / 0.726 | 0.744 / 0.662 | 0.810 / 0.705 |

At one body G and C are the same model, as the test holds them to be. From three bodies on the
direct classifier beats the factorised decoder by 3 to 9 points: the product of per-body
posteriors treats the bodies as independent given their names, and they are not (a patient's
size and offsets run through the whole field), which the classifier reads from the joint
features. The published means decoded, with nothing fitted at all, come within 2.5 points of
the fitted classifier at nine bodies in `both` (0.810 against 0.835) and within 2.8 in the AP
plane (0.715 against 0.743); the lateral plane is 7 points behind (0.590 against 0.659). That
is the outside check of section 7 in its strongest form: the table alone, read as a distance,
names four bodies in five from a nine-body field.

### 1.5 Nonlinear, and the size of the fit

Solution H, one hidden layer, the width chosen on the selection seed, scored on the scoring seed
beside C on the same rows (`mlp[]`):

| arm | regime | hidden width chosen | H: typical / worst (t13) | C on the same rows | difference, points |
|---|---|---|---|---|---|
| with the target, 5 bodies | lateral | 32 | 0.549 / 0.485 | 0.538 / 0.464 | +1.1 / +2.1 |
| | ap | 32 | 0.604 / 0.548 | 0.592 / 0.539 | +1.2 / +0.9 |
| | both | 128 | 0.699 / 0.601 | 0.702 / 0.605 | -0.3 / -0.4 |
| neighbours only, flank | lateral | 32 | 0.415 / 0.365 | 0.369 / 0.330 | +4.6 / +3.5 |
| | ap | 32 | 0.476 / 0.424 | 0.437 / 0.385 | +3.9 / +3.9 |
| | both | 32 | 0.568 / 0.495 | 0.522 / 0.458 | +4.6 / +3.7 |

With the target visible the network is within 1.2 points of the linear classifier in every
regime, inside the column-clustered standard error of 0.012 to 0.014; it is still worst on
`t13` by the same margin. Without the target it gains four to five points, which says that the
neighbour-only problem has a curvature the linear rule misses (the two neighbours' shapes
interact in saying what lies between them) and the problem with the target in view does not.
The shuffle test is 50 of 50 on every H cell.

The size of the fit (`fit_size[]`; C with the target at five bodies and G at five bodies,
`both`, typical / worst):

| typical columns fitted on | rows | C on the field | G |
|---|---|---|---|
| 100 | 1,800 | 0.672 / 0.584 | 0.631 / 0.562 |
| 300 (the study's size) | 5,400 | 0.702 / 0.605 | 0.645 / 0.570 |
| 1,000 | 18,000 | 0.712 / 0.622 | 0.641 / 0.574 |
| 2,000 | 36,000 | 0.712 / 0.629 | 0.648 / 0.576 |

The classifier saturates by 1,000 columns, one point above the study's 300, inside one
standard error (0.012); the decoder saturates by 300. So the rates of this report are the
model's, not the fit's, and more synthetic columns will not move them; what would is a
different generator (section 8).

## 2 Anomalous spines

### 2.1 Per phenotype, neighbours only, with the signed offsets

`flank`, regime `both`, solution C, 200 scoring columns per phenotype, against the count from C2
(`cells[].solutions.C.per_phenotype`, drawn in `figures/neighbour_offsets.csv`). The offset is
the named ordinal minus the true one: negative is a name too cranial. The last column excludes
the one body per column that the typical fit cannot name (section 0, the edge names): L5 in
`six_lumbar` and `t13`, whose 200 windows are wrong by construction.

| phenotype | n windows | exact (Wilson 95%) | within one | mean signed offset, levels | share at -2 / -1 / 0 / +1 / +2 | exact against the rib reading (n) | exact, the unnameable body excluded |
|---|---|---|---|---|---|---|---|
| typical | 4,000 | 0.522 (0.507 to 0.538) | 0.840 | -0.03 | .053 / .170 / .522 / .148 / .044 | 0.522 (4,000) | |
| four_lumbar | 3,800 | 0.499 (0.483 to 0.515) | 0.834 | +0.09 | .047 / .158 / .499 / .176 / .054 | 0.499 (3,800) | |
| six_lumbar | 4,200 | 0.489 (0.474 to 0.504) | 0.839 | -0.02 | .049 / .191 / .489 / .159 / .046 | 0.489 (4,200) | 0.514 (4,000) |
| t13 | 4,200 | 0.458 (0.443 to 0.473) | 0.815 | -0.17 | .073 / .224 / .458 / .134 / .046 | 0.517 (4,000) | 0.481 (4,000) |
| lumbar_rib | 4,000 | 0.523 (0.507 to 0.538) | 0.836 | -0.03 | .062 / .161 / .523 / .152 / .041 | 0.475 (3,800) | |
| no_rib_t12 | 4,000 | 0.519 (0.504 to 0.534) | 0.839 | +0.01 | .050 / .154 / .519 / .167 / .042 | 0.439 (4,000) | |

Beyond two levels either way is 6 to 7% in every phenotype and beyond three 2 to 3%; the largest
offset seen is 12. The rib column drops the windows whose target has no rib name, the inserted
body of `t13` and the blended L1 of `lumbar_rib`. `four_lumbar` is 2.3 points below typical
(about 2.5 column-clustered standard errors) with no mechanism in the generator, whose
`four_lumbar` column differs from a typical one only by ending at L4 (section 8); `lumbar_rib`
and `no_rib_t12` are within one point of typical against the count; `six_lumbar` is within one
point once its unnameable L5 is excluded, and `t13` stays four points below. The same table for
the two single planes is in the record (`flank`/`ap`: typical 0.437, worst `t13` 0.385, mean
offset -0.20; `flank`/`lateral`: 0.369, 0.330, -0.08).

### 2.2 The one-level shift, found where the brief said to look

Mean signed offset by true level (`cells[].solutions.C.per_phenotype[].mean_offset_by_level`,
drawn in `figures/neighbour_shift.csv`); the L5 column of `six_lumbar` and `t13` is the body the
fit cannot name, every call on it an error, and is marked so:

| phenotype | C4 | T11 | T12 | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|---|---|---|
| typical | +0.42 | -0.01 | -0.21 | +0.29 | -0.10 | -0.25 | -0.56 | (not eligible) |
| six_lumbar | +0.43 | +0.09 | +0.07 | +0.31 | +0.03 | -0.19 | -0.47 | -1.34 (unnameable) |
| t13 | +0.34 | +0.10 | +0.03 | +0.33 | -0.40 | -1.04 | -1.24 | -1.55 (unnameable) |
| lumbar_rib | +0.36 | -0.01 | -0.12 | +0.12 | -0.09 | -0.34 | -0.50 | |
| no_rib_t12 | +0.41 | +0.23 | +0.04 | +0.43 | -0.07 | -0.39 | -0.48 | |

In `t13` the count names the inserted body L1 and everything below it one further than its
shape. The inserted body is a 0.5 blend of T12 and L1, and the model, reading only shape, splits
it (mean offset +0.33, like typical L1's +0.29). The shift begins below it: the count's L2, whose
upper neighbour is the blend, is split between L1 and L2 (-0.40), and from the count's L3 down
the calls sit one level cranial on average (L3 -1.04, L4 -1.24), with the bulk of the mass at
exactly -1 (22% of all `t13` windows against 17% in typical). The brief called this the failure
that makes a level-naming device dangerous, confident and systematic; it is here. The brief
predicted a one-level shift in `six_lumbar` and `t13` without naming levels or a sign; `t13`
shows it, and the `six_lumbar` row, once its unnameable L5 is set aside, shows none (L1 to L4
within 0.1 of typical). The first write-up read the `six_lumbar` L5 row as a shift and gave a
wrong reason for it; the review corrected both (section 12).

Every phenotype drifts cranial at L4 (-0.5) and caudal at C4 (+0.3 to +0.4): L5 and C3 are
absent from the `flank` fit, not rare, so every error at the first and last nameable body is
forced one way. That is the edge of the arm, not the anatomy.

Against the rib reading the `t13` column is named at 51.7%, within one point of typical, and
`lumbar_rib` and `no_rib_t12` fall to 0.475 and 0.439: the model names the shape, and which
convention is right is not a question shape can answer. This is the finding to carry to any
device: a namer must be told which convention it is scored against, and on a spine with a
thirteenth rib it will be one level off the count below that rib unless the rib is read.

### 2.3 What does not remove it

- **Fitting on all six phenotypes** (`mixed_fit`, 50 columns of each, 6,050 fit rows): C names
  typical 0.516 and `t13` 0.454, the shift unchanged at L3 (-1.08) and worse at L4 (-1.47, and
  typical's L4 drift goes from -0.56 to -0.74), because the same pair of neighbour shapes is now
  labelled L2 in a typical column and L3 in a `t13` one, and the model splits the difference. In
  the mixed fit L5 is a label (from the longer columns), so its L5 row (-1.73) is on a different
  class set from the main one and the two are not compared. A, the scalar index, drops 2.4
  points (0.286 to 0.262) and its worst phenotype becomes typical; B is unfitted and cannot
  move.
- **Abstaining** (solution F, `cells[].selective`, `figures/neighbour_coverage.csv`): at 50%
  coverage `both` names typical 0.693 and `t13` 0.606 exactly, within one 0.942 and 0.926; at
  90% coverage 0.553 against 0.483. The gap between typical and `t13` is 7 to 9 points at the
  three chosen coverages, up to 11 at a quarter coverage, and closes only below a tenth, so
  confidence does not find the shifted calls; they are confident.
- **More context** does not close it either: `flank2` is worst on `t13` by 9 points (0.671
  against 0.577), `with_target` by 10, and the field of nine bodies by 11 (section 2.4).

### 2.4 On the field, the target in it

The same per-phenotype table for the main arm, C on the field, `both`, at five and nine bodies
(`field[].arms.with_target.C_field.per_phenotype`); the unnameable body is L4 at five bodies and
L2 at nine, in `six_lumbar` and `t13`, 200 windows each:

| bodies | phenotype | n | exact (Wilson 95%) | within one | mean offset | exact against the rib reading (n) | exact, the unnameable body excluded |
|---|---|---|---|---|---|---|---|
| 5 | typical | 3,600 | 0.702 (0.687 to 0.717) | 0.920 | -0.01 | 0.702 (3,600) | |
| 5 | four_lumbar | 3,400 | 0.667 (0.651 to 0.682) | 0.920 | +0.05 | 0.667 (3,400) | |
| 5 | six_lumbar | 3,800 | 0.656 (0.640 to 0.670) | 0.927 | -0.03 | 0.656 (3,800) | 0.692 (3,600) |
| 5 | t13 | 3,800 | 0.605 (0.590 to 0.621) | 0.906 | -0.12 | 0.652 (3,600) | 0.639 (3,600) |
| 5 | lumbar_rib | 3,600 | 0.682 (0.667 to 0.698) | 0.918 | -0.04 | 0.622 (3,400) | |
| 5 | no_rib_t12 | 3,600 | 0.717 (0.702 to 0.731) | 0.937 | +0.03 | 0.573 (3,600) | |
| 9 | typical | 2,800 | 0.835 (0.821 to 0.848) | 0.987 | -0.02 | 0.835 (2,800) | |
| 9 | four_lumbar | 2,600 | 0.781 (0.765 to 0.797) | 0.975 | +0.02 | 0.781 (2,600) | |
| 9 | six_lumbar | 3,000 | 0.763 (0.747 to 0.778) | 0.983 | -0.06 | 0.763 (3,000) | 0.818 (2,800) |
| 9 | t13 | 3,000 | 0.726 (0.709 to 0.741) | 0.976 | -0.10 | 0.793 (2,800) | 0.778 (2,800) |
| 9 | lumbar_rib | 2,800 | 0.801 (0.786 to 0.815) | 0.981 | -0.03 | 0.795 (2,600) | |
| 9 | no_rib_t12 | 2,800 | 0.833 (0.818 to 0.846) | 0.986 | +0.03 | 0.711 (2,800) | |

Exact naming by true level on the field, typical and `t13`, `both`
(`field[].arms.with_target.C_field.exact_by_level`; the mean offsets are
`per_phenotype[].mean_offset_by_level`):

| bodies | column | T8 | T9 | T10 | T11 | T12 | count's L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | typical | .40 | .48 | .60 | .69 | .66 | .69 | .63 | .82 | (not eligible) |
| 5 | t13 | .42 | .44 | .55 | .56 | .57 | .59 (the blend, +0.02) | .59 (-0.23) | .28 (-0.82) | .00 (unnameable, -1.27) |
| 9 | typical | .70 | .71 | .71 | .74 | .81 | .90 | (not eligible) | | |
| 9 | t13 | .65 | .64 | .63 | .66 | .64 | .77 (the blend, -0.24) | .00 (unnameable, -1.01) | | |

With the target in view the shift is still there and still one level: at five bodies the
count's L3, the second body below the blend, is named exactly 28% against typical's 82%, with
mean offset -0.82, while the body just below the blend is held to 59% by the field above it.
At nine bodies no nameable `t13` target lies below the blend, and the deficit changes shape:
every level from T8 down is 5 to 17 points below typical (T12 .64 against .81, L1 .77 against
.90), because a nine-body field at those targets holds the inserted body and the shifted bodies
below it, and the classifier reads an inconsistency it was never fitted on. The deficit is the
count convention either way: against the rib reading `t13` names 0.652 at five bodies and 0.793
at nine. `six_lumbar`, with its unnameable body excluded, is within one point of typical at five
bodies and 1.7 below at nine; `four_lumbar` is 3.5 and 5.4 points below with no mechanism in the
generator (section 8). G and `G_B` are worst on `t13` in every field cell too, by 7 to 11 points.

## 3 Latency

Measured on this container (`latency` in the two records; Linux, 4 CPUs, Python 3.13.17, numpy
2.5.3), single target, the mean over repeated calls (2,000 for the neighbour-only solutions,
1,000 for the field), no thread count pinned:

| operation | time | rate |
|---|---|---|
| name one window from the two neighbours, solution C (softmax) | 0.018 ms | 56,000 /s |
| name one window, solution A (scalar index) | 0.013 ms | 80,000 /s |
| name one window, solution B (published means) | 0.016 ms | 63,000 /s |
| name one field of 1 / 3 / 5 / 7 / 9 bodies, C on the field | 0.016 / 0.024 / 0.024 / 0.025 / 0.030 ms | 33,000 to 62,000 /s |
| name one field of 1 / 3 / 5 / 7 / 9 bodies, G, the decoder | 0.035 / 0.090 / 0.129 / 0.272 / 0.224 ms | 3,700 to 29,000 /s |
| synthesize one column | 0.37 ms | 2,700 /s |
| fit C, 120 / 300 / 600 columns of neighbour windows | 0.33 / 0.74 / 1.73 s | |
| fit C on the field of 1 / 3 / 5 / 7 / 9 bodies, 300 columns | 0.24 / 1.6 / 3.1 / 5.5 / 6.8 s | |
| fit H, 5 bodies, 1,500 steps, widths 32 to 128 | 7.0 to 17.2 s | |
| fit A, 120 / 300 / 600 columns | 2.1 / 3.6 / 6.1 ms | |
| fit C, one cell of the neighbour-only study | 0.20 to 2.9 s | |
| the neighbour-only study, 15 cells, the r sweep, the ladder, the mixed fit | 93 s | |
| the continued study, 27 field cells, 6 H cells, the fit-size sweep, the r sweep per width | 567 s | |
| the enumeration, 127 fits of C (`enumerate-shard0.json`, `rows[].fit_seconds`, `seconds`) | 0.13 to 3.9 s each, 56 s of fitting, 82 s in all | |

The handoff's 0.40 ms per window for junction placement was on a Windows workstation, which
section 9 puts at three to four times slower than this container on the same synthesis, so
like for like the neighbour namer is six to seven times cheaper than junction placement: a
fourteen-number log vector through a 14-by-22 matrix. Whatever the clinical budget, it is not
spent here: SPINEPS segmentation of a volume is seconds to minutes, and the registration step
section 4.3 specifies is the only part of a 3-D answer with a latency of its own. Training is
cheap enough to refit per convention, per phenotype or per field of view at will.

## 4 Dimensionality

### 4.1 Statistical

Section 1.3's table: one direction is a monotone formula that names 28.6%; five reach 47.9%;
from eight directions to all fourteen the typical curve gains one point (0.516 to 0.527, 1.2
column-clustered standard errors) and the worst-phenotype curve is flat (0.456 to 0.466,
`figures/neighbour_formula_dims.csv`). So the information occupies five to eight directions of
the fourteen-dimensional neighbour space. On the field with the target in view the linear
classifier and the one-hidden-layer network are within 1.2 points of each other (section 1.5),
so no curvature is missing there either; the brief's rule gives the linear classifier.

### 4.2 Projective: 3-D

**Neighbours only.** The three regimes on the `flank` arm over all six phenotypes pooled, the
unidentified within-patient correlation r between measures swept over the grid 0, 0.2, 0.4,
0.6, 0.8, 0.9 of the exchangeable form (`r_sweep`, `identified`, `sign`, `profile_in_r`; drawn in
`figures/neighbour_r.csv`). Column-clustered standard errors 0.0036 to 0.0039 at every point.

| regime | exact at r = 0 | at r = 0.9 | identified set over the grid | Imbens-Manski 95% |
|---|---|---|---|---|
| lateral | 0.359 | 0.366 | [0.359, 0.366] | [0.353, 0.372] |
| ap | 0.420 | 0.427 | [0.420, 0.427] | [0.414, 0.434] |
| both | 0.501 | 0.519 | [0.501, 0.519] | [0.495, 0.525] |

Every profile rises with r; the largest gap across the grid is 0.86 standard errors, and the
record's `informative` flag is false for every regime, which the code defines as a measured
slope below the Monte Carlo noise floor: the run cannot see a slope, which is not a proof that
there is none, so the gap is indicative and r is left as the set and never pointed. The
Imbens-Manski interval is used as `covariance.py` documents it, with its two known weaknesses
(Stoye's correction for a set whose width is poorly estimated, and under-coverage in small
samples) unaddressed; at the margins below neither matters.

| difference | over the grid | Imbens-Manski 95% | sign constant over the grid | margin at the worst r |
|---|---|---|---|---|
| both minus ap | [+0.081, +0.092] | [+0.072, +0.100] | yes | 15.4 se |
| both minus lateral | [+0.142, +0.153] | [+0.133, +0.162] | yes | 26.3 se |
| ap minus lateral | [+0.060, +0.063] | [+0.051, +0.073] | yes | 11.1 se |

**The field, the target in it.** The same sweep for C on the field at every width, all six
phenotypes pooled (`field_r.sign.C_field`, keyed by half-width; `field_r.identified`,
`field_r.profile_in_r`; the decoder G is in the record beside it with margins of 11 to 16 se):

| bodies in the field | both at r = 0 / 0.9 | ap | lateral | both minus ap: set, IM 95%, margin | both minus lateral | ap minus lateral |
|---|---|---|---|---|---|---|
| 1 | 0.356 / 0.371 | 0.296 / 0.303 | 0.238 / 0.243 | [+0.059, +0.068], [+0.052, +0.075], 14.2 se | [+0.117, +0.128], [+0.111, +0.135], 28.9 se | [+0.058, +0.060], [+0.051, +0.068], 14.4 se |
| 3 | 0.555 / 0.578 | 0.457 / 0.474 | 0.415 / 0.425 | [+0.098, +0.103], [+0.087, +0.114], 16.1 se | [+0.141, +0.153], [+0.131, +0.163], 22.9 se | [+0.043, +0.051], [+0.032, +0.061], 6.9 se |
| 5 | 0.671 / 0.691 | 0.581 / 0.594 | 0.522 / 0.538 | [+0.090, +0.097], [+0.078, +0.109], 12.3 se | [+0.149, +0.154], [+0.136, +0.167], 19.9 se | [+0.056, +0.060], [+0.043, +0.073], 7.5 se |
| 7 | 0.739 / 0.756 | 0.659 / 0.671 | 0.584 / 0.603 | [+0.080, +0.086], [+0.066, +0.100], 9.8 se | [+0.153, +0.156], [+0.138, +0.171], 18.7 se | [+0.068, +0.075], [+0.053, +0.090], 7.9 se |
| 9 | 0.789 / 0.805 | 0.708 / 0.719 | 0.638 / 0.657 | [+0.081, +0.087], [+0.066, +0.102], 9.3 se | [+0.148, +0.152], [+0.133, +0.168], 17.2 se | [+0.063, +0.070], [+0.047, +0.086], 6.7 se |

The sign of every difference is constant over the grid and certified at every width; the
largest gap across the grid within a regime is 0.96 standard errors. The brief's decision rule:
if one plane reaches `both` within the margin, 2-D. Neither does, at any r on the grid 0 to
0.9, at any width, by nine standard errors or more on the comparison that decides it (`both`
against the AP plane) and by seventeen or more against the lateral plane. Since a projection as
a clean selection of in-plane measures is an optimistic idealisation (no magnification,
obliquity, cone-beam distortion or superimposition is modelled), a real radiograph in one plane
yields at most the single-plane number, so the gap between the idealised `both` arm and a real
image in one plane is at least this; whether a device reaches the `both` rate is the question
of section 4.3. **The discriminating information is 3-D.** The AP plane is the better single
plane by four to eight points at every width, and the AP widths carry the leading direction of
the formula (section 1.3), so if only one shot can be had it is the AP; from a nine-body field
it names 74% of bodies in this idealised form and 66% on `t13`.

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
above the AP set and 7.8 above the lateral. A single width, EPWu of the two neighbours, already
names 26%, five times chance. The selection seed and the scoring seed agree to within 1.6
points on every row of the table and 3.1 over all 127 subsets, so the enumeration has not
overfitted its choice. The k = 5 row, the AP set plus one out-of-plane depth, recovers about
half the gap between the AP set and the full seven, which is what the route below would read
from a CT.

### 4.3 The route to the third axis, specified and not built

Since `both` beats each plane at every width, the out-of-plane measures a fluoroscopic shot
lacks are to be read from a preoperative CT through registration. The claim is narrow and must
stay narrow: registration here is a **measurement device** for the out-of-plane measures of the
few visible bodies, not a localiser; it needs to be locally right over two to nine bodies, never
globally right over the column, and it names nothing. Registration-based level localisation,
which needs a globally correct correspondence, is a different route with a published accuracy
of its own, not recorded here.

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
3. **Register locally**: align the CT's visible bodies to the image by the in-plane measures
   and the inter-body distances, a rigid or piecewise-rigid fit over the field, and read each
   visible body's out-of-plane three (AP shot: EPDu, EPDl, SCD) from the CT at the matched body.
   The quantity to measure for this stage is the error of those three values at the matched
   body, in millimetres, against the CT's own measurement, as a function of the registration's
   precision; a field that matches the wrong body by one level is the failure that matters, and
   it must be reported as an offset distribution, as section 2.1 does.
4. **Name**: the seven measures of each visible body into the classifier of section 1.4, under
   the convention the device is scored against (section 2.2).

What decides whether the route is worth building is stage 3's number, and the bar is higher
than the first write-up set it. The adjacent-level steps of the out-of-plane depths in the
reference table are small: across T1 to T12 the upper end-plate depth steps by 0.5 to 3.1 mm
(median 1.2) and the lower by 0.2 to 1.9 mm (median 1.3), the same order as the 1 mm of noise
every rate here assumes. So the registration error on the out-of-plane depths must be well
under a millimetre for the `both` rates of section 1.4 to apply; at a millimetre or more the
route buys little or nothing over the AP shot. Neither the threshold nor the error has been
measured: the sweep over added noise on the three out-of-plane measures, which would turn the
threshold from an assertion into a number, is the first thing to run.

## 5 Assumptions every number rests on

- The published means and spreads are the whole truth of a level's shape; a patient is a
  shared size (7%), a shared offset across measures within a level (rho 0.5), and 1 mm of
  noise per value. None of rho, scale_sd, noise_mm or blend is given by the literature; rho and
  noise were chosen as the package's existing synthetic corpus uses them, and the r sweeps
  show the rates move by under two points across the whole range of r at every width.
- Adjacent levels of one patient are correlated only through the shared size and offsets; a
  patient's own gradient down the column (a long thorax, a short lumbar spine) is not modelled,
  and it is the thing a field-of-view rule would be most exposed to.
- The transitional bodies are blends at 0.5 between the two shapes; a real transitional body may
  be neither.
- A projection is a clean selection of in-plane measures (section 4.2), an upper bound.
- The classes are the 22 of the table, and a fit on typical columns labels only the names a
  typical column gives the arm (section 0, the edge names); L6 is never named.
- The fit is on typical columns only, except where the mixed fit says otherwise.
- The field always fits inside the column: a target near either end of a short column, which a
  real field of view would show with fewer bodies on one side, is not a case here.

## 6 The three traps

### 6.1 Position never reaches the model

`shuffle_invariance`: for each of 50 trials the target's neighbourhood is moved to another
place in a reshuffled column and the prediction compared. Every cell of both studies, every rung
of the normalisation ladder, the mixed fit and every H cell report 50 of 50 identical
(`cells[].shuffle`, `normalisation[].shuffle`, `mixed_fit.shuffle`, `field[].arms[].shuffle`,
`.shuffle_C_field`, `mlp[].shuffle`). What the test shows is that the features are a function
of the window's contents alone; for the external-constant arms that is the whole claim, since
the feature reads nothing but the window (section 0). The unit test `TestPosition` holds the
features themselves identical under the move for every arm and every rung of the ladder over
20 trials, asserting that the window moved in most of them, and the three fitted solutions
invariant over 30; `TestField` holds the field features and the fitted field models to the same.
The grouped out-of-fold rate on the fit seed (`oof_typical_exact_rate`: lateral 0.344, ap 0.431,
both 0.510) is within 2.5 points of the fresh-seed rate (2.5, 0.6 and 1.3), so the fit is not
memorising columns.

### 6.2 The visible median leaks position, and it buys nothing for the classifier

The brief's trap 2, run as a ladder: each measure divided by its median over the k bodies on
either side of the target, the target excluded, clipped at the ends of the column
(`normalisation`, `figures/neighbour_normalisation.csv`); `flank`, `both`:

| bodies in the median | C: exact, typical | C: exact, worst (t13) | A | LDA_full |
|---|---|---|---|---|
| 2 | 0.274 | 0.236 | | |
| 4 | 0.371 | 0.295 | | |
| 6 | 0.420 | 0.338 | | |
| 10 | 0.495 | 0.401 | | |
| the whole column | 0.610 | 0.515 | 0.504 | 0.681 |
| the external constant (no median) | 0.522 | 0.458 | 0.286 | 0.527 |

A median over ten bodies or fewer is worse than a fixed constant for the classifier, because the
median removes the between-level signal along with the patient's size; the whole-column median
adds nine points to C, 15.5 to LDA_full and 22 to the scalar index A, so what removing the
patient's size is worth depends on the solution, and the nine-point figure is C's alone. The
shuffle test is 50 of 50 on every rung, but the review showed it cannot see this leak: it never
samples a target whose normalising set is clipped at the column's end (8 of the 20 scored
`flank` targets at the ten-body rung, 4 at six, 2 at four), and on the whole-column rung it moves
the same body with the same multiset, so that rung's invariance is by construction. The
whole-column normaliser also carries one bit of the withheld target measurement, whether it is
above or below the column's median (true in all 28,000 target-measure cases on the scoring
columns); refitting with the target inside the median gives 0.611 against 0.610, so the bit is
worth nothing, and the clipped windows are the leak the brief named. The conclusion stands on
the rates, not on the test: a median carries the column's composition, which a limited field of
view does not have, and the constant is the right arm for a device.

### 6.3 Chance is stated

The marginal over true levels on a typical column is uniform over the names the arm can see
(section 0), 200 columns each; so chance is 1/20 = 0.050 exact for `flank`, and within one
(3k - 2)/k^2 = 0.145; 1/21 and 0.138 for the single-neighbour arms; 1/18 and 0.160 for the
five-body arms; from 1/22 and 0.132 at one body to 1/14 and 0.204 at nine on the field
(`chance` in each record). The majority rule gives the same. The recorded chance is the typical
column's; a `four_lumbar` column gives `flank` 19 names (1/19) and a `six_lumbar` or `t13`
column 21 (1/21), which changes no comparison in section 2. Solution C's rate is at least 4.7
times chance in every cell of both studies and at least 8 times on the field; the scalar index A
falls to 4.1 times in the lateral plane, and the by-level rates of section 1.2 go down to three
times chance at the thoracic floor.

## 7 Checks outside the computation

- Solution B fits nothing: it is the published means and spreads read as a distance. On the
  flanking bodies it names within five points of the fitted classifier in `both` and within ten
  in each single plane, with the same ordering of the regimes, and agrees with it on 64% of
  windows; decoded along a nine-body field (`G_B`) it comes within 2.5 points of the fitted
  classifier in `both` and 2.8 in the AP plane (section 1.4). The fitted models are not finding
  something the table does not hold.
- The formula's signs are the table's trends: end-plates and heights grow down the column, the
  canal narrows to the mid-thoracic. The thoracic floor of section 1.2 is where the index steps
  between adjacent classes are smallest in within-class units; the first write-up tied it to a
  flat stretch of printed widths that lies at T1 to T5, not at the floor (section 12).
- The one-level shift in `t13` was predicted in the brief's last section before the run, as a
  shift of one level in `six_lumbar` and `t13`, without levels or sign; `t13` shows it from the
  second body below the blend, and `six_lumbar` does not once its unnameable last body is set
  aside.
- The binary case of the Newton softmax agrees with the package's existing `fit_logreg` to
  0.02 (`TestFit`); the noise-free column at the published means is named exactly at every
  level by B for every arm and regime (`TestPublished`) and by the published decoder `G_B` for
  every field width and regime at three body sizes (`TestField`); a one-body field through G is
  the self model to the bit.
- The classifier saturates with the size of the fit by 1,000 columns (section 1.5), so the
  rates are the model's and not an accident of 300 columns.
- Chance is computed from the marginal, not assumed.

## 8 What could not be settled

- The absolute rates depend on rho, scale_sd, noise_mm and blend, which no published source
  gives; the study shows the ordering of arms, widths, regimes and phenotypes is stable under
  r, and nothing more about the other three.
- A patient's own gradient down the column is not in the generator, and a field-of-view rule
  is the one most exposed to it; whether it helps (a consistent patient) or hurts (a patient
  whose thoracic bodies run large) is not known.
- The projection is idealised; the 2-D rates are upper bounds and nothing here says how far
  above an image they sit.
- The registration route's deciding number, the millimetre error of the out-of-plane measures
  read at the matched body, is unmeasured, and the threshold it must beat is of the order of
  the between-level steps of the depths, about a millimetre (section 4.3).
- The edge names (section 0): a fit on typical columns cannot name the last body of a longer
  column, so every `six_lumbar` and `t13` rate is given twice; the fix is in the next run.
- `four_lumbar` is 2.3 points below typical on `flank` and 3.5 to 5.4 points below on the field
  (2 to 3 column-clustered standard errors) although its columns differ from typical ones only
  by ending at L4, so every field above T12 has the same composition; no mechanism was found.
- The choice between the count's convention and the rib reading on a spine with a thirteenth
  rib is not a shape question.
- The enumeration ran on this container as one shard; the sharded grid run the command
  supports was not needed and was not sent.

## 9 Found on the way, written down, not fixed

- The brief says 23 levels, C2 to L5 as the table's canal rows run; C2 carries no end-plate row
  (the dens occupies it), so `panjabi.py` and this study carry 22 (C3 to L5), and T13 and L6
  arise only inside a phenotype.
- The edge names: a fit on typical columns has no row for the names at either end of the arm's
  reach, so the classifier never says them, and the last body of a `six_lumbar` or `t13` column
  is wrong by construction (found by the review, section 12). The fix is to cut the fit
  columns short at random so that every name is a label, or to fit on every phenotype with the
  columns cut; it changes every anomalous rate by the excluded body's share and is left for the
  next run so that this record stays what the commands above produce. The continued study
  records the exact rate at every level per phenotype (`exact_by_level`) so the floored body
  shows as zero where it is.
- The chance in the records is the typical column's marginal; the longer and shorter columns
  have one name more or fewer (section 6.3).
- `gather_subsets` drops the shard's fit times, so the gathered `enumerate.json` carries none
  and the shard file was run again and kept beside it; the gather would delete it if run again.
- `HANDOFF.md` expects 70 tests with one matplotlib error from `python -m unittest discover -s
  tests`; this container ran 78 and all passed before this study, 94 with it.
- The handoff's latency table is from a Windows workstation and reads three to four times
  slower than this container on the same synthesis; neither is the device.
- The first build of this study's own figures printed a doubled percent sign in two captions;
  fixed here, since the file is this study's.

## 10 Figures

All under `records/neighbour-2026-10-26/figures/`, drawn by `bordercall/neighbour_figures.py`
from `neighbour.json`, `enumerate.json` and `neighbour_more.json`, each as PDF with the type
embedded and no date, PNG at 300 dpi, a CSV of the numbers drawn and its caption; `FIGURES.md`
carries the sha256 of every input. Captions are under sixty words; the argument is in the text
above.

| figure | what it shows | section |
|---|---|---|
| neighbour_field | exact naming against the number of bodies in the field, the target in it, three regimes, typical and worst phenotype, with the published means decoded | 1.4 |
| neighbour_arms | exact naming by neighbour-only arm and regime; typical, worst phenotype, lowest within one | 1.1 |
| neighbour_levels | exact naming by true level, three regimes, neighbours only | 1.2 |
| neighbour_formula | the index by level with its spread; exact against directions kept; the share per direction | 1.3, 4.1 |
| neighbour_offsets | the signed offset distribution per phenotype, neighbours only | 2.1 |
| neighbour_shift | the mean signed offset by level and phenotype, neighbours only | 2.2 |
| neighbour_normalisation | exact against the number of bodies in the median, with the constant as the line | 6.2 |
| neighbour_coverage | exact against coverage for the abstaining rule | 2.3 |
| neighbour_r | the r sweep with the identified sets and Imbens-Manski intervals, neighbours only | 4.2 |
| neighbour_subsets | every subset's worst-phenotype rate against its size | 4.2 |

## 11 Files

- `bordercall/neighbour.py`: the neighbour-only study; `bordercall/neighbour_more.py`: the
  field named as a whole, the decoder, the network, the size of the fit, the r sweep per width;
  `bordercall/neighbour_figures.py`: the figures; `bordercall/run.py`: the commands
  `neighbour`, `neighbour-enumerate`, `neighbour-more`, `neighbour-figures`.
- `tests/test_neighbour.py`: the position tests among them, `TestField` and `TestNonlinear` for
  the continued study; 94 tests in the suite.
- `records/neighbour-2026-10-26/neighbour.json`, `models.json`, `enumerate.json`,
  `enumerate-shard0.json`, `neighbour_more.json`, `figures/`.
- `docs/NEIGHBOUR_IDENTITY_STUDY.md`: the brief this answers.

## 12 What the review corrected

Four independent readers were each given one verdict of the first write-up, the records and the
code, and told to refute it; each reproduced the numbers it checked from the records (the
verdicts' numbers all stood) and returned the claims it could contradict. What changed in this
text as a result:

- **The edge names** (verdict 2, the one finding of substance): the typical fit never labels
  L5 or C3 on `flank`, so the `six_lumbar` L5 row that the first write-up read as a one-level
  shift, and explained by L6 having no name, was a body the model could not name at all; the
  same holds for the last body of every `t13` column and for the field arms at every width.
  Sections 0, 2.1, 2.2, 2.4, 5, 8 and 9 now say so, and every anomalous rate is given with
  that body excluded.
- The monotone check of section 1.3 pools the six phenotypes; on typical columns the two
  single-plane indices each have two sign changes, which the table now shows; the lateral
  sign change in the pooled check is at L3 to L4, not at the flattest step.
- Solution B is within five points of C in `both` only, and 9.5 and 9.3 points behind in the
  single planes (sections 1.1 and 7); the "five points in every regime" is gone.
- The third number of the table in 1.1 is the lowest within-one rate over the phenotypes, not
  `t13`'s; the first verdict's interval was Wilson, now labelled, with the clustered one beside
  it; "flat from eight directions on" is a one-point gain at 1.2 standard errors; the
  enumeration's seeds agree to 1.6 points on the table's rows, not 1.5; the sweep's standard
  errors start at 0.0036; "two bodies below" was two bodies on either side, by 13 to 15 points;
  withholding the target costs one to four points, not three everywhere.
- Four explanations the record contradicts are gone: the abutting end-plates, the body-above
  weights as the asymmetry of 1.1, the flat printed widths as the cause of the thoracic floor
  (they are flat at T1 to T5, where naming is good), and the two reasons given for L1.
- `four_lumbar` is 2.3 points below typical, not within one; the `t13` shift starts at the
  second body below the blend, the first being split; the mixed fit moves A by 2.4 points and
  B cannot move; beyond two levels is 6 to 7%, not 4 to 6; the rib column's denominators are
  stated; the L4 drift is because L5 is absent from the fit, not rare, with its mirror at C4;
  the abstention gap is 7 to 9 at the chosen coverages and up to 11 at a quarter; the worst
  phenotype of every cell is `t13` for solution C, while A's is `six_lumbar` in 14 of 15.
- The latencies are means, not medians, over 2,000 calls with no core pinned; the "one cell"
  row was the softmax fit alone; the enumeration's times were not in any record until the
  shard was run again and kept; the cross-machine factor against the handoff's workstation is
  divided out before the model's size is credited.
- The registration route's threshold was mis-set at 2 to 3 mm; the table's adjacent steps of
  the depths are about 1.2 mm, so the bar is under a millimetre and unmeasured; "the real gap
  is at least this" is now the gap between the idealised arm and a real image; "in-plane" read
  "out-of-plane"; the uncited 73% localisation figure is dropped; the `informative` flag is
  described as the code defines it, with the Imbens-Manski caveats; "at any r" is the grid.
- The shuffle test cannot see the median ladder's leak (section 6.2), and the nine points of
  the whole-column median are C's alone; `TestPosition` now covers every rung of the ladder and
  asserts that the window moved, where it asserted nothing before; "every rate five times
  chance" is 4.7 for C, 4.1 for A and 3 at the by-level floor; the out-of-fold lateral rate is
  2.5 points from the fresh one, not two; the brief's prediction named no levels or sign.
