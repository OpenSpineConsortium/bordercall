# Morphometrics from the gold tier 3 CT masks

Thread "Extract morphometrics from gold tier 3 CT" of the claude.ai project symphony_4, 29 October 2026, from the owner's message of 02:12 UTC that day: start a survey of the morphometrics that can be taken programmatically from the gold tier 3 data, using patented validated approaches and those of the clinical reread (Eisenstein's posterior limit of the canal among them), implement and test them on the masked CTs, and look for test cases with ground-truth measurements, open datasets and code to compare with and reproduce. Confidential, like everything in bordercall: nothing here goes to a public place. No paper's text is quoted; the papers' methods are described in our own words and their values come from the paper tables (series.csv, below). No mask, CT or per-study row is in git: the rows stay in the project's files, and only aggregates are written here.

## The result in brief

The run over the 229 thin-slice ENHANCE.PET studies finished at 13:10 UTC on 29 October 2026: 228 studies measured and one (0980) stopped by an error, 452,546 rows in the project's files under gold3-ct/morphometry/run229/, never in git. Every measure can be drawn on its own cuts of its own vertebra, and on study 0004 all 150 lines at C5, T1, T8, L3, L4 and L5 match the run's rows (morphoview, below). Against truth of five kinds: on the phantom's exact shapes the 20 tests hold lengths to 0.75 mm and angles to 1.5 degrees; on three ENHANCE.PET CTs the masks lie on the bone's own edge to within a few tenths of a millimetre, and leave each lumbar disc 0.3 mm wider and each cervical disc 0.5 mm narrower than the disc the CT shows; read again on the same studies thinned to 3 and to 5 mm slices, the median of every measure moves by less than 0.9 mm; and against the papers' adult means, the heights, the end-plates' depths and the widths at their rims read larger, the papers themselves differing by as much at some levels (the comparison, below). Four measures were wrong by their construction and are reworked on PR 44's branch, claude/project-thread-e89pjg, which supersedes PR 30 (pedicle.py, canal.py, body.py; handoff.md), not yet verified on real spines beyond study 0004's traces, so they stay out of the comparison until the run is made again: the interpedicular distance at L4, L5 and in the neck, read across the canal's middle where the papers read between the pedicles; the pedicle's width and height in the neck and at C7 and T1; and the mid-disc height in the neck and the upper thorax, whose rule for a plate's surface reads 1.35 mm short of the gap the masks leave; and the pedicle's sagittal angle, read from one column's middle a row and so stepped with the raster, whose row in the table below is that old construction's. The VerSe test of the heights against two readers' fracture grades waits on the helper thread that reads VerSe.

## What was built

