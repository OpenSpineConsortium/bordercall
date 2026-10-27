# Which vertebrae of a normal spine can be named best, and by what: results

**Status: done, synthetic.** Source: the thread "Finish CNS slides with junction predictor",
2026-10-26, the owner's ask of 08:21 UTC with Kunkel et al. 2010 (J Anat 216:320-328)
attached: "On Fig 2A T12 appears to be the most isolated point along the x axis. Please do a
similarly thorough evaluation of whether there are certain vertebra in the synthetic data that
you can maximize the identification of, assuming normal anatomic spine, please rely on the
prior research to formulate this problem most truthfully." Everything is drawn from typical
columns synthesized from Panjabi's published means and spreads
(`bordercall/reference/panjabi_full_spine.csv`), the same generator as
`docs/NEIGHBOUR_IDENTITY_RESULTS.md`, with no anomalous phenotype in the fit or the score. No
CT, no label, no corpus, no data access was used. The code is `bordercall/identify.py` and
`bordercall/identify_figures.py`; the record is `records/identify-2026-10-26/identify.json`;
the tests are `tests/test_identify.py`. A review of the design by three independent readers,
each told to refute it, shaped sections 0 and 7 before the run; a review of this text by
four more, each told to refute one part of it against the record, the code and the paper,
corrected it in the places section 12 lists.

Every number here is in one file, written by the first command below and drawn by the
second, run from `bordercall/`:

```
python run.py identify --outdir ../records/identify-2026-10-26
python run.py identify-figures --json ../records/identify-2026-10-26/identify.json --outdir ../records/identify-2026-10-26/figures
```

The first writes `identify.json` (308 s on this container); the second draws the nine
figures and writes `figures/FIGURES.md` with the sha256 of the record and of each code file,
and a CSV beside every figure holding the numbers drawn. Beside each table below is the key
of the record the numbers come from; a rate given as a percentage is the record's fraction
rounded, a fraction that falls exactly on a half rounded to the even neighbour (585 of 1,000 is
58%).

## The verdicts

1. **The premise.** T12 is not the most isolated level along the x axis of Kunkel's Fig 2A,
   and no level is identifiable along that axis. Fig 2A plots the level means of the upper
   end-plate width against the level means of the posterior body height, with no spread. With
   Panjabi's population SDs drawn (figure `identify_kunkel`, panel A), T12's posterior height
   is 22.7 mm with an SD of 3.6 mm, and its nearest neighbours along the axis are L1 at 1.1 mm
   and T11 at 1.4 mm. Over the sixteen levels Kunkel used, the widest gap along the body height
   is T1's, 1.5 mm to T2, which is 0.66 of the pooled single-body spread of T1 and T2 in the
   generator; T12's gap of 1.1 mm ties T11's for the second widest in millimetres, but is only
   fifth in units of the pooled spread, 0.27 of that of T12 and L1
   (`one_measure.h_post.kunkel_16`). Over all twenty-two levels
   of the table T12's nearest rival along the body height is L5, which Kunkel left out as
   morphologically distinct, at 0.2 mm (`one_measure.h_post.all_22`). T12 looks isolated in
   Fig 2A because Kunkel's frame holds neither L5, which sits on top of it along that axis, nor
   the spreads, which exceed the gaps at every one of the sixteen levels: the pooled table SD
   of a level and its nearest rival is 1.2 times the gap at T1 (1.74 mm against 1.5), 1.9 to
   2.0 times at T10 and T11, 3.3 times at T12, 4.8 times at T7 and T8, and 18 to 20 times or
   unbounded at T2 to T5 and L1 to L4, where the means are 0.0 to 0.2 mm apart
   (`one_measure.h_post.kunkel_16.<level>.gap_table_sd`, its inverse).

2. **Which levels can be named best.** The cervicothoracic junction, at every width of the
   field and in every projection: C7 is the most isolated level with one body in view, then T1
   and T2, tied (nearest-rival Mahalanobis distances 2.20, 1.66 and 1.66 pooled SD, seven
   measures, the patient's size unknown; `isolation.both.size_unknown.nearest`), and the
   classifier names them exactly in 61%, 56% and 56% of columns from one body, 94%, 93% and 90%
   from five and 99%, 96% and 95% from nine, both planes (`cells`, regime `both`,
   `by_level.<level>.recall`). After them come C5 and C6 (1.18; 97% and 93% at five bodies) and
   T11 (1.10; 41% at one body, 75% at nine). T12 is near the bottom and below every level named above: distance 0.62
   to L1 with one body, tied with L1 for the third-smallest of the twenty-two, and its one-body
   recall of 16% is the lowest of the twenty-two; it is named exactly in 58% of columns from
   three bodies, 67% from five, 73% from seven and 77% from nine, where T11 is its rival both by
   the closed form (`field_isolation`) and by the classifier's errors (of 1,000 true T12 bodies
   119 are named T11, 100 L1 and 13 T10; `cells[14].confusion`, rows and columns over the
   twenty-two `classes`). The
   levels that resist naming are the mid-thoracic run T4 to T10 (distances 0.52 to 0.69; 18% to
   32% at one body, 70% to 91% at nine) and the pair T12 and L1, which with one body are each
   other's nearest rival at 0.62 and are told apart with an AUC of 0.66
   (`by_level.T12.auc_vs_adjacent.L1`).

3. **What maximises a level's identification.** The width of the field above everything:
   both planes, the exact rate over all eligible levels rises from 36.5% with one body to
   58.2%, 70.3%, 77.5% and 83.3% with three, five, seven and nine (`cells[].exact`), and within
   one level from 70% to 99%; by the closed form, T12's nearest-rival distance rises from 0.63
   to 1.61, 2.03, 2.34 and 2.47 (`field_isolation`). Then both planes over one: at nine bodies
   AP alone reaches 74.8% and lateral alone 68.0%. Then knowing the patient's size: with one body
   and the size spread removed T12's distance rises from 0.62 to 1.12 and T11's from 1.10 to
   1.73 (`isolation.both.size_known`), and the one-body exact rate from 36.5% to 41.6%
   (`size.variants`). The measures that carry each level are the end-plate widths for C7, T11
   and T12 (0.83, 0.76 and 0.48 along the upper width alone) and the body height for T1 (0.65);
   the two canal measures isolate nothing but L5 (`subsets.per_measure`). The two pedicle rows
   of Panjabi's table, which no SPINEPS label gives, would lift the lumbar levels most (L5 from
   0.87 to 2.23, L4 from 0.75 to 1.85; `table.isolation_size_unknown`) and T12 only from 0.62
   to 0.78. With a confidence threshold chosen on a separate seed to reach 95% precision, at
   nine bodies C7, T1, T2 and T3 can be named while keeping 100%, 97%, 96% and 93% of their true
   bodies; T12 keeps 41% at a precision that reaches 0.93 on the scoring seed, and T11 24%
   (`cells[].abstain`).

