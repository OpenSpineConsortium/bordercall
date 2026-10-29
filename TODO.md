# TODO: the work left for the next account

Written on 27 October 2026, when the old repository moved under [archive/](archive/) and [README.md](README.md) was rewritten around the exact Bayes rule. The owner asked for the items below to wait for the next account, and none of them has been started. Each item says what to build, why, and how to tell it worked.

## The order of work, in the owner's words of 27 October 2026, 05:48 UTC

1. **Item P below, and nothing else, until the owner says otherwise.** Flesh out Panjabi: extract the rest of the data and tables from all three papers, going past what a SPINEPS segmentation can easily measure, to see how more measurements improve accuracy. On 27 October 2026 at 08:10 UTC the owner widened it from three papers to four, the articular facets paper of 1993 added, and set its five steps, a to e, each a pull request merged once green (item P).
2. **Then gold tier 1, 2 and 3 data** for segmentation-based empirical testing of this Bayesian generator (item 5).
3. **Everything else after that,** items 1 to 4, 6 and 7, in any order the owner picks.

## The owner's decisions of 28 October 2026, 20:40 UTC, to act on later

On 28 October 2026 the owner wrapped up every thread. Of seven directions another thread had set out for him, he wrote at 20:40 UTC: "ok fyi i agree to all these directions but i want to wrap up all threads for now so simple put it in the final handoff my decisions". Each is agreed, and none is done. He wrote it while his rule of 27 October 2026, 11:56 UTC, "Send nothing to the grid", was in force, so the first send or fetch below waits for his word that it starts. The seven, as that thread wrote them:

1. Send the bordercall pilot. It is approved for two CPU jobs but unsent, under your rule that nothing goes to the grid for now. It answers the first question on this page: how many census CTs count from C2. The status word would go first.
2. Decide whether non-SPINEPS masks may feed the table. ENHANCE.PET's 1,557 columns are MOOSE masks, and TotalSegmentator's 142 are its own. I would use them only as a second arm, never pooled with the SPINEPS one.
3. Fetch the NHANES 2013-14 DXA files. These are 13 small public files, one per body from T4 to L4. They are the only public, population-weighted, per-person heights found, and the fetch needs your word and count. The size is read before any byte lands.
4. Read the whole tables already in hand. Tan 2004 and Busscher 2010 both cover C3 to L5, and Lien 2007 and Kunkel 2011 (uploaded today) have thoracic rows. Only their lower rows were ever copied.
5. Decide on a systematic search. The 42 were never searched for. A designed PubMed and Scopus search, screened against them, would turn the list into a review.
6. Decide which C-ArmLSpine and COBRA people may be spent to fit how CT measures differ from fluoroscopy, since both are test sets now.
7. Later: applications. The New Mexico decedent CTs, NAKO and UK Biobank each need an agreement you would sign. NMDID is free and has whole columns with height and weight, so it is the one I would apply to first.

## P. THE PRIORITY: the rest of Panjabi's four papers, read so every number can be checked, on a rule rewritten in PyMC

**The owner's widening of 27 October 2026, 08:10 UTC.** Item P covers four papers, not three: the articular facets paper of 1993 joins the cervical, thoracic and lumbar papers. The work goes in five steps, a to e, in this order, each a pull request in this repository merged once green. The thread doing it keeps every finding here, tells the owner in one line with the link as each step merges, and after step e was to go on to the owner's queue of 09:44 UTC, below the steps, as the owner asked on 27 October 2026 at 11:56 UTC, until the owner took that queue to another account at 15:41 UTC (below). The first step writes this item as it stands here. Where the steps below and the older steps 1 to 6 differ, the steps a to e hold.

