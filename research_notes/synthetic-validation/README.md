# The synthetic spines against the published populations

Thread "Validate synthetic data against population means", 2026-10-29, project symphony_4, for greg's ask
of 2026-10-29 02:12 UTC: "Do a State space exploration of the synthetic data, Curation, QI, rerun power
calculations, visualization, rendering, and validation of all the synthetic data compared to the known
population means of these measurements". The synthetic data are the spines schwingcheck's generator draws
(schwingcheck/columns.py on Panjabi's tables, schwingcheck/measures.py). The known populations are the 39
papers of the clinical reread (bordercall draft pull request 26, branch claude/project-thread-adplcz),
cut at its commit 401aaee. Everything here is synthetic but the papers' own numbers: no grid, no WSU
data, no scan.

Confidential: this note is bordercall's and stays in this private repository, as the owner's rule says of
bordercall's and SchwingNet's research notes. A synthetic result raises no evidence tier.

**What the snapshot is.** This note's first run read the reread at 45130ac. Its second readers' code
review then found 27 faults in the paper-tables tools, each reproduced, fixed and checked again, and
401aaee remade series.csv with them fixed (its commit message): a cell's plain value no longer displaces
a printed mean and SD, both misprints of Tan 2004 and Robertson 2000 are left out with their reasons,
values printed again under another label count once (the tools' REPRINTS, and Tang 2016's quotes of its
own dissertation), each cell takes its mean from the table that prints its SD, and per-level counts are
read where a table prints them. Masharawi's two cohorts now carry their own labels. The branch's newest
commits when this note was run, 72c06ae and 3aff843, leave series.csv and its cohort files as they were.
The errors the note sets beside the generator's (synthesis/error.md) are read at 448006f, after an
accuracy critic and four completeness critics had been through that part and it was fixed (f067734,
ad83cfc); 401aaee, 72c06ae and 3aff843 leave it as it was. Every number of this note's own is read from
records that one command rewrites (Run it), and the figures it quotes from cadaver-power, the reread's
error part and results, 401aaee's commit message and SchwingNet's admission name their source where they
stand; a later snapshot is cut with `python3 -I snapshot.py --write <commit>` and the note run again.

## The answer

1. **Panjabi's means sit above the papers', and the excess is one of shape more than of size.** In the 57
   cells (measure and level) where three or more bone or CT series pool, Panjabi's mean lies outside the
   95% prediction interval, where one more population's mean should fall, in none, once his twelve
   spines' own sampling variance widens it; the Higgins interval alone leaves him out in one cell, the
   pedicle's width at T11 (9.75 against 5.55 to 9.30, four series), and in none without Tan 2004. Set against the pooled
   mean with his twelve spines' own SE taken in, it differs in 16 cells by z and 10 by t on k - 1 degrees
   of freedom, every one above (14 and 8 without Tan 2004, 11 and 8 above); taken as exact, in 25, 23
   above (table means). Over all 421 cells his mean sits a median 0.69 of his own SD above the papers',
   above in 76% of cells (0.91 absolute). But 281 of those cells rest on Tan's ten Singaporean cadavers
   alone, and over the 140 that other series cover, with Tan's series taken out, the median falls to
   0.17, above in 58% (0.88 absolute). What stays is depth: the canal's depth and both end-plates' depths
   sit 1.26 to 1.36 SD above, the pedicle's width and height 0.8 to 1.0 above (its area 0.66 below), the
   pedicle's transverse inclination 1.01 below, the posterior body height 1.96 and the superior facet
   width 1.26 below, while the end-plates' widths, the canal's width and area and the pedicle's sagittal
   inclination sit within 0.4 of the papers' (table by_measure, figure fig1_means for the eight measures
   it draws). Transverse span and the lower end-plate's inclination, 1.76 and 2.29 above, are Panjabi
   against Tan alone, the 2.29 from T1 to L2, where Tan's means are negative (-1.1 to -4.1) and Panjabi's
   positive (1.2 to 4.0).
