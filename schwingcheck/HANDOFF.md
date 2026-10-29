# Handoff: item P's last two pieces, 29 October 2026, 14:30 UTC

Written by the thread "Finish the chain of levels" (project symphony_4) at the owner's checkpoint word of 14:25 and 14:27 UTC, for the account that continues. Everything it needs is in git; nothing is on the grid, and the hold stands: no grid job and no WSU data for the Bayesian work until the owner's attorney advises.

## Where item P stands

- Merged on main: the chain of levels (pull request 31, 12:06 UTC) and the one-vertebra evaluation (pull request 32, 14:12 UTC, main 8d305e5): schwingcheck/one_body.py, records/one-body-2026-10-29/, the README's section The one-vertebra evaluation, 19 review findings fixed, every suite run alone (schwingcheck 229 tests in 959 s).
- Open: pull request 33, a draft from the branch claude/project-thread-tzrsgs, the fixed-k NUTS review with the categorical step the owner asked for at 13:01 UTC. It holds schwingcheck/fixed_k.py, schwingcheck/categorical.py (MetropolisedGibbs, Liu's acceptance; no result uses it), records/fixed-k-2026-10-29/ made from 77cea35 after the review (every draw, share, error and R-hat the first record's; the closed form's intervals at mid-step, the ArviZ panel counts and the kernel's law at 0.89 and 0.11 are what moved), the README's section The fixed-k NUTS review brought to that record, 35 fixed-k tests and 4 categorical tests, seven of them holding the README's prose numbers and the committed figures to the record, and TODO.md's lines on both items. The 12 review findings are fixed (listed below). The owner chose on 29 October 2026, 09:01 UTC, to keep all 32 measures as printed; nothing is rerun on 30.

## What is left on pull request 33, in order

Check the pull request first: if it is merged, nothing below is left. At the checkpoint every bordercall suite was running on its merge commit 6ab26fe (started 14:17 UTC, about 25 minutes); the run's log dies with the session's container, so unless this handoff's writer landed the pull request before stopping, run it again.

1. Every suite, each alone and timed with nothing else on the CPU, in the venv of requirements-schwingcheck.txt on Python 3.12.3, from the repository's root:
   - `python -m unittest tests/test_schwingcheck_*.py` (268 tests expected: 229 before this pull request, 35 fixed-k, 4 categorical; about 17 minutes)
   - `cd archive && python -m unittest discover -s tests` (243)
   - `python -m unittest discover -s scanimport/tests -t .` (168), `-s coarse/tests -t .` (6), `-s combinations/tests -t .` (6), `-s holdings/tests -t .` (136; it prints a "FAIL lowest_ribs" line inside a test that passes)
   - `python -m schwingcheck.fixed_k check`, `python -m schwingcheck.one_body check`, `python -m schwingcheck.chain_study check`, `python -m schwingcheck curve check --record records/curve-2026-10-28/curve.nc` (the curve check needs the record named)
2. The README's Tests header (schwingcheck/README.md, section Tests) reads "268 tests, whose full run ... took TIME_C s on 29 October 2026": put the measured seconds in place of TIME_C, and the count if it is not 268. Run the tests that read the README and TODO: `python -m unittest tests.test_schwingcheck_one_body.CommittedRecord tests.test_schwingcheck_curve.Arms tests.test_schwingcheck_fixed_k.CommittedRecord`. Commit ("The README's Tests header: 268 tests, N s, every suite run alone") and push to claude/project-thread-tzrsgs; no forced push is needed.
3. The pull request's body: a Tests section with each suite's count and seconds, and a section `## Adversarial review` listing the findings below as pull requests 31 and 32 did (ten lenses, the skeptic pass stopped, each finding checked by hand as it was fixed). Then mark it ready in a call of its own, and merge it as a merge commit with the head's sha copied from git, on the owner's standing permission; if the organisation's approval rule blocks the merge, ask the owner to tick the bypass box.
4. After the merge nothing of item P is open but the upstream report: PyMC 6.3.2's CategoricalGibbsMetropolis.metropolis_proportional accepts with (1 - p_current) / (1 - p_proposed_renormalised) where Liu's Metropolised Gibbs takes min(1, (1 - p_current) / (1 - p_proposed)); fixed_k.proposal_kernel writes its kernel's stationary law out and categorical.py is the corrected step. Reporting it to PyMC is outward and waits for the owner's word.

## The fixed-k review's findings, all fixed in 77cea35 and a33a1f1

- The quick test of the summed-out model never compared it with the exact posterior (rated high): now held within its errors on every field, outright where the chains agree and flagged by R-hat where one sat in a far mode.
- The integrated-out test never called free_level or place_loglik: place_loglik integrated over each measure's offset by Gauss-Hermite quadrature (60 nodes) equals rule.py's likelihood to 3e-14; 20 nodes do not.
- The two-place "proportional" kernel was not PyMC's: PyMC takes the softmax of its compiled log density, whose rounding at 0.89 and 0.11 gives a ratio above one both ways, so its chain swaps at every draw (law each place half) and never moves at 0.5 and 0.5; the kernel, the table, the caption and the test say so.
- The closed form's 89% interval sat half a grid step low: the distribution function at a node is the mass below it and half its own.
- az.plot_trace and az.plot_forest were never called: both run in the record's run on the known draws and the record counts their panels; the figures are the house format's drawings of what they show.
- The far tail's headline blamed the estimator where NUTS makes most of the shortfall on two of three fields.
- The exact-draws test used a field whose places hardly mattered: now the example field.
- "The mean over the runs is 0.97 to 1.04" is the median over places of per-place means, which run from 0.52 to 3.66.
- "Most runs of 8,000 miss the sliver" contradicted the README's 0.013%: about one draw expected, about a third of runs miss it.
- Smaller: "hundreds of draws" at one place where the place changes in 2.9% of them; the tail figure's alt text; the test docstring's overclaim, met by the seven tests that hold the prose numbers and the figures.

## How this repository is worked

bordercall has no CI: every suite runs before a merge. One pull request per change from the thread's own branch, opened as a draft with the attribution block, assigned to Gregory-Schwing-MD-PhD (a reviewer request fails, since the pull requests are authored as that login), marked ready in a call of its own, merged with the head's sha copied from git. Results are synthetic (Panjabi's tables) and confidential; bordercall stays private. threadpoolctl's limit covers only libraries already loaded, so chain_study.load_loops runs before the limit. A record is made only from a clean commit (made_by, changed_during_run), and FIGURES.md hashes the code, so the figures are redrawn after any code change.
