# VerSe Genant join, 2026-10-29

Source: the thread "Extract morphometrics from gold tier 3 CT", 2026-10-29. The join of the
morphometry engine's vertebral body ratios on VerSe's masks against Riedel's Genant grades,
re-done with the screening package (screening/truth.py) so that every number here re-derives
from joined.csv by `python -m screening detect`, and screening/tests/test_truth.py holds it to
the digit, bootstrap included.

## Inputs, each by its SHA-256

- Riedel's table (osf.io/download/zy68u/): 9859a382c65bb23c374db7e269a7e090a928e0f6ea3fe1510f42407e186b5629
- series.json (VerSe series to person): 9ce47932389eee6f51b5c8359c3091575c403a0e20375878169bd9d29e81ce08
- OUT.jsonl (the facts of the VerSe masks): 7278e12b820bab9b7458a631564ec7ca67fd792734aaf6de1203b3f549d94437
- rows.csv (the engine's measures, code stamp 7bda317295ef9f5b, the column-line frame):
  2b3f464c9f8452f801072a0c4ad36a99564b51e90ce5fd7b799e355943c3a571

None of the inputs is in git: the masks and the measures stay on the grid and in the project's
files, as the owner's rule says. The three outputs are here.

## Commands

    python -m screening truth-from-riedel riedel.csv --out truth.csv --persons series.json
    python -m screening join --rows rows.csv --truth truth.csv --facts OUT.jsonl --persons series.json --out joined.csv
    python -m screening detect --joined joined.csv --out aggregates.json

## Outputs

- truth.csv: 13a0670b...
- joined.csv: 079db4a8...
- aggregates.json: 802108d0...

(The full digests are in SHA256SUMS beside this file.)

## What it says

3,720 cells in Riedel's table, 3,696 graded 0 to 3 (23 cells coded 5 and 1 coded 8 are not
grades and are left out), 3,674 vertebrae once one reading per person's level is kept (22
duplicate series dropped, none conflicting), 320 persons with a ratio read, 52 vertebrae with
no reading. The smaller of the two body-height ratios screens a grade 1 or worse fracture with
AUC 0.8362 [0.7800, 0.8871] and grade 2 or worse with 0.843 [0.7804, 0.9018] (2,000 bootstrap
resamples over persons, seed 20261029); against Genant's implied grade the quadratic weighted
kappa is 0.6139 and the exact agreement 0.9326. VerSe is a second arm: it is never pooled with
ENHANCE.PET.