The package [morphometry/](../../morphometry/) measures a labelled CT: every vertebra, every disc, the column and the pelvis, one row per measure with its value or the reason it has none. It builds on [scanimport/](../../scanimport/) (the label schemes, the frames and the canal's slabs) and adds nothing outside Python's standard library, NumPy, SciPy and nibabel.

```
python -m morphometry measure --labels 0004.nii.gz --scheme enhance --study 0004 --out rows.csv
python -m morphometry run --masks DIR --scheme enhance --out DIR --workers 3 --max-slice 1.25
python -m morphometry compare --rows DIR/rows.csv --series series.csv --out DIR/compare.csv --max-slice 1.25
python -m morphometry phantom
python -m morphometry thicken --labels 0004.nii.gz --scheme enhance --study 0004 --to 2.5 5 --out thick.csv
python -m morphometry bench --slice 2.5
python -m maskedge measure --ct CT.nii.gz --labels 0004.nii.gz --scheme enhance --study 0004 --out edge.csv
```

`run` measures every mask in a folder whose coarsest spacing is at most `--max-slice`, one CSV per study, so a run cut short resumes; each CSV carries a stamp of the measuring code, and a study is measured again when the code has changed since. `compare` sets our values beside every row of the paper tables. `phantom`, `thicken` and `bench` are the checks below.

Each vertebra is read in its own frame: z starts on the column's line through the centroids of its whole neighbours and is turned once onto the vertebra's own axis, the bisector of its two end-plates' planes, each plate the body's face toward the neighbouring vertebra (the section on the axis, below); y points to the body, and the canal is the hole the slabs across the vertebra find. The body is the bone in front of the canal's anterior wall, cut along that wall's line as it leans through the canal's full rings, and in the neck clipped at the transverse foramina. Every module's docstring gives its definitions and the failures that shaped them; this note does not repeat them.

## The measures

Per vertebra, 81 keys:

- Body (body.py): anterior, middle and posterior heights read from corner to corner 2.5 mm inside each end-plate's own corners, and Panjabi's posterior height at the wall itself (h_ant, h_mid, h_post_inset, h_post); Genant's ratios (body_index_ant_post, body_index_mid_post); Panjabi's end-plate widths and depths (endplate, endplate_depth, endplate_lower, endplate_lower_depth); the waist's width and depth (body_w_mid, body_d_mid, Eisenstein's mid-waist width and body depth); each end-plate's area, concavity and inclination to the plane square to the posterior wall; the wedge angle; the body's and the vertebra's volumes.
- Canal (canal.py): the least midline depth and where it lies (canal_ap_min, canal_ap_min_share), the depth at the pedicles (canal_ap), the lateral depth (canal_ap_lateral), Eisenstein's lateral-film construction at L1 to L4 (canal_ap_lateral_film), the interpedicular distance at its least and its greatest (interpedicular, interpedicular_max), the canal's width at the pedicles (canal_w), its least and middle areas (canal_area_min, canal_area), and the Torg, Jones and trefoil indices.
- Pedicles (pedicle.py): width, height and area at the isthmus, the transverse and sagittal angles, and the chord a screw would take through bone (Zindrick's), each side and their mean.
- Posterior elements (posterior.py): transverse processes' span, length and height (Panjabi's TPW; Castellvi's 19 mm), the spinous process's length and angle, the laminae's thickness and angle, the facets' axial angles, tropism and the interfacet widths, and the articular processes' apex heights.
- The vertebra's axis: how far its own axis lies from the column's line through its neighbours (axis_offset), how far the axis read again in the turned frame lies from that frame's z (axis_residual), and how far the bisector of the end-plates as the frame's cells read them lies from z (plate_offset).

Per disc, 12 keys (column.py): the disc heights in front, in the middle and behind and their mean; the segmental angles sagittal, coronal and axial between the two end-plates drawn from rim to rim; the slip by Meyerding's corners and as a share of the end-plate's depth; the foramen's height on each side.

Per pelvis, 13 keys (pelvis.py): pelvic incidence, sacral slope and pelvic tilt as the patient lay, the hip axis's width, the acetabula's radii, the intercristal line's level, the transverse processes' gaps to the sacrum and the ilium, and which lumbar vertebra is lowest. Per column, 6 keys: lordosis L1 to S1, kyphosis T4 to T12, the cervical curve C2 to C7, and the coronal Cobb angle with its end vertebrae.

## How accurate it is where the truth is known

The phantoms of [morphometry/tests/phantom.py](../../morphometry/tests/phantom.py) draw lumbar vertebrae whose every measure is fixed by their parameters, on 0.8 by 0.8 by 1 mm voxels with the column tilted 18 degrees and the grid turned 7: a straight column, the same with one part changed at a time (a wedge, concave end-plates, a waist, angled pedicles, a steeper facet and spinous process), a column whose joints open 8 degrees, tilt 4, turn 5 and slip 4 mm, a pelvis, thick slices, and two masks a segmenter gets wrong (two labels swapped, a column cropped). The 20 tests require linear measures within 0.75 mm, angles within 1.5 degrees (3 for the spinous and facet angles), areas within 4 per cent and the slip within 1.5 mm; all 20 pass (`python -m unittest morphometry.tests.test_morphometry`, 281 s).

On 2.5 mm slices, as most of ENHANCE.PET is cut, `bench --slice 2.5` over 22 tilts and turns of the straight phantom gives:

| measure | mean error | standard deviation | largest | readings |
| --- | ---: | ---: | ---: | ---: |
| h_ant | +0.72 mm | 0.87 | 2.25 | 22 |
| h_mid | +0.60 mm | 1.18 | 2.38 | 22 |
| h_post_inset | +0.61 mm | 0.85 | 2.21 | 22 |
| endplate_incl | -0.07 degrees | 1.27 | 3.22 | 22 |
| endplate_lower_incl | +0.15 degrees | 1.50 | 3.52 | 22 |
| disc_h_ant | -0.82 mm | 1.03 | 2.52 | 44 |
| disc_h_mid | -0.58 mm | 0.95 | 2.45 | 44 |
| disc_h_post | -0.59 mm | 0.85 | 2.40 | 44 |

Drawn rim to rim, an end-plate's inclination scatters by 1.3 to 1.5 degrees on these slices, where the plane through the plate's middle had scattered by 3.2 to 3.5 (largest 9.5).

So heights and discs gain or lose about a quarter of a slice on thick slices, with errors up to about one slice. The comparison with the papers is therefore made on the thin-slice studies only.

## What real masks broke, and what was changed

The first pass over 14 ENHANCE.PET studies, and then an adversarial review of the code (four reviewers by frame, definitions, robustness and the pipeline, each finding checked by a skeptic; 12 confirmed, 27 lower-ranked kept), found these failures, each fixed and each recorded in the docstring of the function that now avoids it:

- The canal's wall line leaned 69 degrees at study 0004's T6, where holes in the body 20 mm in front of the canal counted as canal: the line is now fitted through the canal's full rings only and bounded at 30 degrees.
- Thoracic pedicles read 20 to 30 mm wide: the cut across them took in the rib's head. The pedicle is now the island beside the canal in coronal slabs from the wall back, its axis following the medial wall; 0004's widths now read 6.5 (T3), 6.0 (T7), 8.9 (T11), 10.0 (L1), 9.2 (L3) and 12.4 mm (L4).
- The pedicle's sagittal angle read 3 degrees on a level pedicle and 8 on one pitched 6, the raster's steps: it was the slope of one column's middle a row, and a layer of 1.24 mm over the isthmus rows' 7.5 mm is 9 degrees. Each of the pedicle's top and bottom surfaces is now parted from the scan's own voxel centres under the columns across the isthmus rows, bone from air, by the surface of widest margin (a linear program), and the climb is the mean of the two; over six phantoms on six grids on 1 mm slices every reading whose columns span 5.5 mm or more lies within 1.8 degrees of the truth, but for one of the overhang phantom's at 2.1 and those on a grid within a few degrees of the vertebra's frame, where the posterior wall's slope reads 1.8 to 4.2 degrees off and the angle 2.5 to 3.4 high (body.posterior_wall_slope, to be traced next; the end-plates' inclinations take the same error). The angle is refused where the surfaces that still part the lattice leave it free over 9 degrees, as on every 2.5 mm phantom (10.6 to 33 degrees free), and where the top's and the bottom's climbs differ by more than 5 (pedicle.py's docstring, handoff.md's pass of 30 October).
- L5's anterior height read 15 mm on a body 32 mm tall, the band set at a lip of its lower rim; heights and discs are now read at each end-plate's own corners, which also kept the wedge right on a concave, waisted phantom (2.7 degrees had been read where it is 5.1).
- Lumbar wedges read 11 to 21 degrees where the heights differ by 1 to 4 mm: a concave plate's middle tilts. The plate's line is now drawn rim to rim.
- L5's mid-waist width read 76 mm, the transverse processes' roots included: the width is now taken across the body's mid-depth.
- The T12-L1 disc was never measured, since the level list counts a T13 that ENHANCE.PET's scheme does not have; the slipped vertebra's disc bands missed its corners; Panjabi's depths took a planar wall where the frame leans; a stray piece of a label steered the column's line; a vertebra cut by the volume's edge kept canal and pedicle values; C2's dens was read as an end-plate; a pedicle whose axis could not be read wrote 0-degree angles; the spinous process's principal direction turned vertical on near-square processes; Eisenstein's construction was written outside L1 to L4; the thickening tool thinned columns on the 0.7 mm studies and took 2.5 mm as 2; a dead worker could hang a run; the summary pooled pigs, children and size-selected groups with adults.

