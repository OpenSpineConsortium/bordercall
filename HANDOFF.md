# bordercall — handoff

Naming a vertebral border from the shape of the bone, with no count from C2. Ported out of
the CTSpinoPelvic1K thoracolumbar experiment (`03_ctspinopelvic1k_dataset/mdpa/`) with the
corpus and the border taken out as parameters, so it can be pointed at the full-spine
segmented census this folder owns.

## Where this stands at the checkpoint of 2026-10-26, 03:10 UTC

Written on the owner's word to push everything and hand off, so that a new account's project
continues from git alone. Nothing needed is held only in a thread, a scratch folder or OneDrive.
The commands further down that name `06_transitional_ct_census` and `03_ctspinopelvic1k_dataset`
are from the spine-program origin; in this repository it is `cd bordercall && python run.py ...`,
and `selftest` takes no argument.

### In this repository

| What | Where | Rebuilt by |
|---|---|---|
| The method and its tests | `bordercall/` (`run.py`, `panjabi.py`, `junction.py`, `junction_figures.py`, `disagree.py`, `synth_corpus.py`, `reference/panjabi_full_spine.csv`) and `tests/` | `cd bordercall && python run.py selftest`; `python -m unittest discover -s tests` from the repository root (37 tests; 36 pass, and `test_junction_figures.JunctionFigures` errors in `setUpClass` on a matplotlib colour fault that is present on `origin/main` independently of any of this work) |
| The recorded runs every figure and slide number is read from | `records/panjabi-2026-10-26/three-measures/panjabi_junction.json` and `four-measures/panjabi_junction.json` | the commands in `records/README.md`; a re-run is a new record beside these, never a replacement |
| The five figures: PDF, PNG, the CSV of the numbers drawn and the caption of each, with `FIGURES.md` naming the record and the code by sha256 | `records/panjabi-2026-10-26/figures/` | `cd bordercall && python run.py panjabi-figures --json ../records/panjabi-2026-10-26/three-measures/panjabi_junction.json --outdir ../figures/junction` (the root `figures/` is ignored by git; the copy under `records/` is the committed one) |
| The six CNS slides, as PowerPoint and as PDF | `slides/junction_slides.pptx`, `slides/junction_slides.pdf` | `python slides/make_junction_slides.py --template <deck> --out out/junction_slides.pptx --figures records/panjabi-2026-10-26/figures`, where `<deck>` is the owner's CNS deck, which spine-program holds at `provisional_patent/wsu_tto/TTO_package_2026-09-25/followup/CNS2026_spine_talk_v10_2026-09-26_CNS_template_ACCME.pptx` (sha256 59497c01f0cadee96a9a6a96489015bfc72be3d366051308c6345426ed72a3f5) and this repository does not |

Pull request #1 (merged as aa31c7a) brought the code, the tests and the records; the pull
request after it brings the figures and the slides, which until then were attached to a thread
and in a `figures/` that git ignored.

### What the slides say, and what they do not

Everything on them is fitted to Panjabi's published tables and scored on synthetic columns drawn
from those tables: no CT, no patient and no SPINEPS mask has been measured yet. The numbers are in
the CSV beside each figure; the headline ones, three measures (end-plate width, posterior height,
canal width):

- A window of eight bodies names the cervicothoracic junction exactly in 85.6% of 250 windows
  and within one level in 98.4% (`junction_width.csv`, row `ct,8`); the thoracolumbar junction is
  the hard one, exact in the sixties and within one in the nineties (row `tl,8`).
- By class, 500 windows each (`junction_twins.csv`, `phenotype` rows): C7/T1 exact in 85.2% of
  every class; T12/L1 exact in 59.4% (six lumbar) to 65.2% (four lumbar).
- A lumbosacral twin, the same column with the lumbosacral levels added or taken away, changes
  the call in 0.4% (four lumbar) and 0.8% (six lumbar) of 500 at either junction (`twin` rows):
  the anomaly at L5/S1 leaves the two junctions where they were, which is what the owner asked
  the predictor to be robust to.
- At a thirteenth thoracic body the count and the ribs name the junction one level apart and the
  shape cannot choose; `junction_blend.csv` scores both truths side by side. That is the TLTV
  case the owner named as the hard one, and it is not solved here.

### Not done, in the order to take it