4. **The ceiling.** No rule can name one body past the exact likelihood of the generator with
   the size integrated out: 47.3% exact over the twenty-two levels, 76.1% within one, against
   the linear classifier's 36.5% (`bayes.exact_likelihood`, `bayes.quadratic_from_moments`).
   Per level the Bayes rule's own recall is T1 76%, T2 72%, C7 70%, C4 70%, C6 66%, L5 58%,
   T11 50%, T12 37%, L1 36%, T5 24%; it bounds the overall rate, not any one level's recall,
   which a rule can raise by giving up others' (the linear rule already beats it at T5 and L3).
   So the rule that is best overall names T12 about one time in three from one body, and the
   gap between the linear classifier and the Bayes rule (T12 16% against 37%) is where a
   quadratic or richer rule has room.

5. **The table's own sampling error.** Panjabi's means and SDs come from twelve spines. Over
   400 redraws of the table, C7 is the most isolated level in 83% of them, T1 in 9% and T2 in
   5%; T12's rank is 19 of 22 with a 95% interval of 5 to 21, and L1 stays its nearest rival in
   72% of redraws (`table_bootstrap.by_level`). Along the body height alone the most isolated
   level is T1 in 34% of redraws and C7 in 30%; T12 in 0.5% (2 of 400). The ranking of the ends
   against
   the middle is robust to the table's error; the order within the middle is not.

What this says for the junction predictor: a field of nine bodies that holds the
cervicothoracic junction is named with near certainty (C7 99%, T1 96%), and one that holds the
thoracolumbar junction is not (T11 75%, T12 77%, L1 90%), from the seven SPINEPS measures of a
typical synthetic column. Of the two junctions, the thoracolumbar one is where the predictor
earns its keep; the mid-thoracic run T7 to T10 is named worse still (70% to 74% at nine bodies)
but is no junction.

## 0 How it was done

**The column.** Twenty-two levels C3 to L5 drawn from Panjabi's means and population SDs
(`bordercall/panjabi.py`): a patient size factor exp(N(0, 0.07)) on every value, a per-measure
patient offset shared down the column (rho 0.5; its correlation r between measures 0 in the
main cells, swept over 0, 0.4 and 0.8), a measurement error of 1 mm, a floor of 0.5 mm. Seven
measures, the ones a SPINEPS mask gives: upper and lower end-plate width and depth, posterior
body height, canal width and depth. The AP plane holds the three transverse measures and the
height, the lateral plane the three antero-posterior measures and the height. Typical columns
only, as the owner asked; the anomalous phenotypes of the neighbour study are not drawn.

**The field.** One to nine bodies with the target among them, the target's own measurements
in the features (the owner's rule of 06:31 UTC), named as a whole by the classifier of the
neighbour study (C on the field): a softmax over the seven measures of every visible body,
each in log over a fixed constant per measure, the geometric mean of its published means over
the column (`external_constant`), so the feature carries no position; 1,000 columns fitted on,
500 the
confidence thresholds are chosen on, 1,000 scored, on three seeds. A field of 2h + 1 bodies
fits only around levels with h bodies on each side, so the eligible levels are the 22 of the
table at one body, C4 to L4 at three, C5 to L3 at five, C6 to L2 at seven and C7 to L1 at nine
(`cells[].levels`); every rate over levels is over the eligible ones, and a level at either end
of the column is reported at the widest field that holds it. `exact_common_levels` is the same
rate over the fourteen levels every width holds. The record's `cells` list is ordered lateral
(0 to 4), AP (5 to 9) and both planes (10 to 14), each by half 0 to 4, so `cells[10]` is both
planes at one body and `cells[14]` both planes at nine.

**Four measures of identifiability**, from the loosest to the most honest:

- A. Along one measure, as Fig 2A invites: the gap from each level's mean to the nearest other
  level's, in units of the table's SD at that level and in units of one body's spread in the
  generator, the pooled SD sqrt(sd^2 + noise^2 + (scale_sd mu)^2); over Kunkel's sixteen levels
  and over all twenty-two (`one_measure`).
- B. In the full measure space, one body, closed form: the Mahalanobis distance from each level
  to its nearest other level under the within-level covariance of the log measures, taken from
  the empirical moments of 10,000 drawn columns (`isolation`) and from the delta-method formula
  (`isolation_analytic`), the patient's size unknown, known (the size factor removed from the
  generator) and removed from the features (shape only); by projection regime; along every
  subset of the measures (`subsets`); and when the field around the body is named as a whole,
  the joint Gaussian of the visible bodies profiling the shared size and offsets out as far as
  it can (`field_isolation`). The Bhattacharyya distance and the pairwise error bound beside the
  Mahalanobis distance for the nearest pairs (`isolation_analytic.size_unknown.nearest`).
- C. The classifier, scored on fresh columns: per level the recall, the precision, the
  within-one rate, the confusion with every other level, the one-against-the-rest AUC and the
  AUC against each adjacent level, at each width and in each regime (`cells`); the share of
  each level kept when it is named only above a confidence chosen on the selection seed to
  reach 95% or 99% precision (`abstain`); the precision under a uniform prior over the
  eligible levels among T10 to L5, eight at one body and the four T10 to L1 at nine
  (`thoracolumbar_prior`, `precision_thoracolumbar_prior`); and chance per level with the
  region known, one over the eligible levels of the level's region (`chance_by_level`: with
  one body one in five cervical, one in twelve thoracic, one in five lumbar).
- D. What the patient's size does: C at one and five bodies with the size spread removed,
  doubled, with shape-only features and with the published means as the only fit (`size`); the
  r sweep (`r_sweep`, `isolation_in_r`); the Fig 2A plane alone (`axes`).

**The ceiling.** The exact likelihood of the generator at one body, the size integrated out
by 41-node Gauss-Hermite quadrature over log s, which no classifier can pass on the overall
rate, since it is the Bayes rule under a uniform prior over the twenty-two levels, the
generator's 0.5 mm floor left out (`bayes.exact_likelihood`); and the
quadratic rule from the empirical moments beside it. The table's two pedicle rows (PDW and PDH,
which no SPINEPS label gives) as a ninth and tenth measure, the synthetic ceiling beyond what
the masks measure (`table`).

**The table's error.** 400 redraws of the reference table, each level's mean drawn as
N(mean, sem) and each SD as a chi variable on eleven degrees of freedom, with the closed-form
isolation of B (the formula, not the drawn moments) recomputed on each: the interval of each level's distance and rank, the share of redraws in
which it is the most isolated, and the share in which it keeps its nearest rival
(`table_bootstrap`).

**External checks**, before any number was read (section 8): Kunkel's Table 1 is reproduced
from this table's means over T1 to L4, coefficient by coefficient, and the Fig 2A linear fit
and R^2 too; the closed-form covariance matches a draw.

## 1 The premise: Fig 2A read with its spreads

### 1.1 Kunkel's fits, reproduced (`kunkel`)

Kunkel 2010 regresses twenty parameters per level by cubics over the level means of T1 to L4,
Panjabi's cadaveric tables, eighteen of them on the posterior body height (VBHP) and the body
width and depth on the end-plate widths and depths instead (the width linearly); the cervical
levels are
not in the paper and L5 is excluded as morphologically distinct. Six of the twenty parameters
are among the seven measures here. Refitted on this table's means over the same sixteen
levels, every one of Kunkel's R^2 values and residual SDs comes back, and the cubic
coefficients agree with the printed ones to within 0.005 in every term, twenty-two of the
twenty-four to their printed rounding (the cubic terms of EPDS and SCD, 0.0035 and 0.0055,
round the other way from the printed 0.004 and 0.006) (`kunkel.measures.<m>.cubic_16`;
`tests/test_identify.py`, `TestKunkel`):

