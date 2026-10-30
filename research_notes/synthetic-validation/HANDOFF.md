# Handoff: the synthetic validation note, for the next account

Written 2026-10-30 03:35 UTC by the thread "Continue Bayesian synthetic validation" of the claude.ai
project symphony_3, carrying on the handoff of 2026-10-29 23:15 UTC (the thread "Finalize and benchmark
the Bayesian generator", symphony_2). The owner moved the covariate work to the next account on
2026-10-30 (his words to the Tan thread, 03:26 UTC: "do the covariate work and full run on the next
account"); the Tan thread's handoff is the project file tan-split/HANDOFF.md. The pull request that
finishes the steps below deletes this file.

## Where things stand

- Pull request 38 (branch claude/project-thread-o3ng22-all-measures, a draft) holds the second part,
  every measure of the reread; the strata, every paper its own population (synthval/strata.py,
  run_strata.py, records/strata, fig14_strata, README answer 11), on the owner's word of 2026-10-29 23:43
  UTC; the selection of the rule by held-out prediction (synthval/select.py, run_select.py,
  records/select, fig15_select, answer 12), on his words of 2026-10-30 02:10 UTC; the exclusion scored
  held out (the same files, fig16_exclusion, answer 13 and the section "Leaving a paper out, scored held
  out"), on his choice of 03:05 UTC, "Score exclusion held out"; and the covariates both ways
  (synthval/covariates.py, run_covariates.py, records/covariates, fig17_covariates, answer 14 and the
  section "Covariates both ways"), on his words of 02:55 UTC.
- Pull request 43 (the Tan split and the population register) merged to main at 9024b05 on 2026-10-30;
  38 has merged it in (its answers 8 and 9 come first, this note's are 10 to 14). After the merge
  run_strata.py and run_covariates.py give the committed records byte for byte, so records/select stands.
- The results to carry: the plain rule tempered by T = 2 (held-out log loss 0.09 to 0.12 nats below
  plain, calibration error 0.10 to 0.02-0.04); no paper leaves the prior (leaving Yadav 2020 out is 0.04
  to 0.05 nats worse, leaving Front. Phys. 2026 out costs three populations 0.16 to 0.21, and tempered all
  are within 0.012 nats); synthval/literature.py's EXCLUDED stays empty. Whether schwingcheck's rule
  carries the temperature is the owner's call.
- The covariates from the papers: only bach2019, chen2011, duman2026 and twomey1985 print the sexes apart
  with SDs, and bach2019, duman2026, griffith2016 and yu2015 the adult age bands; sex moves the end plate
  1.4 to 1.6 within-sex SDs (Chen) and the disc heights 0.3 to 0.8 (Bach), age under 0.25 SD a decade,
  body height the pedicle 0.34 to 0.48 SD per 100 mm (Yu). Held out, the effect's sign transfers and its
  size does not. One measure is the unit, since no paper prints the correlation within a person.
- The pages: the stats view https://claude.ai/artifact/VXV7NqZTv6gG1f4cXGhgd2 (report/build.py,
  report/notes.json) and the ML view https://claude.ai/artifact/13LehVRhuCUB4r4hNC2b3H
  (report/build_ml.py, report/ml_notes.json), both from the symphony_3 account; another account publishes
  new links and records them in the builders' docstrings.

## Next steps, in order

1. The covariates per person, the owner's ask of 02:55 UTC carried on: the gold tier 3 CTs measured by
   bordercall's morphometry on the grid (SchwingNet docs/memory/morphometry-on-the-grid.md; the report
   leaves the grid as aggregates only, the rows stay under the lab volume) with each person's age and
   sex. VerSe's demographics table (VerSeFusion configs/verse_demographics.csv) carries age, and sex by
   SchwingNet's data/gold3-ct/verse/series.json note, which left sex out; TotalSegmentator's meta.csv
   carries age (SchwingNet data/gold3-ct/totalsegmentator/subjects.json), and whether it carries sex is
   not checked. covariates.py's functions take one row a person once the rows are grouped as strata or
   bands; a person-level classifier held out by dataset or institute is the test the papers cannot give.
   It runs on the grid, so it needs the owner's word and the number of jobs.
2. The population-conditioned prior: the mixture candidate of select.py with the register's
   populations (synthval/register.py, RG.tag(series, register)[variable]) or the covariates as the
   components' weights, so a field's posterior also says which population, sex or age band it
   resembles; scored by the same nested leave-one-population-out.
3. When the owner sends the grid rerun with its count (grid/README.md, three jobs): the second part's
   records are a container's and their code digests predate the array change. run_strata.py runs in
   two minutes and is not sent to the grid; run it again after any recut.
4. When bordercall pull request 39 merges: `papers_table.write_snapshot_all` to recut
   data/series_all.csv, then run_all.py, run_strata.py, run_select.py and run_covariates.py again.
5. Delete this file, mark 38 ready with its adversarial review, merge on the owner's standing permission.