Three limits stand: L5's pedicle is fused with the transverse process's root in every row of the masks read (sections of 22 to 26 mm at study 0004, now flagged and not read), most thoracic pedicles span under 5.5 mm front to back so their sagittal angle is not read, and the slabs' canal walls lean half as far as the posterior wall does, a cause in scanimport not found and worked around by reading corners from all the voxels in front of the canal's middle.

## The vertebra's own axis

On 29 October 2026 at 13:45 UTC the owner saw that the axial cut of study 0004's C5 did not run through the vertebra's principal axis, and asked that every measure that needs the axis take it into account. The frame's z was the column's line through the neighbours' centroids, which is the axis of the column at the vertebra and not of the vertebra: over the 228 studies of the run below, the bisector of the end-plates lay a median of 16.7 degrees from that line at C3, 13.3 at C4, 8.9 at C5, 5.4 at C6, 7.4 at C7, 2.4 to 4.6 from T2 to T12 and 18.1 at L5 (the key axis_offset of that run), so in the neck and at L5 the frame cut the body obliquely. Everything read along or across the frame's z depends on it: the heights and the end-plates' widths and depths, the plates' inclinations and the wedge, the waist, the canal's slabs and so its depths, widths and areas, the pedicles' isthmus and angles, the posterior elements' angles, the discs (read along the lower vertebra's z), and the renders' cuts; the volumes alone do not.

Five readings of the vertebra's own axis taken inside the frame were tried on 0004 and set aside, since each moved with the frame it was read in: with the body's voxels fixed once and the frame turned 10 and 20 degrees about x and about y, the bisector of the plates as the frame's cells read them moved by 4 to 19 degrees, a line through the body's layers' centroids by 17 to 47, one through the layers' posterior tenth by 21 to 78, the canal's axis through the slabs' holes stood on fewer than four full rings at many thoracic levels, and the body's least principal direction, which needs no frame, lay 9 to 87 degrees off the column's line and is no axis of a body as wide as it is tall. A reading that needs no frame is in anatomy.plate_face: each end-plate is the body's face toward the neighbouring vertebra, the body's voxels on the label's surface that lie within 15 mm of the neighbour's label and whose outward normal, the smoothed label's gradient, points within 45 degrees of the neighbour's nearest voxel; its plane is the direction of the face's least spread, refitted without the points more than two slices off it; the axis is the bisector of the two planes, or one plate's normal where only one faces a neighbour (flagged), and the column's line is kept, flagged, where no plate faces a neighbour, where the axis lies more than 25 degrees off the line or where the turned frame loses the canal. The frame is turned onto the axis once (anatomy.own_axis), the vertebra read again there, and the axis read again in the turned frame written as axis_residual.

