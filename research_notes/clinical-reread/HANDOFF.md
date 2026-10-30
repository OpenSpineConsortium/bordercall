# Handoff: the clinical reread and the papers' tables

Source: thread "Finish the clinical reread", project symphony_4, 2026-10-29, written at 17:30 UTC at the owner's
checkpoint ("PUSH ALL WORK AND CHECKPOINT AND WRITE HANDOFFS NOW", 17:22 UTC), after bordercall pull request 26
went to main at 6409164 (17:1x UTC). The handoffs before it (the stop of 2026-10-28 21:25 UTC and the checkpoint of
2026-10-29 00:40 UTC) are in this file's git history; everything they listed as next is done below or listed again.
Every file of the reread is on main; this checkpoint's own pull request carries only this handoff and the
validation sampler (../paper-tables/tools/validation_sample.py), nothing else was in flight. The auto-anatomist,
chain of levels, gold tier 3 morphometrics and synthetic validation threads were told at 17:1x UTC where the measure
set is (../paper-tables/tools/vocabulary.csv, synthesis/measures.md, ../paper-tables/data/series.csv) and that
series.csv changes once more at step 1 below.

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
  data/series.csv, 3,760 series since pull request 39 (4,357 before it), 49 measures over 208 paper-measure pairs; the comparison with Panjabi's rule at
  200 fields a setting (data/cross_naming.json) and its page, [results/README.md](../paper-tables/results/README.md).
- The paper-tables tools were reviewed twice by independent readers. The first round's 27 faults and 10 wording
  findings were fixed and checked again. The second round's findings are in
  ../paper-tables/review/round-2-findings.json, each with the refuters' verdicts; its wording findings were fixed in pull
  request 26 and its data findings in pull request 39, each with its `resolution` in that file.

## Next, in order