| measure | Kunkel's name | linear R^2 | cubic R^2 (Kunkel) | residual SD, mm (Kunkel) | the printed cubic's worst miss at this table, mm |
|---|---|---|---|---|---|
| endplate | EPWS | 0.941 | 0.982 (0.982) | 1.19 (1.195) | 5.2 |
| endplate_lower | EPWI | 0.923 | 0.976 (0.976) | 1.45 (1.454) | 6.6 |
| endplate_depth | EPDS | 0.959 | 0.981 (0.981) | 0.85 (0.852) | 8.0 |
| endplate_lower_depth | EPDI | 0.936 | 0.981 (0.981) | 0.77 (0.769) | 2.9 |
| canal_w | SCW | 0.518 | 0.964 (0.964) | 0.63 (0.634) | 6.1 |
| canal_ap | SCD | 0.576 | 0.811 (0.811) | 0.57 (0.573) | 8.4 |

The linear fit of Fig 2A, y = 2.20 x - 10.51 with R^2 0.94, comes back as 2.2012 x - 10.5052
with R^2 0.941 (`kunkel.measures.endplate.linear_16`). The last column is a caution for anyone
using the printed equations: the coefficients are printed to three decimals (SCD's linear term
to four), and at a body
height of 24 mm the rounding of C4 alone moves the curve by millimetres, so the printed cubics
miss the very means they were fitted to by up to 8.4 mm
(`kunkel.measures.<m>.printed.max_mm_at_this_table`). The refitted coefficients are in the
record.

### 1.2 The levels Kunkel left out (`kunkel.measures.<m>.departures_from_cubic_16`)

Carried to the cervical body heights, the T1 to L4 cubic for the upper end-plate width
overshoots C3 to C6 by 10.4 to 11.6 mm, 4.7 to 7.3 of their own table SDs, and C7 by 3.6 mm
(1.6 SD); it undershoots L5 by 7.3 mm (1.8 SD). The lower width departs further (C3 to C6 by
8 to 21 SD, L5 by 1.2 SD), the depths run the other way (C3 to C6 are deeper than the curve
by 2.3 to 4.9 SD, C7 by 1.5 to 1.7, L5 within 0.3 SD), and the canal width is 2.2 to 4.8 SD
narrower
at C3 to C6. So Kunkel's one-curve picture holds for T1 to L4 and not beyond: the cervical
bodies are a different shape for their height, which is why they are easy to name (section 2),
and L5 is wider than its height predicts, which is why it is the one lumbar level with a
measure of its own (the canal, section 2.3).

### 1.3 Along the body height alone (`one_measure.h_post`)

Per level, the gap to the nearest other level's mean, in millimetres and in units of the
pooled single-body spread of the level and its rival, the root mean square of their two
spreads, each the table's SD, the 1 mm error and the 7% size spread pooled (2.70 mm for T11
against T10, 4.06 for T12 against L1, 3.93 for L5 against T12; a level's own spread,
`body_sd_mm`, is 3.05 at T11, 4.06 at T12 and L1, 3.79 at L5):

| level | over Kunkel's 16, mm (rival) | in pooled body SD | over all 22, mm (rival) | in pooled body SD |
|---|---|---|---|---|
| C7 | - | - | 1.2 (C3) | 0.62 |
| T1 | 1.5 (T2) | 0.66 | 1.3 (C7) | 0.64 |
| T6 | 0.8 (T7) | 0.30 | 0.8 (T7) | 0.30 |
| T10 | 0.9 (T9) | 0.36 | 0.9 (T9) | 0.36 |
| T11 | 1.1 (T10) | 0.41 | 1.1 (T10) | 0.41 |
| T12 | 1.1 (L1) | 0.27 | 0.2 (L5) | 0.05 |
| L1 | 0.0 (L3) | 0.00 | 0.0 (L3) | 0.00 |
| L5 | - | - | 0.2 (T12) | 0.05 |

The other levels' gaps are 0.0 to 0.6 mm (T2 to T5 and L1 to L4 all 0.2 mm or less; the full
table is `figures/identify_kunkel.csv`). No gap exceeds 0.66 of the pooled spread, so along
this axis alone no level is named better than about two in three against its nearest rival
(0.63 at T1, 0.55 at T12, one minus the two-class Gaussian error at that distance), and among
sixteen or
twenty-two names, far worse (section 4.5: 13.8% exact). Along the upper
end-plate width, Fig 2A's y axis, the picture is a little better and T12 is still not the
best: C7's gap to T1 is 2.7 mm (0.83 body SD), T11's to T10 3.0 mm (0.78), T12's to L1
2.2 mm (0.53) (`one_measure.endplate.all_22`).

### 1.4 What the table's error does to this (`table_bootstrap.by_level.<level>`: `gap_body_sd_point`, `gap_body_sd_lo`, `gap_body_sd_hi`, `most_isolated_h_post`)

Over the 400 redrawn tables, the most isolated level along the body height is T1 in 34% of
redraws and C7 in 30%, and T12 in 0.5% (2 of 400); T12's gap in pooled body SD has a 95%
interval of 0.00 to 0.31. The ordering along one axis is within the table's own noise everywhere but at the two
ends.

## 2 One body in the full measure space

### 2.1 Isolation, seven measures (`isolation.both`, `isolation_analytic`)

The Mahalanobis distance from each level to its nearest other level under the within-level
covariance, from the moments of 10,000 drawn columns; a distance of 1 is one pooled SD, and
the pairwise error of two equally likely levels at that distance is 0.38 at a distance of 0.63
and 0.14 at 2.20 (`isolation_analytic.size_unknown.nearest.<level>.pair_error`), with the
Bhattacharyya bound on it 0.44 and 0.21 (`.bhattacharyya_error_bound`):

