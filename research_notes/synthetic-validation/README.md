# The synthetic spines against the published populations

Thread "Validate synthetic data against population means", 2026-10-29, project symphony_4, for greg's ask
of 2026-10-29 02:12 UTC: "Do a State space exploration of the synthetic data, Curation, QI, rerun power
calculations, visualization, rendering, and validation of all the synthetic data compared to the known
population means of these measurements". The synthetic data are the spines schwingcheck's generator draws
(schwingcheck/columns.py on Panjabi's tables, schwingcheck/measures.py). The known populations are the 39
papers of the clinical reread (bordercall draft pull request 26, branch claude/project-thread-adplcz),
cut at its commit 45130ac, at which the reread's second readers had checked the series this note pools.
Everything here is synthetic but the papers' own numbers: no grid, no WSU data, no scan.

Confidential: this note is bordercall's and stays in this private repository, as the owner's rule says of
bordercall's and SchwingNet's research notes. A synthetic result raises no evidence tier.

**The snapshot will move.** After 45130ac the reread's code review found faults in some rows: Lien 2007's,
Tan 2004's (two of its pedicle angles change sign), Moncada-Habib 2025's, Ahmed 2019's, Cizmic 2023's and
Yu 2015's rows, Bonczar's sagittal angle (right side only), Robertson's L3 left SD (a misprint), reprinted
tables counted twice, and Masharawi's crosswise cohort labels. Its corrected series.csv was not pushed when
this note was run. Every number below is read from records that one command rewrites (Run it); the next
snapshot is cut with `python3 -I snapshot.py --write <commit>` and the note run again. The error draft this
note also reads (synthesis/error.md at 45130ac) had no second reader at that commit.

## The answer

1. **The means are Panjabi's, and Panjabi's twelve spines are larger than the papers' populations.** In
   the 56 cells (measure and level) where three or more bone or CT series pool, Panjabi's mean lies
   outside the 95% confidence interval of the pooled published mean in 25, 23 of them above it (17 of 32
   without Tan 2004, 13 above). It lies outside the 95% prediction interval, where a new population's mean
   should fall, in only 1, and in none of the 27 cells with five series or more, but with three series
   that interval takes t on one degree of freedom and is too wide to test much (table means). Over all
   374 cells his mean sits a median 0.91 of his own SD from the papers', and 0.91 again over the 134 that
   do not rest on Tan alone; canal depth, transverse span and both end-plate depths sit 1.4 to 1.8 SD
   above, the posterior body height 0.75 below (table by_measure, figure fig1_means).
2. **The synthetic spread is too wide, by about two thirds.** In the 134 cells with a published SD, each
   synthetic SD is a median 1.69 times the papers' (1.81 with the generator's error of one reading, which
   is larger than a caliper's or a CT's). Most of it is Panjabi's own: his SDs are 1.47 times the papers',
   and the generator draws a size of its own on top of them (table means, figure fig2_spread). Taking the
   size out of his SDs brings it to 1.47; the nearest point of the state space (below) to 1.04, and 1.30
   with the error.
3. **The generator ties the canal to the body more than people do, and its depth to its width less.**
   Griffith's 1,080 CTs give the canal a correlation of 0.20 to 0.44 with the body's area; the generator
   gives 0.56 to 0.59, since one size scales every length alike, but 0.50 for the canal's depth with its
   width, against Griffith's 0.55 and 0.61. The papers that print both sexes put the canal's and the
   pedicle's width at about a third of the body's sex difference, and the canal's depth at none (table
   structure, figure fig3_structure).
4. **About four synthetic vertebrae in ten could not exist.** 42% of vertebrae, and every person, carry
   at least one geometric impossibility: mostly an area larger than the rectangle of its own width and
   depth (32%), then an end-plate under half of it (10.5%). Curation for the two that no definition
   allows (a length or area at or below zero, a canal wider than its own transverse processes) drops 38%
   of people. The seven measures the rule reads are flagged in 13 of 10,000 people, by a canal depth at or
   below zero or at the floor (table quality, figure fig7_quality).
5. **The point nearest the papers is narrower, and it names better.** Searched over 180 points, the
   nearest takes the size's spread from 0.07 to 0.02 and every SD to 0.7 of Panjabi's. There the
   impossible vertebrae fall from 42% to 11%, and the exact rule names one body in 57% of fields against
   47.5% at the generator, three in 80% against 73%, nine in 98% against 96% (tables grid and naming,
   figures fig4_state_space and fig5_naming). The papers pin the size's spread and the SDs' scale; they
   leave the two correlations rho and r_between open.
