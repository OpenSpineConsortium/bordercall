# Morphometry: the handoff of 2026-10-29, 17:30 UTC

Source: the thread "Extract morphometrics from gold tier 3 CT", checkpointed on the owner's word
of 17:22 UTC ("push all work and checkpoint and write handoffs now"). Everything below is pushed;
nothing waits in a container.

## Where the work is

- bordercall, branch claude/project-thread-6o9umj, draft PR 30. HEAD carries the morphometry
  engine in the own-axis frame (code stamp 81e732f142d3aa16), the morphobench axis-shift
  command and figures, the screening package and the VerSe Genant record.
- SchwingNet, branch claude/project-thread-6o9umj, a draft pull request of its own: the grid
  word `morphometry <set>` (grid/gate.sh, grid/morphometry.sbatch), the vendor tool that pins
  bordercall's engine under grid/bordercall/ (tools/bordercall_vendor.py), their tests and the
  memory docs/memory/morphometry-on-the-grid.md. Built by a worker and not reviewed by a person.
- The run over the gold tier 3 masks in the own-axis frame (run-axis) is complete: the rows are
  in the project's files under gold3-ct/morphometry/run-axis/ (rows.csv, 16,431,396 bytes, with
  its SHA-256 beside it), never in git. The status page is the artifact 9SiGQnvxDGPsMsRKBqoNtQ,
  last published before run-axis finished.

## The screening package

screening/ generalises SchwingNet's gold tier 3 admission to any CT label set: facts.py reads a
study's masks once into one row in level names (VerSe, ENHANCE.PET and TotalSegmentator
layouts, segmentations/ folders included); whole.py is the mask rule (version 1) and the field
rule (version 3) with the head and foot tables (tables.json, SchwingNet's own); truth.py joins
the engine's ratios to Riedel's VerSe grades; stats.py holds the percentile, AUC, bootstrap and
weighted kappa over plain values; convert.py (written by a worker, its test unrun by me) makes
the int16 label volume a TotalSegmentator folder becomes. Contracts and beartype on every
public function, the one import point screening/contracts.py.

Verified: the facts reader equals holdings.fullspine_facts on real data; the classes and
verdicts equal SchwingNet's on all members (the recorded samples under screening/tests/
fixtures/); the VerSe aggregates re-derive to the digit.

The suite: `PYTHONPATH=. python -m unittest discover -s screening/tests -t .` runs 76 tests.
At the checkpoint one fails: test_whole.RecordedSamplesTest.test_enhance_pet_classes_and_verdicts
on study 1347, an input difference (SchwingNet judged the repaired row, the fixture row is the
raw mask), marked known_difference in the fixture for the keys complete and flags; if it still
fails after that edit, the next key differs for the same reason and takes the same mark. No
other suite of bordercall was run after the last commit.

## What the owner has given

- The count of 15:19 UTC: two CPU jobs, `morphometry enhance` (every ENHANCE.PET label map)
  and `morphometry verse` (VerSe's 374 int16 copies and TotalSegmentator's 154 admitted
  subjects stacked to int16). Nothing has been sent to the grid. Before any send: `update`
  once, then the status word, then the two words, each recorded with its time and Slurm id.
- The hold on grid and WSU data use for the Bayesian work was lifted at 17:05 UTC; each grid
  job still needs his word and its count.

## What is left, in order

1. Merge the SchwingNet pull request once its check is green (the owner's standing permission).
2. Send `update`, the status word, then `morphometry enhance` and `morphometry verse`; record
   each send.
3. Records of the new frame: the comparison at --max-slice 1.25, the axis shift against run229,
   the figures; then the census tables (levels.csv, correlation.csv) for the chain-of-levels
   thread, and the audit of the 106 measures of the clinical reread.
4. The library plan (3D and 2D), every bordercall suite, the adversarial review in PR 30's
   body, mark ready, merge.
5. Answer the auto-anatomist thread (frame stability, the frame beside the rows, the landmarks
   export: the frame export rides in the next stamp change, landmarks after the merge) and
   republish the status artifact.