On study 0004 the turn is 21.7 degrees at C3, 14.4 at C4, 17.0 at C5, 11.3 at C6, 5.9 at C7, 5.6 at T1, 0 to 4 through the thorax, 4 to 7 at L1 to L4 and 16.7 at L5, and the residual after the turn is at most 2.2 degrees at every level (0.0 to 0.6 from T1 to L1), so the reading holds still where every in-frame reading moved; the sagittal and axial cuts of C3, C5 and L5 then run square to the body. C2's lower plate alone faces a neighbour and lies 35 degrees off its column line, so C2 keeps the column's line with a flag. The 20 phantom tests pass on the new frame (the straight phantom's L3 turns under 1.5 degrees, its heights, areas and angles hold), the reading taking 0.1 to 1.4 s a vertebra. The bisector the frame's cells read (plate_offset) still lies 12 to 22 degrees off the turned frame at C3, C4, C5 and C7, which says that reading is unusable in the neck, not that the frame is wrong: the uncinate processes above and the lip below are the extremes its cells take.

The change moves the code's stamp to 81e732f142d3aa16, so every study is measured again; the run below, the renders, the thick-slice and canal-shape readings, the phantom sweep and the comparison with the papers all stand on the column-line frame until it lands (handoff.md says where it stands). The mask-edge and disc readings of the three CTs were made in the column-line frame too and are not read again without the CTs, which need the owner's word.

## The 229 thin-slice studies of ENHANCE.PET

The run measured every study whose coarsest spacing is at most 1.25 mm, 229 of them, by the code at bordercall b90675f (stamp 7bda317295ef9f5b, the column-line frame; the frame of the section above supersedes it and its run is under way), the last 108 from a frozen worktree after the pause. The rows are in the project's files under gold3-ct/morphometry/run229/ with their sha256, never in git; the comparison, compare-229.csv, is aggregates only and is in records/morphometry-2026-10-29/. Against adult people only (the summary leaves out another species, children, groups chosen by size, a disease and worked examples), with each paper's technique set apart, each cell gives the median of the rows' differences in units of the paper's standard deviation, then the median difference in mm or degrees, then the rows and papers:

| our key | CT | direct on bone | film | MRI | quoted or pooled |
| --- | --- | --- | --- | --- | --- |
| endplate | +4.72, +9.4 (54, 5) | +2.10, +8.8 (17, 2) |  | +1.67, +6.6 (2, 1) | +1.52, +7.2 (4, 1) |
| endplate_lower | +5.46, +10.0 (49, 5) | +2.49, +7.1 (17, 2) |  | +2.11, +8.7 (3, 1) |  |
| endplate_depth | +4.40, +6.1 (40, 4) | +0.94, +2.1 (12, 1) | +0.62, +1.6 (12, 2) | -0.26, -0.7 (2, 1) | -0.32, -1.7 (2, 1) |
| endplate_lower_depth | +2.87, +4.7 (44, 4) | -0.10, -0.3 (12, 1) | +0.11, +0.3 (14, 2) | -0.50, -1.4 (3, 1) |  |
| h_ant | +2.62, +4.2 (58, 5) |  | +2.47, +4.4 (23, 2) |  |  |
| h_post | +0.71, +1.7 (58, 5) |  | +0.81, +1.7 (23, 2) |  |  |
| h_mid | +1.22, +2.1 (31, 3) |  |  |  |  |
| body_w_mid | +0.62, +2.2 (5, 1) |  |  |  |  |
| body_d_mid | +1.18, +3.4 (5, 1) |  |  | +1.61, +5.2 (5, 1) |  |
| disc_h_ant | -0.12, -0.2 (75, 2) | -3.72, -3.0 (12, 1) | -6.06, -2.6 (12, 1) |  |  |
| disc_h_mid | -0.24, -0.4 (75, 2) | -3.33, -2.6 (12, 1) |  |  |  |
| disc_h_post | -0.78, -0.8 (75, 2) | -4.40, -2.7 (12, 1) | -2.88, -1.2 (12, 1) |  |  |
| foramen_h | -0.46, -0.8 (63, 3) |  |  |  |  |
| canal_w | -0.89, -2.0 (20, 4) |  |  |  |  |
| canal_ap | +1.10, +1.7 (48, 6) |  |  | -0.79, -1.6 (5, 1) |  |
| canal_area | +3.73, +49.8 mm2 (32, 3) |  |  |  |  |
| interpedicular |  |  | -2.08, -4.2 (32, 3) |  | -2.23, -6.0 (5, 1) |
| interpedicular_max | +2.48, +2.5 (27, 2) |  |  |  |  |
| pedicle_w | +1.43, +2.6 (112, 8) | +1.65, +2.6 (39, 2) | +0.92, +1.9 (24, 3) |  | +1.62, +2.6 (47, 2) |
| pedicle_h | +1.81, +3.8 (80, 8) | +1.17, +2.4 (37, 2) | +0.20, +0.4 (24, 3) |  | +1.38, +2.0 (37, 2) |
| pedicle_chord | +1.92, +7.6 (47, 5) | +0.74, +2.5 (9, 1) | +1.08, +4.9 (14, 2) |  | +0.49, +2.8 (37, 2) |
| pedicle_angle_transverse | -0.87, -1.9 (51, 5) | -1.50, -4.2 (15, 1) | -0.58, -1.7 (5, 1) |  | -0.32, -1.6 (37, 2) |
| pedicle_angle_sagittal | +3.88, +8.5 (32, 2) | +13.95, +25.3 (15, 1) | -1.04, -2.7 (11, 1) |  | +4.77, +23.4 (17, 1) |
| transverse_width | +5.20, +16.2 (22, 1) |  |  |  |  |
| spinous_length | -4.31, -11.7 (22, 1) |  |  |  |  |

Figure papers.png in records/morphometry-2026-10-29/figures/ draws ten of these by level, ours beside the papers with the most levels. What the pattern says, and what it does not:

- The width at the end-plate's rim reads 9.4 mm wide against five CT papers where the waist's width reads 2.2 mm wide, on the same bodies, and from T2 to L5 the excess holds at every level (62.2 against 49.0 mm at L5). The renders put the rim width on the ring's flare and the lips at its edge (L3, below); the masks are not the cause (the mask-edge test), so osteophytes of a PET clinic's adults and the papers' narrower definitions remain. In the neck the width is mostly the body's cut: where a foramen transversarium is not found closed, the body is cut a millimetre beyond the canal's side walls (anatomy.clip_to_foramina), so it reads about the canal's width, 25 to 29 mm, where a cervical body is 15 to 21; the cut fell back so at C3 to C6 in 89 to 166 of the 228 studies and at C7 in 186. T1 stands out of its neighbours (40.2 mm against 25.1 at C7 and 31.2 at T2); study 0004's T1 reads 33.1 mm on a body its coronal cut shows whole and alone, so that render does not explain the median, and the studies at the top of T1's spread are the next to draw.
- The heights read 4.2 mm tall in front and 1.7 behind against CT papers, but the papers disagree with each other by as much (figure papers, A and B): at T8 Busscher 2010's CT of human cadavers gives 20.1 mm against our 21.1, where Kunkel 2011's contact radiographs give 17.0 and Tan 2004's ten Singapore cadavers 16.1; at L3 Busscher gives 28.7 and Gilad 1985's films 27.9 against our 30.2, Tan 21.4. Tan 2004's bodies are the smallest of any series and its standard deviations the narrowest, and it weighs in nearly every comparison of the body. The masks put at most half a millimetre into a height.
- The discs: against the lumbar CT papers the mid-disc height reads 0.4 mm short; against Kunkel 2011's cadaver sections in the neck and thorax 2.6 mm short. Of that, 0.5 mm is the masks taking in the disc and 1.35 mm the plate rule (the disc in the CT, below), and the rest is these patients: the CTs show their cervical discs 3.2 mm tall at the middle, where Kunkel's sections give 5.6.
- The interpedicular distance reads narrow against films (4.2 mm), the narrowing growing from L3 to L5 (20.0 against 25.9 mm at L3, 18.5 against 30.0 at L5) and in the neck (19.5 against 28.8 at C4), while L1, L2 and the thorax read 2 to 4 mm narrow, about what a film's magnification gives. The run reads it across the canal's middle, front to back, where the papers read it between the pedicles' medial walls, at the canal's front corners. Where the canal is round the two agree; where it is a trefoil, at L4 and L5, or a triangle, in the neck, the canal's widest in its front half, where the pedicles join the body, is 3.4 to 9.8 mm wider than at its middle in all three studies read (canal-shape.csv). The fix reads the width at the pedicles' own place front to back.
- The pedicle's width in the neck reads 12.4 to 13.6 mm from C3 to C6 against 4.5 to 5.2 (Tan 2004), and its height 12.8 to 13.8 against 6.0 to 6.8: the coronal island at a cervical pedicle's isthmus takes in more than the pedicle, likely the lateral mass and the bar behind the transverse foramen (C5, below). C7 and T1 read 16.2 and 18.1 mm wide; at study 0004's T1 the isthmus cuts are islands 13 to 14 mm square, about twice the papers' 7.7. None of these is used. From T3 to L3 the widths sit 1.6 to 3.5 mm over the papers' median means, T2 and L4 4.3 and 4.8, and L5's island takes in the transverse process's root (22.3 against 15.2 mm), the limit stated above.
- The canal's depth at the pedicles reads 3 to 4 mm deep in the thorax against Tan 2004, the one CT paper there, and within a millimetre of the lumbar papers; its area takes in the lateral recesses, which the CT papers' outlines along the medial pedicle borders leave out.
- Two keys differ by definition, not by measurement. Our spinous length runs from the canal's posterior wall at the midline to the tip; the dry-bone paper's runs from the tip to about the upper end-plate's centre, and the pool that names the laminar base gives 60 to 66 mm, nearer that longer length than ours. The transverse width has one CT paper, a series of ten Singapore cadavers whose bodies are the smallest of all the series (an L3 anterior height of 21.4 mm), whose standard deviations (under 1 mm for an end-plate's width at L3 and L4) are smaller than any other series gives.
- The pedicle_angle_sagittal row is the run's old construction, the slope of one column's middle a row, which stepped with the raster (what real masks broke, above), and is not used; the thoracic rows read tens of degrees over. The reworked angle is read again when the run is made again on the grid.