6. **The papers disagree with one another more than twice as much as part B measured.** The spread
   between published series is a median 0.83 of Panjabi's SD over 56 cells, 0.92 once corrected for
   REML's low reading at three to seven series, against the 0.39 that research_notes/cadaver-power part B
   took from his comparison tables. An infinite pool of published series is then worth a median of about
   1.8 CT scans of the population named (1.3 at the corrected spread), below the 2 to 16 part A gave at the
   old spreads. A rule built on a table moved that much loses 10 to 19 points of exact naming, 10 to 14 on
   Panjabi's own definitions alone (tables spread and part_c, figure fig6_power).
7. **What the 159 gold persons can test.** At 159 whole spines a two-sided test at 5% has 80% power for a
   shift of a level's mean of 0.22 of a person's SD (0.36 for one cell of the seven SPINEPS measures' 154,
   with a Bonferroni split), an SD ratio of 1.17, and gives a neighbouring-level correlation to within
   0.12. The papers' prevalences lead one to expect about 4 people with six lumbar-type segments among
   them; the generator's equal sixths are 4 to 9 times what the papers count, 6.7 times for six
   lumbar-type segments (tables gold and assumptions, figures fig6_power and fig8_assumptions).

## What was compared

**The generator.** schwingcheck draws each value as s^p (mu + sd (rho z + sqrt(1 - rho^2) e)) + error n:
Panjabi's mean and SD at that level, a person's size s (log-normal, scale_sd 0.07) to the measure's power
p, a person's offset z shared by every level of a measure (rho 0.5), the level's own part e, and the CT's
error of one reading (1 mm for a length, sqrt(pi A / 2) for an area, 3 degrees for an angle), measured
values held at a floor of 0.5. synthval/population.py draws the same model vectorised and keeps the true
anatomy, the measured value and the size apart, and tests/test_synthval.py holds its moments to
columns.draw_columns within five standard errors at every measure and level.

**The papers.** data/literature_series.csv is the part of the reread's series.csv this note can use, cut
at 45130ac with its sha256 in data/SOURCE.json; `python3 -I snapshot.py --write 45130ac` cuts it again to
the same bytes, and `--check` says whether it still matches. synthval/literature.py turns rows into
series by eight rules written in its docstring, each counted in records/selection.json; among them the
paper's own values, adult unselected humans (the cohort read as well as the group, since Masharawi's
Table 5 labels its two cohorts' rows crosswise), one of the pool's measures under Panjabi's definition or
one close to it, one technique and one group per cohort, the sexes pooled where printed apart, and, new
here, no length or area under half or over twice the mean of its series' printed neighbours, where both
are next to it in a column. 23 of the 39 papers give a series with a mean, an SD and a count. That last
rule was written for Tan's lower end-plate area at L3, printed as 172 mm2: the reread confirmed it a
misprint on the page and dropped the row, so at 45130ac the rule catches nothing and stays as a guard.
The two end-plate inclinations are left out whole, since the reread found one set of numbers printed for
both C3 to C7 and L1 to L5 (research_notes/panjabi-endplate-inclination.md on its branch, checked by three
second readers).

<!-- table selection -->
| what | count |
| --- | ---: |
| rows of the 32 measures in the snapshot | 2490 |
| series formed | 935 |
| series with a mean, an SD and a count of two or more | 764 |
|   of them bone | 478 |
|   of them CT | 203 |
|   of them film | 59 |
|   of them MRI | 24 |
|   of them with the cohort's count of people | 48 |
|   of them with Tan's uncertain SDs (weighting the means, left out of the published SD) | 364 |
|   of them one sex only | 48 |
| papers behind the usable series | 23 |
| rows left out: quoted from another study | 796 |
| rows left out: a stratum of a cohort printed whole | 215 |
| rows left out: definition differs | 154 |
| rows left out: selected, diseased or example group | 147 |
| rows left out: a meta-analysis pooling other series | 75 |
| rows left out: end-plate inclination, one set printed for two regions | 54 |
| rows left out: another technique on the same people | 45 |
| rows left out: not human | 28 |
<!-- end selection -->

**The comparison.** Bone and CT series pool together as the main comparison, film and MRI apart, since
film magnifies and MRI reads soft tissue. Means pool by REML with the prediction interval of Higgins,
Thompson and Spiegelhalter on t(k - 2), SDs on the log scale (synthval/pooling.py). Tan's SDs, whose
conversion from standard errors the reread could not settle, weight the pooled means and set the spread
between series like any other series', but the published SD a synthetic SD is held to leaves them out:
it is pooled where two other series print one, the one series' where one does, and there is none in the
240 cells that Tan alone covers. d is the distance from the papers' mean in Panjabi's SD at that level,
the SD the generator draws with, so a shift reads as what it costs the rule.

## Means

