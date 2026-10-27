# TODO: the work left for the next account

Written on 27 October 2026, when the old repository moved under [archive/](archive/) and [README.md](README.md) was rewritten around the exact Bayes rule. The owner asked for the items below to wait for the next account, and none of them has been started. Each item says what to build, why, and how to tell it worked.

## The order of work, in the owner's words of 27 October 2026, 05:48 UTC

1. **Item P below, and nothing else, until the owner says otherwise.** Flesh out Panjabi: extract the rest of the data and tables from all three papers, going past what a SPINEPS segmentation can easily measure, to see how more measurements improve accuracy.
2. **Then gold tier 1, 2 and 3 data** for segmentation-based empirical testing of this Bayesian generator (item 5).
3. **Everything else after that,** items 1 to 4, 6 and 7, in any order the owner picks.

## P. THE PRIORITY: the rest of Panjabi's three papers

**What is in now.** The reference table holds, for every level, the body table (upper and lower end-plate widths and depths, posterior body height), the canal table (width and depth) and the pedicle table (width and height, left and right). The rule uses the seven of these a SPINEPS mask can measure.

**What is out.** [archive/bordercall/reference/build_panjabi.py](archive/bordercall/reference/build_panjabi.py) says what it leaves out: "Surface areas, angular dimensions, pars interarticularis, spinous and transverse process tables, rib articulations and the uncovertebral joints are in the papers and are not transcribed here".

**Steps.**

1. **Inventory every table and figure value in all three papers**: cervical 1991, thoracic 1991 and lumbar 1992, in [archive/bordercall/reference/papers/](archive/bordercall/reference/papers/). For each, write down the levels it covers, its mnemonic and what it measures. Count the dimensions gained, and say for each whether a SPINEPS mask, an AP view, a lateral view or only a CT can read it.
2. **Transcribe the tables**, following [papers/README.md](archive/bordercall/reference/papers/README.md):
   - *Read from page images.* The papers are scans, so read every value from rendered page images. Automatic text extraction of the thoracic canal table already produced plausible, wrong numbers, so never parse it.
   - *Two independent passes per table.* Check every value the papers also state in prose. The earlier pass found a standard error copied from the row above, VBHp L1.
3. **Put the values into build_panjabi.py.** They go into its region tables and its `CANON` map, and `python build_panjabi.py` regenerates panjabi_full_spine.csv. Every dispersion is a standard error; the population SD is sem x sqrt(12).
4. **Model each kind of dimension honestly.** The likelihood and the generator now take every measure as a length: value = s x (mean + spread) + error, with the patient's size s.
   - *Areas.* Under the same isometric scaling, areas go with s^2.
   - *Angles.* Angles do not scale with s.
   - *Code.* Each kind needs its own term in `place_loglik` and in `panjabi.synthesize`.
   - *Left and right pairs.* Pairs such as the pedicles and facets are near duplicates. Take their mean, or model their correlation. Never add them as two independent measures, or the posterior grows overconfident.
5. **Score how more measurements improve accuracy.**
   - *Do not enumerate every subset.* The record enumerated all 127 subsets of seven measures. With 20 or more measures that is past a million subsets, so do not enumerate.
   - *Score these instead:*
     - the seven-measure baseline;
     - each family added to it in turn (areas, angles, processes, and so on);
     - everything an AP view could read, everything a lateral view could read, and everything at all;
     - a forward order chosen greedily on selection columns from a seed of their own, then scored on the scoring columns.
   - *Report* the share named exactly and named at 0.99, with the precision there, at 1, 3 and 9 bodies.
   - *Report the twelve-spine table worlds too* (the `robust` part of exact.py). More measures from the same twelve specimens can make the rule more confident without making it more right.
6. **Deliver.**
   - the new build_panjabi.py, the CSV and papers/README.md's table map;
   - a record with its command, seeds and digests;
   - figures drawn by committed code in the style of Benzel's textbooks;
   - the README's tables brought up to date;
   - tests, with the archive's 222 still passing.
   The work may live in archive/bordercall or, after item 1, in the new package.

Still synthetic: this item says how much more Panjabi's tables could name, not what a patient's measurements do. Item 5 is where that gets tested.

## Rules that hold for every item

- **No compute without the owner's word.** No grid job, fetch or training runs without the owner's word and the number of jobs.
  - The bordercall grid pilot has the owner's word: two CPU jobs, still unsent.
  - Nothing else for bordercall on the grid has it.
- **Truth comes from full-spine CTs only.** Only full-spine CTs from C2 to the pelvis count as truth, because a level's name is a count from C2. The 802 CTSpinoPelvic1K columns are not used for any reported result.
- **SPINEPS masks are reused.** Use the existing SPINEPS masks on the grid. Never re-run SPINEPS, and never use TotalSegmentator, for this work.
- **Numbers and figures.**
  - Every number carries its file: the record and the key it comes from.
  - Figures follow the style of Benzel's textbooks and are drawn by committed code from a record.
- **Confidentiality.** The repository stays private until the provisional is filed. Results may be shown; the method may not, until the technology transfer office has reviewed it.

## 0. Start here

- **The rule.** It is [archive/bordercall/exact.py](archive/bordercall/exact.py). Its records are [archive/records/exact-2026-10-26/](archive/records/exact-2026-10-26/): exact.json and supplement.json.
- **The tests.** Run them from the archive: `cd archive && python3 -m unittest discover -s tests`. There are 222 tests, which passed before and after the move.
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
