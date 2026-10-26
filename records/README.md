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