| level | size unknown (rival) | size known | shape only | AP four | lateral four | best single measure |
|---|---|---|---|---|---|---|
| C3 | 0.96 (C4) | 1.06 | 0.90 | 0.83 | 0.56 | 0.53 endplate |
| C4 | 0.96 (C3) | 1.06 | 0.90 | 0.83 | 0.56 | 0.17 endplate_lower_depth |
| C5 | 1.18 (C6) | 1.49 | 1.01 | 1.11 | 0.75 | 0.94 endplate_lower |
| C6 | 1.18 (C5) | 1.49 | 1.01 | 1.11 | 0.75 | 0.47 endplate_depth |
| C7 | 2.20 (T1) | 2.36 | 1.92 | 1.67 | 1.30 | 0.83 endplate |
| T1 | 1.66 (T2) | 1.67 | 1.65 | 1.26 | 1.05 | 0.65 h_post |
| T2 | 1.66 (T1) | 1.67 | 1.65 | 0.71 | 1.05 | 0.53 endplate_lower_depth |
| T3 | 0.82 (T4) | 0.82 | 0.81 | 0.64 | 0.42 | 0.35 endplate_lower_depth |
| T4 | 0.52 (T5) | 0.69 | 0.42 | 0.27 | 0.42 | 0.35 endplate_lower_depth |
| T5 | 0.52 (T4) | 0.69 | 0.40 | 0.27 | 0.47 | 0.35 endplate_lower_depth |
| T6 | 0.69 (T5) | 1.07 | 0.40 | 0.55 | 0.63 | 0.45 endplate_depth |
| T7 | 0.62 (T8) | 0.97 | 0.47 | 0.55 | 0.34 | 0.49 endplate |
| T8 | 0.62 (T7) | 0.97 | 0.47 | 0.56 | 0.34 | 0.42 endplate_lower |
| T9 | 0.69 (T10) | 1.02 | 0.47 | 0.61 | 0.45 | 0.54 endplate_lower |
| T10 | 0.69 (T9) | 1.02 | 0.47 | 0.61 | 0.45 | 0.54 endplate_lower |
| T11 | 1.10 (T10) | 1.73 | 0.76 | 1.01 | 0.51 | 0.76 endplate |
| T12 | 0.62 (L1) | 1.12 | 0.30 | 0.59 | 0.48 | 0.48 endplate |
| L1 | 0.62 (T12) | 0.88 | 0.30 | 0.51 | 0.41 | 0.35 endplate |
| L2 | 0.75 (L1) | 0.88 | 0.66 | 0.51 | 0.37 | 0.46 endplate_lower |
| L3 | 0.75 (L4) | 0.92 | 0.65 | 0.55 | 0.37 | 0.35 endplate |
| L4 | 0.75 (L3) | 0.89 | 0.65 | 0.55 | 0.46 | 0.13 endplate_lower_depth |
| L5 | 0.87 (L4) | 0.89 | 0.87 | 0.67 | 0.64 | 0.36 canal_w |

(`isolation.<regime>.size_unknown.nearest.<level>.d`, `.rival`; `isolation.both.size_known`,
`.shape_only`; `subsets.best_single`.) The order with size unknown: C7, T1 and T2, C5 and C6,
T11, C3 and C4, L5, T3, L2 to L4, T6, T9 and T10, T7 and T8, T12 and L1, T4 and T5. Four
things to read off it:

- The cervicothoracic junction is isolated by shape, not by size: C7's and T1's distances
  barely move when the size is known or removed (2.20, 2.36, 1.92; 1.66, 1.67, 1.65).
- T12's isolation is mostly size: 0.62 with the size unknown, 1.12 with it known, 0.30 from
  the shape alone. Its shape is L1's; what tells them apart is that L1 is a little larger.
  The same holds of T11 (1.10, 1.73, 0.76) and of the whole run T6 to T10.
- The lateral four isolate every level less than the AP four except T2 and T4 to T6,
  which is the plane question of the neighbour study seen per level: for the thoracolumbar
  levels the transverse widths carry more than the depths.
- No single measure isolates a level by as much as one SD. The largest are the lower
  end-plate width at C5 (0.94), the upper end-plate width at C7 (0.83) and T11 (0.76) and the
  body height at T1 (0.65); T12's best single measure, the upper end-plate width, gives 0.48,
  tenth of the twenty-two (`subsets.best_single`, `subsets.per_measure`, figure
  `identify_measures`); the two canal measures isolate nothing but L5 (canal width 0.36, canal
  depth 0.26), and the lower end-plate depth is the best single measure at T2 to T5 only
  because every measure is weak there (0.53 at T2, 0.35 at T3 to T5).

The delta-method formula reproduces the drawn moments to 0.13 of the variance at its worst
entry, T2's canal depth, whose cv is 0.28 (`covariance_check.worst_variance`); the drawn
moments are what every number above uses. At the junction the Bhattacharyya distance splits
into its mean and spread terms: T12 against L1 (and so L1 against T12) 0.132, of which the
mean term is D^2 / 8 = 0.628^2 / 8 = 0.049 and the rest, 0.082, is the term the spreads of
different size add; T11 against T10 0.270, of which 0.148 is the mean term and 0.123 the
spreads (`isolation_analytic.size_unknown.nearest.<level>`: `bhattacharyya`,
`mahalanobis_to_that_rival`). So even the small separation T12 has from L1 with one body comes
more from its measures being differently spread than from their being differently placed.

### 2.2 With the correlation of the offsets (`isolation_in_r`, `r_sweep`)

The per-measure patient offsets share a correlation r that the literature does not give; r 0
is the main setting. Swept over 0, 0.3, 0.6 and 0.9 in the formula, the nearest-rival distance
rises with r at nineteen levels and falls at T6, T12 and L1 (`isolation_in_r.by_level`); in
the classifier r 0, 0.4 and 0.8 give 36.5%, 37.2% and 37.8% at one body and 70.3%, 71.0% and
72.1% at five (`r_sweep.cells[].acc`), so the identified interval the sweep gives each level is
narrow: T12 15.8% to 17.1% at one body and 66.7% to 68.5% at five, C7 61.4% to 65.7% and
93.5% to 94.5% (`r_sweep.identified_by_level`). r moves nothing the verdicts rest on.

### 2.3 The subsets (`subsets`)

Over all 127 subsets of the seven measures, the subset that isolates a level most is the
full seven at every level (`subsets.best_subset`): adding a measure can never shorten a
Mahalanobis distance under a fixed covariance, so no subset beats the whole. Per plane, from
the separate four-measure draws, the AP four give C7 1.67 and T12 0.59 and the lateral four C7
1.30 and T12 0.48 (`isolation.ap.size_unknown.nearest`, `isolation.lateral.size_unknown.nearest`);
the AP and lateral sub-blocks of the seven-measure draw (`subsets.ap`, `subsets.lateral`) agree
with them to 0.02 on those four and to 0.05 at every level, the worst being L5 in AP (0.63
against 0.67) and T9 and T10 in lateral (0.49 against 0.45), which is two draws agreeing.

### 2.4 The table's own error (`table_bootstrap`)

| level | d, the table as printed | 95% interval over redrawn tables | rank of 22 (interval) | most isolated, share of redraws | nearest rival kept, share |
|---|---|---|---|---|---|
| C7 | 2.20 | 1.76 to 2.74 | 1 (1 to 3) | 83% | 54% |
| T1 | 1.67 | 1.22 to 2.47 | 2 (1 to 9) | 9% | 82% |
| T2 | 1.67 | 1.11 to 2.23 | 3 (1 to 13) | 5% | 53% |
| C5 | 1.18 | 0.87 to 1.79 | 4 (3 to 19) | 0% | 60% |
| T11 | 1.09 | 0.90 to 1.78 | 6 (2 to 20) | 0% | 64% |
| L5 | 0.90 | 0.75 to 1.92 | 9 (2 to 22) | 1% | 87% |
| T12 | 0.63 | 0.67 to 1.59 | 19 (5 to 21) | 0% | 72% |
| L1 | 0.63 | 0.57 to 1.54 | 20 (5 to 22) | 0% | 55% |
| T4 | 0.50 | 0.50 to 1.35 | 21 (7 to 22) | 0% | 63% |
| T5 | 0.50 | 0.53 to 1.42 | 22 (7 to 22) | 0% | 53% |

