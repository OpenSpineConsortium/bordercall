# Handoff: VerSe heights against fracture grades (2026-10-29, 14:35 UTC)

This is from the thread "Benchmark VerSe heights against fracture grades" of the project symphony_4. The owner checkpointed it at 14:25 UTC to move to another account. The coordinator's brief was the owner's ask of 12:20 UTC: "testing suites against true known benchmarked datasets".

## Done

1. The masks and grades are downloaded and checked:
   - VerSe's 473 _seg.nii.gz files, 1,428,261,472 bytes;
   - Riedel's grades, 11,823 bytes.

   Every size and sha256 matched.
2. The masks are carried to the grid, on the owner's word of 12:53 UTC.
   - Landing: verse_masks_2026_10_29 on the data root, landed and checked at 14:11 UTC.
   - Contents: 378 files, 387,949,238 bytes.
   - These are the 374 chosen masks as lossless int16 copies, 29 per cent of VerSe's bytes.
   - The record is SchwingNet grid/carry/verse_masks_2026_10_29.txt (#460, merged).
   - The carrier is the bordercall branch claude/project-thread-6vy0yb at 27d84df. It is never merged, and the owner may delete it now.
3. All 374 series are measured with bordercall 44e7402 (PR 30), code stamp 7bda317295ef9f5b. The rows are rows.csv here.
4. The join and the aggregates are joined.csv and aggregates.json. README.md has the numbers, the rules and every sha256.
5. The container's copies of the masks are deleted; the grid holds them.

## Not done, for the next account

1. Tell the morphometrics thread's successor, which owns bordercall PR 30, about these results. The thread was sent the numbers at 14:35 UTC; check that they reached its handoff.
2. Questions the numbers raise. Each is a change to bordercall that belongs on PR 30's branch, never here:
   - body_index_ant_post barely falls with grade (median 0.970 at grade 0 and 0.962 at grade 3), while body_index_mid_post falls from 0.897 to 0.737. Either h_ant is read too far posterior on a wedged body, or VerSe's fractures here are mostly mid-plate (biconcave). Render a few grade 2 and 3 vertebrae from joined.csv with the three heights drawn on the sagittal slice to tell which.
   - 34 vertebrae have no heights and no note. The flags should say why.
   - 11 of the 68 grade 3 vertebrae did not read at all, so the severe fractures are the ones measured least.
   - Lumbar sensitivity at 0.80 is 0.50 against 0.84 for thoracic. Genant's 0.80 may be the wrong cut for a lumbar mid/post ratio, whose grade 0 median is already 0.89. Any new cut is chosen on a split and scored on the rest, never on the whole set.
   - A crush, seen only against neighbours, explains a few misses, not most (tools/neighbour_check.py, README.md).
3. To run again, use the grid's copy. Do not download VerSe again. Then:
   - run `python -m morphometry run --masks <landing>/masks --scheme verse --out OUT --workers 3`, then `python tools/verse_genant.py` as README.md says;
   - inputs/ holds the grades and series.json, and tools/ holds every script this thread wrote.

   A grid job needs the owner's word and count first. In a container, read_labels needs the int16 copies: VerSe's float64 verse602 does not fit in 15 GB.
4. Riedel's paper reports 3,548 vertebrae of 331 patients, and the file holds 3,696 graded cells; nothing here explains the difference. The codes 5 and 8 (24 cells) are undefined in the table and left out.

## Rules this work kept

- VerSe is never pooled with ENHANCE.PET.
- Results stay in this folder and bordercall, never in git or public.
- No grid job without the owner's word and count.
- The masks went to the grid only on his 12:53 UTC word.