Medians at L3 over the 228 studies, as a sense of scale: end-plate width 51.2 mm, end-plate depth 36.3, the waist 43.3 wide and 33.7 deep, anterior height 30.2, posterior 28.3, body volume 39,880 mm3, transverse span 93.0, least canal depth 13.7, canal width 22.4, interpedicular distance 20.2, pedicle width 11.8, and the L3-L4 disc 9.2 mm at its middle.

## Where the mask's surface lies against the bone

The package [maskedge/](../../maskedge/) reads, at up to 400 points per region of each vertebra (the two end-plates, the body's lateral, anterior and posterior walls at its middle three fifths, and the arch), the CT along the surface's outward normal, and finds the bone's half-maximum edge, half-way between the cortex's peak just inside and the level just outside, against the mask's own surface on the same line. A point is read only where nothing labelled lies 0.6 to 3.5 mm beyond it and the peak stands 150 HU or more above the outside. A height then reads tall by the sum of the two end-plates' offsets, a disc short by the same, a width by twice the lateral wall's.

```
python -m maskedge measure --ct 0004_ct.nii.gz --labels 0004.nii.gz --scheme enhance --study 0004 --out edge.csv
python -m maskedge summary --rows edge.csv
```

On the phantom with a CT drawn from the same shapes (each voxel the mean of 27 points, a 0.8 mm cortex at 800 HU over cancellous bone at 200 and soft tissue at 40, blurred by 0.45 mm across and 0.55 along the column), the exact mask reads +0.14 to +0.20 mm in every region, a mask grown by one voxel 0.74 to 1.04 mm further in and one shrunk by a voxel 0.82 to 1.01 mm further out, each within 0.1 mm of how far a one-voxel growth moves that surface (8 tests, `python -m unittest discover -s maskedge/tests -t .`, 43 s). On the owner's word of 29 October 2026, 12:12 UTC, three CTs were read from the public bucket into the container, each at its listed size (0004 271,621,479 bytes, 1 mm slices; 0006 411,250,425, 0.7 mm; 0010 271,977,076, 1 mm; 954,848,980 in all), measured and deleted; nothing went to the grid. Their sha256 and the per-vertebra rows (aggregates, no image) are in the project's files under gold3-ct/morphometry/maskedge-2026-10-29/. Each study gave 23 vertebrae, C2 to L5, in every region; 65 to 80 per cent of the sampled points showed an edge (median per region), the cortex standing a median of 278, 416 and 314 HU above what lay outside. Over the 69 vertebrae, the median of the vertebrae's medians:

| region | vertebrae | median offset (mm) | quartiles |
| --- | ---: | ---: | --- |
| upper end-plate | 69 | +0.72 | -0.21 to +0.93 |
| lower end-plate | 69 | -0.34 | -0.77 to +0.23 |
| lateral wall | 69 | -0.07 | -0.30 to +0.02 |
| anterior wall | 69 | +0.13 | -0.05 to +0.26 |
| posterior wall | 69 | -0.21 | -0.43 to -0.04 |
| arch | 69 | -0.34 | -0.41 to -0.25 |

A positive offset is bone beyond the mask. What they make of a measure taken on the masks: a height 0.37 mm short, a disc 0.37 mm long, a width 0.14 mm wide, a depth 0.08 mm wide; study by study the height reads -0.23, +0.29 and -0.15 mm off and the width +0.59, +0.14 and +0.04. The phantom's +0.14 to +0.20 mm, the half-maximum edge's own outward lean on a 0.8 mm cortex, would make each wall's offset that much smaller and each width a few tenths wider; a blurrier low-dose CT leans further, which this test cannot measure. Either way the masks explain at most half a millimetre of the 2 to 9 mm by which our heights, depths and widths exceed the papers' CT means.

The end-plates' two offsets do not cancel within a study: the bone's half-way point between its two plates, (upper less lower) over two, lies above the mask's by +0.25 to +0.98 mm at every level of 0004 and +0.43 to +1.19 mm of 0010, and below it by 0.02 to 1.29 mm at every level of 0006, the 0.7 mm study. Each mask is displaced along the column against its CT, by a median of 0.63 mm (0004), 0.44 mm (0006) and 0.77 mm (0010) over the levels, about half a slice, one way or the other by study. A mask made on a coarser grid and carried back by nearest neighbour would do this, by up to half the coarser voxel; that is a guess, not tested. No measure here is taken across the two, so none is moved, but anything that sets a mask on its CT's intensities (density, a CT-based reading of the end-plate) would be.

### The disc in the CT

The edge reading skips a point with another label within 3.5 mm of it, so it could not read an end-plate where two masks nearly meet, which is where a mask taking in the disc would show. maskedge/disc.py reads each disc instead along 25 lines parallel to the column's line in the frame of the vertebra below, through the middle three fifths of that body's width and depth: the masks' gap is the distance between the two labels along the line, and the CT's disc is the distance between the two half-maximum crossings either side of the CT's least value near the masks' junction, each half-way from that side's cortex to the disc. A line counts where both cortices stand 150 HU or more above the disc, and a disc where eight or more lines count.

```
python -m maskedge disc --ct CT.nii.gz --labels 0004.nii.gz --scheme enhance --study 0004 --out disc.csv
python -m maskedge disc-summary --rows disc.csv
```

On the phantom's 10 mm discs the exact masks leave 9.6 mm and the CT shows 9.5 (the labels' voxels put each surface within half a voxel of the truth), a mask grown by one voxel narrows the gap by 0.9 mm and one shrunk widens it by as much, and the CT's reading does not move (5 tests, `python -m unittest maskedge.tests.test_disc`, 76 s). The phantom's posterior elements collide below a 10 mm disc, so no thinner disc is drawn. The three CTs were read again for this on the owner's word of 12:12 UTC, the same files at the same sizes and sha256, and deleted after. Over the discs read on eight lines or more (records/morphometry-2026-10-29/disc-ct.csv, figure disc.png):