2. **The synthetic spread is too wide, by about 70%.** In the 140 cells with a published SD, the
   generator's SD of the true anatomy is a median 1.71 times the papers', and 1.86 measured, with its
   error of one reading, which is larger than a caliper's and than most CT errors the error part gives
   (not the canal's, table assumptions). Neither is like for like, since a published SD carries its own
   technique's smaller error, so the fair ratio lies between them, nearer the first. Most of the excess is
   Panjabi's own: his SDs are 1.51 times the papers', 2.83 times for the angles, and the generator draws a
   size of its own on top of them (tables means, figure fig2_spread). Taking the size out of his SDs
   brings the true ratio to 1.53; the nearest point of the state space (below) to 0.98, 1.24 measured,
   though its angles stay 1.69 times as wide.
3. **The generator ties the canal to the body more than people do, and its depth to its width less.**
   Griffith's 1,080 CTs, his two sexes taken together since the generator has none, give the canal a
   correlation of 0.24 to 0.48 with the body's area; the generator gives 0.56 to 0.59, since one size
   scales every length alike, but 0.50 for the canal's depth with its width, against Griffith's 0.58. Of
   the three papers whose own rows hold both sexes with ten people or more each in a group not selected, Eisenstein's skeletons
   put the canal's width at about a third of the body's sex difference, set against Chen's end-plates,
   and its depth at little or none (0 to -0.5; pairs in whole millimetres cannot resolve less), and
   Duman's CTs the pedicle's width at a third; Griffith's own means by sex, within one population, put
   the canal's width at 0.61 of his body area's difference per length and its depth at 0.17, and the
   reread's error part reads Yu 2015's 503 skeletons as putting the pedicle's at or above the body's
   (table structure, figure fig3_structure).
4. **About four synthetic vertebrae in ten fail a quality indicator, and nearly every person does.**
   42.2% of vertebrae and 9,998 of 10,000 people carry at least one flag, 41.1% of vertebrae without the
   floor, which is the generator's clip of a measured value rather than an anatomy. Most are an area
   larger than the rectangle of its own width and depth (32.3%), then an end-plate under half of it
   (10.5%), both bounds that hold under allowances this note judges. The two that no definition allows (a
   length or area at or below zero, a canal wider than its own transverse processes) fail 2.2% of
   vertebrae, and curation for them drops 3,793 of 10,000 people. The seven measures the rule reads are
   flagged in 13 of 10,000 people, by a canal depth at or below zero or at the floor (table quality,
   figure fig7_quality). Curation is counted, never applied: every other result here is read on the whole
   draw.
5. **The point nearest the papers is narrower, and it names better.** Searched over 480 points, the
   nearest takes every SD to 0.6 of Panjabi's, the size's spread from 0.07 to 0.035, rho from 0.5 to
   0.9 and r_between from 0 to 0.2. There the vertebrae that fail an indicator fall from 42% to 7%, and the exact rule names one body
   in 57.1% of fields against 47.5% at the generator, three in 80.2% against 72.8%, nine in 99.0% against
   95.6% (tables grid and naming, figures fig4_state_space and fig5_naming); at nine bodies the gain is
   mostly rho's. The papers pin the SDs' scale to 0.6 to 0.7 (with the other axes held, 0.55 reads 0.032 and 0.8 reads 0.082; the grid's best point at 0.8, at scale_sd 0.01 and r_between 0.4, reads 0.059, the held reading fig4_state_space F draws); they
   leave the size's spread (0 to 0.035), rho (0.9 and above read alike) and r_between open, since all
   three set how much of a person's measures move together and Griffith's four correlations are one
   constraint on them.
6. **The papers disagree with one another by about 0.8 of Panjabi's SD, about twice part B's raw
   reading.** The spread between published series is a median 0.83 of Panjabi's SD over 57 cells,
   against the 0.39 that research_notes/cadaver-power part B read from his comparison tables, both
   uncorrected: 2.1 times. Corrected alike for the low reading of few series, it is 0.92 against the 0.48
   to 0.53 part B's median implies, 1.7 to 1.9 times (part B's pooled reading was 0.72). In the papers'
   own SD the spread is 1.15 (1.28 corrected). An infinite pool of published series is then worth about
   one CT scan of the population named (1.0, 0.8 corrected; 1.7 in Panjabi's SD), below the 2 to 16 part
   A gave, on part A's assumption that the population named is exchangeable with those pooled. A rule
   built on a table moved that much loses about 10 to 20 points of exact naming, and its answers at 0.99
   are right only 88 to 96% of the time on the mean of each arm's four tables, against 99.5 to 100 on its
   own table (tables spread and part_c, figure fig6_power).
7. **What the 159 gold persons can test.** At 159 whole spines, against the table taken as exact, a
   two-sided test at 5% has 80% power for a shift of a level's mean of 0.22 of a person's SD (0.36 for
   one cell of the seven SPINEPS measures' 154, with a Bonferroni split) and an SD ratio of 1.17, and
   gives a neighbouring-level correlation to within 0.12. Against Panjabi's twelve as the sample they
   are, it finds only a shift of 1.36 SD and a ratio of 1.81. The papers' prevalences, in populations not
   chosen for a spinal anomaly (Eisenstein's 443 skeletons, Duman's 517 chest-hospital CTs), lead one to
   expect about 4 people with six lumbar-type segments among them; the generator's equal sixths are 4 to
   9 times what the papers count, 6.7 times for six lumbar-type segments (tables gold and assumptions,
   figures fig6_power and fig8_assumptions).
8. **Tan 2004 apart from the rest takes a fifth to a half of the variance between populations out, moves
   the predictor by under a point, and narrows the prediction for one more population only with the
   spread taken as known.** Tan's means sit a median 1.71 of Panjabi's SD below the other papers' pooled
   mean in the seven measures' 15 matched cells, so pooled he nearly doubles the variance between
   populations there (the spread 0.87 to 0.63 of Panjabi's SD with him apart; 0.77 to 0.63 over all 34
   matched cells) and a pool's worth rises from 1.1 to 1.9 scans. The calibrated shift the rule's tables
   are moved by falls only from 0.94 to 0.83 SD, and the rule's exact naming on tables moved by the rest's
   spread is within a point of the pooled arm's, paired table by table (quick record). A table as far off
   as Tan's own costs 8 to 21 points and is right at 0.99 only 78 to 98% of the time. Read as a
   meta-analysis's prediction for one more population, the rest's interval is a quarter narrower than the
   merged pool's in the seven's cells with the spread taken as known (a half-width of 1.32 against 1.84
   SD) but then covers held-out series 87% of the time, under its nominal 95; Higgins' t interval, t on
   k - 2 degrees of freedom, is wider from the rest than from the merged pool in most cells (a median ratio
   of 1.09; the medians 2.97 and 3.07 point the other way) because its multiplier is 12.7 on three series
   and 4.3 on four against 4.3 and 3.2 with one more; held out it covers 96 to 100% of the series,
   consistent with its nominal 95, so its width is what one or two degrees of freedom require with so
   few populations, as Higgins and colleagues (2009) and the Cochrane Handbook say of a prediction
   interval from very few studies, and only the plug-in interval falls short (table tan, figure
   fig_tan_strata, section Tan's population apart).
9. **Split by every variable the papers state, what the variables account for is mostly Tan 2004's
   distance under other names, and no population sits as far off as his.** Every cohort a usable series
   comes from is registered with its country, its ancestry as the paper words it, the specimen, the ages,
   the counts of its sexes and of the groups it prints apart, and the year (data/populations.csv, 26
   cohorts), and one subgroup meta-analysis runs for any variable: the spread within the subgroups by
   REML, the Cochrane test for subgroup differences under that one spread, and the share of the spread
   between populations the variable accounts for, each read where the spread within has two degrees of
   freedom or more, and the share read twice, with Tan's series in and out. Over the 53 to 57 cells with
   three series or more the test can be made in 15 to 34 a variable and falls below 0.05 in 3 to 8 of
   them; with Tan in, the country accounts for a median 0.47 of the variance between populations, the
   stated ancestry 0.28, the decade 0.25, the specimen and the region 0.22, the modality 0.18 and the age
   band nothing (0.00, the six cohorts that print their mean age per sex placed by the count-weighted
   mean); with Tan out, the decade's and the modality's shares are 0.00 too, the region's 0.10, the
   ancestry's 0.16 and the country's 0.35, and only the specimen's holds (0.24). Against the
   rest of its cells dry bone sits a median 0.82 SD below and cadavers 0.83 above, the Chinese cohorts
   0.69 below and the cohorts with no stated ancestry 0.67 above; paper by paper Tan 2004 is the farthest
   below (-0.86 over 34 cells), Abbas 2021 and Cizmic 2023 the farthest above (1.56 and 1.45); by
   Higgins' t interval the papers fall outside the rest's prediction in 11 of 224 cells, Tan in 4 of 34,
   Arockiaraj in 3 of 15, Duman in 2 of 12 and no other paper in more than one, and with the spread
   taken as known in 29, Tan in 11. The contrasts a paper prints apart are few: Duman's men exceed his
   women by 0.07 to 0.21 SD in the pedicle's width within age bands (4 cells, 3 below 0.05, on counts
   the register derives from his band and sex totals, since he prints none by sex within a band), and
   Yu's African American and Caucasian skeletons differ by -0.23 to 0.20 SD in the pedicle (10 cells, 3
   below 0.05) (table subgroups, figure fig_subgroups, section The populations apart).

10. **Every measure of the reread, three tables.** Of the vocabulary's 95 measures of a vertebra, 68 are
   drawn in some table: A, Panjabi's 42 (782 cells); B, the papers' 53 over 46 keys (694 cells, 292 of
   them Tan 2004 alone); C, both, 75 measures (1,054 cells). Each table drawn from its own means and SDs
   reads a true SD 1.11 to 1.25 times its own at the generator and 1.00 at its nearest point (sd_scale
   1.0, scale_sd 0 to 0.01, rho 0.9, r_between 0.4), a self-consistency reading, not the papers'. On
   table C 15.5% of vertebrae fail a relation no anatomy can fail, most where two papers' means are drawn
   independently (the pedicle's cortex and core against its width, 19.5%). The rule on every complete
   measure names one lumbar body in 97.6% of fields against 92.3% on the 32 and 49.1% on the seven.
   The series of the 14 measures pooled from three or more differ by a median 1.07 of a person's SD
   (tables all_inventory to all_spread, figures fig9_tables to fig13_spread_all).

11. **Every paper its own population: a rule built on the others loses about 9 points at one body and 12 at
   three, and widening its SDs by tau names nothing better; it answers at 0.99 half as often, and those
   answers are right where the populations are the model's own, not on a paper whose people spread wider
   than the pool.** The owner's word of 2026-10-29: keep the populations separate and predict as a
   meta-analysis predicts. Each of the 22 papers that print a measure at every lumbar level another paper
   pools is left out in turn, its cohorts one population, and the
   rule built on the others' random-effects pool, borrowing nothing from the paper, is scored on columns
   drawn from that paper's own means over L1 to L5, on the measures it prints at every lumbar level: it
   loses a pooled 8.8 points of exact naming at one body and 12.2 at three against the paper's own table,
   with a spread between papers of 6.7 to 8.4 points, so one more population is predicted to lose between
   nothing and about 30 (at three bodies frontphys2026, Otsuki 2021, Busscher 2010, Arockiaraj 2025,
   Tan 2004 and Yadav 2020 lose 18 to 33 points; Hinck 1966, Cizmic 2023, Chaudhary 2015, Abbas 2021 and
   Amonoo-Kuofi 1985 3 or under). The same rule with every SD widened for a population it has not seen,
   sqrt(sd^2 + tau^2 + SE^2) with the SE taken under that tau, 1.82 times the within SD at the median,
   loses the same (a paired difference of 0.2 points or less, SD about 3 over the papers), since the SD
   difference alone costs 2 to 4 of those points and the shift of the means the rest, which no SD undoes;
   what it changes is the promise: at three bodies it
   answers at 0.99 on 4.7% of fields against 10.1% and, over the answers, is right on 88% against 89%,
   both floors Yadav 2020's, whose own SDs are 2.1 times the pool's; Yadav apart it is right on 99%
   against 96%, on the nine papers that print the pedicle's width and height on 98% against 96% (least
   paper 97 against 93%), and on populations drawn from the random-effects model itself on 100% at every
   width against 86% at three bodies (least 59%). Yadav 2020, Busscher 2010 and frontphys2026 stay under
   90% right under the merged rule at three bodies, their means far from the others' and, for the first
   two, their SDs 1.4 to 2.1 times the pool's (tables strata, figure fig14_strata).
12. **Choosing the rule by held-out prediction: tempering the plain rule's posterior, dividing its log
   evidence by T = 2, is the best of five candidates on the held-out log loss at every width, about 0.1
   nats below the plain rule and better on 15 to 17 of the 22 populations, with the calibration error
   down from 0.10 to 0.02 to 0.04, and it names exactly what the plain rule names; the mixture over the
   other papers' populations is the only candidate that names more, by half a point, within its SE; and
   nothing closes the 9 to 12 point gap to a population's own table, which is the shift of the means.**
   The owner's words of 2026-10-30: a statistically valid way to maximize predictive ability, not rooted
   in biology. Each of the 22 papers is held out in turn, five rules are built on the other papers alone
   (the plain pool, the pool widened by tau, every SD scaled by one factor, the plain rule tempered, and
   a mixture over the other papers' tables), the factor and the temperature set by a second leave-one-out
   nested inside the training papers, and each rule is scored on the held-out population at one, two and
   three bodies by exact naming, the log score and the calibration error, the paper's own table beside
   them as the ceiling. The tempered rule's log loss is 1.342, 1.127 and 0.849 nats against the plain
   rule's 1.431, 1.243 and 0.957 (a paired 0.090, 0.116 and 0.108 below, SE 0.049 to 0.065), half of that
   gain Yadav 2020's, without which it is 0.043 to 0.053 (SE 0.015 to 0.020) on 14 to 16 of 21; the inner
   choice fell on T = 2 for 11 to 13 of the 22 papers and the held-out curve bottoms there at every
   width. The widened rule is second, 0.058 to 0.076 nats below plain with no knob and a calibration
   error of 0.03 to 0.04; the scaled rule (factor 1.45 for 14 of 22) gains 0.03 to 0.05 nats and loses 0.4
   to 0.9 points of naming; the mixture names 0.4, 0.3 and 0.5 points more (SE 0.3) and stays as
   overconfident as plain (calibration error 0.07 to 0.09). At 0.99 the tempered rule answers on 1.1,
   2.2 and 3.1% of fields and is right on 99, 90 and 91% of those answers, Yadav again the floor; Yadav
   apart it is right on 99.5 to 99.9% against plain's 95.5 to 96.6% (table select, figure fig15_select).
13. **Leaving a paper out of the prior, scored held out: neither end-plate paper should go, and the
   tempering carries the gain whichever is kept.** The owner chose on 2026-10-30, 03:05 UTC, to let the
   held-out score decide whether Yadav 2020 leaves the prior, over leaving it out by eye. Yadav's 302
   people spread 2 to 6 times wider than the rest at the end-plate cells, where the only other paper
   with an SD of its own is Front. Phys. 2026's 20 people (0.6 to 2.4 mm), and no wider than the rest on
   the canal (0.8 to 1.1 times). Built without Yadav, the rule's held-out log loss is 0.053, 0.044 and
   0.041 nats worse than the plain rule's at one, two and three bodies (SE 0.037 to 0.051), better on 2
   to 3 of the 22 populations, and Front. Phys. 2026's population loses 0.81 nats at three bodies, its
   end-plate prior left to Tan 2004 alone; built without Front. Phys. 2026 it is 0.013 and 0.026 worse at
   two and three bodies (0.004 better at one), Busscher 2010, Moncada-Habib 2025 and Tan 2004 losing 0.16
   to 0.21; one vote per population for the SD is within 0.006 of plain. Tempered, every one of them is
   within 0.012 nats of the tempered plain rule (0.849 to 0.861 at three bodies), so no paper leaves the
   prior and the rule to carry is still the plain rule tempered by T = 2 (table exclusion, figure
   fig16_exclusion, section Leaving a paper out, scored held out).
14. **Covariates both ways, from what 22 papers print apart: men exceed women by about 1.3 within-sex
   SDs on the vertebral body and end plate, 0.5 to 0.7 on the pedicle, 0.45 on the canal's width and
   nothing on its depth; age moves a measure by under a fifth of an SD a decade; held out by paper, an
   effect's sign carries to a new population (85% of strata) but its size only partly, so one measure
   names a person's sex with an AUC of 0.63 against the population's own 0.64 and a log loss of 0.680
   against the base rate's 0.693.** The owner's words of 2026-10-30, 02:55 UTC: show the covariate
   effects on the spine's shape and predict either from the other. Each effect is read inside one paper
   first, men against women of one stratum or a series over age or size bands, and the papers pooled
   second, so no paper's own shift enters it; the papers' own men's and women's rows, which the
   reread's snapshot pools, are read from the sexes' snapshot (data/series_sexes.csv), and a stratum
   printed with means alone is read against the other papers' SD. Sex, pooled: the body's sagittal
   diameter 1.33 within-sex SDs over four papers (an interval for one more paper of 0.41 to 2.25),
   Griffith 2016's body area 1.42, Tang 2016's end plates 1.31 to 1.56, Duman 2026's body heights 1.21
   to 1.31, the pedicle's width 0.72 and height 0.55 over six papers each, the canal's width 0.45 over
   six (0.32 to 0.58 for one more paper) and its depth -0.03 over ten. Age per decade: Bach 2019's
   foramen -0.19 and disc heights -0.14 to 0.06, Griffith's body area 0.09, the pedicle 0.05 to 0.07
   (Yu 2015, Duman). Held out over 20 papers and 357 strata (the median stratum): AUC 0.63 against the
   population's own 0.64, R^2 0.03 against 0.06, log loss 0.680 against 0.654 own and 0.693 for the
   base rate; Tang's end plate (0.82) and Twomey 1985's disc height (0.86) name sex best. One measure is
   the honest unit, since no paper prints the correlation within a person; the combination waits for
   measured people with their sex and age, the gold tier 3 join on the grid (table covariates, figure
   fig17_covariates, section Covariates both ways).
15. **Bounds for a generator: yes, as a card a synthetic cohort must pass, and schwingcheck's generator
   fails it on the level steps.** The owner's question of 2026-10-30, 03:38 UTC: could these results
   "serve as bounds for generative models making synthetic spines from ideal spines". The card holds,
   for 694 cells of 53 measures and 635 level-to-level steps, the interval for a new population's mean,
   SD and step, and for 222 cells the sex contrast; calibrated on 33 papers each held out, a cohort
   passes where its mean, SD and step pass rates reach the 10th percentile of the held-out papers'
   (0.58, 0.53 and 0.89), every cell scored as if the cohort had 40 people, the bar papers' own size.
   The card's centre, the ideal spine, passes (every mean and SD, 98.6% of steps); the same spine with
   its lumbar gradient flattened or reversed fails on the steps (0.87 and 0.79) while its means pass;
   schwingcheck's generator on Panjabi's table fails on the steps (0.86, means 0.70), and so does the
   point nearest the papers (0.80) (figure fig19_bounds, section Bounds for a generator).
16. **Told the person's sex, naming a short field gains nothing held out, and little even where the sexes'
   tables are a population's own.** The owner's words of 2026-10-30, 03:45 UTC: the sex of the patient
   being imaged is known, so the rule may read it. Each of 16 papers held out on its own men and women,
   the others' table moved by the others' sex contrast scores within 0.003 nats of the same table
   unmoved at one, two and three bodies (SEs 0.006 to 0.009), and names 0.1 to 0.2 points more often.
   Had the others printed the held-out paper's own contrast, the gain would be 0.007 to 0.011 nats; with
   its own two tables in place of its own sexless one, 1.0 to 1.7 points; its own sexless table in place
   of the others' is worth 5.9 to 8.4 points. On synthetic populations split by the papers' own
   contrasts, the gain is 1.9 points at one body, 1.1 at two and none at three. Which population a
   person comes from matters about five times more than the sex (figure fig18_sex_naming, section
   Naming told the person's sex).
17. **Real CTs on the card: gold tier 3's two cohorts pass the body and end-plate steps and keep the
   sex contrasts' sign, and fail the steps on the discs and the pedicles.** The gold tier 3 join on the
   grid (SchwingNet's job 40878978) printed each sex's moments for autoPET's 857 adults and
   TotalSegmentator's 133, measured by the engine. Scored as a generator is, at 40 people a cell, both
   pass the means and SDs and fail the steps (0.79 and 0.83 against the bar's 0.89); their body and
   end-plate steps pass at 0.94 and 0.99, their discs' at 0.74 and 0.65, their pedicles' and canal's at
   0.64 and 0.70. The pedicles leave the papers' at T10 to T12 and from L3 down (27 mm wide at L5
   against 15), the known defects of the engine pinned before bordercall PR 44; the disc failures, at
   the step to L4-L5 and at T10 to T12, are unexplained, and the first may be the people's age. Their sex contrasts have the papers' sign
   at 127 of 130 cells and lie inside the card's interval for a new population at 93 of 118 and 99 of
   122, a little smaller than the papers' (figure fig20_gold3, section Real CTs on the card).

## What was compared

**The generator.** schwingcheck draws each value as s^p (mu + sd (rho z + sqrt(1 - rho^2) e)) + error n:
Panjabi's mean and SD at that level, a person's size s (log-normal, scale_sd 0.07) to the measure's power
p, a person's offset z shared by every level of a measure (rho 0.5), the level's own part e, and the CT's
error of one reading (1 mm for a length, sqrt(pi A / 2) for an area, 3 degrees for an angle), measured
lengths and areas held at a floor of 0.5 (angles have none). synthval/population.py draws the same model
vectorised and keeps the true anatomy, the measured value and the size apart, and tests/test_synthval.py
holds its moments to columns.draw_columns within five standard errors at every measure and level.

**The papers.** data/literature_series.csv is the part of the reread's series.csv this note can use, cut
at 401aaee with its sha256 in data/SOURCE.json; `python3 -I snapshot.py --write 401aaee` cuts it again to
the same bytes, and `--check` says whether it still matches. synthval/literature.py turns rows into
series by eight rules written in its docstring, each counted in records/selection.json: the paper's own
values; human adults not selected for a spinal disease or anomaly, the cohort read as well as the group
(patients scanned for back pain stay in: Cizmic 2023's CTs, Olsewski's Part 3 and Ahmed 2019's MRIs,
since a pain is not an anatomy); one of the pool's 32 measures under Panjabi's definition or one close
to it; one technique and one set of people per cohort, measure and level; one group per cohort where the
whole is printed; the sexes pooled where printed apart; a mean, an SD and a count of people; and no
length or area under half or over twice the mean of its series' printed neighbours. That last rule was
written for Tan's lower end-plate area at L3, printed as 172 mm2, which the reread has since left out of
series.csv, so the rule catches nothing and stays as a guard. 25 of the 39 papers give a usable series.
Zindrick's counts are of films and scans pooled, so his series are a mixed modality that no comparison
pools. Both end-plate inclinations are kept, by the owner's choice of 2026-10-29 09:01 UTC that every
study score all 32 measures as printed (bordercall TODO.md, step b; pull request 31), though their
lumbar rows reprint Panjabi's cervical ones (research_notes/panjabi-endplate-inclination.md on the
reread's branch); only Tan's series measure either, so they enter no pooled cell.

<!-- table selection -->
| what | count |
| --- | ---: |
| rows of the 32 measures in the snapshot | 2407 |
| series formed | 954 |
| series with a mean, an SD and a count of two or more | 903 |
|   of them bone | 532 |
|   of them CT | 210 |
|   of them film | 59 |
|   of them mixed | 68 |
|   of them MRI | 34 |
|   of them with a count this note sets from the cohort file or the paper (n is the printed pedicles halved 29) | 29 |
|   of them with Tan's uncertain SDs (weighting the means, left out of the published SD) | 416 |
|   of them one sex only | 48 |
| papers behind the usable series | 25 |
| rows left out: quoted from another study | 778 |
| rows left out: a stratum of a cohort printed whole | 170 |
| rows left out: definition differs | 159 |
| rows left out: selected, diseased or example group | 137 |
| rows left out: a meta-analysis pooling other series | 80 |
| rows left out: another technique on the same people | 45 |
| rows left out: the other sex, not pooled (no SD or no count) | 41 |
| rows left out: not human | 28 |
| rows left out: a cohort whose people another cohort holds | 15 |
<!-- end selection -->

**The comparison.** Bone and CT series pool together as the main comparison, film and MRI apart, since
film magnifies and MRI reads soft tissue. 12 of the 32 measures have no published series at all, the
inferior facet's width, both facets' heights, areas, transverse and sagittal angles and the three
interfacet distances, so they are held to no paper; they carry 56% of the generator's sign flags
(records/qi.json, sign by measure). Means pool by REML with the prediction interval of Higgins,
Thompson and Spiegelhalter on t(k - 2), SDs on the log scale (synthval/pooling.py). Tan's SDs, whose
conversion from standard errors the reread could not settle, weight the pooled means and set the spread
between series like any other series', but the published SD a synthetic SD is held to leaves them out:
it is pooled where two other series print one, the one series' where one does, and there is none in the
281 cells that Tan alone covers. d is the distance from the papers' mean in Panjabi's SD at that level,
the SD the generator draws with, so a shift reads as what it costs the rule.

## Means

<!-- table means -->
| Panjabi's means and SDs against the papers (bone and CT) | all series | without Tan 2004 |
| --- | ---: | ---: |
| cells (measure, level) with a bone or CT series | 421 | 140 |
|   of them on Tan 2004 alone | 281 | - |
|   with three series or more, so pooled with an interval | 57 | 34 |
|     cells by the number of series behind them | 3: 23, 4: 7, 5: 7, 6: 4, 7: 1, 8: 5, 9: 6, 10: 4 | 3: 7, 4: 7, 5: 4, 6: 1, 7: 5, 8: 6, 9: 4 |
|   Panjabi's mean outside the 95% prediction interval | 0 | 0 |
|     of the cells with five series or more (27; 20) | 0 | 0 |
|   Panjabi's mean differs from the pooled mean, his twelve spines' SE taken in: z / t(k - 1) | 16 / 10 | 14 / 8 |
|     of them with Panjabi's mean above | 16 / 10 | 11 / 8 |
|     his mean taken as exact, as a stricter reading would | 25 (23 above) | 20 (16 above) |
| Panjabi - papers in his SDs, median (all cells) | 0.69 | 0.17 |
|   share of cells where he is above | 76% | 58% |
|   the same, absolute | 0.91 | 0.88 |
|   share of cells more than one of his SDs away | 45% | 44% |
|   absolute, in the papers' SD (cells with one) | 1.29 | 1.34 |
| cells with a published SD: pooled from two series or more / one series / none (Tan's alone) | 57 / 83 / 281 | 57 / 83 / 0 |
| Panjabi's SD over the papers' SD, quartiles (140 cells; 140) | 1.13 / 1.51 / 2.23 | 1.13 / 1.51 / 2.23 |

| synthetic population | values | cells | absolute d of its mean, median (Panjabi's SDs) | absolute d over 1 (%) | its SD over the papers', median (quartiles) | SD inside the papers' SD interval |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| generator | measured | 421 | 0.92 | 47 | 1.86 (1.45 to 2.79) | 26 of 34 |
| generator | true | 421 | 0.92 | 46 | 1.71 (1.35 to 2.38) | 27 of 34 |
| nearest the papers | measured | 421 | 0.91 | 45 | 1.24 (0.93 to 1.89) | 30 of 34 |
| nearest the papers | true | 421 | 0.91 | 45 | 0.98 (0.77 to 1.42) | 29 of 34 |
| size_removed | measured | 421 | 0.91 | 45 | 1.71 (1.25 to 2.57) | 27 of 34 |
| size_removed | true | 421 | 0.91 | 45 | 1.53 (1.13 to 2.23) | 27 of 34 |

| SD over the papers', median | cells with a published SD | Panjabi's | generator, true | measured | nearest point, true | measured |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| angles | 34 | 2.83 | 2.82 | 3.20 | 1.69 | 2.34 |
| lengths and areas | 106 | 1.35 | 1.53 | 1.71 | 0.89 | 1.08 |
| the seven SPINEPS measures | 57 | 1.35 | 1.60 | 1.71 | 0.91 | 1.10 |
<!-- end means -->

The prediction interval and the tests against the pooled mean answer different questions. The first
asks whether Panjabi's twelve spines could be one more population among the papers', and the answer is
yes everywhere, partly because with three series that interval takes t on one degree of freedom and is
too wide to test much. The interval the table counts is widened by his twelve spines' sampling variance,
sd^2 / 12 under its root (run.py, inside_prediction); the Higgins interval alone leaves his mean out in
one cell, the pedicle's width at T11 (9.75 against 5.55 to 9.30, four series), and in none without Tan.
The film and MRI series, kept apart, cover 68 cells of 11 measures: there Panjabi's mean sits a median
0.13 of his SD below the papers', his SD is 1.16 times theirs, the generator's true SD 1.38 times (1.45
measured) and the nearest point's 0.79 (records/validation_cells.csv, modalities film_mri). The second asks whether he sits at their centre. With his twelve spines' SE taken
in, which a sample of twelve has, he does not in 16 cells by z and 10 by t, all above; taken as exact, a
stricter reading than his twelve can bear, in 25. Both are true at once: his spines are a plausible
population, a large one in some respects.

Tan matters both ways. The 281 cells only he covers put Panjabi a median 0.83 of his SD above, which
lifts the median over all cells. In the 140 cells others cover, Tan's series pull the pooled mean down,
adding to Panjabi's excess: with them in, Panjabi sits 0.52 above (0.76 absolute); with them out, 0.17
(0.88 absolute, since some measures then read further below, the posterior height at 1.96 rather than
0.75). In the papers' own SD, where a cell has one, the absolute distance is 1.29 (1.34 without Tan). The
synthetic populations' means are Panjabi's, so they sit as far from the papers as he does, and only their
spread changes with the setting.

<!-- table by_measure -->
| measure | cells | pooled (3 series or more) | with a published SD | Panjabi - papers (his SDs) | same, absolute | Panjabi - papers, Tan left out (cells) | Panjabi's SD over the papers' | measured SD over the papers': generator | size taken out | nearest point |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| canal_ap | 22 | 5 | 6 | 1.56 | 1.56 | 1.27 (6) | 1.12 | 1.43 | 1.25 | 0.94 |
| canal_area | 22 | 5 | 5 | 0.88 | 0.88 | 0.23 (5) | 0.99 | 1.26 | 1.02 | 0.76 |
| canal_w | 22 | 5 | 5 | 1.31 | 1.31 | 0.36 (5) | 0.90 | 1.22 | 0.99 | 0.76 |
| endplate_area | 22 | 0 | 0 | 0.46 | 0.46 | - (0) | - | - | - | - |
| endplate_depth | 22 | 0 | 6 | 1.43 | 1.43 | 1.36 (6) | 1.42 | 1.76 | 1.47 | 1.05 |
| endplate_incl | 22 | 0 | 0 | -0.39 | 0.44 | - (0) | - | - | - | - |
| endplate_lower | 22 | 5 | 6 | 0.96 | 0.96 | 0.19 (6) | 1.90 | 2.46 | 1.95 | 1.43 |
| endplate_lower_depth | 22 | 0 | 6 | 1.61 | 1.61 | 1.26 (6) | 1.05 | 1.42 | 1.12 | 0.85 |
| endplate_lower_incl | 22 | 0 | 0 | 2.29 | 2.34 | - (0) | - | - | - | - |
| h_post | 22 | 7 | 22 | -0.75 | 0.75 | -1.96 (22) | 1.40 | 1.80 | 1.62 | 1.25 |
| pedicle_area | 22 | 0 | 5 | -0.16 | 0.22 | -0.66 (5) | 0.95 | 1.15 | 0.98 | 0.69 |
| pedicle_h | 22 | 9 | 17 | 1.03 | 1.03 | 0.82 (17) | 1.31 | 1.59 | 1.45 | 1.07 |
| pedicle_incl_sag | 22 | 7 | 17 | 0.25 | 0.27 | 0.09 (17) | 3.66 | 3.82 | 3.82 | 2.42 |
| pedicle_incl_trans | 22 | 0 | 17 | 0.04 | 0.45 | -1.01 (17) | 2.37 | 2.92 | 2.92 | 2.22 |
| pedicle_w | 22 | 9 | 17 | 0.68 | 0.68 | 0.99 (17) | 1.78 | 1.97 | 1.93 | 1.27 |
| spinous_length | 22 | 0 | 0 | 0.35 | 0.60 | - (0) | - | - | - | - |
| transverse_width | 22 | 0 | 0 | 1.76 | 1.76 | - (0) | - | - | - | - |
| endplate | 21 | 5 | 6 | 0.98 | 0.98 | 0.07 (6) | 1.69 | 2.44 | 1.90 | 1.42 |
| endplate_lower_area | 21 | 0 | 0 | 0.53 | 0.63 | - (0) | - | - | - | - |
| facet_w_sup | 5 | 0 | 5 | -1.26 | 1.26 | -1.26 (5) | 1.28 | 1.43 | 1.35 | 0.92 |
<!-- end by_measure -->

Columns five to seven are Panjabi's own table against the papers, the seventh with Tan's series left out
and the count of cells that leaves; the last four are the median ratio of an SD to the published SD, his
own and the measured synthetic SD at three settings (below); a dash is a measure whose cells have no
published SD, or none but Tan's. Of the seven measures the rule reads, the three depths sit furthest
above the papers: the canal's a median 1.56 of his SDs (1.27 without Tan), the end-plates' 1.43 and 1.61
(1.36 and 1.26); without Tan the posterior height sits further still, 1.96 below. Why is not recorded
here; a difference of definition the reread's mapping did not catch would read the same. The two
inclinations' rows run C3 to L5, Panjabi's printed values against Tan's angles at every level. Only at L1
to L5 do Panjabi's rows reprint his cervical ones (there the medians are 0.02 and 0.24); the lower
plate's 2.29 comes from T1 to L2, where Tan's means are negative (-1.1 to -4.1) and Panjabi's positive
(1.2 to 4.0).

## Spread

Panjabi measured twelve spines, and his SDs are already 1.51 times the papers' at the median (quartiles
1.13 to 2.23), 2.83 times for the angles and 1.35 for lengths and areas. The generator then draws a size
of its own and multiplies, so its spread counts the size a second time: 1.71 for the true anatomy, 1.53
for lengths and areas. sd_mode "size_removed" takes the size's share out of his SDs before drawing,
which leaves his own excess; the nearest point shrinks every SD to 0.6 of his and halves the size's
spread. The validation's 20,000 people give the nearest point's SDs as 0.98 of the papers' for the true
anatomy and 1.24 measured; the grid's own reading on 4,000 people, chosen among 480, gave 0.98.

Neither figure is the like-for-like one. A published bone or CT SD carries its own technique's error of
one reading, a caliper's 0.35 to 0.95 mm or a CT's 0.2 to 1.2 mm (table assumptions), mostly smaller than
the generator's 1 mm; for a length whose SD is 2 mm an error of 0.5 mm adds 3% to the SD and 1 mm adds
12%. So the fair ratio lies between the true and the measured one, nearer the true for these series. At
the nearest point, chosen on the true SDs, the lengths sit at a median 0.90 of the published SDs
(records/validation_cells.csv). Taking a technique error e out of each published SD as sqrt(sd^2 - e^2),
and counting only the cells whose published SD exceeds it (96 of 96 up to 0.6 mm, 87 at 0.95 mm, 72 at
1.2 mm), the nearest point's lengths read 3 to 9% narrower than the papers' anatomy for an error of 0.2
to 0.5 mm, about as wide at 0.6 to 0.65 mm, 3% wider at 0.7 to 0.75 and about 9% wider at 0.95 to 1.2
mm. Its areas sit at 0.67 and its angles at 1.69.

## Structure

<!-- table structure -->
| correlation of subject means, L1-L5 | Griffith, men | women | sexes together | generator | size taken out | nearest point |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| canal area with body area | 0.29 | 0.25 | 0.32 | 0.59 | 0.78 | 0.44 |
| canal w with body area | 0.44 | 0.37 | 0.48 | 0.58 | 0.77 | 0.44 |
| canal ap with body area | 0.29 | 0.20 | 0.24 | 0.56 | 0.72 | 0.41 |
| canal ap with canal w | 0.61 | 0.55 | 0.58 | 0.50 | 0.63 | 0.37 |

| measure | cells | printed equal | share of the body's sex difference | quartiles | generator | papers (cells) |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| canal_ap | 15 | 9 | 0.00 | -0.47 to 0.00 | 1 | eisenstein1977 15 |
| canal_w | 15 | 1 | 0.35 | 0.33 to 0.37 | 1 | eisenstein1977 15 |
| endplate | 5 | 0 | 1.05 | 0.98 to 1.08 | 1 | chen2011 5 |
| endplate_depth | 5 | 0 | 0.99 | 0.96 to 1.01 | 1 | chen2011 5 |
| endplate_lower | 5 | 0 | 0.96 | 0.93 to 1.11 | 1 | chen2011 5 |
| endplate_lower_depth | 5 | 0 | 0.97 | 0.91 to 0.99 | 1 | chen2011 5 |
| pedicle_w | 12 | 0 | 0.34 | 0.23 to 0.44 | 1 | duman2026 12 |

The body's unit, log(men/women) = 0.133, is the median over the pairs of the upper end-plate width and the upper end-plate depth (chen2011 10), one population's; the rows for those measures are the unit itself.
<!-- end structure -->

Griffith's are the only correlations between body and canal measures any of the 39 papers prints, over
540 men and 540 women apart, on CT (Makino 2012 prints regressions of the pedicle's least diameter on its
transverse and sagittal widths, at each lumbar level). The synthetic ones are read on measured values, as
his carry a CT's error, and each of the generator's two end-plate areas stands in for his mid-pedicle
section on its own, the two correlations averaged. The generator has no sex, so it is held to his two
sexes taken together (structure.mixed_sex_r, from his within-sex correlations and his means and SDs by
sex). Mixing the sexes raises a correlation only where both measures differ by sex, as the canal's width
and the body's area do (0.48 against 0.44 and 0.37 apart); the canal's depth barely does, so its
correlation with the body falls between the two sexes' (0.24, between 0.29 and 0.20). The generator sits
well above for the body (0.56 to 0.59) and below for the canal's depth with its width (0.50 against
0.58), since nothing but the size ties two measures of the canal. Taking the size out of Panjabi's SDs
lifts every correlation (0.63 to 0.78), since the size then carries more of what is left. The nearest
point, whose halved size spread (0.035) and rho of 0.9 bring them down (its narrower SDs and r_between of
0.2 alone would raise them), comes down to 0.44 for the canal's width and area with the body, below
Griffith's 0.48 for the width but still above for the area (0.32) and for the depth (0.41 against 0.24),
and to 0.37 for the canal's depth with its width, further below Griffith's 0.58.

The second table tests the generator's assumption that every length scales with one size. It rests on
three papers, the only ones whose own rows hold both sexes with ten or more of each in a group not
selected (Mitra 2002 and Olsewski 1990 print fewer, and the snapshot holds Griffith 2016 by sex only for
his largest and smallest quartiles): Eisenstein's skeletons for the canal (15 pairs each), Chen 2011's
end-plates (5 pairs each) and Duman's CTs for the pedicle's width (12 pairs). Ahmed 2019's pairs, which
this note's first run read, the reread now counts as reprints of its own Tables 1 and 2 (REPRINTS in the
paper-tables tools at 401aaee) and pools their sexes. The unit is Chen's upper end-plate's width and
depth, so each share sets one population's ratio against another's unit and mixes the measure's own
difference between the sexes with the populations'. The canal's width carries about a third of the body's
difference, and so does the pedicle's width in Duman's CTs (0.23 to 0.44). Griffith's own means by sex,
within one population (structure.GRIFFITH_SEX, from his paper beside the snapshot, which no record
repeats), put the canal's width at 0.61 of his body area's difference per length and its depth at 0.17:
log(23.66 / 22.26) and log(15.82 / 15.55) against half of log(1419.3 / 1162.9). The reread's error part
reads the same shares across populations, Griffith's canal against Chen's and van der Houwen's bodies
(synthesis/error.md at 448006f, L345: half to two thirds, and a fifth or less). So the canal width's
third rests on Eisenstein set against Chen's unit, as the pedicle's rests on Duman (below). The canal's depth carries little or none: 9
of Eisenstein's 15 pairs print the two sexes equal, and his other six print the women's canal one
millimetre deeper (-0.46 to -0.52 of the unit); his whole millimetres step by about half the unit, so his
pairs cannot tell a third from nothing. The lower end-plate, from Chen too, carries all of it. The
reread's error part reads the pedicle otherwise: Yu 2015's 503 skeletons a level, which the snapshot does
not hold by sex, give the pedicle's width a log ratio of men over women of 0.128 to 0.223, at or above
the body diameters' 0.094 to 0.128 (synthesis/error.md at 448006f, L333 and L335), so the pedicle's third
rests on Duman alone. A model that gave each measure its own loading on size (population.py holds the
option, loadings) might draw both the lower correlations and the sexes' differences; it is not tried
here.

Four ratios of means by level, L1 to L5, set the generator beside the papers that print them
(records/structure.json, ratios; fig3_structure C and D, fig7_quality C). Each synthetic ratio sits
within 0.03 of Panjabi's own ratio of means, as it must. Against the papers: the canal's depth over the
body's is 0.50 to 0.58 synthetic, below Alonge 2021's 0.58 to 0.70 and level with Amonoo-Kuofi 1985's
0.45 to 0.61; the canal's width over its depth is 1.27 to 1.41, below Cizmic 2023's 1.30 to 1.79, and the
gap grows down the lumbar spine (1.39 against 1.79 at L5); the transverse span over the end-plate's width
is 1.72 to 1.97, above Tan 2004's 1.48 to 1.79; and the canal's area over its width times depth is 0.63
to 0.73, below Tan's 0.70 to 0.83. The last two are Tan alone, so they are the one paper's shape against
Panjabi's twelve.

## Quality and curation

A vertebra a person could have holds relations that the papers' definitions make geometrically necessary,
whatever the population; synthval/qi.py writes each with its argument. None is fitted. Three unions are
read beside each indicator: "sign or inside", which no anatomy can fail; "any but floor", which adds box
and convex, bounds that hold only under their allowances (5% over for an end-plate's curved area, 15%
for a facet's) and the end-plate's near symmetry; and "any", which adds floor, the generator's clip of a
measured value at 0.5 rather than an anatomy.

<!-- table quality -->
| setting (% of vertebrae / % of people) | sign | inside | sign or inside | box | convex | any but floor | floor | any |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| generator, all 32 measures | 2.1 / 36 | 0.1 / 3 | 2.2 / 38 | 32.3 / 99 | 10.5 / 77 | 41.1 / 100 | 3.7 / 54 | 42.2 / 100 |
| generator, the seven SPINEPS measures | 0.0027 / 0.060 | 0.0 / 0 | 0.0027 / 0.060 | 0.0 / 0 | 0.0 / 0 | 0.0027 / 0.060 | 0.0055 / 0.12 | 0.0059 / 0.13 |
| size_removed, all 32 measures | 1.7 / 30 | 0.090 / 2 | 1.7 / 32 | 21.6 / 97 | 1.8 / 30 | 24.2 / 99 | 3.0 / 47 | 25.4 / 99 |
| size_removed, the seven SPINEPS measures | 0.00045 / 0.010 | 0.0 / 0 | 0.00045 / 0.010 | 0.0 / 0 | 0.0 / 0 | 0.00045 / 0.010 | 0.0032 / 0.070 | 0.0032 / 0.070 |
| nearest the papers, all 32 measures | 0.1 / 2 | 0.00091 / 0.020 | 0.1 / 2 | 6.0 / 43 | 0.7 / 7 | 6.7 / 48 | 0.5 / 10 | 7.1 / 51 |
| nearest the papers, the seven SPINEPS measures | 0.0 / 0 | 0.0 / 0 | 0.0 / 0 | 0.0 / 0 | 0.0 / 0 | 0.0 / 0 | 0.0 / 0 | 0.0 / 0 |

| setting | people kept | dropped | for sign | for inside |
| --- | ---: | ---: | ---: | ---: |
| generator | 6207 | 3793 | 3611 | 282 |
| nearest the papers | 9795 | 205 | 205 | 2 |
| size_removed | 6849 | 3151 | 3018 | 196 |
<!-- end quality -->

The seven SPINEPS measures are almost never flagged because no indicator ties two of them: only sign and
floor reach them, through a canal depth drawn at or below zero or held at the floor, in 13 of 10,000
people at the generator and none at the nearest point. The rate is set by the SDs (sd_scale, sd_mode),
a little by r_between, by the CT's error only through the floor, since box, convex and inside read the
true anatomy, and not at all by the size's spread, since size scales an area and its rectangle alike
(table state_space). The six phenotypes of model.py carry the same rates as the typical column, 41.8 to
42.5% of vertebrae. Curation drops a person only for sign or inside, which no definition allows: 3,793 of
10,000 at the generator, 205 at the nearest point. Box and convex are left as indicators, since their
allowances are judgements.

## State space

Each axis was moved alone from the generator's point (the first table), then a grid of the four axes that
set the spread and the correlations was searched (synthval/sweep.py: scale_sd 0 to 0.07, sd_scale 0.6 to
1.0, rho 0.25 to 0.9, r_between 0 to 0.6, 480 points), each scored by the squared log of its median SD
ratio (true anatomy, cells with a published SD) plus the mean squared distance of its four correlations
from Griffith's sexes taken together. The first table's last column counts the cells (measure, level)
where size_removed holds the level's own SD at a tenth of the printed one, and, in parentheses, those of
them where the size alone passes the printed SD, leaving none of the level's own.

<!-- table state_space -->
| point | SD ratio, true | SD ratio, measured | neighbour r | mean Griffith-pair r | sign or inside (% vertebrae) | any but floor (% vertebrae) | any but floor (% people) | cells held at a tenth of the SD (the size alone passing it) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| generator | 1.70 | 1.86 | 0.39 | 0.55 | 2.3 | 40.8 | 100 | 0 |
| scale_sd=0.0 | 1.53 | 1.70 | 0.25 | 0.01 | 2.4 | 40.9 | 100 | 0 |
| scale_sd=0.035 | 1.56 | 1.74 | 0.29 | 0.24 | 2.3 | 40.8 | 100 | 0 |
| scale_sd=0.05 | 1.60 | 1.78 | 0.33 | 0.39 | 2.3 | 40.8 | 100 | 0 |
| scale_sd=0.1 | 1.87 | 2.04 | 0.49 | 0.71 | 2.3 | 40.8 | 100 | 0 |
| rho=0.0 | 1.69 | 1.86 | 0.20 | 0.69 | 2.3 | 40.8 | 100 | 0 |
| rho=0.25 | 1.68 | 1.86 | 0.24 | 0.65 | 2.3 | 40.7 | 100 | 0 |
| rho=0.75 | 1.70 | 1.86 | 0.64 | 0.44 | 2.3 | 40.9 | 99 | 0 |
| rho=0.9 | 1.70 | 1.86 | 0.84 | 0.38 | 2.3 | 40.9 | 95 | 0 |
| phi=0.3 | 1.69 | 1.86 | 0.57 | 0.50 | 2.3 | 40.8 | 100 | 0 |
| phi=0.6 | 1.68 | 1.86 | 0.75 | 0.44 | 2.3 | 40.8 | 100 | 0 |
| phi=0.9 | 1.69 | 1.87 | 0.93 | 0.37 | 2.3 | 41.1 | 98 | 0 |
| r_between=0.2 | 1.69 | 1.87 | 0.39 | 0.60 | 2.3 | 38.9 | 100 | 0 |
| r_between=0.4 | 1.69 | 1.86 | 0.39 | 0.65 | 2.3 | 36.8 | 100 | 0 |
| error_scale=0.5 | 1.70 | 1.76 | 0.39 | 0.56 | 2.3 | 40.8 | 100 | 0 |
| error_scale=2.0 | 1.70 | 2.27 | 0.39 | 0.51 | 2.3 | 40.8 | 100 | 0 |
| sd_scale=0.7 | 1.30 | 1.49 | 0.49 | 0.70 | 0.3 | 15.6 | 94 | 0 |
| sd_scale=0.85 | 1.48 | 1.68 | 0.43 | 0.62 | 1.0 | 27.9 | 100 | 0 |
| sd_mode=size_removed | 1.52 | 1.70 | 0.43 | 0.72 | 1.8 | 24.0 | 99 | 34 (32) |
<!-- end state_space -->

<!-- table grid -->
| scale_sd | sd_scale | rho | r_between | SD ratio, true | neighbour r | any (% vertebrae) | distance |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.035 | 0.60 | 0.90 | 0.20 | 0.98 | 0.83 | 7.1 | 0.023 |
| 0.035 | 0.60 | 0.75 | 0.20 | 0.98 | 0.62 | 7.8 | 0.026 |
| 0.000 | 0.70 | 0.90 | 0.40 | 1.07 | 0.81 | 8.9 | 0.026 |
| 0.010 | 0.70 | 0.90 | 0.40 | 1.06 | 0.81 | 8.9 | 0.026 |
| 0.020 | 0.60 | 0.90 | 0.40 | 0.94 | 0.82 | 4.8 | 0.027 |
| 0.020 | 0.60 | 0.75 | 0.40 | 0.93 | 0.58 | 6.1 | 0.028 |
| 0.035 | 0.60 | 0.50 | 0.00 | 0.98 | 0.36 | 9.4 | 0.028 |
| 0.020 | 0.70 | 0.90 | 0.40 | 1.09 | 0.82 | 8.9 | 0.028 |

480 points searched; the eight nearest shown. The nearest sits on the grid's edge in rho (0.90) and sd_scale (0.60); past it, with the other axes held, rho 0.99 reads 0.023, rho 0.95 reads 0.023, sd_scale 0.55 reads 0.032, sd_scale 0.50 reads 0.054.
<!-- end grid -->

The nearest point sits on two of the grid's edges, the lowest sd_scale and the highest rho, so
sweep.beyond_edges reads past them with the other axes held (the line under the table). The SDs' scale is
pinned: past 0.6 the distance grows (0.032 at 0.55, 0.054 at 0.5). rho is not: 0.95 and 0.99 read as near
as 0.9, a shade nearer (0.0231 and 0.0230, against 0.0234), so the papers want a high correlation between
a measure's levels and cannot say how high. Nor is the size's spread, though the nearest point sits
inside the grid at 0.035: the next three points, at 0.026, take 0.035, 0 and 0.01, with r_between 0.2 or
0.4 and sd_scale 0.6 or 0.7, since a between-measure correlation stands in for the size in Griffith's
correlations and a wider SD for it in the spread. The four points within 0.004 of the nearest change
order from one draw to the next, though the nearest stayed first in six seeds of 4,000 people, a check
run beside the records, which hold seed 11 alone (records/RECORD.json), and the
gold persons' first measurable number is the correlation between neighbouring levels (item 7).

## Naming across the state space

The exact rule on the seven SPINEPS measures with the CT's errors, on fields drawn at points of the state
space. "1 body" is the share of fields of one body named exactly; "rule matched" is a rule built for the
point's own setting where a rule can hold it: the generator's column is blank, since its rule is its
own, and the phi and r_between rows repeat the generator's rule, since no rule holds either. The nearest
point's matched rule holds its SDs, size spread and rho and ignores its r_between of 0.2
(records/naming.csv, rule_ignores), so figure fig5_naming, which draws a matched rule only where it holds
the whole setting, leaves it out with phi's and r_between's.

<!-- table naming -->
| point | 1 body | 3 | 9 | rule matched: 1 | 3 | 9 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| generator | 47.5 | 72.8 | 95.6 |  |  |  |
| scale_sd=0.035 | 50.2 | 74.2 | 96.0 | 51.9 | 76.9 | 96.2 |
| scale_sd=0.1 | 44.2 | 70.7 | 95.4 | 44.7 | 71.0 | 95.5 |
| rho=0.25 | 47.0 | 72.9 | 95.3 | 47.0 | 73.6 | 95.8 |
| rho=0.9 | 47.3 | 74.5 | 98.3 | 47.3 | 80.8 | 99.4 |
| phi=0.6 | 46.7 | 73.6 | 96.3 | 46.7 | 73.6 | 96.3 |
| r_between=0.4 | 47.5 | 73.5 | 95.9 | 47.5 | 73.5 | 95.9 |
| error_scale=2.0 | 39.1 | 61.8 | 88.9 | 40.3 | 63.9 | 90.3 |
| sd_mode=size_removed | 56.9 | 84.2 | 99.1 | 60.0 | 87.8 | 99.7 |
| sd_scale=0.7 | 51.2 | 76.1 | 97.4 | 53.1 | 77.9 | 97.8 |
| nearest the papers | 57.1 | 80.2 | 99.0 | 61.0 | 86.2 | 99.7 |
<!-- end naming -->

Doubling the CT's error costs more than any other axis, 8 points at one body. A narrower population names
better: taking the size out of the SDs gains 9 points at one body and 11 at three, the nearest point 10
and 7. At nine bodies the nearest point's gain is mostly rho's: rho 0.9 alone names nine in 98.3%, the
nearest 99.0%, while a narrower SD alone (sd_scale 0.7, the table's nearest to the point's 0.6) reaches
97.4%. phi and r_between, which no rule here can hold, cost almost nothing.

## Power, rerun

research_notes/cadaver-power part B took the spread between studies from Panjabi's comparison tables, a
median 0.39 of a person's SD over 86 cells, which it calls one reading of several (its pooled reading is
0.72) and corrects to 0.48 to 0.53 for the low reading of few series (cadaver-power/README.md L109 to
L116 and L349 to L353). The 39 papers' own series give it again, from the REML spread in every cell with
three series or more, its sampling error already out. REML's spread reads low with few series, its
median near 0.83 of the truth at three: had the truth been 0.83 in every cell, the median would read
0.75. No cell here reads zero. The calibrated column is the spread that, given to every cell with its own
series' counts and SEs, makes the expected median the one observed (synthval/power.py,
calibrated_median_f); it corrects the median, not the spread of the spread. Set like for like, the
papers' spread is 2.1 times part B's raw median and 1.7 to 1.9 times its corrected one. The worth in
scans is part A's ceiling, (sd^2 + e^2) / tau^2 scans of the population named for an infinite pool,
with the papers' SD as a person's, and with Panjabi's beside it as part B read it.

<!-- table spread -->
| spread between series | cells | tau / Panjabi's SD, median (quartiles) | calibrated | tau / papers' SD | calibrated | worth in scans, the papers' SD (calibrated) | the same, Panjabi's SD (calibrated) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| part B before (Panjabi's comparison tables) | 86 | 0.39 |  |  |  |  |  |
| 39 papers, main | 57 | 0.83 (0.61 to 1.11) | 0.92 | 1.15 | 1.28 | 1.0 (0.8) | 1.7 (1.4) |
| 39 papers, same definition only | 17 | 0.87 (0.79 to 1.03) | 0.98 | 0.92 | 1.04 | 1.4 (1.1) | 1.4 (1.2) |
| 39 papers, without tan2004 | 34 | 0.63 (0.48 to 0.88) | 0.69 | 0.81 | 0.88 | 1.9 (1.6) | 2.8 (2.4) |

| split of the spread | series x measure | distances | shift, whole measure (calibrated) | level by level (calibrated) | total (calibrated) |
| --- | ---: | ---: | ---: | ---: | ---: |
| all | 54 | 297 | 0.85 (0.94) | 0.41 (0.44) | 0.94 (1.04) |
| same definition only | 13 | 68 | 0.80 (0.90) | 0.34 (0.39) | 0.87 (0.98) |
| without tan2004 | 39 | 194 | 0.75 (0.83) | 0.42 (0.45) | 0.86 (0.95) |

Drawn with a shift of 0.90 and a rest of 0.40, 24 sets of series laid out as the papers' give the moments 0.81 and 0.38 and the calibrated pair 0.91 (SE of the mean 0.019) and 0.40 (SE 0.005); one set's calibrated pair, as the papers' is, varies by an SD of 0.093 and 0.027.
<!-- end spread -->

The split takes each series' distance from its cell's pooled mean and parts it into a shift that a paper
carries through a whole measure and a level-by-level rest. Its moments read low too, since the pooled
mean holds the series itself and the same paper's shift; the calibrated pair is the shift and rest that,
drawn into series laid out as the papers' are, give on average the moments the papers give
(shift_split); the line under the second table above says how well it finds a pair it was given.

<!-- table part_c -->
| the rule's table | shift / level (SD) | 1 body: exact (loss; right at 0.99) | 3 bodies | 9 bodies |
| --- | ---: | ---: | ---: | ---: |
| own table | 0.00 / 0.00 | 47.5 (0.0; 100.0) | 72.8 (0.0; 99.5) | 95.6 (0.0; 99.7) |
| part C, 0.3 SD level by level | 0.00 / 0.30 | 42.3 (5.2; 99.5) | 63.8 (9.1; 98.0) | 89.9 (5.7; 98.2) |
| part C, seven-r0 | 0.57 / 0.00 | 41.5 (5.9; 98.8) | 66.9 (6.0; 98.7) | 95.2 (0.4; 99.5) |
| 39 papers, all | 0.94 / 0.44 | 34.0 (13.5; 87.8) | 52.6 (20.2; 91.0) | 83.1 (12.5; 94.8) |
| 39 papers, without tan2004 | 0.83 / 0.45 | 35.5 (12.0; 90.0) | 56.4 (16.5; 91.8) | 83.6 (12.0; 94.5) |
| 39 papers, same definition only | 0.90 / 0.39 | 37.1 (10.4; 95.4) | 58.5 (14.3; 94.1) | 86.0 (9.6; 96.0) |
| 39 papers, all, one shift for every measure | 0.94 / 0.44 | 35.9 (11.6; 95.9) | 56.2 (16.7; 92.7) | 82.4 (13.2; 93.7) |

Each moved row is the mean over 4 tables of the same 300 columns; the own-table row is the one table itself.
<!-- end part_c -->

The first rows repeat cadaver-power's part C on this note's columns; the last four move the rule's table
by the calibrated split just measured, the last with one shift for every measure of a table, as a paper
whose whole method reads large would. On every table moved by the papers' split the rule's answers at
0.99 are right 88 to 96% of the time at one, three and nine bodies, the mean of four tables, against 99.5
to 100 on its own table, so the promise part C was framed around breaks, and not by noise: a single
table at one body ranges from 69 to 100% on 25 to 206 answers, and at nine bodies each such table answers
2,368 to 3,044 fields and none is right more than 98% of the time (records/power_naming.csv). The reread's
own comparison, on the papers' fields rather than on tables moved by a fitted spread, reads the same way
at 3aff843: at three bodies the rule built on Panjabi's table names 23.7% of the papers' fields exactly
against 47.2% of his own, and is right on 88.8% of the 660 it names at 0.99
(research_notes/paper-tables/results/README.md on the reread's branch). Without Tan's series, whose SDs
are uncertain, the spread is 0.63 (0.69 calibrated) and a pool is worth about 1.9 scans in the papers' SD
(2.8 in Panjabi's). Either way part A's answer, that no meta-analysis of published series matches 2,000
CT scans of the population named, gets stronger, on its assumption that the population named is
exchangeable with those pooled (cadaver-power/README.md L175 to L178). The usable series' cohorts are
from Singapore, China, India, Israel, Turkey, Saudi Arabia, Nigeria, Bosnia, Mexico, the Netherlands,
Taiwan, the United States, Germany, Italy and New Zealand (Germany and Israel inferred from Kunkel 2011's
and Gilad 1985's institutions, New Zealand where Robertson 2000's bones were studied; Zindrick 1987's
cohort names no country), so their spread is largely one between
populations, which is what a named population would be drawn from only if it were one more of them.

## Tan's population apart

Thread "Separate TAN population in synthetic data", 2026-10-29, project symphony_2, for greg's ask of
22:43 UTC: "separate the tan population from the rest to reduce variance and re-evaluate in a quick way
how that effects the power and accuracy of the predictor". The readings above pool every usable series
of a cell into one population of populations, Tan 2004's ten Chinese Singaporean cadavers among them.
Tan prints 22 levels of 19 measures, 417 of the 954 series, so he is one of three or four series in most
cells, and his means sit apart from the rest's: in the seven SPINEPS measures' 15 matched cells, where
the rest alone hold three series or more and Tan prints too, his mean sits a median 1.71 of Panjabi's SD
below the rest's pooled mean (quartiles 2.01 to 1.27), above it in none, and 2.8 of the rest's own spread
(records/tan-strata/matched_cells.csv). Pooled, that distance enters the spread between populations as if
any population could sit as far off, and every reading built on the spread widens with it: part A's worth
in scans, part B's f and the tables part C moves the rule by. Dropped, as the "without tan2004" rows
above drop him, his information goes with him and the cells compared change. Here Tan is a stratum of his
own (synthval/tan.py, run by tan_strata.py into records/tan-strata/): the rest's series pool as before,
Tan is one population, fixed, and the spread with him pooled in and with him apart is read on the same
cells. His SDs stay out of every published SD, as the validation leaves them out.

<!-- table tan -->
| spread between populations, Tan pooled in to Tan apart | cells | tau / Panjabi's SD, median | tau / papers' SD, median | worth in scans, the papers' SD | variance pooled / apart, median | Tan's distance from the rest (Panjabi's SD), median (quartiles) | cells with Tan above |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| every matched cell | 34 | 0.77 to 0.63 | 1.04 to 0.81 | 1.2 to 1.9 | 1.22 | -0.86 (-1.65 to -0.49) | 2 |
| the seven's cells | 15 | 0.87 to 0.63 | 1.01 to 0.79 | 1.1 to 1.9 | 1.87 | -1.71 (-2.01 to -1.27) | 0 |

The calibrated split of the spread is a shift of 0.94 and a rest of 0.44 with Tan pooled in (54 series by measure, 297 distances), 0.83 and 0.45 for the rest alone (39, 194).

| the rule's table | 1 body: exact (loss; right at 0.99) | 3 bodies | 9 bodies | SD of the loss between tables, 1 / 3 / 9 |
| --- | ---: | ---: | ---: | ---: |
| own table | 49.8 (0.0; 100.0) | 76.1 (0.0; 100.0) | 98.2 (0.0; 100.0) | 0.0 / 0.0 / 0.0 |
| before: 39 papers pooled | 39.5 (10.2; 100.0) | 56.6 (19.6; 98.2) | 84.9 (13.3; 96.8) | 1.9 / 3.3 / 3.7 |
| after: the rest without Tan | 40.1 (9.7; 100.0) | 56.9 (19.2; 98.2) | 84.7 (13.5; 96.0) | 2.2 / 3.0 / 3.2 |
| after: Tan's own table | 30.8 (19.0; 77.8) | 54.8 (21.4; 92.2) | 90.5 (7.7; 98.0) | 0.0 / 0.0 / 0.0 |

Each moved row is the mean over 2 tables of the same 40 columns, the before and after tables of one index drawn from the same standard draws; the rest's tables lose, paired with the pooled, -0.5 (SE 0.2) at 1, -0.3 (SE 0.2) at 3, 0.2 (SE 0.4) at 9 bodies. Tan's row is his one table (every level his own printed mean), and the own-table row is the generator's. Tan's median distance over the seven's 15 matched cells is 1.71 of Panjabi's SD; 12 persons find a shift of 0.89 in one cell, so a population as far off as Tan's shows in 100% of those cells from twelve gold persons.

| prediction for one more population, Tan pooled in to Tan apart | cells | half-width, t on k - 2 (Panjabi's SD), median | the same, the spread taken as known (z) | the rest's over the merged, median of the cells' ratios, t / z | the two strata as a mixture, t | cells with Tan inside the rest's, t / z | series held out | held-out series covered, t: merged / rest / mixture | z: merged / rest |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| every matched cell | 34 | 2.37 to 2.34 | 1.62 to 1.35 | 1.10 / 0.92 | 2.56 | 30 / 23 | 173 in 27 | 96 / 97 / 97 | 91 / 87 |
| the seven's cells | 15 | 3.07 to 2.97 | 1.84 to 1.32 | 1.09 / 0.74 | 3.40 | 11 / 5 | 63 in 12 | 100 / 100 / 100 | 97 / 87 |
<!-- end tan -->

The power readings. On the 34 matched cells the spread between populations is 0.77 of Panjabi's SD with
Tan pooled in and 0.63 with him apart (1.04 and 0.81 in the papers' SD), and on the seven's 15 it is 0.87
against 0.63: Tan's series nearly doubles the variance between populations in the seven's cells (a
median ratio of 1.87) and adds a fifth over all of them (1.22). Part A's ceiling moves with it: in the
seven's cells a pool of published series is worth a median 1.1 scans of the population named with Tan
pooled in and 1.9 with him apart, in the papers' SD; either is far under the 2,000 CT scans part A set
the pool against, so its answer stands. The calibrated split the rule's tables are moved by changes less,
a shift of 0.94 to 0.83 of a person's SD with the level-by-level rest as it was (0.44 and 0.45), since Tan
carries his distance as a whole-measure shift and the 39 series by measure left still spread.

The predictor. The rule is scored as part C scores it above, on the same columns and seeds, the rule's
table moved by the pooled split (before) and by the rest's (after), the two arms' tables of one index
drawn from the same standard draws so that their difference is the spreads' alone. On the quick record
in place (40 columns, 2 tables per arm; the full record of 300 columns and 8 tables is the next step
below), the rest's tables lose 9.7 points of exact naming at one body, 19.2 at three and 13.5 at nine,
against the pooled tables' 10.2, 19.6 and 13.3: paired table by table, 0.5 (SE 0.2) and 0.3 (SE 0.2)
points less at one and three bodies and 0.2 (SE 0.4) more at nine. Separating Tan therefore takes a
fifth to a half of the variance out of the spread, but moves the predictor's accuracy by under a point,
because the rule's loss is set by the whole-measure shift, which falls only from 0.94 to 0.83 SD. Tan's
own population is the harder case: the rule built on his means with Panjabi's SDs names the generator's
columns 19.0 points worse at one body, 21.4 at three and 7.7 at nine, and its answers at 0.99 are right
77.8, 92.2 and 98.0% of the time, so a population as far off as his is what breaks the 0.99 promise, and
twelve gold persons would show such a population in every one of the seven's matched cells.

The prediction (greg's word of 23:43 UTC: keep the populations separate and make "a metaanalysis style
prediction", never one merged population). The pool is already that: each paper's series is one study,
REML's tau the spread between them, and the prediction for one more population Higgins' interval, mean
+/- t(k - 2) sqrt(tau^2 + SE^2). Read three ways on the matched cells (synthval/tan.py,
prediction_by_stratum; the third table above; figure fig_tan_strata), keeping Tan apart narrows the
spread but not that interval: its half-width from the rest alone is wider than from the merged pool in
most cells, a median ratio of 1.09 (the medians of the half-widths, 2.97 against 3.07 of Panjabi's SD in
the seven's cells and 2.34 against 2.37 over all 34, point the other way, being medians of two sets
rather than of the cells' ratios, so the table prints the ratio too). The reason is the multiplier, not
the spread: Higgins' interval takes t on k - 2 degrees of freedom, a fixed allowance for a spread
estimated from k populations, and in the seven's cells the rest hold three series in 3 cells and four in
7, where t at 0.975 is 12.71 on one degree of freedom and 4.30 on two, against 4.30 and 3.18 with Tan's
series as one more; the narrower scale (a median ratio of 0.74) does not make that up. With the spread
taken as known (z in place of t) the rest's interval is a quarter narrower in the seven's cells (1.84 to
1.32) and, by the cells' ratios, an eighth over all (a median ratio of 0.92; the medians, 1.62 to 1.35,
overstate it), but held out one series at a time it covers 87% of the rest's series against its nominal
95% (151 of 173; a binomial at 95% gives so few 3 times in 10,000), the merged pool's 91%, while the t
intervals cover 97% of the 173 (168, which a binomial at 95% gives or betters 13% of the time) and all
63 of the seven's, which share their cells: the t coverage is consistent with its level and only the
plug-in interval falls short. The t interval's width is then what its one and two degrees of freedom
require of three or four populations (28 of the 63 held-out series in the seven's cells face an interval
built on three, t at 12.7 times the scale), as Higgins and colleagues (2009) and the Cochrane Handbook
(section 10.10.4) say of a prediction interval from very few studies: at its level, and wide. The two strata as a mixture, the prediction for a population of unknown kind, is wider than the
merged pool (3.40 against 3.07), Tan's component carrying his stratum's mean from one draw and one more
draw, 2 tau^2 + v. Tan's mean falls inside the rest's t interval in 11 of the seven's 15 cells and inside
its z interval in 5. So the stratum narrows the prediction only for a population known to be of the
rest's kind, and only as far as the spread is taken as known: what more papers of that kind buy is the
degrees of freedom, which no split supplies. The next section splits the populations by every variable
the papers state.

What is left (2026-10-30). The naming rows are the quick record's (40 columns, 2 tables per arm) and
stay so on greg's word of 2026-10-29, 23:43 UTC, that no large rebenchmark runs while the synthetic
populations are still moving (#38's rerun, #39's recut); the full run is `python3 -I tan_strata.py --out
records/tan-strata --tables 8` (about 25 minutes on 4 CPUs) and `tables.py --write`, after which the
quick numbers in this section and in answer 8 are read against it (the matched-cell, split and
prediction numbers do not change with the run's size). tan.py reads Tan's SDs for nothing but his SE, as
the validation does; whether his SDs, read as SE x sqrt(n), should be his stratum's own spread is not
decided.

## The populations apart

greg's ask of 2026-10-29, 23:54 UTC: "continue this splitting process into as many known populations
there are, probably by author but if there are race variables and sex variables etc make sure you can do
subgroup analysis very easily, and make sure its all professionally done". Two pieces do it. The
register, data/populations.csv (synthval/register.py), is one row per cohort a usable series comes from,
26 of them, read from the reread's cohort files (research_notes/paper-tables/data/cohorts/) by two
readers each, one extracting every field and a second refuting each against the file, which changed
none: the country as the text states it or inferred from the institution and said so (23 stated, 2
inferred, Zindrick's none), the ancestry only in the paper's own word (12 state one, 14 none), the
specimen (6 dry bone, 4 cadaver, 15 living, 1 mixed), the ages (a mean a paper prints per sex carried as
the count-weighted mean, six cohorts, said so in notes), the counts of the sexes and of the groups a
paper prints apart, as printed, the year, and the page. The subgroup analysis, synthval/subgroups.py, runs for
any variable of a series (paper, cohort, the group a paper printed apart, sex, modality, technique) or
of its cohort (country, region, ancestry, specimen, an age band, the decade), through register.tag, so a
new variable is one column of the register and no code. Three readings (subgroups_run.py,
records/subgroups/): in every cell with three series or more, each subgroup pooled by REML as the cell
is, the spread within the subgroups (tau^2 pooled over the subgroups with two series or more, on their
degrees of freedom), the Cochrane test for subgroup differences in Borenstein's form for few studies a
subgroup (every series weighted by its variance plus that one common spread, so a subgroup of one series
carries the spread the others show, and Q between the subgroups' means on G - 1 degrees of freedom) and
the share of the spread between populations the variable accounts for (one minus the spread within over
the whole cell's), the test and the share read only where the spread within has two degrees of freedom
or more, so a variable every subgroup of which is one series (paper, cohort) has neither, and the share
read again with Tan's series out; each paper, and each value of the other variables, against the rest
of its cells as Tan was read above (the same code gives Tan's distances to the bit,
tests/test_subgroups.py); and the contrasts a paper prints apart, pooled within the paper so that its
own shift drops out (the sexes within an age band, two ancestries of one collection), from a selection
that keeps every printed stratum (literature.select with strata "apart"), which nothing else uses, a
cohort's strata read before its whole so that nobody pools twice, and a sex printed apart within a group
with no count of its own given the group's count times the cohort's share of the sex from the register,
noted on the series, or left out.

<!-- table subgroups -->
| variable | cells | subgroups a cell, median | cells whose test is below 0.05, of the cells tested | share of the spread it accounts for, median (cells read) | the same with Tan 2004's series out | spread over the cells read, the whole cell to within the subgroups, median | widest gap between subgroups, median (Panjabi's SD) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| age_band | 57 | 2 | 3 of 30 | 0.00 (30) | 0.00 (22) | 0.83 to 0.88 | 0.70 |
| ancestry | 57 | 3 | 5 of 24 | 0.28 (24) | 0.16 (19) | 0.87 to 0.79 | 1.21 |
| cohort | 57 | 4 | none | none | none | none | 1.94 |
| country | 57 | 4 | 8 of 15 | 0.47 (15) | 0.35 (15) | 0.99 to 0.79 | 1.85 |
| decade | 57 | 3 | 6 of 27 | 0.25 (27) | 0.00 (27) | 0.86 to 0.76 | 1.49 |
| modality | 53 | 2 | 6 of 34 | 0.18 (34) | 0.00 (20) | 0.77 to 0.67 | 1.14 |
| paper | 57 | 4 | none | none | none | none | 1.94 |
| region | 53 | 4 | 5 of 24 | 0.22 (24) | 0.10 (16) | 0.75 to 0.64 | 1.26 |
| specimen | 53 | 2 | 8 of 31 | 0.22 (31) | 0.24 (22) | 0.79 to 0.69 | 1.38 |

| each paper against the rest | cells | series | distance from the rest's pooled mean (Panjabi's SD), median (quartiles) | cells above | cells inside the rest's interval, t / z | variance pooled / apart, median |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tan2004 | 34 | 34 | -0.86 (-1.65 to -0.49) | 2 | 30 / 23 | 1.22 |
| yadav2020 | 5 | 5 | -0.63 (-0.72 to -0.47) | 0 | 5 / 5 | 0.90 |
| arockiaraj2025 | 15 | 15 | -0.53 (-2.02 to 0.01) | 4 | 12 / 11 | 1.09 |
| masharawi2021 | 20 | 20 | -0.40 (-0.99 to 0.02) | 6 | 20 / 20 | 0.88 |
| griffith2016 | 10 | 10 | -0.35 (-0.52 to 0.03) | 3 | 10 / 10 | 0.86 |
| moncadahabib2025 | 20 | 20 | -0.15 (-0.71 to 0.09) | 6 | 20 / 20 | 0.92 |
| lien2007 | 19 | 19 | 0.00 (-0.22 to 0.29) | 10 | 19 / 19 | 0.88 |
| amonookuofi1985 | 5 | 5 | 0.06 (0.00 to 0.08) | 4 | 5 / 5 | 0.86 |
| duman2026 | 12 | 12 | 0.29 (-0.25 to 1.09) | 8 | 10 / 8 | 1.00 |
| alonge2021 | 10 | 10 | 0.37 (0.21 to 0.82) | 9 | 10 / 10 | 0.86 |
| frontphys2026 | 5 | 5 | 0.46 (0.39 to 0.52) | 5 | 5 / 5 | 0.83 |
| hou1993 | 14 | 14 | 0.53 (-0.05 to 0.78) | 10 | 14 / 11 | 0.92 |
| yu2015 | 10 | 10 | 0.66 (0.45 to 0.78) | 9 | 10 / 10 | 0.96 |
| otsuki2021 | 10 | 10 | 0.67 (-0.15 to 1.26) | 6 | 9 / 8 | 0.99 |
| olsewski1990 | 15 | 19 | 0.82 (-0.55 to 1.17) | 10 | 14 / 12 | 1.03 |
| busscher2010 | 5 | 5 | 0.98 (0.89 to 1.17) | 5 | 5 / 5 | 1.22 |
| cizmic2023 | 10 | 10 | 1.45 (1.23 to 1.63) | 10 | 10 / 8 | 1.17 |
| abbas2021 | 5 | 5 | 1.56 (1.35 to 1.58) | 5 | 5 / 5 | 1.15 |

| each value against the rest | cells | series | distance from the rest's pooled mean (Panjabi's SD), median (quartiles) | cells above | cells inside the rest's interval, t / z | variance pooled / apart, median |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| modality: bone | 30 | 85 | -0.93 (-1.27 to 0.32) | 8 | 29 / 20 | 1.56 |
| specimen: dry bone | 30 | 70 | -0.82 (-1.27 to 0.18) | 10 | 30 / 23 | 1.13 |
| decade: 2000s | 30 | 45 | -0.82 (-1.65 to -0.29) | 3 | 26 / 20 | 1.19 |
| ancestry: Chinese | 27 | 49 | -0.69 (-1.26 to -0.40) | 6 | 27 / 21 | 1.03 |
| ancestry: Indian | 5 | 5 | -0.63 (-0.72 to -0.47) | 0 | 5 / 5 | 0.90 |
| region: South Asia | 5 | 5 | -0.63 (-0.72 to -0.47) | 0 | 5 / 5 | 0.90 |
| ancestry: Saudi | 15 | 15 | -0.53 (-2.02 to 0.01) | 4 | 12 / 11 | 1.09 |
| region: East Asia | 27 | 64 | -0.49 (-1.09 to -0.04) | 7 | 27 / 21 | 0.92 |
| age_band: 60 and over | 29 | 94 | -0.45 (-0.63 to -0.17) | 4 | 29 / 25 | 1.22 |
| age_band: under 40 | 4 | 4 | -0.35 (-0.37 to -0.23) | 1 | 4 / 4 | 0.85 |
| specimen: living | 19 | 54 | -0.24 (-1.12 to 0.28) | 9 | 16 / 12 | 1.23 |
| modality: ct | 19 | 64 | -0.24 (-0.85 to 0.28) | 9 | 19 / 14 | 1.23 |
| ancestry: Mexican | 20 | 20 | -0.15 (-0.71 to 0.09) | 6 | 20 / 20 | 0.92 |
| region: Latin America | 20 | 20 | -0.15 (-0.71 to 0.09) | 6 | 20 / 20 | 0.92 |
| region: West Asia | 31 | 52 | 0.01 (-0.85 to 0.49) | 16 | 30 / 23 | 0.96 |
| decade: 2020s | 24 | 85 | 0.02 (-0.83 to 0.70) | 14 | 23 / 19 | 1.02 |
| decade: 1980s | 5 | 5 | 0.06 (0.00 to 0.08) | 4 | 5 / 5 | 0.86 |
| ancestry: Nigerian | 10 | 15 | 0.27 (0.15 to 0.82) | 8 | 10 / 10 | 0.75 |
| region: Africa | 10 | 15 | 0.27 (0.15 to 0.82) | 8 | 10 / 10 | 0.75 |
| age_band: not stated | 25 | 40 | 0.28 (-0.17 to 0.46) | 16 | 25 / 25 | 0.82 |
| ancestry: Turkish | 12 | 12 | 0.29 (-0.25 to 1.09) | 8 | 10 / 8 | 1.00 |
| age_band: 40 to 59 | 26 | 52 | 0.31 (-0.30 to 0.64) | 17 | 26 / 23 | 0.99 |
| decade: 2010s | 25 | 25 | 0.46 (-0.30 to 0.89) | 17 | 25 / 25 | 0.92 |
| decade: 1990s | 19 | 33 | 0.54 (-0.15 to 1.07) | 14 | 18 / 15 | 1.01 |
| ancestry: Caucasian and African American | 10 | 10 | 0.66 (0.45 to 0.78) | 9 | 10 / 10 | 0.96 |
| ancestry: not stated | 34 | 88 | 0.67 (0.06 to 1.02) | 27 | 34 / 30 | 0.92 |
| specimen: cadaver | 20 | 30 | 0.83 (0.08 to 1.24) | 15 | 18 / 17 | 1.19 |
| region: North America | 15 | 39 | 0.86 (-0.55 to 1.28) | 10 | 12 / 8 | 1.19 |
| region: Europe | 15 | 15 | 1.22 (1.07 to 1.56) | 15 | 15 / 13 | 1.20 |

| within-paper contrast | over | cells | pairs a cell, median | difference, median (quartiles), Panjabi's SD | cells above zero | cells below 0.05 | measures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ancestry: African American - Caucasian | every cell | 10 | 1 | -0.01 (-0.06 to 0.03) | 4 | 3 | pedicle_h, pedicle_w |
| sex: male - female | every cell | 4 | 3 | 0.17 (0.13 to 0.19) | 4 | 3 | pedicle_w |

The register holds 26 cohorts, every one a usable series names; 903 usable series under the main selection, 1067 with the strata apart (24 of them a sex printed apart, 24 of those with the count the register's group counts give, the paper counting its groups and its sexes but not the sexes within the groups). The test and the share are read where the spread within the subgroups has 2 degrees of freedom or more, and a subgroup of one series carries that common spread in the test. A value's row pools every cell where the value has a series and the rest hold three or more, and a value with fewer than 3 such cells is left out; a value with several series in a cell is held to the rest's interval for a mean of that many populations, so its inside counts read as a paper's do. The contrasts come from African American - Caucasian from yu2015; male - female from duman2026.
<!-- end subgroups -->

What it says. The test can be made where the spread within the subgroups has two degrees of freedom or
more, in 15 of the country's 57 cells to 34 of the modality's 53, and falls below 0.05 in 3 to 8 of
them a variable, so with three to ten series a cell it has little to say, and the share is the reading,
taken twice. With Tan's series in, the country accounts for a median 0.47 of the variance between
populations (15 cells), the stated ancestry 0.28 (24), the decade 0.25 (27), the specimen 0.22 (31), the
region 0.22 (24), the modality 0.18 (34) and the age band nothing (0.00 in 30 cells, once the six
cohorts that print their mean age per sex, Abbas, Cizmic, Masharawi, Olsewski's two and Tang, are placed
by the count-weighted mean, where the band of what papers left unsaid had carried 0.14); with them out,
the decade's and the modality's shares are 0.00 too, since the 2000s are Tan, Lien and Robertson and
Tan is the far member of the dry-bone and the East Asian subgroups, the region's falls to 0.10,
the ancestry's to 0.16 (the Chinese cohorts, Tan, Hou, Griffith and the Zhengzhou CTs, and the two
Nigerian ones being the only stated ancestries with more than one paper) and the country's to 0.35, and only the specimen's holds
(0.24): what the variables account for is mostly Tan's distance under other names. Dry bone sits a
median 0.82 of Panjabi's SD below the rest and cadavers 0.83 above, Europe's two cohorts 1.22 above;
paper by paper Tan is the farthest below and Abbas and Cizmic the farthest above; by Higgins' t
interval, wide as it is with three to nine series, the papers fall outside the rest's prediction in 11
of 224 cells (Tan in 4 of 34, Arockiaraj in 3 of 15, Duman in 2 of 12, no other paper in more than one),
and with the spread taken as known in 29 (Tan in 11, Arockiaraj and Duman in 4 each, no other in more
than 3): by Higgins' interval no paper is mispredicted in more than a cell in five (Arockiaraj 3 of 15, Duman 2
of 12, Tan 4 of 34), and with the spread taken as known Tan, Duman and Arockiaraj each in about a cell
in three, Tan in nearly three times the cells of either.
The sex contrast comes from one paper (Duman's pedicle widths, men 0.07 to 0.21 SD wider within age
bands, 3 of 4 cells below 0.05) on counts he does not print: he counts his bands (198, 176 and 143) and
his sexes (277 men, 240 women) but not the sexes within the bands, so each sex of a band is given the
band's count times the cohort's share of the sex (the register's group counts, noted on every such
series), the nearest reading short of leaving the contrast out, and the SEs are read as they would be
on those counts, not on his 517. The ancestry contrast comes from one collection (Yu's, the pedicle's
width 0.20 SD wider in African American skeletons at L1 and 0.23 narrower at L5, the heights alike),
since the other papers print their sexes without an SD, pooled, or in selected quarters. The subgroups
are few and observational: a value with one paper is that paper, a variable the papers state unevenly
makes a subgroup of what was left unsaid (the cohorts with no stated ancestry sit 0.67 above the rest),
and a difference between specimens may be shrinkage, selection or the decade's technique at once (figure
fig_subgroups).

## What gold persons can test

<!-- table gold -->
| persons | least mean shift found, one cell (SD) | one cell of 154, Bonferroni (SD) | least SD ratio found | half-width of a neighbour r of 0.5 | six lumbar-type segments | of which a true L6 | four lumbar segments | a rib on the first lumbar-type body | no twelfth rib, one side or both |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 17 | 0.72 | 1.35 | 1.61 | 0.38 | 0.4 | 0.1 | 0.3 | 0.4 | 0.7 |
| 142 | 0.24 | 0.38 | 1.18 | 0.12 | 3.5 | 0.6 | 2.6 | 3.3 | 6.0 |
| 159 | 0.22 | 0.36 | 1.17 | 0.12 | 3.9 | 0.7 | 2.9 | 3.7 | 6.8 |
| 300 | 0.16 | 0.26 | 1.12 | 0.09 | 7.4 | 1.3 | 5.4 | 7.0 | 12.8 |
| 1000 | 0.09 | 0.14 | 1.06 | 0.05 | 24.8 | 4.5 | 18.1 | 23.2 | 42.6 |

| persons | least mean shift: the table exact (SD) | against Panjabi's 12 as a sample, Welch (SD) | least SD ratio: the table exact | against his 12, F |
| ---: | ---: | ---: | ---: | ---: |
| 17 | 0.72 | 1.48 | 1.61 | 2.20 |
| 142 | 0.24 | 1.36 | 1.18 | 1.82 |
| 159 | 0.22 | 1.36 | 1.17 | 1.81 |
| 300 | 0.16 | 1.35 | 1.12 | 1.79 |
| 1000 | 0.09 | 1.34 | 1.06 | 1.78 |

In the second table Panjabi's SD is 1.51 times the gold persons', the papers' median (records/power.json).
<!-- end gold -->

In the first table the three columns after the count of persons are the least effect a two-sided test at
5% finds with 80% power against the table taken as exact: the noncentral t for a mean, with the SD read
from the same people, and the chi-square for an SD. The fourth is the half-width of a 95% interval for a
correlation of 0.5. The rest are the persons expected with each state at the papers' prevalences. The
second table sets the same tests against Panjabi's twelve as a sample, Welch's t and the F test, which is
what his table is; his twelve then carry most of the uncertainty, so more gold persons barely help.

17 and 142 are VerSe's and TotalSegmentator's gold 3 persons, 159 both (holdings/gold-tier-3.md). The
expected counts are of the papers' populations, which these are not quite: the 142 are the subjects whose
masks hold C2 to L5 and the sacrum, so a column with four lumbar segments, which has no fifth to label
unless it is misnamed, is selected out, and other anomalous columns may be, as their labels go.
SchwingNet's admission of 2026-10-29 (pull request 451; data/gold3-ct/admission.json at its main a301b72,
rule version 2) now admits 1,729 studies by their fields: ENHANCE.PET 1,560, whose persons it does not
count (autoPET scans some patients more than once, and Leipzig's and Careggi's studies carry no person
id), and of whose CTs only autoPET's are on the grid, not yet matched to their masks, under the owner's
hold; TotalSegmentator 151, 22 of them flagged as children; VerSe 18. 1,726 of them are gold 3 (the three
repaired ENHANCE.PET studies stay gold 4), of 1,034 to 1,647 persons by SchwingNet's records
(docs/research/gold3-ct/README.md L23 at a301b72), which the rows at 1,000 and 2,000 persons in
records/power.json bracket.

## The assumptions beside the papers

<!-- table assumptions -->
| error of one reading | modality | range | source |
| --- | --- | ---: | --- |
| body heights | CT | 0.30 to 0.65 mm | duman2026, 50 scans read again after 4 weeks; error.md L55 |
| pedicle width and height | CT | 0.20 to 0.55 mm | duman2026; error.md L65 |
| pedicle angle | CT | 0.70 to 1.80 deg | duman2026; error.md L73 |
| canal width and depth | CT | 0.40 to 1.20 mm | griffith2016, by level L1-L5; error.md L62 |
| canal area | CT | 10.00 to 30.00 mm2 | griffith2016; error.md L62 |
| disc and end-plate diameters | MRI | 0.50 to 0.90 mm | tang2016, between observers; error.md L60 |
| disc and end-plate area | MRI | 40.00 mm2 | tang2016, between observers; error.md L60 |
| pedicle width and height | bone, caliper | 0.35 to 0.95 mm | yu2015; error.md L67 |
| interpedicular distance | film | 0.27 mm | hinck1966, 89 duplicate readings; error.md L63 |
| one pig vertebra, CT repeated | CT | 0.22 mm | vanderhouwen2009, the mean of nine dimensions' SDs over three repeats; error.md L59 |
| CT against caliper | CT and bone | 0.66 mm | vanderhouwen2009 Fig. 4, 12 dimensions of 2 pig vertebrae, the caliper's own error in it; error.md L91 |

| the generator's error, by kind | measures | error | median error / SD at L3 |
| --- | ---: | ---: | ---: |
| angle | 8 | 3.00 | 0.50 |
| area | 6 | 9.47 to 32.00 | 0.31 |
| length | 18 | 1.00 | 0.34 |

| state | model.py (%) | chain (%) | papers (%) | source |
| --- | ---: | ---: | ---: | --- |
| six lumbar-type segments (L6 or lumbarised S1) | 16.7 | 5.0 | 2.48 (1.39 to 4.39) | eisenstein1977 p. 177, 11 / 443 dry skeletons (2 true L6, 9 lumbarised S1); anomaly-priors.md L11 |
| of which a true L6 | - | - | 0.45 (0.12 to 1.63) | eisenstein1977 p. 177, 2 / 443; anomaly-priors.md L12 |
| four lumbar segments (sacralised L5), a ceiling | 16.7 | - | 1.81 (0.92 to 3.52) | eisenstein1977 p. 177, 8 / 443; sacralisation undefined, so a ceiling; anomaly-priors.md L14 |
| a thirteenth rib-bearing body (T13) | 16.7 | 5.0 | no count | no count and no bound in the 43 papers; any value is a modelling choice; anomaly-priors.md L22 |
| a rib on the first lumbar-type body | 16.7 | - | 2.32 (1.33 to 4.01) | duman2026 Table 5 p. 10, 12 / 517 adults' CTs at a chest hospital for other reasons; a T13 not told apart; anomaly-priors.md L21 |
| no twelfth rib, one side or both | 16.7 | - | 4.26 (2.83 to 6.36) | duman2026 Table 5 p. 10, 22 / 517; a ceiling for bilateral absence, laterality never reported; anomaly-priors.md L23 |
<!-- end assumptions -->

The errors are the reread's error part (synthesis/error.md at 448006f), each row with the line it stands
on there. The generator's 1 mm for a length is larger than most CT and caliper reading errors that part
gives, but not the canal's largest on CT (0.4 to 1.2 mm, Griffith) nor Moncada-Habib 2025's per-reading
SD of about 1 mm, which the part infers from its 2 mm tolerance (L69); CT and caliper differ with an SD
of 0.66 mm (a mean of 0.18 mm) on van der Houwen's pig vertebrae, the caliper's own error in it (L91).
Its 3 degrees for an angle is larger than the 0.7 to 1.8 degrees of the pedicle's. Its error for the
canal's area at L3, sqrt(pi A / 2), is about 20 mm2, inside Griffith's 10 to 30. The prevalences are the
reread's checked priors (anomaly-priors.md, whose 43 papers are the 39 and Panjabi's four), each of the
population its paper names: model.py draws each of its six phenotypes as one column in six, the chain of
levels at 0.05, and the papers count six lumbar-type segments in 2.48% of 443 skeletons and give no count
at all for a thirteenth rib-bearing body.

## Every measure of the reread

The first part held the generator to the 32 measures it draws. The owner asked at 15:18 UTC on 2026-10-29
for all the unique measures of the clinical reread, not just Panjabi's. This part reads the whole reread
snapshot, data/series_all.csv (4,357 rows) and data/vocabulary.csv (106 keys), cut from bordercall main
6409164 and held to data/SOURCE_ALL.json (papers_table.check_snapshot_all), and builds three tables a
population can be drawn from: A, Panjabi's 42 measures at every level where he prints a spread, his own
means and SDs; B, the papers' 53 measures, pooled as the first part pools them (literature.py's rules,
pooling.py's REML means, the papers' SDs with Tan 2004's left out where another series prints one) and
placed at a vertebra of C3 to L5; and C, both, Panjabi's measures with his errors and the papers' with
their kind's (synthval/papers_table.py). The inventory, MEASURES.md, lists every key of the vocabulary
with what became of it. Of the 95 measures of a vertebra, 49 are Panjabi's, 7 of them printed as a mean
with no spread (the end-plates' wedge, two rib areas, the facets' four Cardan angles), which no table can
hold; 46 have a usable series in the papers, 20 of them Panjabi's, all among the 32; 17 keys no paper of
the 39 prints a series for (the lamina's thickness, height and width, the pars' width, the spinous
height, the transverse process's length and height, the pedicle's outer width and height and its two
angles, the body's wedge and index, the lateral height, the facets' sagittal angle, tropism and gap);
and 3 have rows but no series with a mean, an SD and a count of two or more that passes the rules
(spinous_angle, disc_index, endplate_concavity). Nine keys are split into variants where their papers
measure different things under one name (papers_table.VARIANTS, with the reason in VARIANT_WHY: Bach's
disc height from three points and Kunkel's from the two rims, Hou's pedicle chord parallel to the
midline and the others' along the axis, Chen's body depth as the end-plates' mean and Moncada's on the
slice through the pedicles, Alonge's Torg ratio of depths and Griffith's canal index of areas, among
them); each variant is a measure of its own in table B, so the 53 measures of B are 46 keys' worth.

<!-- table all_inventory -->
| the vocabulary | keys |
| --- | ---: |
| keys in the vocabulary | 106 |
|   not a measure of one vertebra (the subjects, a prevalence, a reliability, an alignment) | 11 |
|   measures of a vertebra | 95 |
|     Panjabi prints them | 49 |
|       with a spread, so a table can hold them | 42 |
|       the generator's 32 | 32 |
|       as a mean with no spread | 7 |
|     with a usable series in the papers | 46 |
|       of them Panjabi's | 20 |
|       of them the papers' own | 26 |
|     no paper of the 39 prints a series | 17 |
|     rows, but no series with a mean, an SD and a count | 3 |
|     split into variants (papers_table.VARIANTS) | 9 |
|     drawn in some table | 68 |

| table | measures | count | cells (measure, level) | complete C3 to L5 | complete L1 to L5 | by kind |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| A | Panjabi's, every measure | 42 | 782 | 32 | 33 | angle 12, area 12, length 18 |
| B | the papers' | 53 | 694 | 21 | 50 | angle 7, area 6, length 39, ratio 1 |
| C | Panjabi's and the papers' | 75 | 1054 | 35 | 63 | angle 15, area 14, length 45, ratio 1 |
<!-- end all_inventory -->

The papers' cells are not of a piece, and the table below says what each count is made of. Of the 694
cells placed at a level, 292 rest on Tan 2004's ten Singaporean cadavers alone, whose SD is uncertain
(his methods define the SE as SD / n, literature.DISPERSION_UNCERTAIN; the SD is read back as SE times
sqrt(n)), 279 on one other series and 123 on a pooled SD; 665 pool bone and CT, 22 film and 7 MRI, each
cell from the first class that has a series, so no mean mixes a magnified film with bone; 81 cells pool
three series or more and carry a prediction interval. The upper end-plate lacks C6 in table B because
Tan prints an SD of 0 there, so B holds 21 of its cells and C 22, Panjabi's filling the gap. A disc or a
foramen printed between two levels is placed at the upper; one printed against a single vertebra with
no word of which space (Busscher's and Yadav's discs, Yadav's foramina) is pooled under its own label
and placed nowhere, 44 cells in all, 22 of them the mid-disc height. The reread's own n-faults are not
fixed in this snapshot: bordercall pull request 39 (branch claude/project-thread-r19vr5, at 1119506 when
this was written, marked ready for the owner) cuts series.csv from 4,357 to 3,760 rows, taking out
Griffith's adjusted rows, which duplicate his 1,080, Bach's figure points, Chaudhary's and Mitra's
reprints, Hou's T9 misprint and Shin 2024's covariate-adjusted tables, pooling Bach 2019's decades
with their printed counts, and reading the counts of people for Frontphys 2026, Kunkel 2011, Olsewski
1990, Shin 2024 and Chen, Tan's end-plate angles as magnitudes, and Otsuki 2021's pedicle heights, an
isthmus axis, as differing from Panjabi's measure. When it merges, `papers_table.write_snapshot_all` cuts the snapshot again and
run_all.py is run again; every number of this part moves with it, and the pooled cells' counts above
first.

<!-- table all_cells -->
| the papers' cells | count |
| --- | ---: |
| rows of the whole snapshot | 4357 |
| series formed | 1576 |
| series with a mean, an SD and a count of two or more | 1386 |
| papers behind them | 33 |
| cells (measure, level as printed) pooled | 738 |
| cells placed at a level of C3 to L5 | 694 |
|   SD Tan 2004's alone, uncertain | 292 |
|   SD one series | 279 |
|   SD pooled | 123 |
|   pooled from MRI | 7 |
|   pooled from bone and CT | 665 |
|   pooled from film | 22 |
|   one series / two / three or more | 477 / 136 / 81 |
| cells pooled but placed nowhere (a disc or foramen against one vertebra, a level past L5) | 44 |
|   body_d_mid | 1 |
|   canal_ap | 1 |
|   disc_h_mean | 7 |
|   disc_h_mid | 22 |
|   endplate | 1 |
|   endplate_area | 1 |
|   endplate_depth | 1 |
|   endplate_lower_depth | 1 |
|   foramen_w | 7 |
|   h_ant | 1 |
|   lateral_recess | 1 |
<!-- end all_cells -->

## The state space on every table

The first part's state space was searched against the papers' SDs on the 32 measures. Here each table is
drawn from at the generator's point and the 20 single-axis points of synthval/sweep.py, and the grid of
480 points is searched on each, scored as before by the squared log of the median SD ratio plus the
squared distance of the four correlations from Griffith's. The SD ratio on a table is over the table's
own SDs, since a table drawn from its own means and SDs has no other population to be held to, so the
reading is one of self-consistency: how far the generator's size and its clip move the SD it is given,
and how near a point of the grid brings it back to one. At the generator's point the true SD is 1.11
to 1.25 times the table's own (1.23 to 1.57 measured, table B the widest, whose SDs, the papers', are smaller than
Panjabi's, so the size's spread and the errors stand larger against them); every table's nearest
point sits at sd_scale 1.0, scale_sd 0 or 0.01, rho 0.9 and r_between 0.4, where the true ratio reads
1.00 or 1.01 and the neighbouring levels correlate at 0.81 (0.39 to 0.43 at the generator). Those
nearest points agree with the first part's on rho and on the size's spread, and differ on sd_scale,
which the papers' SDs set at 0.6 and the tables' own leave at 1.0, as they must. The median correlation
of Griffith's four pairs falls from 0.53 to 0.57 at the generator to 0.39 at every nearest point,
against Griffith's 0.24 to 0.58, since the size's spread is what ties measure to measure.

<!-- table all_state_space -->
| table | point | scale_sd / sd_scale / rho / r_between | SD ratio, true | measured | neighbour r | median Griffith-pair r | necessary (% vertebrae) | any but floor (% vertebrae) | any (% vertebrae) | any but floor (% people) | distance |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | generator | 0.070 / 1.00 / 0.50 / 0.00 | 1.11 | 1.23 | 0.40 | 0.57 | 6.0 | 43.4 | 46.0 | 100 | - |
| A | nearest | 0.010 / 1.00 / 0.90 / 0.40 | 1.01 | 1.09 | 0.81 | 0.39 | 5.7 | 29.9 | 32.5 | 92 | 0.015 |
| B | generator | 0.070 / 1.00 / 0.50 / 0.00 | 1.25 | 1.57 | 0.43 | 0.53 | 12.4 | 44.5 | 46.7 | 100 | - |
| B | nearest | 0.010 / 1.00 / 0.90 / 0.40 | 1.00 | 1.26 | 0.81 | 0.39 | 10.9 | 39.2 | 41.9 | 100 | 0.020 |
| C | generator | 0.070 / 1.00 / 0.50 / 0.00 | 1.12 | 1.25 | 0.39 | 0.56 | 15.4 | 55.0 | 59.4 | 100 | - |
| C | nearest | 0.000 / 1.00 / 0.90 / 0.40 | 1.00 | 1.10 | 0.81 | 0.39 | 12.9 | 41.8 | 46.8 | 99 | 0.017 |
<!-- end all_state_space -->

<!-- table all_axes -->
| point (table C) | SD ratio, true | measured | neighbour r | median Griffith-pair r | necessary (% vertebrae) | within | outside | any but floor (% vertebrae) | any but floor (% people) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| generator | 1.12 | 1.25 | 0.39 | 0.56 | 15.4 | 5.2 | 4.4 | 55.0 | 100 |
| scale_sd=0.0 | 1.00 | 1.10 | 0.25 | -0.00 | 15.4 | 5.1 | 4.5 | 55.1 | 100 |
| scale_sd=0.035 | 1.03 | 1.14 | 0.29 | 0.23 | 15.4 | 5.2 | 4.4 | 55.0 | 100 |
| scale_sd=0.05 | 1.06 | 1.18 | 0.33 | 0.39 | 15.4 | 5.2 | 4.4 | 55.0 | 100 |
| scale_sd=0.1 | 1.24 | 1.38 | 0.49 | 0.72 | 15.4 | 5.2 | 4.4 | 55.0 | 100 |
| rho=0.0 | 1.12 | 1.25 | 0.20 | 0.72 | 15.4 | 5.1 | 4.5 | 55.2 | 100 |
| rho=0.25 | 1.12 | 1.25 | 0.25 | 0.67 | 15.5 | 5.2 | 4.5 | 55.1 | 100 |
| rho=0.75 | 1.12 | 1.25 | 0.64 | 0.44 | 15.4 | 5.2 | 4.3 | 55.1 | 100 |
| rho=0.9 | 1.12 | 1.25 | 0.84 | 0.37 | 15.3 | 5.2 | 4.2 | 55.2 | 100 |
| phi=0.3 | 1.12 | 1.25 | 0.58 | 0.51 | 15.5 | 5.2 | 4.4 | 55.0 | 100 |
| phi=0.6 | 1.12 | 1.25 | 0.76 | 0.44 | 15.6 | 5.3 | 4.4 | 55.1 | 100 |
| phi=0.9 | 1.12 | 1.25 | 0.94 | 0.36 | 15.5 | 5.2 | 4.5 | 54.9 | 100 |
| r_between=0.2 | 1.12 | 1.25 | 0.40 | 0.61 | 15.2 | 5.0 | 4.3 | 53.4 | 100 |
| r_between=0.4 | 1.12 | 1.25 | 0.40 | 0.66 | 14.7 | 4.8 | 4.1 | 51.5 | 100 |
| error_scale=0.5 | 1.12 | 1.17 | 0.39 | 0.56 | 15.4 | 5.2 | 4.4 | 55.0 | 100 |
| error_scale=2.0 | 1.12 | 1.48 | 0.39 | 0.56 | 15.4 | 5.2 | 4.4 | 55.0 | 100 |
| sd_scale=0.7 | 0.86 | 1.03 | 0.50 | 0.72 | 6.6 | 3.0 | 2.2 | 29.4 | 100 |
| sd_scale=0.85 | 0.99 | 1.13 | 0.44 | 0.64 | 10.5 | 4.1 | 3.3 | 42.3 | 100 |
| sd_mode=size_removed | 1.00 | 1.10 | 0.43 | 0.74 | 13.1 | 4.6 | 3.5 | 40.3 | 100 |
<!-- end all_axes -->

## Quality on every table

qi.py's five indicators are read on every table's population, and nine relations between the papers'
measures and Panjabi's with them (synthval/relations.py), each necessary whatever the population: an
inner pedicle width or height inside the outer, the medial cortex and the core inside the width, the
screw path along the pedicle's axis longer than the pedicle proper and than the distance to the
posterior longitudinal ligament, the interpedicular distance and two pedicles inside the span of the
transverse processes, Griffith's body section and Shin's foramen inside the rectangles of their own
extents (with the end-plate's allowances for the body, none convex for the foramen), and a ratio of two
areas above zero. "Necessary" unites the relations no anatomy can fail; "any but floor" adds the two
bounds that hold under this note's allowances. On table C at the generator 15.5% of vertebrae and 96% of
people fail a necessary relation (6.3% and 74% on sign or inside alone, the first part's reading), 55.1%
and every person any but the floor, 59.4% any; at C's nearest point 12.4% and 78%, 41.3% and 99%, 46.2%
and every person. The relations the papers bring fail most where two papers' means are set beside each
other with independent draws: the medial cortex and the inner width against the pedicle's width 19.5%
(Otsuki's cortex, Makino's core, Panjabi's pedicle), the inner width against the width 12.9%, the
pedicles inside the transverse processes 4.6% of 88,000 tests, the inner height 4.1%; the two chords
and the ratio fail none. Griffith's body section passes the rectangle of Moncada's width and depth in
30.2% and falls under half of it in 0.9%, Shin's foramen passes his own rectangle in 37.7%: areas
drawn independently of the extents that bound them, as the first part found of Panjabi's end-plates.
A relation that joins two papers' populations asks whether the generator's independent draws from
their pooled means make a vertebra that could exist, not whether the papers disagree. On table B alone,
whose cells are the papers', sign or inside fails 0.4% of vertebrae and 9% of people, the necessary
union 12.5% and 95%, and the box 40.2%. Curation is counted here as in the first part, never applied.

<!-- table all_quality -->
| table | setting (% of vertebrae / % of people) | measures | sign or inside | necessary (with within, past, outside, positive) | box | convex | any but floor | floor | any |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | generator | 42 | 6.2 / 74 | 6.2 / 74 | 32.2 / 99 | 10.3 / 77 | 43.4 / 100 | 9.5 / 86 | 46.0 / 100 |
| A | size_removed | 42 | 5.2 / 68 | 5.2 / 68 | 21.2 / 97 | 1.8 / 29 | 26.7 / 100 | 8.1 / 83 | 29.6 / 100 |
| A | size_removed, scale_sd 0.035 | 42 | 5.9 / 72 | 5.9 / 72 | 29.2 / 99 | 7.8 / 69 | 38.9 / 100 | 9.0 / 85 | 41.5 / 100 |
| A | nearest the papers (32 measures) | 42 | 0.6 / 11 | 0.6 / 11 | 5.7 / 43 | 0.6 / 7 | 6.9 / 52 | 1.9 / 30 | 8.2 / 63 |
| A | nearest the papers (A) | 42 | 5.6 / 45 | 5.6 / 45 | 20.9 / 79 | 5.6 / 33 | 29.2 / 91 | 8.4 / 58 | 31.7 / 93 |
| B | generator | 53 | 0.4 / 9 | 12.5 / 95 | 40.2 / 100 | 0.3 / 5 | 45.2 / 100 | 9.2 / 90 | 47.4 / 100 |
| B | size_removed | 53 | 0.4 / 8 | 10.8 / 92 | 24.6 / 100 | 0.0 / 0 | 30.1 / 100 | 9.0 / 90 | 33.1 / 100 |
| B | size_removed, scale_sd 0.035 | 53 | 0.4 / 9 | 11.9 / 94 | 33.3 / 100 | 0.1 / 2 | 38.4 / 100 | 9.1 / 90 | 40.8 / 100 |
| B | nearest the papers (32 measures) | 53 | 0.022 / 0 | 7.6 / 67 | 25.2 / 99 | 0.0 / 0 | 29.6 / 100 | 7.8 / 87 | 33.0 / 100 |
| B | nearest the papers (B) | 53 | 0.5 / 7 | 10.9 / 84 | 34.6 / 99 | 0.1 / 1 | 39.8 / 100 | 9.0 / 88 | 42.4 / 100 |
| C | generator | 75 | 6.3 / 74 | 15.5 / 96 | 40.8 / 100 | 10.5 / 79 | 55.1 / 100 | 17.9 / 98 | 59.4 / 100 |
| C | size_removed | 75 | 5.2 / 67 | 13.2 / 94 | 30.6 / 100 | 1.7 / 29 | 40.3 / 100 | 16.4 / 98 | 45.9 / 100 |
| C | size_removed, scale_sd 0.035 | 75 | 5.9 / 72 | 14.9 / 95 | 38.1 / 100 | 7.9 / 71 | 51.3 / 100 | 17.4 / 98 | 55.9 / 100 |
| C | nearest the papers (32 measures) | 75 | 0.6 / 11 | 3.9 / 46 | 14.8 / 83 | 0.6 / 7 | 18.3 / 91 | 9.5 / 91 | 23.7 / 99 |
| C | nearest the papers (C) | 75 | 5.6 / 44 | 12.4 / 78 | 30.0 / 94 | 5.6 / 34 | 41.3 / 99 | 16.7 / 92 | 46.2 / 100 |
<!-- end all_quality -->

<!-- table all_relations -->
| relation | indicator | measures | vertebrae tested | flagged at the generator (%) | at C's nearest point (%) | why it must hold |
| --- | --- | --- | ---: | ---: | ---: | --- |
| inner width within the pedicle | within | pedicle_w_inner, pedicle | 20000 | 12.9 | 9.6 | the cancellous core lies inside the cortex |
| inner height within the pedicle | within | pedicle_h_inner, pedicle_h | 20000 | 4.1 | 2.1 | the cancellous core lies inside the cortex |
| cortex and core within the pedicle | within | pedicle_cortex [medial], pedicle_w_inner, pedicle | 20000 | 19.5 | 15.9 | the width is the two walls and the core together, so the medial wall and the core are less than it |
| the chord runs past the pedicle | past | pedicle_length [proper], pedicle_chord [along the axis] | 20000 | 0.0 | 0.0 | the screw path reaches the anterior cortex of the body, beyond the pedicle proper |
| the chord runs past the ligament | past | pedicle_length [to the ligament], pedicle_chord [along the axis] | 20000 | 0.0 | 0.0 | the posterior longitudinal ligament lies on the body's back wall, before its anterior cortex |
| the pedicles inside the transverse processes | outside | interpedicular, pedicle, pedicle, transverse_width | 88000 | 4.6 | 3.1 | the transverse processes arise lateral to the pedicles, which stand lateral to the canal |
| body section inside its box (convex bound) | convex | body_area, body_w, body_d [through the pedicles] | 20000 | 0.9 | 0.3 | a plane region lies inside the rectangle of its extents; the body section is nearly symmetric and convex |
| body section inside its box | box | body_area, body_w, body_d [through the pedicles] | 20000 | 30.2 | 25.7 | a plane region lies inside the rectangle of its extents; the body section is nearly symmetric and convex |
| foramen inside its box | box | foramen_area, foramen_w [body to facet], foramen_h | 19999 | 37.7 | 34.6 | a plane region lies inside the rectangle of its extents; the foramen is not symmetric, so no convex bound |
| a ratio above zero | positive | canal_index [areas] | 20000 | 0.0 | 0.0 | a ratio of two positive areas is positive |
<!-- end all_relations -->

## Naming with more measures

The exact rule is built on table C and read on columns drawn from it, with each subset's own errors, on
measures complete over the run it names: over C3 to L5 the seven SPINEPS measures, the generator's 32
and every complete measure of C (35); over L1 to L5 the seven, the 32, and every complete measure of A
(33), B (49) and C (62). canal_index [areas] is complete over the lumbar run but has no modelled error,
a ratio having none, so it is left out of every subset (naming_all.csv, no_modelled_error). At the
generator's point one body of the whole column is named exactly in 47.3% of fields on the seven, 87.2%
on the 32 and 89.0% on all 35; three bodies in 72.8, 98.3 and 98.9%; nine in 96.2% on the seven and
every field on the rest. Over the lumbar run one body reads 49.1% on the seven, 92.3% on the 32, 92.6%
on A's 33, 95.4% on B's 49 and 97.6% on C's 62: the papers' own measures add three points over the 32
and the whole table five, and three bodies are named in every field from 32 measures on. At C's
nearest point, with the rule built for its SDs, size spread and rho and ignoring its r_between of 0.4
as the first part's rule ignored its 0.2, the seven name one body in 50.9% and three in 81.3% (86.7% lumbar), while the
larger subsets read a few points lower at one body (82.4% on the 32, 83.2% on the 35, 92.2% on the 62),
since a draw with less size and more correlation between neighbours gives the rule less to tell one
column from the next by when every measure is in; from 32 measures on, at three bodies and more the two
points read alike.
The answers at 0.99 are right 97 to 100% of the time throughout (table all_naming, figure
fig12_naming_measures).

<!-- table all_naming -->
| run | measures | generator: n | 1 body | 3 bodies | 5 bodies | 9 bodies | nearest the papers (C): n | 1 body | 3 bodies | 5 bodies | 9 bodies |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C3-L5 | the seven | 7 | 47.3 (99) | 72.8 (100) | 96.2 (100) | 7 | 50.9 (97) | 81.3 (100) | 99.6 (100) |
| C3-L5 | the generator's 32 | 32 | 87.2 (100) | 98.3 (100) | 100.0 (100) | 32 | 82.4 (99) | 98.8 (100) | 100.0 (100) |
| C3-L5 | every complete measure of C | 35 | 89.0 (100) | 98.9 (100) | 100.0 (100) | 35 | 83.2 (99) | 99.2 (100) | 100.0 (100) |
| L1-L5 | the seven | 7 | 49.1 (100) | 77.3 (100) | 100.0 (100) | 7 | 51.6 (98) | 86.7 (100) | 100.0 (100) |
| L1-L5 | the generator's 32 | 32 | 92.3 (100) | 99.9 (100) | 100.0 (100) | 32 | 87.1 (98) | 100.0 (100) | 100.0 (100) |
| L1-L5 | every complete measure of A | 33 | 92.6 (100) | 99.9 (100) | 100.0 (100) | 33 | 87.4 (98) | 100.0 (100) | 100.0 (100) |
| L1-L5 | every complete measure of B | 49 | 95.4 (100) | 99.9 (100) | 100.0 (100) | 49 | 89.4 (99) | 100.0 (100) | 100.0 (100) |
| L1-L5 | every complete measure of C | 62 | 97.6 (100) | 100.0 (100) | 100.0 (100) | 62 | 92.2 (98) | 100.0 (100) | 100.0 (100) |

Each cell is the share of fields named exactly, and in parentheses the share of its answers at 0.99 that are right. The widths are 1, 3 and 9 bodies over C3 to L5 and 1, 3 and 5 over L1 to L5, so the last column of each setting reads 9 or 5 by the run. Left out of every subset, having no modelled error: canal_index [areas].
<!-- end all_naming -->

## The spread between series on every measure

The first part's part B read the spread between published series on Panjabi's measures; here it is
read on every cell of the whole snapshot that pools three series or more (power.py's REML tau over the
cell's SD): 81 cells of 14 measures, a median 1.07 (quartiles 0.72 to 1.38), 81% of cells over 0.5, so
the series differ among themselves by about a person's SD. Panjabi's measures read 1.15 over 57 cells,
the first part's reading in the papers' own SD; the papers' own measures 0.76 over 24 cells of five
measures, with the widest and the narrowest spreads both among them: the anterior body height 1.61
(seven cells), against the interpedicular distance 0.32 and the mid body height 0.23 (two cells). Of
Panjabi's, the pedicle's sagittal inclination reads 2.78, the end-plates' widths 1.53 and 1.28, the
pedicle's height 1.24 and width 0.57. An infinite pool of published series is worth a median 0.1 scan
of the population named for the sagittal inclination and 28 for the mid body height, by part A's rule;
between half a scan and 1.2 for eight of the fourteen.

<!-- table all_spread -->
| spread between series, tau / the cell's SD | cells (3 series or more) | measures | median | quartiles | cells over 0.5 (%) |
| --- | ---: | ---: | ---: | ---: | ---: |
| all | 81 | 14 | 1.07 | 0.72 to 1.38 | 81 |
| panjabi's measures | 57 | 9 | 1.15 | 0.90 to 1.43 | 91 |
| the papers' own | 24 | 5 | 0.76 | 0.34 to 1.16 | 58 |

| measure | whose | cells | median tau / SD | worth of an infinite pool, scans (median) |
| --- | --- | ---: | ---: | ---: |
| pedicle_incl_sag | Panjabi's | 7 | 2.78 | 0.1 |
| h_ant | the papers' own | 7 | 1.61 | 0.5 |
| endplate | Panjabi's | 5 | 1.53 | 0.6 |
| endplate_lower | Panjabi's | 5 | 1.28 | 0.7 |
| pedicle_h | Panjabi's | 9 | 1.24 | 0.9 |
| h_post | Panjabi's | 7 | 1.19 | 0.9 |
| canal_area | Panjabi's | 5 | 1.11 | 1.0 |
| canal_ap | Panjabi's | 5 | 1.06 | 1.2 |
| pedicle_chord [along the axis] | the papers' own | 5 | 0.98 | 1.1 |
| canal_w | Panjabi's | 5 | 0.95 | 1.2 |
| pedicle_w | Panjabi's | 9 | 0.57 | 3.1 |
| foramen_h | the papers' own | 5 | 0.44 | 6.2 |
| interpedicular | the papers' own | 5 | 0.32 | 11.9 |
| h_mid | the papers' own | 2 | 0.23 | 28.5 |
<!-- end all_spread -->

## Every paper its own population

The owner's word of 2026-10-29, 23:43 UTC: keep the populations separate and predict as a meta-analysis
predicts, never merge them all together. The pooling above already does the first half: every cell of
the papers' table pools its series by random effects (pooling.py's REML tau, Higgins's prediction interval
for one more population's mean), so the papers are combined as a meta-analysis combines them. The tables B
and C then keep only the pooled mean and the within-person SD, so a population drawn from them, and the
rule built on them, merges every paper into one and drops tau. synthval/strata.py keeps each paper a
population of its own, the stratum a paper (a cohort, a sex or a variable of the population register
the owner asked for on 2026-10-29, on pull request 43's branch, is the same code with another grouping), its cohorts
one population with the
mean weighted by their counts and the SD over all its people, and asks what the rule built on the
others does on it, over the lumbar run L1 to L5 where most of the papers print, on three readings, each
paired on the same fields (run_strata.py, records/strata, 1,000 columns a population, each on a seed of
its own):

- every paper left out in turn, scored on the measures it prints at every lumbar level that the other
  papers still pool there and that carry a modelled error (22 papers, 1 to 15 measures each), on columns
  drawn from its own means, with its own SD where it prints a certain one and the others' pooled SD where
  not (Tan's 75 cells);
- the nine papers that print the pedicle's width and height at every lumbar level, scored on those two
  alone, so every population is read on the same measures;
- eight populations drawn from the random-effects model itself on the seven SPINEPS measures, each
  cell's pooled mean moved by the spread of one more population's mean, sqrt(tau^2 + SE^2), 82% of that
  variance as one shift through the whole measure and the rest cell by cell, the split the first part
  calibrated.

Each population is named by four rules on the same fields: its own table, the loss's zero; the others'
random-effects pool with the within SD, as tables B and C hold it (merged); its own means with the others'
SD (own means, the others' SD), whose loss is what the SD difference alone costs, the rest of the merged
rule's being the shift of the means; and the same means with every
SD widened for a population the rule has not seen, sqrt(sd^2 + tau^2 + SE^2) (predicted), the SE
taken under the same tau, 1 / sum 1 / (v_i + tau^2) over the series' variances, so a cell printed by one
series spreads by sqrt(2 tau^2 + sd^2 / n), that series being itself a population away from the grand
mean. A cell with three series or more has a tau of its own (81 of 694); one with fewer takes its
measure's median tau over SD from the cells that have one (205), else every cell's median, 1.07 (408),
and the record says which. The widened SD is 1.71 to 1.84 times the within SD over the quartiles of
cells. The medians a left-out paper's rule borrows are taken over the cells pooled without that paper,
so nothing of it reaches the rule scored on it: without Tan 2004 the overall median is 0.77, and
frontphys2026's end-plate measures lose their own median (loo.csv says which measures fell and the
median without each paper). The per-paper losses are then combined by random effects as a
meta-analysis combines studies, giving the loss one more population is predicted to bring and its
interval.

<!-- table strata -->
| reading | bodies | populations | merged: loss (SE) | one more population | spread | predicted: loss (SE) | one more population | spread | the others' SD alone: loss (SE) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| every measure the paper prints | 1 | 22 | 8.8 (1.4) | -5.4 to 23.1 | 6.7 | 8.8 (1.4) | -5.4 to 23.1 | 6.7 | 2.2 (0.7) |
| every measure the paper prints | 2 | 22 | 11.8 (1.7) | -5.5 to 29.1 | 8.1 | 11.9 (1.9) | -6.9 to 30.7 | 8.8 | 3.8 (1.2) |
| every measure the paper prints | 3 | 22 | 12.2 (1.8) | -5.8 to 30.1 | 8.4 | 12.0 (1.8) | -6.0 to 29.9 | 8.4 | 4.0 (1.2) |
| the pedicle's width and height | 1 | 9 | 8.5 (1.6) | -3.3 to 20.2 | 4.7 | 7.1 (1.4) | -3.2 to 17.4 | 4.1 | 0.7 (0.3) |
| the pedicle's width and height | 2 | 9 | 10.4 (2.2) | -6.0 to 26.8 | 6.6 | 9.1 (1.9) | -4.8 to 23.0 | 5.6 | 0.8 (0.3) |
| the pedicle's width and height | 3 | 9 | 11.2 (1.8) | -2.3 to 24.6 | 5.4 | 10.6 (2.2) | -6.0 to 27.2 | 6.6 | 1.0 (0.3) |
| a population drawn from the model | 1 | 8 | 24.9 (1.7) | 12.3 to 37.5 | 4.8 | 21.5 (1.8) | 8.7 to 34.3 | 4.9 | - |
| a population drawn from the model | 2 | 8 | 33.5 (3.2) | 10.1 to 56.8 | 9.0 | 28.1 (2.9) | 7.1 to 49.1 | 8.1 | - |
| a population drawn from the model | 3 | 8 | 29.2 (4.7) | -5.6 to 63.9 | 13.4 | 22.9 (3.2) | -0.3 to 46.2 | 9.0 | - |

| reading | bodies | merged: exact (%) | answered at 0.99 (%) | right, over the answers (%) | right, mean over the populations (least) (%) | predicted: exact (%) | answered at 0.99 (%) | right, over the answers (%) | right, mean over the populations (least) (%) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| every measure the paper prints | 1 | 39.8 | 3.7 | 92 | 95 (55) | 39.8 | 1.5 | 94 | 97 (63) |
| every measure the paper prints | 2 | 49.0 | 6.4 | 87 | 94 (52) | 49.0 | 2.7 | 86 | 96 (54) |
| every measure the paper prints | 3 | 60.2 | 10.1 | 89 | 94 (63) | 60.4 | 4.7 | 88 | 95 (61) |
| the pedicle's width and height | 1 | 40.8 | 3.4 | 94 | 98 (89) | 42.2 | 1.6 | 98 | 99 (96) |
| the pedicle's width and height | 2 | 50.9 | 4.5 | 95 | 98 (91) | 52.2 | 2.0 | 98 | 100 (96) |
| the pedicle's width and height | 3 | 61.2 | 6.0 | 96 | 98 (93) | 61.8 | 2.8 | 98 | 100 (97) |
| a population drawn from the model | 1 | 47.6 | 4.4 | 98 | 94 (69) | 51.1 | 0.2 | 100 | 100 (100) |
| a population drawn from the model | 2 | 56.2 | 16.1 | 83 | 87 (63) | 61.6 | 0.4 | 100 | 100 (100) |
| a population drawn from the model | 3 | 67.2 | 23.6 | 86 | 88 (59) | 73.4 | 1.4 | 100 | 100 (100) |

| paper left out | measures | cells with its own SD | people | its SD over the others' | own table: exact (%) | merged: loss (SE) | answered at 0.99 (%) | right (%) | predicted: loss (SE) | answered at 0.99 (%) | right (%) | the others' SD alone: loss (SE) |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| frontphys2026 | 5 | 25 of 25 | 20 | 0.42 | 87.7 | 32.9 (1.2) | 7.4 | 84 | 30.2 (1.3) | 0.1 | 100 | 18.2 (1.1) |
| otsuki2021 | 3 | 15 of 15 | 6 | 1.30 | 88.1 | 27.1 (1.1) | 16.7 | 93 | 20.0 (0.9) | 11.0 | 99 | 5.7 (0.7) |
| busscher2010 | 3 | 15 of 15 | 6 | 1.37 | 85.7 | 23.4 (1.0) | 2.7 | 77 | 23.2 (1.0) | 0.1 | 67 | 14.9 (0.9) |
| arockiaraj2025 | 4 | 20 of 20 | 300 | 0.62 | 86.3 | 19.6 (0.7) | 17.0 | 100 | 23.1 (0.8) | 2.8 | 100 | 2.0 (0.5) |
| tan2004 | 15 | 0 of 75 | 10 | - | 96.6 | 19.3 (0.8) | 43.1 | 94 | 17.9 (0.7) | 25.4 | 99 | 0.0 (0.0) |
| yadav2020 | 5 | 25 of 25 | 302 | 2.10 | 70.2 | 18.5 (1.2) | 40.9 | 63 | 20.8 (1.2) | 29.3 | 61 | 16.7 (1.1) |
| lien2007 | 4 | 20 of 20 | 15 | 1.02 | 86.1 | 16.9 (0.8) | 17.0 | 99 | 19.7 (1.0) | 8.8 | 98 | 0.4 (0.4) |
| moncadahabib2025 | 6 | 30 of 30 | 37 | 0.98 | 73.1 | 13.5 (1.1) | 9.3 | 92 | 15.8 (1.1) | 0.8 | 100 | 9.5 (1.0) |
| yu2015 | 2 | 10 of 10 | 503 | 0.86 | 78.0 | 12.3 (1.0) | 12.4 | 99 | 6.8 (0.8) | 4.0 | 100 | 0.1 (0.3) |
| bach2019 | 4 | 20 of 20 | 240 | 0.99 | 73.3 | 11.6 (0.9) | 2.2 | 97 | 6.7 (0.8) | 0.0 | - | 2.0 (0.5) |
| shin2024 | 4 | 20 of 20 | 2800 | 1.01 | 70.8 | 11.1 (0.9) | 1.6 | 98 | 20.9 (1.0) | 0.0 | - | 1.2 (0.5) |
| griffith2016 | 3 | 15 of 15 | 1080 | 1.15 | 70.1 | 9.6 (1.0) | 8.1 | 98 | 6.6 (0.9) | 0.0 | 100 | 2.3 (0.7) |
| masharawi2021 | 5 | 25 of 25 | 50 | 1.20 | 71.4 | 9.2 (1.0) | 11.6 | 92 | 8.1 (1.0) | 3.4 | 98 | 3.5 (0.8) |
| alonge2021 | 2 | 10 of 10 | 120 | 1.02 | 65.5 | 8.9 (1.0) | 4.8 | 99 | 3.9 (0.8) | 0.1 | 100 | 0.3 (0.5) |
| olsewski1990 | 4 | 20 of 20 | 49 | 1.26 | 79.1 | 8.7 (0.8) | 21.4 | 99 | 9.5 (1.0) | 15.4 | 98 | 1.5 (0.5) |
| amonookuofi1982 | 1 | 5 of 5 | 290 | 0.65 | 54.8 | 7.1 (1.0) | 0.0 | - | 5.2 (1.0) | 0.0 | - | 2.5 (0.8) |
| hou1993 | 2 | 10 of 10 | 40 | 0.89 | 73.1 | 5.7 (0.8) | 1.4 | 100 | 7.4 (0.9) | 0.3 | 100 | 1.2 (0.6) |
| amonookuofi1985 | 1 | 5 of 5 | 122 | 0.65 | 53.6 | 3.1 (0.8) | 0.0 | - | 4.6 (0.8) | 0.0 | - | 1.8 (0.7) |
| abbas2021 | 2 | 10 of 10 | 180 | 0.87 | 62.4 | 2.8 (0.8) | 0.2 | 100 | 4.7 (0.9) | 0.0 | - | 2.0 (0.8) |
| chaudhary2015 | 1 | 5 of 5 | 300 | 1.36 | 52.2 | 2.8 (0.8) | 0.9 | 100 | 3.2 (0.9) | 0.7 | 100 | 2.0 (0.7) |
| cizmic2023 | 2 | 10 of 10 | 200 | 0.99 | 65.3 | 2.3 (0.6) | 2.1 | 100 | 2.6 (0.7) | 0.0 | - | -0.2 (0.5) |
| hinck1966 | 1 | 5 of 5 | 90 | 1.11 | 49.3 | 2.1 (0.9) | 0.4 | 100 | 2.8 (0.8) | 0.0 | - | 1.8 (0.6) |

| the strata | value |
| --- | ---: |
| placed cells | 694 |
|   with a tau of their own (three series or more) | 81 |
|   taking their measure's median tau over SD | 205 |
|   taking every cell's median, 1.07 | 408 |
| predictive SD over the within SD, quartiles | 1.71 / 1.82 / 1.84 |
| share of the spread one shift through a measure carries (the first part's split) | 82% |
| columns drawn a population / populations drawn from the model | 1000 / 8 |
<!-- end strata -->

The first table's loss is in points of fields named exactly, the pooled mean over the papers (its SE), the
interval for one more population (Higgins's, on the spread between papers), that spread, and in the last
column the loss under the others' SD alone; the second the promise at 0.99; the third each paper at three
bodies, its SD over the others' and the others' SD alone; the fourth where the taus came from, the
widened SD's quartiles, the split's share and the sizes.

A rule built on the other papers loses a pooled 8.8 points at one body, 11.8 at two and 12.2 at three
against the paper's own table, with a spread between papers of 6.7 to 8.4 points, so one more population
is predicted to lose anywhere from nothing to about 30 (the interval -5 to 23 at one body, -6 to 30 at
three): at three bodies frontphys2026, Otsuki 2021, Busscher 2010, Arockiaraj 2025, Tan 2004 and Yadav
2020 lose 18 to 33 points, and Hinck 1966, Cizmic 2023, Chaudhary 2015, Abbas 2021 and Amonoo-Kuofi
1985 3 or under; the loss follows how far a paper's means sit from the others' and not how many measures
it prints (Tan's 15 lose 19, Otsuki's 3 lose 27). The SD difference alone, a paper's own means scored
under the others' SD, costs a pooled 2.2, 3.8 and 4.0 points at one, two and three bodies, so the shift
of the means carries about two thirds of the loss, though for the four populations whose SDs sit
furthest from the pool's it carries half or more (frontphys2026 18 of its 33, Busscher 2010 15 of 23,
Yadav 2020 17 of 19, Moncada-Habib 2025 10 of 14); on the pedicle pair the SD difference costs 0.7 to
1.0 of 8.5 to 11.2. Widening every SD by tau changes exact naming by a paired 0.2 points or less at
every width (SD 2.9 to 3.6 over the 22 papers; 0.6 to 1.3 points better on the pedicle pair, within its
SE): no SD undoes a shift of the means. What the widening changes is the promise at 0.99. The merged rule answers at 0.99 on 3.7, 6.4 and 10.1% of fields
at one, two and three bodies and is right on 92, 87 and 89% of those answers taken together (94 to 95%
on a mean over the papers); the widened rule answers on 1.5, 2.7 and 4.7% and is right on 94, 86 and
88% (95 to 97% on the mean). Both floors are Yadav 2020's: 878 of the widened rule's 3,069 answers at
three bodies are on its population and 346 of them wrong, since its own SDs are 2.1 times the others'
pooled SD (every end-plate cell 2.1 to 6.0), so its people spread twice as wide as any table the rule is
built on and a widening of 1.8 is not enough. Yadav apart, the widened rule is right on 99% of its
answers at every width against the merged rule's 96 to 97%. On the pedicle pair, read on the same two
measures for every population, the widened rule is right on 98% of its answers at every width (least
paper 96 to 97%) against 94 to 96% (least 89 to 93%). On the populations drawn from the model itself,
which are what the widened SD assumes, the merged rule's answers are right on 98, 83 and 86% (the least
population 59 to 69%) and the widened rule's on 100% at every width, answering on 0.2 to 1.4% of fields,
while it names 3 to 6 points more of them exactly. Those drawn populations lose 25, 34 and 29 points
under the merged rule and 22, 28 and 23 under the widened, more than any pooled reading of the real
papers, since 25 of the seven's 35 lumbar cells carry a tau of their own, 0.9 to 3.5 within SDs, the
ten depth cells borrow every cell's median, and the model moves every cell by it; at one and two bodies the real papers' pooled loss sits below the
bottom of the model's interval (12 and 10 points), so the model overstates what a real paper brings, and
only at three bodies does every real paper sit inside it. Four real populations stay under 90% right
under one rule or the other: Yadav 2020 (63 and 61% at three bodies), Busscher 2010 (77% on 81 answers,
and 2 of 3 under the widened rule), frontphys2026 (84% under the merged rule, where the widened rule
answers on 0.1% of fields and is right) and, at one body, Otsuki 2021 (87 and 97%); Busscher's and
Otsuki's six people print SDs 1.3 to 1.4 times the pool's, frontphys2026's twenty 0.42 of it. A rule
that holds the strata themselves, a mixture over populations rather than one widened table, is the next
thing to try, and whether schwingcheck's rule should carry the widened SD is the owner's to choose; this
note changes neither.

## Choosing the rule by held-out prediction

The owner's words of 2026-10-30, 02:10 UTC: "cant you figure out what works best? I just want a
statistically valid way to maximize predictive ability that doesnt necessary have to rooted in realistic
biology". So the rule is chosen as a model is chosen in machine learning, on populations it has never
seen, and the strata above are the test set: each of the 22 papers of the leave-one-out is held out in
turn, on the same columns drawn on the same seeds, five candidate rules are built on the other papers
alone, and each is scored on the held-out population at one, two and three bodies on the same fields
(synthval/select.py, run_select.py, records/select). The candidates: the others' random-effects pool
with the within SD, as tables B and C hold it (plain, the merged rule above); the same with every SD
widened by tau, sqrt(sd^2 + tau^2 + SE^2) (widened, the predicted rule above, with no knob); the same
with every SD multiplied by one factor k (scaled); the plain rule with its log evidence divided by a
temperature T before the posterior is taken (tempered), which moves the posterior's confidence and never
which place wins; and a mixture, one table per other paper, the pool with that paper's own cells put in
where it prints them, the field's evidence the equal-weight average over those tables. The two knobs are
set by a second leave-one-out nested inside the training papers: for each held-out paper, every other
paper that prints any of its measures is held out of the rest in turn on 150 columns, the rule built on
the rest is scored over the grids k in 0.7 to 3 and T in 0.5 to 8, and k takes the best mean log score
over those folds and the three widths, T the best per width; the held-out paper is dropped from the
cells first, its stratum and its series, so nothing of it reaches the choice. Every rule is read by the
share of fields named exactly, by the log score, the mean log posterior probability of the true place,
whose negative is the log loss in nats and the proper score the choice is made on, by the expected
calibration error of the top probability over ten bins, and by the promise at 0.99. The held-out paper's
own table is scored beside them, the best any rule of this kind can do on that population. Each
population is one fold with the same weight: a candidate's number is its mean over the 22 with the SE
across them, and its difference from the plain rule the paired difference per population with its SE
across them. Choosing the best of five on the same folds is a small selection; each candidate's own
number is honest.

<!-- table select -->
| candidate | bodies | log loss (SE) | log loss minus plain (SE) | beats plain | accuracy % (SE) | accuracy minus plain (SE) | calibration error | answered at 0.99 (%) | right (%) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| own table | 1 | 1.145 (0.056) | - | - | 48.7 (2.6) | - | 0.002 | 3.1 | 100 |
| plain | 1 | 1.431 (0.071) | - | - | 39.8 (1.7) | - | 0.094 | 3.7 | 92 |
| widened by tau | 1 | 1.373 (0.050) | -0.058 (0.030) | 14 of 22 | 39.8 (1.7) | 0.0 (0.6) | 0.027 | 1.5 | 94 |
| scaled SD | 1 | 1.403 (0.066) | -0.028 (0.016) | 14 of 22 | 39.0 (1.9) | -0.8 (0.7) | 0.044 | 1.6 | 90 |
| tempered | 1 | 1.342 (0.040) | -0.090 (0.049) | 15 of 22 | 39.8 (1.7) | 0.0 (0.0) | 0.020 | 1.1 | 99 |
| mixture | 1 | 1.411 (0.065) | -0.021 (0.017) | 15 of 22 | 40.2 (1.8) | 0.4 (0.3) | 0.069 | 2.7 | 88 |
| own table | 2 | 0.855 (0.060) | - | - | 60.9 (3.0) | - | 0.004 | 6.5 | 100 |
| plain | 2 | 1.243 (0.110) | - | - | 49.0 (1.8) | - | 0.110 | 6.4 | 87 |
| widened by tau | 2 | 1.168 (0.078) | -0.076 (0.041) | 15 of 22 | 49.0 (1.9) | -0.0 (0.7) | 0.039 | 2.7 | 86 |
| scaled SD | 2 | 1.205 (0.103) | -0.038 (0.018) | 16 of 22 | 48.1 (2.0) | -0.9 (0.8) | 0.049 | 3.0 | 81 |
| tempered | 2 | 1.127 (0.056) | -0.116 (0.065) | 17 of 22 | 49.0 (1.8) | 0.0 (0.0) | 0.037 | 2.2 | 90 |
| mixture | 2 | 1.237 (0.113) | -0.007 (0.010) | 13 of 22 | 49.3 (1.8) | 0.3 (0.3) | 0.089 | 5.1 | 83 |
| own table | 3 | 0.590 (0.052) | - | - | 72.4 (2.8) | - | 0.003 | 12.2 | 100 |
| plain | 3 | 0.957 (0.099) | - | - | 60.2 (1.7) | - | 0.101 | 10.1 | 89 |
| widened by tau | 3 | 0.892 (0.077) | -0.064 (0.032) | 13 of 22 | 60.4 (1.8) | 0.2 (0.8) | 0.042 | 4.7 | 88 |
| scaled SD | 3 | 0.909 (0.095) | -0.047 (0.016) | 16 of 22 | 59.8 (1.9) | -0.4 (0.6) | 0.039 | 4.9 | 85 |
| tempered | 3 | 0.849 (0.048) | -0.108 (0.059) | 16 of 22 | 60.2 (1.7) | 0.0 (0.0) | 0.039 | 3.1 | 91 |
| mixture | 3 | 0.941 (0.099) | -0.016 (0.008) | 13 of 22 | 60.7 (1.8) | 0.5 (0.3) | 0.086 | 8.6 | 89 |

| paper held out | measures | inner folds | SD factor k | T at 1 | T at 2 | T at 3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| abbas2021 | 2 | 7 | 1.75 | 2.8 | 2.8 | 2.8 |
| alonge2021 | 2 | 7 | 1.20 | 2.0 | 1.4 | 1.4 |
| amonookuofi1982 | 1 | 2 | 1.20 | 1.0 | 1.0 | 1.4 |
| amonookuofi1985 | 1 | 7 | 1.45 | 2.8 | 2.0 | 1.4 |
| arockiaraj2025 | 4 | 8 | 1.45 | 1.4 | 1.4 | 1.4 |
| bach2019 | 4 | 2 | 1.20 | 1.4 | 1.4 | 1.4 |
| busscher2010 | 3 | 3 | 1.00 | 2.0 | 2.0 | 2.0 |
| chaudhary2015 | 1 | 2 | 1.45 | 2.0 | 2.0 | 2.0 |
| cizmic2023 | 2 | 7 | 1.20 | 1.4 | 1.4 | 1.4 |
| frontphys2026 | 5 | 4 | 3.00 | 2.8 | 5.6 | 5.6 |
| griffith2016 | 3 | 7 | 1.45 | 2.0 | 2.0 | 2.0 |
| hinck1966 | 1 | 2 | 1.45 | 1.4 | 2.0 | 2.0 |
| hou1993 | 2 | 8 | 1.45 | 2.0 | 2.0 | 2.0 |
| lien2007 | 4 | 8 | 1.45 | 1.4 | 1.4 | 1.4 |
| masharawi2021 | 5 | 16 | 1.45 | 2.0 | 1.4 | 1.4 |
| moncadahabib2025 | 6 | 10 | 1.45 | 2.0 | 2.0 | 2.0 |
| olsewski1990 | 4 | 8 | 1.45 | 2.0 | 2.0 | 2.0 |
| otsuki2021 | 3 | 8 | 1.45 | 2.0 | 2.0 | 2.0 |
| shin2024 | 4 | 2 | 1.45 | 2.0 | 2.0 | 2.0 |
| tan2004 | 15 | 16 | 1.45 | 2.0 | 2.0 | 2.8 |
| yadav2020 | 5 | 8 | 1.20 | 2.8 | 2.0 | 2.0 |
| yu2015 | 2 | 8 | 1.45 | 1.4 | 2.0 | 2.0 |

| the selection | value |
| --- | ---: |
| winner by held-out log score | tempered |
| winner by held-out accuracy | mixture |
| populations held out / columns a population / columns an inner fold | 22 / 1000 / 150 |
| the SD factor's grid | 0.7, 0.85, 1, 1.2, 1.45, 1.75, 2.1, 2.5, 3 |
| the temperature's grid | 0.5, 0.7, 1, 1.4, 2, 2.8, 4, 5.6, 8 |
<!-- end select -->

The first table is each candidate at each width over the 22 held-out populations: the log loss (its SE
over the populations), the paired difference from the plain rule (its SE), how many populations it beats
the plain rule on, exact naming with the same, the calibration error over every field pooled, and the
promise at 0.99 pooled over the answers; the second each paper's inner choice of the factor and the
temperature with its inner folds; the third the winners, the sizes and the grids.

Tempering wins on the log loss at every width: 1.342, 1.127 and 0.849 nats at one, two and three bodies
against the plain rule's 1.431, 1.243 and 0.957, a paired 0.090, 0.116 and 0.108 below it (SE 0.049 to
0.065), better on 15, 17 and 16 of the 22 populations, and it names exactly what the plain rule names,
by construction. Half of the mean gain is Yadav 2020's, 1.07 to 1.28 nats on its population, whose
people spread twice as wide as the pool; without it the gain is 0.043, 0.053 and 0.052 (SE 0.015 to
0.020), better on 14, 16 and 15 of 21. The inner choice fell on T = 2 for 11 to 13 of the 22 papers, 1.4
for 6 to 8 and 2.8 for 1 to 4, and the curve over T on the held-out populations bottoms at 2 at every
width, so the nested choice sits where the held-out best is. The calibration error falls from 0.094,
0.110 and 0.101 to 0.020, 0.037 and 0.039. The widened rule is second, 0.058, 0.076 and 0.064 nats below
plain (SE 0.030 to 0.041) with no knob, a calibration error of 0.027, 0.039 and 0.042 and the same
naming. The scaled rule's factor fell on 1.45 for 14 of 22 papers, where the held-out curve over k
bottoms too, and it gains 0.028 to 0.047 nats while losing 0.4 to 0.9 points of naming, since one factor
for every cell is wrong for the population it is scored on more often than the cell's own tau is. The
mixture is the only candidate that names more: 0.4, 0.3 and 0.5 points over plain (SE 0.3), 5.0 on Yu
2015 and 3.3 on Arockiaraj 2025 and Otsuki 2021 at three bodies, 1 to 2 less on Olsewski 1990 and
Griffith 2016; its log loss sits 0.007 to 0.021 below plain and its calibration error at 0.069 to 0.089,
as overconfident as the plain rule, since every component is as sure as the pool. The promise at 0.99
under the tempered rule: it answers on 1.1, 2.2 and 3.1% of fields (plain 3.7, 6.4 and 10.1) and is right
on 99, 90 and 91% of those answers taken together, Yadav 2020 again the floor, with 170 of the 178
errors at three bodies; Yadav apart it is right on 99.9, 99.6 and 99.5% against the plain rule's 96.3,
96.6 and 95.5% and the widened rule's 98.8 to 99.1%. No candidate closes the gap to a population's own
table, 0.29 to 0.37 nats and 9 to 12 points of exact naming: that gap is the shift of the means between
populations, which no SD, temperature or mixture of the populations seen undoes, and only the
population's own data would.

What this note takes from it: the rule to carry is the plain rule with its posterior tempered by T = 2
at every width, one division before the posterior, which keeps every name and makes the 0.99 label mean
what it says on every population but the one whose people spread twice as wide as any table; the
widened rule does nearly as much with no knob, and the two can be combined, as can the mixture with the
tempering, neither tried here. Whether schwingcheck's rule carries the temperature is the owner's to
choose; this note changes nothing of it. The population register has landed (pull request 43), and
running the same selection over its populations, with the mixture's components the register's strata,
is the next step (HANDOFF.md).

## Leaving a paper out, scored held out

The owner chose on 2026-10-30, 03:05 UTC, on a card that asked whether to leave Yadav 2020 out of the
prior outright or let the held-out score decide, the second. Cell by cell, Yadav's SD is 0.80 to 1.08
times the other seven papers' pooled SD on the canal's depth at L1 to L5, and 2.1 to 6.0 times at the
end plate's width and 2.2 to 5.7 times at the lower end plate's, where the only other series with an
SD of its own is Front. Phys. 2026's (20 people, 0.6 to 2.4 mm, against Yadav's 302 at 3.5 to 5.0 mm)
and Tan 2004's 10 carry none; at the end plates' depths it is 1.6 to 3.7 times an SD borrowed from Tan
alone. So the disagreement at the end plates is two papers', and the selection above takes each side
of it as candidates (synthval/select.py): the plain rule built as if Yadav 2020 had never been read,
the same without Front. Phys. 2026, and one vote per population, every cell's SD the geometric mean of
the other populations' own SDs whatever their sizes, so that two papers disagreeing on a spread meet
halfway; each of the three also tempered, its own temperature chosen by the same inner leave-one-out on
its own rule. Leaving a paper out changes nothing on the fold that holds it out, where the plain rule
never reads it anyway, and a cell no third paper prints keeps the plain rule's value and is counted
(fallback_cells in records/select/scores.csv), so every candidate scores the same measures on the same
fields.

<!-- table exclusion -->
| candidate | bodies | log loss (SE) | log loss minus plain (SE) | beats plain | accuracy % (SE) | accuracy minus plain (SE) | calibration error | answered at 0.99 (%) | right (%) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plain | 1 | 1.431 (0.071) | - | - | 39.8 (1.7) | - | 0.094 | 3.7 | 92 |
| tempered | 1 | 1.342 (0.040) | -0.090 (0.049) | 15 of 22 | 39.8 (1.7) | 0.0 (0.0) | 0.020 | 1.1 | 99 |
| without yadav2020 | 1 | 1.484 (0.089) | 0.053 (0.051) | 2 of 22 | 39.3 (1.9) | -0.5 (0.5) | 0.106 | 3.9 | 90 |
| without yadav2020, tempered | 1 | 1.350 (0.042) | -0.081 (0.049) | 14 of 22 | 39.3 (1.9) | -0.5 (0.5) | 0.022 | 1.2 | 99 |
| without frontphys2026 | 1 | 1.427 (0.053) | -0.004 (0.022) | 1 of 22 | 39.3 (1.7) | -0.5 (0.3) | 0.100 | 3.3 | 94 |
| without frontphys2026, tempered | 1 | 1.346 (0.037) | -0.086 (0.053) | 14 of 22 | 39.3 (1.7) | -0.5 (0.3) | 0.019 | 1.0 | 100 |
| one vote per population | 1 | 1.435 (0.071) | 0.003 (0.002) | 8 of 22 | 39.7 (1.7) | -0.1 (0.0) | 0.097 | 3.9 | 92 |
| one vote per population, tempered | 1 | 1.342 (0.040) | -0.090 (0.049) | 17 of 22 | 39.7 (1.7) | -0.1 (0.0) | 0.019 | 1.2 | 99 |
| plain | 2 | 1.243 (0.110) | - | - | 49.0 (1.8) | - | 0.110 | 6.4 | 87 |
| tempered | 2 | 1.127 (0.056) | -0.116 (0.065) | 17 of 22 | 49.0 (1.8) | 0.0 (0.0) | 0.037 | 2.2 | 90 |
| without yadav2020 | 2 | 1.287 (0.118) | 0.044 (0.039) | 3 of 22 | 48.8 (1.8) | -0.3 (0.2) | 0.118 | 7.3 | 86 |
| without yadav2020, tempered | 2 | 1.127 (0.055) | -0.116 (0.065) | 16 of 22 | 48.8 (1.8) | -0.3 (0.2) | 0.034 | 2.3 | 91 |
| without frontphys2026 | 2 | 1.256 (0.100) | 0.013 (0.017) | 1 of 22 | 48.3 (1.8) | -0.7 (0.4) | 0.117 | 5.9 | 87 |
| without frontphys2026, tempered | 2 | 1.132 (0.052) | -0.111 (0.068) | 17 of 22 | 48.3 (1.8) | -0.7 (0.4) | 0.033 | 1.6 | 93 |
| one vote per population | 2 | 1.246 (0.110) | 0.002 (0.005) | 9 of 22 | 49.0 (1.7) | -0.0 (0.1) | 0.111 | 6.7 | 87 |
| one vote per population, tempered | 2 | 1.128 (0.055) | -0.115 (0.065) | 17 of 22 | 49.0 (1.7) | -0.0 (0.1) | 0.035 | 1.9 | 89 |
| plain | 3 | 0.957 (0.099) | - | - | 60.2 (1.7) | - | 0.101 | 10.1 | 89 |
| tempered | 3 | 0.849 (0.048) | -0.108 (0.059) | 16 of 22 | 60.2 (1.7) | 0.0 (0.0) | 0.039 | 3.1 | 91 |
| without yadav2020 | 3 | 0.997 (0.109) | 0.041 (0.037) | 3 of 22 | 60.1 (1.7) | -0.1 (0.1) | 0.107 | 11.4 | 87 |
| without yadav2020, tempered | 3 | 0.849 (0.048) | -0.108 (0.059) | 16 of 22 | 60.1 (1.7) | -0.1 (0.1) | 0.036 | 3.3 | 92 |
| without frontphys2026 | 3 | 0.982 (0.099) | 0.026 (0.014) | 1 of 22 | 59.5 (1.6) | -0.7 (0.4) | 0.107 | 9.6 | 88 |
| without frontphys2026, tempered | 3 | 0.861 (0.048) | -0.096 (0.058) | 15 of 22 | 59.5 (1.6) | -0.7 (0.4) | 0.040 | 2.6 | 93 |
| one vote per population | 3 | 0.962 (0.098) | 0.006 (0.005) | 8 of 22 | 60.2 (1.6) | -0.0 (0.1) | 0.103 | 10.4 | 89 |
| one vote per population, tempered | 3 | 0.851 (0.048) | -0.106 (0.059) | 16 of 22 | 60.2 (1.6) | -0.0 (0.1) | 0.033 | 2.7 | 90 |

| paper held out | without yadav2020: log score minus plain at 3 bodies | without frontphys2026: log score minus plain at 3 bodies | one vote per population: log score minus plain at 3 bodies | measures |
| --- | ---: | ---: | ---: | ---: |
| alonge2021 | 0.001 | 0.000 | -0.007 | 2 |
| amonookuofi1982 | 0.000 | 0.000 | 0.001 | 1 |
| amonookuofi1985 | -0.002 | 0.000 | 0.001 | 1 |
| arockiaraj2025 | 0.000 | 0.000 | -0.003 | 4 |
| bach2019 | 0.000 | 0.000 | 0.002 | 4 |
| busscher2010 | 0.000 | -0.194 | 0.020 | 3 |
| chaudhary2015 | 0.000 | 0.000 | -0.016 | 1 |
| cizmic2023 | -0.006 | 0.000 | -0.001 | 2 |
| frontphys2026 | -0.806 | 0.000 | -0.032 | 5 |
| griffith2016 | 0.001 | 0.000 | 0.003 | 3 |
| hou1993 | 0.000 | 0.000 | -0.005 | 2 |
| lien2007 | 0.000 | 0.000 | -0.025 | 4 |
| masharawi2021 | -0.005 | 0.000 | -0.026 | 5 |
| moncadahabib2025 | 0.000 | -0.156 | 0.059 | 6 |
| olsewski1990 | 0.000 | 0.000 | -0.014 | 4 |
| otsuki2021 | 0.000 | 0.000 | -0.002 | 3 |
| tan2004 | -0.082 | -0.214 | -0.071 | 15 |
| yadav2020 | 0.000 | 0.002 | 0.001 | 5 |
| yu2015 | 0.000 | 0.000 | -0.010 | 2 |

| rule the temperature is read on | T at 1, median (range) | T at 2, median (range) | T at 3, median (range) |
| --- | ---: | ---: | ---: |
| plain | 2.0 (1.0 to 2.8) | 2.0 (1.0 to 5.6) | 2.0 (1.4 to 5.6) |
| without yadav2020 | 2.0 (1.0 to 2.8) | 2.0 (1.0 to 5.6) | 2.0 (1.4 to 5.6) |
| without frontphys2026 | 2.0 (1.0 to 2.8) | 2.0 (1.0 to 5.6) | 2.0 (1.4 to 5.6) |
| one vote per population | 2.0 (1.0 to 2.8) | 2.0 (1.0 to 5.6) | 2.0 (1.4 to 5.6) |
<!-- end exclusion -->

The first table is the exclusion candidates beside the plain and tempered rules, as the selection's
first table gives them; the second each held-out population at three bodies where any untempered
candidate moves its log score by 0.0005 nats or more, in log score minus plain (right is better); the
third the temperature each rule's inner leave-one-out chose.

Leaving Yadav 2020 out costs more than it saves: 0.053, 0.044 and 0.041 nats of held-out log loss at
one, two and three bodies against the plain rule (SE 0.051, 0.039 and 0.037), better on 2, 3 and 3 of
the 22 populations, and 0.81 nats on Front. Phys. 2026's own population at three bodies, whose
end-plate prior is then Tan 2004's alone; Tan's population loses 0.08. Leaving Front. Phys. 2026 out
costs less on average, 0.004 better at one body and 0.013 and 0.026 worse at two and three, but it is
better on only one population at each width and costs Busscher 2010 0.19, Moncada-Habib 2025 0.16 and
Tan 2004 0.21 at three bodies, populations that share its other measures. One vote per population is
within 0.006 nats of plain at every width, Tan 0.07 and Moncada-Habib 0.06 apart. The tempering gains
each of them 0.08 to 0.16 nats: tempered, the rule without Yadav is 0.849 at three
bodies, the one-vote rule 0.851, the rule without Front. Phys. 2026 0.861, against the tempered plain
rule's 0.849, and every inner temperature's median is 2. What this note takes from it: no paper leaves
the prior; the spread the two papers disagree on is real disagreement between populations, which the
temperature answers for every population at once and no exclusion answers for any.

## Covariates both ways

The owner's words of 2026-10-30, 02:55 UTC: "i want to demonstrate how this shows there are demographic
and sex and age ect covariate effects on spine morphology and hpw you can predict these covariates based
on the measurements or vice versa". The reread prints no person, but some papers print a cohort's men
and women apart, or its age bands, or (Yu 2015) its body heights and weights, each with a mean, an SD
and a count, and those are read here (synthval/covariates.py, run_covariates.py, records/covariates).
Every effect is read inside one paper first, so none of a paper's own shift (method, specimen,
country) enters it, and the papers are pooled second by REML, as the populations are kept apart
everywhere in this note: a stratum printed for both sexes gives men minus women as Hedges' g, in
within-sex SDs; a series printed over two or more bands gives the weighted least-squares slope of the
band means on the bands' midpoints, in within-band SDs per decade, per 100 mm or per 10 kg. Only a
paper's own people are read (a quoted study is that study's), only measures with a kind, only rows with
an SD and a count of their own, only adults for age (a band from 18), and never a stenosis group or a
size quartile. Then both ways, held out by paper: the effect taken from the other papers alone is put
on the held-out paper's population as a new population would be met, its sexes-pooled mean and SD
known and nothing of its split; shape to sex is the posterior probability of male from one measure at
a known level (AUC, and log loss against ln 2 for equal men and women), sex to shape the measure's
out-of-sample R^2, each beside the population's own split, every expectation exact by quadrature.

<!-- table covariates -->
| covariate | measure | effect in | pooled effect (95% interval) | interval for one more paper | papers | cells | strata | papers named |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| sex | endplate_lower_area | men minus women, within-sex SDs | 1.56 (1.10 to 2.01) | - | 1 | 3 | 3 | tang2016 |
| sex | disc_w | men minus women, within-sex SDs | 1.55 (1.12 to 1.99) | - | 1 | 3 | 3 | tang2016 |
| sex | disc_d | men minus women, within-sex SDs | 1.52 (1.09 to 1.96) | - | 1 | 3 | 3 | tang2016 |
| sex | body_area | men minus women, within-sex SDs | 1.42 (1.28 to 1.55) | - | 1 | 5 | 5 | griffith2016 |
| sex | body_d | men minus women, within-sex SDs | 1.35 (0.87 to 1.83) | - | 1 | 6 | 6 | chen2011 |
| sex | body_d_mid | men minus women, within-sex SDs | 1.33 (1.10 to 1.55) | 0.41 to 2.25 | 4 | 21 | 31 | abbas2021, amonookuofi1985, eisenstein1977, italianmri |
| sex | h_mid | men minus women, within-sex SDs | 1.31 (1.12 to 1.50) | - | 1 | 4 | 4 | duman2026 |
| sex | endplate_area | men minus women, within-sex SDs | 1.31 (0.87 to 1.75) | - | 1 | 3 | 3 | tang2016 |
| sex | body_w_mid | men minus women, within-sex SDs | 1.28 (1.06 to 1.50) | - | 2 | 10 | 20 | abbas2021, eisenstein1977 |
| sex | h_post | men minus women, within-sex SDs | 1.26 (1.07 to 1.45) | - | 1 | 4 | 4 | duman2026 |
| sex | h_ant | men minus women, within-sex SDs | 1.21 (1.03 to 1.40) | - | 1 | 4 | 4 | duman2026 |
| sex | endplate_lower_depth | men minus women, within-sex SDs | 1.10 (0.21 to 2.00) | - | 2 | 9 | 9 | tang2016, yadav2020 |
| sex | endplate | men minus women, within-sex SDs | 0.96 (0.54 to 1.39) | - | 2 | 10 | 10 | tang2016, yadav2020 |
| sex | endplate_lower | men minus women, within-sex SDs | 0.93 (0.22 to 1.65) | - | 2 | 9 | 9 | tang2016, yadav2020 |
| sex | endplate_depth | men minus women, within-sex SDs | 0.86 (0.43 to 1.29) | - | 2 | 10 | 10 | tang2016, yadav2020 |
| sex | pedicle_chord | men minus women, within-sex SDs | 0.85 (0.64 to 1.06) | -0.51 to 2.21 | 3 | 19 | 22 | arockiaraj2025, hou1993, olsewski1990 |
| sex | facet_w_sup | men minus women, within-sex SDs | 0.79 (0.21 to 1.36) | - | 1 | 5 | 5 | masharawi2021 |
| sex | disc_h_mean | men minus women, within-sex SDs | 0.78 (-0.04 to 1.60) | -9.68 to 11.24 | 3 | 18 | 29 | bach2019, twomey1985, yadav2020 |
| sex | lateral_recess | men minus women, within-sex SDs | 0.77 (0.54 to 1.01) | - | 1 | 7 | 7 | yadav2020 |
| sex | pedicle_w | men minus women, within-sex SDs | 0.72 (0.39 to 1.05) | -0.37 to 1.82 | 6 | 33 | 38 | arockiaraj2025, duman2026, hou1993, masharawi2021, olsewski1990, yu2015 |
| sex | disc_h_ant | men minus women, within-sex SDs | 0.70 (0.53 to 0.86) | - | 2 | 11 | 11 | bach2019, shin2024 |
| sex | pedicle_h | men minus women, within-sex SDs | 0.55 (0.29 to 0.80) | -0.27 to 1.36 | 6 | 33 | 38 | arockiaraj2025, duman2026, hou1993, masharawi2021, olsewski1990, yu2015 |
| sex | interpedicular | men minus women, within-sex SDs | 0.50 (0.21 to 0.78) | - | 2 | 10 | 10 | amonookuofi1982, chaudhary2015 |
| sex | canal_w | men minus women, within-sex SDs | 0.45 (0.36 to 0.54) | 0.32 to 0.58 | 6 | 30 | 40 | ahmed2019, alonge2021, cizmic2023, eisenstein1977, griffith2016, masharawi2021 |
| sex | disc_h_mid | men minus women, within-sex SDs | 0.40 (0.18 to 0.62) | - | 2 | 11 | 11 | bach2019, shin2024 |
| sex | foramen_h | men minus women, within-sex SDs | 0.32 (0.08 to 0.55) | - | 2 | 11 | 11 | bach2019, masharawi2021 |
| sex | disc_h_post | men minus women, within-sex SDs | 0.25 (0.12 to 0.38) | - | 2 | 11 | 11 | bach2019, shin2024 |
| sex | canal_area | men minus women, within-sex SDs | 0.17 (-0.03 to 0.38) | - | 2 | 10 | 10 | abbas2021, griffith2016 |
| sex | pedicle_incl_sag | men minus women, within-sex SDs | 0.11 (-0.02 to 0.25) | -0.75 to 0.98 | 3 | 14 | 17 | arockiaraj2025, duman2026, olsewski1990 |
| sex | foramen_w | men minus women, within-sex SDs | 0.05 (-0.15 to 0.24) | - | 2 | 12 | 12 | amonookuofi1985, yadav2020 |
| sex | pedicle_length | men minus women, within-sex SDs | -0.00 (-0.52 to 0.52) | - | 2 | 10 | 10 | arockiaraj2025, masharawi2021 |
| sex | canal_ap | men minus women, within-sex SDs | -0.03 (-0.19 to 0.14) | -0.56 to 0.51 | 10 | 53 | 63 | abbas2021, ahmed2019, alonge2021, amonookuofi1985, cizmic2023, eisenstein1977, griffith2016, italianmri, masharawi2021, yadav2020 |
| sex | lamina_angle | men minus women, within-sex SDs | -0.09 (-0.39 to 0.20) | - | 1 | 5 | 10 | abbas2021 |
| sex | facet_angle_axial | men minus women, within-sex SDs | -0.22 (-0.77 to 0.34) | - | 1 | 5 | 5 | masharawi2021 |
| age | body_area | within-band SDs per decade | 0.09 (0.05 to 0.12) | - | 1 | 5 | 5 | griffith2016 |
| age | pedicle_h | within-band SDs per decade | 0.07 (0.02 to 0.13) | - | 1 | 5 | 5 | yu2015 |
| age | disc_h_mid | within-band SDs per decade | 0.06 (-0.01 to 0.14) | - | 1 | 6 | 12 | bach2019 |
| age | pedicle_w | within-band SDs per decade | 0.05 (0.01 to 0.09) | - | 2 | 9 | 13 | duman2026, yu2015 |
| age | disc_h_post | within-band SDs per decade | -0.09 (-0.17 to -0.02) | - | 1 | 6 | 12 | bach2019 |
| age | disc_h_mean | within-band SDs per decade | -0.11 (-0.19 to -0.03) | - | 1 | 6 | 24 | bach2019 |
| age | disc_h_ant | within-band SDs per decade | -0.14 (-0.22 to -0.06) | - | 1 | 6 | 12 | bach2019 |
| age | foramen_h | within-band SDs per decade | -0.19 (-0.27 to -0.11) | - | 1 | 6 | 12 | bach2019 |
| body height | pedicle_h | within-band SDs per 100 mm | 0.48 (0.39 to 0.58) | - | 1 | 5 | 5 | yu2015 |
| body height | pedicle_w | within-band SDs per 100 mm | 0.34 (0.24 to 0.45) | - | 1 | 5 | 5 | yu2015 |
| body weight | pedicle_w | within-band SDs per 10 kg | 0.23 (0.13 to 0.33) | - | 1 | 5 | 5 | yu2015 |
| body weight | pedicle_h | within-band SDs per 10 kg | 0.16 (0.06 to 0.26) | - | 1 | 5 | 5 | yu2015 |

| covariate | paper held out | measures | strata | AUC held out | AUC own split | R^2 held out | R^2 own split | log loss held out | log loss own split |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| age | duman2026 | pedicle_w | 8 | 0.53 | 0.53 | 0.00 | 0.00 | - | - |
| age | yu2015 | pedicle_w | 5 | 0.57 | 0.57 | 0.01 | 0.01 | - | - |
| sex | abbas2021 | body_d_mid, body_w_mid, canal_ap, canal_area | 20 | 0.68 | 0.68 | 0.11 | 0.13 | 0.633 | 0.598 |
| sex | ahmed2019 | canal_ap, canal_w | 10 | 0.56 | 0.59 | 0.01 | 0.02 | 0.689 | 0.675 |
| sex | alonge2021 | canal_ap, canal_w | 10 | 0.59 | 0.59 | 0.02 | 0.03 | 0.681 | 0.661 |
| sex | amonookuofi1982 | interpedicular | 5 | 0.60 | 0.60 | 0.03 | 0.03 | 0.679 | 0.676 |
| sex | amonookuofi1985 | canal_ap, foramen_w | 10 | 0.43 | 0.68 | -0.02 | 0.10 | 0.702 | 0.632 |
| sex | arockiaraj2025 | pedicle_chord, pedicle_h, pedicle_incl_sag, pedicle_length, pedicle_w | 25 | 0.64 | 0.64 | 0.06 | 0.06 | 0.660 | 0.656 |
| sex | bach2019 | disc_h_ant, disc_h_mean, disc_h_mid, disc_h_post, foramen_h | 36 | 0.65 | 0.65 | 0.05 | 0.07 | 0.669 | 0.650 |
| sex | chaudhary2015 | interpedicular | 5 | 0.67 | 0.67 | 0.05 | 0.09 | 0.670 | 0.617 |
| sex | cizmic2023 | canal_ap, canal_w | 10 | 0.57 | 0.59 | 0.01 | 0.02 | 0.689 | 0.681 |
| sex | duman2026 | pedicle_h, pedicle_incl_sag, pedicle_w | 12 | 0.54 | 0.54 | -0.01 | 0.01 | 0.697 | 0.685 |
| sex | griffith2016 | canal_ap, canal_area, canal_w | 15 | 0.54 | 0.59 | 0.00 | 0.02 | 0.691 | 0.676 |
| sex | hou1993 | pedicle_chord, pedicle_h, pedicle_w | 27 | 0.62 | 0.62 | 0.03 | 0.05 | 0.685 | 0.654 |
| sex | italianmri | body_d_mid, canal_ap | 12 | 0.69 | 0.74 | 0.14 | 0.19 | 0.615 | 0.579 |
| sex | masharawi2021 | canal_ap, canal_w, foramen_h, pedicle_h, pedicle_length, pedicle_w | 30 | 0.55 | 0.55 | -0.01 | 0.01 | 0.698 | 0.672 |
| sex | olsewski1990 | pedicle_chord, pedicle_h, pedicle_incl_sag, pedicle_w | 36 | 0.73 | 0.73 | 0.15 | 0.16 | 0.614 | 0.593 |
| sex | shin2024 | disc_h_ant, disc_h_mid, disc_h_post | 15 | 0.60 | 0.60 | 0.02 | 0.03 | 0.684 | 0.675 |
| sex | tang2016 | endplate, endplate_depth, endplate_lower, endplate_lower_depth | 12 | 0.82 | 0.82 | 0.22 | 0.29 | 0.576 | 0.523 |
| sex | twomey1985 | disc_h_mean | 10 | 0.86 | 0.86 | 0.24 | 0.37 | 0.565 | 0.455 |
| sex | yadav2020 | canal_ap, disc_h_mean, endplate, endplate_depth, endplate_lower, endplate_lower_depth, foramen_w | 47 | 0.64 | 0.64 | 0.00 | 0.06 | 0.705 | 0.654 |
| sex | yu2015 | pedicle_h, pedicle_w | 10 | 0.78 | 0.78 | 0.19 | 0.23 | 0.593 | 0.559 |

| what the reread gives | value |
| --- | ---: |
| sex: strata printed for both sexes, 419 with each sex's SD and 65 by means alone (papers) | 484 (abbas2021, ahmed2019, alonge2021, amonookuofi1982, amonookuofi1985, arockiaraj2025, bach2019, chaudhary2015, chen2011, cizmic2023, duman2026, eisenstein1977, griffith2016, hou1993, italianmri, masharawi2021, olsewski1990, shin2024, tang2016, twomey1985, yadav2020, yu2015) |
| age: series over two or more adult bands (papers) | 95 (bach2019, duman2026, griffith2016, yu2015) |
| body height and body weight: series over bands (papers) | 10 and 10 (yu2015) |
| strata and series scored held out | 370 |
| log loss of the base rate (equal men and women) | 0.693 |
<!-- end covariates -->

The first table is every effect pooled across the papers that print it, with how many papers, cells
and printed strata stand behind it; the second each paper held out where another paper prints the same
measure, the median over its strata; the third what the reread gives to read from.

The effects are real and most of them are of the body's size. Sex: men exceed women by 1.2 to 1.6
within-sex SDs on the vertebral body (its sagittal diameter 1.33 over Abbas 2021, Amonoo-Kuofi 1985,
Eisenstein 1977 and the Italian MRI series; Griffith 2016's area 1.42; Chen 2011's end-plate mean 1.35,
its 830 end-plates read as its 83 people; Duman 2026's heights 1.21 to 1.31) and on Tang 2016's end
plates (1.31 to 1.56); by 0.55 to 0.85 on the pedicle (height, width and chord, three to six papers
each); by 0.45 on the canal's width, which six papers print and agree on (0.32 to 0.58 for one more
paper), and by nothing on its depth (-0.03 over ten papers); by 0.25 to 0.78 on the disc's heights. A
measure whose definition differs from Panjabi's is left out as the tables leave it out, so Olsewski
1990's transverse inclination, Abbas's canal width and Amonoo-Kuofi 1982's pedicle area give no
contrast. Age, per decade of adult life: Bach 2019's foramen loses 0.19 SD and his disc heights 0.09 to
0.14 (the middle height gains 0.06), Griffith's body area gains 0.09 and the pedicle 0.05 to 0.07 in Yu
2015 and Duman. Body size, Yu alone: the pedicle's height gains 0.48 SD and its width 0.34 per 100 mm of
body height, and 0.16 and 0.23 per 10 kg.

Shape to sex, held out by paper (each paper's effect taken from the others only, its sexes-pooled mean
and SD known): over 20 papers' 357 strata the median AUC is 0.63 against the population's own split's
0.64, the median R^2 0.03 against 0.06, and the log loss 0.680 against 0.654 own and 0.693 for the base
rate (equal men and women); the sign transfers in 85% of strata. Where the effect is large the transfer
is good: Tang's end plate 0.82, Twomey 1985's disc height 0.86, Yu's pedicle 0.78; where a paper's own
contrast is far from the others' it is not (Amonoo-Kuofi 1985 0.43 against its own 0.68). Age held out
explains 0.00 to 0.01 of the pedicle's width, as in the paper itself.

What this note takes from it: sex is the covariate that matters, about one within-sex SD on the body's
size and half that on the posterior elements, age matters little within adults, and held out the
direction of an effect travels between populations while its size travels only partly, the same lesson
as the means' shift above. One measure is the honest unit here: a person's measures share their size
and no paper prints the correlation within a person, so the evidence of two measures cannot be added.
The combination across measures and a held-out test with people as the unit wait for measured spines
with each person's sex and age: the gold tier 3 CTs that bordercall's morphometry measures on the grid,
joined with ENHANCE.PET's DICOM headers, VerSe's demographics table and TotalSegmentator's meta.csv by
SchwingNet's gate word morphometry covariates (SchwingNet pull request 497), one CPU job on the owner's
count of 2026-10-30 08:55 UTC, aggregates alone leaving the grid.

## Naming told the person's sex

The owner's words of 2026-10-30, 03:45 UTC: "i think its total reasonable to expect to know the sex of
the patient you are imaging". So sex is an input the rule is given, never a thing it predicts, and the
question is what it is worth to naming a field of one, two or three bodies at an unknown offset
(synthval/sex_naming.py, run_sex_naming.py, records/sex_naming). This reading is exploratory: it was
not pre-registered, and its rules are chosen here, not by the held-out selection that chose the
temperature. Every rule names the same simulated persons on the same fields, so each difference is
paired, its SE over persons.

Two readings. Synthetic: the selection's lumbar table split into two sexes by a known shift (d within-sex
SDs, the same at every cell or following the level profile the papers print), or by the papers' own
pooled contrasts per measure or per cell; persons half men and half women; rule A reads the sexless
table and rule B the table of the person's sex, both the generator's exact rule, so B minus A is what
the information is worth and nothing else. Held out: each paper that prints a stratum's men and women
apart is held out in turn, persons drawn from its own two tables; rule A is the others' plain table at
the held-out paper's own temperature, chosen on the others alone as select.py chooses it, and rule B
that table moved by the others' sex contrast, at the same temperature, so the two differ only in the
sex. Beside them, as ceilings and never rules: A moved by the paper's own contrast, the paper's own
sexless table, and its own two sexes' tables. Of the 18 papers scored, Amonoo-Kuofi 1985 and Eisenstein
1977 print means alone and their persons' spread is the rule's own, so the headline pools the other 16.

| held out, 16 papers, told the sex minus not | 1 body | 2 bodies | 3 bodies |
| --- | ---: | ---: | ---: |
| the others' contrast: log score, nats (SE) | 0.001 (0.006) | -0.003 (0.009) | -0.003 (0.008) |
| the others' contrast: named right, points | 0.1 | 0.2 | 0.1 |
| ceiling, the paper's own contrast: nats | 0.007 | 0.009 | 0.011 |
| ceiling, its own tables by sex over its own sexless: points | 1.0 | 1.6 | 1.7 |
| for scale, its own sexless table over the others': points | 5.9 | 8.4 | 8.1 |

Held out, the sex buys nothing the papers can show: the others' contrast moves each paper's table by
an amount its own sexes do not quite share, and what is gained where they agree (Yu 2015, Bach 2019,
Shin 2024, 0.01 to 0.03 nats) is lost where they do not (Yadav 2020, whose printed SDs are twice the
others', loses 0.08 to 0.13). Even the paper's own two tables, which no rule meets, gain under two
points, while its own sexless table gains six to eight: the population a person comes from carries far
more than the sex. On synthetic populations split by the papers' own contrasts per cell the gain is
0.034 nats and 1.9 points at one body, 0.025 and 1.1 at two and 0.007 and 0.1 at three; a shift of 1.5
SDs at every cell, about the largest contrast the papers print (the body's 1.3, Tang's end plates up to
1.6) put on every measure at once, gives 0.053 nats and 1.9 points at one body. Sex is worth carrying in a rule as a given input, at little cost and no harm in
expectation where the contrast is the population's own; it does not close the gap to the population's
own table, which only target-population data or the population register's strata can.

## Bounds for a generator

The owner's words of 2026-10-30, 03:38 UTC: "could these at least serve as bounds for gnerateive models
making synthetic spines from idea spines?" They can, on what the papers print, and the card is
synthval/bounds.py, run by run_bounds.py into records/bounds (bounds.json, bounds.csv one row a cell or
step, gradients.csv, calibration.csv). Per measure, level and kind of population (living, dry bone,
cadaver, mixed, and every paper together) it gives the interval for a new population's mean, pooled
plus or minus 1.96 sqrt(SE^2 + tau^2), the interval for its SD, the sex contrast and age slope that
covariates.py reads, and the step from each level to the next read inside each paper first, so a
paper's own shift falls out of it. Naming lives on the steps, so the steps decide: check() scores a
generated cohort cell by cell and passes it only where its step pass rate reaches the bar and no other
test with a bar falls short of its own; the rate over every test decides nothing. A measure of the
cohort that the card does not hold is scored on nothing and named in the summary (measures_not_on_card)
and in the verdict's why, whatever the verdict: the card keys the pedicle's width as pedicle, after the reread, so a cohort
keyed pedicle_w:mean would otherwise be scored with no pedicle test and say nothing (the auto-anatomist
thread's catch of 2026-10-30). Of schwingcheck's generator's measures, 22 are not on the card, each one
no paper prints (the facets' areas, heights and angles, the inferior facet's width, the interfacet
distances, the uncovertebral and costovertebral joints, the pars), not a name apart (bounds.json's
checks).

The bar is real populations held out: each of 33 papers left out in turn and scored on the card of the
rest as a cohort is scored, the bar the 10th percentile of their own pass rates over the papers with
20 rows or more of a test (mean 0.58 over 12 papers, SD 0.53 over 10, steps 0.89 over 7). Those papers
measured about 40 people each (median 44), and a cohort of thousands judged at its own size would meet
intervals they never met, so every cell is scored as if the cohort had REFERENCE_N = 40 people, its own
sampling error replaced by theirs, and a cell with fewer than 40 is not scored and is counted
(short_cells). The price is power: a flattened gradient fails fewer steps at 40 people than at its own
thousand (tests/test_bounds.py states both).

| cohort, scored at 40 people | means | SDs | steps | verdict |
| --- | ---: | ---: | ---: | --- |
| the card's centre, the ideal spine, 1,000 people | 1.00 | 1.00 | 0.99 | passes |
| 200 populations of the card's own model, 300 people each | 0.95 | 0.96 | 0.91 | 175 pass |
| the centre, its lumbar gradient flattened | 0.99 | 1.00 | 0.87 | fails on the steps |
| the centre, its lumbar levels reversed | 0.95 | 0.97 | 0.79 | fails on the steps |
| schwingcheck's generator on Panjabi's table, 2,000 people | 0.70 | 0.57 | 0.86 | fails on the steps |
| the point nearest the papers, 2,000 people | 0.70 | 0.84 | 0.80 | fails on the steps |

The 25 of the card's own populations that fail do so on steps no population can honour: at 188 of the
635 steps the two levels' intervals differ in spread by more than the step's interval allows, and those
steps pass 0.80 against 0.96 for the rest (bounds.json's checks.drawn). A flattened lumbar gradient
keeps an overall rate of 0.95, which is why the steps and not the overall rate decide. A generator can
use the card three ways: as the acceptance test above, as a loss term (the mean square of the cells'
z-scores, about 1 for a cohort the card's model draws and 3.4 for schwingcheck's generator), and with
each person's sex given, as a check that men and women differ in the papers' direction where the
interval for a new population's contrast clears zero. What it cannot bound, and says so: one person's
correlation across measures or levels (no paper prints it), the anomalies (an L6 or a T13 goes
unscored, and a lumbar rib's L1 is held to the ordinary L1), and a population no paper sampled.

## Real CTs on the card

The gold tier 3 join (SchwingNet's gate word `morphometry covariates`, job 40878978 of 2026-10-30)
printed, for two cohorts the morphometry engine measured, each sex's count, mean and SD at every
measure and level from T10 to L5, Hedges' g, the correlation with the level above within each sex and
the age slope (records/gold3/report.txt, aggregates alone; the per-person tables stay on the grid).
synthval/gold3.py scores them on the card from those moments as check() scores a generator: the sexes
pooled for the means and SDs, each step's sampling variance from the two levels' pooled SDs and the
covariance that the within-sex correlations and the sexes' shift give, every cell at 40 people
(run_gold3.py, records/gold3). They are real people measured by the engine, so they are what a
generator measured by the same engine should look like. VerSe's 21 persons are not scored, since the
join read no sex for them, nor ENHANCE.PET's Leipzig and Careggi, whose releases carry none.

What the report holds and the score leaves out is named in each member's not_scored (gold3.json), never
passed over: the card's interpedicular distance, pooled from films alone that no paper corrected for
magnification (Hinck 1966, Amonoo-Kuofi 1982, Chaudhary 2015), its cells and the steps read inside
those papers, and its MRI cell of the lower end-plate's area at L3, the cohorts being CT at true size;
spinous_length, which on the card is Tan 2004's SPL, Panjabi's, from the upper end-plate's centre to
the tip, where the engine's runs from the canal's posterior wall (paper-tables/validation/
mapping_audit.csv); h_post_inset, wedge and lamina_thickness, which no paper of the card prints; and
the cells whose one sex's mean the report withholds (its disc_h_mean is shown only where its persons
are each of its three heights'), four of autoPET's disc_h_mean cells and so all its disc_h_mean steps,
and TotalSegmentator's disc_h_mean at T11-T12 and three of its pedicle's sagittal angles.

| family of measures, scored at 40 people | autoPET means | SDs | steps | TotalSegmentator means | SDs | steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| body and end plate | 0.60 | 0.78 | 0.94 | 0.69 | 0.74 | 0.99 |
| disc and foramen | 0.81 | 0.85 | 0.74 | 0.87 | 0.77 | 0.65 |
| pedicle and canal | 0.58 | 0.60 | 0.64 | 0.65 | 0.65 | 0.70 |
| posterior elements (transverse width) | 0.12 | - | 0.71 | 0.12 | - | 0.86 |
| every family | 0.60 | 0.72 | 0.79 | 0.68 | 0.72 | 0.83 |
| the bar, real papers held out | 0.58 | 0.53 | 0.89 | 0.58 | 0.53 | 0.89 |

Both cohorts fail on the steps, at 123 of 156 and 128 of 155, and pass the means and SDs, autoPET's
means with three cells to spare (113 of 187 against the bar's 0.584). The body and end-plate steps pass above the
bar; the discs', the pedicles' and the canal's fall below it. Only the pedicles' failures have a known
cause in the engine.

The pedicle and canal measures leave the papers' at both ends of the range, not below L2 alone: their
means fail at 19 of 27 cells at T10 to T12, 2 of 18 at L1 and L2 and 9 of 26 at L3 to L5 for autoPET
(17 of 25, 0 of 16 and 6 of 24 for TotalSegmentator), and their steps most from L3 down. The engine's
pedicle runs about 2 mm wider than the papers' at T10 to T12 and breaks away from L3, reaching 27 mm at
L5 against 15 (figure fig20_gold3, C); its height runs 3 to 7 mm above the papers' at every level,
failing at T10 to T12 and passing below only inside the card's wide lumbar intervals; its sagittal
angle reads 32 to 42 degrees at T10 to T12 against 7 to 9, and its transverse angle turns to -5 at
T12 against +8 and to -17 at L5 against +23 (-13 for TotalSegmentator); its chord falls to 27 mm at L5
against 44 and is read at L4 and L5 for only 262 and 251 men of the 478 whose bodies autoPET measured
at T10, the angle for 262 and 271; and the thoracic canal is about 4 mm wider. These are the engine's known pedicle
defects: the join ran the engine pinned before bordercall PR 44's rework, which reads the pedicle from
the canal, takes its width at the isthmus, flags an L5 whose transverse process's root is fused to the
pedicle and says the transverse angle is not to be trusted on real masks.

The disc steps that fail are T10-T11 to T11-T12 and L3-L4 to L4-L5: the engine's L4-L5 disc is lower
than its L3-L4 disc (mid height -1.56 and -1.41 mm against the papers' +0.44), and its L4-L5 foramen
falls further below the L3-L4's than the papers' does. Nothing here tells the engine from the people for the discs. The L4-L5 disc is where these
people's discs narrow fastest with age (mid height -0.64 mm a decade in autoPET's men and -0.41 in its
women, against -0.27 and -0.33 at L3-L4), as an older cohort's degenerating discs would; scoring the
steps within age bands would test it, and needs the per-person table on the grid.

The body passes most of its means and SDs (its SDs fail at one cell and three), its middle height's
means alone below (2 and 4 of 8 levels, up to 4.6 mm above the papers'). The end plates pass their steps, but their widths do not
pass their means: the upper and lower end-plate widths pass at 2 of 8 levels each (2 and 4 for
TotalSegmentator), 6 to 11 mm above the papers', and their SDs at 1 of 6, while the depths pass at 6 of
8, 3 to 8 mm above inside the card's wider intervals (cells.csv). A definition apart (the mask's outer
rim against a caliper's) would explain it, and this note does not test it. The transverse width, which
the card holds from Tan 2004's ten cadavers alone, reads 9 to 23 mm wider and fails 7 of 8 means.

The sex contrasts keep the papers' sign: 61 of 63 and 66 of 67 cells where the card's interval for a
new population's contrast clears zero. Their size is under-covered: g lies inside that interval at 93
of 118 cells for autoPET and 99 of 122 for TotalSegmentator (79 and 81 percent of a nominal 95), and
inside it widened by each g's own error at 98 and 111; the cohorts' contrasts run a little smaller
(mean z -0.21 and -0.69, root mean square 1.35 and 1.21), so the card's intervals are a little narrow.
The front body height shows it most (autoPET's h_ant g 0.38 against Duman 2026's 1.21); the end
plates, whose SDs run about three times the papers', show the reverse (autoPET's endplate g 1.30
against 0.90), so a noisier measure does not explain it. The age slopes, which the card makes no test on, lie inside the card's interval at
13 of 33 and 16 of 37 cells (18 and 29 widened by their own error): the card's spread between
populations for them is the zero its two donor papers give, and these cohorts say it is wider.

So for a generator: the card can judge the body and end-plate steps, most of the body's means and the
sex contrasts' sign of a cohort the engine measures today; a pedicle step it fails says as much about the
engine as about the generator until the engine with PR 44's pedicles is pinned and the join run again,
which is grid work on greg's word and count; a disc step it fails at L4-L5 may be the people's age as
much as either; and the gold cohorts themselves, measured by the same engine, are a second bound beside
the papers' that shares the engine's definitions.

## Figures and renders

figures/FIGURES.md lists each with its caption, its CSV, the sha256 of every file and the abbreviations
on the axes. Line graphs are in the house format (schwingcheck/figures.py, the build-up study's, which
synthval/house.py takes and adds to); the renders draw synthetic vertebrae in Benzel's manner, each
section a superellipse holding its measured width, depth and area, and dashed where no superellipse of
those extents holds the area (the box indicator, drawn). An end-plate area at or past its box is lofted
in the solid at render.BOX_SHARE of it, since no loft holds more. Panjabi's spinous length is drawn from
the centre of the upper end-plate, as his paper measures it (render.py's docstring); schwingcheck's
mnemonics.py starts it at the canal's posterior wall.

- fig1_means, fig2_spread, fig3_structure: the validation.
- fig4_state_space, fig5_naming: the state space and naming across it.
- fig6_power: the spread between series, part C rerun, what gold persons can test.
- fig7_quality: the quality indicators by measure and level.
- fig8_assumptions: the errors and prevalences the generator assumes, beside the papers'.
- fig_tan_strata: Tan 2004 as a stratum of his own: the prediction intervals, the rule on each stratum's
  tables, the coverage of each interval against its width.
- fig_subgroups: the populations by every variable of the register: the share each accounts for, each
  paper and each value against the rest, the contrasts a paper prints apart.
- fig9_tables, fig10_relations, fig11_state_space_all, fig12_naming_measures, fig13_spread_all: the second
  part, every measure of the reread (figures_all.py, drawn by figures.py with the rest).
- fig14_strata: every paper its own population, the rule built on the others scored on each, the pooled
  loss with its interval for one more population, the promise at 0.99 and the populations drawn from the
  random-effects model (figures_all.py, from records/strata).
- fig15_select: choosing the rule by held-out prediction, each candidate's held-out log loss and accuracy,
  the calibration curves, the SD factor and the temperature swept with the inner choices, and the winner
  against the plain rule population by population (figures_all.py, from records/select).
- fig16_exclusion: leaving a paper out, scored held out: each exclusion candidate against the plain rule,
  paired over the populations, population by population at three bodies, and calibration
  (figures_all.py, from records/select).
- fig17_covariates: covariates both ways from what the papers print apart: the sex, age and body-size
  effects pooled within papers first, how well one measure tells men from women, and how much of a
  measure sex or age explains, in the population and held out (figures_all.py, from records/covariates).
- fig18_sex_naming: naming a short field told the person's sex, on synthetic populations whose sexes
  differ by a known shift and held out by paper on the papers' own men and women (figures_all.py, from
  records/sex_naming).
- fig19_bounds: the bounds card, one measure's interval for a new population's mean down the column with
  a flattened and a reversed lumbar gradient, and each cohort's pass rate by test beside the step bar
  (figures_all.py, from records/bounds).
- fig20_gold3: gold tier 3's two real cohorts on the card, each test's pass rate by family of measures
  against the papers' bar, the sex contrast and the age slope by measure against the card's interval for
  a new population (the counts in B and D are inside that interval as drawn), and the engine's pedicle
  width down the column beside the card's (figures_all.py, from records/gold3 and records/bounds).
- render1_axial, render2_column, render3_solid: L3 from above, the lumbar column from in front, and the
  column as solids, Panjabi's means beside synthetic people.

## Run it

From this folder, with the Python that holds bordercall's pinned packages (requirements-schwingcheck.txt):

```
python3 -I run.py --out records                    # every record, about ten minutes on 4 CPUs
python3 -I run_all.py --out records/all            # the second part, about half an hour; --quick smoke-tests it
python3 -I run_strata.py --out records/strata      # every paper its own population, about two minutes; --quick too
python3 -I run_select.py --out records/select      # choosing the rule by held-out prediction, about ten minutes; --quick too
python3 -I figures.py --records records --out figures
python3 -I run_covariates.py --out records/covariates   # covariates both ways, seconds
python3 -I run_bounds.py --out records/bounds           # the bounds card, about four minutes
python3 -I run_sex_naming.py --out records/sex_naming   # naming told the sex, about half an hour; --quick too
python3 -I run_gold3.py --out records/gold3             # gold tier 3's cohorts on the card, a second
python3 -I tan_strata.py --out records/tan-strata --quick       # Tan's population apart, the record in place; --tables 8 is the full run, about 25 minutes
python3 -I subgroups_run.py --out records/subgroups              # the populations apart, a few seconds
python3 -I tables.py --records records --write README.md --write MEASURES.md
python3 -I tables.py --records records --check README.md --check MEASURES.md   # exit 1 when a table differs
cd ../.. && python3 -m unittest discover -s research_notes/synthetic-validation/tests
```

records/RECORD.json gives the command, the seeds, the sizes, bordercall's commit, the snapshot's commit
and digest, and the sha256 of every Python file of this note, run.py, tables.py, figures.py, render.py,
snapshot.py, synthval/ and the tests, read before the run starts. The run is deterministic: two runs give
the same bytes in every record but RECORD.json's seconds. records/all/RECORD_ALL.json records the second
part's run the same way, with the whole snapshot's digests from data/SOURCE_ALL.json. The grid search
of the second part also runs as a Slurm array on the grid, one task a point, with a merge that writes the
same records (grid/README.md). records/strata/strata.json records the strata reading the same way, with
its own seeds and sizes; it reads the first part's records/power.json for the split's share and runs in
about two minutes, so it is not sent to the grid. records/select/select.json records the selection the same
way, with its grids, its seeds and each paper's inner choice; it runs in about ten minutes. As committed on 2026-10-29 the records are a container's, and the code
digests in RECORD.json and RECORD_ALL.json predate the last changes to run.py, run_all.py and
synthval/all_measures.py (the array's --point and merge, no number changed); the owner's word of 23:03 UTC
sends the final rerun to the grid, which rewrites both records.

## Files

- run.py writes records/, run_all.py records/all/, run_strata.py records/strata/, run_select.py
  records/select/, run_covariates.py records/covariates/, run_bounds.py records/bounds/, run_sex_naming.py
  records/sex_naming/, run_gold3.py records/gold3/ (from the grid's report there); tan_strata.py writes records/tan-strata/ (Tan's
  population apart); subgroups_run.py writes records/subgroups/ (the populations apart); figures.py,
  figures_all.py and render.py draw figures/; tables.py writes the tables above and MEASURES.md;
  snapshot.py cuts and checks data/.
- synthval/: literature.py (the selection), pooling.py, population.py, validate.py, structure.py, qi.py,
  sweep.py, naming.py, power.py, references.py (the papers' errors and prevalences), tan.py (Tan 2004 as a
  stratum of his own, and the prediction by stratum), register.py and subgroups.py (the population
  register and the subgroup meta-analysis by any variable), house.py; for the second part
  papers_table.py (the vocabulary, the variants, the three tables), relations.py and all_measures.py;
  strata.py, every paper its own population and the rule predicted for one more; select.py, the rule
  chosen by held-out prediction, a paper's exclusion among its candidates; covariates.py, sex, age and
  body size read both ways from what the papers print apart; bounds.py, the card a generator's cohort is
  scored on; sex_naming.py, naming told the person's sex; gold3.py, gold tier 3's cohorts on the card.
- data/: the snapshot of the reread's series and SOURCE.json; populations.csv, the register of the
  cohorts; series_all.csv, vocabulary.csv and SOURCE_ALL.json, the whole reread for the second part.
- MEASURES.md: every key of the vocabulary with what became of it, written from records/all.
- tests/test_synthval.py: the code against what its docstrings say; tests/test_subgroups.py: the register
  and the subgroups; tests/test_all_measures.py: the second part's; tests/test_strata.py: the strata's;
  tests/test_select.py: the selection's; tests/test_covariates.py: the covariates'; tests/test_bounds.py:
  the card's; tests/test_sex_naming.py: naming told the sex; tests/test_gold3.py: gold tier 3 on the card.
- report/: build.py writes the stats page and build_ml.py the page for a machine-learning reader, each
  from its notes file (notes.json, ml_notes.json), both ignored outputs rebuilt by one command.

## What this note does not do

- The sex-naming reading is exploratory and not pre-registered: its comparisons were set here, after the
  covariates were read, and its synthetic split is a model of the papers' contrasts, not people. The held
  out reading draws persons from each paper's printed tables, so it tests what the papers print, not
  their people; the gold tier 3 join (SchwingNet's job 40878978) is the first data with each person's
  sex beside their measures.
- The gold tier 3 cohorts are read as the moments the grid printed, not as persons: a step's pairing
  comes from the within-sex correlations with the level above, and the engine's measures are matched to
  the papers' by name and definition; whether the disc steps fail for the engine or for the people's
  age, and whether the end-plate widths are a definition apart, is not examined here, and the pedicles'
  failures wait for the join run again on the engine with PR 44's pedicles.
- The bounds card bounds what papers of about 40 people can show: a cohort is scored as if it had 40,
  so a break smaller than such a paper's sampling error passes, and the card cannot bound one person's
  correlation across levels, the anomalies or a population no paper sampled.
- It does not change the generator. The nearest point is the nearest of a grid, not a fitted model; it
  sits on two of the grid's edges, and it is held to the correlations of Griffith's two sexes by a
  population with no sex. A change to schwingcheck's defaults is the owner's to choose, and would move
  every result the build-up study recorded.
- It reads 39 papers' tables, not their people: a pooled mean is of populations, and the gold persons are
  the first data that can test the correlation between a person's levels (Griffith's give only four
  correlations between measures).
- It does not say why Panjabi's depths exceed the papers'; a definition the mapping did not catch would
  read the same as a population.
- The sex table rests on three papers, the prevalences on two, and the error part is read at 448006f;
  a later snapshot of the reread is cut and the note run again.
- The second part reads the reread at main 6409164, before pull request 39 fixes its counts of people
  and its duplicated rows; a table drawn from its own means and SDs can be read for self-consistency
  and for what the relations between measures allow, never for a match to the papers, which the first
  part made.
- The strata reading is a quick lumbar run, 1,000 columns a population on 4 CPUs, not the grid search,
  which stays as it is until the owner sends it (his word of 2026-10-29: no large rerun while the
  populations move); 613 of its 694 cells borrow a tau, and a paper's population is its printed means
  with the pool's SD where its own is uncertain, so it reads what the papers print, not their people;
  Yadav 2020's printed SDs, 2.1 times the others' pooled SD, are read as printed and not questioned here.
  It splits by paper; the population register the owner asked for on 2026-10-29 (by author, with sex,
  ancestry and the like for subgroup analysis) is on pull request 43's branch and not merged, so no
  subgroup is read here; once it lands it gives strata_of another grouping.
- The selection of the rule reads the same synthetic populations, so it chooses among rules for naming
  people drawn from printed means and SDs, not real patients, and only on the lumbar run at 1,000
  columns a population; five candidates were tried, and the two that could be stacked, the widening or
  the mixture with the tempering, were not. The temperature it chooses is not put into schwingcheck's
  rule here.
