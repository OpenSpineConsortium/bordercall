# scanimport: from a scan to a column the rule can name

Confidential with the rest of this repository: nothing here goes to a public place before the provisional is filed.

The owner's ask of 27 October 2026, 09:44 UTC, item 6 of that queue: "get 2D/3D scan to bordercall-importable data pipeline done so i can start importing empirical data". This package is that pipeline. It takes a CT's label volume or a radiograph's corner annotation, measures Panjabi's seven chords on every body, records what the labels say about the study (whether it was counted from C2, its phenotype, its evidence tier), and names it with the archive's exact rule, extended so that a real study's missing measures, gaps and uncertain scale are handled by the same model rather than dropped.

No real scan has been imported yet. Every scan this would read is on the grid, and nothing goes to the grid without the owner's word and count. Everything below was checked on synthetic spines with known chords and on Panjabi's own synthetic columns.

## What it reads

- A CT label volume in NIfTI, in any of five label schemes: VerSe (and SPINEPS's instance masks, which use the same alphabet), CTSpinoPelvic1K v11, MOOSE's stored ids, and TotalSegmentator, either as its folder of one mask per structure or as a multilabel volume with its own class map. SPINEPS's subregion volume is read beside the instance volume where there is one. Every raw value is resolved in [schemes.py](schemes.py), and each scheme says what it cannot express. TotalSegmentator has no L6 and no T13, so a column read from it is never called typical on the strength of their absence.
- A radiograph annotated in SchwingNet's X-ray format, schwingnet-spine-xr/1: four corners per body, with the level named. An AP gives the two end-plate widths. A lateral gives the two end-plate depths and the posterior height, once the image says which side is anterior. A body may carry an optional `chords` object with two points per canal measure, which is the one addition to version 1 the importer reads. An AP and a lateral of one study merge into one column.

## What it writes

A directory of imports holds:

- `columns/<study>.json`, the whole record;
- `bodies.csv`, one row per body and measure, with how the measure was taken and why it was not, where it was not;
- `fields/<study>.csv`, the study as one field in the format `python -m schwingcheck name` reads;
- `studies.csv`, the facts and each study's own tier;
- `tiers.csv`, one row per person at the best tier their studies reach, alone and as a CT and X-ray pair;
- `MANIFEST.json`, every command that wrote to the directory, with the sha256 of its inputs and the commit of the code.

The imports hold per-body measurements under the source's own case ids. They stay on the grid with the data, and only aggregates come back to git.

## The commands

```sh
python -m scanimport ingest-ct --labels seg.nii.gz --scheme verse --study s0001 --source verse \
                               --annotation human --out imports/verse
python -m scanimport ingest-ct --labels inst.nii.gz --subregion sub.nii.gz --scheme spineps \
                               --study s0001 --source verse --annotation machine --made-by "SPINEPS" --out imports/spineps
python -m scanimport ingest-xr --xr ap.json --xr lateral.json --study f0001 --source aasce --out imports/aasce
python -m scanimport check     imports/verse
python -m scanimport tiers     imports/verse imports/aasce --out imports/tiers
python -m scanimport compare   imports/verse --out imports/compare
python -m scanimport name      imports/verse/fields/s0001.csv
python -m scanimport score     imports/verse --n 1 3 5 9 15 --out imports/scores
```

`--annotation` is the caller's statement of who drew the labels. It is never inferred, and a machine's labels never raise a tier.

It needs nothing the archive does not already need: numpy, scipy and nibabel, from [archive/requirements.txt](../archive/requirements.txt). It was tested with numpy 2.5.4, scipy 1.18.1 and nibabel 5.4.2 on Python 3.13.

## How the chords are taken on a CT

[geometry.py](geometry.py) gives every vertebra its own frame. The z axis starts along the column, through the neighbours' centroids, and is then refined to the direction along which the body is thinnest, so that a neighbour's turn or slip does not tilt it. The y axis runs from the canal to the body, and is found from which side beyond the canal walls holds more of the vertebra, so a prone patient is read the same way as a supine one. Every chord is taken in that frame from the voxels' world positions, through the volume's affine, so nothing is resampled. The canal is the hole the arch closes round in a slab across the column, and the body is what lies in front of it. A whole-vertebra label needs no subregions and no threshold. Where SPINEPS's subregions exist, they are read directly.

A surface lies between the last voxel centre inside the bone and the first outside it. How far beyond the outermost centre it lies depends on how the grid meets the chord, and `edge_gap` reads that from the centres themselves.

The synthetic spines in [tests/phantom.py](tests/phantom.py) have known chords: a 44 by 34 mm body 27 mm high, a 22 by 16 mm canal, and a cervical-sized variant. Here is the worst error over the seven chords on three bodies:

| Spine | Whole-vertebra label | SPINEPS subregions |
| --- | --- | --- |
| Aligned with the grid, 1 mm voxels | 0.42 mm | 0.50 mm |
| Tilted 25 degrees, 3 mm slices | 0.70 mm | 0.68 mm |
| Prone, grid turned 5 degrees | 0.96 mm | 0.57 mm |
| Middle body turned 20 degrees about its own axis | 0.46 mm | 0.86 mm |
| Cervical sizes, 0.6 by 0.6 by 1 mm voxels | 0.32 mm | 0.37 mm |

[tests/test_geometry.py](tests/test_geometry.py) holds every chord to the larger of 0.75 mm and one voxel's shadow on the chord's axis. A vertebra cut by the field of view loses the chords it is cut through, and each lost chord carries its reason.

What the phantoms cannot show is whether these chords are Panjabi's on real bone. A whole-vertebra label includes the cortex, a segmenter can swell a body by a voxel, and Panjabi's calipers sat on landmarks no mask names. `compare` sets each imported chord beside Panjabi's mean and SD, level by level. It reports the shift in millimetres and in Panjabi's SDs, and the spread of the ratio down the column. A small spread is a scale, which the rule absorbs. A large one is a change of shape, which it does not. That comparison is the first thing to read on real imports, before any score.

## How the rule names an import

[bridge.py](bridge.py) is the archive's exact rule ([archive/bordercall/exact.py](../archive/bordercall/exact.py)), imported from where it is and not copied, with three marginals of the same model:

- A missing measure is integrated out. The covariance of the entries present is the subset of a diagonal-plus-rank-one matrix, which is again diagonal plus rank one, so Sherman-Morrison runs over what is present.
- Bodies with gaps between them are compared each with its own level, through offsets taken from the names.
- The scale is integrated with the study's own spread. A CT carries the generator's 0.07. A film carries that plus the spread of its magnification, which radiograph.py records (default m0 1.15 with a log spread of 0.08, a stated choice that the image's own geometry replaces). A film with no pixel size is named under a flat prior on its scale, with the measurement error carried by the scale, so it gives the same answer in any unit.

On complete fields of consecutive bodies, its log evidence equals the archive's (exact.evidence_lean on the same trapezoid nodes) to 1e-10. With values missing or gaps, it equals the dense normal marginal written out with a Cholesky factor to 1e-9, and an unknown scale gives the same posterior whatever the unit, to 1e-9 ([tests/test_bridge.py](tests/test_bridge.py)).

`score` runs the rule on every window of each width in every study whose labels were counted from C2, against those labels. Studies whose phenotype is not typical are scored in a group of their own, since the rule is the typical column's. `name` names one field file and prints the posterior, the mapping quality and the 99 per cent set.

## Tests

```sh
python -m unittest discover -s scanimport/tests -t .
```

There are 43 tests, and they take about a minute. The archive's own 240 tests are unchanged.

## What comes next, on the owner's word

1. Import the held whole spines with human masks: VerSe and TotalSegmentator, the 159 gold tier 3 persons of SchwingNet's corpus-tiers page. Run `compare` first and `score` second, as one grid job each, on the owner's word and count.
2. Import SPINEPS's existing grid masks as the machine arm, never re-run and never pooled with the human-annotated arm.
3. Import the corner sets already held (AASCE, the spondylolisthesis landmarks, CSXA) through converters to schwingnet-spine-xr/1, and BUU-LSPINE's edge lines. None of them is counted from C2, so they feed `compare`, not `score`.