| region | discs | masks' gap (mm) | CT's disc (mm) | masks' gap less CT's disc (mm) | quartiles |
| --- | ---: | ---: | ---: | ---: | --- |
| cervical | 14 | 2.60 | 3.15 | -0.47 | -0.66 to -0.34 |
| thoracic | 16 | 3.00 | 3.48 | -0.11 | -0.62 to +0.19 |
| lumbar | 10 | 7.90 | 7.46 | +0.31 | +0.04 to +0.44 |

So the masks take in about half a millimetre of each cervical disc, a tenth of each thoracic one, and leave each lumbar disc 0.3 mm wide, the same few tenths the edge test found. Most of the thoracic discs of study 0010 and a few of 0004's showed too little contrast to count. The CTs themselves show these patients' cervical discs 3.2 mm tall at the middle and their thoracic discs 3.5, where Kunkel 2011's sections give 5.6 at C7-T1 and 4.4 to 6.7 down the thorax.

The run's own mid-disc height (disc_h_mid) on the same discs reads a median of 1.35 mm less than the masks' gap in the neck (quartiles -1.75 to -0.88), 0.87 in the thorax and 0.32 in the lumbar spine. Its rule takes each plate's outermost point within a 3 by 6 mm band, carried along a plane fitted to the plate, where the lines here take the median gap; on a thin disc between irregular plates the outermost points stand proud of the typical one by a large share of the disc. With the masks' half millimetre, the run's cervical discs read 1.7 mm short of the CT, and they are not used until the rule reads a typical surface.

