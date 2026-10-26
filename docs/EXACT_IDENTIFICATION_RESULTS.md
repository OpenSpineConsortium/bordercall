# Naming vertebrae exactly from 1 to n consecutive bodies, and what can be said for certain: results

**Status: done, synthetic.** Source: the thread "Finish CNS slides with junction predictor",
2026-10-26, two asks of the owner's. At 10:43 UTC: "so essentially i want to know if there are
any formulas or functions possible neural network which takes any number of sequential
vertebral measurements from 1 to n such that this function unambiguously identifies a
vertebra? please rely on any of the ideas from the [solver survey] particularly the 'exactness
by construction (no relaxation, big-M, tolerance or optimality gap) plus the entire ranked
score distribution' im fishing for some positive result, and im willing to let you tell me what
i can say with this panjabi synthetic data". At 11:26 UTC: "also look into alternative
statements you can test the probability of using this synthetic data, such as the probability
that Verbebra k is below L1 or T4 ect, essentially i want find something i can say nearly
certainly on as local morphology as possible using explainable widely accepted measurements
downstream of spineps sewgmentation". Everything is drawn from typical columns synthesized
from Panjabi's published means and spreads (`bordercall/reference/panjabi_full_spine.csv`),
the generator of `docs/NEIGHBOUR_IDENTITY_RESULTS.md` and `docs/LEVEL_IDENTIFIABILITY_RESULTS.md`,
in the seven measures SPINEPS masks give (upper and lower end-plate width and depth, posterior
body height, canal width and depth). No CT, no label, no corpus, no data access was used. The
code is `bordercall/exact.py`, `bordercall/exact_supplement.py` and
`bordercall/exact_figures.py`; the records are `records/exact-2026-10-26/exact.json` and
`records/exact-2026-10-26/supplement.json`; the tests are `tests/test_exact.py` and
`tests/test_exact_supplement.py`. While a first full
run was still going, four independent readers, each told to refute one part of it, read its code
and ran small checks of their own; what they found changed the code and this text in the places
section 12 lists, and the run was made again. The finished document was then read by five more,
each finding checked again against the record by another reader, and what they found is
corrected in place (section 12).

Every number here is in one of two files, written by the first two commands below and drawn by
the third, run from `bordercall/`, but for these, which come from elsewhere: the
identifiability study's classifier and its recalls by level (verdict 1 and section 1) and its
47.3% from one body (section 9), from `records/identify-2026-10-26/identify.json`; the
twelve decimal places the tests hold and the 60 columns (1,320 bodies) they hold them on
(section 9, `tests/test_exact.py`); the 50 and 100 columns the joint and quadrature checks
use, and so the 8,400 fields (section 9, set in
`bordercall/exact.py`); the spreads of Panjabi's table (section 12,
`bordercall/reference/panjabi_full_spine.csv`); and the counts of the review's readers and
findings (above and section 12), which no file records:

```
OMP_NUM_THREADS=1 python run.py exact --outdir ../records/exact-2026-10-26
OMP_NUM_THREADS=1 python run.py exact-supplement --outdir ../records/exact-2026-10-26
python run.py exact-figures --json ../records/exact-2026-10-26/exact.json --outdir ../records/exact-2026-10-26/figures
```

The first writes `exact.json` (4,652 s, 78 minutes, on this container's four cores; the record is written
after each part, with `complete` true only at the end); the second writes `supplement.json`,
the checks the second review asked for (879 s; `bordercall/exact_supplement.py`), whose keys
are cited as `supplement.<key>`; the third draws the eight figures and
writes `figures/FIGURES.md` with the sha256 of the record and of each code file, and a CSV
beside every figure holding the numbers drawn. Beside each table below is the key of the record
the numbers come from; a percentage is the record's fraction rounded.

## The verdicts

1. **No function names every field from fewer than twenty-two bodies, and none names more
   fields than one that can be written down.** While the generator is the truth, the rule that
   enumerates every place a field can take and weighs each by the generator's own likelihood is
   the Bayes rule: no formula or network of the same measurements names fields more often. It
   names 47% of single bodies, 73% of three-body fields, 86% of five, 96% of nine and 99.7% of
   fifteen, in both planes (section 1), 11 to 15 points more than the identifiability study's
   classifier on the fields that classifier was scored on, the first 1,000 of these columns; from
   nine bodies it names T12 in 94% of the fields of all 2,000 columns whose middle body is T12,
   where that classifier named 77% of those of its 1,000. A closed formula,
   one quadratic discriminant per place written from the table, comes within 1.2 points of it;
   two quadratic rules and a network fitted on 5,000 columns all fall short of it at each of the
   four widths scored (1, 3, 5 and 9 bodies), by 0.2 to 4.6 points, and by 6 or more standard
   errors in log loss (section 5).
2. **The positive result: the rule says when it is right.** While the generator is the truth
   and every place is equally likely, its posterior is the probability that its name is right,
   so a name given only at 0.99 is right at least 99 per cent of the time by construction, on
   average over the fields it names (verdict 4 says what happens when the table is itself an
   estimate), and the record agrees: 99.78% of the 17% of three-body fields it names
   at 0.99, 99.93% of the 72% of nine-body fields (section 2). The whole ranked distribution is
   the answer: the shortest run of levels holding 99 per cent of a single body's posterior holds
   it 99.65% of the time, at 6.3 levels on average, and 1.4 levels from nine bodies.
3. **What one body says nearly certainly** (sections 3 and 7): its region, for 61% of single
   bodies, wrong 21 times in 26,786, but only 2 of those 21 times at a body more than two levels
   from a regional border; within two levels of T12/L1 the claim is made for 7% of bodies and is
   wrong 12 times in 568 (97.9 per cent right), so there it is no near-certain statement
   (`supplement.region_split.generator`); the side of the cervicothoracic border, for 56% of the
   bodies within two levels of C7/T1, right 99.84% of the time; "below T4" (at or below T5) for
   99.4 per cent or more of lumbar bodies. "Below L1" (at or below L2) is said from five bodies of
   78% of true L3 and half of true L2 middle bodies (a five-body field is never centred below L3),
   and at the thoracolumbar junction one body says almost nothing (a claim for 7% of nearby
   bodies). From one body, the single measure that makes the most claims near each border makes
   them for at most 15 per cent of nearby bodies, right only 83 to 99 per cent of the time, and
   which measure that is differs along the column: an end-plate width at the cervical borders and
   from T6/T7 to T12/L1, an end-plate depth from T1/T2 to T5/T6, the canal width from L1/L2 to
   L3/L4 and the canal depth at L4/L5 (section 4).
4. **The premise is the weak point, not the mathematics** (section 6). Built on a table
   estimated from twelve spines, as every rule built on Panjabi's tables is, the rule names 40%,
   60%, 72% and 86% of fields from one, three, five and nine bodies, and its names at 0.99 are
   right only 95 to 96 per cent of the time. A rule that widens the table's spreads and assumes
   2 mm of measurement error (the 2 mm tuned on a pilot) brings them back to 98.9 to 99.3 per
   cent from three to nine bodies (99.6 from fifteen) and its near-border claims to 99.3 per cent
   or more, answering a little over a quarter to nearly two-thirds as often as the nominal rule
   (5.5% of three-body fields against 19.5%, 42.9% of nine-body fields against 68.5%). Those
   rates are pooled over every name it gives, and lean on its cervical names: its names that put
   the middle body in the lumbar spine are right 96.75% of the time from three bodies and 97.65%
   from five, and in the thoracic spine 98.69% from five and 98.63% from nine. Its region claim
   from one body survives at 99.90 per cent pooled over every body, but within two levels of
   T12/L1 it is the thoracolumbar claim and is right only 97.3 per cent of the 6% of bodies it
   is made for (26 wrong of 949; `supplement.region_split.worlds.specimens`); its
   cervicothoracic claim survives at 99.70.
   At 2 mm of measurement error those two claims are right 99.1 per cent of the time or more in
   every rule as measured, the region claim pooled over every body, which the record does not
   split near T12/L1 (`misspecified.noise_mm=2`); the lowest, the nominal rule's cervicothoracic
   claim, 99.10%, 10 wrong of 1,111, is less than one standard error above 99 (the record keeps
   none for one border in one setting, `precision_within_two_se` being NaN there; a binomial one
   from these counts, which leaves out the clustering by column, is 0.28 points), so not shown to
   reach it. At 2 mm only the rule that assumes 2 mm keeps its names at 0.99 (99.8 per cent from
   three bodies, against 96.2 and 97.3); at 3 mm every rule's names at 0.99 (82.6 to 96.85 per
   cent from three bodies) and cervicothoracic claim (96.1 to 97.8) fail, while the region claim,
   pooled over every body, is right 99.1 to 99.6 per cent, the nominal rule's 99.07% (60 wrong of
   6,433) again less than one standard error above 99 (the record keeps none for the region
   claim, and a binomial one from these counts is 0.12 points; `misspecified.noise_mm=3`);
   and a spread of patient size twice the generator's breaks the border claims made from one or
   three bodies and takes the region claim from one body to 98.5 to 98.6 per cent and the
   cervicothoracic claim to 98.7 to 98.9 in every rule.
