<!-- claude-projects-attribution: {"github_login":"Gregory-Schwing-MD-PhD"} -->
_Requested by **greg** · [project thread](https://claude.ai/code/project/chan_01MwYPPvcbNuPAZMMRXv1mUg?thread=cmsg_01MwYPPvcbNuPAZMMRXv1mUgU53FoS6pWbiBU9pX1cq664); carried on in the project symphony_5's thread "Run morphometry on gold tier 3 masks"_

Draft. Supersedes #30: this branch carries every commit of #30 (the morphometry engine, maskedge, the screening package, the VerSe record and the own-axis frame), bordercall main merged in, and on top of them the rework of the three measures the run of 29 October withheld as wrong by construction, the sagittal angle read from the pedicle's own surfaces, and now the posterior wall that angle and the end-plates' inclinations are read against. `research_notes/morphometry/handoff.md` says, pass by pass (30 October at the top), what is verified and what is not, and the steps left in order.

## What this adds beyond #30

- The pedicle (`morphometry/pedicle.py`, rewritten): found by a march from the canal's midline in rows front to back at three heights, the isthmus the least section area, the isthmus rows cleaned of the body's corner, the lamina and a process's edge, the width and height the medians over them, the axis across along the medial wall, the level's width limit (C 12, T 16, L 20 mm) and a guard for a cervical pedicle whose foramen transversarium the mask does not close.
- The sagittal angle (30 October): each of the pedicle's top and bottom surfaces is parted from the scan's own voxel centres under the columns across the isthmus rows, bone from air, by the surface z = a + b y + c x' + d x'^2 of widest margin (a linear program on scipy, already a dependency), and the climb is the mean of the two; one column's surfaces step with the raster, which had read 3 degrees on a level pedicle and 8 on one pitched 6. The angle is the sagittal projection, atan2(d[2], -d[1]). It is refused where the surfaces that still part the lattice leave it free over 9 degrees, as on every 2.5 mm phantom, where the two surfaces' climbs lie more than 5 degrees apart, and where a surface's worst centre lies more than 1.5 layers across it. On 1 mm slices, over six phantoms on six grids, every reading whose columns span 5.5 mm or more lies within 1.8 degrees of the truth, where the fourth pass read up to 9 off, but for one overhang reading at 2.1 and those on a grid aligned with the frame (below).
- The posterior wall's slope (30 October, `body.posterior_wall`), which the sagittal angle, the end-plates' inclinations and the spinous angle are taken against: read on the scan's own lattice from the vertebra's whole label, the last bone of each scan line in a band across the midline, a trimmed and reweighted fit of the surface y = a + b z + c x + d x^2, and the slope clamped into the range of slopes whose surfaces part the label's bone from its air, up to three stray edges set aside first. It is refused, and the angles taken against it with it, each flagged, where that range is wider than 9 degrees or where more than 40 per cent of the band's edges lie over a step off the fit (a deep basivertebral notch); at C2 the window ends at the top of the canal's full rings, below the dens. The hindmost-voxel reading it replaces erred up to 4.14 degrees on 1 mm slices and 5.66 on 2.5 mm over 98 phantom vertebrae on seven grids; this one errs at most 0.35 and 0.79 (medians 0.07 and 0.19), and up to 1.64 and 3.03 under alterations that keep the wall's slope (notches, holes, an osteophyte, a scallop, a bow, flipped boundary voxels, the volume's edge). Two go further and are written down: a segmenter's ragged edge leans the label's own wall, and a lip 1.5 mm proud near the window's top reads up to 11.7 degrees off on 2.5 mm slices, told by no statistic of the fit. `morphometry/tests/probe_wall.py` builds that cache and scores a reading on it.
- The interpedicular distance, least and greatest, read between the pedicles' own medial walls at their place (`pedicle.canal_between`, `canal.measures`), the hole's width through the middle standing in, flagged, where a pedicle is missing.
- The disc's plate rule: a plate's surface is the typical one over its band (`body.band_typical`), not the band's outermost point, which read 1.35 mm into the disc in the neck.
- `morphoview/lines.py` draws the new lines; the phantom's lateral-mass case and the LateralMass test are rewritten for the foramen beside the pedicle; three probes under `morphometry/tests/` (trace_pedicle, which prints the parted surfaces, probe_axis, slices_pedicle) print and draw the reading row by row.

## Where it stands

- The suite at 0cce747: 39 tests, all pass (428 s on four CPUs); the thirteen added since 9e565c4 are the wall's: its reading on a grid 2 degrees off the frame, its refusal carried to the four angles taken against it, the clamp, specks behind it, a notch below mid-height that a plain fit reads 7.0 degrees off, a speck on the solver's tolerance, a notch too deep to read past, a wall the lattice leaves free and the flag where the label does not part, C2 with its dens, and the end-plates' inclinations on thick slices and past the notch. The tests the review asked for each fail with their fix taken out. morphoview's 10 pass.
- Verified by trace on the phantoms: widths within 0.1 mm, heights within 0.1, the transverse angle within 0.6 degrees, the interpedicular distances within 0.2 mm, the sagittal angle within 0.5 degrees at the suite's tilt (0.46 on the straight column, 6.40 on the one pitched 6).
- On study 0004 (the fourth pass, 29 October, in the earlier thread's container; nothing real is measured in a container since the owner's rule of 23:41 UTC): widths, heights and interpedicular distances read plausibly at L3, L4 and T8; L5 is flagged (the transverse process's root fused to the pedicle); C5 is refused by the foramen guard; the transverse angle is not trustworthy on real masks (L4's left -6.5, T1's right 47 degrees); the sagittal angle of the reworked reading has not been read on a real level yet, which happens on the grid once the engine is re-pinned.
- Fixed since 9e565c4: the posterior wall's slope (above), which on a grid within a few degrees of the vertebra's frame, as most supine lumbar studies lie, had put the sagittal angle 2.5 to 3.4 degrees high and the end-plates' inclinations off by as much. Left, and written in the handoff: the canal's line (`anatomy.wall_slope`), which sets the body's cut, Panjabi's depths and the wall's gate, still follows the lattice's staircase (up to 3.7 degrees on 1 mm slices, 7.7 on 2.5 mm) and a notch's floor; it is next.
- Not run: the 229-spine sweep with this engine, which is grid work on the owner's count after the merge and the re-pin. The enhance and verse sets of 29 October ran on the engine pinned before this branch (bordercall 16f7b40): enhance (Slurm 40872077) ended at 05:58 UTC, verse (Slurm 40877151) at 12:21 UTC, both exit 0, so their sagittal angles, inclinations and spinous angles carry the old wall reading.

Nothing here touches holdings/ or the grid; no mask, CT or per-study row is committed, and no paper's text.

## Adversarial review

### First review, of the sagittal angle (30 October)

Four reviewers read commit 0e847cd by geometry, robustness, the words against the code and the tests; each finding of the first two lenses went to two skeptics (the skeptics of the last two lenses did not run, the session's plan having run out). `research_notes/morphometry/handoff.md` holds every finding; all eight are fixed in 9e565c4:

- **Confirmed, fixed: the angle was the axis's elevation, not the sagittal projection.** It under-read by 0.13 degrees on the Shapes phantom and by 1.3 to 1.9 at L5-like convergence. It is the projection again; the height keeps the elevation's cosine.
- **Confirmed, fixed: on 2.5 mm slices the surface could snap to the scan's layers.** The range of slopes that still part the lattice is now read by two more linear programs, and the angle is refused where it is over 9 degrees (thin phantoms 0.2 to 7.7, thick 10.6 to 33). ThickSlices asserts the angle is refused or right.
- **Confirmed, fixed: the two surfaces' climbs were averaged unchecked.** Refused beyond 5 degrees apart (at most 3.2 on the thin phantoms).
- **The reviewers' alone, fixed:** the research note counts four reworked measures and marks the old sagittal row; four phantoms over five tilts in the earlier pass; the docstrings of columns, parting and climb; the overhang and pitched-down tests, which make the per-column admission and the sign decide a reading; a surface crossed far, now refused beyond 1.5 layers.

Refuted by the skeptics: an unbounded margin program misreported (unreachable from the band built), the crossing threshold against the solver's tolerance, and the violated share as a share of all centres.

### Second review, of the wall's reading (30 October)

Four reviewers read the rework by geometry, robustness, the words against the code and the tests, and each finding went to skeptics; twelve held. Fixed in the head:

- **A notch holding more than a quarter of the band's edges read the wall about 29 degrees off, unflagged.** The wall is now refused where more than 40 per cent of the edges lie over a step off the fit (DeepNotch).
- **C2's wall was read mostly on the dens, 2.3 to 9 degrees off.** The window ends at the top of the canal's full rings (DensAtC2).
- **HiGHS's no-verdict status was read as an unbounded range, so one speck refused the wall as free over 180 degrees.** Parting is asked of a widest-margin program first (SpeckOnTheMargin).
- **The clamp was all or nothing: one stray voxel among 80 to 240 edges turned it off.** Up to three edges are set aside first (LeanedWall's specks test).
- **The free-wall flag promised an error of half the freedom,** which the clamp does not give; it now says up to the freedom where the label parts, and that the freedom bounds nothing where it does not.
- **The band was twice as wide as the words said.** The words say a half-width.
- **The figures rested on a scratch cache with no record in the repository.** `morphometry/tests/probe_wall.py` builds and scores it, and reproduces the scratch figures on the same configurations.
- **No test pinned the clamp, and BasivertebralNotch did not test the robust fit.** LeanedWall's clamp test, and the notch drawn 4 mm below mid-height, where a plain least-squares fit reads 7.0 degrees off.

Left, with the reason, in body.py's docstring and the handoff:

- **The gate is centred on the canal's line, which a notch leans** (18.7 degrees through a 5 by 6 by 4 mm notch). Re-centring it on the first fit hid the dropped share and let the deep notch read 29.7 off, so the share's refusal stands behind it; the canal line itself is the next fix.
- **On cervical bodies the 6 mm band reaches the pedicle roots.** The wall still reads within 1.47 degrees there; a band of a quarter of the body's width was better on one thickness and worse on the other, and was not taken.
- **No flag where the label does not part.** On the cache that is all but 5 of the 294 readings with flipped voxels or a ragged edge, so the flag would say little.

A check of the fixes found the share rule refusing some sound walls (a 5 by 10 by 4 mm notch on three of four grids and thicknesses) and five places in the words and the research note that no longer matched; the words are corrected and the refusal is written down as a known cost.

---
_Generated by [Claude Code](https://claude.ai/code)_

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01Pn5qEJbGG6tvpFq8R3s7FA
