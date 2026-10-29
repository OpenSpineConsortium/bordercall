# VerSe heights against the readers' Genant grades

Thread "Benchmark VerSe heights against fracture grades" of the claude.ai project symphony_4, 2026-10-29, on the owner's choice of 12:28 UTC ("Yes, run VerSe in a helper thread"). Confidential to bordercall: nothing here goes to git or anywhere public. VerSe is never pooled with ENHANCE.PET. The next steps are in HANDOFF.md.

## What was measured

- Masks: the 374 VerSe series that /mnt/project-files/gold3-ct/verse-read-2026-10-29/OUT.jsonl chose (sha256 7278e12b820bab9b7458a631564ec7ca67fd792734aaf6de1203b3f549d94437). They were downloaded from OSF (nodes 923ap and b2wxj) with SchwingNet's osf_list.py and verse_get.py, and every size and sha256 was checked. 365 were measured as lossless int16 copies of VerSe's float64 files and 9 as published. The copies are on the grid as verse_masks_2026_10_29 (SchwingNet #460).
- Grades: Riedel's table Genant_Fractures_thoracolumbar_reference.csv from osf.io/download/zy68u/, 11,823 bytes, sha256 9859a382c65bb23c374db7e269a7e090a928e0f6ea3fe1510f42407e186b5629. A copy is under inputs/.
- Series to patient: SchwingNet main data/gold3-ct/verse/series.json, sha256 9ce47932389eee6f51b5c8359c3091575c403a0e20375878169bd9d29e81ce08. A copy is under inputs/.
- Code: bordercall at 44e7402bbd8fd79535eff3595a7d176aa2e7f29f (branch claude/project-thread-6o9umj, PR 30), morphometry code stamp 7bda317295ef9f5b.
- The commands:
  - `python -m morphometry run --masks DIR --scheme verse --out OUT --workers 3`. This gave rows.csv: 385,361 rows for 374 studies, sha256 2b3f464c9f8452f801072a0c4ad36a99564b51e90ce5fd7b799e355943c3a571. The run was cut by a container restart at 285 of 374; the second run measured the other 89 and joined them.
  - `python tools/verse_genant.py rows.csv inputs/Genant_Fractures_thoracolumbar_reference.csv inputs/series.json OUT.jsonl .`. This gave joined.csv (sha256 28bb592d69e6920673bb1bfaa2de64a74d10de333923e114cd38dde6f341895a) and aggregates.json (sha256 39eb1b4c1b8eef2e9538a7a60d506c3a6a9cd8f8f279c67950ffc3b49ea55046).

## Rules, fixed before the join was looked at

- A grade is a table cell holding 0, 1, 2 or 3.
  - The table also holds 23 cells of 5 and 1 cell of 8. Genant's scale has no such grade, and the table does not define them, so they are counted and left out.
  - That leaves 3,696 graded cells. Riedel's paper reports 3,548 vertebrae of 331 patients; the file and the paper differ, and nothing here says why.
- A vertebra is one patient's level.
  - 22 cells are a second series of one patient at one level. They were dropped, and none of them disagreed on the grade.
  - The reading kept is from the series where more ratios read, then the one with more voxels of that level, then the lower series id.
  - That leaves 3,674 vertebrae of 320 patients (328 series): 2,209 thoracic and 1,465 lumbar. VerSe's gl series carry no grade.
- The smaller ratio is the lower of body_index_ant_post and body_index_mid_post, using only the ones that read.
  - Below 0.80 is called fractured, Genant's 20 per cent.
  - The grade a ratio implies is 0 at 0.80 or more, 1 from 0.75, 2 from 0.60, and 3 below 0.60.
  - The AUC counts a tie as half.
  - The 95 per cent intervals come from 2,000 bootstrap resamples of patients (seed 20261029).

## Results

All 3,622 vertebrae with a reading (320 patients):

- AUC for grade 1 or more against grade 0 is 0.836 (95 per cent CI 0.780 to 0.887). For grade 2 or more against grade 0 it is 0.843 (0.780 to 0.902).
- At 0.80:
  - Sensitivity is 0.630 for grade 1 or more (189 vertebrae) and 0.685 for grade 2 or more (143).
  - Specificity is 0.966: 116 of the 3,433 grade 0 vertebrae (3.4 per cent) fall below the cut.
- Thoracic and lumbar differ:

| Stratum | Vertebrae | AUC, grade 1+ | Sensitivity at 0.80, grade 1+ | Specificity |
|---|---|---|---|---|
| Thoracic | 2,178 | 0.932 | 0.838 | 0.953 |
| Lumbar | 1,444 | 0.802 | 0.496 | 0.987 |

- Other strata, AUC for grade 1 or more:
  - T4 to L4: 0.844.
  - Coarsest spacing at most 1.25 mm: 0.860 (2,390 vertebrae).
  - Coarsest spacing over 1.25 mm: 0.806 (1,232).
- The grade the ratio implies against the readers' grade: quadratic weighted kappa 0.614, exact agreement 0.933.
  - Grade 0 dominates the exact agreement.
  - The matrix, with the readers' grade as rows and the implied grade as columns, is in aggregates.json.
- Smaller ratio by grade, median (quartiles):

| Grade | Vertebrae | Read | Smaller ratio |
|---|---|---|---|
| 0 | 3,472 | 3,433 | 0.893 (0.863 to 0.926) |
| 1 | 47 | 46 | 0.809 (0.764 to 0.855) |
| 2 | 87 | 86 | 0.752 (0.709 to 0.807) |
| 3 | 68 | 57 | 0.726 (0.625 to 0.931) |

- body_index_mid_post carries the signal: its median falls from 0.897 at grade 0 to 0.737 at grade 3.
- body_index_ant_post barely moves: 0.970 at grade 0, 0.924, 0.909 and 0.962 at grades 1 to 3. HANDOFF.md asks why.
- No reading: 52 vertebrae.
  - By grade: 39 grade 0, 1 grade 1, 1 grade 2 and 11 grade 3.
  - 11 of the 68 grade 3 vertebrae are unread (16 per cent), so the severe fractures are the ones read least. The sensitivity above is over the read vertebrae only.
  - By reason:
    - 34: the heights did not read and the code left no note (a gap in bordercall's flags).
    - 16: the body touches the edge of the volume.
    - 2: the level is not in the mask.
  - 4 vertebrae read only one ratio.

## One explanation, partly tested

A crush lowers all three heights of a vertebra, so a ratio within that vertebra cannot see it. tools/neighbour_check.py compared each vertebra's h_post_inset with the median h_post_inset of its grade 0 neighbours in the same series.

Of the grade 3 vertebrae the ratio missed (smaller ratio 0.80 or more), 15 had such neighbours. Only 4 of those 15 (27 per cent) had a posterior height under 0.80 of their neighbours'. The same is true of 30 per cent of the grade 3 vertebrae the ratio caught.

So crush explains a few of the misses, not most of them. This is not settled.
