# VerSe's masks read for gold tier 3, 2026-10-29

Thread "Read the rest of VerSe's masks" of the claude.ai project symphony_4, for the thread "Complete gold tier 3 full-spine CT", which owns the take, the counts and the merges. Confidential like SchwingNet and bordercall: nothing here goes to a public place. No mask or CT is in this folder or in any repository; the masks were read in this thread's cloud container from VerSe's public release on OSF, never from the grid, and nothing went to the grid.

## The result

- OUT.jsonl: 374 rows, one per VerSe series, sorted by series id, ASCII with LF.
  sha256 7278e12b820bab9b7458a631564ec7ca67fd792734aaf6de1203b3f549d94437, 844,349 bytes.
- Error rows: none. No row carries "error" and no row carries "outside_scheme" (no label outside VerSe's scheme).
- What the 374 rows are made of: 191 rows came from the part file of the earlier run (verse-facts.part.jsonl at SchwingNet 3d03196, sha256 941ded262d9b8eef8748318d5f25304dcf33929abc4ca6194db3e230fd2a9381), kept as written, and 183 rows were read here. As a check, 12 of the 191 earlier rows (6 with other_release, 6 without) were read again here and came out byte for byte the same.
- Releases: 313 rows read from verse20 and 61 from verse19 (the series published only in verse19). 99 series are in both releases; every one of the 99 carries other_release, and in all 99 the verse19 copy has the same grid, the same levels and no level whose voxel count differs.
- Files: the rows record 473 mask files (374 read as the chosen copy, 99 as other_release), each with its bytes and sha256, and all 473 agree with the files downloaded and with OSF's listed sizes.
- Levels: 76 rows hold C2. No row holds the sacrum, because no VerSe mask draws label 26 (the scheme has it, the annotations stop at the last lumbar level); a sacrum test on VerSe has to come from the field, not from a label.

## The masks

- LISTING.json: every file of the MICCAI nodes 923ap (VerSe 19) and b2wxj (VerSe 20), 1,911 files.
- Mask files ending _seg.nii.gz: 160 in verse19 and 313 in verse20, 473 in all, 1,428,261,472 bytes, every one downloaded at its listed size (verse_get_seg.log). The second download, for files ending _msk.nii.gz, found none (verse_get_msk.log): the MICCAI nodes spell every mask _seg.
- The six series named in the review of bordercall PR 25 (verse112, verse139, verse141, verse151, verse251, verse257): series.json marks each as in VerSe 20, but b2wxj publishes no mask for any of them, so this download has no verse20 copy of them either, and their part-file lines were kept and they are read from verse19 with no other_release. verse251 has a CT in b2wxj, 01_training/verse402/verse402_verse251_CT-sag.nii.gz (84,670,093 bytes, the same size as verse19's verse251.nii.gz), with no mask beside it. The VerSe 20 BIDS node 4skx2 was listed too (LISTING-bids-4skx2.json, 857 files, 214 vertebra masks) and holds none of the six; it may not be the whole BIDS release. This is why series.json counts 319 VerSe 20 series and the release gives 313 VerSe 20 masks.
- verse251's row has patient_in_name null, because its verse19 file names no patient; series.json gives its patient as verse402, so the person key is unaffected. Every row whose file names a patient agrees with series.json.

## The CT check

- CTHEAD.json: the NIfTI header of every CT in the two nodes, from a ranged read of each file's first 16 KB; 474 headers, no error. No CT was downloaded.
- CTCHECK.json (scripts/verse_ctcheck.py as committed): same 473, differ 0, missing 0.
- CTCHECK-by-release.json (ctcheck_by_release.py in this folder): the same check held to one release, so a mask in verse19 is set only beside 923ap's CT of its name and one in verse20 only beside b2wxj's, since 20 CT file names appear in both nodes and the committed check would let a mask pass on the other release's CT of the same name. Same 473, differ 0, missing 0, no name with two CTs in one release.
- The 474th CT is verse402_verse251_CT-sag above, the one CT with no mask.

## Memory and time

The run used 2 workers, as the brief said. The correction to 1 worker arrived at 02:43 UTC, when 313 rows were written and the largest masks (verse602, 512 x 512 x 2023 float64, 4.24 GB raw; verse573 4.03 GB; verse563 3.88 GB; verse503 3.49 GB) had been read; the largest left was verse809 at 2.85 GB raw, so the run went on with 2 and was not killed. The highest memory in use seen, sampled every 15 to 20 seconds, was 8.7 GB of the container's 15 GB. The facts run ran from 02:36:53 to 02:45:44 UTC.

## Exact commands

Python 3.13.17; ~/venv-sc with numpy 2.5.4, scipy 1.18.1, nibabel 5.4.2. bordercall at 4a6cd725fce2b21ae9e353a7f7451640192b9abb (branch claude/project-thread-3vxvxq, PR 25) and SchwingNet at 3d03196e7474f042dd510021afb39e073974e3dc (the same branch name), each as a detached worktree. SC is SchwingNet's docs/checkpoints/2026-10-29-gold3-full-spine/, BC bordercall's root, W the working folder.

```
curl -sS -g "https://api.osf.io/v2/nodes/923ap/files/osfstorage/?page[size]=2"
python3 -m venv ~/venv-sc && ~/venv-sc/bin/pip install numpy==2.5.4 scipy==1.18.1 nibabel==5.4.2
python3 -I SC/scripts/osf_list.py W/LISTING.json 923ap b2wxj
python3 -I SC/scripts/verse_get.py W/LISTING.json W/MASKS _seg.nii.gz
python3 -I SC/scripts/verse_get.py W/LISTING.json W/MASKS _msk.nii.gz
cp SC/verse-facts.part.jsonl W/OUT.jsonl.part
cd BC && ~/venv-sc/bin/python -m holdings.fullspine_facts verse W/MASKS W/OUT.jsonl --workers 2
~/venv-sc/bin/python -I SC/scripts/verse_cthead.py W/LISTING.json W/CTHEAD.json
~/venv-sc/bin/python -I SC/scripts/verse_ctcheck.py W/MASKS W/CTHEAD.json > W/CTCHECK.json
~/venv-sc/bin/python -I ctcheck_by_release.py W/MASKS W/CTHEAD.json > W/CTCHECK-by-release.json
python3 -I SC/scripts/osf_list.py W/LISTING-bids-4skx2.json 4skx2
```

The part file is OUT.part for the module's OUT argument W/OUT.jsonl, so it is W/OUT.jsonl.part; the run deleted it when it finished, as it does.

## sha256 of the other files

- LISTING.json 00e660cff18b73c08c6b7a30aaa0bb94d9870f037473d66cc658eff2ea31f63c
- CTHEAD.json 3f677d62a8b5b6d885c495ed57d0d80317064189b18cd218cf0feb94ad554174
- CTCHECK.json c98871d3692bd127c060cfdbd4c507e5edf58be6500fbc8ecfce159bc6c4b1e0
- CTCHECK-by-release.json 529e7700655a550de2c8fd2a84e4d3fbceff9a9513d1b9a5b7cc075e36e1907a
- LISTING-bids-4skx2.json cc4808b8d9db2715cf20406642993194a8e5456415a78bf1c9893ffd60b99de4
