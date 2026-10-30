# Morphometry: the handoff of 2026-10-30, 20:30 UTC: the lines carried onto FleXray's X-rays, and curved shapes

Source: the thread "Run morphometry on gold tier 3 masks" in the claude.ai project symphony_5, on
the owner's words of 16:49 UTC ("make sure these lines can be projected from 3D to 2D natively,
surviving a conversion by flexray to a fluroscopic xray, further, there should be basic
functioanlity for non-linear arcs/curves/planes/volumes/ect") and of 20:06 UTC ("Please write a
handoff and checkpoint so another account can continue this work at this point do not more
checking just push and write everything"). So this entry was written and pushed with no review
and no mutant run, on that word. This pass read no real mask or CT and queued no grid job; the
owner's hold of 14:45 UTC on the jobs stands (no grid sends, no report reading, no plots until
the owner says the resynthesis is done). SchwingNet's side of the same stop is its checkpoint
docs/checkpoints/2026-10-30-morphometry-lines/README.md, on its branch
claude/project-thread-gv744i.

## What was built

The research note's section "Carrying the lines onto FleXray's X-rays" says what each part does
and what holds it; in brief:

- morphoview/projection.py copies FleXray 1.0.2's camera on nanoDRR 0.1.5 (the pose, the
  intrinsics, one ray a pixel to its centre, row by row), the crop SchwingNet renders, and
  FleXray's canvas from its model's preprocessing.json (256, padded to a square); CHECKED names
  the two releases, and a render of another FleXray is projected with a warning.
- `python -m morphoview project` (morphoview/__main__.py) carries lines.csv and frames.csv onto a
  render in three forms: SchwingNet's render manifest, a render of its realism programme
  (`--realism RENDER --sample ID --ct CT`, whose records name no camera, read from manifest.jsonl
  and recipe.json), or a view file. With `--edits` and `--filter` it lists each fluoroscopic
  edit of a realism render: whether it holds the render's pixels, how far it moved the render's
  picture (edit_shift, the phase correlation's peak by magnitude, refined by Foroosh's ratio, to
  0.01 px on known shifts) on the render and on FleXray's canvas, and whether FluXray's filter
  kept it.
- FleXray's labels at both thresholds a request names are recorded and told apart: 0.0, the
  training profile's, the support, which our shadows equal pixel for pixel in all nine views and
  levels; and 0.5, a bare request's, at which SchwingNet's realism programme renders its truth
  masks, which drops bone thinner than about 8.7 mm along the ray. Landings are measured on the
  shadow, never the mask.
- morphoview/shapes.py: curves (open or closed, cut at the source's plane), arcs, circles,
  ellipses and centripetal splines sampled to 0.05 mm, planes fitted by least squares with
  patches and angles, flat polygons, volumes with their path lengths and silhouettes, and
  surfaces: triangles through a grid, a height over a plane refined to 0.05 mm, Delaunay
  through scattered points, and the least-squares quadric through points, with each surface's
  area, rims and sag (a concave end-plate's dip below its rim). A surface's shadow is the pixel
  centres inside its projected triangles; one reaching behind the source is refused.
- tests/flexray_record.py recorded tests/fixtures/flexray.json from FleXray 1.0.2 itself on the
  straight L2 to L4 phantom (now with its placed frames, flexray_record.placed);
  tests/test_projection.py holds the copy to it, and its class Shapes draws an ellipse, an arc,
  a closed spline, a patch's outline, a dome and a cap inside the phantom's bodies and finds
  every one on FleXray's support of its body; tests/test_shapes.py holds every shape to its
  geometry on the render, under a cone beam and parallel rays.

## What is verified, and what is not

- Verified: the three modules' 94 tests pass in the plain environment, 3 skipped where FleXray
  and torch are absent, in 82 s (`python -m unittest morphoview.tests.test_projection
  morphoview.tests.test_shapes morphoview.tests.test_lines`), run once on this commit's code
  before it was copied here.
- Not run on this commit: Live, test_projection's class that renders the record's views again
  with FleXray 1.0.2 and torch (both thresholds, the crop and two fresh views of beads); it last
  passed before the shapes, the surfaces and the edits' shift were added.
- Not run at all: mutants over projection.py, shapes.py and the project command's new paths
  (the earlier harness lived in the container and is gone); an adversarial review of this diff.
- morphometry's own suite was not run again; nothing under morphometry/ changed, and
  flexray_record.placed only reads its phantom's placed frames.
- Found after the push: bordercall's main moved to a87e0b3 and now holds
  autoanatomist/project.py (e751cbc, another thread's), which projects readings and lines onto
  FluXray's detector under nanoDRR 0.1.7's convention, read from its source, with FluXray's 90
  poses; morphoview/projection.py copies FleXray 1.0.2 on nanoDRR 0.1.5 and is held to renders
  FleXray itself made. Which nanoDRR SchwingNet's renders run on, and whether the two
  conventions agree, is not checked, and flexray_check warns on another FleXray, not on another
  nanoDRR. The two are to become one camera, held to one record, before either is trusted on a
  render. This branch merges with that main without a conflict (git merge-tree).

## What is left, in order

1. In a container with FleXray 1.0.2 and torch (the environment the record was made in), run
   test_projection with Live and the three modules again; fix what fails.
2. Mutants: a one-token change at a time to projection.py, shapes.py (above all mark_inside's
   slack and sides, refined_grid's stopping rule, Surface.rims, Surface.fit's rank test) and
   __main__.py's edit_shift, realism_view and edits_of; each must fail a test, and a survivor
   gets a test.
3. An adversarial review of this pull request's diff, by correctness, by fitness for PR 45's
   stage 1, and by the tests and the words, written into the pull request's body as its
   "Adversarial review" section; fix what holds up.
4. Merge this pull request once 1 to 3 are done. Then SchwingNet's task (its checkpoint above):
   re-vendor bordercall at the merged commit with morphoview (projection.py, shapes.py and the
   lines), pass --lines in grid/morphometry.sbatch, and the rest that the 17:10 UTC entry below
   lists under "What SchwingNet needs before the counted jobs".
5. Only on the owner's word after the resynthesis: the counted jobs, enhance, verse and the
   covariates join, one at a time, with plots of the old engine against the new.

# Morphometry: the handoff of 2026-10-30, 17:10 UTC: the lines export, reviewed

Source: the thread "Run morphometry on gold tier 3 masks" in the claude.ai project symphony_5, on
the owner's word of 14:28 UTC ("yes do all these": merge PR 44, re-pin the engine in SchwingNet,
give a count) read with the other thread's note of 14:34 UTC, which asked that PR 45's stage 1
export ride in the morphometry jobs. This pass read no real mask or CT and queued no grid job; at
14:45 UTC the owner held the jobs until a resynthesis.

## What the export is

- `python -m morphometry run --lines` writes, per study, lines/ID.csv and frames/ID.csv beside
  rows/ID.csv and joins them as lines.csv and frames.csv; the research note says what each row
  holds. The lines are morphoview.lines' builders run on the vertebrae measure_volume built (its
  new `keep`) and checked against the values it wrote: 25 keys a vertebra (VERTEBRA_KEYS), 3 a
  disc (DISC_KEYS), each end named (ENDS). The lines and frames are written before the rows, which
  stay the commit marker, and a run with the lines has a stamp of its own, over
  morphoview/lines.py too.
- morphoview.lines.pedicles takes the measure's own reading of each side (side_reading), since
  reading pedicle.one_side again took five sixths of a study's drawing on the phantoms (3.5 of
  4.2 s of CPU on L2 to L4 at 0.8 by 0.8 by 1 mm); on a vertebra the volume's edge cuts, whose
  values the measure blanks, it reads the side again.