Step 1 below was done on 2026-10-29 in pull request 39 (thread "Plan clinical reread next steps", project
symphony_2): the sixteen findings fixed, data/series.csv remade, the comparison and the page rerun in a cloud
session on 4 CPUs, no grid job, and SYNTHESIS.md's points 5 and 7 brought to the new numbers; the old series
reproduced the old record first. A third review round then read the result (../paper-tables/review/round-3.md):
nothing refuted, seven small faults fixed, 4,077 series, the comparison rerun once more; a fourth round
(../paper-tables/review/round-4.md) found eight more, one in the record's seeding, 3,760 series, rerun again. The papers' data are printed tables, not images, so nothing of this step can leak
into a test set of the auto-anatomist. Step 2's parts a and b were done the same day in the same pull request
(../paper-tables/validation/README.md): the blind re-read of the 468 cells found 0 record faults (Wilson 0.0 to 0.8
percent), and the 116 plausibility flags were each the paper's own printed number; part c, the mapping audit, read
all 765 distinct mappings, fixed the 17 that held (Otsuki 2021's pedicle_h to differs, which reaches the comparison)
and lists 41 judgements for the owner. Step 3 was done the same day: ../prior-art-measurement/README.md with
all nine family notes, landed one commit each as the readers finished (the first four at the owner's ask of
23:05 UTC, the rest by 23:15); each note ends with what its reader could not read or did not reach, and the README
collects those gaps. Step 4 was done twice as series.csv changed (the four auto-anatomist threads told of the
3,760 count and of Otsuki 2021's vs_panjabi change); nothing changed it after that.

Handoff of 2026-10-29 23:15 UTC, at the owner's word to checkpoint everything: all four steps are on the branch of
pull request 39, which is marked ready and waits only for the owner's merge; nothing is unfinished in this thread.
What the next account would take up, none of it started: the 41 mapping judgements and the round-4 open items,
which the owner settles (../paper-tables/validation/README.md, ../paper-tables/review/round-4.md); the prior-art
gaps the README lists, if the owner wants them read; and a further review round over the validation and prior-art
folders themselves, which no round has read.

Review of 2026-10-30 (thread "Finish the clinical reread", project symphony_5), on the same pull request: the
further review round and the prior-art gaps are done (../prior-art-measurement/review/README.md, with a figure).
Second readers checked 2,109 claims of the nine notes and the validation folder at their sources; refuters held 131
of 143 findings, all applied, and refuted 12; a second sweep ran every search the README said a budget had not
reached and added 75 rows or entries to the notes, each read again by a verifier. The paper Otsuki 2021 is Irie 2021
(the file name stays otsuki2021). What is left is the owner's: the 41 mapping judgements and the round-4 open items,
as before; four items the validation review found (Abbas 2021's seven cells that still carry the old note, Bach
2019's map_note at the printed level, Mitra 2002's L5 female pedicle height 18.5, a new flag on today's series that
no checker has read on the page, and Robertson 2000's pedicle axis near vertical at L1 to L3, which bears on reading
all five of Irie 2021's pedicle_h series as differs), listed at the top of ../paper-tables/validation/README.md; and
the merge. No grid job ran and nothing was fetched into git.

1. **Fix the second review's data findings and rerun.** (Done, above; kept as the record of what was asked.) Take each finding of
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
   The fourteen findings to act on, by index in round-2-findings.json, and the file each fix belongs in, as the
   stopped workflow of 17:15 UTC had them (its design agents had started on the first two and changed no file):
   series.py or a record for 0 Griffith 2016's adjusted estimates (a second series of the same 1,080 patients),
   1 Frontphys 2026's n of 20 reliability vertebrae, 2 Kunkel 2011's h_post n (at most 12 bodies a level, 6 at
   C7 and T12), 3 Olsewski 1990's n counting pedicles, 4 with 18 Chaudhary 2015's Table II "Present study" rows
   (REPRINTS), 5 Bach 2019's figure decades repeating Tables 2 and 3 (split verdict, check first), 6 with 17 Mitra
   2002's Abstract giving the men's value as the cohort's, 7 count_of giving a subgroup the cohort's count (the
   fix found: printed_counts keeps a count only where the row's level is empty or one vertebra, and REGROUPED maps
   Shin 2024's "Caucasian" and "African-American" to "White" and "Black"), 11 Chaudhary 2015's method row in the
   cohorts file naming Hinck alone, 12 Tan 2004's signed lower end-plate angle against Panjabi's unsigned one
   (compare magnitudes), 16 Hou 1993's T9 cumulative pedicle height 12.9, outside its sexes' 12.2 and 12.5
   (MISPRINTS); cross_naming.py or results.py for 8 Busscher 2010's C/NC-only rows counted as read measures on
   the page, 19 a --leave-out key that names no series, 20 --cohorts empty letting the pig spines in while the
   page says they are out. The shape that works: one agent a finding reproduces it on the page and the code and
   designs the fix, a second tries to refute the finding and the fix, then one agent applies the data fixes in
   series.py and the records and another the tool fixes, each running the tool after each change, then one
   checker a finding diffs the old series.csv against the new and confirms only the expected rows moved. The
   old series is reproduced by `git show 6409164:research_notes/paper-tables/data/series.csv`.
2. **The owner's ask of 2026-10-29 15:15 UTC, validation that the measures and their data are of good quality.**
   The plan, nothing of it run yet: (a) a blind re-read, the transcription error rate with its Wilson interval:
   `python3 tools/validation_sample.py data/readings <out>` in ../paper-tables draws the same 468 cells (twelve a
   paper, seed 2026, 141 pages), tasks/<paper>.csv for the readers and hidden/<paper>.csv for the comparison; one
   reader a paper renders the pages named with pdftoppm into a scratch folder (never into git), reads each cell
   from the image without the recorded value and reports its value and legibility; a script compares with
   hidden/, and an adjudicator re-reads each mismatch at a higher resolution to say whether the record or the
   reader is wrong; the rate is mismatches the record lost over 468, with the interval, by paper and overall, and
   every record fault is corrected in data/readings/ with series.csv remade. (b) Plausibility flags, by code: for
   each key and level, cells beyond four median absolute deviations of the other papers' values, an SD above its
   mean, a count above its cohort's people, a level order that reverses between neighbours; each flag checked on
   the page. (c) A mapping audit: for each paper, every distinct (measure_label, key, factor, technique) against
   the paper's methods and tools/vocabulary.csv's definition, one reader a paper and a refuter a flag.
3. **The owner's ask, continued: how prior art has measured these measures, with benchmarked public test sets and
   code.** Start from SchwingNet's docs/research/morphometry-beyond-the-42-papers.md, benchmarks-to-beat.md and
   public-spine-and-pelvis-models-to-benchmark.md and bordercall's research_notes/"Vertebra measures without
   masks"/, so nothing already found is searched again. Then, for each family of vocabulary.csv's 106 keys
   (vertebral body dimensions, end-plate dimensions and angles, pedicles, canal and foramina, discs, facets, the
   transverse and spinous processes, sagittal alignment and pelvic parameters, counts and anomalies), a sweep by
   measure name, by dataset (VerSe, TotalSegmentator, CTSpine1K, SPIDER, MRSpineSeg, BUU-LSPINE, NHANES II,
   AASCE, SpineWeb), by code repository and by challenge, each hit verified by fetching the source: is the test
   set public, how large, what modality and truth, is the code public and under what licence, what accuracy is
   reported and against what truth. The result is one folder research_notes/prior-art-measurement/ with a README
   table, measure family by method, dataset, code, accuracy and what it lacks for naming levels, and a note a
   family; confidential like the rest, nothing fetched into git but links and numbers. The web is reachable from
   a cloud session (WebSearch, WebFetch; arXiv works, most publishers are refused).
4. Tell the chain of levels, the auto-anatomist, the gold tier 3 morphometrics and the synthetic validation
   threads when series.csv or the record changes; all four read series.csv.

Waiting for the owner, unchanged: archive/bordercall/SPINEPS_MAPPING.md (line 88) and archive/bordercall/covariance.py
(line 28) call Panjabi's specimens embalmed; his papers say fresh autopsy specimens, cleaned to dry bone
([notes/panjabi1992.md](notes/panjabi1992.md)). The archive is kept unchanged until he says where to correct it.

The evaluation Claude Doc of the old account (claude.ai/artifact/RF7zs7UAEGwE4ZMaQWtn8F) is not shared with the new
one, so it was not filled; ../paper-tables/results/README.md is the record it would have shown.

Nothing went to the grid, and no WSU data was used.
