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
