# Morphometrics from the gold tier 3 CT masks

Thread "Extract morphometrics from gold tier 3 CT" of the claude.ai project symphony_4, 29 October 2026, from the owner's message of 02:12 UTC that day: start a survey of the morphometrics that can be taken programmatically from the gold tier 3 data, using patented validated approaches and those of the clinical reread (Eisenstein's posterior limit of the canal among them), implement and test them on the masked CTs, and look for test cases with ground-truth measurements, open datasets and code to compare with and reproduce. Confidential, like everything in bordercall: nothing here goes to a public place. No paper's text is quoted; the papers' methods are described in our own words and their values come from the paper tables (series.csv, below). No mask, CT or per-study row is in git: the rows stay in the project's files, and only aggregates are written here.

## The result in brief

Paused on the owner's priorities of 29 October 2026, 12:06 UTC, with the thin-slice run part way: 121 of the 229 thin-slice ENHANCE.PET studies are measured, and the first 51 are set against the papers (handoff.md says how to carry on). On the phantoms every measure lands within its tolerance, and on 2.5 mm slices heights and discs move by about a quarter of a slice. Against the papers' adult means the masks read the bone larger: the end-plate widths by a median of 9 mm against five CT papers, the anterior heights by 4 to 5 mm, the end-plate depths by 6 mm, while the discs read 0.5 mm short against CT papers, and the foramen's height and the canal's width at the pedicles sit within a paper's spread in 60 to 76 per cent of rows. It is not the masks standing off the bone: on three ENHANCE.PET CTs read on the owner's word (12:12 UTC), the masks lie on the bone's own edge to within a few tenths of a millimetre, so a height reads 0.37 mm short, a disc 0.37 mm long and a width 0.14 mm wide from the masks, against the 2 to 9 mm differences from the papers (maskedge/, below). What is left is a larger population, osteophytes at the rims and the papers' definitions. The same CTs show each mask displaced along the column against its CT, by a median of 0.63, 0.44 and 0.77 mm over the levels of the three studies, one way in two of them and the other way in the third, which moves no measure taken within a vertebra.

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

Each vertebra is read in its own frame: z is the column's line through the centroids of its whole neighbours, y points to the body, and the canal is the hole the slabs across the vertebra find. The body is the bone in front of the canal's anterior wall, cut along that wall's line as it leans through the canal's full rings, and in the neck clipped at the transverse foramina. Every module's docstring gives its definitions and the failures that shaped them; this note does not repeat them.

## The measures

Per vertebra, 79 keys:

- Body (body.py): anterior, middle and posterior heights read from corner to corner 2.5 mm inside each end-plate's own corners, and Panjabi's posterior height at the wall itself (h_ant, h_mid, h_post_inset, h_post); Genant's ratios (body_index_ant_post, body_index_mid_post); Panjabi's end-plate widths and depths (endplate, endplate_depth, endplate_lower, endplate_lower_depth); the waist's width and depth (body_w_mid, body_d_mid, Eisenstein's mid-waist width and body depth); each end-plate's area, concavity and inclination to the plane square to the posterior wall; the wedge angle; the body's and the vertebra's volumes.
- Canal (canal.py): the least midline depth and where it lies (canal_ap_min, canal_ap_min_share), the depth at the pedicles (canal_ap), the lateral depth (canal_ap_lateral), Eisenstein's lateral-film construction at L1 to L4 (canal_ap_lateral_film), the interpedicular distance at its least and its greatest (interpedicular, interpedicular_max), the canal's width at the pedicles (canal_w), its least and middle areas (canal_area_min, canal_area), and the Torg, Jones and trefoil indices.
- Pedicles (pedicle.py): width, height and area at the isthmus, the transverse and sagittal angles, and the chord a screw would take through bone (Zindrick's), each side and their mean.
- Posterior elements (posterior.py): transverse processes' span, length and height (Panjabi's TPW; Castellvi's 19 mm), the spinous process's length and angle, the laminae's thickness and angle, the facets' axial angles, tropism and the interfacet widths, and the articular processes' apex heights.
- The vertebra's axis offset, the angle between the column's line and the bisector of its end-plates.

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
- L5's anterior height read 15 mm on a body 32 mm tall, the band set at a lip of its lower rim; heights and discs are now read at each end-plate's own corners, which also kept the wedge right on a concave, waisted phantom (2.7 degrees had been read where it is 5.1).
- Lumbar wedges read 11 to 21 degrees where the heights differ by 1 to 4 mm: a concave plate's middle tilts. The plate's line is now drawn rim to rim.
- L5's mid-waist width read 76 mm, the transverse processes' roots included: the width is now taken across the body's mid-depth.
- The T12-L1 disc was never measured, since the level list counts a T13 that ENHANCE.PET's scheme does not have; the slipped vertebra's disc bands missed its corners; Panjabi's depths took a planar wall where the frame leans; a stray piece of a label steered the column's line; a vertebra cut by the volume's edge kept canal and pedicle values; C2's dens was read as an end-plate; a pedicle whose axis could not be read wrote 0-degree angles; the spinous process's principal direction turned vertical on near-square processes; Eisenstein's construction was written outside L1 to L4; the thickening tool thinned columns on the 0.7 mm studies and took 2.5 mm as 2; a dead worker could hang a run; the summary pooled pigs, children and size-selected groups with adults.

Three limits stand: L5's pedicle island takes in the transverse process's root (widths near 21 mm), most thoracic pedicles span under 5.5 mm front to back so their sagittal angle is not read, and the slabs' canal walls lean half as far as the posterior wall does, a cause in scanimport not found and worked around by reading corners from all the voxels in front of the canal's middle.

## The 229 thin-slice studies of ENHANCE.PET

The run is stopped at 121 of the 229 (the container restarted at 08:52 UTC and the thread then paused); the rows are in the project's files under gold3-ct/morphometry/run229-partial/, never in git, measured by the code at bordercall b90675f (stamp 7bda317295ef9f5b), so a `run` with the same `--out` measures only the 108 left. The comparison below is the interim one over the first 51 studies, against adult people only (the summary leaves out another species, children, groups chosen by size, a disease and worked examples), with each paper's technique set apart. Each cell gives the median of the rows' differences in units of the paper's standard deviation, then the median difference in mm or degrees, then the rows and papers:

| our key | CT | direct on bone | film | MRI | quoted or pooled |
| --- | --- | --- | --- | --- | --- |
| endplate (width) | +4.78, +9.0 (54, 5) | +2.12, +8.9 (17, 2) | | +1.72, +6.8 (2, 1) | +1.56, +7.4 (4, 1) |
| endplate_depth | +4.16, +6.0 (40, 4) | +1.30, +2.6 (12, 1) | +0.78, +1.8 (12, 2) | -0.12, -0.3 (2, 1) | |
| h_ant | +2.69, +4.3 (58, 5) | | +2.71, +4.6 (23, 2) | | |
| h_post | +0.79, +1.8 (58, 5) | | +1.05, +1.7 (23, 2) | | |
| body_w_mid | +0.66, +2.3 (5, 1) | | | | |
| disc_h_ant | -0.26, -0.5 (75, 2) | -3.75, -3.2 (12, 1) | -6.38, -2.9 (12, 1) | | |
| disc_h_post | -1.02, -1.1 (75, 2) | -4.50, -2.9 (12, 1) | -3.38, -1.4 (12, 1) | | |
| foramen_h | -0.45, -0.8 (63, 3) | | | | |
| canal_w | -0.61, -1.4 (20, 4) | | | | |
| canal_ap | +1.41, +2.2 (48, 6) | | | -0.55, -1.1 (5, 1) | |
| canal_area | +3.93, +57 mm2 (32, 3) | | | | |
| interpedicular | | | -1.86, -3.7 (32, 3) | | -1.97, -5.3 (5, 1) |
| pedicle_w | +1.33, +2.4 (112, 8) | +1.61, +2.4 (39, 2) | +0.85, +1.9 (24, 3) | | +1.61, +2.6 (47, 2) |
| pedicle_h | +1.75, +3.8 (80, 8) | +1.12, +2.3 (37, 2) | +0.15, +0.3 (24, 3) | | +1.30, +1.8 (37, 2) |
| pedicle_angle_transverse | -0.79, -1.7 (51, 5) | -1.44, -3.0 (15, 1) | -0.53, -1.6 (5, 1) | | -0.53, -1.6 (37, 2) |
| pedicle_angle_sagittal | +4.80, +12.8 (28, 2) | +12.18, +25.3 (12, 1) | +2.27, +4.5 (11, 1) | | +5.22, +24.1 (13, 1) |
| transverse_width | +5.24, +16.6 (22, 1) | | | | |
| spinous_length | -4.23, -11.7 (22, 1) | | | | |

What the pattern says, and what it does not:

- The width at the end-plate's rim reads 9 mm wide where the waist's width reads 2.3 mm wide, on the same bodies against CT papers. A mask follows bone, and these are adults of a PET clinic, so marginal osteophytes at the rims are a likely part of it; it is not tested.
- Heights read 2 to 5 mm tall and discs 0.5 to 3 mm short at once, which is what a mask standing off the bone at each end-plate would give, and also what a larger population and thinner degenerate discs would give. The mask-edge test tells the first apart.
- Two keys differ by definition, not by measurement. Our spinous length runs from the canal's posterior wall at the midline to the tip; the dry-bone paper's runs from the tip to about the upper end-plate's centre, and the pool that names the laminar base gives 60 to 66 mm, nearer that longer length than ours. The transverse width has one CT paper, a series of ten Singapore cadavers whose bodies are the smallest of all the series (an L3 anterior height of 21.4 mm), whose standard deviations (under 1 mm for an end-plate's width at L3 and L4) are smaller than any other series gives.
- The canal's area takes in the lateral recesses, which the CT papers' outlines along the medial pedicle borders leave out; its depth at the pedicles reads 2 mm deep against CT, its least depth 1.6 mm shallow against bone.
- The interpedicular distance reads 3.7 mm narrow against films, which magnify; there is no CT paper for it among the 51 studies' rows.
- Thoracic pedicles' sagittal angles are not right (T6 59.7 degrees, T12 36.5 against tens of degrees less), and L5's pedicle width takes in the transverse process's root (21.4 mm): both are the limits stated above, and neither is used.

Medians at L3 over the first studies, as a sense of scale: end-plate width 50.8 mm, end-plate depth 36.1, the waist 43.8 wide and 33.5 deep, anterior height 30.2, posterior 29.0, body volume 39,946 mm3, transverse span 93.5, least canal depth 13.9, canal width 23.6, interpedicular distance 20.9, pedicle width 11.6.

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

handoff.md, beside this note, is where to start: the resume command for the run, the checks still to do, the one fetch that needs the owner's word, and what must pass before the pull request is marked ready.