(`table_bootstrap.by_level.<level>`: `d_point`, `d_lo`, `d_hi`, `rank_7_point`, `rank_7_lo`,
`rank_7_hi`, `most_isolated_7`, `same_rival_7`; the distance, its interval, the most-isolated
share and the point rank of all twenty-two levels are `figures/identify_field.csv`, panel B,
and the rank intervals and the rival-kept shares are in the record only.) The intervals are
wide and skewed upward, since redrawing two means that nearly coincide, T12's and L1's or
T4's and T5's, can only push them apart, so the redrawn distance is almost always above the
printed table's, and a point can fall below its interval for that reason; the ranking of the
two ends against the middle holds, the ranking within the middle does not. The
redraw moves only the within-level moments; the classifier is not refitted on each table.

## 3 The field of view

### 3.1 By the closed form (`field_isolation`)

When the field around a body is named as a whole, the joint Gaussian of the visible bodies
profiles out the patient's shared size and shared offsets as far as a Gaussian can, and each
level's nearest-rival distance rises with the width (figure `identify_field`, panel A):

| level | 1 body | 3 | 5 | 7 | 9 | rival at the widest |
|---|---|---|---|---|---|---|
| C7 | 2.20 | 3.38 | 4.03 | 4.56 | 4.77 | T1 |
| T1 | 1.67 | 3.31 | 4.09 | 4.38 | 4.62 | T2 |
| T2 | 1.67 | 2.33 | 3.41 | 4.18 | 4.43 | T3 |
| T6 | 0.70 | 1.00 | 1.20 | 1.67 | 2.78 | T7 |
| T8 | 0.63 | 0.95 | 1.17 | 1.64 | 2.23 | T9 |
| T11 | 1.09 | 1.61 | 1.84 | 2.16 | 2.45 | T10 |
| T12 | 0.63 | 1.61 | 2.03 | 2.34 | 2.47 | T11 |
| L1 | 0.63 | 1.26 | 2.15 | 2.37 | 2.76 | T12 |

(`field_isolation[].nearest.<level>`.) The field lifts T12 most between one and three bodies
(0.63 to 1.61, its rival changing from L1 to T11 as L1 enters the field and the size is
profiled out), then slowly; C7 and T1 start higher and are about two SD above T11 and T12
from five bodies on (2.0 to 2.4 above them at five, seven and nine; with one body C7 is 1.6
and T1 1.0 above T12, with three 1.8 and 1.7), and 1.9 to 2.2 above L1. The
mid-thoracic levels are the last to be lifted, since their neighbours are copies of them.

### 3.2 By the classifier (`cells`, regime `both`)

The rate over all eligible levels by width, and the same over the fourteen levels every width
holds (`exact`, `exact_common_levels`, `within_one`):

| bodies in view | exact | over the common 14 | within one | eligible levels | chance, uniform |
|---|---|---|---|---|---|
| 1 | 36.5% | 34.0% | 70.3% | 22, C3 to L5 | 4.5% |
| 3 | 58.2% | 54.0% | 86.5% | 20, C4 to L4 | 5.0% |
| 5 | 70.3% | 66.5% | 93.3% | 18, C5 to L3 | 5.6% |
| 7 | 77.5% | 75.1% | 96.6% | 16, C6 to L2 | 6.3% |
| 9 | 83.3% | 83.3% | 98.6% | 14, C7 to L1 | 7.1% |

AP alone: 30.1%, 47.4%, 60.8%, 68.7%, 74.8%; lateral alone: 24.5%, 43.1%, 55.1%, 61.8%,
68.0% (`cells` with regime `ap`, `lateral`). These are the neighbour study's typical rates
refitted on typical columns alone (that study, fitted on all six phenotypes, gives 37.0%,
57.5%, 70.2%, 77.4% and 83.5% on typical columns; `records/neighbour-2026-10-26/neighbour_more.json`),
so the anomalous phenotypes in that fit cost the typical column nothing. Per level, both
planes (`by_level.<level>.recall`, `.precision`, `auc_vs_adjacent`; figure `identify_levels`):

| level | recall, 1 body | 3 | 5 | 7 | 9 | precision at 9 | AUC against the level above / below, 1 body |
|---|---|---|---|---|---|---|---|
| C3 | 55 | - | - | - | - | - | - / 0.74 |
| C4 | 53 | 83 | - | - | - | - | 0.74 / 0.84 |
| C5 | 38 | 77 | 97 | - | - | - | 0.84 / 0.78 |
| C6 | 59 | 84 | 93 | 99 | - | - | 0.78 / 0.94 |
| C7 | 61 | 90 | 94 | 96 | 99 | 98 | 0.94 / 0.91 |
| T1 | 56 | 86 | 93 | 94 | 96 | 97 | 0.91 / 0.85 |
| T2 | 56 | 76 | 90 | 94 | 95 | 96 | 0.85 / 0.86 |
| T3 | 32 | 66 | 82 | 91 | 94 | 94 | 0.86 / 0.70 |
| T4 | 30 | 52 | 72 | 85 | 91 | 90 | 0.70 / 0.63 |
| T5 | 32 | 43 | 55 | 75 | 86 | 83 | 0.63 / 0.68 |
| T6 | 18 | 40 | 49 | 59 | 78 | 77 | 0.68 / 0.69 |
| T7 | 22 | 33 | 46 | 54 | 74 | 76 | 0.69 / 0.64 |
| T8 | 24 | 35 | 41 | 56 | 70 | 71 | 0.64 / 0.67 |
| T9 | 27 | 36 | 49 | 63 | 70 | 70 | 0.67 / 0.65 |
| T10 | 28 | 42 | 60 | 66 | 72 | 73 | 0.65 / 0.76 |
| T11 | 41 | 54 | 62 | 69 | 75 | 75 | 0.76 / 0.79 |
| T12 | 16 | 58 | 67 | 73 | 77 | 78 | 0.79 / 0.66 |
| L1 | 32 | 47 | 70 | 75 | 90 | 89 | 0.66 / 0.70 |
| L2 | 18 | 53 | 63 | 90 | - | - | 0.70 / 0.69 |
| L3 | 36 | 43 | 80 | - | - | - | 0.69 / 0.70 |
| L4 | 41 | 70 | - | - | - | - | 0.70 / 0.63 |
| L5 | 29 | - | - | - | - | - | 0.63 / - |

Percentages; 1,000 columns scored, so a level's recall at nine bodies carries a Wilson
interval of about plus or minus 2.5 points (T12 74.1 to 79.3, C7 98.3 to 99.5;
`by_level.<level>.recall_wilson`), and the overall rate a column-clustered standard error of
0.6 points (`se_cluster`). With one body, chance with the region known is 20% at a cervical
or lumbar level and 8.3% at a thoracic one (`cells[10].chance_by_level`); as the field widens
the eligible cervical and lumbar levels shrink, to C7 and L1 alone at nine bodies, so the
region-known chance is read at one body only. The confusion of each level (figure
`identify_confusion`, `cells[].confusion`) is with its neighbours from five bodies on (a true
T12 is named T11 152 and L1 127 times of 1,000, and 23% of all errors go beyond the adjacent
levels; `cells[12]`); with one body nearly half of all errors (47%) go beyond the adjacent
levels, and a true T12 is named L5 (210), T11 (199) and L1 (174) each more often than T12
(158) (`cells[10]`); the thoracolumbar prior of section 4.6 does not resolve it.

