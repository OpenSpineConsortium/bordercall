# Recorded runs

Every figure and every slide number is drawn from a run recorded here, never
from a run made on the fly, so that the same command gives the same figure on
any machine and the record of what was drawn travels with the code.

## panjabi-2026-10-26

The junction predictor fitted to Panjabi's published tables alone, with no CT
and no patient data (`python run.py panjabi`). Two runs, differing only in the
measures the profile template scores:

| folder | command |
|---|---|
| `three-measures/` | `python run.py panjabi --measures endplate,h_post,canal_w --outdir records/panjabi-2026-10-26/three-measures` |
| `four-measures/` | `python run.py panjabi --measures endplate,h_post,canal_w,canal_ap --outdir records/panjabi-2026-10-26/four-measures` |

Both took the defaults the command had on that day: 2,000 synthetic columns to
fit the template, 500 evaluation windows per width and per class, per-level
noise of 1.0 mm with a correlation of 0.5 between neighbouring levels, a
per-column scale spread of 0.07, margin 0 and seed 0. A run made after that day
records `seed`, `widths` and `blends` in its own JSON; these two predate that
line and used the defaults above.

The figures are made from a record with

    python run.py panjabi-figures --json records/panjabi-2026-10-26/three-measures/panjabi_junction.json --outdir figures/junction

which writes, for each of the five figures, the PDF, a PNG, the CSV of the
numbers drawn and the caption, and one `FIGURES.md` naming the record, the
code and their hashes. The slides are made from the same record with
`slides/make_junction_slides.py` (README, "The junction from Panjabi's tables").

## neighbour-2026-10-26

The neighbour-identity and dimensionality study of `docs/NEIGHBOUR_IDENTITY_STUDY.md`,
answered in `docs/NEIGHBOUR_IDENTITY_RESULTS.md`: can a vertebra be named from its
neighbours alone, with its own measurements withheld, and does the information fit in
one radiographic plane. Synthetic columns only, run from `bordercall/`:

| file | command |
|---|---|
| `neighbour.json`, `models.json` | `python run.py neighbour --outdir ../records/neighbour-2026-10-26` |
| `enumerate.json` | `python run.py neighbour-enumerate --arm flank --shard 0 --of 1 --out ../records/neighbour-2026-10-26/enumerate-shard0.json`, then `python run.py neighbour-enumerate --gather ../records/neighbour-2026-10-26/enumerate-shard0.json --out ../records/neighbour-2026-10-26/enumerate.json` (the gather deletes the shard file, which carries the time of every fit and the gathered record does not, so the shard was run again afterwards and kept as `enumerate-shard0.json`; do not gather it again) |
| `neighbour_more.json` | `python run.py neighbour-more --outdir ../records/neighbour-2026-10-26` (the series continued on the owner's word of 06:31 UTC: the target measurable, the field named as a whole, a nonlinear classifier, the size of the fit) |
| `figures/` | `python run.py neighbour-figures --json ../records/neighbour-2026-10-26/neighbour.json --enumerate-json ../records/neighbour-2026-10-26/enumerate.json --more-json ../records/neighbour-2026-10-26/neighbour_more.json --outdir ../records/neighbour-2026-10-26/figures` |

The run took the command's defaults: 300 typical columns fitted on (seed 11), 150
columns per phenotype to choose thresholds and the winning subset on (seed 23), 200
columns per phenotype scored (seed 97); rho 0.5, noise 1.0 mm, scale spread 0.07,
blend 0.5, r 0 in the main cells and swept over 0, 0.2, 0.4, 0.6, 0.8, 0.9. The record
carries every setting, and `figures/FIGURES.md` the sha256 of each record and code file.

## identify-2026-10-26

Which vertebrae of a normal spine can be identified best, and by what, framed from Kunkel
2010 (the owner's ask of 2026-10-26 08:21 UTC), answered in `docs/LEVEL_IDENTIFIABILITY_RESULTS.md`.
Typical columns only, run from `bordercall/`:

| file | command |
|---|---|
| `identify.json` | `python run.py identify --outdir ../records/identify-2026-10-26` |
| `figures/` | `python run.py identify-figures --json ../records/identify-2026-10-26/identify.json --outdir ../records/identify-2026-10-26/figures` |

The run (308 s) took the command's defaults: 1,000 typical columns fitted on (seed 11), 500 the
confidence thresholds are chosen on (seed 23), 1,000 scored (seed 97), 10,000 for the
within-level moments (seed 5), 400 redraws of the reference table for its sampling error
(seed 17), 41 Gauss-Hermite nodes for the exact likelihood at one body; rho 0.5, noise
1.0 mm, scale spread 0.07, r 0 in the main cells and swept over 0, 0.4 and 0.8 (and over 0,
0.3, 0.6, 0.9 in the formula). The arm with the table's pedicle rows draws its own columns
with nine measures on the same seeds. The record carries every setting, and
`figures/FIGURES.md` the sha256 of the record and of each code file.

## exact-2026-10-26

Whether any function of 1 to n consecutive bodies' measurements names a vertebra
unambiguously, and what a field can say for certain about one body (the owner's asks of
2026-10-26 10:43 and 11:26 UTC), answered in `docs/EXACT_IDENTIFICATION_RESULTS.md`. Typical
columns only, run from `bordercall/`:

| file | command |
|---|---|
| `exact.json` | `OMP_NUM_THREADS=1 python run.py exact --outdir ../records/exact-2026-10-26` |
| `supplement.json` | `OMP_NUM_THREADS=1 python run.py exact-supplement --outdir ../records/exact-2026-10-26` |
| `figures/` | `python run.py exact-figures --json ../records/exact-2026-10-26/exact.json --outdir ../records/exact-2026-10-26/figures` |
| `slide-figures/` | `python run.py exact-slide-figures --json ../records/exact-2026-10-26/exact.json --outdir ../records/exact-2026-10-26/slide-figures` |
| `slide-figures/cns/` | the same command, which writes the CNS set here (or `--venue cns` for this set alone) |

The run (4,652 s on four processes) took the command's defaults: 2,000 typical columns scored
(seed 97) at every width from 1 to 22, every one of the 127 subsets of the seven measures, 161
Gauss-Hermite nodes; 5,000 columns fitted on (seed 11) and 1,000 for the network's early
stopping (seed 23) for the challengers at 1, 3, 5 and 9 bodies; the robustness worlds from
seed 29 (40 specimen worlds and 40 level worlds of 100 columns, 20 combined worlds, single
draws of 500 columns for each setting set wrong and for the two biases, 400 columns with the
correlation known) and the pilot from seed 5 (16 specimen worlds); rho 0.5, noise 1.0 mm,
scale spread 0.07, r 0. The record is written after each part and is `complete` only at the
end; `figures/FIGURES.md` holds the sha256 of the record and of each code file.

`supplement.json` holds the checks the second review of the results asked for (879 s on four
processes): the region claim split near the two regional borders, under the generator on the
2,000 scoring columns and in the record's specimen, level and combined worlds drawn again from
its seeds; the quadrature on all 2,000 columns; the exact rule on the first 1,000 columns, the
classifier's; and its names at 0.99 on 150 columns each of three anomalous phenotypes (seed 99).
The run's comparison with the record read the record's pooled share of region claims as a
count, so `region_split.matches_record` was computed again from the saved tallies by the
corrected `matches_record` (all 18 cells match); nothing else in the file was touched.

`slide-figures/` holds the seven panels of the five NeurIPS exact-rule slides (the owner's ask of
2026-10-26 20:45 UTC), and `slide-figures/cns/` the six of the results-only CNS slides (no
calibration panel, a step larger type, no method word in a label or a caption). Each panel is drawn
at the exact inches its deck gives it, with its CSV and caption, and each set has one `FIGURES.md`
naming the record and the code by sha256. The posterior panel scores the record's scoring columns
again for the fields centred on T12, refuses to draw unless its shares named exactly, answered at
0.99 and right at 0.99 all match the record's and the record was scored with the generator's own
settings (161 quadrature nodes, the seven measures), and draws the column nearest the median
posterior at one, three and nine bodies together. The decks are built from these panels and the
two records with `python slides/make_exact_slides.py` (into `slides/exact/`; `--pdf` adds a
LibreOffice preview of each, whose equations are pictures and whose bytes carry the time LibreOffice
ran), and the test `tests/test_exact_slides.py` rebuilds both figure sets and both decks byte for
byte, every zip entry of a deck carrying one fixed date.

## whitepaper-2026-10-26

The computations new to the white paper `docs/SCHWINGCHECK_LEVELCHECK.md`, which sets the exact
rule against the labeller whose CT labels LevelCheck transfers and specifies a randomized browser
study of surgeons using either aid (the owner's ask of 2026-10-26 21:18 UTC, reframed on the owner's
comments in the Doc), and the checks its review asked for. Its section on one or two C-arm views
without a CT reads the AP, lateral and both-plane regimes of `exact-2026-10-26/exact.json` directly. Run from `bordercall/`:

| file | command |
|---|---|
| `second_opinion.json` | `python run.py second-opinion --outdir ../records/whitepaper-2026-10-26` |
| `checks.json` | `python run.py whitepaper-checks --outdir ../records/whitepaper-2026-10-26` |
| `study_power.json` | `python run.py study-power --outdir ../records/whitepaper-2026-10-26` |
| `study_power_three_arms.json` | `python run.py study-power-three --outdir ../records/whitepaper-2026-10-26` |

`second_opinion.json` scores the exact study's own 2,000 scoring columns again (seed 97, both
planes, the record's table and settings) at 1, 3, 5 and 9 bodies, and for every field keeps the
posterior the rule gives the true place and each place one level away: the share of each below
0.01 and 0.05 and at or above 0.5, 0.9 and 0.99, overall and, under `by_centre`, for the fields
centred on each level, since the share of off-by-one answers the rule contradicts varies widely by
place. It refuses to write unless the share it names exactly matches `exact-2026-10-26/exact.json`
at every width (76 s). Its `latency` is the median and maximum of 50 single-field calls at three
bodies on the machine that ran it, a four-CPU x86_64 cloud container with Python 3.13.17 and numpy
2.5.3, measured with nothing else running, and does not include reading the measures off an image.

`checks.json` holds two numbers the paper's review found no record held (115 s). Within one level:
the rule that names the likeliest place is the Bayes rule for naming exactly, not for naming within
one level, whose Bayes rule names the centre of the likeliest run of three places; both are scored
on the same 2,000 columns at 1, 3, 5 and 9 bodies, and the file refuses to write unless the first
rule's exact and within-one shares equal `exact.json`'s. The count from C2: the supplement scored
the rule's names at 0.99 on three anomalous phenotypes (seed 99, 150 columns each) against each
column's own names, which call the thirteenth rib-bearing body T13; the study takes as truth each
body's number counted from C2, under which that body is L1. The same columns are scored both ways,
and the file refuses to write unless the own-name counts at 1, 3 and 5 bodies equal
`supplement.json`'s. On six- and four-lumbar columns the two conventions agree.

`study_power.json` simulates the study's analyses (seed 20261026; every cell its own generator
seeded from that and the cell's indices; 10,000 studies per cell for power, 20,000 for size; 120
s). Correctness is logistic with a reader intercept (SD 0.5) and a case intercept (SD 1.0), every
reader reading the same cases, and a reader-by-aid and a case-by-aid term at three settings (none;
0.25 and 0.5; 0.25 and 1.0), each aid's intercept set by Gauss-Hermite quadrature to its stated
accuracy. The primary analysis is the per-reader difference over the two primary strata with a
variance that treats readers and cases as random (the law of total variance, Satterthwaite degrees
of freedom) and critical values calibrated by simulation, because near 95% a nominal t value lets
too many null studies through; the t interval over readers, which treats the cases as fixed, is
recorded beside it. The grid is 20, 30 and 40 readers by 20, 24, 32 and 40 primary cases: nominal
sizes of both analyses at each null setting, the calibrated critical values, and the power of
noninferiority with both aids at 95% and of superiority at 90% against 95%. The strata give one
10-case stratum's two-sided comparison at 20, 30 and 40 readers, at 5% and at 1.25%, the level
Holm's correction across four strata gives the first stratum it tests. `--power-reps` and
`--size-reps` shorten a trial run.

`study_power_three_arms.json` simulates the owner's three-arm design of 2026-10-27 the same way
(the same seed with its own cell keys; 10,000 studies per power cell and 20,000 per size cell; 251
s): every case randomized within reader and stratum to registration alone (A), the rule alone (B)
or the two together (C), a third of each stratum to each, in four strata, and the contrast C minus
A over all the cases. Each aid has its own reader-by-aid and case-by-aid terms, independent between
aids with SDs the setting's over the square root of two, so that any two aids differ as the
two-arm settings say. A contrast uses each reader's cases with its two aids; its case variance
term is over all the cases, since each case is equally likely to fall to each aid, and leaves out
of its estimate a case read with either aid by fewer than two readers. The grid is 20, 30 and 40
readers by 48 and 60 cases, with the power of superiority at 85% against 95% beside 90% against
95%, and one 12-case stratum, 4 per aid, at 20, 30 and 40 readers.

`tests/test_whitepaper.py` recomputes the nine-body second-opinion counts to the bit, by place as
well as overall; checks the power model's draws against the accuracy its quadrature calibrates to,
its allocation and its analysis on a study worked by hand; holds the power record monotone where
more readers or cases can only help; and holds `checks.json` to the exact study and the supplement
wherever they overlap.