5. **Everything is synthetic, typical-column and uniform over places.** What would make it real
   is section 10: SPINEPS masks counted from C2, their measurement error measured, the anomalous
   phenotypes given places of their own, and the prior of a real series.

## 0 How it was done

**The rule needs no fitting.** A field of n consecutive bodies can sit at only 23 - n places in
a column of twenty-two (C3 to L5), and naming the field is choosing the place: once the place
is known, every body in it has its name. Given the place, the generator of the earlier studies
(`bordercall/panjabi.py`) says exactly how the field's values are distributed. For one measure,
given the patient's size s,

    x_i = s (mu_i + sd_i (rho z + sqrt(1 - rho^2) e_i)) + noise_i,      i = 1..n,

with z one draw per patient and measure, e_i one draw per body, rho 0.5, the size lognormal
with SD 0.07 and the measurement error 1 mm. Given s, the n values are jointly normal with mean
s mu and covariance Delta + u u', a diagonal plus a rank-one matrix whose inverse and
determinant have closed forms (Sherman-Morrison, no matrix is inverted), and the seven measures
are independent given s when the between-measure correlation r is 0, as it is in these columns.
The likelihood of the field at a place is the product over measures, integrated over log s by
Gauss-Hermite quadrature on 161 nodes; normalising over every place under a uniform prior gives
the posterior over places (`exact.log_evidence`, `exact.posterior`).

This is the solver survey's "exactness by construction (no relaxation, big-M, tolerance or
optimality gap) plus the entire ranked score distribution"
(`research/solver-survey-2026-10-26/REPORT.md`, the paragraph on enumeration): every
alternative is enumerated, the one numerical step is a one-dimensional quadrature whose error is
measured (section 9), and the answer is the whole ranked distribution over places, not an
argmax.

**What follows by construction, while the generator is the truth.**

1. No function of the same measurements, formula or neural network, names fields correctly
   more often than this rule, because it is the Bayes rule for these fields and this prior over
   places (up to the 0.5 mm floor of section 8, which the likelihood leaves out and 4 of 308,000
   scored values touched, and up to the quadrature of section 9). Its error is the floor for any
   network.
2. No function names every field correctly for n below 22: given the size, the generator's
   values are normal (marginally a mixture of normals over the size, cut at the 0.5 mm floor),
   so every place gives every field a positive density, or at the floor a positive probability,
   and the Bayes error is positive.
3. The posterior of the named place is the probability that the name is right. A rule that
   answers only when that posterior reaches 1 - eps is right at least 1 - eps of the times it
   answers: E[correct | p >= 1 - eps] = E[p | p >= 1 - eps] >= 1 - eps. The smallest set of
   places holding 99 per cent of the posterior holds the truth at least 99 per cent of the
   time. A claim about a border is a sum of the same posterior, so a claim made at 0.99 is
   right at least 99 per cent of the times it is made, and two claims made about one field
   are both right at least 98 per cent of the time (the union bound).
4. All three hold at every n, so one function takes 1 to n bodies, as the owner asked.

All three are averages over the generator and over the prior over places, and the prior here
is uniform: every place of every column counts once, in the score as in the rule. They hold
too within any group of fields picked out by the measurements alone, such as the fields the
rule calls lumbar (`widths.<n>.regimes.both.selective_099_by_called_region`), but not within a
group picked out by the truth: the fields whose middle body truly is T12, or truly lies within
two levels of a border. The rates this document gives per true level, per landmark and near a
border are therefore measurements, with no guarantee behind them. A real fluoroscopy series is
not uniform over places (lumbar fields are commoner than cervicothoracic ones); a rule used on
it must carry that prior, or its posteriors are probabilities about a different population of
fields.

**The claims.** A field says something about its middle body (the upper of the two middle
bodies when n is even), whose posterior over the twenty-two levels is the place posterior moved
along by its position in the field (`exact.target_posterior`). At each of the twenty-one
borders between adjacent levels the field says "at or below" the lower level when that
probability is at least 0.99, "at or above" the upper level when it is at most 0.01, and nothing
otherwise (`exact.cut_decisions`). In the owner's words of 11:26 UTC, "below L1" is the claim
"at or below L2", made at the border L1/L2; "below T4" is "at or below T5", made at T4/T5. A
border the middle body cannot fall on either side of, for the field's size alone, is left out
of every rate (`exact.open_cuts`). A claim about a body far from its border is easy and is
right almost always, so every border claim's rate is given twice: over all fields, and over
the fields whose middle body lies within two levels of the border (the two levels above it and
the two below), which is where a border claim is hard. The region claim (cervical, thoracic,
lumbar) and the shortest run of consecutive levels holding 99 per cent of the middle body's
posterior are made at the same 0.99; the record scores them over all fields only
(`claims.regions`, `claims.interval`), and the supplement splits the region claim by distance
from the two regional borders, C7/T1 and T12/L1 (`supplement.region_split`).

**What was scored.** 2,000 typical columns from the scoring seed of the earlier studies (97),
every place of every column, for every n from 1 to 22 (section 1), in both planes (seven
measures), AP (four) and lateral (four); every one of the 127 subsets of the seven measures at
every n on the same fields, common random numbers (section 4); the closed form in the log
measures, and three rules fitted on 5,000 columns from the fitting seed (11), the network kept
at the step that did best on 1,000 columns from the selection seed (23), the last of its 3,000
steps at each of the four widths the fitted rules were scored at (1, 3, 5 and 9 bodies), all
on the same fields as the exact rule (section 5); and the robustness
worlds (section 6), drawn from seeds of their own. Standard errors are clustered by column within
one set of columns and by world across worlds.

## 1 The ceiling: how often a field can be named at all (`widths.<n>.regimes`)

Named exactly means the field's place, and so every body in it, named right. Every place of
every one of the 2,000 columns is scored, so a width of n holds 2,000 (23 - n) fields; the
standard error is clustered by column. "Predicted" is the error the posterior itself expects,
the mean of one minus the posterior of the named place, set beside the error counted.

| Bodies | Places | Named exactly, both planes | SE | Within one | Error predicted / counted | AP plane | Lateral plane |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 22 | 47.3% | 0.26 | 76.5% | 0.528 / 0.527 | 36.5% | 30.1% |
| 2 | 21 | 62.7% | 0.29 | 85.5% | 0.373 / 0.373 | 48.4% | 42.8% |
| 3 | 20 | 73.1% | 0.29 | 91.0% | 0.271 / 0.269 | 58.2% | 53.4% |
| 5 | 18 | 85.7% | 0.28 | 96.6% | 0.144 / 0.143 | 73.4% | 68.3% |
| 7 | 16 | 92.4% | 0.25 | 98.9% | 0.075 / 0.076 | 83.2% | 77.4% |
| 9 | 14 | 96.1% | 0.21 | 99.7% | 0.038 / 0.039 | 89.1% | 83.6% |
| 11 | 12 | 97.9% | 0.16 | 99.9% | 0.020 / 0.021 | 92.9% | 88.7% |
| 13 | 10 | 99.0% | 0.11 | 100.0% | 0.009 / 0.010 | 95.8% | 93.0% |
| 15 | 8 | 99.7% | 0.06 | 100.0% | 0.0025 / 0.0031 | 98.2% | 96.4% |
| 17 | 6 | 99.96% | 0.02 | 100.0% | 0.0005 / 0.0004 | 99.2% | 98.2% |
| 19 | 4 | 100.0% (0 of 8,000 wrong) | 0 | 100.0% | 0.0002 / 0 | 99.6% | 98.9% |
| 22 | 1 | 100.0% | 0 | 100.0% | 0 / 0 | 100.0% | 100.0% |

SE is in percentage points. Widths 4, 6, 8, 10, 12, 14, 16, 18, 20 and 21 are in the record and
fall between their neighbours; from 19 bodies on no field of the 2,000 columns was named wrong
with both planes pooled (either plane alone still errs: at 19 bodies the AP plane names 99.6%,
31 of the 8,000 fields wrong, and the lateral 98.9%, 86 wrong), though the posterior still
predicts an error of 0.0002 at 19, 0.0001 at 20 and less at 21 (`bayes_error_predicted`), which
section 0's second point says is never zero below 22.

The posterior predicts its own error: the error predicted and the error counted differ by at
most 0.0023 at any width from 1 to 22 bodies (at three). From 1 to 18 bodies that is within
1.25 standard errors of the rate, the largest relative gaps at ten and twelve bodies (0.0022
and 0.0017, against standard errors of 0.0019 and 0.0014), and the counted error is a little
above the predicted at 2 and 4 (at 2 by 0.0001, which three digits hide) and at every width
from 6 to 15; the widths share their columns, so
these are not separate tests. From 19 bodies on no field was named wrong where the posterior
expects 1.6 wrong fields of 8,000 at 19 bodies and fewer than one at 20 and 21. Both planes
together beat either alone by 7 to 20 points from one to nine bodies (7 to 15 over the AP plane,
12 to 20 over the lateral), as in the neighbour and identifiability studies.

