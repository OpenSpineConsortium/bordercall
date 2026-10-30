# Handoff: the synthetic validation note, the strata added, two steps still waiting

Written 2026-10-30 by the thread "Continue Bayesian synthetic validation" of the claude.ai project
symphony_3, carrying on the handoff of 2026-10-29 23:15 UTC (the thread "Finalize and benchmark the
Bayesian generator", symphony_2). The pull request that finishes the steps below deletes this file.

## Where things stand

- Pull request 38 (branch claude/project-thread-o3ng22-all-measures) holds the finished second part,
  every measure of the reread, and since 2026-10-30 the strata: every paper its own population
  (synthval/strata.py, run_strata.py, records/strata, fig14_strata, the README's section "Every paper its
  own population" and its answer 9, tests/test_strata.py), on the owner's word of 2026-10-29 23:43 UTC
  that the populations stay separate and the prediction is a meta-analysis's; and the selection of
  the rule by held-out prediction (synthval/select.py, run_select.py, records/select, fig15_select, the
  README's section "Choosing the rule by held-out prediction" and its answer 10, tests/test_select.py), on
  his words of 2026-10-30 02:10 UTC, "a statistically valid way to maximize predictive ability that
  doesnt necessary have to rooted in realistic biology". It is a draft.
- The owner's words of 2026-10-29: no large rerun while the synthetic populations are volatile
  (23:43 UTC), so the grid rerun of the second part and the recut after pull request 39 wait; the
  page is plots with short reading notes, not a wall of text (22:58 UTC), which report/build.py now is;
  the splitting goes on into every known population with subgroup variables (23:54 UTC, to the thread
  on Tan 2004's stratum, whose pull request 43 now carries the population register, by author with sex,
  ancestry and the like, pushed on 2026-10-30 and not merged); strata_of here takes any grouping, so the
  register's variables drive the predictor side once it lands. Pull request 43 touches README.md (answers 8
  and 9, two sections and two table blocks), tables.py, figures.py and figures/FIGURES.md too, so whichever
  of 38 and 43 lands second rebases onto the first.
- The pages: the stats view https://claude.ai/artifact/VXV7NqZTv6gG1f4cXGhgd2, built by report/build.py
  from report/notes.json (one reading note a figure) and the figures, and the ML view, built by
  report/build_ml.py from report/ml_notes.json for the owner's ask of 2026-10-30 02:13 UTC ("i am a
  machine learning specialist so i need things to be presented in a bayesian or ML natural way, you can
  keep these for like stats people but make a CS friendly report"),
  https://claude.ai/artifact/13LehVRhuCUB4r4hNC2b3H, recorded in build_ml.py's docstring; both published from the symphony_3 account with the figures as their files. The two
  earlier links are in build.py's docstring, and another account publishes new links and records them
  there.

## Next steps, in order

1. When the owner sends the grid rerun, with its count (grid/README.md, three jobs): the second part's
   records are a container's and their code digests predate the array change. run_strata.py runs in
   two minutes and is not sent to the grid; run it again after any recut.
2. When bordercall pull request 39 merges: `papers_table.write_snapshot_all` to recut data/series_all.csv,
   then run_all.py, run_strata.py and run_select.py again; every number of the second part, of the strata
   and of the selection moves.
3. When the population register lands (pull request 43: synthval/register.py, `RG.load()` reads
   data/populations.csv by paper and cohort, `RG.tag(series, register)[variable]` gives a series' value of
   any of RG.VARIABLES, and subgroups.by_value groups rows by one): give strata_of a grouping by a
   register variable and read the leave-one-stratum-out loss by subgroup, and run the selection over the
   register's populations as well as the papers; the mixture candidate takes the register's populations
   as components as it takes the papers. The Tan thread's own reading (records/subgroups on 43) found
   that with Tan's series out the register's variables account for almost none of the spread between
   series, only the specimen's kind holds a share, so expect the subgroup split to move the loss little.
4. Delete this file, mark 38 ready, merge on the owner's standing permission.