## 4 What maximises a level's identification

### 4.1 The width of the field

Section 3: the largest single gain for every level, and the only thing that lifts T12 past
one in two. Between one and three bodies T12 gains 42 points (16% to 58%), L1 15, T11 13, C7
28; between three and nine, T12 gains 19 more, L1 44, T11 21, C7 10. At nine bodies the four
levels of the thoracolumbar junction are named at 72% (T10), 75% (T11), 77% (T12) and 90%
(L1), the cervicothoracic pair at 99% and 96%.

### 4.2 Both planes

At every width both planes beat AP alone by 6 to 11 points and lateral alone by 12 to 16
points overall; at nine bodies
C7 is named at 99% in both, 96% in AP and 93% in lateral, T12 at 77%, and in the single planes
at the rates `cells` holds for `ap` and `lateral` (figure `identify_isolation`, panel B, gives
the one-body distances per plane: for T12, 0.59 AP and 0.48 lateral against 0.62 both).

### 4.3 The patient's size (`size.variants`, figure `identify_size`)

| bodies | size spread | features | exact | C7 | T1 | T11 | T12 | L1 | L5 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 (size known) | absolute | 41.6% | 64 | 58 | 54 | 23 | 40 | 21 |
| 1 | 0.07 | absolute | 36.5% | 61 | 56 | 41 | 16 | 32 | 29 |
| 1 | 0.07 | shape only | 30.3% | 57 | 51 | 33 | 9 | 14 | 30 |
| 1 | 0.07 | published means, nothing fitted | 32.2% | 57 | 60 | 34 | 8 | 20 | 61 |
| 1 | 0.14 | absolute | 33.0% | 60 | 54 | 33 | 12 | 21 | 25 |
| 5 | 0 | absolute | 76.0% | 94 | 93 | 74 | 75 | 76 | - |
| 5 | 0.07 | absolute | 70.3% | 94 | 93 | 62 | 67 | 70 | - |
| 5 | 0.07 | shape only | 61.6% | 91 | 90 | 48 | 49 | 54 | - |
| 5 | 0.07 | published means | 65.7% | 94 | 94 | 55 | 59 | 64 | - |
| 5 | 0.14 | absolute | 68.5% | 93 | 93 | 60 | 64 | 68 | - |

"Size known" is the generator's size factor removed; Panjabi's SDs still hold the cadavers'
own sizes, so it is a lower bound on what knowing the patient's height would give. The
cervicothoracic levels do not care (C7 57 to 64 in every row); the thoracolumbar levels are
named by their absolute size (T12 23 with the size known, 9 from the shape alone; T11 54 and
33), and doubling the size spread costs them a fifth to a third of their recall with one body
(T11 41 to 33, T12 16 to 12, L1 32 to 21) and little with five. The published means with nothing fitted name L5 at 61% from one body, twice the
fitted classifier, which is the edge effect of the neighbour study: the fit on columns that
end at L5 learns L5 as "the last body" and the means do not.

### 4.4 The measures (`subsets`, `table`)

No subset of the seven beats the seven (section 2.3). Adding the table's two pedicle rows,
which a lateral radiograph shows and no SPINEPS label measures, lifts the one-body distances
most in the lumbar spine (L5 0.87 to 2.23, L4 0.75 to 1.85, L3 0.75 to 1.13), then T11 (1.10
to 1.49) and T1 (1.66 to 1.92), and T12 and L1 only from 0.62 to 0.78
(`table.isolation_size_unknown.<level>`); the classifier with nine measures names one body at
43.9% (L4 70, T1 69, C7 67, T11 62, L5 60, T12 26) and five at 79.6% (T12 80, L1 85, L3 95)
(`table.cells`). The pedicle is the measurement that would move the lumbar and the junction
most; it is not available from the masks this project uses.

### 4.5 One measure, or Fig 2A's plane, as the features (`axes`)

The classifier on the body height alone names 13.8% of bodies exactly (C6 64, L2 55, T12 11);
on the upper end-plate width alone 19.4% (C3 76, L4 62, T12 30); on the two together, the
plane of Kunkel's Fig 2A, 21.9% (C3 72, L4 56, T12 11). Fig 2A's plane names T12 one time in
nine. What the figure shows as isolation is the gap between means that the spreads swallow.

### 4.6 Abstention and the prior (`cells[].abstain`, `cells[].thoracolumbar_prior`)

For each level and width, the classifier names that level only when its posterior clears a
threshold chosen on the selection seed to give 95% (or 99%) precision for that name; the
record gives, on the scoring seed, the share of true bodies of the level that clear it ("kept")
and the precision reached. The rule is a detector per name, so a body can be kept by its own
name's detector without being the classifier's top choice, and "kept" can exceed the recall
(C5 at five bodies: kept 98%, recall 97%). Figure `identify_abstain`:

| level | kept at 95% precision, 5 bodies | 9 bodies (precision reached) |
|---|---|---|
| C7 | 92% | 100% (0.95) |
| T1 | 91% | 97% (0.95) |
| T2 | 82% | 96% (0.95) |
| T3 | 25% | 93% (0.95) |
| T11 | 14% | 24% (0.95) |
| T12 | 5% | 41% (0.93) |
| L1 | 14% | 86% (0.93) |

At nine bodies T12 is kept at 41% with the threshold 0.74, and the precision reached on the
fresh seed is 0.93, two points under the 95% the threshold was chosen for; at the 99%
threshold (0.96) 2.3% of T12 bodies are kept at a precision of 1.00
(`cells[14].abstain.T12`). L1 at 99% keeps 64% at a precision of 0.98. A uniform prior over
T10 to L1, as a field known to hold the thoracolumbar junction would give, lifts T10's
precision at nine bodies from 0.73 to 0.85 and T11's from 0.75 to 0.77 and leaves T12 (0.78)
and L1 (0.89) where they were (`cells[14].precision_thoracolumbar_prior`); it cannot lift the
recall, which is the per-level classifier's.

## 5 The ceiling (`bayes`, `table`)

The exact likelihood of the generator at one body, the size integrated out and the 0.5 mm
floor left out, is the Bayes rule under a uniform prior over the twenty-two levels, so no rule
passes its overall rate: 47.3% exact, 76.1% within one, clustered
standard error 0.4 points (`bayes.exact_likelihood`). The quadratic rule from the drawn moments
reaches 46.6%; the linear classifier the study uses, 36.5%; with the pedicle rows, 43.9%
(figure `identify_ceiling`):

