# Pre-registration: how sharply a visible run of vertebrae names its levels (bordercall #56)

Frozen on 2026-10-30, before any run on a fitted prior, by the thread "Train on randomized spine phantoms" (step 5 of #51). The code is schwingcheck/run_naming.py at the commit that adds this file; its constants are the settings below. A change after this file is frozen goes in DEVIATIONS.md beside it, with its reason, before the run it affects.

## Question

greg, 2026-10-30 23:30 UTC: can landmarks found in a fluoroscopic shot of any field of view name each vertebra? This measures how much the shape measures of k consecutive vertebrae say about which levels they are, under the population's correlation between levels and measures. It is the information the measures carry in 3-D with a 1 mm error; a network's 2-D landmarks can do no better, and nothing here is a real image.

## Model and data

- Fields are drawn by schwingcheck.columns.draw_columns with correlation= the fitted prior, the generator's tables (Panjabi's means and spreads, the size law) and a 1 mm measurement error on every measure; the place of a field without an anchor is uniform over the column.
- Measures: endplate, endplate_depth, endplate_lower, endplate_lower_depth, h_post.
- Column types and prior weights: typical 0.9, six_lumbar 0.05, t13 0.05, four_lumbar 0.05 (chain.WEIGHTS and autoanatomist/naming.py, stated choices). Each type's fields are scored under all four types.
- Run lengths k = 1 to 6. Anchors: none, bottom (the run ends at the column's last body, the sacrum in view) and top (the run starts at C3, C2 in view).
- Scorers: the true structure (the prior the fields came from) and the generator's assumed structure (levels at rho^2 = 0.25, measures uncorrelated). The size is integrated on 81 even nodes of log s over 6 prior SDs either side; 281 nodes agree to 5e-10 in the posterior (tests).
- 2,000 fields per type, run length and anchor; the seeds are 1000 k + 10 (anchor index) + (type index).

## The prior

The gold tier correlation prior of #52, fitted on the grid by SchwingNet's word `morphometry prior` over C3 to L5. Each population with a C3 to L5 fit is run on its own, never pooled; the primary is the population whose C3 to L5 fit has the most whole spines. A run records the prior file's sha256. The stand-in prior of the code is for the smoke and the tests only and is never reported.

## Outcomes

- Primary: the fewest visible vertebrae k at which the typical column, with no anchor and under the true structure, reaches top-1 level accuracy of 0.90 at the lower end of its 95 per cent Wilson interval; or the statement that no k up to 6 does.
- Secondary: top-1 accuracy with Wilson intervals, the mean probability of the true names and the expected calibration error (10 bins) of the top answer, for every type, k, anchor and scorer; the difference between the true and the assumed scorer at each.
- An answer is right when the level names it gives the run are the run's true names, whichever type gave them.

## What is not done

No setting above is tuned on a result. No real spine, image or test person is read.
