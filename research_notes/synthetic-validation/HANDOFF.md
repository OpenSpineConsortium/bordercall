# Handoff: the synthetic validation note, first part nearly done, second part started

Written 2026-10-29 at 17:40 UTC on the owner's checkpoint word of 17:22 UTC ("push all work and
checkpoint and write handoffs now"; at 17:27 "stop all adversarial review and push"), by the thread
"State space exploration of the synthetic data" of the claude.ai project symphony_4. This file is
the handoff for whoever picks the work up; the pull request that finishes the second part deletes it.
The owner's ask, 2026-10-29 02:12 UTC: a state space exploration of the synthetic data, curation,
QI, rerun power calculations, visualization, rendering, and validation of all the synthetic data
against the known population means; at 15:18 UTC: all the unique measures of the clinical reread,
not just Panjabi's; at 15:09 UTC: the state space and population quality report as a page.

## Where things stand

1. First part, the generator's 32 Panjabi measures: branch claude/project-thread-o3ng22, pull
   request 29, a draft. Its code, records, figures and README are finished and pushed: every record
   is byte-identical over four full runs but records/RECORD.json, which hashes every .py of the
   note; `python3 -I tables.py --check README.md` passes; figures/FIGURES.md names the committed
   RECORD.json and figures.py. Every bordercall suite passed on this code on 2026-10-29 (holdings
   136, scanimport 168, combinations 6, coarse 6, archive 243, this note's 31, the root's 292; the
   root's test_recover_draws_levels_as_the_posterior_says failed once on a Monte Carlo tolerance,
   max 0.0319, and passed when run alone; it is main's code, not this note's). What is left is
   prose: a fourth check read the README against the records and found the corrections listed
   under "Held corrections" below, two of which are applied (F1 and F2 of the answer reader); the
   rest are unapplied because the owner stopped the review. None needs a rerun: they change
   sentences, the report builder and a caption. After them: `tables.py --check README.md`, the
   suites, the PR body's "## Adversarial review" section (a draft is in the PR body), mark ready,
   merge on the owner's standing permission.
2. The report page, private: https://claude.ai/artifact/H82v6B1drWmpjTJhrWrLxv, built by
   report/build.py (kept here with report/style.css, since it lived only in the thread's scratch
   folder) from the README and figures/. To rebuild and republish: `python3 report/build.py
   <branch or commit>` from the note's folder writes report/index.html and copies the figures
   beside it (both git-ignored); then a session publishes report/index.html with its Artifact tool
   to that url, so the link stays the same. The four tiles at the top of the page are typed in
   build.py from the README's answer and change by hand with it. The published page is behind the
   README by the two applied corrections; F3 and F4 below are applied in build.py but not yet
   republished. Republish after the held corrections.
3. Second part, every measure of the reread: this branch, a draft pull request. The code is
   written and partly checked by hand (the tables, draw_table against draw); run_all.py has not
   been run, there are no tests, no records, no figures, no tables and no README text for it yet.
   The owner ranked this work first (12:06 UTC: the threads evaluating the Bayesian generator and
   the data, then the auto-anatomist, then the gold tier CT data).

## What the second part holds