## Seeing each measure where it was taken

The package [morphoview/](../../morphoview/) draws a vertebra's measures on its own mask, cut in four planes of its frame: sagittal through the body's middle across, coronal through the body's mid-depth, coronal through each pedicle's isthmus (the right at its isthmus, the left at its own, since the two can lie millimetres apart front to back), and axial through the pedicles' centre. Every line is built again from the measuring modules' own functions, its ends where the measure takes them, and the value its construction gives is set beside the value in the run's rows; a line that differs by more than the rows' rounding (four decimals) and a millionth of the value is not drawn and is listed as withheld. A length's ends are the line's ends; a disc is the gap along the lower vertebra's axis between the two plates' bands; a pedicle's width and height are drawn on the isthmus slab nearest the median they are taken over, the width then times the cosine of the axis's transverse angle; the wedge is the two end-plates drawn rim to rim.

```
python -m morphoview render --labels 0004.nii.gz --scheme enhance --study 0004 --levels L3 T8 C5 --rows rows.csv --out DIR
```

On the phantom every line of L3 and its two discs is drawn, and each length's ends lie on the solid's true surface, bone a step of 0.8 mm inward and none a step outward (canal walls the other way round), which 10 tests hold (`python -m unittest discover -s morphoview/tests -t .`, 36 s). On study 0004 all 150 lines of C5, T1, T8, L3, L4 and L5 matched the run's rows (records/morphometry-2026-10-29/renders/). What the drawings show that the numbers did not:

- At C5 the masks of C4, C5 and C6 nearly touch, so the three disc heights read -0.7 to 1.6 mm; over the 228 studies the mid-disc height reads a median of 1.6 to 1.9 mm from C4-C5 to C5-C6 and 2.8 at T6-T7, where L3-L4 reads 9.2. The disc test in the CT (above) settles it: the masks take in half a millimetre, the run's plate rule 1.35, and the CTs' own discs are 3.2 mm.
- C5's pedicle chord reads 6.25 mm on the right and nothing on the left: the right axis turns 61 degrees from the sagittal plane and the march along it leaves bone after 6.25 mm, and the left pedicle spans too little front to back to give an axis at all (its row's flag). Cervical chords are not used.
- L3's lower end-plate width (47.6 mm) runs from rim lip to rim lip, 9 mm wider than the waist (38.3 mm) a few millimetres above it. The full run shows the same excess at every level from T2 to L5 against the CT papers (the comparison, above): the slab Panjabi's width is read in takes in the ring's flare and any lip at its edge.
- L3's left pedicle chord (61.8 mm) is 14 mm longer than the right (47.5 mm): the left axis climbs 10.5 degrees where the right climbs 1.5, so it leaves the axial cut and runs into the posterior elements higher up, and the chord's posterior end is not the same landmark on the two sides.
- T8's lower end-plate width (36.6 mm) is drawn past the body's outline in the coronal cut: it is read across a slab front to back that holds bone at the rim the cut through the body's mid-depth does not, 8.8 mm wider than the waist (27.8 mm). Its pedicles read 7.6 and 5.9 mm wide and 14.7 and 14.1 tall, and its discs 1.8 to 3.0 mm.
- L4's lower end-plate depth (34.5 mm) runs about 5 mm behind the posterior wall's line at the lower plate, where the upper (26.5 mm) ends at the wall (the drawn lines' ends in render-0004-L4.csv). Whether that is a lip at the back of the rim or other bone the band takes in is not yet told apart; it is one body, and the next renders are to say whether it is common.
- L5's interpedicular distance (23.4 mm) is drawn across the canal's middle front to back, behind the pedicles, where the trefoil canal narrows; in the canal's front half, between the pedicles, it is 27.6 mm wide. This is the construction the comparison faults at L4 and L5 (above), and canal-shape.csv measures it in three studies.
- L5's pedicle widths (19.8 and 22.8 mm) and heights (33.3 and 18.8 mm) are drawn on islands that take in the transverse process's root, and its anterior height (37.3 mm) and wedge (19.2 degrees) on a body whose lower end-plate rises steeply behind; the L5 rows are to be read with that in mind.

## The survey

The 43 papers of the clinical reread (bordercall PR 21, one note per paper) gave the definitions: Panjabi's for the body, end-plates, pedicles, canal, processes and facets; Eisenstein's for the least canal depth, the greatest interpedicular distance, the mid-waist and his lateral-film construction, which puts the canal's posterior limit on the line from the superior articular process's apex to the inferior's inverted apex, opposite the upper half of the body; Genant's and Teijin's corner heights and ratios; Zindrick's pedicle chord; Meyerding's slip; Castellvi's 19 mm. Their means, 4,476 rows from 39 papers, are the paper tables' series.csv (bordercall branch claude/project-thread-adplcz at f067734), which `compare` reads.

Patented approaches that measure what a mask can show, none of which publishes per-case truth: Teijin US 5,224,035 (central and rim heights and their ratios, the wedge, biconcave and crush types); Hologic US 5,850,836 (posterior, middle and anterior heights and the wedge indices); Siemens US 11,074,688 (six sagittal points per vertebra and height loss against neighbours, AI-Rad Companion, FDA K222361) and US 10,588,588 (holder not confirmed); the Penn family US 2022/0237779 and US 12,450,731 (anterior, middle and posterior heights from landmarks); Hitachi US 9,594,975 (canal asymmetry and area ratios); Theseus AI US 11,488,717 (canal and foraminal areas); 25SEGMENTS US 12,616,522 (the minimum transverse pedicle width plane and screw trajectory); Holo Surgical EP 3470006 (segmentation of the spinous process and laminae). The implementation here follows the clinical definitions, which these patents also follow; the patents add no measure the definitions lack.

Open data with measured truth, and what each could test:

- VerSe 19 and 20 with the readers' Genant grades (Riedel 2026, OSF node 4skx2): 3,548 thoracic and lumbar vertebrae of 331 patients, graded 0 to 3 by an attending neuroradiologist and a resident independently, 116 of them (3.3 per cent) settled by consensus. The masks are VerSe's public 473 files ending _seg.nii.gz, 1,428,261,472 bytes, already listed and checked in the thread "Read the rest of VerSe's masks" (/mnt/project-files/gold3-ct/verse-read-2026-10-29/LISTING.json); the reference table, fracture_data/Genant_Fractures_thoracolumbar_reference.csv, is 11,823 bytes (osf.io/download/zy68u/). This is the one test of our heights against human reads on masks we did not make; it needs a container with full network access, since this one is refused OSF.
- CTLungCa-500 with six points per vertebra (anchor-free-genant, 3,565 vertebrae of 100 studies, CC BY-NC 4.0) and Pisov 2020's heights: per-vertebra heights, but on CTs with no released masks, so a test there needs new segmentations, which the owner's rule rules out.
- xVertSeg Data1 (Genant grade and type per lumbar level, with masks, 15 CTs; its licence asks for written permission beyond the challenge), the Ashish 2023 dry-bone caliper table (54,754 bytes, CC BY 4.0, figshare 21307917: lamina, facet, pars and interpedicular values per vertebra) and the SVAD subadult canal diameters (Zenodo 6342097) test distributions, not cases.
- No open CT set gives per-case canal, pedicle or facet dimensions measured by people.

Open code that claims these measures: Swin-X2S's morphometry (MIT, its morphometry folder and licence 99,924 bytes at 3f8b8ed: spinous length and angle, anterior and posterior heights, end-plate lengths, canal length) and naamii's xrayto3D-morphometry, which it copies; TPTBox's spinestats (Apache-2.0, needs SPINEPS's subregions); TotalSegmentator's spine report (heights at 15, 50 and 85 per cent of the depth); Spine-Morphology-Analyzer (no licence shown; synthetic spines with a measurements.csv); pedicle-screw-simulator (MIT, the isthmus as the least coronal section, as here); Comp2Comp and HealthiVert-GAN for heights; the Spinal Cord Toolbox for canal sections on MRI. None comes with measured truth; each is a second implementation to check ours against on the same mask.

What masks cannot give: cortical thickness and the inner pedicle width, density and anything read from intensities, the disc's own height where the vertebra labels take in the end-plate's cartilage, ligaments, and the posterior limit of the canal where the ligamentum flavum, not bone, bounds it.

## What comes next

In the order the findings above ask for them; handoff.md, beside this note, says where each piece of work stands.

- The run on the vertebra's own axis (the section above): its rows into the project's files, the comparison with the papers, the renders, the thick-slice and canal-shape readings and the phantom sweep made again, in records/morphometry-2026-10-29-axis/, and the shift of each measure between the two frames tabled by region, so that what the axis changed is on record.
- The interpedicular distance read between the pedicles at their own place front to back, not across the canal's middle (canal-shape.csv). It changes the code's stamp, so every study is measured again, about an hour and a half here.
- A cervical pedicle that keeps out the lateral mass and the bar behind the transverse foramen, and the same at C7 and T1; L5's pedicle without its transverse process's root.
- The disc's plate rule reading a typical surface, not the outermost point in its band, and the neck's body cut where no transverse foramen is found closed.
- Renders of the studies at the top of T1's end-plate spread, and of L4's lower end-plate depth in more studies; the end-plate width read inside the rim's lips as the CT papers read it, beside Panjabi's.
- The VerSe test of the heights against the readers' grades, when the helper thread brings its rows, never pooled with ENHANCE.PET.
- The published masks of 1347, 1283 and 1134 against their repaired copies, at 3 mm.