## The review, and what was done

Four reviewers read commit 4086684 by correctness, robustness on the grid, fitness for PR 45's
stage 1, and the tests and the words; two skeptics tried the first finding and could not refute
it. Fixed:

- Three of Panjabi's seven chords, the posterior height at the wall and the canal's width and
  depth at the pedicles (h_post, canal_w, canal_ap), had no line, though PR 45's minimal shape
  model is fitted on all seven. morphoview.lines draws them (panjabi_height, panjabi_canal); each
  is a median, drawn in the cell or section nearest it, with the median as its value.
- The words promised a line for every measure; they name the keys that have one.
- Ends, values and frames were written to four places, so a frame read back was orthonormal only
  to 1e-4 and failed the oracle interface's check at 1e-6; they are written whole.
- The ends were unnamed and their order was set builder by builder; each is named (a_end, b_end).
- A frame did not say which axis its z lies along; frames.csv adds axis and the column's line.
- The frame tests passed with the origin at zero, x and y reversed, the frame turned 5 degrees or
  left on the column's line. Frames now takes every line's ends into its frame on a chain whose
  joints open, tilt, turn and slip, and holds the origin to the main piece's centroid and each end
  to the side its name says.
- One failing builder dropped every line of its level; each has its own guard, and the flag names
  it.
- After a run a dead worker cut short, the joins mixed files an older code wrote with the run's;
  they take only the studies whose rows carry the run's stamp, and are written to a part file and
  moved into place.
- No test held the write order or the reset after a failed measuring; Failing kills a study at
  each of its three writes, and fails one after its vertebrae are kept.

Each test the fixes added fails with its fix taken out, or with a slip a later change could make: 28
mutants of the export and its tests, all caught. The first round's 14 caught 13; the one that lived,
the canal's depth read on the wrong section, led to the test that holds each median's line to the
cell or section nearest it. The 13 were run again on the final tree, and the second round's 15 were
caught too, the two that move an end's name run again once the end-name test read every pair either
way round, so a wrong name fails on the geometry and not on a missing key.

Left, with the reason:

- A run whose pool breaks exits 0 and prints "a worker died ... run again", as every run has, with
  the lines or without; SchwingNet's report is to read that line from the run's log.
- A key with no line leaves no line row; VERTEBRA_KEYS and DISC_KEYS give the denominator.
- The oracle's frame and the one found without the mask, which PR 45's stage 1 compares with the
  engine's, need the CT and autoanatomist, which the job has not; they are a step of their own.

## What SchwingNet needs before the counted jobs

None of this is done in bordercall:

