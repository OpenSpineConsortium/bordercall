# Handoff: morphometrics from the gold tier 3 CT masks

Thread "Extract morphometrics from gold tier 3 CT" of the claude.ai project symphony_4, written 29 October 2026 at about 12:20 UTC, when the owner ranked the threads (12:06 UTC: the Bayesian generator and the data first, then the auto-anatomist, then the gold tier CT data, the rest low priority) and the coordinator asked this thread to push, leave its draft and stop until the owner names it again. Confidential like the rest of bordercall. The findings are in README.md beside this file; this page says only where things stand and what is left.

## Where it stands

- Branch claude/project-thread-6o9umj, draft pull request 30. It holds morphometry/ (the measures, commit b90675f), maskedge/ (the mask-edge test) and this note. Nothing is merged.
- The thin-slice run: 121 of the 229 ENHANCE.PET studies whose coarsest spacing is at most 1.25 mm are measured, by the code at b90675f, stamp 7bda317295ef9f5b. Their rows, the run's log, the interim comparison over the first 51 (interim-compare-51.csv) and the paper tables it read (series_f067734.csv, from the paper-tables branch claude/project-thread-adplcz at f067734) are in the project's files under /mnt/project-files/gold3-ct/morphometry/run229-partial/, never in git. The 14 older rows in /mnt/project-files/gold3-ct/morphometry/rows/ are from code before the fixes and are not to be used.
- Suites in an environment with every dependency (numpy, scipy, nibabel, pydicom, PyMC): scanimport 168, holdings 136, coarse 6, combinations 6 and maskedge 8 tests pass; morphometry's 20 passed on b90675f in the plain environment; tests/ and archive/tests were not finished in this thread. bordercall has no CI, so all of them must pass before a merge.

## What is left, in order

1. Copy run229-partial/ to a scratch folder on local disk and measure the other 108 (about 45 minutes on 3 workers, 4 CPUs): `python -m morphometry run --masks /mnt/project-files/gold3-ct/enhance-pet-source/masks --scheme enhance --out <scratch>/run229 --workers 3 --max-slice 1.25`. A study is measured again only where its rows carry another stamp, so do not change morphometry/ or scanimport/ first, or every study is measured again. Copy the joined rows.csv back to the project's files.
2. `python -m morphometry compare --rows <scratch>/run229/rows.csv --series <scratch>/series_f067734.csv --out <scratch>/run229/compare.csv --max-slice 1.25`, then the aggregates: coverage, the comparison by technique, left against right, and Eisenstein's lateral film against the least depth at L1 to L4. Replace the interim table in README.md with the full one; aggregates only.
3. The thickened-slice check on 0004, 0006 and 0010 at 2.5 and 5 mm (`python -m morphometry thicken`), and the published masks of 1347, 1283 and 1134 against their repaired ones (/mnt/project-files/enhance-pet-repair/), at 3 mm.
4. One decision card for the owner, with exact sizes: read three ENHANCE.PET CTs in the container (0004 271,621,479 bytes, 0006 411,250,425, 0010 271,977,076; 954,848,980 bytes in all, from the public bucket s3://enhance-pet-1-6k under imaging-data/images/CT/, the sizes in SchwingNet data/gold3-ct/enhance-pet/bucket.json), never the grid and never kept, and run `python -m maskedge measure` on each. It tells whether the masks stand off the bone, which is what the larger heights and widths and the shorter discs most need. The second option is the VerSe height test: VerSe's 473 masks (1,428,261,472 bytes, listed in /mnt/project-files/gold3-ct/verse-read-2026-10-29/LISTING.json) and Riedel's Genant table (11,823 bytes, osf.io/download/zy68u/), in a thread on an environment with full network access, since this one is refused OSF; never pooled with ENHANCE.PET.
5. Every suite, then an adversarial review of the whole diff written into the pull request's body under "## Adversarial review", then mark it ready and merge on the owner's standing permission once all suites pass.

## Traps

- Run the suites from the repository's root with `-t .` for the packages (`python -m unittest discover -s morphometry/tests -t .`), tests/ as `discover -s tests`, and archive/tests from inside archive/.
- scanimport's and combinations' suites need pydicom and PyMC; without them they fail with import errors that are not the code's.
- A container restart kills a run; the rows already written stay, and the run resumes.
- The run reads 1,597 mask headers over the network mount before it starts, which takes minutes.
