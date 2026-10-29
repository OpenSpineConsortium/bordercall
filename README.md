# VerSe's masks, one copy per series, as compact integer volumes

Thread "Benchmark VerSe heights against fracture grades" of the claude.ai project symphony_4, 2026-10-29. Carried to the grid on the owner's word of 12:53 UTC: "Make sure to save those masks if that is a better more efficient storage format, you can put in grid". Confidential like bordercall and SchwingNet; the masks themselves are VerSe's public release.

## What is here

- masks/<series>.nii.gz: the 374 VerSe series that OUT.jsonl of the thread "Read the rest of VerSe's masks" chose (/mnt/project-files/gold3-ct/verse-read-2026-10-29/OUT.jsonl, sha256 7278e12b820bab9b7458a631564ec7ca67fd792734aaf6de1203b3f549d94437), one file per series, named by the series id, in VerSe's label scheme (1 to 7 C1 to C7, 8 to 19 T1 to T12, 20 to 24 L1 to L5, 25 L6, 28 T13).
- MANIFEST.csv: for each series its release (verse19 or verse20), the file VerSe published (name, bytes, sha256), this file (bytes, sha256), its dtype before and after, its shape and the labels it holds.
- to_int16.py: the script that made the copies.
- SHA256SUMS: every other file here.

## How the copies were made

VerSe writes 365 of these 374 masks as float64. Each was downloaded from OSF (nodes 923ap and b2wxj), checked against the size and sha256 recorded in OUT.jsonl, and written again as int16 with the same affine, qform and sform: every voxel was checked to be a whole number in int16's range, and the copy was read back and compared voxel for voxel and affine for affine before it was kept. The other 9 were integers already and are VerSe's files as published. On disk the 374 files take 387,805,416 bytes against the 1,320,467,690 VerSe published for them, 29 per cent, and loaded they take a quarter of the memory, which is what lets the largest (verse602, 512 x 512 x 2023) be read on a 15 GB machine. Two masks measured by bordercall's morphometry both ways gave the same rows.

The 99 series that both releases publish are here once, as OUT.jsonl's chosen copy; the earlier read found the other release's copy on the same grid with the same levels and the same voxel count per level, and its name and sha256 are in OUT.jsonl. No CT is here.