<!-- table means -->
| Panjabi's means and SDs against the papers (bone and CT) | all series | without Tan 2004 |
| --- | ---: | ---: |
| cells (measure, level) with a bone or CT series | 374 | 134 |
|   of them on Tan 2004 alone | 240 | - |
|   with three series or more, so pooled with an interval | 56 | 32 |
|     cells by the number of series behind them | 3: 24, 4: 5, 5: 8, 7: 10, 8: 1, 9: 2, 10: 5, 11: 1 | 3: 5, 4: 7, 5: 1, 6: 8, 7: 3, 8: 2, 9: 5, 10: 1 |
|   Panjabi's mean outside the 95% prediction interval | 1 | 0 |
|     of the cells with five series or more (27; 20) | 0 | 0 |
|   Panjabi's mean outside the 95% CI of the pooled mean | 25 | 17 |
|     of them with Panjabi's mean above | 23 | 13 |
| median distance from the papers' mean, in Panjabi's SDs (all cells) | 0.91 | 0.91 |
|   share of cells more than one of his SDs away | 44% | 47% |
| cells with a published SD: pooled from two series or more / one series / none (Tan's alone) | 56 / 78 / 240 | 56 / 78 / 0 |
| Panjabi's SD over the papers' SD, quartiles (134 cells; 134) | 1.12 / 1.47 / 2.11 | 1.12 / 1.47 / 2.11 |

| synthetic population | values | cells | |d| of its mean, median (Panjabi's SDs) | |d| over 1 (%) | its SD over the papers', median (quartiles) | SD inside the papers' SD interval |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| generator | measured | 374 | 0.91 | 46 | 1.81 (1.45 to 2.69) | 25 of 32 |
| generator | true | 374 | 0.91 | 46 | 1.69 (1.36 to 2.35) | 26 of 32 |
| nearest the papers | measured | 374 | 0.91 | 44 | 1.30 (0.96 to 1.87) | 28 of 32 |
| nearest the papers | true | 374 | 0.91 | 44 | 1.04 (0.82 to 1.51) | 25 of 32 |
| size_removed | measured | 374 | 0.90 | 44 | 1.67 (1.25 to 2.33) | 26 of 32 |
| size_removed | true | 374 | 0.90 | 44 | 1.47 (1.13 to 2.11) | 26 of 32 |
<!-- end means -->

The prediction interval and the confidence interval answer different questions. The first asks whether
Panjabi's twelve spines could be one more population among the papers', and the answer is yes nearly
everywhere, partly because with three series that interval is wide. The second asks whether he sits at
their centre, and in 25 cells he does not, 23 times above. Both are true at once: his spines are a
plausible population, a large one. 240 of the 374 cells rest on Tan 2004 alone, ten Singaporean cadavers;
the second column leaves him out, and the median distance does not move. The second table is the
synthetic populations themselves: their means are Panjabi's, so they sit as far from the papers as he
does, and only their spread changes with the setting.

<!-- table by_measure -->
| measure | cells | pooled (3 series or more) | with a published SD | Panjabi - papers (his SDs) | same, absolute | Panjabi's SD over the papers' | measured SD over the papers': generator | size taken out | nearest point |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| canal_ap | 22 | 5 | 6 | 1.74 | 1.74 | 1.14 | 1.48 | 1.26 | 1.00 |
| canal_area | 22 | 5 | 5 | 0.88 | 0.88 | 0.99 | 1.25 | 1.02 | 0.77 |
| canal_w | 22 | 5 | 5 | 1.31 | 1.31 | 0.90 | 1.21 | 0.99 | 0.78 |
| endplate_area | 22 | 0 | 0 | 0.46 | 0.46 | - | - | - | - |
| endplate_depth | 22 | 0 | 6 | 1.43 | 1.43 | 1.42 | 1.77 | 1.48 | 1.10 |
| endplate_lower | 22 | 5 | 6 | 0.96 | 0.96 | 1.90 | 2.48 | 1.97 | 1.47 |
| endplate_lower_depth | 22 | 0 | 6 | 1.61 | 1.61 | 1.05 | 1.43 | 1.12 | 0.86 |
| h_post | 22 | 7 | 22 | -0.75 | 0.75 | 1.40 | 1.80 | 1.62 | 1.30 |
| pedicle_area | 22 | 0 | 5 | -0.16 | 0.22 | 0.95 | 1.16 | 0.99 | 0.73 |
| pedicle_w | 22 | 9 | 15 | 0.68 | 0.68 | 1.61 | 1.78 | 1.72 | 1.36 |
| spinous_length | 22 | 0 | 0 | 0.35 | 0.60 | - | - | - | - |
| transverse_width | 22 | 0 | 0 | 1.76 | 1.76 | - | - | - | - |
| endplate | 21 | 5 | 6 | 0.98 | 0.98 | 1.69 | 2.45 | 1.91 | 1.40 |
| endplate_lower_area | 21 | 0 | 0 | 0.53 | 0.63 | - | - | - | - |
| pedicle_h | 21 | 9 | 16 | 1.00 | 1.00 | 1.28 | 1.54 | 1.41 | 1.11 |
| pedicle_incl_sag | 21 | 6 | 16 | 0.26 | 0.33 | 3.94 | 4.08 | 4.08 | 2.97 |
| pedicle_incl_trans | 21 | 0 | 15 | -0.06 | 0.44 | 2.37 | 2.90 | 2.90 | 2.23 |
| facet_w_sup | 5 | 0 | 5 | -1.26 | 1.26 | 1.28 | 1.45 | 1.37 | 1.02 |
<!-- end by_measure -->

Columns five to seven are Panjabi's own table against the papers; the last three are the median ratio of
a measured synthetic SD to the published SD at three settings (below); a dash is a measure whose cells
have no published SD. Canal depth matters most, since the rule reads it: Panjabi's mean sits a median
1.74 of his SDs above the papers'. Why is not recorded here; a difference of definition the reread's
mapping did not catch would read the same.

## Spread

Panjabi measured twelve spines, and his SDs are already 1.47 times the papers' at the median. The
generator then draws a size of its own and multiplies, so its spread counts the size a second time.
sd_mode "size_removed" takes the size's share out of his SDs before drawing, which leaves the first
excess; the nearest point shrinks every SD to 0.7 of his and the size's spread to 0.02. The validation's
20,000 people give the nearest point's SDs as 1.04 of the papers' without error and 1.30 with it; the
grid's own reading on 4,000 people, chosen among 180, gave 1.04.

## Structure

<!-- table structure -->
| correlation of subject means, L1-L5 | Griffith, men | women | generator | size taken out | nearest point |
| --- | ---: | ---: | ---: | ---: | ---: |
| canal area with body area | 0.29 | 0.25 | 0.59 | 0.78 | 0.41 |
| canal w with body area | 0.44 | 0.37 | 0.58 | 0.77 | 0.41 |
| canal ap with body area | 0.29 | 0.20 | 0.56 | 0.72 | 0.40 |
| canal ap with canal w | 0.61 | 0.55 | 0.50 | 0.63 | 0.37 |

| measure | cells | printed equal | share of the body's sex difference | quartiles | generator | papers (cells) |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| canal_ap | 20 | 9 | 0.00 | -0.46 to 0.00 | 1 | eisenstein1977 15; ahmed2019 5 |
| canal_w | 20 | 1 | 0.35 | 0.33 to 0.41 | 1 | eisenstein1977 15; ahmed2019 5 |
| endplate | 5 | 0 | 1.05 | 0.98 to 1.08 | 1 | chen2011 5 |
| endplate_depth | 5 | 0 | 0.99 | 0.96 to 1.01 | 1 | chen2011 5 |
| endplate_lower | 5 | 0 | 0.96 | 0.93 to 1.11 | 1 | chen2011 5 |
| endplate_lower_depth | 5 | 0 | 0.97 | 0.91 to 0.99 | 1 | chen2011 5 |
| pedicle_w | 12 | 0 | 0.34 | 0.23 to 0.44 | 1 | duman2026 12 |

The body's unit, log(men/women) = 0.133, is the median over the end-plate widths and depths and the posterior heights (chen2011 10).
<!-- end structure -->

Griffith's are the only correlations of a person's measures any of the 39 papers prints, over 540 men
and 540 women apart, on CT; the synthetic ones are read on measured values, and each of the generator's
two end-plate areas stands in for Griffith's mid-pedicle section on its own, the two correlations
averaged. The generator has no sex, so its correlations should sit at or above the within-sex ones; they
sit well above for the body, and below for the canal's depth with its width, since nothing but the size
ties two measures of the canal. The nearest point, with its small size spread, comes down to 0.40 and
0.41 for the body and to 0.37 for the canal's two extents, further below Griffith's 0.55 and 0.61.

The second table tests the generator's assumption that every length scales with one size. The canal's
depth shows no sex difference at the median, but 9 of its 20 pairs print the two sexes equal, every one
Eisenstein's in whole millimetres; Ahmed's five give 0.20 of the body's. The canal's and pedicle's widths
carry about a third of it. The upper end-plate's width and depth are the unit itself (Chen 2011's ten
pairs), so their 1 says nothing; the lower end-plate, from the same paper, also carries all of it. A
model that gave each measure its own loading on size (population.py holds the option, loadings) might
draw both the lower correlations and the sexes' differences; it is not tried here.

## Quality and curation

A vertebra a person could have holds relations that the papers' definitions make geometrically necessary,
whatever the population; synthval/qi.py writes each with its argument. None is fitted.

<!-- table quality -->
| setting (% of vertebrae / % of people) | sign | floor | box | convex | inside | any |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| generator, all 32 measures | 2.1 / 36 | 3.7 / 54 | 32.3 / 99 | 10.5 / 77 | 0.1 / 3 | 42.2 / 100 |
| generator, the seven SPINEPS measures | 0.0027 / 0.060 | 0.0055 / 0.12 | 0.0 / 0 | 0.0 / 0 | 0.0 / 0 | 0.0059 / 0.13 |
| size_removed, all 32 measures | 1.7 / 30 | 3.0 / 47 | 21.6 / 97 | 1.8 / 30 | 0.090 / 2 | 25.4 / 99 |
| size_removed, the seven SPINEPS measures | 0.00045 / 0.010 | 0.0032 / 0.070 | 0.0 / 0 | 0.0 / 0 | 0.0 / 0 | 0.0032 / 0.070 |
| nearest the papers, all 32 measures | 0.3 / 6 | 0.9 / 15 | 9.1 / 70 | 1.4 / 19 | 0.0036 / 0.080 | 11.2 / 79 |
| nearest the papers, the seven SPINEPS measures | 0.0 / 0 | 0.0 / 0 | 0.0 / 0 | 0.0 / 0 | 0.0 / 0 | 0.0 / 0 |

| setting | people kept | dropped | for sign | for inside |
| --- | ---: | ---: | ---: | ---: |
| generator | 6207 | 3793 | 3611 | 282 |
| nearest the papers | 9444 | 556 | 551 | 8 |
| size_removed | 6849 | 3151 | 3018 | 196 |
<!-- end quality -->

The seven SPINEPS measures are almost never flagged because no indicator ties two of them: only sign and
floor reach them, through a canal depth drawn at or below zero or held at the floor, in 13 of 10,000
people at the generator and none at the nearest point. The QI rate is set by the SDs (sd_scale,
sd_mode), a little by r_between, by the CT's error only through the floor, since box, convex and inside
read the true anatomy, and not at all by the size's spread, since size scales an area and its rectangle
alike (table state_space). The six phenotypes of model.py carry the same rates as the typical column,
41.8 to 42.5% of vertebrae. Curation drops a person only for sign or inside, which no definition allows;
box and convex are left as indicators, since the curvature allowances they make (5% over for an
end-plate, 15% for a facet) are judgements.

## State space

Each axis was moved alone from the generator's point, then a grid of the four axes that set the spread
and the correlations was searched (synthval/sweep.py). The last column counts the cells (measure, level)
where size_removed would leave no SD of the level's own, since the size alone passes the printed SD;
there it keeps a tenth of the SD.

<!-- table state_space -->
| point | SD ratio, true | SD ratio, measured | neighbour r | mean Griffith-pair r | box (% vertebrae) | any (% vertebrae) | any (% people) | cells held at a tenth of the SD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| generator | 1.66 | 1.80 | 0.39 | 0.55 | 32.0 | 41.9 | 100 | 0 |
| scale_sd=0.0 | 1.49 | 1.64 | 0.25 | 0.01 | 31.9 | 41.9 | 100 | 0 |
| scale_sd=0.035 | 1.51 | 1.71 | 0.29 | 0.24 | 32.0 | 41.9 | 100 | 0 |
| scale_sd=0.05 | 1.58 | 1.73 | 0.33 | 0.39 | 32.0 | 41.9 | 100 | 0 |
| scale_sd=0.1 | 1.83 | 1.99 | 0.49 | 0.71 | 32.0 | 41.9 | 100 | 0 |
| rho=0.0 | 1.67 | 1.81 | 0.20 | 0.69 | 32.0 | 41.8 | 100 | 0 |
| rho=0.25 | 1.66 | 1.80 | 0.24 | 0.65 | 32.0 | 41.8 | 100 | 0 |
| rho=0.75 | 1.65 | 1.79 | 0.64 | 0.44 | 31.9 | 42.0 | 100 | 0 |
| rho=0.9 | 1.65 | 1.79 | 0.84 | 0.38 | 31.8 | 42.0 | 97 | 0 |
| phi=0.3 | 1.66 | 1.80 | 0.57 | 0.50 | 32.0 | 41.9 | 100 | 0 |
| phi=0.6 | 1.67 | 1.80 | 0.75 | 0.44 | 31.9 | 41.9 | 100 | 0 |
| phi=0.9 | 1.67 | 1.80 | 0.93 | 0.37 | 32.0 | 42.1 | 98 | 0 |
| r_between=0.2 | 1.66 | 1.80 | 0.39 | 0.60 | 30.4 | 39.9 | 100 | 0 |
| r_between=0.4 | 1.66 | 1.81 | 0.39 | 0.65 | 28.8 | 37.9 | 100 | 0 |
| error_scale=0.5 | 1.66 | 1.71 | 0.39 | 0.56 | 32.0 | 41.2 | 100 | 0 |
| error_scale=2.0 | 1.66 | 2.20 | 0.39 | 0.51 | 32.0 | 45.5 | 100 | 0 |
| sd_scale=0.7 | 1.28 | 1.47 | 0.49 | 0.70 | 13.0 | 16.2 | 94 | 0 |
| sd_scale=0.85 | 1.46 | 1.63 | 0.43 | 0.62 | 22.2 | 28.7 | 100 | 0 |
| sd_mode=size_removed | 1.47 | 1.68 | 0.43 | 0.72 | 21.3 | 25.1 | 99 | 34 |
<!-- end state_space -->

<!-- table grid -->
| scale_sd | sd_scale | rho | r_between | SD ratio, true | neighbour r | any (% vertebrae) | distance |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.020 | 0.70 | 0.75 | 0.40 | 1.04 | 0.58 | 11.0 | 0.025 |
| 0.020 | 0.70 | 0.50 | 0.40 | 1.04 | 0.28 | 13.8 | 0.028 |
| 0.035 | 0.60 | 0.75 | 0.00 | 0.97 | 0.62 | 9.4 | 0.028 |
| 0.035 | 0.60 | 0.75 | 0.20 | 0.97 | 0.62 | 7.8 | 0.031 |
| 0.035 | 0.60 | 0.50 | 0.00 | 0.97 | 0.36 | 9.4 | 0.034 |
| 0.035 | 0.70 | 0.75 | 0.20 | 1.11 | 0.61 | 13.5 | 0.035 |
| 0.020 | 0.60 | 0.75 | 0.40 | 0.90 | 0.58 | 6.1 | 0.037 |
| 0.035 | 0.70 | 0.50 | 0.00 | 1.11 | 0.33 | 16.1 | 0.038 |

180 points searched; the eight nearest shown.
<!-- end grid -->

The papers pin the size's spread (0.02 to 0.035) and the SDs' scale (0.6 to 0.7 of Panjabi's); they do
not pin rho or r_between. The three nearest points lie within 0.003 of one another and take rho 0.75,
0.5 and 0.75 and r_between 0.4, 0.4 and 0, so the nearest point's correlations are a tie broken by
sampling, and the gold persons' first measurable number is the correlation between neighbouring levels
(item 7).

## Naming across the state space

The exact rule on the seven SPINEPS measures with the CT's errors, on fields drawn at points of the state
space. "1 body" is the share of fields of one body named exactly; "rule matched" is a rule built for the
point's own setting where a rule can hold it (blank for the generator, whose rule is its own).

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
| nearest the papers | 57.4 | 79.9 | 98.4 | 59.8 | 82.0 | 98.6 |
<!-- end naming -->

Doubling the CT's error costs more than any other axis, 8 points at one body. A narrower population
names better: taking the size out of the SDs gains 9 points at one body and 11 at three, the nearest
point 10 and 7. phi and r_between, which no rule here can hold, cost almost nothing.

## Power, rerun

research_notes/cadaver-power part B took the spread between studies from Panjabi's comparison tables, a
median 0.39 of a person's SD. The 39 papers' own series give it again, from the REML spread in every cell
with three series or more, its sampling error already out. REML reads low with three to seven series,
where it often puts the spread at zero: had the truth been 0.83 in every cell, the median would read
0.75. The calibrated column is the spread that, given to every cell with its own series' counts and SEs,
makes the expected median the one observed (synthval/power.py, calibrated_median_f); it corrects the
median, not the spread of the spread.

<!-- table spread -->
| spread between series | cells | tau / Panjabi's SD, median (quartiles) | calibrated | tau / papers' SD | calibrated | worth in scans (at the calibrated median) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| part B before (Panjabi's comparison tables) | 86 | 0.39 |  |  |  |  |
| 39 papers, main | 56 | 0.83 (0.60 to 1.06) | 0.92 | 0.94 | 1.04 | 1.8 (1.3) |
| 39 papers, same definition only | 17 | 0.82 (0.70 to 0.99) | 0.94 | 0.79 | 0.90 | 1.7 (1.3) |
| 39 papers, without tan2004 | 32 | 0.63 (0.48 to 0.99) | 0.69 | 0.76 | 0.83 | 2.9 (2.5) |

| split of the spread | series x measure | distances | shift, whole measure (calibrated) | level by level (calibrated) | total (calibrated) |
| --- | ---: | ---: | ---: | ---: | ---: |
| all | 56 | 289 | 0.83 (0.92) | 0.41 (0.42) | 0.92 (1.01) |
| same definition only | 12 | 63 | 0.71 (0.82) | 0.35 (0.40) | 0.79 (0.91) |
| without tan2004 | 41 | 188 | 0.76 (0.84) | 0.41 (0.44) | 0.86 (0.95) |

Drawn with a shift of 0.90 and a rest of 0.40, 24 sets of series laid out as the papers' give the moments 0.79 and 0.38 and the calibrated pair 0.89 (SE 0.019) and 0.40 (SE 0.006).
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
| 39 papers, all | 0.92 / 0.42 | 34.6 (12.9; 88.7) | 53.4 (19.4; 92.1) | 83.8 (11.8; 95.3) |
| 39 papers, without tan2004 | 0.84 / 0.44 | 35.5 (11.9; 90.0) | 56.5 (16.3; 92.0) | 83.9 (11.8; 94.7) |
| 39 papers, same definition only | 0.82 / 0.40 | 37.6 (9.9; 96.0) | 58.6 (14.2; 94.0) | 85.8 (9.8; 95.8) |

Each moved row is the mean over 4 tables of the same 300 columns; the own-table row is the one table itself.
<!-- end part_c -->

The first rows repeat cadaver-power's part C on this note's columns; the last three move the rule's
table by the calibrated split just measured. Without Tan's series, whose SDs are uncertain, the spread is
0.63 (0.69 calibrated) and a pool is worth about 2.9 scans. Either way part A's answer, that no
meta-analysis of published series matches 2,000 CT scans of the population named, gets stronger.

## What gold persons can test

<!-- table gold -->
| persons | least mean shift found, one cell (SD) | one cell of 154, Bonferroni (SD) | least SD ratio found | half-width of a neighbour r of 0.5 | six lumbar-type segments | of which a true L6 | four lumbar segments | a rib on the first lumbar-type body | no twelfth rib, one side or both |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 17 | 0.72 | 1.35 | 1.61 | 0.38 | 0.4 | 0.1 | 0.3 | 0.4 | 0.7 |
| 142 | 0.24 | 0.38 | 1.18 | 0.12 | 3.5 | 0.6 | 2.6 | 3.3 | 6.0 |
| 159 | 0.22 | 0.36 | 1.17 | 0.12 | 3.9 | 0.7 | 2.9 | 3.7 | 6.8 |
| 300 | 0.16 | 0.26 | 1.12 | 0.09 | 7.4 | 1.3 | 5.4 | 7.0 | 12.8 |
| 1000 | 0.09 | 0.14 | 1.06 | 0.05 | 24.8 | 4.5 | 18.1 | 23.2 | 42.6 |
<!-- end gold -->

The first four columns are the least effect a two-sided test at 5% finds with 80% power, by the exact
tests: the noncentral t for a mean against a published one, with the SD read from the same people, and
the chi-square for an SD against a published one; then the half-width of a 95% interval for a
correlation of 0.5. The rest are the persons expected with each state at the papers' prevalences. 17 and
142 are VerSe's and TotalSegmentator's gold 3 persons, 159 both (holdings/gold-tier-3.md).

## The assumptions beside the papers

<!-- table assumptions -->
| error of one reading | modality | range | source |
| --- | --- | ---: | --- |
| body heights | CT | 0.30 to 0.65 mm | duman2026, 50 scans read again after 4 weeks; error.md L53 |
| pedicle width and height | CT | 0.20 to 0.55 mm | duman2026; error.md L63 |
| pedicle angle | CT | 0.70 to 1.80 deg | duman2026; error.md L71 |
| canal width and depth | CT | 0.40 to 1.20 mm | griffith2016, by level L1-L5; error.md L60 |
| canal area | CT | 10.00 to 30.00 mm2 | griffith2016; error.md L60 |
| disc and end-plate diameters | MRI | 0.50 to 0.90 mm | tang2016, between observers; error.md L58 |
| disc and end-plate area | MRI | 40.00 mm2 | tang2016, between observers; error.md L58 |
| pedicle width and height | bone, caliper | 0.35 to 0.95 mm | yu2015; error.md L65 |
| interpedicular distance | film | 0.27 mm | hinck1966, 89 duplicate readings; error.md L61 |
| one vertebra, CT against caliper | CT | 0.22 mm | vanderhouwen2009, a pig vertebra; error.md L57 |

| the generator's error, by kind | measures | error | median error / SD at L3 |
| --- | ---: | ---: | ---: |
| angle | 8 | 3.00 | 0.50 |
| area | 6 | 9.47 to 32.00 | 0.31 |
| length | 18 | 1.00 | 0.34 |

| state | model.py (%) | chain (%) | papers (%) | source |
| --- | ---: | ---: | ---: | --- |
| six lumbar-type segments (L6 or lumbarised S1) | 16.7 | 5.0 | 2.48 (1.39 to 4.39) | eisenstein1977 p. 177, 11 / 443 dry skeletons (2 true L6, 9 lumbarised S1); anomaly-priors.md |
| of which a true L6 | - | - | 0.45 (0.12 to 1.63) | eisenstein1977 p. 177, 2 / 443; anomaly-priors.md |
| four lumbar segments (sacralised L5), a ceiling | 16.7 | - | 1.81 (0.92 to 3.52) | eisenstein1977 p. 177, 8 / 443; sacralisation undefined, so a ceiling; anomaly-priors.md |
| a thirteenth rib-bearing body (T13) | 16.7 | 5.0 | no count | no count and no bound in the 43 papers; any value is a modelling choice; anomaly-priors.md |
| a rib on the first lumbar-type body | 16.7 | - | 2.32 (1.33 to 4.01) | duman2026 Table 5 p. 10, 12 / 517 chest CTs; anomaly-priors.md |
| no twelfth rib, one side or both | 16.7 | - | 4.26 (2.83 to 6.36) | duman2026 Table 5 p. 10, 22 / 517; a ceiling for bilateral absence, laterality never reported; anomaly-priors.md |
<!-- end assumptions -->

The errors are the reread's synthesis draft (synthesis/error.md at 45130ac), which no second reader had
checked at that commit. The generator's 1 mm for a length is larger than every CT reading error the
draft gives but the canal's largest (0.4 to 1.2 mm), and its 3 degrees for an angle is larger than the
0.7 to 1.8 degrees of the pedicle's. The prevalences are the reread's checked priors (anomaly-priors.md,
whose 43 papers are the 39 and Panjabi's four): model.py draws each of its six phenotypes as one column
in six, the chain of levels at 0.05, and the papers count six lumbar-type segments in 2.48% of 443
skeletons and give no count at all for a thirteenth rib-bearing body.

## Figures and renders

figures/FIGURES.md lists each with its caption, its CSV and the sha256 of every file. Line graphs are in
the house format (synthval/house.py, a copy of the build-up study's); the renders draw synthetic vertebrae
in Benzel's manner, each section a superellipse holding its measured width, depth and area, and dashed
where no superellipse of those extents holds the area (the box indicator, drawn).

- fig1_means, fig2_spread, fig3_structure: the validation.
- fig4_state_space, fig5_naming: the state space and naming across it.
- fig6_power: the spread between series, part C rerun, what gold persons can test.
- fig7_quality: the quality indicators by measure and level.
- fig8_assumptions: the errors and prevalences the generator assumes, beside the papers'.
- render1_axial, render2_column, render3_solid: L3 from above, the lumbar column from in front, and the
  column as solids, Panjabi's means beside synthetic people.

## Run it

From this folder, with the Python that holds bordercall's pinned packages (requirements-schwingcheck.txt):

```
python3 -I run.py --out records                    # every record, about eight minutes on 4 CPUs
python3 -I figures.py --records records --out figures
python3 -I tables.py --records records --write README.md
python3 -I tables.py --records records --check README.md     # exit 1 when a table differs from the records
cd ../.. && python3 -m unittest discover -s research_notes/synthetic-validation/tests
```

records/RECORD.json gives the command, the seeds, the sizes, bordercall's commit, the snapshot's commit
and digest, and the sha256 of every file of this note's code, read before the run starts. The run is
deterministic: two runs give the same bytes in every record but RECORD.json's seconds.

## Files

- run.py writes records/; figures.py and render.py draw figures/; tables.py writes the tables above;
  snapshot.py cuts and checks data/.
- synthval/: literature.py (the selection), pooling.py, population.py, validate.py, structure.py, qi.py,
  sweep.py, naming.py, power.py, references.py (the papers' errors and prevalences), house.py.
- data/: the snapshot of the reread's series and SOURCE.json.
- tests/test_synthval.py: 23 tests of the code against what its docstrings say.

## What this note does not do

- It does not change the generator. The nearest point is the nearest of a grid, not a fitted model, and
  it is held to within-sex correlations by a population with no sex; a change to schwingcheck's defaults
  is the owner's to choose, and would move every result the build-up study recorded.
- It reads 39 papers' tables, not their people: a pooled mean is of populations, and the gold persons
  are the first data that can test a person's correlations.
- The series will change with the reread's corrections, the errors rest on a draft that had no second
  reader at 45130ac, and the prevalences rest on two papers.