| level | chance, region known | exact likelihood | quadratic rule | linear | linear with the pedicle rows |
|---|---|---|---|---|---|
| C3 | 20 | 63 | 56 | 55 | 60 |
| C4 | 20 | 70 | 72 | 53 | 52 |
| C5 | 20 | 53 | 52 | 38 | 35 |
| C6 | 20 | 66 | 68 | 59 | 62 |
| C7 | 20 | 70 | 68 | 61 | 67 |
| T1 | 8 | 76 | 76 | 56 | 69 |
| T2 | 8 | 72 | 70 | 56 | 55 |
| T3 | 8 | 40 | 38 | 32 | 36 |
| T4 | 8 | 36 | 32 | 30 | 36 |
| T5 | 8 | 24 | 24 | 32 | 27 |
| T6 | 8 | 29 | 30 | 18 | 23 |
| T7 | 8 | 27 | 25 | 22 | 32 |
| T8 | 8 | 44 | 45 | 24 | 25 |
| T9 | 8 | 34 | 33 | 27 | 22 |
| T10 | 8 | 43 | 42 | 28 | 36 |
| T11 | 8 | 50 | 48 | 41 | 62 |
| T12 | 8 | 37 | 36 | 16 | 26 |
| L1 | 20 | 36 | 35 | 32 | 29 |
| L2 | 20 | 39 | 42 | 18 | 33 |
| L3 | 20 | 31 | 30 | 36 | 51 |
| L4 | 20 | 43 | 43 | 41 | 70 |
| L5 | 20 | 58 | 61 | 29 | 60 |

(`bayes.exact_likelihood.recall_by_level`, `bayes.quadratic_from_moments.recall_by_level`,
`cells[10].by_level`, `table.cells[0].by_level`.) Two things follow. The linear classifier is
eleven points under the ceiling with one body, and most of that is at the levels whose
within-level spreads differ from their neighbours' (T12 16 against 37, T8 24 against 44, L5 29
against 58, T1 56 against 76): a quadratic rule recovers nearly all of it, and the neighbour
study's finding that a network buys nothing over the linear rule held for the field, not for
one body. And the Bayes rule's own recall is low at the junction: in this generator the rule
that is best overall names T12 from its own seven measures about 37% of the time, T11 50%, L1
36%, T1 76% and C7 70%; the rule bounds the overall rate, not one level's recall, and a rule
tuned to one name exceeds its figure only at the others' cost (the linear rule already does at
T5, 32 against 24, and L3, 36 against 31). The ceiling is for one body; the field's ceiling
was not computed (section 9).

## 6 The thoracolumbar junction

Pulled together for the junction predictor, both planes, typical columns:

| | T10 | T11 | T12 | L1 |
|---|---|---|---|---|
| one body: distance to the nearest rival (rival) | 0.69 (T9) | 1.10 (T10) | 0.62 (L1) | 0.62 (T12) |
| one body: the Bayes rule's recall | 43% | 50% | 37% | 36% |
| one body: linear classifier | 28% | 41% | 16% | 32% |
| three bodies | 42% | 54% | 58% | 47% |
| five bodies | 60% | 62% | 67% | 70% |
| nine bodies | 72% | 75% | 77% | 90% |
| nine bodies: precision | 73% | 75% | 78% | 89% |
| nine bodies: kept at 95% precision | 18% | 24% | 41% | 86% |
| what carries it | widths | upper end-plate width (0.76) | upper end-plate width (0.48) | widths, weakly |
| with the pedicle rows, one body | 36% | 62% | 26% | 29% |

The junction is named by size and by the end-plate widths, both of which the field supplies
better than the body does; it is where the patient's size matters most (section 4.3) and where
the Bayes rule's one-body recall is low (section 5). The field does not lift every junction
level alike: from one body to nine it lifts T11 least of the fourteen common levels, by the
closed form (1.09 to 2.45) and by the classifier (41% to 75%), and, by the classifier, T12
and L1 among the most (16% to 77% and 32% to 90%). By the closed form T12's advantage over its neighbours is that
the field lifts it fastest between one and three bodies (0.63 to 1.61, against 0.53 for T11,
0.58 for T10 and 0.63 for L1; section 3.1), once T11 and L1 are both in view and the shared
size is profiled out; from three bodies on the classifier names it more often than T10 and
T11.

## 7 Assumptions every number rests on