**Against the rules fitted before.** The identifiability study's linear classifier was fitted
on 1,000 columns and scored on the first 1,000 of these 2,000 columns (the same seed, measures
and order of draws), the target its field's middle body (`classifier`, read from
`records/identify-2026-10-26/identify.json`): 36.5% from one body, 58.2% from three, 70.3% from
five, 77.5% from seven and 83.3% from nine, both planes. The exact rule names 47.3%, 73.1%,
85.5%, 92.3% and 96.0% of those same 1,000 columns' fields (`supplement.first_columns`), 10.8
to 15.3 points more at every width, and 47.3%, 73.1%, 85.7%, 92.4% and 96.1% of all 2,000
columns' fields. The gap is the
classifier's, not the information's: the information in seven measures of nine bodies names 96
fields in a hundred. Level by level, the exact rule on all 2,000 columns and the classifier on
its 1,000 (`widths.<n>.regimes.both.by_centre.<level>.exact`; the classifier's
`cells[].by_level.<level>.recall`):

| Middle body | 1 body: classifier / exact | 3 bodies | 5 bodies | 9 bodies |
|---|---:|---:|---:|---:|
| C7 | 61% / 71% | 90% / 97% | 94% / 99% | 99% / 100% |
| T1 | 56% / 76% | 86% / 96% | 93% / 99% | 96% / 100% |
| T6 | 18% / 29% | 40% / 47% | 49% / 67% | 78% / 96% |
| T11 | 41% / 52% | 54% / 74% | 62% / 86% | 75% / 93% |
| T12 | 16% / 39% | 58% / 73% | 67% / 86% | 77% / 94% |
| L1 | 32% / 35% | 47% / 68% | 70% / 85% | 90% / 97% |
| L3 | 36% / 32% | 43% / 64% | 80% / 89% | (not a middle body) |

T12, which the identifiability study found among the worst-named levels (16% from one body,
77% from nine), is named exactly from nine bodies in 94% of the fields whose middle body is T12 by the exact
rule. The rates
by true level are measurements, not guarantees (section 0), and at L3 from one body the
classifier's recall is the higher, 36% against 32%: the Bayes rule maximises the share of all
fields named, not the recall of any one level, and gives L3's share to its neighbours.

## 2 Certified naming: the posterior is the probability of being right (`widths.<n>.regimes.both.selective`, `.calibration`)

This is the positive result of the first ask. The rule cannot name every field, but it says
which fields it has named: answer only when the posterior of the named place reaches 0.99, and
the answers are right at least 99 per cent of the time, by construction; the record measures
how often it answers and how often it is right.

| Bodies | Answered at 0.99 | Answers | Wrong | Right | Answered at 0.999 | Wrong | 99% set: places | covers |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.7% | 299 | 0 | 100% | 0.16% | 0 | 6.12 | 99.6% |
| 2 | 7.2% | 3,030 | 9 | 99.70% | 3.0% | 1 | 4.57 | 99.6% |
| 3 | 17.1% | 6,848 | 15 | 99.78% | 9.4% | 0 | 3.58 | 99.6% |
| 5 | 36.7% | 13,207 | 25 | 99.81% | 24.9% | 2 | 2.33 | 99.7% |
| 7 | 54.9% | 17,564 | 25 | 99.86% | 38.3% | 1 | 1.69 | 99.8% |
| 9 | 71.8% | 20,112 | 15 | 99.93% | 53.7% | 2 | 1.35 | 99.9% |
| 11 | 83.9% | 20,128 | 13 | 99.94% | 70.1% | 4 | 1.18 | 99.9% |
| 13 | 92.2% | 18,430 | 7 | 99.96% | 83.3% | 3 | 1.08 | 99.97% |
| 15 | 97.8% | 15,651 | 3 | 99.98% | 94.4% | 1 | 1.02 | 99.98% |

