# bordercall

Confidential: a pre-filing draft in a private repository. Nothing here goes to a public place before the provisional is filed.

bordercall names vertebral levels from what can be measured on a few bodies in view, with no count from C2 or the sacrum. The core is one exact Bayes rule over Panjabi's published tables (SchwingCheck): it scores every place the bodies could occupy from C3 to L5 and returns the whole posterior. Around it sit the pipeline that turns a scan into measurements, the studies that score the rule, and the auto-anatomist that learns the measurement lines from a CT.

All results so far are on synthetic columns drawn from Panjabi's tables or on phantoms. No patient has been scored yet.

## Where things are

| Folder | What it is | Start with |
|---|---|---|
| [schwingcheck/](schwingcheck/) | The exact rule as a package, and the same rule and generator in PyMC. The checked table of all four Panjabi papers (32 measures with a spread at C3 to L5), the build-up, chain, one-body and fixed-k studies. | [schwingcheck/README.md](schwingcheck/README.md) |
| [scanimport/](scanimport/) | From a scan to a field the rule can name: CT label volumes (VerSe, SPINEPS), CTs with no labels (mask-free mode), radiograph corners, FleXray masks. | [scanimport/README.md](scanimport/README.md) |
| [autoanatomist/](autoanatomist/) | Measurement lines from a CT, learnt from an oracle that reads them off the mask: degradation ladder, soft gates, soft-Viterbi naming, two fused encoders (JAX/Flax). Smoke run only, nothing trained. | [autoanatomist/README.md](autoanatomist/README.md) |
| [coarse/](coarse/) | Coarse claims a field can make when it cannot name its level (below T5, at or above T6, below T12, below L2), each with its clinical reason. | [coarse/README.md](coarse/README.md) |
| [combinations/](combinations/) | Whether combination variables (ratios, products) add anything to naming. Short answer: not under the generator. | [combinations/README.md](combinations/README.md) |
| [holdings/](holdings/) | What gold tier 3 data is held (whole spines C2 to sacrum), the per-volume facts of VerSe, TotalSegmentator and ENHANCE.PET, and the full-spine completion with SPINEPS. | [holdings/gold-tier-3.md](holdings/gold-tier-3.md), [holdings/spineps_run/README.md](holdings/spineps_run/README.md) |
| [records/](records/) | Records of runs since 27 October 2026, one folder per run and date, each with its figures. | the folder names |
| [research_notes/](research_notes/) | Research by topic (see below). | each folder's README |
| [reports/](reports/) | Finished reports. | [Vertebra measures without masks](reports/Vertebra%20measures%20without%20masks.md) |
| [tests/](tests/) | Tests for schwingcheck and autoanatomist; scanimport, coarse, combinations and holdings keep their own `tests/`. | |
| [archive/](archive/) | Everything before 27 October 2026, frozen: the original `bordercall/` package with `exact.py`, old records, docs, decks, the white paper. Reference only; do not run. | [archive/README.md](archive/README.md) (the old README) |
| [TODO.md](TODO.md) | The work queue, in the owner's order, with his decisions of 27 and 28 October. | |

## Headline numbers (synthetic)

From [schwingcheck/README.md](schwingcheck/README.md#the-build-up-study), three bodies in view, 2,000 typical columns:

- The seven SPINEPS-measurable measures name 73.1% of fields exactly; all 32 measures name 98.3%.
- When the rule answers at posterior 0.99, it is right at least 99.59% of the time at every measure count and width scored.
- It weakens when the table is re-estimated from 12 people (as many as Panjabi measured), on spines with an L6 or T13, and on a body drawn half-way between two levels. Those limits are measured in the same README.

## Run it

```sh
python3 -m venv ~/venv-sc
~/venv-sc/bin/pip install -r requirements-schwingcheck.txt        # pinned: PyMC, PyTensor, ArviZ, xarray
~/venv-sc/bin/pip install -r requirements-autoanatomist.txt       # only for autoanatomist: JAX, Flax, optax

~/venv-sc/bin/python -m schwingcheck name schwingcheck/examples/t11-t12-l1.csv   # name one field
~/venv-sc/bin/python -m schwingcheck table check                                 # table matches provenance
~/venv-sc/bin/python -m scanimport name imports/verse/fields/s0001.csv           # name an imported study
~/venv-sc/bin/python -m unittest discover -s tests                               # root tests
```

Each package README lists its own commands and tests (`python -m coarse`, `python -m combinations study`, `python -m autoanatomist.smoke`, `python -m scanimport ingest-ct ...`).

## Research notes

| Note | Topic |
|---|---|
| [paper-tables](research_notes/paper-tables/README.md) | Every measurement table of the papers, as data |
| [clinical-reread](research_notes/clinical-reread/README.md) | Every paper reread for its clinical detail |
| [synthetic-validation](research_notes/synthetic-validation/README.md) | Synthetic spines against published population means |
| [cadaver-power](research_notes/cadaver-power/README.md) | Power: cadavers against CT scans |
| [fullspine-rule6-calibration](research_notes/fullspine-rule6-calibration/README.md) | Calibrating the disc reading of the full-spine completion |
| [panjabi-endplate-inclination](research_notes/panjabi-endplate-inclination.md) | Which printed L1 to L5 inclination rows are original (all 32 measures kept as printed) |
| [Vertebra measures without masks](research_notes/Vertebra%20measures%20without%20masks/) | Sources behind the report of the same name |
| [provisional](research_notes/provisional/README.md) | The provisional patent and the Bayesian work |

## Open pull requests (29 October 2026)

| PR | What |
|---|---|
| #30 | Morphometry on the gold tier 3 masks (vertebrae, discs, column, pelvis) |
| #35 | Census of every measure in hand |
| #37 | Projecting oracle readings and engine lines onto FluXray's detector |
| #38 | Synthetic validation, part 2: every measure of the reread (unfinished) |
| #39 | Clinical reread: second review's fixes, rerun, validated readings (ready) |
| #40 | Auto-anatomist blocks, session and calibration |
| #41 | Main merged into the morphometry branch, for SchwingNet's vendored copy |

## References

Panjabi MM et al. Cervical (Spine 1991;16:861-869), thoracic (Spine 1991;16:888-901), lumbar (Spine 1992;17:299-306) and articular facets (Spine 1993;18:1298-1310) vertebrae: quantitative three-dimensional anatomy. The scanned papers are in [archive/bordercall/reference/papers/](archive/bordercall/reference/papers/); the statistics references are in [schwingcheck/README.md](schwingcheck/README.md) and [archive/README.md](archive/README.md).
