# Morphometry: the handoff of 2026-10-30, 14:00 UTC

Source: the workflow that reworked the posterior wall's reading on bordercall's branch
claude/project-thread-e89pjg (draft PR 44), item 1 of the list of 01:45 UTC below, then put the
rework through an adversarial review and fixed what it found. The working tree holds the rework
and the fixes, not yet committed. No grid job was sent, and no real mask or CT was read: every
number here is from phantoms.

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
were measured by scratch scripts of this workflow, not committed: build_cache.py, score.py,
judge/robust.py (with a copy that calls body.posterior_wall and keeps its record), speck6.py and
the probes under fix/. So that they can be built again:

- The cache (build_cache.py): L2 to L4 drawn and L3 built as measure_volume builds it, for four
  phantoms and their walls' leans: straight (upright, leaned 5 degrees forward and 5 back), pitched
  (ped_s 10, upright), shapes (Ha 30, concavity 2, waist 0.92, ped_t 12, ped_s 6, facet 55, sp_angle
  32; upright and leaned 4 forward) and pitched down (ped_s -8, ped_t 8, upright); on seven grids,
  each the column's tilt and the grid's turn about z: aligned, 2, 5 and 10 degrees about x, 18
  about (1, 0.3, 0) turned 7 (the suite's), 25 about (1, 0.3, 0) turned 15, and 12 about (0.3, 1,
  0) turned 4; at 0.8 by 0.8 by 1 mm and 0.86 by 0.86 by 2.5 mm. That is 49 vertebrae a thickness,
  98 in all. The lean is drawn by shearing the body's inside test, y less z tan(lean), as
  phantom.Vert.lean now does.
- The score (score.py): the wall's slope against the true lean taken into the frame the vertebra
  was read in, and downstream the pedicles' sagittal angle, the end-plates' inclinations and the
  spinous angle against their truths.
- The alterations (robust.py), twelve that keep the wall's slope, each drawn about the true wall:
  notches 6 mm wide, 4 tall and 2 deep at mid-height and half-way to the window's top, and 5 by 6 by
  4 at mid-height; a lip 1.5 mm proud, 16 mm across, from 3 mm inside the window's top up; an
  osteophyte 3 mm proud at the upper end-plate, outside the window; an axial scallop 1 mm deep at the
  midline, a cosine squared across 16 mm; a sagittal bow 0.8 mm deep at mid-height; six holes of 1 mm
  radius 0.8 to 3 mm inside the wall; a segmenter's ragged edge, a smooth random field of 0.3 mm
  over 3 mm and of 0.5 mm over 4 mm, whose own lean over a band 6 mm either side is reported beside
  it; the wall's boundary voxels flipped at random, one in five; and the volume's last slice 30 per
  cent of the body's height below its top.
- The specks (speck6.py): one voxel of the label, not of the body, a step behind one of six edges
  spread up the window near the midline, each in turn on each vertebra: 294 labels a thickness.
- The probes: the notches of several sizes on the suite's grid and on the grid tilted 2 degrees,
  the cervical C5 at leans of 0 and 5 either way with its pedicles 2 mm up or down, C2 with dens of
  several shapes, and the canal line against the true wall over the cache.

## What is verified, and what is not

SUITE_AND_SCORE_LINES

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

