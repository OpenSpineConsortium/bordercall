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

- SUITE_LINE
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

The grid, as of this pass: the enhance job, Slurm 40872077, stood PENDING on its dependency at 01:16
UTC; `schwingnet-morphometry-verse` waits for status to show it gone (the section The grid, below).

## What is left, in order

1. Trace body.posterior_wall_slope on the grids aligned with the frame, since the sagittal angle and
   the end-plates' inclinations both take its error there, and add a test on a grid tilted 2 degrees.
2. Mark PR 44 ready and merge once the owner says so, then re-pin the engine into SchwingNet
   (`python3 tools/bordercall_vendor.py copy <clone>` from SchwingNet main) and close bordercall PR 41,
   the other thread's vendoring draft.
3. On the grid, on the owner's count: the 229-spine sweep with the reworked engine, as item 2 of the
   list of 00:10 UTC below says, the sagittal angle's refusals counted by level beside its readings.
4. The transverse angle's construction and the isthmus finder's two misses, as below.