1. The grid pilot. The owner approved two CPU jobs on 2026-10-25 at 23:56 UTC ("Two CPU jobs:
   pilot, then full"); none has been sent. The route is in place: SchwingNet #404 (merged) gives
   `grid/gate.sh` the word `bordercall <pilot|full>`, `grid/bordercall.sbatch`,
   `tools/bordercall_corpus.py` (the count from C2 over the census's existing SPINEPS masks, the
   ribs from the census's rib table) and `grid/bordercall/`, this repository vendored at 6938a2e;
   symphony-template #495 (merged 03:08 UTC) gives grid-accounts.yml the dispatch word
   `schwingnet-bordercall-<stage>`; hpcworker #50 (the gate's pass-through) had its review
   section added at 03:04 UTC and its check re-run, and is merged next. Then, each on a dispatch
   of symphony-template's grid-accounts.yml, action `job`: `update`; `schwingnet-status` once
   (last sent 2026-10-25 23:41 UTC; never twice for one read); `schwingnet-bordercall-pilot`;
   read its report; `schwingnet-bordercall-full` only if the report says countable > 0 and the
   pilot ended well. A third job needs the owner's word and count again.
2. What the pilot answers that nothing here does: the published T12/L1 answer against a count
   from C2 on real masks; the per-class tables with denominators; the rib arm beside the circular
   arm (`disagree`); the `sweep` winner with its typical-versus-worst gap.
3. The owner's rules from this thread, which stand: only full-spine C2-to-pelvis CTs are truth
   (00:16 UTC), nothing from the 802 CTSpinoPelvic1K columns; existing SPINEPS masks, never
   re-run and never TotalSegmentator (00:17 UTC); figures in Benzel's style with the code that
   makes them committed and runnable from recorded inputs (01:17 UTC); the OneDrive upload is
   stopped (02:48 UTC; `junction_twins.pdf` is the one verified copy in Documents/bordercall_figures
   and stays); the public deck: count-free naming from morphometry sat near Part A of the
   provisional and was left out of v12_public, so check with the TTO before showing these slides.
4. Not known: traps 1 and 2 below (the identifier map is assumed; only the lumbar measurements
   are validated); every number above is synthetic until the pilot reports.
5. SchwingNet's vendored copy takes `bordercall/` only, so this commit (records, figures, slides)
   leaves its VENDORED record true; after any change under `bordercall/` run
   `python3 tools/bordercall_vendor.py copy` there and commit the copy with the change.

## Run this first

```bash
cd 06_transitional_ct_census/code/bordercall
python run.py selftest --levels ../../../03_ctspinopelvic1k_dataset/mdpa/morphometrics/level_gradients.csv
```

It must print **selftest passed**. It re-derives the three published CTSpinoPelvic1K numbers
(adjacent-pair AUC 0.988, whole-span 0.998, junction placement 95.1%) from the released table
and fails if any has moved by more than 0.004. If it fails, the model or the features have
changed and nothing this copy produces is comparable with the published work. Fix that before
measuring anything new.

## Then, on your corpus

```bash
# 1. label volumes -> one wide row per case
python run.py measure --labels /path/to/labels --out levels.csv

# 2. ask whether shape carries a border
python run.py border --levels levels.csv --above T12 --below L1
python run.py border --levels levels.csv --above C7  --below T1
python run.py border --levels levels.csv --above L5  --below L6
```

`measure` writes the full spine by default. Narrow it when you only want part:

```bash
BORDERCALL_LEVELS=T11,T12,L1,L2,L3,L4,L5 python run.py measure --labels ... --out ...
```

## The five traps, in the order they will bite

**1. The identifier map is assumed, not detected.** `measure_levels.py` carries
`VERSE_NAMES`: 1–7 are C1–C7, 8–19 are T1–T12, 20–25 are L1–L6, 28 is T13. If your corpus
numbers its vertebrae any other way, every measurement will come out of the wrong bone and
nothing will raise — this programme has already shipped a release where pelvic incidence was
computed against the wrong map and the only symptom was a quality flag about a structure that
was plainly there. **Before the first measure run, print the identifiers actually present in
three volumes and check them against `VERSE_NAMES` by eye.** CTSpinoPelvic1K's own rule is to
resolve names with `ostk.labels.labels_for(volume)` rather than import a fixed map; if `ostk`
is available on your corpus, use it and make `VERSE_NAMES` follow it.

**2. Only the lumbar measurements are validated.** End-plate width, canal width and
transverse-process span were checked against published lumbar norms. The original file says
in as many words that those comparisons *do not transfer to thoracic levels*; only the height
and wedge columns are meant to be used above L1. Widening the identifier range makes the code
run over a whole spine. It does not make the numbers validated there. The first real piece of
work on a full-spine corpus is to check each measure at the cervical and thoracic levels
against a published series, the same way the lumbar ones were checked. Until then, treat a
cervical or upper-thoracic border result as a pipeline test, not a finding.

**3. The normalisation is the whole method.** Every measure is divided by that case's own
median across its measured levels, and ratios between measures carry no size at all. Lumbar
vertebrae are simply bigger than thoracic ones; a classifier given raw millimetres learns size
and reports a high AUC that says nothing about the border, where the two neighbours are nearly
the same size. If you change the feature builder, keep the normalisation or the numbers stop
meaning what they say.

**4. Folds are grouped by case.** Two vertebrae from one patient are not independent
observations. A random split leaks and inflates everything. `out_of_fold()` groups by case;
keep it that way, and keep any new split grouped too.

**5. Every synthetic accuracy is an upper bound, and the default hides it.** The generator
draws each measure's departure from its published mean independently. Real vertebrae do not
work that way — a wide body tends to come with a deep one — so independence hands the
classifier more information than it would have. No published source gives the within-patient
correlation; `run.py covariance` shows why, including the one paper that looks like the
answer and is not (Kunkel 2010 regresses parameter on parameter, which is the right shape,
but over sixteen *level means* rather than over individuals — reading a within-patient
correlation from it is the ecological fallacy). So pass `--r-between` and sweep it rather
than quoting the default. On the measure-set question the sweep settles it: the verdict is
unchanged across r = 0.0 to 0.9, moving by at most 1.6 Monte Carlo standard errors. **Do
that sweep for any new synthetic claim before quoting it.** `r_between=0` reproduces the
recorded runs exactly, which is what the tests check.

## What one evaluation costs, and where enumeration stops being free

Measured on a Windows workstation, 2026-10-26. One evaluation of `A(S, r)` -- train the junction
model on 600 synthetic columns, then score six phenotypes at 400 windows each -- is **7.24 s**
(2.40 s train, 4.84 s evaluate, `n = 2400`, 7 measures). Reproduce with `J.train` followed by
`J.evaluate` over `P.PHENOTYPES`, which is exactly what `covariance._score()` calls.

That number decides how this problem should be attacked, so it is recorded rather than guessed
at. Enumerating every subset, scored at both junctions:

| measures `m` | subsets | cost |
|---|---|---|
| 7 | 127 | **0.5 h** -- free |
| 9 | 511 | 2.1 h -- free overnight |
| 12 | 4,095 | 16.5 h -- one night |
| 17 | 131,071 | **22 days** -- not enumerable |

So **at the 7 measures in use there is no optimization problem**: enumerate, which is exact by
construction and returns the whole ranked distribution instead of an argmax. Above roughly
`m = 12` the binding constraint becomes simulator throughput, and the thing to reach for is a
replication-budget rule -- `sim-tools` 1.3.0 (MIT, PyPI 2026-06-24) ships OCBA, OCBA-m, KN and
KN++, with the caveat that every commit touching its `ovs` module since 2021-07-05 is
formatting and the module has no tests, so pin the commit and write your own.

The closed-form separability of the published Gaussians runs about 290,000 times faster than
this, and it is **a different function, not a cheap version of this one**. Use it to rank and
screen; report the final accuracy from the simulator on held-out draws. Never quote the two
interchangeably.

## Ground truth means a count from C2, and this corpus has none

Measured on all 802 CTSpinoPelvic1K volumes, 2026-10-25: **0 are countable.** The most
cranial labelled vertebra is T6 in the best case and T8 in the commonest (T8 210, T7 182,
T9 141, T6 121, T10 74, T11 33). It is abdominopelvic CT; C2 is never in the field.

So every number this method reports on that dataset is against the **labels**, which are a
reader's call at the border, and not against a verified count. `phenotype` records
`countable` per case and `sweep` refuses a corpus with none, which was exercised against this
very corpus rather than only against a synthetic case. Use a whole-spine corpus for any claim
about which border is named most robustly.

## What the method already found, so you know what to expect

On CTSpinoPelvic1K (802 abdominopelvic CT, 713 with the border in view):

| | |
|---|---|
| Junction placed at the labelled T12/L1 interspace | 95.0% |
| Typical column | 97.3% (n=656) |
| **Rib on a lumbar body (L1)** | **28.6% (n=14)** |
| **No rib on T12** | **50.0% (n=10)** |
| Six lumbar (L6) | 88.9% (n=18) |
| Four lumbar identifiers | 100% (n=10) |

The corpus average hides the result. Only the two *thoracolumbar* phenotypes break it; the
lumbosacral ones sit at or near the typical column, which is what a thoracolumbar classifier
should do. Expect the same shape of answer at any border: the classes that break it are the
ones whose anomaly is *at that border*.

Every failure runs in the direction the ribs do. A vertebra carrying a rib is called thoracic,
one without is called lumbar; of the 14 spines whose lowest rib-bearing vertebra is L1, ten are
called one level caudal and in every one the vertebra called thoracic is that rib-bearing L1.
Against the rib criterion: sensitivity 62.5%, specificity 97.0%, precision 41.7%.

## The mislabel question, and the trap inside it

Asked and answered in `03_.../mdpa/scripts/test_relabel_hypothesis.py`: if the border vertebra
is misnamed (no C2 to count from), the "failures" are the reader's and relabelling should fit
better. Three arms, each retrained from scratch:

| Labels | Whole span | T12/L1 pair |
|---|---|---|
| reader, as released | 0.9981 | 0.9880 |
| **rib-defined border** | **0.9986** | **0.9916** |
| model's own call (circular) | 1.0000 | 0.9998 |

**Relabelling to the model's own prediction always improves the score** — the target has been
moved to where the model already points. That arm is in there as the control that shows what a
circular improvement looks like, not as a result. The honest arm moves the border using the
*ribs*, which are not among the features, and it recovers about a third of the circular arm's
gain. So: partly yes, the poorly-performing cases are mislabelled relative to rib anatomy, and
most of the remaining disagreement is not explained that way.

What none of this settles: a rib on L1 could be a thirteenth thoracic vertebra above five
lumbar ones, or a rudimentary rib on a true L1. Those are different columns with the same rib
and only a count from C2 separates them. If your corpus is whole-spine and *does* contain C2,
you can settle it — that is the single biggest thing this corpus can do that CTSpinoPelvic1K
could not.

## Where to start on the census

1. Run `selftest`. Then check the identifier map on three volumes by eye (trap 1).
2. `measure` a few hundred cases first, not the whole corpus; confirm the measures look
   sane at the levels you care about before spending the compute.
3. Run `border` at T12/L1 first, because that is the one with a published answer to compare
   against. A wildly different number means the pipeline, not the anatomy.
4. Only then move to borders with no published answer (C7/T1, L5/S1).
5. Because the corpus has C2, add the true count as a column and ask the question
   CTSpinoPelvic1K could not: of the cases where shape and name disagree, how many are
   *counted* anomalies? That is `disagree`, which also runs the rib arm and the circular arm
   beside it. SchwingNet's `grid/bordercall.sbatch` runs steps 1 to 5 over the census's
   existing SPINEPS masks, counted from C2 by `tools/bordercall_corpus.py` there, a pilot of a
   few hundred countable cases first.

## Files

| File | What it is |
|---|---|
| `run.py` | CLI: `scheme`, `selftest`, `measure`, `phenotype`, `border`, `breakout`, `sweep`, `plot`, `disagree`, `panjabi`, `panjabi-corpus`, `panjabi-figures`, `synth-corpus`, `covariance`, `all` |
| `covariance.py` | the between-measure correlation: what the literature does and does not supply, the exchangeable draw that puts it into the generator, and the sweep showing the measure-set conclusion survives the whole range of it |
| `disagree.py` | step 5 below as a command: the count, the ribs and the circular arm, with denominators |
| `panjabi.py`, `junction.py` | the junction named from Panjabi's tables with no CT; the owner's junction predictor for the CNS slides, robust to lumbosacral anomalies by construction; at a TLTV the count and the ribs name the junction one level apart and the shape cannot choose (README, `panjabi`) |
| `junction_figures.py`, `records/`, `slides/make_junction_slides.py` | the five figures from a recorded `panjabi` run (textbook line figures, each with its CSV, caption and `FIGURES.md`), the recorded runs, and the six CNS slides built from them on the deck's own template |
| `synth_corpus.py` | a made-up corpus in SchwingNet's grid layout, so the commands run anywhere; nothing from it is a finding |
| `border.py` | corpus loading, shape features, grouped-CV logistic regression, border evaluation. No corpus-specific knowledge |
| `measure_levels.py` | label volumes -> wide per-level table. CTSpinoPelvic1K's `extract_level_gradients.py` with `LEVELS` widened to the full spine; everything else unchanged |
| `_separability_reference.py` | the original thoracolumbar experiment, kept verbatim as the thing `selftest` is checking against |

Dependencies: numpy, scipy, nibabel. No sklearn — the model is a logistic regression written
out, because the question is whether the shape carries the border at all, and a black box would
answer it less usefully.
