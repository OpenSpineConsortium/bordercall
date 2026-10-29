# Handoff: the clinical reread and the papers' tables

Source: thread "Finish the clinical reread", project symphony_4, 2026-10-29, written at about 17:20 UTC as bordercall
pull request 26 went to main. The handoffs before it (the stop of 2026-10-28 21:25 UTC and the checkpoint of
2026-10-29 00:40 UTC) are in this file's git history; everything they listed as next is done below or listed again.

## Where it stands

- [notes/](notes/): 43 notes, one per paper, each read whole by a first reader and checked against the whole PDF by
  a second; every one has its structured record notes/<id>.json and passes tools/check_notes.py.
- [papers/](papers/README.md): the 44 PDFs the notes cite, each matching tools/PAPERS.sha256, in git by the owner's
  choice of 2026-10-29 03:30 UTC. Nothing needs fetching or uploading.
- [synthesis/](synthesis/README.md): four parts (anomalies and the junctions; every measure as a recipe for a CT
  mask and a radiograph; measurement error and covariates; a level atlas with a playbook for the autonomous
  anatomist), checked by critics against all 43 notes (288 findings applied, then 32 more from the verifiers), and
  [SYNTHESIS.md](synthesis/SYNTHESIS.md), fifteen points, checked again (31 findings applied). The anomaly priors
  are [synthesis/anomaly-priors.md](synthesis/anomaly-priors.md), checked by a second reader and sent to the chain
  of levels, which weights its L6 and T13 types from them.
- [../panjabi-endplate-inclination.md](../panjabi-endplate-inclination.md): Panjabi's lumbar end-plate inclinations
  repeat his cervical C3 to C7 row (near certain; that the row is cervical is probable). Three second readers did
  not refute it. The owner chose on 2026-10-29 09:01 UTC to keep all 32 measures as printed, so every study,
  the comparison with the papers included, scores them as printed.
- [../paper-tables/](../paper-tables/README.md): every table of the 39 papers besides Panjabi's, read twice blind,
  reconciled on the page image and mapped to 106 measures (tools/vocabulary.csv): 23,918 cells on 60 measures;
  data/series.csv, 4,357 series, 49 measures over 209 paper-measure pairs; the comparison with Panjabi's rule at
  200 fields a setting (data/cross_naming.json) and its page, [results/README.md](../paper-tables/results/README.md).
- The paper-tables tools were reviewed twice by independent readers. The first round's 27 faults and 10 wording
  findings were fixed and checked again. The second round's findings are in
  ../paper-tables/review/round-2-findings.json, each with the refuters' verdicts; its wording findings are fixed,
  and its data findings wait for the next step.

## Next, in order

1. **Fix the second review's data findings and rerun.** Take each finding of
   ../paper-tables/review/round-2-findings.json that both refuters confirmed, or that is unverified, reproduce it,
   fix tools/series.py or the cohorts file, then remake data/series.csv
   (`python3 -I tools/series.py data/readings data/cohorts data/series.csv` in ../paper-tables), the comparison and
   the page (the commands at the end of results/README.md; the comparison takes about 15 minutes on 4 CPUs, or
   runs on the grid now that the owner lifted the hold of 2026-10-28 at 15:32 and 17:05 UTC on 2026-10-29, with his
   word and the count for the job), and bring SYNTHESIS.md's points 5 and 7 and ../paper-tables/README.md to the
   new numbers. Confirmed at the time of
   writing: Griffith 2016's height- and weight-adjusted estimates make a second series of the same 1,080 patients,
   and Frontphys 2026 takes its n from the 20 vertebrae re-measured for reliability. Then a further review round,
   until one finds nothing new; tools/code_review.js is the first round's script.
2. **The owner's ask of 2026-10-29 15:15 UTC:** extensive validation that the measures and their data are of
   good quality, then research into how prior art has measured them, with benchmarked public test sets and code.
3. Tell the chain of levels and the auto-anatomist when series.csv or the record changes; the validation of the
   synthetic data against population means reads series.csv too.

Waiting for the owner, unchanged: archive/bordercall/SPINEPS_MAPPING.md (line 88) and archive/bordercall/covariance.py
(line 28) call Panjabi's specimens embalmed; his papers say fresh autopsy specimens, cleaned to dry bone
([notes/panjabi1992.md](notes/panjabi1992.md)). The archive is kept unchanged until he says where to correct it.

The evaluation Claude Doc of the old account (claude.ai/artifact/RF7zs7UAEGwE4ZMaQWtn8F) is not shared with the new
one, so it was not filled; ../paper-tables/results/README.md is the record it would have shown.

Nothing went to the grid, and no WSU data was used.
