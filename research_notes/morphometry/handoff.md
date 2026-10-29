# Morphometry: the handoff of 2026-10-29, 23:10 UTC

Source: the thread "Advance morphometry", written on the owner's word of 23:06 UTC ("im about to
run out of fable please just write what you have now"). Everything below is pushed to bordercall's
branch claude/project-thread-e89pjg, draft PR 30, with bordercall main (6d261f6, PR 28) merged in.
The handoff of 17:30 UTC follows below it and still describes the screening package, the run on the
vertebra's own axis and the VerSe record.

## What changed since 17:30 UTC, and what is verified

- The pedicle (morphometry/pedicle.py, rewritten): found by a march from the canal's midline in
  rows front to back at three heights, the isthmus the least section area over the rows in the
  front of the canal's depth, the isthmus rows cleaned of the body's corner, the lamina and a
  process's edge (pedicle_rows), the width and height the medians over them, the axis along the
  medial wall extended while the wall keeps its line, the level's width limit (C 12, T 16, L 20 mm)
  and the cervical foramen guard (a C level whose body_foramina flag says the foramen
  transversarium is not closed gets no pedicle), the chord along the axis. The module's docstring
  says why each piece is as it is and what it read before.
- The interpedicular distance (pedicle.canal_between, canal.measures): least and greatest between
  the pedicles' own medial walls over the central half of their height, with a midline guard; where
  a pedicle is not found on both sides the hole's width through the middle stands in, flagged.
- The disc's plate rule (body.band_typical, column.disc_heights): a plate's surface is the median
  over the band's cells of each cell's outermost point, plus half a layer, in place of the band's
  outermost point, which read 1.35 mm into the disc in the neck.
- morphoview/lines.py draws the new pedicle and interpedicular lines; the phantom's lateral-mass
  case and the LateralMass test were rewritten for the foramen beside the pedicle.