The standard error of the precision, clustered by column, is at most 0.1 point at every width
(`precision_se`). The guarantee holds within each region the rule names, which is a fact of the
measurements, not of the truth: at five bodies, of the answers that put the middle body in the
cervical spine 3 of 5,460 are wrong, in the thoracic 18 of 6,287, in the lumbar 4 of 1,460
(`selective_099_by_called_region`). Binned by the posterior, the error predicted and the error
counted agree within sampling error in every bin, at one, three and nine bodies (figure
`exact_calibration`, panel A; `calibration`): at three bodies, the fields whose posterior lay
between 0.9 and 0.99 had a mean posterior of 0.954 and were right 94.9% of the time; between
0.99 and 0.999, 0.9956 and 99.5%; above 0.999, 0.9998 and 100%. In a read aligner's terms
(Li and Durbin's mapping quality, -10 log10 of one minus the posterior), the median field maps
at quality 2.3 from one body, 5.9 from three, 13.4 from five and 32 from nine.

Which fields get answered depends on where they are (`by_centre.<level>.answered_099`, a
measurement given the truth): from five bodies, 94% of fields centred on C5, 90% on C7 and on
T1, 79% on T2, but 20% on L1, 23% on T12 and 0 to 6% on T5 to T8; from nine bodies 99% at C7,
97% at T1, 83% at L1, 63% at T12, 46% at T8.

## 3 What a field can say for certain about its middle body (`widths.<n>.regimes.both.claims`)

This answers the second ask: a statement weaker than a name, about one body, from as few bodies
as possible. At 0.99 a field says, of its middle body, "at or below" or "at or above" each of
the twenty-one borders when the posterior says so, the region it lies in, and the shortest run
of levels holding 99 per cent of its posterior.

**Over all fields, the claims hold as promised.** From one body, the rule makes 699,004 border
claims (about sixteen of the twenty-one borders per field) and 264 are wrong: 99.96% right. From three
bodies, 197 of 654,844 are wrong (99.97%); from nine, 23 of 354,013 (99.99%). Every border on
its own is right at least 99.92% of the times a claim is made at it, from every width scored
(`claims.cuts.<border>.precision`). The region claim is made for 60.9% of single bodies and is
wrong 21 times in 26,786 (99.92%); for 83.1% of three-body fields, 18 wrong of 33,245; for 97.2%
of nine-body fields, 1 wrong of 27,222 (`claims.regions`). Those rates are pooled over every
body, most of them far from a regional border; near one, a group picked by the truth for which
nothing is promised, the claim is harder (`supplement.region_split.generator`). Within two levels
of C7/T1 it is made for 56% of single bodies and is wrong 7 times in 4,501 (99.84%), within two
of T12/L1 for 7% and 12 times in 568 (97.9%); from three bodies, for 93% (1 wrong of 7,444) and
44% (16 wrong of 3,547, 99.55%). Far from both, it is wrong twice in 21,717 from one body and
once in 22,254 from three. The 99 per cent run of levels holds
the middle body in 99.65% of fields from one body, at a mean of 6.3 levels; 99.7% from three, at
3.7; 99.9% from nine, at 1.4 (`claims.interval`).

**Near the border, where a claim is hard.** Most of those claims are about bodies far from the
border, where they are almost never wrong. Of the pairs of a field and a border whose middle body lies
within two levels of that border (the two above and the two below; a body near several borders
counts once at each), the rule makes a claim at that border:

| Bodies in view | Claims made, near the border | Wrong | Right |
|---:|---:|---:|---:|
| 1 | 16.3% (26,762 of 164,000) | 244 | 99.09% |
| 2 | 31.4% (48,928 of 156,000) | 216 | 99.56% |
| 3 | 45.3% (67,036 of 148,000) | 182 | 99.73% |
| 5 | 67.4% (89,010 of 132,000) | 109 | 99.88% |
| 9 | 90.3% (90,278 of 100,000) | 23 | 99.97% |

Pooled near the border the claims stay at or above 99 per cent, but this is a group picked by
the truth, which the guarantee does not cover (section 0), and border by border it is not: from
one body the claims within two levels of a mid-thoracic or lumbar border are right 93.4% (T5/T6,
22 wrong of 333), 95.3% (T4/T5, 16 of 340), 96.6% (L3/L4, 7 of 206) and up to 98.9% of the
time: of the twenty-one borders thirteen fall below 99% from one body, three from three bodies
(T5/T6 98.3%, T6/T7 98.4%, T7/T8 98.9%), and none from five (the lowest T6/T7, 99.34%) or nine
(`claims.cuts.<border>.precision_within_two`; figure `exact_claims`).

**Where one body is enough.** From one body, the rule says of its middle body:

- *cervicothoracic*: "at or below T1" or "at or above C7" for 56% of the bodies within two
  levels of the C7/T1 border, and right in 4,507 of 4,514 (99.84%); at T1/T2, 47% and 99.79%;
  at C6/C7, 52% and 99.61%. Three bodies make the C7/T1 claim for 93% of nearby fields, one
  wrong in 7,444.
- *coarse but nearly always*: of a single lumbar body the rule says "at or below T5" (the
  owner's "below T4") for 99.4% of true L1 bodies and 99.9 to 100% of L2 to L5; "at or below
  T1" for every body from T8 down (100% of the columns) and 99.8% of T6 bodies; and of a single
  cervical body "at or above T12" for every one of them, of T1 to T4 bodies for 99.6 to 99.75%
  (`claims.cuts.<border>.decided_by_level`, shares said given the truth; the claims at these
  borders are right 99.95 to 99.98% of the times they are made, `claims.cuts.<border>.precision`).
- *at the thoracolumbar junction*, from one body, almost nothing: "at or above T12" or "at or
  below L1" for 7.1% of nearby bodies (97.9% right), and for a true L3 the rule says "below L1"
  (at or below L2) in 8% of columns, for a true L5 in 22%. From five bodies it says it for 78%
  of L3 and half of L2 middle bodies (a five-body field is never centred below L3; from three
  bodies it says it for 59% of L4 middle bodies), and the T12/L1 claim for 71% of nearby fields
  (99.84% right); from nine, 88% (99.98%).

In the owner's words, then: from one SPINEPS-measured body, "this is a cervical, thoracic or
lumbar vertebra" can be said for three bodies in five and is wrong about once in 1,300, though
near the thoracolumbar junction it is said for 7% of bodies and is wrong about once in 47;
"this is below T4" can be said of 99.4 per cent or more of lumbar bodies; "this is below L1"
is said from a field of five of 78% of L3 and half of L2 middle bodies (a five-body field is
never centred below L3); and the most local statement one body supports with near certainty is
at the cervicothoracic junction.

## 4 Which measures make which border claims (`widths.<n>.subsets`, figures `exact_measures` and `exact_subsets`)

Every one of the 127 subsets of the seven measures is scored on the same fields. The best subset
of each size, both planes (`subsets`, ranked by exact naming):

| Bodies | Best one | Best two | Best three | All seven |
|---:|---|---|---|---:|
| 1 | upper end-plate width, 21.5% | lower end-plate width + canal width, 28.8% | + lower end-plate depth, 34.8% | 47.3% |
| 3 | lower end-plate width, 33.8% | lower end-plate width + canal width, 46.6% | + lower end-plate depth, 55.7% | 73.1% |
| 5 | upper end-plate width, 44.8% | lower end-plate width + canal width, 60.3% | upper + lower end-plate width + canal width, 69.8% | 85.7% |
| 9 | lower end-plate width, 61.1% | lower end-plate width + canal width, 78.1% | upper + lower end-plate width + canal width, 86.6% | 96.1% |
| 15 | canal width, 80.2% | upper end-plate width + canal width, 93.1% | upper end-plate depth + lower end-plate width + canal width, 97.3% | 99.7% |

Every measure adds something at every width but fifteen, twenty-one and twenty-two: the best
six fall short of all seven by 0.0 to 1.8 points, and the posterior body height, the one measure
the best six leave out at every width from one to seventeen, adds 1.4 points at one body, 0.6 at
nine and nothing at fifteen, where the best six name as many fields as all seven (15,951 of
16,000); from eighteen bodies on the best six fall short by at most two fields. The widths of
the end-plates and of the canal carry most of it, as the identifiability study found with its
classifier.

Near the border a single measure makes few claims, and they are not nearly certain
(`subsets[k=1].claims.cuts_decided_within_two`, `.cuts_errors_within_two`). From one body, the
single measure that makes the most claims near a border is an end-plate width from C3/C4 to
C7/T1 and from T6/T7 to T12/L1, an end-plate depth from T1/T2 to T5/T6, the canal width from
L1/L2 to L3/L4 and the canal depth at L4/L5. It makes a claim for 2.3 to 15.4 per cent of nearby
bodies, and its claims are right 83.0% of the time (the canal width at L3/L4, 40 wrong of 235)
to 99.3% (the upper end-plate width at C6/C7, 9 wrong of 1,235), under 99 per cent at every
border but C6/C7: the upper end-plate width claims a side of C6/C7 for 15% of nearby bodies,
of T11/T12 for 14% (97.9% right) and of T12/L1 for 6% (96.9%); the lower end-plate width of
T10/T11 for 14% (96.7%) and of C5/C6 for 12% (98.5%); the canal width of L1/L2 for 4% (92.2%);
the canal depth of L4/L5 for 10% (91.7%, 48 wrong of 580). The best pair at one body, lower
end-plate width with canal width, makes the C7/T1 claim for 29% of nearby bodies, right 98.7%
of the time (31 wrong of 2,337); all seven for 56%, right 99.84%. Over all fields, claims from
subsets are held to the same 0.99 and keep the same guarantee, since the subset's own posterior
is the Bayes posterior given fewer measurements: from one and from three bodies every subset's
claims at every border are right at least 99.3 per cent of the times they are made
(`subsets[k].claims.cuts_errors`). Near the border, a group picked by the truth, the guarantee
does not reach them (section 0), as the rates above show.

## 5 Is there a formula, or a network, that does as well? (`formula`, `challengers`)

**The closed form.** In the log measures the generator's likelihood is close to normal, and the
size integrates out in closed form: one quadratic discriminant per place, its mean and
covariance written from the table with no fitting and no quadrature (`exact.formula_log_evidence`).
It names 46.5% from one body, 71.9% from three, 84.5% from five, 95.5% from nine and 99.7%
from fifteen, both planes, against the exact rule's 47.3%, 73.1%, 85.7%, 96.1% and 99.7%
(`formula.both.<n>.exact`): an explainable formula within 0.0 to 1.2 points of the ceiling.
It is an approximation, so its posterior carries no guarantee, and it is a little too sure:
it predicts an error of 0.267 from three bodies where 0.281 is counted, and its names at 0.99
are right 98.5% of the time from one body (6 wrong of 409) and 99.34% from three (47 of
7,081), where the exact rule's are 100% and 99.78% (`formula.both.<n>.bayes_error_predicted`,
`.selective`).

**Rules fitted on 5,000 columns** (`challengers.<n>`). Three rules were fitted on 5,000 columns
from the fitting seed (11), five times as many as the earlier studies used, and scored on the
same fields as the exact rule: a quadratic discriminant per place in the log measures (whose
limit with unlimited data is not the exact rule but one Gaussian per place with the log values'
true mean and covariance, which the closed form approximates to second order in the spreads),
the same in the raw measures,
and a network with one hidden layer of 64 units over the log measures, trained by Adam for up
to 3,000 steps and kept at the step whose log loss on 1,000 selection columns (seed 23) was
lowest. Each is set beside the exact rule as the paired difference in points named exactly,
with its standard error clustered by column (`minus_exact`, `minus_exact_se`):

| Bodies | Exact rule | Closed form | Quadratic, log measures | Quadratic, raw measures | Network |
|---:|---:|---:|---:|---:|---:|
| 1 | 47.27% | -0.73 +- 0.12 | -0.79 +- 0.13 | -0.21 +- 0.11 | -0.33 +- 0.11 |
| 3 | 73.08% | -1.15 +- 0.14 | -1.54 +- 0.15 | -0.86 +- 0.12 | -1.49 +- 0.14 |
| 5 | 85.65% | -1.13 +- 0.14 | -1.63 +- 0.15 | -1.01 +- 0.13 | -2.79 +- 0.17 |
| 9 | 96.11% | -0.60 +- 0.10 | -0.97 +- 0.13 | -0.52 +- 0.11 | -4.59 +- 0.21 |

Every rule falls short of the exact rule at each of the four widths scored, the nearest by 1.8 standard errors
(the raw quadratic rule at one body) and the rest by 3 to 22. The log loss, which the Bayes
posterior minimises among all posteriors and which counts every field rather than only the
argmax, says the same more firmly: every challenger's exceeds the exact rule's by 0.011 to
0.118 nats a field, 6 to 26.5 standard errors (`log_loss_minus_exact`). The quadratic rule in the
log measures falls short by a little more than the closed form, which approximates its limit, and the one in the
raw measures closes most of the closed form's gap at one body (-0.21 against -0.73) but only a
tenth to a quarter of it from three bodies on (-0.86 against -1.15 at three). The network falls further behind as the field
widens, from 0.33 points at one body to 4.6 at nine, and it was kept at its last step at every
width (`network.step_kept` 3000) with its selection loss still falling at three bodies and more
(by 0.002 to 0.005 over the last 500 steps, `selection_log_loss`), so its shortfall is partly
its training budget: the record shows that a network of this size and budget did not pass the
exact rule, not that no network can come close to it.

That nothing fitted passes the exact rule is a weak check of the ceiling, since a fitted rule
falls short for reasons of its own. The calibration of section 1 checks something else, that the
likelihood is consistent with the generator: the exact rule's posterior predicts its own error at
every width, which a misstated likelihood generally would not (the closed form, a little too sure,
does not). Agreement in the large is necessary for a right likelihood, not proof of one: a rule
that ignored information would pass it too (the exact rule without the posterior body height
predicts an error of 0.290 from three bodies and counts 0.287, 1.8 points below the ceiling,
`widths.3.subsets`), and the raw quadratic rule's posterior predicts its error from one body as
well (0.531 against 0.529 counted) while missing it at five (0.146 against 0.154). That the exact
rule is the ceiling rests on its construction (section 0). The fitted rules' posteriors are not
certificates either: the quadratic rule in the log measures names single bodies at 0.99 right
97.8% of the time (8 wrong of 366) and, from three bodies, predicts an error of 0.271 where 0.285
is counted (`selective`, `bayes_error_predicted`).

## 6 When the generator is not the truth (`robust`, figures `exact_robust` and `exact_robust_widths`)

Sections 1 to 5 hold while the generator, its table and its settings are exactly true, and the
guarantees of section 0 are about that world alone. A real rule is built on a table that is
itself an estimate: Panjabi's means and spreads come from twelve cadaver spines per level. So
the rule was scored where its premise fails, and three rules built on the same table were set
side by side on the same columns (`robust.rules`):

- **nominal**, the rule of sections 1 to 5, built on the table as printed;
- **predictive**, which knows its table is the mean and SD of twelve spines: a new spine about a
  twelve-spine mean and SD follows a Student t on eleven degrees of freedom, whose variance is
  (1 + 1/12) 11/9 times the SD squared, so every SD is widened by that factor's square root.
  No constant is chosen on any draw;
- **honest**, which widens every SD by the square root of (1 + 1/12), the mean's share of the
  same error, and meets the error in the SDs with a floor instead, taking the measurement error
  at 2 mm where the generator draws 1 mm. The 2 mm was chosen on a pilot of sixteen specimen
  worlds from a seed of their own (5), as the smallest of 1, 1.5 and 2 mm whose answers at 0.99
  were right at least 99 per cent of the time from three and from nine bodies (the pilot table below), so
  the worlds below test that choice on fresh draws of the same model, not on a different one.

The worlds, each drawn from seeds of its own:

- **Specimen worlds** (40, `robust.table_specimens`): the rule's table re-estimated from twelve
  columns drawn from the generator with no size spread and no measurement error, as Panjabi's
  own was estimated from twelve cadavers (the generator adds size and error on top of the
  table's SDs, so the SDs are re-estimated without them; a real cadaver table's SDs hold its
  cadavers' spread of size too, which a rule then counts twice, on the safe side), and 100
  columns scored per world, drawn from the table as printed. The table's errors are shared
  across levels through each specimen's own offsets, as a real table's are. This is the
  realistic case for Panjabi's table: a rule built on it carries a twelve-spine table's error;
  a table from more spines was not scored.
- **Level worlds** (40, `table_levels`): the rule on the printed table, the columns from a table
  whose every mean and SD is redrawn, independently by level, as a true table the printed
  twelve-spine estimate could have come from: each mean from N(mean, SD / sqrt 12), each SD the
  printed SD over sqrt(chi^2_11 / 11).
- **Combined worlds** (20, `combined_worlds`): specimen worlds whose columns also carry a
  correlation of 0.4 between measures and 1.5 mm of measurement error.
- **One setting wrong at a time** (`misspecified`, 500 columns each): rho 0.3 or 0.7; the size
  SD 0.035 or 0.14; the measurement error 0.5, 2 or 3 mm; a correlation between measures of 0.4
  or 0.8, which the rule leaves out; and two biases (`bias`): a size gradient of 5 per cent from
  C3 to L5, and both canal measures 8 per cent low, as a segmenter that undercuts the canal
  might give them.

Standard errors are clustered by world, or by column in the single 500-column worlds.

**A rule built on a twelve-spine table loses its 99 per cent.** In the specimen worlds
(`table_specimens.<rule>.<n>`; the near-border rate is `claims.cuts_precision_within_two`):

| Bodies | Named exactly (5 to 95% of worlds) | Right at 0.99: nominal (answered) | predictive | honest | Near-border claims right: nominal / predictive / honest |
|---:|---:|---:|---:|---:|---:|
| 1 | 40.1% (38.0 to 42.0) | 95.3% +- 1.0 (1.0%) | 96.9% +- 0.8 (0.5%) | 95.3% +- 3.5 (0.1%, 64 answers) | 97.2 / 98.1 / 98.6% |
| 3 | 60.2% (57.2 to 62.5) | 95.5% +- 0.2 (19.5%) | 97.6% +- 0.2 (14.8%) | 99.30% +- 0.19 (5.5%) | 97.8 / 98.6 / 99.3% |
| 5 | 72.5% (68.7 to 75.4) | 95.0% +- 0.3 (40.5%) | 97.1% +- 0.2 (33.9%) | 99.18% +- 0.10 (20.3%) | 98.2 / 98.8 / 99.6% |
| 9 | 86.4% (82.3 to 90.9) | 96.1% +- 0.3 (68.5%) | 97.2% +- 0.2 (62.2%) | 98.91% +- 0.12 (42.9%) | 98.9 / 99.2 / 99.7% |
| 15 | 97.0% (94.9 to 98.8) | 98.9% +- 0.1 (93.5%) | 99.2% +- 0.1 (91.7%) | 99.59% +- 0.07 (82.2%) | (not scored) |

The rate named exactly is the nominal rule's; the other two are within 0.6 points of it at every
width, since widening the spreads changes how sure the rule is far more than what it names.
Three things follow.

- *The ceiling moves.* Built on a twelve-spine table, the exact rule names 40%, 60%, 72% and
  86% of fields from one, three, five and nine bodies, 7 to 13 points below the 47%, 73%, 86%
  and 96% of section 1, and the share depends on which twelve spines the table came from: from
  nine bodies, 82% to 91% across the middle nine-tenths of tables. A rule fitted on enough real
  columns would not carry the table's error; a rule built on published means does.
- *The nominal rule's certificate fails.* Its answers at 0.99 are right 95 to 96 per cent of
  the time from one to nine bodies, its near-border claims 97.2 to 98.9 per cent.
- *The honest rule nearly restores it over all its answers, at a price in answers, but not
  within every region it names.* Its names at 0.99 are right 99.30% of the time from three
  bodies, 99.18% from five, 98.91% from nine (just short, by 0.09 points, within its standard
  error of 0.12) and 99.59% from fifteen; its near-border claims 99.3% or better from three
  bodies. It answers 5.5% of three-body fields where the nominal rule answered 19.5%, and 42.9%
  of nine-body fields against 68.5%. The predictive rule, which chose nothing, sits between the
  two. The pooled rate leans on the cervical names. Split by the region its named place puts
  the middle body in (`table_specimens.<rule>.<n>.selective_099_by_called_region`, a group picked
  out by the measurements, within which section 0's guarantee would hold were the table true),
  its names at 0.99 are right 99.61%, 99.82% and 99.97% of the time from three, five and nine
  bodies when it calls the field cervical; when it calls it thoracic, 99.19% from three
  (+- 0.30) but 98.69% from five (74 wrong of 5,667, +- 0.17) and 98.63% from nine (249 wrong
  of 18,218, +- 0.15); when it calls it lumbar, 96.75% from three (8 wrong of 246, +- 1.09),
  97.65% from five (32 wrong of 1,359, +- 0.52) and 99.45% from nine (+- 0.18). So its
  thoracic names from five and nine bodies and its lumbar names from three and five fall short
  of 99 per cent, each by about two standard errors or more. In the specimen worlds the
  predictive rule's lumbar names are right 93.3% and 95.3% of the time from three and five
  bodies, the nominal rule's 88.6% and 92.6%. In the combined worlds
  (`combined_worlds.<rule>.<n>.selective_099_by_called_region`) the honest rule's lumbar names
  from three bodies are right 92.54% of the time (10 wrong of 134, +- 1.88), the predictive
  rule's 88.4% and the nominal rule's 81.4%.

Border by border the honest rule still falls short close to some borders from few bodies
(`table_specimens.honest.<n>.claims.cuts.<border>.precision_within_two`): from one body it is
right 92.0% of the time near L4/L5 (659 claims), 93.3% near T4/T5 and 93.9% near L3/L4, and
fifteen of the twenty-one borders are under 99%; from three bodies ten are (the lowest T5/T6,
96.8%); from five, four (the lowest T7/T8, 98.1%); from nine, none (the lowest T8/T9, 99.3%).
The nominal rule from nine bodies still has eight borders under 99%, the lowest T8/T9 at 97.7%.

**What survives from one body.** Two of section 3's statements hold in the specimen worlds:

- the *region*: the nominal rule names it for 62.5% of single bodies and is right 99.64% of
  the time (198 wrong); the honest rule for 54.4% and 99.90% (47 wrong); in the combined worlds
  99.62% and 99.90% (`claims.regions_precision`). These rates are pooled over every single body,
  most of them far from a regional border; split, within two levels of C7/T1 the nominal rule's
  region claim is right 99.05% of the time (92 wrong of 9,707) and the honest rule's 99.70% (20
  of 6,677), but within two of T12/L1, where the region claim is the thoracolumbar claim and
  fails like it, 94.07% (97 wrong of 1,635) and 97.26% (26 of 949); far from both, 9 wrong of
  43,697 and 1 of 40,248, so 189 of the nominal rule's 198 errors are near a regional border
  (`supplement.region_split.worlds.specimens`; the level and combined worlds alike, 94.4 to 97.2
  per cent near T12/L1);
- the *cervicothoracic claim*: within two levels of C7/T1 the nominal rule claims a side for
  60.9% of bodies and is right 99.06% of the time, the honest rule for 42.1% and 99.70%; in the
  combined worlds 98.89% and 99.74%.

The thoracolumbar claim from one body does not: near T12/L1 it is right 94.1% (nominal) to
97.3% (honest) of the few times it is made. From five bodies the honest rule makes it for 52%
of nearby fields at 99.63%, from nine for 69% at 99.48%. The record does not hold the per-level
statements of section 3 ("at or below T5", the owner's "below T4", for 99.4 per cent or more of
lumbar bodies) for these worlds; over every field, the claims at T4/T5 from one body are right
99.96% of the times the honest rule makes them (for 63.9% of single bodies) and 99.86% for the
nominal rule (69.1%) (`claims.cuts.T4/T5`).

**Three premises wrong at once** (a twelve-spine table, a correlation of 0.4 between measures and
1.5 mm of error). In the combined worlds the exact names drop to 38%, 56%, 68%,
82% and 95% from one, three, five, nine and fifteen bodies; the nominal rule's answers at 0.99
are right 92 to 94 per cent of the time to nine bodies, the predictive rule's 94 to 96, the
honest rule's 99.0% from three and from five bodies and 98.4% from nine (+- 0.2); the honest
rule's near-border claims stay at 99.3 to 99.5% from three bodies
(`combined_worlds.<rule>.<n>`).

**One setting wrong at a time** (`misspecified.<setting>.<rule>.<n>`, `bias.<kind>.<rule>.<n>`;
500 columns each, so a rate on a few hundred answers carries a standard error of a few tenths):

| World | Named exactly, 9 bodies (nominal) | Right at 0.99, nominal: 3 / 9 bodies | honest: 3 / 9 | Near-border claims right, nominal: 1 / 3 / 9 | honest: 1 / 3 / 9 |
|---|---:|---:|---:|---:|---:|
| Generator as assumed | 96.3% | 99.64 / 99.78% | 100 / 100% | 98.9 / 99.7 / 99.9% | 99.1 / 99.8 / 100% |
| rho 0.3 | 95.3% | 99.88 / 99.80 | 100 / 100 | 98.9 / 99.6 / 99.9 | 99.4 / 99.8 / 99.97 |
| rho 0.7 | 97.4% | 99.94 / 100 | 100 / 100 | 99.2 / 99.7 / 100 | 99.6 / 99.9 / 100 |
| Size SD 0.035 | 96.4% | 99.82 / 99.86 | 100 / 99.97 | 99.5 / 99.9 / 99.96 | 99.9 / 99.98 / 99.99 |
| Size SD 0.14 | 95.4% | 99.82 / 99.90 | 100 / 99.96 | 91.5 / 97.8 / 99.84 | 89.9 / 97.0 / 99.85 |
| Error 0.5 mm | 97.8% | 100 / 99.91 | 100 / 100 | 99.3 / 99.9 / 99.97 | 99.5 / 99.98 / 100 |
| Error 2 mm | 89.4% | 96.2 / 98.7 | 99.8 / 99.96 | 96.8 / 98.5 / 99.55 | 98.4 / 99.6 / 99.9 |
| Error 3 mm | 73.4% | 82.6 / 87.7 | 96.85 / 97.95 | 91.3 / 93.1 / 96.15 | 95.1 / 97.9 / 99.2 |
| Measures correlated, r 0.4 | 96.6% | 99.88 / 99.94 | 100 / 100 | 98.6 / 99.7 / 99.97 | 98.6 / 99.85 / 99.99 |
| Measures correlated, r 0.8 | 96.3% | 99.94 / 99.96 | 100 / 100 | 99.2 / 99.9 / 99.99 | 99.4 / 99.97 / 100 |
| Size gradient 5% | 96.5% | 99.71 / 99.94 | 100 / 100 | 98.5 / 99.6 / 99.98 | 98.8 / 99.8 / 100 |
| Canals 8% low | 94.7% | 99.59 / 99.89 | 100 / 100 | 97.9 / 99.2 / 99.95 | 98.6 / 99.5 / 100 |

Two settings break the claims. *Measurement error past what the rule assumes*: at 2 mm the
nominal rule's names at 0.99 are right 96.2% of the time from three bodies, at 3 mm 82.6%, and
even the honest rule, which assumes 2 mm, falls to 96.85% from three bodies and 97.95% from
nine at 3 mm; the exact names from nine bodies fall from 96% to 89% at 2 mm and 73% at 3 mm. *A size
spread twice the generator's* leaves the names at 0.99 right but breaks the near-border claims
from one body (89.9 to 91.5% in every rule) and from three (97.0 to 97.8%), and takes the region
claim from one body to 98.5 to 98.6% in every rule (81 to 95 wrong); from nine bodies the
border claims hold. Everything else costs little: a setting changed in the rule's favour, the two biases and a
correlation between measures the rule leaves out move the exact names from nine bodies by at
most 1.6 points (the canals 8 per cent low, 94.7% against 96.3%) and the near-border claims
from one body by at most a point. Given the correlation (`r_known`, the joint likelihood at the
true r, 400 columns), the rule names 47.3%, 73.4% and 96.4% from one, three and nine bodies at
r 0.4, against 48.1%, 73.8% and 96.6% for the rule that leaves it out, and 48.9%, 75.2% and
96.9% at r 0.8, against 48.1%, 74.1% and 96.3%. The two are scored on different columns (the
rule that leaves it out on the 500 of `misspecified`), and the record keeps no standard error
for these single draws; scaled from section 1's clustered standard errors, a difference between
400 and 500 columns carries about 0.8 to 0.9 points at one and three bodies (0.6 at nine), so
the differences,
-0.8 to +1.1 points, are within about 1.3 standard errors. The rule given r is the Bayes rule for
those columns and cannot do worse in expectation, so its shortfall at r 0.4 is noise: these
draws do not resolve what leaving the correlation out costs, and the most they show is 1.1
points (three bodies, r 0.8).

**The pilot that chose the honest rule** (`robust.pilot.<variant>.<n>`, sixteen specimen worlds
from seed 5):

| Variant (`pilot_rules`) | Right at 0.99: 1 / 3 / 9 bodies | Answered at 3 / 9 bodies | Near-border claims right: 1 / 3 / 9 |
|---|---:|---:|---:|
| nominal | 95.6 / 95.1 / 96.1% | 19.9 / 68.6% | 97.0 / 97.6 / 98.9% |
| SD x sqrt(13/12) | 96.3 / 95.8 / 96.5 | 18.6 / 67.0 | 97.3 / 97.8 / 99.0 |
| SD x sqrt(13/12), 1.5 mm | 99.0 / 98.0 / 98.0 | 11.6 / 56.7 | 97.9 / 98.7 / 99.4 |
| SD x sqrt(13/12), 2 mm (honest) | 96.3 / 99.3 / 99.1 | 6.0 / 43.8 | 98.1 / 99.2 / 99.7 |
| SD x sqrt(13/12), smoothed by level | 92.0 / 94.4 / 93.1 | 7.5 / 39.9 | 97.4 / 98.2 / 98.6 |
| predictive | 97.4 / 97.4 / 97.3 | 15.2 / 62.2 | 97.9 / 98.4 / 99.2 |

The honest rule answers 27 single bodies in the pilot and 64 in the specimen worlds, too few to
say whether it keeps 99 per cent from one body (95.3% +- 3.5 in the specimen worlds).

**What this means for a real series.** The realistic world is the specimen one. A rule built on
a twelve-spine table should be expected to name about 86 fields in a hundred from nine bodies,
not 96; to certify names and border claims at 99 per cent it needs a wider spread than the
table prints, as the honest rule takes, though even the honest rule's thoracic and lumbar names
fall short of 99 per cent from three to nine bodies at some widths (above), and that spread was
tuned on simulated worlds of the same model, so a real series must check it before it is trusted; and the measurement error of
SPINEPS-derived measures on the images to be read has to be measured, since past the error the
rule assumes no rule here keeps its certificate.

## 7 What can be said, and on what condition

The statements of sections 2, 3 and 6 side by side, each about the field's middle body, with how
often it can be said, how often it is right while the generator is the truth, and how often in
the specimen worlds of section 6, where the rule is built on a twelve-spine table. The first two
columns of rates are counted on the 2,000 scoring columns; "within two" means the bodies within
two levels of the border the claim is about.

| Statement | Bodies in view | Said for | Right, generator true | Right, twelve-spine table: honest rule (said for); nominal rule (said for) | Record |
|---|---:|---:|---:|---:|---|
| It is cervical, thoracic or lumbar | 1 | 60.9% of bodies | 99.92% (21 wrong of 26,786) | 99.90% (54.4%); 99.64% (62.5%) | `claims.regions`; `regions_precision` |
| It is at or below T1, or at or above C7 | 1 | 56% of bodies within two of C7/T1 | 99.84% | 99.70% (42.1%); 99.06% (60.9%) | `claims.cuts.C7/T1` |
| The same | 3 | 93% within two | 99.99% (1 wrong of 7,444) | 99.91% (79.5%); 99.71% (92.1%) | `claims.cuts.C7/T1` |
| It lies in this run of levels (99 per cent) | 1 | every body; 6.3 levels on average | 99.65% | 99.64% at 7.1 levels; 98.55% at 6.1 | `claims.interval`; `interval_coverage` |
| The same | 3 | every field; 3.7 levels | 99.7% | 99.39% at 4.5 levels; 96.83% at 3.5 | the same |
| It is at or below T5 (the owner's "below T4") | 1 | 99.4% of L1, 99.9 to 100% of L2 to L5 bodies | 99.95% of all claims at T4/T5 | 99.96% of all claims at T4/T5 (63.9% of all bodies); 99.86% (69.1%); the shares by true level not recorded | `claims.cuts.T4/T5` |
| It is at or below L2 (the owner's "below L1"), or at or above L1 | 5 | "at or below L2" for 78% of L3 and 50% of L2 bodies; a claim either way for 67% within two of L1/L2 | 99.91% within two | 99.55% (48.7% within two); 98.31% (67.8%) | `claims.cuts.L1/L2` |
| It is at or above T12, or at or below L1 | 5 | 71% within two of T12/L1 | 99.84% | 99.63% (52.1%); 98.75% (70.5%) | `claims.cuts.T12/L1` |
| The same | 9 | 88% within two | 99.98% | 99.48% (68.8%); 98.55% (83.4%) | the same |
| Its name, and so every body's, at 0.99 | 9 | 71.8% of fields | 99.93% | 98.91% (42.9%); 96.08% (68.5%) | `selective.0.99` |
| The same | 15 | 97.8% of fields | 99.98% | 99.59% (82.2%); 98.92% (93.5%) | the same |

The most local statements one body supports nearly certainly are the region and the side of
the cervicothoracic border: in the specimen and level worlds of section 6 both are right 99 per
cent of the time or more as measured, whichever rule makes them (the lowest, the nominal rule's
cervicothoracic claim in the specimen worlds, 99.06% +- 0.09, 92 wrong of 9,747, is less than
one standard error above 99, so not shown to reach it), and the honest rule keeps both at 99.7
per cent or more in those worlds and in the combined ones, where the nominal rule's
cervicothoracic claim falls to 98.89%. The region's rates are pooled over every body: within
two levels of T12/L1 the region claim from one body is the thoracolumbar claim, right 94.1 per
cent (nominal) to 97.3 per cent (honest) of the few times it is made in the specimen worlds, so
the region is a near-certain statement for one body away from the thoracolumbar junction only
(`supplement.region_split.worlds`).

Two of section 6's single settings each break one of the two in every rule. With a spread of patient size twice
the generator's, the region claim is right 98.5 to 98.6 per cent of the time (81 to 95 wrong of
5,602 to 6,489 claims) and the cervicothoracic claim 98.7 to 98.9 per cent (9 to 15 wrong of 787
to 1,133 claims, 0.14 to 0.32 points short of 99; the record keeps no standard error for one
border in one setting, `precision_within_two_se` being NaN there, and a binomial one from these
counts, 0.34 to 0.38 points, which leaves out the clustering by column, puts all three within
one of 99). At 3 mm of measurement error the
cervicothoracic claim is right 96.1 to 97.8 per cent of the time (18 to 43 wrong of 814 to 1,112
claims), while the region claim, pooled over every body, is right 99.1 to 99.6 per cent
(`misspecified.scale_sd=0.14`,
`misspecified.noise_mm=3`). A statement about the
thoracolumbar junction at the same certainty needs about five bodies, and a name for every body
of the field needs about nine with the generator true and more than nine with a twelve-spine
table. These rates are averages over the uniform prior of section 0 and over the specimen
worlds, not a promise about one table, one patient or one series.

## 8 Assumptions every number rests on

- **Fields inside C3 to L5.** Every field but those of section 10's anomalous columns lies wholly
  between C3 and L5, at one of the 23 - n places of section 0; a field that reaches C2 or the sacrum has no place in the rule, and what
  such a landmark adds is not measured.
- **Typical columns only.** Every column but section 10's has C3 to L5 in the usual count; no
  anomalous phenotype is in the rule, and none is in any score but section 10's names on three
  anomalous phenotypes (`supplement.anomalous`), the one score that does not rest on this
  assumption. The neighbour study measured what an extra or missing
  body does to a fitted rule (`docs/NEIGHBOUR_IDENTITY_RESULTS.md`); the exact rule has no
  place for a column of the wrong length, so on such a column its posteriors are about a
  population the column does not belong to.
- **Panjabi's table is the population.** Twelve cadaver spines per level (Panjabi 1991,
  cervical and thoracic, and 1992, lumbar, as `bordercall/reference/panjabi_full_spine.csv`
  holds them). Section 6 measures what
  the table's own sampling error does; a population unlike Panjabi's, a segmenter whose
  measures differ from his calipers, or a projection that changes them, is beyond it except
  for the two biases scored there.
- **The generator's correlation structure.** rho 0.5 within a column for each measure, the
  patient's size lognormal with SD 0.07, the measurement error 1 mm, the measures independent
  given the size (r 0). Section 6 sets each wrong in turn; the correlation of the offsets down
  a real column, and between measures, is not known from any published table.
- **A uniform prior over places.** Every place of every column counts once, in the rule and in
  the score. The guarantees are averages under that prior.
- **The floor.** The generator clips each value at 0.5 mm, which the likelihood leaves out;
  4 of the 308,000 scored values touched it, all canal depths (at C3, C7 and T2; `floor`).
- **Nothing here is a patient.** No CT, no radiograph, no label and no corpus was used, and no
  number here measures a person.

## 9 Checks outside the computation

- **The closed form against the dense density.** At r 0 the Sherman-Morrison likelihood equals
  the dense joint normal density over all seven measures to 6.3e-13 or better in the log
  evidence at one, four and nine bodies, on the fields of the first 50 of the 2,000 scoring
  columns (`joint_check`); the test suite holds it to scipy's multivariate
  normal density (`tests/test_exact.py`, `TestLikelihood`).
- **The quadrature.** Against an independent trapezoid rule on 1,801 nodes over +-9 SD, on the
  8,400 fields of the first 100 of the 2,000 scoring columns at the six widths tried (1, 3, 5,
  9, 15 and 21), the largest difference in a 161-node Gauss-Hermite posterior is 7.1e-10 and no
  call changes; with 41 nodes, the identifiability study's, the largest is 0.0034 and no call
  changes either (`quadrature_check`). On all 2,000 columns (168,000 fields at those six
  widths; `supplement.quadrature_all`) the largest 161-node difference is 1.1e-9 and no call
  changes; with 81 nodes the largest is 2.8e-5 and none changes; with 41 nodes the largest is
  0.0055 and 5 calls change, at three, five, nine and fifteen bodies, none at one.
- **The supplement against the record.** Its robustness worlds, drawn again from the record's
  seeds by the same calls, give the record's region counts in all 18 cells of kind, rule and
  width (`supplement.region_split.matches_record`), so its region split is of the record's own
  worlds.
- **One body reproduces the earlier exact rule.** With 41 nodes the rule names single bodies
  right as often as the identifiability study's exact one-body rule, to twelve decimal places
  of the rate, on the first 60 of that study's scoring columns (1,320 bodies;
  `tests/test_exact.py`, `TestRule`, which compares the rates, not the calls); that study
  recorded 47.3% on its 1,000 columns
  (`records/identify-2026-10-26/identify.json`, `bayes.exact_likelihood`), and this rule names
  47.27% on 2,000 (`widths.1.regimes.both.exact`).
- **Two places with equal covariance err at Phi(-d/2)**, the textbook value (`TestRule`).
- **Calibration on fresh draws** (section 2) and **the challengers** (section 5): no fitted rule
  names more fields than the exact rule beyond its standard error.
- **The seeds.** Each kind of robustness task (the table worlds, the combined worlds, the pilot,
  the single settings with the biases, the known correlations) draws its seeds from a stream of
  its own, so adding worlds of one kind moves no other kind's seeds: more table worlds move
  neither the pilot's seeds nor the first specimen worlds' (`TestRobust`). The specimen and level
  worlds share one stream, specimens first, so the number of table worlds moves the level
  worlds' seeds, as a further single setting would move the biases'.

## 10 What could not be settled here

- **Columns of another length.** The rule has places for typical columns only. On the
  generator's own anomalous phenotypes its posteriors are about a population the column does
  not belong to. Its names at 0.99, each middle body judged by the name its own column's count
  gives it (`supplement.anomalous`, 150 columns of each phenotype), are wrong once in 1,502 on
  four-lumbar columns (1 of 980 from five bodies, none from one or three), never from one or
  three bodies on T13 columns (524 names) but 13 times in 964 from five (98.65%), and on
  six-lumbar columns, whose sixth lumbar body has no place in the rule, 2 times in 20 from one
  body, 15 in 531 from three (97.2%) and 39 in 1,073 from five (96.4%). A rule for anomalous
  spines needs each phenotype as places of
  its own, weighted by its prevalence, which `exact.posterior` admits and nothing here builds.
- **A real series' prior over places.** Fluoroscopy fields are not spread evenly along the
  spine. `exact.posterior` takes a prior, but no series has given one, and a call at 0.99
  whose rival place is ten times as common as its own is right only 0.99 / 1.09 = 91% of the
  time under that series' frequencies.
- **Heavy tails and segmentation outliers.** Every error here is normal. A mask that cuts a
  body short gives a value the normal likelihood calls nearly impossible at the right place, and
  the rule may then grow sure of a wrong one; not tested.
- **Measurement error that differs by measure, or grows with size.** Section 6 sets one error
  for every measure; SPINEPS-derived end-plate and canal measures need not share one.
- **Fitted rules where the table is wrong.** No challenger was scored in the worlds of section
  6. A rule fitted on enough real columns would not carry the twelve-spine table's error, so
  the exact rule's lead over fitted rules in section 5 says nothing about real spines.
- **Real data.** Nothing here is a measured column. The first real test is the grid pilot over
  the census's existing SPINEPS masks counted from C2, which waits for the owner's word.

## 11 Figures

In `records/exact-2026-10-26/figures/`, each with a caption file and a CSV of every number
drawn; `FIGURES.md` there holds the sha256 of the record and of each code file.

- `exact_ceiling`: the share named exactly by width and plane; the share named at 0.99 and
  0.999; and by how many points the closed form and the fitted rules fall short (section 1, 2, 5).
- `exact_calibration`: the error predicted against the error counted, by bins of the
  posterior; and the share named at 0.99 by true level (section 2).
- `exact_claims`: at every border, the share of nearby bodies about which a claim is made, by
  the bodies in view (section 3).
- `exact_interval`: the median length of the 99 per cent run of levels by true level and width
  (section 3).
- `exact_measures`: at which border a single measure, the best pair and all seven make claims,
  one and three bodies (section 4).
- `exact_subsets`: the best subset of each size by width (section 4).
- `exact_robust`: the three rules in thirteen of the fifteen worlds of section 6, three bodies
  (the size SD 0.035 and the 0.5 mm error, two settings in the rule's favour, are neither drawn
  nor in the CSV; the known-r rule is not drawn, and the pilot's variants are in the CSV only).
- `exact_robust_widths`: the three rules in the specimen worlds, by width.

## 12 What the review corrected

While the first full run was still going, its code was read by four readers, each told to
refute one part (the likelihood, the claims, the robustness design and the ceiling), who ran
small checks of their own. What they found, and what changed:

- *The premise was stated too broadly.* The guarantees hold for typical columns under a
  uniform prior over places, marginally and given any function of the measurements, but not
  given the truth; rates by true level, by landmark and near a border are now called
  measurements (section 0), and the union bound for two claims about one field is stated.
- *"The values are normal"* is true given the size; marginally they are a scale mixture, cut at
  the 0.5 mm floor. Reworded, and the floor's hits recorded (`floor`).
- *Border claims pooled over every field hid where they fail.* From one body 96 claims in a
  hundred are about bodies three or more levels from their border, where they are almost never
  wrong (20 wrong of 672,242; `widths.1.regimes.both.claims.cuts`). Border
  claims are now given near the border too, with a standard error in the robustness worlds, and
  the robustness figures draw the near-border rate. The region and interval claims are recorded
  over every field; the supplement splits the region claim near the two regional borders.
- *The owner's phrases.* "Below L1" is "at or below L2", made at L1/L2, not the claim at T12/L1.
- *The level worlds drew the table's SD on the forgiving side* (the estimate times
  sqrt(chi^2/11) where a plausible true SD is the estimate over it). Fixed; there the nominal
  rule's names at 0.99 are now right 99.05 to 99.29 per cent of the time from three to nine
  bodies and 96.75% from one (`table_levels.nominal`).
- *The honest rule's 2 mm was tested only up to 2 mm.* A 3 mm world was added, and it breaks
  every rule (section 6).
- *The pilot that chose the 2 mm was recorded nowhere.* It is now part of the run
  (`robust.pilot`), with every variant it compared, and a predictive rule that chooses nothing
  was added beside the honest one.
- *A worst-world precision was mostly the noise of a hundred answers.* Dropped; the pooled
  precision now carries a standard error clustered by world.
- *Several premises wrong at once, and biases, were missing.* The combined worlds and the two
  biases were added.
- *The challengers would have run out of memory and lost the whole record.* The exact rule is
  now scored in chunks there, every part's failure is recorded rather than raised, and the
  record is written after each part.
- *A quadratic rule in the log measures can reach at best one Gaussian per place (the log
  values' true mean and covariance, which the closed form approximates), not the exact rule.*
  The same rule in the raw measures and the closed form itself were added beside it, each with
  the paired standard error of its difference from the exact rule; the network now stops early
  on a selection set of its own.
- *The closed form is an approximation*, and is called one.

The tables of this document were then checked number by number against the record, and the
finished document was read again by five readers, one part each, every finding re-checked by a
reader of its own (99 readers in all). 82 findings held, and the readers' own scripts became
the supplement (`bordercall/exact_supplement.py`, `supplement.json`). What changed:

- *The honest rule's names are not 99 per cent right in every region.* In the specimen worlds
  its pooled 98.9 to 99.3 per cent from three to nine bodies leans on its cervical names; its
  lumbar names are right 96.75% from three bodies and its thoracic ones 98.69% from five
  (`robust.table_specimens.honest.<n>.selective_099_by_called_region`). Verdict 4 and section 6
  now give the shortfall. Why is not tested here. One candidate: the honest rule scales every
  SD by the same factor and adds the same 2 mm of error, and the table's lumbar SDs are mostly
  3 to 5 mm (23 of 35) and its cervical ones mostly under 2.5 mm (27 of 35;
  `bordercall/reference/panjabi_full_spine.csv`, the seven measures), so against the nominal
  rule it widens a lumbar spread by a median of 15 per cent and a cervical one by a median of 33
  per cent (`exact.RULES`, `rule_table`, `rule_synth`). That does not explain the thoracic
  names, whose spreads it widens by a median of 22 per cent and which from nine bodies fall
  shorter (98.63%) than the lumbar ones (99.45%;
  `table_specimens.honest.9.selective_099_by_called_region`).
- *The region claim near T12/L1 is the thoracolumbar claim.* Pooled over every body it looked
  near certain in the specimen worlds; split, it is right 94.1 to 97.3 per cent within two
  levels of T12/L1 from one body (`supplement.region_split`). Verdicts 3 and 4 and sections 3,
  6 and 7 say so.
- *Verdict 4's sentence on 2 mm and 3 mm of error* misread the single settings; it now gives
  their numbers (section 6).
- *A single measure does not settle a border.* Section 4 now says which measure makes claims
  at which border, for how few nearby bodies and how often right.
- *The L1/L2 row of section 7* was labelled as one side of the border; like every border
  claim it is a claim for either side, and is relabelled.
- *Roundings.* The specimen worlds' share named (40.1%), two of the specimen worlds' standard errors (+-0.2, the nominal rule's from three bodies and
  the predictive rule's from nine), the
  size setting's rates (97.8% and 97.0%), the classifier's one- and three-body rates (36.5%
  and 58.2%) and two calibration figures (0.271 and 0.143) now match the record to the digit
  shown.
- *Checks the record did not hold.* The quadrature was measured on the first 100 of the 2,000
  scoring columns, the exact rule's rates on all 2,000 columns were set beside a classifier scored on only the
  first 1,000 of them, and the
  anomalous columns were only described; the supplement checks the quadrature on every column
  (section 9), scores the exact rule on the classifier's 1,000 columns (section 1) and scores
  its names on three anomalous phenotypes (section 10).

The rest were wordings and references, each checked against the record or the code. The passages
this changed were read a third time by six readers, every finding re-checked by another (34
readers in all), and the 27 findings that held are corrected in place: among them verdict 3's
single-measure sentence, the 2 mm and 3 mm rates of verdict 4 and the size setting's
cervicothoracic rates of section 7 now weighed against a standard error, which worlds section
6's lumbar rates come from, a standard error, two roundings and the low end of section 4's
range, and four figure captions brought under sixty words. Two more readers then read those
corrections, each finding re-checked (8 readers in all), and the six findings that held are
corrected in place: two standard errors in verdict 4 now say where they come from, the T12 rates
of verdict 1 and section 1 name their fields, and the list of numbers from elsewhere and section
8's first assumption now cover section 9's test columns and section 10's anomalous columns.

## Files

- `bordercall/exact.py`: the rule, the claims, the subsets, the closed form, the challengers,
  the robustness worlds and the checks; `python run.py exact` runs it.
- `bordercall/exact_supplement.py`: the checks the second review asked for (the region claim
  near a regional border, the quadrature on every column, the exact rule on the classifier's
  columns, the anomalous columns); `python run.py exact-supplement`.
- `bordercall/exact_figures.py`: the eight figures; `python run.py exact-figures`.
- `tests/test_exact.py`: the likelihood against scipy's dense normal density, the quadrature
  against an independent rule, the earlier one-body rule reproduced, the Bayes error of two
  places, the guarantees on fresh draws, the claims' bookkeeping, the robustness tables and the
  record's writing.
- `tests/test_exact_supplement.py`: a robustness world drawn again gives the record's region
  counts, the bodies near a regional border, the region tally, the pooled quadrature, the
  anomalous count and the match against the record.
- `records/exact-2026-10-26/exact.json`: the record; `records/exact-2026-10-26/supplement.json`:
  the supplement; `records/exact-2026-10-26/figures/`.