- data/series_all.csv, data/vocabulary.csv, data/SOURCE_ALL.json: the whole reread snapshot, every
  measure, cut from bordercall main 6409164 (research_notes/paper-tables/data/series.csv, 4,357
  rows, sha256 5bd5b8b8...; tools/vocabulary.csv, sha256 ea06d37b...). The reread folder itself is
  not on this branch; papers_table.write_snapshot_all(repo, ref, branch) cuts the snapshot again
  with `git show`, and check_snapshot_all holds the copies to SOURCE_ALL.json. A reread fix for its
  n-faults is coming (Griffith's adjusted rows duplicate the 1,080; Frontphys 2026, Kunkel 2011 and
  Olsewski 1990 take n from vertebrae or pedicles; Chaudhary 2015's Table II repeats Table I; a
  subgroup given the cohort's count): re-cut the snapshot once it lands, before the final run.
- synthval/papers_table.py: the vocabulary (106 keys: 49 Panjabi's, 57 others; 52 lengths, 26
  angles, 16 areas, 3 ratios, 6 other, one each of years, count and percent), the variants of a key
  whose papers define it differently (VARIANTS, VARIANT_WHY: disc height, lamina angle, pedicle
  length and chord, body depth, foramen width, canal index, spinous angle, pedicle cortex), the
  selection and pooling of every series (literature.py's rules; Tan 2004's SD is uncertain),
  placement of a series at its vertebra, and three tables: A, Panjabi's 42 measures at every level
  he prints a spread (782 cells); B, the papers' 53 measures (694 placed cells: 292 rest on Tan
  2004 alone, 279 on one series, 123 pooled; 665 bone and CT, 22 film, 7 MRI; the end-plate lacks
  C6 because Tan prints SD 0 there); C, both, 75 measures (1,054 cells). Complete over C3 to L5: A
  32 (the pool), B 21, C 35; over L1 to L5: B 50, C 63. 49 keys have series, 46 usable (20
  Panjabi's, all in the pool, and 26 others); spinous_angle, disc_index and endplate_concavity have
  rows but none usable. inventory() lists every key with why it is or is not drawn.
- synthval/population.py: Population gained `kinds` and `table`; draw_table(table, settings, n,
  seed) draws from any table in draw's RNG order, a cell no paper prints NaN, the floor by np.fmax;
  checked equal to draw() on Panjabi's 32 (array_equal, errors from the registry).
- synthval/relations.py: nine relations between the papers' measures and Panjabi's (within, past,
  outside, box, convex, positive), each with its reason, read with qi.py's five on any population;
  flags_all, vertebra_rates, person_rates.
- synthval/all_measures.py: read_point, nearest (sweep.GRID and sweep.distance on a table),
  one_at_a_time, quality, rule_for and score (the rule on a subset complete over C3 to L5 or over
  L1 to L5), spread and spread_summary (power.py's part B on every pooled cell with k >= 3).
- run_all.py: selection, state space (grid on A, B and C), quality (five settings per table),
  naming (table C at the generator and at C's nearest; subsets: the seven, the 32, every complete
  measure of A, B and C), spread, RECORD_ALL.json; `--quick` for a smoke test. It reads
  records/grid.csv from the first part for the generator's nearest point.

## Next steps, in order

1. Smoke test from this folder with the Python that holds bordercall's pinned packages
   (requirements-schwingcheck.txt; pymc-extras 0.15.1 is needed by the root suite):
   `python3 -I run_all.py --out /tmp/all_quick --quick`. Fix what breaks.
2. tests/test_all_measures.py: variant_of; place; the tables' shapes and no duplicate cell;
   draw_table equals draw on the 32 and leaves NaN where no cell; each relation on a constructed
   population; score on a complete subset; the snapshot check.
3. Full run: `python3 -I run_all.py --out records/all` (unmeasured; the grid alone is 480 points
   on three tables at n 4,000, so an hour or more on 4 CPUs is likely).
4. tables.py: the inventory (a generated MEASURES.md, checked), the three tables' summary, the
   relations, each table's nearest point, naming against the number of measures, the spread; and
   figures for them in figures.py (the house format): the inventory, the papers' table, QI by
   relation, the state space of B and C, naming against the number of measures, the spread.
5. README second part, naming what each count is made of: the 292 Tan-only cells, the reread's
   n-faults, the endplate's C6, the variants. Then the page rebuilt and republished.
6. Full reruns of run.py and run_all.py at the end, the suites, the review section, mark ready.

## Held corrections to the first part's README (the fourth check, 2026-10-29)

Each names the sentence, the problem and the fix as the reader wrote it; the verifiers of most ran
into the account's weekly limit, so only F1, F2 of the answer reader, the spread sentence and the
six seeds were verified by two readers. Apply, then `tables.py --check README.md`.

- Applied: F1 (item 3: "in a group not selected"); F2 (item 5: both sd_scale readings with the
  other axes held, 0.082 at 0.8, the grid's best 0.059 beside them).
- Means prose, the nearest point and the technique error: taking the error out of the published SD
  as sqrt(sd^2 - e^2), the lengths read 3 to 9% narrower for an error of 0.2 to 0.5 mm, about as
  wide at 0.6 to 0.65, 3% wider at 0.7 to 0.75 and 8 to 12% wider at 0.95 to 1.2 mm, counting only
  cells whose published SD exceeds the error (87 of 96 at 0.95 mm, 72 at 1.2 mm); the sentence
  says "about as wide at 0.75" and "at most about 9%".
- Structure, the three papers: the reader's rewording that named Ahmed 2019 was refuted by both
  verifiers (Ahmed's sexes are pooled in the snapshot and the next sentence says so); leave the
  sentence as it is.
- State space, the six seeds: no record holds them; say they are a check beside the records, which
  hold seed 11 alone (or drop the claim, as the completeness reader's F7 asks).
- Structure, L345: the parenthesis offers L345 as the source of the within-population share, but
  L345 sets Griffith's canal against Chen's and van der Houwen's bodies, across populations; cite
  it for that reading (half to two thirds and a fifth or less) and keep 0.61 and 0.17 as Griffith's
  own means by sex (log(23.66 / 22.26) and log(15.82 / 15.55) against half of log(1419.3 / 1162.9),
  from structure.GRIFFITH_SEX, which no record repeats; completeness F4 asks for that arithmetic in
  the text).
- Power, item on the papers' split: "on every table ... 88 to 96%" is the range of the four arms'
  means over four tables each; a single table at one body ranges 69 to 100% on 25 to 206 answers;
  the nine-body field counts are 2,368 to 3,044 per table.
- Power, the countries: Zindrick 1987's cohort names no country; Germany (Kunkel 2011) and Israel
  (Gilad 1985) are inferred from the authors' institutions; New Zealand is where Robertson 2000's
  bones were studied.
- report/build.py (F3): the footer should read "a view of research_notes/synthetic-validation/
  README.md and figures/ on the branch above" and the meta line should name the branch it is
  built from; (F4): the Renders section should carry the README's "Figures and renders" paragraph
  (`S["Figures and renders"].split("\n- ")[0]`).
- Completeness F1: no film, MRI, bone-only or CT-only result is stated anywhere, though run.py
  computes them; add a sentence (the reader's numbers: 68 cells of 11 measures, Panjabi's mean a
  median 0.13 SD below, his SD 1.16 times theirs, the generator's true SD 1.38 times, 0.79 at the
  nearest point; check them against records/validation_cells.csv before writing).
- Completeness F2: say that 12 of the 32 measures have no published series (the inferior facet's
  width, both facets' heights, areas, transverse and sagittal angles, the three interfacet
  distances) and so are held to no paper, and their share of the sign flags.
- Completeness F3: the prediction interval that leaves Panjabi's mean out in none is widened by his
  twelve spines' sampling variance (sd^2 / 12, run.py inside_prediction); the Higgins interval
  alone leaves him out in one cell, the pedicle's width at T11 (9.75 against 5.55 to 9.30, four
  series), none without Tan 2004; say so at both places.
- Completeness F5: figure 5 leaves out the nearest point's matched rule too; the caption and the
  naming table's "rule matched" definition should say which points have none and why.
- Completeness F6: fig3_structure C and D and fig7_quality C compare synthetic ratios with Alonge
  2021, Amonoo-Kuofi 1985, Cizmic 2023 and Tan 2004 but the text never reads them; add the reading
  (records/structure.json, ratios).
- Completeness F8: curation is counted, never applied; every other result is read on the whole
  draw; say so after the curation sentence.
- Completeness F9: the answer's description of the nearest point should add "and r_between from 0
  to 0.2".
- Completeness F10 overlaps F2 (applied); it adds that the grid's best at 0.8 sits at scale_sd
  0.01 and r_between 0.4, as fig4_state_space F draws the held reading.
- F11 (FIGURES.md hashes) is done by the redraw in the last commit of PR 29.