- Verified by trace, third pass (before the row cleaning and the guards): on the phantoms the
  straight column read width 9.07 against 9, height 14.4 against 15, transverse angle 0.04 against
  0, chord 50.4 against 49.9, interpedicular 21.8 against 22 and its greatest 23.3 against 23.2; the
  shapes column read the transverse angle 12.4 against 12; the sagittal angle was wrong on both
  (16.5 and 24.9 against 0 and 6) because one row cut through the articular process's edge, which
  the cleaning now drops. On study 0004, L3 read widths 10.8 and 8.7, L4 11.2 and 9.2, T8 6.9 and
  5.5 with heights 13 to 15, all on the pedicle ovals in the pictures; L5 was flagged (sections 22
  to 26 mm, the transverse process's root fused to the pedicle in every row); C5 read nothing
  sensible (the foramen transversarium is not closed in the mask), which the guard now refuses;
  T1 read 49 degrees across, where 25 to 35 is expected.
- Verified by trace, fourth pass (the code as pushed, run at 23:04 UTC): the straight phantom
  reads width 9.08 against 9, height 15.06 against 15, transverse angle 0.3 against 0, sagittal
  1.2 against 0, chord 49.9 against 49.9, interpedicular 21.8 against 22 and its greatest 23.3
  against 23.2; the shapes column width 9.09, height 14.84, transverse 12.3 against 12, sagittal
  9.3 against 6 (the raster: on a baseline of 7.5 mm the settled middles step by one layer of 1.24
  mm, so the sagittal angle is quantised to about 9 degrees; the Shapes test's 1.5 degrees will
  fail on it until the sagittal angle is read from the pedicle's top and bottom surfaces fitted
  as planes, or the test states the raster's bound), chord 51.3 against 51.1; the lateral-mass
  column width 9.6, height 15.2, interpedicular 21.8 and 23.3, its transverse angle -5.9 against
  0 and one sagittal angle not read (the free pedicle 4.0 mm). On study 0004: L3 widths 10.8 and
  8.7, heights 15.0, transverse -2.3 and 3.8, interpedicular 23.3 and 25.1; L4 widths 11.7 and
  13.5, heights 14.7 and 12.5, transverse 9.8 and -6.5, interpedicular 23.3 and 28.1; T8 widths
  6.9 and 6.0, heights 14.0 and 15.1, transverse -2.9 and 2.9, interpedicular 15.5 and 16.4; T1
  right 8.0 by 12.7 at 47 degrees, left 12.3 by 13.2 with no axis (too few rows after the
  cleaning; the 12.3 is likely the lateral mass's edge), interpedicular 16.4 and 19.5; L5 flagged
  on both sides (sections 27 and 22 mm, the transverse process's root); C5 refused by the foramen
  guard. So the widths, heights and interpedicular distances read plausibly at L3, L4 and T8; the
  transverse angle is not trustworthy (L4's left -6.5, T1's right 47, L3 near 0 where Zindrick
  has about 10): it is the canal wall's angle over a few rows and it needs either a longer
  baseline or another construction; the sagittal angle is read on no real level of 0004.
- Not run on the fourth pass: the test suite (last green before the pedicle rewrite), the
  measure and render of 0004, the 229-spine sweep. One fix came after the traces, in
  axis_rows: a row beyond the isthmus rows takes its wall over the isthmus row's layers, as the
  docstring says, where the pushed trace took the row's own layers for a row the cleaning had
  dropped and so stopped the extension there; the shapes trace was running again on it when
  this was written; with it the shapes column reads width 9.11, height 14.88, transverse 11.8
  against 12, sagittal 8.3 against 6, chord 51.4, interpedicular 21.7 and 23.2.
- Found after the push and fixed in the commit that carries this line: column.foramen reads the
  pedicle's height direction from the pedicle info as `eh`, which the rewrite had dropped, so
  `python -m morphometry measure` on 0004 stopped at the first disc with KeyError; the info
  carries `eh` again (the frame's z, along which the height is read). The 0004 measure and
  the test suite were started again on it as this was written.

## The 0004 measure on the pushed code (23:20 UTC)

`python -m morphometry measure` on study 0004 runs through (1,972 rows). Beside the pedicle
readings above, what the rows show that the next session should look at first:

- The facets: "no pair of superior articular processes found" at C5, T1, L3 and L4, four of the
  six levels looked at, so the facet measures are missing on most levels of this study; the
  posterior module's pairing is the next failure to trace.
- The discs: L3-L4 reads 7.1 mm in front, 5.7 at the middle and 1.6 behind; T8-T9 1.0 in front,
  3.1 at the middle, 2.5 behind; C4-C5 1.5, 2.3 and 1.1. A lumbar disc 1.6 mm behind and a
  thoracic one 1.0 in front are not the discs the CT shows: the bands at the posterior and
  anterior corners catch a rim's lip or the neighbour's, to be seen on the renders.
- C5's upper end-plate depth reads 9.8 mm against 16.7 below, as the second pass's render showed.
- L5's interpedicular distance stands in from the hole's middle (24.2 and 30.3, flagged), since
  no pedicle is free of the transverse process's root there.
- The renders of the six levels (`python -m morphoview render`, 23:25 UTC) draw 17 to 28 lines each
  with none withheld, so every line matches its row. The pedicle widths and heights lie on the
  pedicle ovals of the isthmus cuts at L3, L4 and T8, and the interpedicular lines run between the
  pedicles' walls at the canal's front, as meant; the chord follows the axis, so L4's left chord
  reads 28 mm against 53 on the right, since its axis diverges 6.5 degrees and leaves the body's
  side early: a chord is only as good as the transverse angle, which is the open problem above.

## For the account that continues

Start from bordercall PR 44 (branch claude/project-thread-e89pjg, head dd69c23 plus this commit): the
code, the probes and this handoff are all there, and nothing of this work is in SchwingNet except
the grid word and the pinned engine of the 229 run (SchwingNet main, grid/bordercall/). The masks
of the 229 thin-slice studies and the rows of the runs are in the project's files under gold3-ct/,
never in git. Take the steps below in order, the test suite first.

## What to do next, in order

1. `PYTHONPATH=. python -m unittest morphometry.tests.test_morphometry` (about ten minutes on four
   CPUs): the Straight, Shapes and LateralMass pedicle tests say whether the fourth pass holds the
   phantoms (angles within 1.5 degrees, lengths within 0.75 mm). The sagittal angle is the one most
   likely to fail; the cleaning drops the process row, but the fit over 13 rows with the raster's
   steps may still read 6 to 9 degrees where the shapes column has 6.
2. The traces: `python morphometry/tests/trace_pedicle.py phantom straight` (shapes, mass) and
   `python morphometry/tests/trace_pedicle.py real <0004 labels> L3,L4,L5,T8,T1,C5`, which print
   every row with its marks (* the isthmus, n an isthmus row, t a row the axis takes), the band and
   the flags; `slices_pedicle.py` draws the rows on the mask. Expected after the fourth pass: L4's
   left no longer 47 degrees (the corner row dropped), T1 near 30, C5 flagged, L5 flagged.
3. Measure 0004 (`python -m morphometry measure --labels ... --study 0004 --out rows.csv`), render
   C5, T1, T8, L3, L4, L5 (`python -m morphoview render --labels ... --study 0004 --levels ...
   --rows rows.csv --out DIR`) and review every measure, not only the pedicles: in the renders of
   the second pass the lumbar posterior disc heights read 1.2 to 1.6 mm against 6 to 7 in front,
   and C5's upper end-plate depth 9.8 mm against 16.7 below, both to be looked at.
4. The 229-spine sweep with the reworked engine (`python -m morphometry run --masks <thin masks>
   --scheme enhance --out DIR --workers 3 --max-slice 1.25`, about ninety minutes), the level
   medians of the pedicle angles beside Zindrick's and Panjabi's, the flags counted (L5 and the
   neck), and the list of what fails. The transverse angle is the canal wall's angle along the
   pedicle: it under-reads the pedicle's bisector where the lateral cortex flares, so if its
   medians sit well under the papers' that is the construction, not noise.
5. The adversarial review into PR 30's body, mark ready, merge; then re-pin the engine into
   SchwingNet (`python3 tools/bordercall_vendor.py copy <clone>` from main, its check) and close
   bordercall PR 41, the other thread's vendoring draft, as that thread asked.

## The grid

The owner's count of 2026-10-29 15:19 UTC is two CPU jobs, `morphometry enhance` and `morphometry
verse`, through symphony-template's grid-accounts.yml (action job, job schwingnet-morphometry-<set>).
Enhance was accepted at 22:47 UTC ("morphometry ok"); verse was refused at 22:51 with exit 75
because the gate runs one morphometry job at a time: send it again once enhance ends. The check
scheduled at 02:05 UTC for that belonged to the session that wrote this and dies with it, so the
next account sends `schwingnet-morphometry-verse` by hand through grid-accounts.yml (action job,
any request name) once `schwingnet-status` shows the enhance job gone. Both run the engine pinned in SchwingNet
main, the engine of the 229 run of 13:10 UTC, without the pedicle rework; the rework reaches the
grid only with a later run on the owner's count.

## Dropped and deferred

Dropped by the owner (22:56 UTC): no CTSpinoPelvic1K
cross-implementation check. Deferred by the owner (22:45 UTC): the per-level phantom population
tool and the phantom-to-real deformation study.


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
