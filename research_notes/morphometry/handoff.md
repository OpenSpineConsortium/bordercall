# Handoff: morphometrics from the gold tier 3 CT masks

Thread "Extract morphometrics from gold tier 3 CT" of the claude.ai project symphony_4, rewritten 29 October 2026 at about 13:45 UTC, after the owner's message of 12:20 UTC asked to carry on and to report the status with renders of the measures and tests against known truth. Confidential like the rest of bordercall. The findings are in README.md beside this file; this page says only where things stand and what is left.

## Where it stands

- Branch claude/project-thread-6o9umj, draft pull request 30. It holds morphometry/ (the measures), maskedge/ (the mask edge and the disc in the CT), morphoview/ (the renders), morphobench/ (the benchmarks and their figures), records/morphometry-2026-10-29/ (aggregates, figures and renders) and this note. Nothing is merged.
- The thin-slice run is complete: 228 of the 229 ENHANCE.PET studies whose coarsest spacing is at most 1.25 mm, by the code with stamp 7bda317295ef9f5b; 0980 stopped on an error. The rows, the log and their sha256 are in the project's files under /mnt/project-files/gold3-ct/morphometry/run229/, never in git. run229-partial/ beside it is the earlier half and is superseded.
- morphometry/ and scanimport/ are unchanged since b90675f. Any change to them changes the stamp, and the next run measures every study again.
- The three ENHANCE.PET CTs (0004, 0006, 0010) were read twice on the owner's word of 12:12 UTC, for the mask edge and for the disc, and deleted each time; their per-study rows are in the project's files under gold3-ct/morphometry/maskedge-2026-10-29/ (the disc's under disc/). The thick-slice rows, read from the masks alone, are under thicken-2026-10-29/.
- The status page for the owner is a private artifact, Gold Tier 3 Morphometry, drawn from records/morphometry-2026-10-29/.
- The phantom sweep (`python -m morphobench phantom --out records/morphometry-2026-10-29/phantom-truth.csv`, four slice grids by three tilts by two turns, one worker) takes over an hour; its figure is drawn by `python -m morphobench figures --records records/morphometry-2026-10-29 --out records/morphometry-2026-10-29/figures`.

## What is left, in order

1. The fixes the README's "What comes next" lists, each in morphometry/, so each one measures every study again: the interpedicular distance between the pedicles, the cervical, C7, T1 and L5 pedicles, the disc's plate rule and the neck's body cut. Batch them and run once.
2. The VerSe height test, from the helper thread's aggregates in /mnt/project-files/gold3-ct/morphometry/verse-2026-10-29/ when they come; never pooled with ENHANCE.PET.
3. The published masks of 1347, 1283 and 1134 against their repaired ones (/mnt/project-files/enhance-pet-repair/), at 3 mm.
4. Every suite, then an adversarial review of the whole diff written into the pull request's body under "## Adversarial review", then mark it ready and merge on the owner's standing permission once all suites pass.

## Traps

- Run the suites from the repository's root with `-t .` for the packages (`python -m unittest discover -s morphometry/tests -t .`), tests/ as `discover -s tests`, and archive/tests from inside archive/.
- scanimport's and combinations' suites need pydicom and PyMC; without them they fail with import errors that are not the code's.
- A container restart kills a run; the rows already written stay, and the run resumes.
- The 14 older rows in /mnt/project-files/gold3-ct/morphometry/rows/ are from code before the fixes and are not to be used.
- The run reads 1,597 mask headers over the network mount before it starts, which takes minutes.
- A CT read for a test is read only on the owner's word with its size first, kept in a scratch folder off the project's files, and deleted by its own path afterwards.