- vendor the merged commit with morphoview/__init__.py and morphoview/lines.py
  (tools/bordercall_vendor.py's ENGINE), since `run --lines` imports morphoview before it
  measures;
- pass --lines in grid/morphometry.sbatch's measure() and print code_stamp(True) in the report;
- digest lines.csv and frames.csv, and count flag:lines and the lines per level by status, as
  aggregates only;
- read "a worker died" from the run's log into the report;
- refuse the word where grid/bordercall/morphoview/lines.py is missing;
- then the owner's count of three, enhance, verse and the covariates join, one at a time, which
  the owner held at 14:45 UTC until a resynthesis.

## Tests and timing

- morphometry/tests/test_lines_export.py, 25 tests on phantoms of L2 to L4: straight at 0.8
  by 0.8 by 1 mm, the same cut through L4's body by the volume's edge, the same on 2.5 mm slices,
  and a chain whose joints open 8 degrees, tilt 4, turn 5 and slip 4 mm. The engine's suite,
  75 tests, passes: test_morphometry's 39 in 769 s and the export's and morphoview's 36 in 229 s,
  on four CPUs shared with the mutant runs.
- On three phantom columns on one worker the drawing adds 9 per cent to the measuring of L1 to L5,
  13 to that of C2 to C7 and 13 to that of a column from C2 to L5, and nothing to the peak memory.

# Morphometry: the handoff of 2026-10-30, 14:00 UTC

Source: the thread "Run morphometry on gold tier 3 masks" in the claude.ai project symphony_5, on
the owner's "continue" of 01:15 UTC: item 1 of the list of 01:45 UTC below, the posterior wall's
reading reworked on bordercall's branch claude/project-thread-e89pjg (draft PR 44), then put
through an adversarial review and the findings fixed. The rework, the fixes and the wall's probe
are in the commit that adds this section. This pass queued no grid job, and its code read no real
mask or CT: every figure of the wall's is from phantoms. The verse run on the grid, sent at 08:25
UTC on the engine pinned before this pass, is in its own section below.

## What changed

- body.posterior_wall reads the wall's slope on the scan's own lattice from the vertebra's whole
  label: the last bone of each scan line in a band across the midline, a trimmed and reweighted
  fit of the surface y = a + b z + c x + d x^2, and the slope clamped into the range of slopes whose
  surfaces part the label's bone from its air. Its docstring says how, with every figure below;
  pedicle.wall_reading and posterior.spinous_angle take the same reading, and where it is not read
  the end-plates' inclinations, the pedicles' sagittal angles and the spinous angle are not either,
  each flagged.
- The review's fixes: the wall is refused where more than 40 per cent of the band's edges lie over
  a step off the fit (WALL_DROPPED_SHARE), since a notch 8 mm wide, 6 tall and 5 deep read 29.2 and
  29.5 degrees off with no flag; at C2 the window ends at the top of the canal's full rings, since
  the dens put the reading up to 8.4 degrees off; whether the label parts is asked of a
  widest-margin program first, since HiGHS's status 4 on the range's programs had been read as an
  unbounded end (two of the 294 speck labels on 1 mm slices drew it, one of them refused for a
  freedom of 180 degrees);
  the clamp sets aside the one to three edges the fit leaves furthest across before it gives up, so
  one speck of bone behind the wall no longer turns it off; the flag on a free wall says the angles
  may be off by up to the freedom where the label parts, and that the freedom bounds nothing where it
  does not; the words on the band (a half-width), the window, the gate and the canal line's two
  causes (the staircase and a notch) are corrected in body.py, column.py, anatomy.py, pedicle.py and
  the research note.
- phantom.py draws a notch off mid-height (Vert.notch_z), a dens (Vert.dens_r and its kin) and
  cervical-sized vertebrae (phantom.cervical, about a C5, the review's sizes, from no published
  table). The tests add the clamp and the specks (LeanedWall), the notch drawn 4 mm below
  mid-height, where a plain least-squares fit reads the wall 7.0 degrees off (BasivertebralNotch),
  the speck that drew status 4 (SpeckOnTheMargin), the deep notch's refusal through measure_volume
  (DeepNotch), the free wall's flag (FreeWall) and C2 with its dens (DensAtC2).

## The phantom cache the wall's figures come from

The figures in body.posterior_wall's docstring, its constants' comments and the research note
were measured over a cache of phantom vertebrae. The cache and its score are kept as
morphometry/tests/probe_wall.py (`build <dir>`, then `score <dir>`); the alterations, the specks and
the probes were scratch scripts of this pass and are not kept, so they are described here closely
enough to be written again:

- The cache (probe_wall.py build): L2 to L4 drawn and L3 built as measure_volume builds it, for four
  phantoms and their walls' leans: straight (upright, leaned 5 degrees forward and 5 back), pitched
  (ped_s 10, upright), shapes (Ha 30, concavity 2, waist 0.92, ped_t 12, ped_s 6, facet 55, sp_angle
  32; upright and leaned 4 forward) and pitched down (ped_s -8, ped_t 8, upright); on seven grids,
  each the column's tilt and the grid's turn about z: aligned, 2, 5 and 10 degrees about x, 18
  about (1, 0.3, 0) turned 7 (the suite's), 25 about (1, 0.3, 0) turned 15, and 12 about (0.3, 1,
  0) turned 4; at 0.8 by 0.8 by 1 mm and 0.86 by 0.86 by 2.5 mm. That is 49 vertebrae a thickness,
  98 in all. The lean is phantom.Vert.lean, the body's inside test sheared y less z tan(lean).
- The score (probe_wall.py score): the wall's slope against the true lean taken into the frame the vertebra
  was read in, and downstream the pedicles' sagittal angle, the end-plates' inclinations and the
  spinous angle against their truths.
- The alterations, twelve that keep the wall's slope, each drawn about the true wall:
  notches 6 mm wide, 4 tall and 2 deep at mid-height and half-way to the window's top, and 5 by 6 by
  4 at mid-height; a lip 1.5 mm proud, 16 mm across, from 3 mm inside the window's top up; an
  osteophyte 3 mm proud at the upper end-plate, outside the window; an axial scallop 1 mm deep at the
  midline, a cosine squared across 16 mm; a sagittal bow 0.8 mm deep at mid-height; six holes of 1 mm
  radius 0.8 to 3 mm inside the wall; a segmenter's ragged edge, a smooth random field of 0.3 mm
  over 3 mm and of 0.5 mm over 4 mm, whose own lean over a band 6 mm either side is reported beside
  it; the wall's boundary voxels flipped at random, one in five; and the volume's last slice 30 per
  cent of the body's height below its top.
- The specks: one voxel of the label, not of the body, a step behind one of six edges
  spread up the window near the midline, each in turn on each vertebra: 294 labels a thickness.
- The probes: the notches of several sizes on the suite's grid and on the grid tilted 2 degrees,
  the cervical C5 at leans of 0 and 5 either way with its pedicles 2 mm up or down, C2 with dens of
  several shapes, and the canal line against the true wall over the cache.

## What is verified, and what is not

- The suite: `PYTHONPATH=. python -m unittest morphometry.tests.test_morphometry`, 39 tests, all
  pass (428 s on four CPUs); `python -m unittest morphoview.tests.test_lines`, 10 tests, all pass.
- score.py over the cache with body.posterior_wall as it stands: 49 of 49 read on each thickness,
  within 0.35 degrees on 1 mm slices and 0.79 on 2.5 mm (medians 0.07 and 0.19), where the
  hindmost-voxel reading erred up to 4.14 and 5.66; `python -m morphometry bench --slice 2.5` gives
  the research note's table unchanged.
- Each new test fails with its fix undone (the scratch script bite.py): a plain least-squares fit
  (BasivertebralNotch, the wall refused for the 51 per cent it leaves off), the clamp left out
  (LeanedWall's clamp and specks tests), no bound at C2 (DensAtC2, 8.08 degrees off), no set-aside
  (LeanedWall's specks test, the label no longer parting), no dropped-share rule (DeepNotch, no
  refusal) and wall_slope_range as it stood (SpeckOnTheMargin, free over 180 degrees and refused;
  the other wall tests pass there, since only that speck draws status 4). The status depends on
  HiGHS's tolerances, here scipy 1.18.1.

- What the fixes leave: the band on a cervical body is the whole 6 mm either side, 12 of the
  phantom's 17 mm, and the wall read within 1.47 degrees on 1 mm slices and 1.32 on 2.5 mm there; a
  band of a quarter of the body's width read within 0.92 and 1.72 and was not taken. The gate is
  still centred on the canal's line, which a notch leans (18.7 degrees through the 5 by 6 by 4 mm
  notch at mid-height); re-centring it on the first fit hid the dropped share and let the deep notch
  read 29.7 degrees off on 2.5 mm slices on the grid tilted 2 degrees, so the share's refusal stands
  behind it instead. The share refuses some sound walls: the 5 by 10 by 4 mm notch on three of the
  four grids and thicknesses probed, where on 1 mm slices on the suite's grid the reading without
  the rule had been 0.19 degrees off. No flag is raised where the label does not part, since on the
  cache that is all but 5 of the 294 readings with flipped voxels or a ragged edge and would say
  little; the free wall's flag says what the freedom means in each case.
- Nothing of this pass has been read on a real level; that happens on the grid once PR 44 is merged
  and the engine re-pinned in SchwingNet, on a count of the owner's.

## The verse run on the grid

- Sent at 08:25 UTC by another session, on the owner's yes of 23:47 UTC and the count of 15:19 UTC
  (two CPU jobs, enhance and verse): Slurm 40877151 on mem4, at SchwingNet 3abc2fa, with the engine
  pinned before this pass (code stamp 81e732f142d3aa16). It ended COMPLETED, exit 0, at 12:21 UTC
  after 3 h 55 min (sacct in the gate's status of 13:45 UTC). The cancel another session sent at
  13:40 UTC found it ended and cancelled nothing.
- Its report, read at 14:19 UTC with the gate word `morphometry verse`, which printed the report
  that stood and queued nothing: VerSe's 374 masks measured in 821 s, one study flagged as an
  error; TotalSegmentator's 159 admitted subjects stacked into int16 in VerSe's ids with none failed,
  measured in 84 s, none flagged. Screening verdicts: VerSe 21 admitted, 6 to look at, 347 not
  admitted; TotalSegmentator 154 admitted, 5 not. The per-level medians of the two sets agree within
  about 1 mm: anterior body height at L3 29.8 and 29.5 mm, posterior (inset) 29.8 and 28.6, the
  anterior-to-posterior index rising from about 0.90 to 0.93 at T6 to T8 to 1.13 and 1.14 at L5, as
  thoracic wedging and L5's anterior height lead one to expect. The rows, facts and verdicts stay on
  the grid under the morphometry root; only these aggregates left it.
- Why it took long: measuring took about 15 minutes of the 3 h 55 min. The rest was the stacking of
  TotalSegmentator's subjects, one at a time in a shell loop, and the screening, which the report
  does not time apart. SchwingNet #498 (merged 13:54 UTC by another thread) stacks them in parallel
  for any later run. The covariates join (job 40878978, another thread's) has read both sets' rows.
- These rows come from the engine pinned in SchwingNet before PR 44 (bordercall 16f7b40, its
  grid/bordercall/VENDORED at 3abc2fa), so none of this branch's readings is in them: the pedicles' sagittal angle, the end-plates' inclinations and the spinous
  angle are taken against a posterior wall read by its hindmost voxels, which erred up to 4.1 and
  5.7 degrees on the phantoms near the frame. The heights, widths and areas do not take that slope,
  though the body's cut and the canal's lateral-film depth take the canal line, whose staircase item
  3 below names. A run on the reworked engine waits for PR 44's merge, the re-pin and the owner's
  count.

## What is left, in order

1. Mark PR 44 ready and merge once the owner says so, then re-pin the engine into SchwingNet
   (`python3 tools/bordercall_vendor.py copy <clone>` from SchwingNet main) and close bordercall PR
   41, the other thread's vendoring draft.
2. On the grid, on the owner's count: the 229-spine sweep with the reworked engine, the wall's
   refusals and flags counted by level beside the sagittal angle's.
3. Read the canal's line on the lattice (anatomy.wall_slope), since it still sets the body's cut,
   Panjabi's depths and the gate, and traces the staircase (up to 3.7 degrees off on 1 mm slices and
   7.7 on 2.5 mm) and a notch's floor.
4. The transverse angle's construction and the isthmus finder's two misses, as the list of 01:45 UTC
   says.

# Morphometry: the handoff of 2026-10-30, 01:45 UTC

Source: the thread "Run morphometry on gold tier 3 masks" of the claude.ai project symphony_5. This
pass fixes what the adversarial review of 01:15 UTC found (the section of that name, below), on the
owner's "continue" of 01:15 UTC, after his "PLEASE JUST PUSH ALL RESULTS NOW!" of 01:16 UTC had the
review pushed first (d0d5988). Pushed to bordercall's branch claude/project-thread-e89pjg, draft PR 44.
No grid job was sent in this pass, and no real mask was read in a container.

## What this pass fixed

- Finding 1, the angle's definition: the sagittal angle is the projection again, atan2(d[2], -d[1]),
  as the phantom's truth, the transverse angle and the papers' lateral readings are; the height's
  pitch correction keeps hypot(d[0], d[1]), the cosine of the axis's elevation, which is right for a
  length read square to the axis. The 0.13-degree difference the earlier sections speak of is gone.
- Finding 2, thick slices: parting now returns the range of slopes b of every surface that still
  parts the centres it parts (slope_range, two more linear programs), and climb refuses the angle
  where the mean of the two surfaces' ranges is over FREEDOM_DEG, 9 degrees. The bound is set on the
  phantoms (the scratch probe probe_interval, not committed): on 1 mm slices, six phantoms (straight,
  shapes, pitched 10, pitched down 8, steep 12 with 25 of convergence, overhang) on six grids (the five
  tilts and one within 2 degrees of the frame), the 58 readings whose columns span 5.5 mm or more had
  ranges of 0.2 to 7.7 degrees and lay within 1.8 of the truth but for six: five on the grid tilted 2
  (2.5 to 3.4 high, below) and the overhang's right side at a tilt of 12 (2.1 high, its surfaces 1.9
  apart); on 2.5 mm slices, two phantoms on five grids, the 14 such readings had ranges of 10.6 to 33
  degrees and lay up to 9.7 off. So no 2.5 mm phantom reads a sagittal angle.
  ThickSlices now asserts that the angle is refused or within twice the suite's tolerance.
- Finding 3, the two surfaces: climb refuses where the top's and the bottom's climbs lie more than
  APART_DEG, 5 degrees, apart (at most 3.2 on the 1 mm phantoms); both stay in the record.
- Finding 8, a far crossing: a surface whose worst centre lies more than SURFACE_LAYERS layers across
  the best surface is refused, beside the share rule.
- Findings 4 and 5, the words: the research note counts four reworked measures and marks the table's
  sagittal row as the old construction's (run229); four phantoms over five tilts; the numbers in the
  sections below are corrected where they differed from the prototype's log.
- Finding 6, the docstrings: columns, parting and climb say what the code does, every reason climb
  refuses is listed, and the constants carry their words.
- Finding 7, the tests: PitchedDown (P.lumbar(ped_s=-8, ped_t=8), the sign), Overhang (a thin sagittal
  superior articular process over the isthmus's outer columns, which makes the per-column admission
  decide the reading), LateralMass's angle not read with the span's note, and ThickSlices'
  refused-or-right.

## What is verified, and what is not

- The suite: `PYTHONPATH=. python -m unittest morphometry.tests.test_morphometry`, 26 tests, all pass
  (321 s on four CPUs; the 22 of the previous pass and the four new ones); `python -m unittest
  morphoview.tests.test_lines`, 10 tests, all pass.
- Found while calibrating, not fixed: on a grid within a few degrees of the vertebra's own frame (a
  tilt of 2 degrees, as most supine lumbar studies lie), the sagittal angle reads 2.5 to 3.4 degrees
  high on the pitched phantoms. The climb itself is right there; the error is the posterior wall's
  slope (body.posterior_wall_slope), which reads the phantoms' vertical walls 1.8 to 4.2 degrees off
  on such grids (-0.1 to -0.8 at the suite's tilt of 18 degrees), and the sagittal angle is taken
  against the plane square to that wall. The end-plates' inclinations (body.inclinations) are taken
  against the same plane and carry the same error. Tracing that reading is the next step, before any
  real run reads either.
- Two readings of the 66 find no isthmus (the pitched and the steep column's right side at a tilt of
  12 degrees about (0.3, 1, 0), the grid turned 4), a failure of the profile, left for a later pass.
- Nothing of this pass has been read on a real level; that happens on the grid once PR 44 is merged
  and the engine re-pinned in SchwingNet, on a count of the owner's.

The grid, read at 08:59 UTC on 30 October from symphony-template's branch grid:

- The enhance job, Slurm 40872077 on mem4, ran from 05:17 to 05:58 UTC and exited 0 (40:48 elapsed).
  Its report (logs/job-schwingnet-morphometry-enhance.json, read at 08:24 UTC): 1597 ENHANCE.PET masks
  measured in 2248 s by code stamp 81e732f142d3aa16 at SchwingNet 6b243e7, which is the engine pinned
  before this rework; 6 studies flagged error; the screening admitted 1561 and refused 36. The rows,
  facts and verdicts stay on the grid under /rs/rs_grp_oschome/go2432/morphometry/enhance/. The level
  medians of the heights hold the expected shape: the thoracic bodies wedge (the index 0.90 at T7,
  0.91 at T6 and T8), L5 is taller in front (1.15), and 62 studies carry an L6.
- `schwingnet-morphometry-verse` was sent at 08:24:46 UTC by another session (run 333 of
  grid-accounts.yml, request morphometry-verse-20261030T0826Z), on the owner's yes of 23:47 UTC: Slurm
  40877151, submitted at 08:25:37 UTC. This thread did not send it again; the gate refuses a second
  morphometry job while one is live, and the same word sent once the job has ended reads its report,
  logs/MORPHOMETRY-verse.md.

## What is left, in order

1. Done in the pass of 14:00 UTC above: trace body.posterior_wall_slope on the grids aligned with the
   frame, since the sagittal angle and the end-plates' inclinations both take its error there, and
   add a test on a grid tilted 2 degrees.
2. Mark PR 44 ready and merge once the owner says so, then re-pin the engine into SchwingNet
   (`python3 tools/bordercall_vendor.py copy <clone>` from SchwingNet main) and close bordercall PR 41,
   the other thread's vendoring draft.
3. On the grid, on the owner's count: the 229-spine sweep with the reworked engine, as item 2 of the
   list of 00:10 UTC below says, the sagittal angle's refusals counted by level beside its readings.
4. The transverse angle's construction and the isthmus finder's two misses, as below.

# Morphometry: the handoff of 2026-10-30, 00:10 UTC

Source: the thread "Run morphometry on gold tier 3 masks" of the claude.ai project symphony_5, which took
PR 44 over from the thread "Advance morphometry" (the handoff of 23:10 UTC, below) on the owner's word
of 2026-10-29 23:36 UTC ("do these two"), his rule of 23:41 UTC that the measuring runs on the grid and
not in the cloud, and his yes of 23:47 UTC to sending `schwingnet-morphometry-verse` once the enhance
job is gone. Everything below is pushed to bordercall's branch claude/project-thread-e89pjg, draft PR 44.

## What changed since 23:10 UTC, and what is verified

- The sagittal angle (morphometry/pedicle.py: columns, lattice_under, parting, climb; the module's
  docstring says why): it is no longer the slope of the middles of one column a row, which the raster
  quantised (a layer of 1.24 mm over the isthmus rows' 7.5 mm is 9 degrees, so the suite read 3.1
  against 0 and 8.3 against 6). Each of the pedicle's two surfaces is now parted from the scan's own
  lattice over the isthmus rows: under the columns across the middle half of each row's section whose
  run is the pedicle's (within HEIGHT_SHARE of the isthmus's height, which keeps out the columns under
  the articular process's base and the body's corner), the voxel centres within 1.5 layers of that
  column's surface, bone and air, are parted by the surface z = a + b y + c x' + d x'^2 of widest
  margin, a linear program (scipy.optimize.linprog, no new dependency), x' the place across the section
  from its middle so that the ellipse's crown goes into the quadratic; the climb is the mean of the two
  surfaces' b, along the pedicle's centre line. The centres on both sides of a surface bracket it
  wherever the layers cut it at another phase, which under a tilted grid they do across the columns,
  so the bracket is far tighter than one column's layer. Where no one surface parts the centres (more
  than a tenth lie across the best, a least-crossing program) the angle is not read, with a note. The
  rows beyond the isthmus (the walls' extension, which the transverse angle keeps) are not taken for
  the climb: under them the pillar's and the body's corner's bone stood about the surface, the margin
  went negative and the climb read 10 degrees off on the straight phantom. The sagittal angle is now
  atan2 of the climb against the horizontal length of the axis (it was against the y component alone,
  a difference of 0.13 degrees at 12 degrees of convergence), and the height's pitch correction the
  cosine of that angle. [The review's finding 1: the projection is the right reading, and the pass of
  01:45 UTC, above, reads it again; the height's correction stays.]
- Verified on the phantoms over five tilts and turns of the grid, four phantoms (straight, shapes,
  pitched, pitched down; the lateral-mass column's columns span 4.0 mm and give no reading), L3's two sides (the
  prototype of this pass, run before the code was written into pedicle.py and then as the module's own
  trace): the straight column (truth 0) reads between -1.5 and +0.7 degrees where the pushed code read
  -8.8 to +4.8; the shapes column (truth 6) 5.2 to 6.5 where it read 4.8 to 11.4; a column pitched 10
  degrees 8.2 to 10.9 where it read 10.8 to 20.3; one pitched -8 with 8 degrees of convergence -6.8 to
  -9.4 where it read -0.5 to -9.5; every reading whose columns span 5.5 mm or more within 1.8 degrees
  of the truth, most within 1. At the suite's tilt the module's trace reads 0.46 on the straight
  column and 6.40 on the shapes column; the lateral-mass column's columns span 4.0 mm and its angle is
  not read, as before. The transverse angles, widths, heights, chords and interpedicular distances are
  as the fourth pass read them, since nothing of their construction changed.
- One reading of the fifty found no isthmus at all (the pitched column's right side at a tilt of 12
  degrees about (0.3, 1, 0) with the grid turned 4), a failure of the profile, not of the climb, left
  for a later pass.
- The suite: `PYTHONPATH=. python -m unittest morphometry.tests.test_morphometry`, 22 tests, all pass
  (279 s on four CPUs; 20 of 22 passed on the pushed code). `python -m unittest
  morphoview.tests.test_lines`, 10 tests, all pass, after one fix of the fourth pass's work: the
  interpedicular lines drawn from the band failed test_a_length_is_the_distance_between_its_ends
  on the pushed code too (21.863 drawn against 21.803), since the least distance is the median
  over the rows about the isthmus and the line is drawn in the row nearest it, so those two lines
  now carry the rule median, as the pedicle's width and height do (morphoview/lines.py).
- morphometry/tests/trace_pedicle.py prints the parted surfaces (columns, span, each surface's counts,
  margin, centres across and slope) in place of the middles; morphometry/tests/probe_axis.py called
  isthmus with two arguments where it takes three since the fourth pass, and runs again.

## The adversarial review of this pass (01:15 UTC), and what it leaves open

Four reviewers read the pushed commit 0e847cd by geometry, robustness, the words against the code
and the tests; each finding of the first two lenses was put to two skeptics, and the skeptics of
the last two lenses did not run (the session's plan ran out), so their findings below are the
reviewers' alone, checked by hand where this says so. None is fixed in the commit that recorded
them (d0d5988, on the owner's word of 01:16 UTC to push every result now); every one is fixed in the
pass of 01:45 UTC, at the top of this file.

Confirmed by both skeptics:

1. The sagittal angle is now the axis's elevation, atan(tan s cos t), not the sagittal projection
   atan2(d[2], -d[1]) that the phantom's truth, the transverse angle and the papers' lateral-view
   readings use; it under-reads by 0.13 degrees on the Shapes phantom (t 12, s 6) and by 1.3 to
   1.9 at L5-like convergence (t 30, s 10 to 15). The fourth pass's formula was the projection and
   was not the source of its errors. Fix: report the projection again, keep hypot(d[0], d[1]) for
   the height's correction, which is right for it, and say why the two differ.
2. On 2.5 mm slices the widest-margin surface can snap to the scan's own layers: where a 7 mm span
   crosses no layer gap (a surface within about 20 degrees of the axial planes), every surface
   between two layers parts bone from air and the widest is parallel to the lattice, so the angle
   reads the vertebra's tilt in the scanner with a positive margin and nothing across, which no
   rule refuses; where it crosses one gap it threads the step at 25 to 40 degrees. The phantom
   sweep covered 1 mm slices only and ThickSlices tests no pedicle angle. Fix: compute the
   interval of slopes that still part the lattice (two more linear programs, min and max b) and
   refuse the angle where it is wider than a bound set on thin and thick phantoms; add a
   ThickSlices pedicle assertion (not read, or within its bound); qualify the 1.8 degree claim as
   holding at 1 mm slices.
3. The two surfaces' climbs are averaged with no check that they agree. Fix: refuse where they
   differ by more than a bound set on the phantoms, both kept in the record for the trace.

The reviewers' alone (the words and the tests), to fix with the above:

4. The research note's line 7 still counts three reworked measures; the sagittal angle is a fourth,
   and its row in the comparison table is the old construction's (run229), with no caveat.
5. "Five phantoms" should read four phantoms over five tilts (straight, shapes, pitched, pitched
   down; the lateral-mass column's columns span 4.0 mm and give no reading); two numbers here
   differ from the prototype log (the old reading of the pitched-down column ran -0.5 to -9.5, not
   -1.5; the formulas' difference is 0.13 degrees, not under 0.1, and goes with finding 1).
6. columns' docstring says each row's section where the code takes the isthmus's median section;
   parting returns the first program's margin beside the second program's coefficients; climb's
   docstring omits the reason "no surface parts"; MIN_COLUMNS, MIN_PARTED and SAGITTAL_SPAN_MM want
   their words; the span now counts half a pixel more than the 0004 numbers the docstring quotes.
7. The suite does not exercise the per-column HEIGHT_SHARE admission (switching it off leaves the
   tests green); a phantom with a thin sagittal superior articular process over the isthmus's
   outer columns, P.lumbar(sap_x=19, sap_y=-10, facet=0, sap_thk=3.5, sap_len=14), makes it decide
   the reading; a pedicle pitched down, P.lumbar(ped_s=-8, ped_t=8), tests the sign. Both are to
   be added as tests, with their expected values measured on the fixed code; LateralMass can assert
   that its angle is not read, with the span's flag.
8. A surface crossed far, not by many, passes the VIOLATED_SHARE rule (a margin of -4.8 mm with 5.5
   per cent across was accepted on the overhang phantom with the admission off); refuse a margin
   below -SURFACE_LAYERS layers as well.

Refuted by the skeptics: an unbounded margin program reported as no surface (real in isolation,
not reachable from the band lattice_under builds); the 1e-9 crossing threshold against HiGHS's
tolerance (the slacks of a basic solution are exact zeros); VIOLATED_SHARE as a share of all
centres (no band of that composition arises). Verified by the tests' reviewer: the two red tests
now take the new path, LateralMass and the cut-volume case hold, and no caller reads the removed
key mids.

## The grid

The owner's rule of 23:41 UTC: the measuring runs on the grid, never in the cloud; no mask comes into a
container. The enhance job, Slurm 40872077 (queued 22:47 UTC), stood PENDING on a dependency at 23:02
and at 23:44 UTC (the status reads metaflow-smoke-status-2302 and morphometry-status-20261029T2345Z on
symphony-template's branch grid), behind the runs that held the checkout when it was queued. The next
status read is scheduled for 01:19 UTC on 30 October, then further apart; the moment status shows the
job gone, `schwingnet-morphometry-verse` goes through grid-accounts.yml (action job) on the owner's
yes of 23:47 UTC and his count of 15:19 UTC, and its time and Slurm id are written here. Both sets run
the engine pinned in SchwingNet main, without the pedicle rework; the rework reaches the grid only
once PR 44 is merged, the engine re-pinned (`python3 tools/bordercall_vendor.py copy <clone>` from
SchwingNet main) and a run queued on a count of the owner's.

## What is left, in order

1. The adversarial review of this pass into PR 44's body (the review of the fifth pass is being
   written as this handoff is), then mark ready and merge once the owner says so, and re-pin the
   engine into SchwingNet; close bordercall PR 41, the other thread's vendoring draft.
2. On the grid, on the owner's count: the 229-spine sweep with the reworked engine and the renders of
   study 0004 at C5, T1, T8, L3, L4 and L5, the level medians of the pedicle angles beside Zindrick's
   and Panjabi's, the flags counted (L5 and the neck); the facet pairing that fails at four of six
   levels of 0004, the discs' corner heights (L3-L4 1.6 mm behind, T8-T9 1.0 in front) and C5's
   upper end-plate depth (9.8 against 16.7), all found by the fourth pass's 0004 measure, are traced
   on those renders. None of it runs in a container.
3. The transverse angle's construction (the canal wall's angle over a few rows) stays the open
   problem the fourth pass named; the isthmus finder's one miss above.


# Morphometry: the handoff of 2026-10-29, 23:10 UTC

Source: the thread "Advance morphometry", written on the owner's word of 23:06 UTC ("im about to
run out of fable please just write what you have now"). Everything below is pushed to bordercall's
branch claude/project-thread-e89pjg, draft PR 44 (it supersedes PR 30, now closed), with bordercall main (6d261f6, PR 28) merged in.
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

## The test suite on the pushed code (23:28 UTC)

`python -m unittest morphometry.tests.test_morphometry`: 22 tests, 20 pass, 2 fail, both on the
sagittal angle alone: Straight.test_pedicles reads L3's sagittal angle 3.13 against 0 and
Shapes.test_pedicle_angles 8.30 against 6, each over the 1.5 degrees the tests allow. Widths,
heights, transverse angles, chords and both interpedicular distances pass on every phantom,
the LateralMass case included. The sagittal angle is quantised by the raster on the 7.5 mm
baseline the isthmus rows give (one layer of 1.24 mm over it is 9 degrees); either read it from
the pedicle's top and bottom surfaces fitted as planes over the rows, or let the test state the
raster's bound. Until one of the two is done the suite is red on those two tests and the pull
request stays a draft.

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

Start from bordercall PR 44 (branch claude/project-thread-e89pjg, at its pushed head): the
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
5. The adversarial review into PR 44's body, mark ready, merge; then re-pin the engine into
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