- **a. Four papers.** The fourth is Panjabi MM, Oxland T, Takata K, Goel V, Duranceau J, Krag M. Articular facets of the human spine: quantitative three-dimensional anatomy. Spine 1993;18(10):1298-1310, the citation taken from the PDF's own first page. Its PDF is [archive/bordercall/reference/papers/Panjabi_1993_Facets_Spine_18-10_1298-1310.pdf](archive/bordercall/reference/papers/Panjabi_1993_Facets_Spine_18-10_1298-1310.pdf), beside the other three, and [papers/README.md](archive/bordercall/reference/papers/README.md)'s table map lists its tables.
- **b. Show where every number comes from, so the owner can check that it is true.** One provenance file, one row per printed value of the four papers, every value already in the reference CSVs included: the paper's file and its sha256, the PDF page and the printed page, the table, the row and column labels, mean or standard error, the string exactly as printed, the value and its units, the cell's box on the page as rendered at a stated dpi by a committed command, and what each of two independent reading passes read. A Markdown page in this repository, which GitHub shows with its images, sets every value beside the image of the cell it was read from and says plainly how the numbers were read: rendered pages read by eye by Claude, twice, never by text extraction. Tests fail when the two passes disagree, when a value the papers also state in prose disagrees, or when a CSV holds a value the provenance file does not. The pull request lists every existing value that changes. Done on 27 October 2026: [archive/bordercall/reference/provenance/](archive/bordercall/reference/provenance/README.md), 4,216 values from 3,534 cells, both passes agreeing on every cell; 13 prose contradictions and 7 comparison-table ones recorded as the papers' own; no existing value changed, one (EPDl T3, 23.3 in the transcription of the then absent thoracic Table 3) contradicted by Table 8's 23.2. Printed page 892 came on 27 October 2026 from the owner's second scan and was read on its own, that one page and nothing else again: Table 3 prints 23.3, so the archive's value stands and Table 8's 23.2 is the paper's own contradiction; 4,468 values from 3,786 cells, and the contradictions of all four papers, between tables, between text and tables and within a table's own arithmetic, are reported by committed code in [CONTRADICTIONS.md](archive/bordercall/reference/provenance/CONTRADICTIONS.md). What the papers print about their specimens was entered the same day, after step d: all four papers measured the same twelve spines, C2 to L5, whose age, sex, weight and height one by one are the thoracic paper's Table 1 (S3 to S24), and the Methods of the cervical, lumbar and facets papers each print one summary of them, the same 12 numbers in each paper (12 spines, 8 men and 4 women, and the mean, minimum and maximum of age, weight and height). Two independent passes read those 36 numbers and the four abstracts' counts of vertebrae (72, 144, 60 and 276, twelve spines times the levels each paper covers), 43 numbers in all with the facets paper's "12 spines into 276 vertebrae" and "12 vertebrae at each level", and agree on every one. prose.csv holds each summary to Table 1: they agree in every number but the weight's maximum, printed as 85 kg in all three where Table 1's heaviest specimen, S15, weighs 84 kg, which CONTRADICTIONS.md records with the papers' other contradictions (249 numbers in prose.csv, 193 held to cells, 18 contradictions). Nothing of step b is left open: the one check it left, the facets paper's X-card angle against its transverse-plane angle, the first rung of step e added (below). One finding across two papers came from the first rung's review on 28 October 2026: the lumbar paper prints its upper and lower end-plate inclinations (EPItu and EPItl, the rule's endplate_incl and endplate_lower_incl) at L1 to L5 as the same 20 numbers, means and standard errors, that the cervical paper prints at C3 to C7, in cells both passes read alike and whose images show it (lumbar-t2 rows 12 and 13 against cervical-t2 rows 19 to 22). CONTRADICTIONS.md compares each paper with itself, so it does not hold this; which paper's values are right, if either, is for the owner to settle, and the rule scores the lumbar values as printed. The clinical reread recommended scoring the chain on 30 measures without the two; the owner chose on 29 October 2026, 09:01 UTC, to keep all 32 as printed, so no study is run again without them.
- **c. Refactor for PyMC and for scale.** Items 1 and 2 below, the package `schwingcheck/` and one object per measure, are built on data shaped for PyMC: the checked table as one long CSV, one row per value with its kind (length, area or angle) and its planes, loaded into an xarray Dataset with named dimensions (level, measure, side); columns, synthetic or real, as arrays (column, body, measure) with NaN for a missing value and integer offsets for gaps; results as ArviZ InferenceData in NetCDF, with the command, the seeds and the digests in its attributes; the code vectorised, with no loop per body or per field, so one call names thousands of fields and the measures can grow past twenty. The archive's 222 tests still pass. Done on 27 October 2026: [schwingcheck/](schwingcheck/README.md), the long table of 2,690 values from 2,008 cells, 682 of which print a mean with its standard error (Table 3 read from page 892 like every other table), the twelve specimens of the thoracic paper's Table 1 (age, sex, weight, height) for the owner's ask of 11:06 UTC, one `Measure` per measurement and side (101) carrying its table rows with their cells, its mnemonics, its measurers, its correlations and its error, a pair or a measure selected twice refused, the rule to 1e-10 of exact.py and reading each measure's own error, the generator bit for bit, and seed 97 rescored to every rate exact.json records for the three regimes at 1, 3 and 9 bodies (its 127 subsets per width are not rescored); the archive's tests, 242 since step b, still pass.
- **d. Rewrite the naming rule and the column generator in PyMC.** PyMC and the packages it brings (PyTensor, ArviZ, xarray and theirs) are allowed as new dependencies of bordercall by the owner's word of 27 October 2026, pinned to exact versions; nothing else new. The current NumPy code stays as the reference, and tests prove the rewrite before anything new is scored with it: on the seven measures and the same fields the PyMC rule gives every field the same answer as the current code (to 1e-6 where it integrates the same way, within Monte Carlo error where it samples); the PyMC generator's columns match the current generator's in distribution, within Monte Carlo error; and rescoring seed 97's 2,000 columns reproduces the record's rates at 1, 3 and 9 bodies ([archive/records/exact-2026-10-26/exact.json](archive/records/exact-2026-10-26/exact.json)). Done on 27 October 2026: [schwingcheck/](schwingcheck/README.md#the-pymc-models), the rule as a PyMC model whose observed density sums the level of every body out exactly, so NUTS samples only the patient's size and no discrete variable is ever sampled (the owner's word of 09:46 UTC on Metropolis bottlenecks), the rule also as one compiled PyTensor function, the fixed-level model as the development baseline and the generator as a forward model, each model's graph drawn from PyMC's own analysis of it beside a plate diagram, and the covariates of the owner's ask of 11:06 UTC (height in the size prior, isometric to begin with; weight, age and sex through hooks at zero). On the seven measures the compiled rule equals the NumPy rule within 1e-10, the naming model integrated on the rule's nodes equals the compiled rule within 1e-6 in the tests (within 5.2e-13 over every field of seed 97's columns at 1, 3 and 9 bodies) and its observed density is the NumPy rule's likelihood summed over the levels, its NUTS posterior is within five Monte Carlo errors of the exact one at every place above 0.05 and within five plus 1e-3 everywhere, bounds that none of 96 other seeds of the sampler crossed, set so that a correct sampler crosses those at the places above 0.05, of R-hat and of the errors in fewer than one run in a thousand, the one at every place held by a wide margin (the far tail tends to run low, and why is open: the fixed-k NUTS review below, which was to take it up, moved with the owner's queue to the owner's other account at 15:41 UTC), the PyMC generator's columns match the NumPy generator's in distribution, and rescoring seed 97's 2,000 columns with the compiled rule, and again with the naming model's likelihood of each hypothesis integrated on the same nodes, reproduces every rate of the three regimes at 1, 3 and 9 bodies within 8.1e-13, the share named identical. Each measure carries its own error throughout.
- **e. Only then add the new measures**, the facets' among them, to the PyMC model, each kind as step 4 below says, and score them as step 5 below says, at 1, 3 and 9 bodies and per phenotype. **The owner's words of 27 October 2026 at 16:40 and 16:43 UTC make it a build-up study.** At 16:40 UTC, of a trial of pymc-extras' automatic marginalisation for its `DiscreteMarkovChain`: "i absolutely want this". At 16:43 UTC, word for word, its line breaks made spaces: "make sure to account for this feature existing as well https://www.pymc.io/projects/extras/en/latest/developer/extending_marginalization.html essentially i want reverse-ablation as you gradually try more features/sophisticated methods/to see how well they improve the accuracy. further you can consider how each will improve with more data as that is the other side of the coin i am working to get 2000 population samples from real patient annotated CTs, and incorpoate all literature populations similar to panjabi,". So step e starts from the seven-measure exact rule and adds one thing at a time, each a rung scored on the same columns as the rung below it, so that every gain is read against the rung it was added to; each rung is a pull request of its own, merged once green.
  - *Rung 0, the baseline.* The seven measures under the exact rule, at 1, 3 and 9 bodies, per phenotype: the typical column as exact.json records it, and the five anomalous phenotypes scored anew on the same columns, since supplement.json holds only three of them (four_lumbar, six_lumbar and t13), at 1, 3 and 5 bodies. The typical column is scored at 5 bodies too, so that every anomalous rate at 5 bodies has a typical one beside it. Done on 28 October 2026 in pull request 18, the build-up study, from its one record ([schwingcheck/README.md](schwingcheck/README.md#the-build-up-study), the record in [records/curve-2026-10-28/](records/curve-2026-10-28/figures/FIGURES.md)): the seven name 47.3%, 73.1%, 85.7% and 96.1% of the typical fields exactly at 1, 3, 5 and 9 bodies, and each anomalous phenotype is scored on 150 columns, the same 150 patients' for all five, which differ only where the spine does, so the five rows are paired: with all 32 at three, five and nine bodies, 5.1% to 7.2% of the answers at 0.99 on six-lumbar spines and spines with a T13 are wrong, nearly all of them fields that reach the L6 or the T13; on spines with a rib on L1 or no rib on T12, whose odd body is drawn half-way between T12 and L1, the seven's and all 32's answers at 0.99 at three, five and nine bodies are right 99.25% of the time or more, but with fewer measures, or at one body, they can fall below 99%, the least 45.45% of 22 answers at three bodies with one measure; both are the case for item 6.
  - *The measures, a family at a time.* First step 4's kinds, a length scaling with the patient's size s, an area with s squared and an angle not at all, in the compiled rule, the naming model and the generator alike. Done on 27 October 2026 as the first rung, pull request 15: each measure's power of the size and its own error by its kind (1 mm for a length, sqrt(pi A / 2) square millimetres for an area of mean A, 3 degrees for an angle), in rule.py, compiled.py, the naming and fixed-level models and the generator, each held by tests to rule.py (the compiled rule and the naming model), to scipy's normal density (the fixed-level model) or to the NumPy generator in distribution (the PyMC generator), and the rule from before to the bit where every power is 1, so the archive's within 1e-10; the generator's floor at 0.5, which the likelihood leaves out, touches 1,647 of the pool's 1,056,000 values that can be floored, where the seven's it touched 3 of 308,000, both in the 2,000 typical columns of seed 1234 that [schwingcheck/examples/floor_check.py](schwingcheck/examples/floor_check.py) draws, and the build-up study's record counts it at every measure and level, 1,611 of the 1,056,000 on its own 2,000 typical columns ([schwingcheck/README.md](schwingcheck/README.md#values-at-the-floor)); `measures.pool()`, the 32 measures printed with a spread at all of C3 to L5, 18 lengths, 6 areas and 8 angles, with `measures.left_out()` saying why each of the other 17 is not among them; and the trapezoid rule over log s beside the Gauss-Hermite nodes, since with all 32 the size's posterior gets about as narrow as those nodes are apart, its grid refused where it cuts off a patient's own size prior, as for a known height outside 161 to 175 cm ([schwingcheck/README.md](schwingcheck/README.md#the-rule)). Rung 0 was scored with the rungs above it, from one record, in pull request 18. Then step 5's families, each added to the rung below: the pedicles' angles, the processes, the facets, the interfacet distances, the areas, the angles; then everything an AP view reads, everything a lateral view reads, and everything; then a forward order chosen greedily on selection columns of a seed of their own and scored on the scoring columns. Done on 28 October 2026 in pull request 18 ([schwingcheck/README.md](schwingcheck/README.md#the-build-up-study)): at three bodies one measure names 42.0% of the typical fields exactly, the seven 73.1%, the first seven of the greedy order, none of them among the seven, 89.2% and all 32 98.3%; from 25 measures on every nine-body field is named exactly; and of the fields named at 0.99, 99.59% or more were right at every count and width where any was named. A left and right pair enters as its mean. A mirrored pair, whose right side has the opposite sign to its left at every level, as the facets paper's sagittal-plane angle S and Y-card angle CAY have for both facets, is mirrored first, or its mean is about zero and carries nothing. A measure that duplicates another enters once: the facets paper's X-card angle CAX is the negative of its transverse-plane angle T, for the superior facets to the printed digit at every level and side but T1 left, where the cells print 57.7 and -47.7, and for the inferior facets within 0.1 everywhere. That T1 cell is the paper's own contradiction, and since the first rung CONTRADICTIONS.md checks the relation at every cell: 91 of the 92 hold it within 0.1, all but that one. The rule scores T, never CAX.
  - *The methods, one at a time, on the best measures.* First the column as a chain of levels, summed out by pymc-extras' `DiscreteMarkovChain` with the forward algorithm, a missed body and an L6 or a T13 as the chain's transitions, set against step d's enumerated gap patterns: it should equal them where both apply and go on where the patterns run out, in long columns with unknown gaps. The patient's offsets are shared by every body of a column, so the bodies' likelihood does not factor along the chain, and the trial compares two ways round that: the offsets sampled, which leaves the chain to pymc-extras' own marginalisation, and a marginalisation of the model's own, by the page the owner linked (a `MarginalRV` subclass; a rewrite registered in the marginal rewrite database, which the page calls `marginal_rewrites_db` and pymc-extras 0.15.1's code names `marginal_ir_rewrites_db`; its log density; and a `marginalized_conditional`, without which `recover()` cannot give the level back), which keeps the closed form exact and gives the level back through `recover()`. Then the covariates, height first, then weight, age and sex once their hooks have priors. Then the literature populations, pooled hierarchically, as the owner brings them in. The chain was done on 28 October 2026 in pull requests 20 and 23 ([schwingcheck/README.md](schwingcheck/README.md#the-chain-of-levels), the records and figures in [records/chain-2026-10-28/](records/chain-2026-10-28/figures/FIGURES.md)): the chain and its exact answer, summed along the paths' shared beginnings (schwingcheck/chain.py); the two PyMC models (schwingcheck/chain_pymc.py); and its scoring against step d's rule on the same fields at 1, 3, 5 and 9 bodies, on typical, six-lumbar and T13 columns, at the papers' type weights, on the data axis and for speed (schwingcheck/chain_study.py, schwingcheck/chain_figures.py), with their tests, on synthetic columns whose fields miss a body about one step in six. With all 32 measures at nine bodies the chain names 99.0%, 98.0% and 97.5% of typical, six-lumbar and T13 fields exactly where step d's rule names 72.5%, 74.0% and 70.0%, and with all 32 at three, five and nine bodies its answers at 0.99 are right 99.37% of the time or more on every type, where step d's are right as little as 72.11% of the time; summing out the missed bodies does most of it, and the L6 and the T13 the rest on those columns. At the papers' type weights (their counts: 11 and 2 of 443 for six lumbar bodies, 12 of 517 for the T13's stand-in) the share named exactly does not move with all 32 at three to nine bodies; at one body the chain names up to 2.5 points fewer at them. On tables from 12 people taken as exact the chain's answers at 0.99 at five bodies are right only 97.99% of the time on typical columns, 90% of its prior, with all 32 and 94.98% with the seven, and from 50 people on, with all 32, 99.34% or more on every type. Built once beforehand, the chain names one nine-body field with all 32 in about 79 ms on one machine, every thread pool at one thread, where chain.path_logev, the same sum taken path by path, takes about 16 s. The covariates and the literature populations are not begun. What the review of pull request 23 left, which the owner deferred to the next account on 29 October 2026 at 00:30 UTC, was done on 29 October in the pull request after it: the four records made again from one commit, 9d94314, `speed` with load_loops and every thread pool at one thread, the seven timed as a rule cut to seven measures; axis.json reproduced every share, count and standard error of the first one, its log loss and predicted error within 3e-16 of their size (7e-15 at most), now summed in one order; the weights' rows tested against a posterior computed at the papers' weights, and the claims and speed tables' cells, the tables' labels and load_loops in a process of its own; and both PyMC models sampled one field at a time against the exact answer (pymc.json). On 18 three-body fields, each sampled with the seven and with all 32, they name every field as the exact rule does, within 0.02 at every name but in one sampling, where one of model (b)'s four chains, started by PyMC's default jitter 11 prior SDs out, fell into a mode of the size five prior SDs out and stayed there: R-hat 1.54 showed it, and the five-error bound alone did not, since that chain inflated the error. Under all three checks of the naming model's NUTS test, R-hat's among them, 69 of the 72 samplings pass, model (a) failing two on tails of 1e-9 too thin for its draws. NUTS took 6 to 119 s a field where the exact rule takes milliseconds. The build-up study's NUTS runs bear on it: at 16 measures, 20 fields sampled together on the naming model, one field's posterior was 1.0 from the exact one with an R-hat of 1.00, so a trial that samples is checked against the exact rule field by field, not by its R-hat ([schwingcheck/README.md](schwingcheck/README.md#nuts-on-the-naming-model)).
  - *The data axis, at every rung.* The other side of the coin: the table re-estimated from 12, 50, 200 and 2,000 people drawn from the generator, the rule built on each and scored on columns drawn from the generator itself, so that each rung says how much of its gain more people would raise or lower, ready for the owner's 2,000 real CTs. Twelve is the table worlds of exact.py's `robust`, where more measures from the same twelve specimens can make the rule more confident without making it more right. The people are drawn with no size spread, no measurement error and no floor, so that the estimate tends to the printed table as P grows; at least two tables are drawn at every P (8, 4, 2 and 2 at P = 12, 50, 200 and 2,000, `WORLDS` in [schwingcheck/curve.py](schwingcheck/curve.py)); every share and the precision carry two standard errors, one clustered by column with the tables drawn held fixed and one that counts the variation between tables too, a crossed two-way estimate on one degree of freedom fewer than the tables; and every table is read against the table as printed scored on the same 200 columns, not against the nominal arm on all 2,000. Done for the measures on 28 October 2026 in pull request 18 ([schwingcheck/README.md](schwingcheck/README.md#tables-from-fewer-people)): at three bodies a table from 12 people names 13.2 points fewer fields exactly with the seven, and 5.2 fewer with all 32, than the table as printed, and its answers at 0.99 are right 95.75% and 98.05% of the time; from 50 people on, 99.36% or more, and the largest loss 4.1 points, though with the seven the 200 columns cannot tell 99.41% at 50 people (0.32 points counting the tables, on 3 degrees of freedom) from 99%, and the axis's people have one size and no error, where Panjabi's twelve were 157 to 178 cm tall.
  - *The assumptions, beside the nominal arm.* Every measure's error halved and doubled, in the columns and the rule alike, and a patient's offsets correlated at 0.4 between measures. The correlated arm is the archive's misspecified world at r 0.4 (exact.py's `MISSPEC`), not its combined world (`COMBINED`, which also draws 1.5 mm of error and builds the rule on twelve-specimen tables), and it shows how the independence rule fares on correlated columns and whether its answers at 0.99 stay right. It does not measure what treating the measures as independent costs, which needs a rule that knows r, scored against this rule on the same columns; that rule is not built here (exact.py's `r_known` worlds built one for the seven, on columns of their own). Done on 28 October 2026 in pull request 18 ([schwingcheck/README.md](schwingcheck/README.md#errors-and-correlated-offsets)): in every cell of the arms table, the seven and all 32 at three and nine bodies, the answers at 0.99 are right 99.77% of the time or more, and on the typical columns of each of the four arms, wherever any field was named at 0.99, 99.40% or more, the least 1 wrong of 168, with every error doubled, at four measures and one body.
  - *What each rung reports.* The share named exactly, the share named at 0.99 with its precision there and the count answered, and the share named within one level, at 1, 3 and 9 bodies, per phenotype, each with its Monte Carlo error, and, where no answered field is wrong, the precision's exact two-sided 95 per cent lower bound in place of an error of 0; within one level is read on a half-step scale, so that on a T13 column a T12 called L1, or an L1 called T12, counts as within one level though the two are two bodies apart; the time to name one field, with how it was taken; InferenceData records with their command, seeds and digests; tables in the README and figures drawn by committed code.
  - *What it needs.* pymc-extras 0.15.1, pinned exactly with what it brings, for the trial the owner wanted at 16:40 UTC, and matplotlib 3.11.2 for the figures, which pymc-extras brings through preliz and ArviZ's plotting extra asks for too; the pull request that first needs each lists every package it brings. pymc-extras and the eight packages it brings (pull request 20) were allowed by the owner's word of 28 October 2026, 23:03 UTC: "yes you can bring in new packages". Nothing runs on the grid: every column is synthetic. A statespace model, in which one person's deviations from the table are more alike at neighbouring levels than at distant ones, waits for a measurement of that within-person correlation on gold-tier masks, a grid job that needs the owner's word.

**After step e: the owner's queue of 27 October 2026, 09:44 UTC,** word for word below, two typographic marks made ASCII, as the restart kit in SchwingNet (docs/checkpoints/2026-10-27-restart-kit/README.md) quotes it. At 11:56 UTC the owner gave the thread doing item P these of it, in this order: "the one-vertebra evaluation, the 2D/3D scan import pipeline, PyMC combination variables, coarse predictions (below T12, below T5 and others with clinical citations), Table 1 covariates (age, sex, weight, height), and the fixed-k NUTS review". At 15:41 UTC the owner took those six back: "im doing these on another account so remove them from your todo list", so the thread doing item P ends with step e, and the queue stays here as the record of what was asked. The queue's last two lines, the gold tier 3 count and chapter 4 by tiers, were never given to this thread; the count has since come from the owner's other account ([holdings/gold-tier-3.md](holdings/gold-tier-3.md), pull request 12, merged at 15:38 UTC).

```text
AFTER YOU FINISH THIS PLEASE MOVE ONTO THESE NEXT STEPS:
evaluate the Panjabi synthetic data fully for 1-vertebra prediction
get 2D/3D scan to bordercall-importable data pipeline done so i can start importing empirical data
evaluate for the power of combination variables native to pymc,
extend to other coarse predictions such as below T12, below T5, and any others with citable clinically beneficial utility

AND THEN AFTER THAT WORK ON THIS PROMPT BELOW:
Act as a Principal Bayesian Engineer and PyMC Framework Architect. I need a critical review of my proposed model development workflow for the "SchwingCheck" spine-level identification system.

### My Current Development Context & Desires
1. Objective: Identify the anatomical location (k) of a sequence of n consecutive vertebral bodies using Panjabi's historical measurement tables, scaling up to include all newly transcribed 1993 facet dimensions.
2. Workflow Phase: I am in the early prototyping/development phase. I want to use standard, beginner-friendly diagnostic tools from the PyMC core tutorials - specifically `az.plot_trace` to check convergence, `az.summary(kind="stats")` for basic intervals, and `az.plot_forest` to compare parameter spreads.
3. Strategy to Avoid Metropolis Bottlenecks: Because guessing a discrete level index (k) forces PyMC into slow, low-performance Metropolis sampling, I am keeping 'k' fixed as a known constant baseline during this development stage. This turns the problem into a continuous estimation of the patient-specific scaling parameter 's' and the feature covariance mechanics.

### Your Task
Provide a clear evaluation structured into two parts:

1. AFFIRMATION: Confirm if fixing 'k' to a constant baseline during development is a correct, idiomatic way to safely use PyMC's NUTS sampler and native ArviZ diagnostic tools (`az.plot_trace`, `az.summary`, `az.plot_forest`) without hitting performance walls. Explain why this aids model checking.
2. REFUTATION / WARNINGS: Identify any hidden pitfalls or architectural traps when I eventually try to expand this fixed-k prototype into a full multi-level predictive model. Specifically, explain why running standard MCMC sampling over a dynamic discrete 'k' variable later will fail, and suggest the proper way to handle discrete level matching in production.

THEN AFTER THAT DO THIS:
get 2D/3D scan to bordercall-importable data pipeline done
evaluate for the power of combination variables native to pymc,
extend to other coarse predictions such as below T12, below T5, and any others with citable clinically beneficial utility
see how much gold tier 3 data i have, including checking this source, https://registry.opendata.aws/enhance-pet-1-6k/
updating chapter "4 The registry and the holding: every source by reach" list data by tiers,
```

**Two of the queue came back on 28 October 2026.** At 23:03 UTC the owner wrote that the other accounts had not begun the one-vertebra evaluation and the fixed-k NUTS review ("no they havent"), and, not sure what they meant, left them to the owner's rule that an idk takes the option recommended; the coordinator gave both to the thread finishing the chain, to plan once pull request 23 merged. Each is a pull request of its own, on synthetic columns, with nothing on the grid. The one-vertebra evaluation landed on 29 October 2026 as pull request 32 (schwingcheck/README.md, The one-vertebra evaluation; records/one-body-2026-10-29/), and the fixed-k NUTS review as pull request 33 (schwingcheck/README.md, The fixed-k NUTS review; records/fixed-k-2026-10-29/), with the categorical step the owner asked for that day at 13:01 UTC, PyMC's proportional proposal corrected with Liu's acceptance (schwingcheck/categorical.py), which no result uses. Reporting that proposal's acceptance ratio to PyMC is outward and waits for the owner's word. The handoff of the owner's checkpoint of 29 October 2026, 14:27 UTC, is schwingcheck/HANDOFF.md: what pull request 33 holds and the steps that land it.

1. *The one-vertebra evaluation* ("evaluate the Panjabi synthetic data fully for 1-vertebra prediction"): what one body alone tells, as a C-arm shot that shows one vertebra would. One record at one body: for every true level, the share named exactly and within one level, the 99 per cent set's size, and the answers at 0.99 with how often they are right; which levels a lone body is taken for, as a confusion table; the seven, all 32, each view's measures and every prefix of the build-up study's order; the three column types through the chain at one body; the coarse answers a lone body can give where it cannot be named, its region and whether it is above or below T12 or T5, read from the same posterior, as the queue's coarse predictions ask; the data axis at one body; the type weights at one body, where pull request 23 found the papers' weights move the chain's answers most; and a known height, the first covariate. Line graphs in the house format (schwingcheck/figures.py). Done on 29 October 2026: schwingcheck/one_body.py, its record records/one-body-2026-10-29/ and the README's section The one-vertebra evaluation, reviewed by ten lenses and fixed, in pull request 32.
2. *The fixed-k NUTS review* (the owner's prompt in the queue above): a written answer in its two parts, each claim backed by a run. The affirmation: fixing every body's level and sampling the size and the offsets with NUTS is the right way to check the continuous part of the model, shown with `az.plot_trace`, `az.summary(kind="stats")` and `az.plot_forest` on schwingcheck's fixed-level model against its closed form. The warnings: NUTS cannot move a discrete level, and a Metropolis step on it mixes badly between the narrow, separated places a field's posterior puts its weight on; an R-hat of 1.00 can sit beside a wrong posterior, as the build-up study found at 16 measures; so in production the level is summed out exactly, as rule.py, the naming model and the chain do, and given back afterwards through `recover()`. It also takes up why NUTS's far tail runs low (below 0.001 its estimate of a place runs low, schwingcheck/README.md, The naming model), with longer and more chains and the exact rule's weights at the sampled sizes, to tell the sampler's failure from the estimator's. Done on 29 October 2026: schwingcheck/fixed_k.py, its record records/fixed-k-2026-10-29/ and the README's section The fixed-k NUTS review, reviewed by ten lenses and fixed, with schwingcheck/categorical.py, in pull request 33. The affirmation holds (NUTS is the closed form within its errors on all 16 fields); of the warnings, NUTS cannot move the level, PyMC's uniform proposal hardly moves it, its proportional proposal mixes and samples the wrong law, summing the level out is exact except where NUTS leaves a chain in a far mode of the size, which R-hat shows, and the far tail runs low from the estimator and more from NUTS where the sliver is far out.

**What is in now.** The reference table holds, for every level, the body table (upper and lower end-plate widths and depths, posterior body height), the canal table (width and depth) and the pedicle table (width and height, left and right). The rule uses the seven of these a SPINEPS mask can measure.

**What is out.** [archive/bordercall/reference/build_panjabi.py](archive/bordercall/reference/build_panjabi.py) says what it leaves out of the first three papers: "Surface areas, angular dimensions, pars interarticularis, spinous and transverse process tables, rib articulations and the uncovertebral joints are in the papers and are not transcribed here". Nothing of the facets paper is in: its facet widths, heights, areas, interfacet distances, plane angles and card angles, superior and inferior, left and right, C2 to L5.

**Steps.** The older plan, kept because its traps still hold; the steps a to e above say in which pull request each lands.

1. **Inventory every table and figure value in all four papers**: cervical 1991, thoracic 1991, lumbar 1992 and facets 1993, in [archive/bordercall/reference/papers/](archive/bordercall/reference/papers/). For each, write down the levels it covers, its mnemonic and what it measures. Count the dimensions gained, and say for each whether a SPINEPS mask, an AP view, a lateral view or only a CT can read it. This is the first part of step b's page.
2. **Transcribe the tables**, following [papers/README.md](archive/bordercall/reference/papers/README.md), as step b says:
   - *Read from page images.* The papers are scans, so read every value from rendered page images. Automatic text extraction of the thoracic canal table already produced plausible, wrong numbers, so never parse it; the facets paper carries an OCR text layer, which is not read either.
   - *Two independent passes per table.* Check every value the papers also state in prose. The earlier pass found a standard error copied from the row above, VBHp L1.
3. **Put the values into the table.** The checked long CSV of step c is the table the package reads, written from the provenance file by committed code. build_panjabi.py and panjabi_full_spine.csv stay as the archive's record and are held to the same provenance by test, so one source feeds both. Every dispersion is a standard error; the population SD is sem x sqrt(12).
4. **Model each kind of dimension honestly.** The likelihood and the generator took every measure as a length until step e's first rung (27 October 2026), which gave each kind its own power of the patient's size s: value = s^p x (mean + spread) + error.
   - *Areas.* Under the same isometric scaling, areas go with s^2.
   - *Angles.* Angles do not scale with s.
   - *Code.* Each kind needs its own term in the likelihood and in the generator; in step e that is the PyMC model of step d.
   - *Left and right pairs.* Pairs such as the pedicles and facets are near duplicates. Take their mean, or model their correlation. Never add them as two independent measures, or the posterior grows overconfident.
5. **Score how more measurements improve accuracy.**
   - *Do not enumerate every subset.* The record enumerated all 127 subsets of seven measures. With 20 or more measures that is past a million subsets, so do not enumerate.
   - *Score these instead:*
     - the seven-measure baseline;
     - each family added to it in turn (areas, angles, processes, facets, and so on);
     - everything an AP view could read, everything a lateral view could read, and everything at all;
     - a forward order chosen greedily on selection columns from a seed of their own, then scored on the scoring columns.
   - *Report* the share named exactly and named at 0.99, with the precision there, at 1, 3 and 9 bodies, and per phenotype: the typical column and each anomalous column the archive's generator draws, reported apart.
   - *Report the twelve-spine table worlds too* (the `robust` part of exact.py). More measures from the same twelve specimens can make the rule more confident without making it more right.
6. **Deliver.**
   - the provenance file and its page, the long CSV, build_panjabi.py and papers/README.md's table map;
   - a record with its command, seeds and digests, as InferenceData;
   - figures drawn by committed code in the style of Benzel's textbooks;
   - the README's tables brought up to date;
   - tests, with the archive's 222 still passing.

Still synthetic: this item says how much more Panjabi's tables could name, not what a patient's measurements do. Item 5 is where that gets tested.

## Rules that hold for every item

- **No compute without the owner's word.** No grid job, fetch or training runs without the owner's word and the number of jobs.
  - The bordercall grid pilot has the owner's word: two CPU jobs, still unsent.
  - Nothing else for bordercall on the grid has it.
- **Truth comes from full-spine CTs only.** Only full-spine CTs from C2 to the pelvis count as truth, because a level's name is a count from C2. The 802 CTSpinoPelvic1K columns are not used for any reported result.
- **SPINEPS masks are reused.** Use the existing SPINEPS masks on the grid. Never re-run SPINEPS, and never run TotalSegmentator, for this work. Masks that another segmenter's authors released with their data, TotalSegmentator's 142 columns and ENHANCE.PET's 1,557 MOOSE columns, may feed a second arm, never pooled with the SPINEPS one: decision 2 above, which the owner agreed to on 28 October 2026 at 20:40 UTC, and the project's instructions of 29 October 2026 say the same.
- **Numbers and figures.**
  - Every number carries its file: the record and the key it comes from.
  - Figures follow the style of Benzel's textbooks and are drawn by committed code from a record.
- **Confidentiality.** The repository stays private until the provisional is filed. Results may be shown; the method may not, until the technology transfer office has reviewed it.

## 0. Start here

- **The rule.** It is [archive/bordercall/exact.py](archive/bordercall/exact.py). Its records are [archive/records/exact-2026-10-26/](archive/records/exact-2026-10-26/): exact.json and supplement.json.
- **The tests.** Run them from the archive: `cd archive && python3 -m unittest discover -s tests`. There were 222 at the move, which passed before and after it, 242 since item P's step b and 243 since step e's first rung, which checks the facets paper's X-card angle.
- **SchwingNet's copy of bordercall.**
  - SchwingNet keeps a pinned copy under grid/bordercall/, taken at bordercall 6938a2e, so the move breaks nothing there today.
  - Its `tools/bordercall_vendor.py copy <clone>` looks for `bordercall/run.py` at the root of the clone it is given. After this move, give it the archive folder instead: `python3 tools/bordercall_vendor.py copy <clone>/archive`. The tool reads the commit and the clean state from git, which works from a subfolder.
- **Other open work.** The rest of this thread's open work lives in SchwingNet's checkpoint folder, docs/checkpoints/2026-10-27-cns-junction/: textbook chapter 36 and its review findings.

## 1. Lift the rule out of the archive

Build a small package at the top level, `schwingcheck/`, holding only the rule. Every item below is easier with it.

- **What goes in.** Copy these from the archive:
  - from `exact.py`: `quadrature`, `place_loglik`, `field_loglik`, `log_evidence` and `posterior`;
  - from `panjabi.py`: the table loader and the typical-column generator;
  - the reference table.
- **Generalise two things.**
  - *Gaps.* A field may have gaps: give it the bodies' offsets, (0, 1, 2) for three consecutive bodies or (0, 2, 4) for every other body. The places are then the starts k at which the last offset still fits.
  - *Missing values.* A value may be missing (NaN). Given s, one measure's values have covariance Delta + u u'. On any subset of bodies the covariance is the same form on that subset, so dropping the missing entries gives the exact marginal likelihood. A measure missing on every body adds nothing, and a field with no measure at all gets the prior back.
- **Tests that prove it is the same rule.**
  - On contiguous, complete fields, the posterior equals `exact.py`'s to within 1e-10.
  - The generator reproduces `neighbour.draw_columns` for the same seed. This means consuming the random stream in the same order: the size, then the seven offsets, then 24 level draws for each measure in turn, then 24 noise draws for each measure in turn.
  - Rescoring the 2,000 columns of seed 97 reproduces the record's exact rates at 1, 3 and 9 bodies.
  - On gapped fields, the closed form equals a dense multivariate normal computed independently.
- **A command.** Something like `python -m schwingcheck name <field.csv>` that prints the ranked places, the 99% set and whether the top place reaches 0.99.

## 2. Wrap each measurement as one object

Today a measure is a row name in a CSV plus an entry in a plane list. Make it one object that carries everything the rule and a measurer need:

- **Name and definition.** Its name, and its definition as landmarks: for example, the upper end-plate width is the distance between the lateral ends of the superior end-plate.
- **Where it can be read.** The planes that show it: AP, lateral, or both.
- **The table.** Its table rows: the mean, spread and number of specimens at each level, and the source.
- **Its own error.** The rule now uses 1 mm for every measure; each measure should carry its own error in millimetres.
- **The measurers.** On a SPINEPS mask, [archive/bordercall/spineps_map.py](archive/bordercall/spineps_map.py) already takes all seven measures ([archive/bordercall/SPINEPS_MAPPING.md](archive/bordercall/SPINEPS_MAPPING.md)) and refuses the pedicle. The measurer on an image's landmarks, for C-arm frames, does not exist yet.
- **Correlations.** Its correlation with the other measures, once a CT table can estimate it.

The rule then reads a list of measure objects and nothing else. Adding the pedicle widths and heights, which the table already holds, becomes one new object and one new measurer. A test scores every registered measure and refuses one with no table rows or no error.

## 3. The validation grid, from 0 to N measures and 0 to K bodies

Most of the grid is already measured. Scoring all 127 subsets of the seven measures at every width from 1 to 22 is in exact.json, and the README tabulates it.

What remains:

- **The two trivial edges, as tests.**
  - With no measure, the posterior equals the prior for every field, and the forced choice is right 1/(23 - n) of the time.
  - With no body there is nothing to name, and the command says so instead of answering.
- **One figure.** Draw share named exactly against bodies in view, from 1 to 22, with one line per number of measures from 0 to 7 (the best subset of each size, and separately the AP-only and lateral-only sets). Draw it from the record, with code in the package.
- **A bigger N.** N grows when item 2 adds measures, such as the pedicle rows, spinous length or transverse-process span. Score each addition across the whole grid, not at one width.
- **A bigger K.** K grows when the rule gains C2, the sacrum and the anomalous places (item 6). With C2 and the sacrum the column runs to 24 bodies, and the anomalous columns change its length.

## 4. The experiments not yet run

Each experiment uses fresh synthetic columns from a seed of its own. Earlier studies used 0, 5, 11, 23, 29, 97 and 99, among others, so search the package for every seed constant before choosing one. Each scores every place of every column, reports clustered standard errors, and checks that names given at 0.99 are right at least 99% of the time, which the exact posterior guarantees when the rule's prior is the one the fields were drawn under.

### 4a. Consecutive bodies, fewer than K

This is already in the record, at every width from 1 to 22 (exact.json, `widths`).

What remains:

- **Each place on its own.** Report each width by the region the rule calls and by the true centre level (`by_centre` is already recorded).
- **A real prior.** Repeat under a prior over places taken from a real series (item 6).

### 4b. Bodies with gaps between them, gaps known

The bodies in view need not be consecutive: a body may be hidden by hardware, gas or the edge of the collimator, and the reader knows which.

- **Patterns.**
  - Two bodies: (0, 1), (0, 2), (0, 3) and (0, 5).
  - Three bodies: (0, 1, 2), (0, 1, 3), (0, 2, 4) and (0, 3, 6).
  - Five bodies: (0, 1, 2, 3, 4) and (0, 2, 4, 6, 8).
- **Planes.** Both planes, AP alone and lateral alone.
- **The two questions.**
  - Does spreading the same number of bodies over a longer span help? Compare (0, 2, 4) with (0, 1, 2).
  - How close does a gapped field come to a consecutive field of the same span? Compare (0, 2, 4) with (0, 1, 2, 3, 4).

### 4c. Gaps the reader does not know about

Now the reader cannot tell whether a body is missing between two neighbours.

- **Candidate patterns.** List every pattern in which each step between neighbours is 1 or 2 bodies: 4 patterns for three bodies, 16 for five. Add steps of up to 3 bodies for three bodies, 9 patterns.
- **The prior.** Every (pattern, place) pair is equally likely, and the posterior runs over the pairs.
- **The truth.** Fields are drawn from the same candidates under the same prior.
- **Report three rules on the same fields:**
  - the rule that wrongly assumes consecutive bodies;
  - the rule that does not know the pattern;
  - the rule that knows it.
- **What to report.** The share named exactly (pattern and place both right), the share named at 0.99 and the precision there. The difference between the second and third rules is the cost of not knowing; the first rule shows what assuming consecutive bodies costs when they are not.

### 4d. Measures missing on some bodies

Real views lose measures body by body: the edge body is cut by the collimator, or one end-plate is not visible.

- **Missing at random.** Each (body, measure) value is missing with probability 0, 0.25, 0.5 or 0.75, at 3 and 9 bodies, both planes (Little and Rubin 2019).
- **Structured loss.**
  - Lose the top and bottom bodies' end-plate depths only.
  - Mix the planes: some bodies show only the AP measures, others only the lateral ones.

### 4e. Only some measures, AP first or lateral first

The record already holds all 127 subsets, and the README tables the two fixed orders at 1, 3 and 9 bodies.

What remains:

- **A figure.** Draw the orders at every width.
- **Errors by plane.** Score them with each plane's own measurement error once item 2 gives measures their own errors. A lateral canal depth may be read less precisely than an AP width.

## 5. Gold tier data and a larger population table from public de-identified full-spine CTs

This is second in the owner's order, after item P: gold tier 1, 2 and 3 data for segmentation-based empirical testing of the Bayesian generator.

The owner's tiers (27 October 2026; SchwingNet data/corpus-tiers/, draft #420, docs/checkpoints/2026-10-27-corpus-tiers/HANDOFF.md):

- **Gold** means one study shows C2 to the sacrum; silver means partial.
- **Tier 1** is a real CT paired with a real X-ray of the same person, with human annotation on at least one.
- **Tier 2** is the same pair with no human annotation.
- **Tier 3** is a CT or an X-ray alone, with human annotation.
- **Machine masks never raise a tier.**


The weak point is the table, not the mathematics. Panjabi measured twelve cadaveric spines; a rule whose table is estimated from twelve spines is right 95.5% of the time when it answers at 0.99 from three bodies, against the 99.78% it promises.

- **The source.** Full-spine CTs from C2 to the pelvis, from public de-identified collections already held on the grid, measured from their existing SPINEPS masks with `spineps_map.py`, each column counted from C2.
- **The first run.** The owner's approved bordercall pilot (two CPU jobs, SchwingNet's `bordercall` gate word, still unsent) runs over the existing SPINEPS masks counted from C2. Check what it writes against the seven measures before counting it as the table's first run. Any further job needs the owner's word and the count.
- **What to estimate.**
  - each level's mean and spread;
  - the loading rho of the patient's own offset in each measure, shared by every level of the column, now 0.5 by assumption. Given size it implies a correlation of rho^2 = 0.25 between two levels' deviations, so an estimated within-column correlation c enters as rho = sqrt(c);
  - the correlation between measures, now 0 by assumption (the record's r correlates only the patients' offsets), with nothing published to replace it;
  - the size spread;
  - how size, sex and age shift the means;
  - how often each anomaly occurs.
- **How to test it.** Hold out whole patients. Score the rule built on the CT table on the held-out columns. Report the same tables as the README, and set the CT table beside Panjabi's level by level.
- **A truth that does not depend on SPINEPS.** Readers count from C2 on a sample of columns, so the table's names are not only SPINEPS's.
- **Cadavers against CTs.** [research_notes/cadaver-power/](research_notes/cadaver-power/README.md), the owner's ask of 27 October 2026 at 23:55 UTC, works out how many cadavers a meta-analysis of the published series would need to match 2,000 CT scans: none matches them, however many it pools, if the CTs come from the population the rule will name, and the note says why and what is not known. Its part C is synthetic, the rule's own generator standing in for the cadavers and the scans.

## 6. Anomalous places and a real prior

- **Anomalous places.**
  - The rule has none. The anomalous columns the archive's generator draws are four lumbar, six lumbar, a thirteenth rib-bearing body, a rib on L1, and no twelfth rib.
  - Add them as places, each with its own column length and its frequency as the prior's weight, so the rule names the anomaly as well as the level.
  - A count from C2 and a count from the sacrum then disagree exactly where the white paper says they do.
- **A real prior.** Take the prior over places from a real series of fields, such as where surgeons centre the C-arm, instead of a uniform prior.

## 7. From a predictive rule to a generative tool

This is much further work. The rule already rests on a generative model: it names a field by inverting a model that can draw columns. Today that model is used only to score. The programme below turns it into a tool that generates, imputes, explains and plans.

1. **Predict the bodies not yet seen.**
   - Given the bodies in view, the model gives the posterior predictive of every body above and below, with intervals: if this field is T11 to L1, the next body down should have a lower end-plate width of so many millimetres.
   - That is a check the surgeon can make by moving the C-arm one body.
   - Test it on held-out bodies of the CT columns: the intervals should hold at their stated rate.
2. **Criticise the model.**
   - Posterior predictive checks on real columns ask whether a measured spine looks like a draw from the model (Gelman et al. 2013).
   - A field the model cannot explain at any place should be flagged and left unnamed, not named confidently.
3. **A richer column model, learned from the CT table.**
   - A hierarchical model with a patient's size, a shape factor per measure and correlated levels, with covariates and the anomalies as discrete latent states.
   - Sampling it gives realistic whole columns, typical and anomalous, with exact labels.
4. **From measures to shape.**
   - A statistical shape model of each vertebra, conditioned on level, measures and patient, gives meshes.
   - Meshes rendered as digitally reconstructed radiographs, as SchwingNet's DRR work already does for segmented CTs, give synthetic fluoroscopy frames whose labels are true by construction.
   - That closes a loop: generate a frame, measure it, name it, and compare the name with the truth.
5. **Images conditioned on a column.**
   - A generative image model conditioned on the level sequence and the measures, checked against held real frames, makes training and test images for SchwingNet's detector with every label known.
   - SchwingNet's realism work is the place this would join.
6. **Amortised inference.**
   - Enumeration is exact but scales with the number of places and patterns. For the richer models of items 3 to 5, a network trained on draws from the generator can approximate the posterior quickly (simulation-based inference; Cranmer, Brehmer and Louppe 2020).
   - Check it against the exact rule wherever enumeration is still possible, since the exact rule is the ceiling no network can pass.
7. **Plan the next image.**
   - The model can say which next view would teach the most: which body to centre, AP or lateral, or one body up or down. It does this by computing the expected drop in the posterior's entropy for each choice (Lindley 1956).
   - This turns the rule from naming what is seen into choosing what to see, fewest shots to a name at 0.99.
8. **Image evidence in place of measured numbers.**
   - Replace the measured values with the detector's own uncertainty about each landmark, so the measures become latent and the rule's error model is the detector's.
   - Every step from pixels to a level is then one probability model, and the 0.99 guarantee carries from the image to the name, as far as the model is right.

## References for this file

1. Little RJA, Rubin DB. Statistical Analysis with Missing Data. 3rd ed. Hoboken: Wiley; 2019.
2. Gelman A, Carlin JB, Stern HS, Dunson DB, Vehtari A, Rubin DB. Bayesian Data Analysis. 3rd ed. Boca Raton: CRC Press; 2013.
3. Cranmer K, Brehmer J, Louppe G. The frontier of simulation-based inference. Proc Natl Acad Sci USA 2020;117(48):30055-30062.
4. Lindley DV. On a measure of the information provided by an experiment. Ann Math Stat 1956;27(4):986-1005.

The anatomical and statistical references of the rule itself are in [README.md](README.md).