- The published means and spreads of twelve spines are the whole truth of a level's shape; a
  patient is a shared size (7%), a per-measure offset shared down the column (rho 0.5) whose
  correlation r between measures is 0 and swept, and 1 mm of noise per value; none of rho,
  scale_sd, noise_mm or
  r is given by the literature (the neighbour study's list, which this study inherits).
- Typical columns only: no anomalous phenotype is drawn, fitted or scored, as the owner asked;
  the neighbour study holds the per-phenotype results.
- A level's identifiability is measured against a uniform prior over the eligible levels; the
  only prior tried is the thoracolumbar one of section 4.6.
- Six of Kunkel's twenty parameters and his predictor, the posterior body height, are
  measurable from a SPINEPS mask and are the seven features; the pedicle rows are the one
  addition tried, as the synthetic ceiling beyond the masks.
- "Size known" removes the generator's size factor and nothing more; Panjabi's SDs keep the
  cadavers' own sizes.
- The field always fits inside the column, so the eligible levels shrink with the width and a
  level at the end of the column is judged at the widest field that holds it; a real field of
  view at the end of a column shows fewer bodies on one side, which is not a case here.
- A projection is a clean selection of in-plane measures, an upper bound on a plane.
- The classifier is linear in the log measures; the ceiling of section 5 says how much that
  costs with one body.
- The table's error (section 2.4) is propagated through the closed form only; the classifier
  is not refitted on each redrawn table.

## 8 Checks outside the computation

- Kunkel's Table 1, six rows, and the Fig 2A linear and cubic fits are reproduced from this
  table's means over T1 to L4 before any number of this study was read: every R^2 to 0.002,
  every residual SD to 0.02 mm, every coefficient to 0.005 (`TestKunkel`, which allows 0.4 per
  cent). The
  same data underlies both, so this checks the table, the level set and the fitting, not the
  generator.
- The closed-form moments match a draw of 10,000 columns: the means to 0.01 in the log and
  the covariance to 0.13 of the variance at the worst entry (`covariance_check`;
  `TestIsolation.test_formula_follows_the_draw_where_the_spread_is_small` at one body,
  `TestPatchedPieces.test_the_formula_follows_the_draw_in_a_field` in a field).
- The exact likelihood at one Gauss-Hermite node equals a diagonal quadratic rule computed
  independently in the test; with equal spreads and no noise it names a body at its own mean;
  it beats the linear cell on 60 columns (`TestPatchedPieces`).
- The Bhattacharyya distance is D^2 / 8 under one shared covariance and larger otherwise; the
  field at one body equals the one-body isolation; a field of five bodies isolates every
  common level more than one body (`TestPatchedPieces`), and the record's `field_isolation`
  rises at every step from one to nine bodies for every common level.
- The classifier's rates on typical columns agree with the neighbour study's typical rates,
  fitted on all six phenotypes, to 0.8 points at every width (0.7 at three bodies, under 0.5
  at the others; section 3.2).
- The precision under a uniform prior equals the plain precision, and a point prior gives 1
  or undefined (`TestPatchedPieces`).

## 9 What could not be settled

- The ceiling of the field: the exact likelihood with the size integrated out was computed at
  one body only; at five and nine bodies the linear classifier's distance from the ceiling is
  not known.
- Whether the pedicle rows, or any measure beyond the seven, can be taken from a SPINEPS mask
  or a radiograph in practice: here they are the table's rows and nothing more.
- The real spine: nothing here says what a real T12 looks like, and the generator has no
  patient gradient down the column, no disc, no rib table and no sacrum or C2 in view.
- The fit's edge names: the classifier learns C3 and L5 as the ends of the column, which a
  real field of view does not show as ends; the published-means arm of section 4.3 says how
  much that moves L5.

## 10 Figures

All under `records/identify-2026-10-26/figures/`, black ink on white, serif type, a PDF, a
PNG, a CSV of the numbers drawn and a caption file each; `FIGURES.md` holds the sha256 of the
record and of the code.

- `identify_kunkel`: Fig 2A with the spreads drawn, the sixteen levels filled and the six
  Kunkel left out open, the refitted cubic; and each level's gap along the body height in body
  SD.
- `identify_isolation`: the one-body nearest-rival distance, size known, unknown and removed,
  and by projection regime.
- `identify_levels`: recall and precision by level and width, both planes.
- `identify_confusion`: what each level is mistaken for, one and five bodies.
- `identify_abstain`: the share of each level kept at 95% precision by width.
- `identify_measures`: which measure isolates which level.
- `identify_size`: recall by level under the size variants.
- `identify_field`: the field's isolation by width by the closed form; the one-body distance
  with the table's sampling interval and with the pedicle rows.
- `identify_ceiling`: recall by level under the exact likelihood, the quadratic rule, the
  linear classifier and the linear classifier with the pedicle rows.

## 11 Files

- `bordercall/identify.py`: the study; `bordercall/identify_figures.py`: the figures;
  `bordercall/run.py`: the commands `identify` and `identify-figures`.
- `tests/test_identify.py`: 31 tests, among them the reproduction of Kunkel's table and the
  checks of section 8.
- `records/identify-2026-10-26/identify.json`, `figures/`; `records/README.md` names the
  settings.
- `docs/NEIGHBOUR_IDENTITY_RESULTS.md`: the study this one continues, with the anomalous
  phenotypes and the plane question.

## 12 What the review corrected

Three independent readers of the design, before the run, each told to refute it; four of
this text, each told to refute one part of it against the record, the code and the paper, who
checked 1,164 numbers between them and found 32 wrong numbers, wrong keys or claims the
evidence contradicts; and a second round of three on the corrected text, of whom two returned
(940 numbers checked, 3 wrong) and the third, on sections 4 to 11, stopped at the account's
usage limit, so those sections were checked again by script against the record instead. What
changed:

- Before the run: the eligible levels per width are stated and every rate over levels is over
  them, with the common-fourteen rate beside it; the prior is stated as uniform; the pedicle
  rows are added as the ceiling beyond the seven measurable parameters, since Kunkel's twenty
  are not all available; "size known" is defined as the generator's size factor removed; the
  assumption list of the neighbour study is carried; the closed form took the Jensen term of
  the log, without which its means missed the drawn ones by more than the test allows (0.02).
- Of this text, the numbers: T12 is the most isolated level along the body height in 2 of
  the 400 redrawn tables, not none; the abstention table's precisions at nine bodies are those
  reached under the 95% rule on the scoring seed, not the plain precisions; the AUC columns of T9 and T10 were swapped; C7
  gains 28 and 10 points, not 29 and 9; both planes beat AP by 6 to 11 points and lateral by
  12 to 16, not either by 7 to 12; doubling the size spread costs the junction a fifth to a
  third, not a third; T2's lower end-plate depth isolates it by 0.53, not 0.35; the per-plane
  distances of two draws agree to 0.05 over all levels, not 0.02; the typical rates
  agree with the neighbour study's to 0.8 points, not 0.6; the test count is 31.
- Of this text, the keys: the `cells` list is ordered lateral, AP, both, so the both-planes
  cells are `cells[10]` to `cells[14]`, not `cells[0]` to `cells[4]`; the bootstrap keys are
  `d_point`, `d_lo`, `d_hi`, `rank_7_*`, `most_isolated_7`, `same_rival_7` and
  `gap_body_sd_*`; the pairwise error and the Bhattacharyya bound are two keys and the text
  had the bound's number under the error's key; the one-body covariance check is
  `TestIsolation`'s test, not `TestPatchedPieces`'s; `identify_field.csv` holds no rank
  interval and no rival-kept share.
- Of this text, the claims: the Bayes rule bounds the overall rate and not any one level's
  recall, so "T12 cannot be named more than 37% whatever the rule" became the Bayes rule's own
  recall, which the linear rule already passes at T5 and L3; the gap along one measure is in
  units of the pooled spread of the level and its rival, not the level's own; the spreads
  exceed the gaps at every level but T1, not "two to three times everywhere"; along the body
  height the best two-class rate is about two in three, not one in two; T12 is tied third
  from the bottom by distance and last by one-body recall, not "mid-pack"; with one body nearly half the errors go beyond the adjacent levels and a true T12 is named
  L5 more often than anything, so "confused with its neighbours and almost nowhere else"
  holds from five bodies on; C7 and T1 are two SD above the junction from five bodies on, not
  at every width; the T12 to L1 size step is the third largest in the lower column, not the
  largest, so it no longer explains T12's lift; the thoracolumbar prior moves T10 and T11 and
  leaves T12 and L1; the features are logs over a fixed constant, not over the field's median;
  the best single measure of any level is C5's lower end-plate width, which the text omitted;
  the lateral four beat the AP four at T2 and T4 to T6 only, not at L5; the bootstrap's
  upward skew comes from redrawing coincident means, not from small redrawn SDs; the cervical
  depths' 2.3 to 4.9 SD holds for C3 to C6, with C7 at 1.5 to 1.7; the thoracolumbar prior is
  over the eligible levels among T10 to L5, four only at nine bodies; the region-known chance
  is a one-body figure.
- Of this text, the reading of Kunkel: eighteen of the twenty parameters are cubics on the
  posterior body height, the body width and depth on the end-plate widths and depths; the
  seven features are six of the twenty and the predictor; the cubic coefficients come back to
  within 0.005, twenty-two of twenty-four to the printed rounding, not all.
- Of the corrected text, in the second round: the first round's own count of T12's errors at
  nine bodies read the confusion matrix over the fourteen eligible levels, where its rows and
  columns run over the twenty-two classes, so "the commonest error is L1 (144 against 119)"
  was the true-T8 row; T11 is T12's commonest error (119, L1 100), as it is its closed-form
  rival; L1 gains 44 points from three bodies to nine, not 43; the per-plane agreement of
  section 2.3 is between two draws, not the formula and a draw; T1 and T2 are tied in
  distance; the mid-thoracic run named worse than the junction is T7 to T10 (T6 at 78% is
  named better than T11 and T12); the spreads exceed the gaps at all sixteen levels once the
  pooled SD is used throughout; the bootstrap recomputes the closed form, not the drawn
  moments; "the field matters most at the junction" is gone, since the field lifts T11 least
  of the fourteen common levels; C7 and T1 are about two SD above T11 and T12 from five bodies
  on, and 1.9 to 2.2 above L1; the 0.63 and 0.55 of section 1.3 are one minus the error; C7's
  rival-kept share 54.5% rounds to 54 under the stated rule; the key of the pedicle-row
  distances is `table.isolation_size_unknown.<level>`; Kunkel prints SCD's linear term to four
  decimals, and his SDs for EPDI, SCW and SCD are now beside the refits.
