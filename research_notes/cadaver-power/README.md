# Cadavers against CT scans: the power calculation

Thread "Flesh out Panjabi, rewrite in PyMC", 2026-10-28, for greg's ask of 2026-10-27 23:55 UTC: "also can you do
a power calculation for how many cadavers i need in the metaanalaysis to match 2000 empirical CT scans with
sufficient power". Everything in part C is synthetic: the rule's own generator stands in for both the cadavers
and the scans. Parts A and B are arithmetic, a reading of Panjabi's printed tables and a count of the series
that spine-program's synthetic_spine/ records.

## Corrections after review (2026-10-28, 02:40 UTC; revised 04:50, 06:20 and 07:10 UTC)

Three reviews, of this note's arithmetic, its reading of Panjabi's tables and its simulation, made 21 findings;
a second check confirmed 13 of them, and the other 8 were rated low. All 21 are carried into the sections each
item below names. The answer holds and gets stronger. The scripts behind the figures are under verify/ (Files).
At 02:40 this list had six items. It now has eleven: the first eight reword those six as the rewrite carried
them, the ninth is for a check of the rewrite itself, the tenth for a second check of it, at 05:50, and the
eleventh for a third, at 06:50.

1. The headline is now that no meta-analysis of the published series matches 2,000 CT scans, however many
   cadavers it pools. It states its assumption that the CTs come from the population the rule names, and part A
   gives what they are worth if they do not (The answer; A).
2. "The 42 series" were 42 papers. synthetic_spine records 39 series, 36 of them with their counts, so their
   figures are now per cell from those counts: Panjabi's 12 spines are the only series at 675 of the 704 cells
   (The answer, item 1; A).
3. The 1,700 cadavers are now the best case, not a reason. They need calipers and the SPINEPS chord to agree
   within about 0.06 mm, and they rest on CT errors that measures.py assumes (1,184 to 1,917 with the errors
   doubled or halved). Over the 154 cells of the seven SPINEPS measures, the only ones a CT measurer reads, it
   is 1,716, and 2,000 CTs give the other 550 of the 704 cells no value at all (The answer, item 1; A).
4. "About 8 scans" is now a range, about 2 to 16 scans (about 4 to 16 without the cervical endplate area's 6
   cells, item 10), and 3 to 10 for the five measures the rule reads, since the median spread of 0.39 is now read
   beside pooled estimates, the five measures alone and the rows the papers attribute to another definition (The
   answer, item 2; A; B).
5. tau is now defined by the exchangeable model the formulas use, and each of part A's figures over many cells
   is a median over them with the least and the most (A).
6. "Near r = 0 ... keeps the promise" is gone: over 36 tables the r = 0 table sits at the edge of the promise at
   3 bodies, 11 of the 36 below it, and falls short with the shift pooled or with very large earlier series. The
   published-series rows now give their table-to-table spread (The answer; C).
7. "About 60 CTs" now holds for the means only once the rule's size term is taken out of the table, and the SDs
   need about 68 (The answer; A; C).
8. Smaller: Panjabi's own reasons for the two rows left out, the over-correction of the paired measures, the
   ten-measure split's largest group named (the cervical endplate area with each level's own SD, the lumbar
   pedicle width with one SD per group), "nearly all" at r = 0, and four runs, not three (B; C; How to rerun).
9. A check of the rewrite found slips of its own, now fixed where they stood: four roundings, and ranges part
   A still lacked; Bonczar 2024, a meta-analysis of 18 studies with Panjabi's, Tan's and Robertson's among them,
   counted as one more series of living people, and a series with no count taken as 12 without saying so; the
   CT pool's bound written as a distance from the population named; very large earlier series said to break the
   promise "whatever r is", when only r = 0 was run; and the published-series tables matched to one count of
   people of the population named for every width, where the count differs from one width to the next. Found
   while fixing these: the pedicle counts are the table's, four of whose rows spine-program pull request #239
   (branch claude/238) finds wrong, and the note now says so (The answer; A; C).
10. A second check of the rewrite found more, now fixed where it stood. The answer named ENHANCE.PET's three
    sites among the whole-spine collections held; bordercall's holdings count 159 persons' whole spines with a
    person's masks, TotalSegmentator's and VerSe's, and the table's CTs are to be measured from the census's
    SPINEPS masks. The range's low end, 2.3 scans, comes from a pooled spread that the cervical endplate area's 6
    cells raise from 0.55 to 0.72, and the note now says so and why it names no value in the range as the
    likeliest. The break at 9 bodies at r = 0.8 rests on 4 tables, and the answer and handoff-item4.md now say so.
    Claims made at every width now leave out 1 body for the rows near 99%, whose few answers at 0.99 there can
    show the promise neither kept nor broken; 12 people's, far below it, break it there too (item 11). Sources
    found only on a branch not yet merged are cited as such, or described. Smaller: what a field is and how many
    are answered at 1 body, a shift bound given only for the shifts run, one rounding and uneven decimals (The
    answer; A; B; C).
11. A third check found five more, now fixed where they stood. At 1 body a table's few 0.99 answers can still
    show the promise broken where it gets several wrong: 12 people's do, and so do those of 0.5 SD level by
    level and of the series read harshly, and, less surely, of r = 0.8 and r = 1. The pilot gives the count of
    masks from C2 only for the rows it reads; only the full run gives it for all. Robertson's pedicle width is
    no longer named among the definitions the series mix, since only a branch not yet merged reads it, and its
    newer commit reads it otherwise. The break at 9 bodies rests on the note's 4 tables at r = 1 as well as at
    r = 0.8. The scripts behind EPAl's share and the 1-body counts are now under verify/ (The answer; A; B; C;
    What is not known).

## The answer

No meta-analysis of the published series matches 2,000 CT scans, however many cadavers it pools. That assumes the
2,000 CTs come from the population the rule will name. They are to come from public de-identified collections
already held on the grid, measured from their existing SPINEPS masks (bordercall TODO.md, section 5, on main at
eb29680). The first run over them is to be bordercall's pilot, not yet sent: it reads at most 4,000 rows and stops
at 300 countable cases, and the full run after it reads every row of the census's two tier lists, tier1.tsv and
tier2.tsv with 5,094 and 12,217 CTs, that names a SPINEPS vertebra mask (SchwingNet
docs/research/bordercall-corpus.md); these are the census's tiers, not the gold tiers below. What the pilot writes
is to be checked against the seven measures before it counts as the table's first run (TODO.md, section 5), and how
many of those masks count from C2 is not known until the full run. The whole spines held now with a person's masks,
gold tier 3, are 159 persons' CTs, TotalSegmentator's 142 and VerSe's 17; ENHANCE.PET's Leipzig and Careggi CTs are
not held, and autoPET's are held without ENHANCE.PET's masks (bordercall holdings/gold-tier-3.md). Nothing here
shows that any of these CTs sample that population. CTs pooled from other populations carry a population term of
their own, and part A gives what they are then worth. There are three reasons.

1. **Precision, at best.** Suppose every study had measured the population named, and calipers agreed with the
   SPINEPS chord within 0.024 of a person's SD, about 0.06 mm (part A). A cadaver chord is taken as exact; a CT
   measure carries the error measures.py assumes and no source measures: 1 mm for a length, sqrt(pi A / 2) mm2
   for an area A (9.5 to 32 mm2 here) and 3 degrees for an angle. Then about 1,700 cadavers match 2,000 scans on
   a level's mean: 1,706 is the median over the 704 level-and-measure cells of the 32 measures (51 to 1,988), and
   1,716 the median over the 154 cells of the seven SPINEPS measures, the only ones a CT measurer reads (896 to
   1,920). With the CT errors halved it is 1,917 (189 to 1,997); doubled, 1,184 (13 to 1,954). The recorded
   series fall short even of this best case:
   - synthetic_spine's two tables hold 39 distinct series from 42 papers. By the tables' cohort columns, 15 are
     cadaveric or skeletal, with 1,163 recorded specimens in all and no count for three of them. The other 24 are
     23 CT, MRI or radiograph series of living people, each with an imaging error of its own, and Bonczar 2024, a
     meta-analysis of 18 studies of mixed modality, Panjabi 1992, Tan's 10 spines and Robertson 2000 among them
     (synthetic_spine/README.md). The check of the papers in spine-program pull request #239 (branch
     claude/238) finds the cohort columns wrong in four of the pedicle rows, so the pedicle counts below are the
     table's, not the papers' (A).
   - Panjabi's 12 spines are the only series at 675 of the 704 cells, worth a median of 14 scans there (12 to
     471).
   - At the other 29 cells there are 22 to 144 cadavers for the four SPINEPS measures the series reach (worth 23
     to 194 scans), and, as the pedicle table records them, about 790 for the pedicle width at L1 to L5, which
     no SPINEPS measurer reads (worth 853 to 1,435). No cell reaches 2,000 at the tables' counts.
2. **The studies do not agree.** Panjabi's comparison tables print his means beside earlier studies' means for
   the same measure and level: cervical Table 7, thoracic 8A and 8B, lumbar 6, and facets 9 and 10, read cell by
   cell into provenance.csv. Take the 86 level-and-measure cells, over 10 measures, where three or more of 14
   studies give a mean. After sampling error is taken out, the studies' means differ by a median of 0.39 of one
   person's SD over those cells (quartiles 0 and 0.73; 56% of cells above 0.3). That median is one reading of
   several, and most of the others put the spread higher (part B):
   - Pooled over the cells, weighted by degrees of freedom, the spread is 0.72. A pooled figure follows its largest
     cells: the cervical lower endplate area's 6 cells (EPAl), 12 of the 229 degrees of freedom, carry 38% of the
     weighted sum it averages, and without them it is 0.55 (verify/epal_share.py). A median of per-cell figures
     that rest on 2 to 5 degrees of freedom each runs low: if the true spread were 0.39 everywhere, the median
     would come out about 0.31.
   - Over the 36 cells of the five measures the seven SPINEPS measures read, the median is 0.50 (pooled 0.62).
     The 40 pedicle cells, which no SPINEPS measurer reads, hold 21 of the 25 cells at 0.
   - The papers' own text attributes some rows to another definition. With those rows left out the median is
     0.27 over 74 cells (pooled 0.50), and 0.35 over the five measures' 34 cells (pooled 0.53).
   - At these spreads even an infinitely large meta-analysis is worth at most about 2 to 16 scans of the
     population named for each level's mean, or about 4 to 16 without EPAl (medians over the 704 cells: 16 at
     0.27, 7.7 at 0.39, 4.7 at 0.50, 3.9 at 0.55 and 2.3 at 0.72), and 3 to 10 for the five measures the rule
     reads (medians over the seven's 154 cells: 9.5 at 0.35, 4.7 at 0.50 and 3.0 at 0.62). Its table can come
     no closer to the population named than the spread between populations. Panjabi's 12 alone are worth
     medians of 3.0 scans at 0.39 and 2.0 at 0.50.
   - To match 2,000 scans, the studies would have to agree within 0.024 of a person's SD (median over the 704
     cells; 0.022 to 0.14), a tenth to a thirtieth of the readings above.
3. **No correlations.** A published table gives means and SDs. It never gives the correlation of one level with
   the next, or of one measure with another, and the rule's rho and the copula of the analysis greg attached on 27
  October 2026 at 23:55 UTC ("Bayesian Articulated Statistical Shape Modeling of the Spine: Prior Art, Accuracy, and Computational Performance",
  an upload to the Claude project that bordercall does not hold) both need
   those. Only individual people's measurements give them: the CTs, or a series that prints every specimen.

What naming needs is less than a match, and part C measures it on synthetic columns:

- **From the population named.** A table taken from about 50 people of the population the rule names, measured
  without error and with no size spread (as part C draws them), names within 2 to 4 points of a table from 2,000.
  On part C's 300 columns, at 3 and 9 bodies, its 0.99 answers are right 99.58% and 99.63% of the time (worst of 6
  tables 99.35% and 99.38%), which keeps the rule's promise that they are right 99% of the time, counting the
  tables' spread but not the columns' error; bordercall's build-up study, on 200 columns of its own and counting
  their error, cannot tell at 3 bodies whether 50 people keep it (part C). A table from 12
  people loses 8 to 14 points and breaks it. CTs need more: about 60 for the means and about 68 for the SDs, once
  the CT error's variance is taken out of each SD and the estimator of TODO.md item 5 takes the rule's size term out of the
  table. A plain table from 50 CTs loses 4.8 to 7.2 points, and 58 CTs with only the error taken out lose about 6
  points at 3 bodies and answer half as many fields at 0.99 (part C).
- **From the published series.** A table built from the published series, with the studies disagreeing as
  Panjabi's comparison tables show over the five measures the rule reads, loses about 2 to 13 points (17 read
  harshly). That holds however many cadavers it pools, since these tables carry no sampling error at all.
  - How far it falls turns on two numbers the comparison tables cannot give: r, how closely one measure follows
    itself from level to level within a person, and the earlier studies' specimen counts.
  - At the kindest reading, r near 0 and earlier series as small as Panjabi's 12, it loses about 4 to 5 points
    at 1 and 3 bodies and about 2 at 9 (4.4, 4.7 and 1.6 over all its 24, 36 and 36 tables). That is about what
    25 people of the population named lose at 1 body (4.4), a little more than 50 lose at 3 bodies (4.0), and
    between what 50 and 100 lose at 9 bodies (2.1 and 1.0). At 3 bodies its 0.99 answers are right 99.06% of
    the time over the 36 tables, at the edge of the promise, and 11 of the 36 fall below 99%; at 9 bodies they
    keep it (99.62%, none below).
  - With the shift pooled the way the level-by-level part is, r = 0 loses about 6.5 points at 3 bodies and its
    0.99 answers are right 98.3% of the time, 13 of 20 tables below 99%. Read that way, r decides how far the
    series fall short at 3 bodies, not whether they do. With very large earlier series, r = 0 loses about 7 to
    11 points at 1 and 3 bodies and breaks the promise at 3 and 9 bodies. Such series leave a level-by-level
    part of 0.233 to 0.279 at any r (verify/sampling_share.py), so the promise should break at every r, but
    only r = 0 was run.
  - From r = 0.5 up it is worth about 12 to 25 people at 3 bodies and breaks the promise there; at 9 bodies it
    breaks at r = 1 and, narrowly, at r = 0.8, both on the note's 4 tables alone (97.84% and 98.53%). Real
    columns likely put r that high, but that is not known here; the CTs would give it.

## A. The arithmetic (cadaver_power.py, part_a.json)

For the mean of one level of one measure, sd is the person-to-person SD and e the measure's CT error. A cadaver
is taken as measured exactly (calipers), the case kindest to the cadavers. A CT carries the error measures.py
assumes, which no source measures: 1 mm for a length, sqrt(pi A / 2) mm2 for an area A and 3 degrees for an
angle. One cadaver is then worth r = 1 + e^2 / sd^2 scans.

The populations the studies sampled and the population being named are taken as draws about one centre, with SD
tau = f * sd, f being part B's spread of the studies' means about their centre. So the population named is
exchangeable with those studied: it lies tau from the centre and sqrt(2) tau from any one study (0.55 sd at
f = 0.39). That is an assumption, and the ceiling below rests on it.

- **One population.** n cadavers match N scans when n = N sd^2 / (sd^2 + e^2) = N / r.
- **The population being named.** k studies of m cadavers each are worth r / (f^2 (1 + 1/k) + 1/(k m)) scans,
  and studies of unequal counts n_i are worth r / (f^2 + 1 / sum_i 1/(f^2 + 1/n_i)). However many cadavers it
  pools, a meta-analysis lands at the centre, tau from the population named, so it is worth at most r / f^2
  scans and matches N scans only when f <= sqrt(r / N).
- **A method bias.** A bias b between the caliper chord and the CT's chord, shared by every study, adds
  (b / sd)^2 to that denominator, and no number of studies averages it away: a match also needs
  b <= sqrt(r / N) * sd.
- **The centre.** If the population named sat at the studies' centre instead, there would be no ceiling: k
  studies would be worth r / (f^2 / k + 1/(k m)), and N f^2 / r studies of unlimited size would match 2,000
  scans (medians over the 704 cells: 154 at f = 0.3, 5 to 179 over the cells, and 426 at 0.5, 13 to 497). No
  patient comes from that average.
- **CTs from other populations.** N CTs pooled from k_ct populations about the same centre carry the same term:
  they are worth r / (f^2 (1 + 1/k_ct) + r / N) scans of the population named.

In the next two tables and the lines with them, each figure is a median over cells, with the least and the most
in brackets. The 704 cells are the pool's 32 measures at its 22 levels, C3 to L5: 396 length, 132 area and 176
angle cells. The seven's 154 cells are the seven SPINEPS measures, all lengths and the only measures a CT
measurer reads, so 2,000 CT scans would give the other 550 cells no value at all. The ends of the all-cell
ranges are single cells: the least cadavers and the largest r at the T10 endplate inclination, an angle whose
person SD of 0.49 degrees sits against the CT's 3, and the most cadavers at the transverse width, whose person SD
is about 13 mm (verify/extremes.py).

| | all 704 cells | the seven's 154 cells |
|---|---|---|
| r = 1 + e^2 / sd^2 | 1.17 (1.006 to 39) | 1.165 (1.04 to 2.23) |
| cadavers that match 2,000 scans of one population | 1,706 (51 to 1,988) | 1,716 (896 to 1,920) |
| the same, CT errors halved | 1,917 (189 to 1,997) | 1,921 (1,529 to 1,979) |
| the same, CT errors doubled | 1,184 (13 to 1,954) | 1,204 (337 to 1,713) |
| the largest f that matches 2,000 scans | 0.024 (0.022 to 0.140) | 0.024 (0.023 to 0.033) |
| the same, CT errors halved | 0.023 (0.022 to 0.073) | 0.023 (0.022 to 0.026) |
| the same, CT errors doubled | 0.029 (0.023 to 0.278) | 0.029 (0.024 to 0.054) |
| the largest caliper-to-CT bias that matches, mm | 0.059 (0.030 to 0.294) over the 396 length cells | 0.059 (0.030 to 0.111) |
| CTs that match 50 error-free people on the means, 50 r | 59 (50 to 1,963) | 58 (52 to 112) |
| the same on the SDs, 1 + 49 r^2 | 68 (51 to 75,547) | 68 (54 to 245) |

The SDs cost a CT r^2 where the means cost r, since a CT's SD estimate is s^2 - e^2, whose variance is
2 (sd^2 + e^2)^2 / (N - 1). Over the 176 angle cells alone the median r is 1.27 (1.009 to 39), and 1,572
cadavers match there (51 to 1,982).

At most what a meta-analysis is worth, r / f^2 in scans of the population named per level mean, and what
Panjabi's 12 spines are worth alone (k = 1, m = 12), at the spreads part B reads:

| f, the spread between populations | at most worth, all 704 cells | at most worth, the seven's 154 cells | Panjabi's 12 alone, all 704 cells |
|---|---|---|---|
| 0 | no limit | no limit | 14.1 (12.1 to 471) |
| 0.1 | 117 (101 to 3,927) | 117 (104 to 223) | 11.3 (9.7 to 380) |
| 0.2 | 29 (25 to 982) | 29 (26 to 56) | 7.2 (6.2 to 240) |
| 0.27: all cells, the definition rows left out | 16.1 (13.8 to 539) | 16.0 (14.3 to 30.6) | 5.1 (4.4 to 171) |
| 0.35: the five, the definition rows left out | 9.6 (8.2 to 321) | 9.5 (8.5 to 18.2) | 3.6 (3.1 to 120) |
| 0.39: all cells, as published | 7.7 (6.6 to 258) | 7.7 (6.9 to 14.7) | 3.0 (2.6 to 101) |
| 0.50: the five, as published | 4.7 (4.0 to 157) | 4.7 (4.2 to 8.9) | 2.0 (1.7 to 67) |
| 0.62: the five, pooled | 3.0 (2.6 to 102) | 3.0 (2.7 to 5.8) | 1.4 (1.2 to 46) |
| 0.72: all cells, pooled | 2.3 (1.9 to 76) | 2.2 (2.0 to 4.3) | 1.0 (0.90 to 35) |
| 0.87: synthetic_spine's series' own spread | 1.5 (1.3 to 52) | 1.5 (1.4 to 2.9) | 0.73 (0.63 to 24.6) |

With the CT errors halved or doubled, the ceiling at f = 0.39 is 6.9 (6.6 to 69) or 11.1 (6.7 to 1,013) scans
over the 704 cells, and 6.8 (6.6 to 8.6) or 10.9 (7.7 to 39.0) over the seven's 154.

**What the recorded series are worth.** synthetic_spine's tables, level_references.csv (27 series, T11 to L5)
and pedicle_width_references.csv (13 series, L1 to L5), with Panjabi 1992 in both, reach 35 of the 704 cells, and
29 of those hold a series beside Panjabi's (verify/count_series.py, verify/recorded_counts.py). Cadaveric or
skeletal specimens per cell, and what they would be worth if every study agreed (f = 0):

| cells | series | cadaveric specimens | worth at f = 0, scans |
|---|---|---|---|
| EPWu (synthetic_spine's endplate), T12 | 4 | 22 | 27 |
| EPWu, L1 to L5 | 7 | 22 | 23 to 25 |
| VBHp (h_post), T12 | 5 | 58 | 62 |
| VBHp, L1 to L5 | 6 to 7 | 28 | 30 to 31 |
| SCW (canal_w), T12 | 2 | 22 | 23 |
| SCW, L1 to L5 | 13 | 22, beside Eisenstein's dry bone with no count | 24 to 30 |
| SCD (canal_ap), T12 | 3 | 22 | 27 |
| SCD, L1 to L5 | 12 | 144 | 168 to 194 |
| PDW (pedicle), L1 to L5, which no SPINEPS measurer reads | 13 | 791, two counts missing | 853 to 1,435 |
| the other 675 cells | Panjabi's alone | 12 | 14 (12 to 471) |

The 791 takes Zindrick's "26-56 per level" as 56; read as 41 it is 776 (verify/per_cell.py). Counting the imaging
series of living people and Bonczar's meta-analysis too, the 29 cells hold 22 to 4,241 specimens and people. The
4,241, at the canal depth at L1 to L5, counts Bonczar's pooled 1,481, which takes in Panjabi's 12 and Tan's 10
again; without it those cells hold 2,760 (verify/recorded_counts.py).

These counts read the cohort columns as the tables record them. On spine-program's main (11d2aca),
synthetic_spine/README.md names only Robertson's cohort columns as wrong; the check of the papers in spine-program
pull request #239 (branch claude/238), which the rest of this paragraph follows, finds four of the pedicle rows
wrong. Olsewski's "cadaveric + patients, 100" are 21 cadaver spines. Robertson's "patients New Zealand, 100, CT"
are 10 dry-bone spines on radiographs. Krag's "CT vs cut cadaver" is CT of 41 living patients, with 8 sectioned
cadaver vertebrae as its check. Zindrick's "caliper" was radiographs and CT, and the paper gives no count of
specimens or people. Yu's five values are also midpoints of two age groups' means, not means of its 503
skeletons. So the pedicle width's 791 is the table's count, not the papers'. Read from the papers, Olsewski's 100
becomes 21 and Robertson's 10 join the cadavers, but the total is not known, since Zindrick's paper gives no
count and the table records none for Lien.

Part A's formula at the recorded counts (verify/worth_real.py) treats every series as exact, which favours the
imaging series, and counts Bonczar's 1,481 as a series of its own. It takes a series that records no count as
12: Lien's and Krag's pedicle series, which it counts among the cadavers by their cohort columns (Krag's was CT
of living patients, above), and Eisenstein's dry bone at the canal width, which it counts with the other series
and not with the cadavers, since its cohort names no cadaver. Then:

- at f = 0.39, Panjabi's 12 alone are worth 3.0 scans at the 675 cells (2.6 to 101), and the series at the 29
  cells 3.9 to 10.9 (median 6.5; their cadavers alone 3.9 to 10.5, median 4.5);
- at f = 0.87, the series' own spread, Panjabi's 12 are worth 0.7 at the 675 cells (0.6 to 24.6), and the series
  at the 29 cells 0.9 to 2.2 (median 1.3; their cadavers alone 0.9 to 2.1, median 1.0).

With Bonczar left out, none of these figures moves at the precision printed (verify/worth_real_no_bonczar.log).

That 0.87 is the median spread of the series' own means, in units of Panjabi's person SD, over the 28 cells with
three or more series (0.42 to 1.94; verify/per_cell.py). It keeps sampling error, mixes definitions and methods (an
endosteal pedicle width, uncorrected radiographs, MRI, as the two tables' modality columns record them on
spine-program's main) and includes Bonczar 2024, a meta-analysis of 18 studies that takes in Panjabi 1992
(synthetic_spine/README.md), so it is an upper reading, not a replacement for part B's.

**CTs from other populations.** A pool of N = 2,000 CTs from k_ct populations that differ from the one named as
the studies do is worth r / (f^2 (1 + 1/k_ct) + r / N) scans of the population named per level mean. f is 0.39
if all of the 0.39 is population, and 0.12 if a tenth of its variance is. The last two columns give the largest
f, the SD of the pool's populations' means about their centre in person SDs, at which the pool is still worth
1,000 scans. Medians over the cells, with the least and the most:

| populations in the pool | worth at f 0.39, all 704 cells | worth at f 0.39, the seven's 154 | worth at f 0.12, all 704 cells | worth at f 0.12, the seven's 154 | largest f for 1,000 scans, all 704 cells | largest f for 1,000 scans, the seven's 154 |
|---|---|---|---|---|---|---|
| 1 | 3.8 (3.3 to 121) | 3.8 (3.4 to 7.3) | 40 (34 to 811) | 40 (36 to 75) | 0.017 (0.016 to 0.099) | 0.017 (0.016 to 0.024) |
| 3 | 5.8 (4.9 to 177) | 5.7 (5.1 to 10.9) | 59 (51 to 1,011) | 59 (53 to 110) | 0.021 (0.019 to 0.121) | 0.021 (0.020 to 0.029) |
| 5 | 6.4 (5.5 to 194) | 6.4 (5.7 to 12.2) | 66 (57 to 1,064) | 65 (59 to 121) | 0.022 (0.020 to 0.128) | 0.022 (0.021 to 0.031) |
| 10 | 7.0 (6.0 to 210) | 6.9 (6.2 to 13.3) | 71 (62 to 1,107) | 71 (64 to 132) | 0.023 (0.021 to 0.134) | 0.023 (0.022 to 0.032) |
| 20 | 7.3 (6.3 to 219) | 7.3 (6.5 to 13.9) | 75 (64 to 1,130) | 74 (67 to 138) | 0.024 (0.022 to 0.137) | 0.024 (0.022 to 0.033) |

So to be worth 1,000 scans, the pool's populations' means must spread about their centre by an SD of at most
0.017 (one population) to 0.024 (20) of a person's SD. That puts the pool's mean within sqrt(r / N) of a
person's SD (RMS) of the named population's mean, whatever the number of populations: 0.024 (0.022 to 0.140)
over the 704 cells, the same figure as the largest f at which an unlimited meta-analysis matches 2,000 scans,
since the population term then equals the 2,000 CTs' own sampling variance.

## B. How far the studies disagree (between_studies.py, between_studies.json)

| measure | cells | studies (median) | person SD | SD between studies | f, sampling error kept | f, sampling error taken out |
|---|---|---|---|---|---|---|
| lower endplate area (EPAl) | 6 | 3 | 37.60 mm2 | 66.18 mm2 | 1.85 | 1.83 |
| lower endplate depth (EPDl) | 14 | 4 | 2.48 mm | 1.43 mm | 0.66 | 0.59 |
| lower endplate width (EPWl) | 5 | 3 | 3.15 mm | 3.10 mm | 0.91 | 0.86 |
| pedicle height (PDH) | 12 | 3 | 1.81 mm | 0.34 mm | 0.22 | 0.00 |
| pedicle sagittal angle (PDIs) | 14 | 3.5 | 8.37 deg | 3.63 deg | 0.30 | 0.06 |
| pedicle width (PDW) | 14 | 4 | 2.32 mm | 1.06 mm | 0.37 | 0.24 |
| canal depth (SCD) | 5 | 3 | 2.15 mm | 1.31 mm | 0.75 | 0.69 |
| canal width (SCW) | 5 | 3 | 3.05 mm | 1.11 mm | 0.31 | 0.11 |
| superior facet angle to the sagittal plane (Ss) | 4 | 3 | 20.01 deg | 10.41 deg | 0.57 | 0.49 |
| posterior body height (VBHp) | 7 | 4 | 3.57 mm | 1.64 mm | 0.57 | 0.49 |
| all | 86 | | | | 0.49 | 0.39 |

Each row gives medians over its cells. f with the sampling error taken out subtracts the error a study of 12
specimens would carry. The comparison tables do not print the earlier studies' counts, and where those held more
than 12, less sampling error is in the spread than is taken out, so f is the low side. It also runs low for the
paired measures (PDH, PDW, PDIs and Ss, 44 of the 86 cells): the SD of a left-right mean is
s sqrt((1 + rho) / 2), at most the mean of the two sides' SDs used here, so the error taken out there is too
large. At a left-right correlation of 0.8 the median over the 86 cells would be 0.40 or 0.42 (in single-side or
bilateral units), and at 0.5 it would be 0.42 or 0.44 (verify/paired_sd.py).

The spread over groups of cells, f with sampling error taken out (between_studies.json's summary):

| cells | count | median f (quartiles) | cells at 0 | above 0.3 | pooled, weighted by df | pooled, unweighted |
|---|---|---|---|---|---|---|
| all, as published | 86 | 0.39 (0, 0.73) | 25 | 56% | 0.72 | 0.76 |
| the five the seven SPINEPS measures read: EPDl, EPWl, VBHp, SCD, SCW | 36 | 0.50 (0.29, 0.72) | 4 | 72% | 0.62 | 0.62 |
| the pedicles, which no SPINEPS measurer reads: PDH, PDIs, PDW | 40 | 0 (0, 0.45) | 21 | 33% | 0.48 | 0.46 |
| all, without EPAl | 80 | 0.35 (0, 0.66) | 25 | 53% | 0.55 | 0.55 |
| all, also without Liu's cervical depths | 80 | 0.29 (0, 0.60) | 27 | 48% | 0.53 | 0.52 |
| all, also without Scoles's and Cotterill's thoracic depths | 78 | 0.28 (0, 0.52) | 27 | 45% | 0.51 | 0.49 |
| all, also without Ss | 74 | 0.27 (0, 0.49) | 27 | 43% | 0.50 | 0.49 |
| the five, without those depths | 34 | 0.35 (0.23, 0.62) | 6 | 56% | 0.53 | 0.52 |

The pooled figures average f^2 over the cells, weighted by each cell's degrees of freedom (its studies less one) or
not, and take 1/12 out. The median sits below them for two reasons. Each cell's f rests on 2 to 5 degrees of
freedom (45 of the 86 cells on three means) and 25 cells are cut to 0, so a median of them runs low: with every
study at 12 specimens, a true common spread of 0.39 gives a median of about 0.31, and a median of 0.39 needs a true
common spread of about 0.48, or about 0.53 if the earlier series held 50 (verify/median_bias2.py). That closes only
part of the gap to 0.72. The rest is that a mean of f^2 follows its largest cells: EPAl's 6 cells, 12 of the 229
degrees of freedom, carry 38% of the weighted sum of f^2, 52.2 of 136.2 (verify/epal_share.py, from
between_studies.json's cells), and without them the pooled spread is 0.55 (the row "all, without EPAl"), worth a
median of 3.9 scans over the 704 cells (part_a.json's median r, 1.172, over 0.55^2) against 2.3 at 0.72 (part A).
So the low end of the note's range, about 2 scans, rests on those 6 cells, whose earlier rows the papers attribute
to another definition (below); without them the range is about 4 to 16 scans. The zeros are mostly pedicle cells,
and the groups differ: the five measures the rule reads fit a common spread of 0.5 to 0.6 in both their median and
their share of cells at 0 (11%), while a common 0.4 gives a median of 0.34 (5 to 95%: 0.23 to 0.45) and a common
0.3 puts a third of the cells at 0; the pedicle cells fit 0 to 0.2 (verify/zeros_by_group.py). That is why the note
gives a range and names no value in it as the likeliest: the 0.48 to 0.53 above, worth medians of 5.1 and 4.2
scans, is what a median of 0.39 means only if every cell shares one spread, and these groups do not; no script
carried here estimates how the spread varies from cell to cell.

Two rows are left out whole (LEFT_OUT in between_studies.py), because the earlier studies measured something else
under the name:

- the thoracic transverse pedicle angle (PDIt). The thoracic paper (p900) says Berry's transverse-plane angles
  "appeared to be grossly incorrect (eg, at T2, Berry: 137.0, Zindrick: 17.5, present study: 17.9)". Without
  Berry no level of the row has three studies.
- the cervical body height (VBH). The cervical paper (p868) says the earlier heights were "the posterior wall
  height as observed from the lateral direction", 2 to 2.5 mm above Panjabi's posterior height in the
  midsagittal plane, and its present column restates his VBHp to the digit. It is now left out by name; before,
  it dropped only because no dimension table prints a VBH, so a rename would have added its 5 cells unseen.

The papers' own text attributes four more rows to another definition (DEFINITIONS in between_studies.py). They
stay in the 86 cells, which shift_profile.py reads, and the summary above leaves them out one after another:

- the cervical lower endplate area (EPAl), every study: "Our areas did not include the uncovertebral facet area;
  the values of Liu et al probably did" (p868), and Francis's areas equal the ellipse of his own depth and width,
  which the same page finds "an overestimate of the measured area by 10%". Liu's areas are 45 to 68% above
  Panjabi's.
- Liu's cervical lower endplate depths (EPDl): "probably measured at the centrum midheight instead of the lower
  end-plate" (p868).
- Scoles's and Cotterill's thoracic lower endplate depths: the depth "may be at the body mid-height" (thoracic
  p898).
- the lumbar superior facet angle (Ss), every study: earlier angles are "angles between the two intersection
  lines of the facet and sagittal planes made with the transverse plane (computed tomographic slice). This could
  account for the differences in the angle comparisons of Table 10" (facets p1309).

The papers attribute nothing else. The rest of the spread is part different populations and part definitions or
methods no text names, and the tables do not say how much is which.

## C. What naming needs (cadaver_power.py and shift_profile.py)

The exact rule is built on each kind of table and scored on the same 300 typical synthetic columns. The columns
carry the seven SPINEPS measures with their CT errors. A field is one run of 1, 3 or 9 consecutive bodies of a
column, whose place the rule names from those bodies' measures. Each of the 300 columns has 22 levels, C3 to L5,
and so holds 22, 20 and 14 such runs (bordercall's columns.fields): 6,600, 6,000 and 4,200 fields at 1, 3 and 9
bodies. Each cell gives the share named exactly, and in brackets its paired difference, in points, from a table
re-estimated from 2,000 people. The last two columns give how often the answers given at 0.99 are right. All
rules here are nominal; the predictive rows are in the .txt files. Each row is a mean over drawn tables: 8 for 12
people, 6 for 25 and 50, 4 for 100, 3 for 200, 2 for 500 and 2,000, and 4 for every other-population and
published-series row (part_c_table.py prints each row's count and table-to-table SD).

| the table the rule is built on | exact, 1 body | exact, 3 bodies | exact, 9 bodies | 0.99 right, 3 bodies | 0.99 right, 9 bodies |
|---|---|---|---|---|---|
| the generator's own | 48.6% | 73.6% | 96.4% | 99.80% | 99.77% |
| 2,000 people of the population named | 48.5% | 73.6% | 96.4% | 99.80% | 99.78% |
| 500 people | 48.2% (-0.4) | 73.2% (-0.5) | 96.1% (-0.5) | 99.76% | 99.77% |
| 200 people | 48.0% (-0.6) | 72.4% (-1.2) | 95.9% (-0.7) | 99.70% | 99.77% |
| 100 people | 47.0% (-1.6) | 71.6% (-2.0) | 95.5% (-1.0) | 99.60% | 99.66% |
| 50 people | 46.1% (-2.5) | 69.6% (-4.0) | 94.4% (-2.1) | 99.58% | 99.63% |
| 25 people | 44.2% (-4.4) | 65.3% (-8.3) | 91.7% (-4.9) | 98.62% | 98.78% |
| 12 people | 40.9% (-7.7) | 60.0% (-13.7) | 85.2% (-11.3) | 94.86% | 95.32% |
| another population, one shift of 0.5 SD per measure | 46.5% (-2.1) | 71.5% (-2.1) | 96.1% (-0.5) | 99.65% | 99.82% |
| another population, 0.2 SD level by level | 45.2% (-3.4) | 68.1% (-5.5) | 93.6% (-3.0) | 99.42% | 99.31% |
| another population, 0.3 SD level by level | 43.2% (-5.4) | 64.6% (-9.0) | 90.3% (-6.3) | 98.45% | 98.62% |
| another population, 0.5 SD level by level | 38.1% (-10.5) | 55.8% (-17.9) | 81.4% (-15.1) | 92.18% | 93.99% |
| the published series as they disagree, r = 0 | 45.1% (-3.5) | 70.3% (-3.3) | 95.5% (-1.1) | 99.39% | 99.81% |
| the same, r = 0.5 | 43.0% (-5.6) | 65.9% (-7.7) | 92.0% (-4.6) | 98.40% | 99.22% |
| the same, r = 0.8 | 39.5% (-9.1) | 61.9% (-11.7) | 90.2% (-6.4) | 97.78% | 98.53% |
| the same, r = 1 | 39.9% (-8.7) | 60.3% (-13.4) | 88.1% (-8.4) | 96.82% | 97.84% |
| the same, read harshly | 37.6% (-11.0) | 56.6% (-17.1) | 85.5% (-11.1) | 95.44% | 96.66% |

How to read it:

- **How sure the numbers are.**
  - The standard error of a share named exactly, clustered by column, is 0.5 to 1.1 points (exact_se_columns,
    0.52 to 1.06 in the JSONs).
  - For the published-series rows the tables drawn matter more. Their 4 tables differ by an SD of 0.4 to 3.9
    points (the next table), so from the tables alone a 4-table mean there is uncertain by up to 2 points (the SD
    over the square root of 4: 1.7 for r = 0 at 3 bodies, 2.0 read harshly). A difference between two readings
    is known more closely only when they share their draws, as the fresh tables below do.
  - The precision of a published-series row's 0.99 answers is uncertain from its 4 tables alone by 0.04 to 1.4
    points (the precision's table SD over 2, verify/part_c_table.log), and by more with the columns. Nor does
    that SE settle a call near 99%, since 4 tables can all fall on one side. The r = 0 row at 3 bodies sits more
    than two such SEs above 99% (99.39%, table SD 0.35, so an SE of 0.17; worst table 99.03%), yet over all 36
    r = 0 tables its 0.99 answers are right 99.06% of the time, 0.33 points lower, with 11 of the 36 below 99%:
    its 4 tables were drawn mild (below). The r = 0.5 row at 9 bodies sits about one SE above (99.22%, SE 0.21),
    and the 8 fresh r = 0.5 tables keep the promise there, narrowly (99.25%, 1 of them below). The order of
    r = 0.8 and r = 1 is not settled either: r = 0.8 loses 1.7 and 2.0 points less at 3 and 9 bodies and 0.4
    more at 1 body, on 4 tables each whose losses have table SDs of 0.9 to 2.5 points.
  - The table leaves out the 0.99 answers from one body. Its rows answer 43 to 76 of the 6,600 fields there at
    0.99 (means over their tables), about 1 field in 150 to 1 in 90, so one wrong answer moves a table's figure
    by about 1.3 to 2.3 points; the part_b_seven*.txt files under seven/ have them. So few answers cannot show
    that a table keeps the promise: the generator's own table is right on 47 of its 48 (97.92%), and a row that
    gets one or two of them wrong per table, or none, cannot be told from it. They can show the promise broken
    where a table gets several wrong. A table whose 0.99 answers were each right with probability 0.99,
    independently, gets 4 or more of 72 wrong with probability 0.006, 5 or more of 76 with 0.001, 6 or more of
    68 with under 0.0001, and 3 or more of 66 or 68 with about 0.03 (binomial, verify/one_body.py). So at 1 body
    12 people, about 4.5 wrong of 72 per table, break it, and so do 0.5 SD level by level, about 5.2 of 76, and
    the published series read harshly, about 6.6 of 68; r = 0.8 and r = 1, about 3.4 of 66 and 3.3 of 68, break
    it less surely.
- **People of the population named.**
  - The loss halves about every time the count doubles.
  - 12 people break the 0.99 promise at every width: at 3 and 9 bodies (94.86% and 95.32%), and at 1 body, where
    they are right 93.71% of the time, about 4.5 wrong of 72 answers per table, and a table keeping the promise
    gets 4 or more of 72 wrong with probability 0.006 (above). The worst of the 8 twelve-person tables is right
    only 92.4% of the time at 3 bodies.
  - From about 50 people the promise holds at 3 and 9 bodies on these 300 columns (99.58% and 99.63%, worst of 6
    tables 99.35% and 99.38%), counting the tables' spread and not the columns' error. bordercall's build-up study
    (schwingcheck/README.md, The build-up study) scores the first 200 of seed 97's scoring columns against the
    table as printed, itself right 99.54% of the time there, and counts the columns' error: it finds the seven's
    50-person 99.41% (standard error 0.32 points, counting the tables) too close to 99% to tell, while agreeing on
    what 50 people cost at 0.99, 0.22 points below the 2,000-person tables here and 0.13 below the table as
    printed there. Those 50 are drawn from the generator as typical
    columns with no size spread and no measurement error, which is not how a CT measures. A CT carries its error,
    so about 60 CTs carry the same sampling error on the means (50 r, r's median being 1.17 over the 704 cells and
    1.165 over the seven) and about 68 on the SDs (1 + 49 r^2), once the error's variance is taken out of each SD
    (part A); simulated, 58 such CTs come within about half a point of the 50-person table (Tables from CTs,
    below). Real people differ in size, so a table from real CTs has to be estimated with the rule's size term
    taken out. That estimator, TODO.md item 5's, is not built yet; the tables from CTs below show what leaving it out costs.
- **Another population.**
  - A shift shared by every level of a measure, up to 0.5 SD, costs at most about 2 points; larger shifts were
    not run. It moves every candidate place nearly alike, and the rule's size integral takes up part of the rest.
  - A difference that changes from level to level is what costs. It costs 3 to 6 points at 0.2 SD, 5 to 9 at
    0.3 and 10 to 18 at 0.5. From 0.3 the 0.99 promise breaks at 3 and 9 bodies, and at 0.5 at 1 body too
    (above).
  - These tables carry no sampling error at all, so they are the best any meta-analysis of that population can
    do. They are also what a table from 2,000 CTs of another population would do.
- **The published series as they disagree.** shift_profile.py splits the disagreement in Panjabi's comparison
  tables into a shift and a level-by-level part. It does this over the five measures there that the seven
  SPINEPS measures read: the lower endplate's depth and width, the posterior body height, and the canal's depth
  and width. No comparison table gives the upper endplate, so the lower stands for it.
  - A study's shift is one value per measure and region (cervical, thoracic, lumbar). Its SD over the studies
    has a median of 0.59 person SDs over the 11 measure-and-region groups (0.30 to 1.29). Pooled by degrees of
    freedom, the way the level-by-level part is pooled, it is 0.75 over 37 degrees of freedom
    (shift_profile_seven.json). A median of 11 SDs from groups of 4 to 6 studies runs below their pooled value
    even when every group shares one SD. Refitting the split on the same cells with one shift SD of 0.75 for
    every group and the level-by-level part at 0.28, the median comes out at 0.91 of the pooled value on average
    and below it in 85% of 2,000 draws, and the observed 0.78 (0.59 over 0.75) lies at the 10th percentile, so
    one shared SD fits the groups (verify/median_shift.py). The rows above, which take the median, are the kind
    side; the pooled shift's tables are under Fresh tables, below.
  - What is left, level by level, is 0.28 SD pooled over the same groups, sampling error included.
  - Where one study gives a measure in both the thoracic and the lumbar region, its two shifts are correlated
    0.70 (16 pairs). The table rows draw them so. The cervical shift is drawn apart, since the cervical series
    are other studies, which leaves a step at C7 to T1.
  - The sampling error of 12 specimens, at most 1/12 of a person's variance per mean, is in both parts. How it
    splits between them turns on r, the correlation of one measure across a person's levels. At r = 0 nearly all
    of it falls in the level-by-level part, which then vanishes (0.57 shift, 0 level by level); each shift keeps
    1/(12 L) of it, L being its group's levels, 3.3 on average. At r = 1 it all falls in the shift (0.51 shift,
    0.28 level by level). The comparison tables cannot give r; the CTs would. These bounds treat Panjabi's person
    SDs as exact; with one SD per group in place of each level's own, the five's level-by-level part is 0 to 0.27
    in place of 0 to 0.28 (verify/pooled_sd_split.py).
  - The split takes 1/12 out of every study's mean, as if each earlier study held 12 specimens, the fewest the
    reading allows. With larger earlier series less sampling error is in the spread, and a level-by-level part is
    left even at r = 0 (Larger earlier series, below).
  - On the note's 4 tables r = 0 loses 1 to 4 points, but those tables were drawn mild (below). Over all its
    tables, 24 at 1 body and 36 at 3 and 9 bodies, it loses 4.4, 4.7 and 1.6 points: about what 25 people of the
    population named lose at 1 body (4.4), a little more than 50 lose at 3 bodies (4.0), and between what 50 and
    100 lose at 9 bodies (2.1 and 1.0). At 3 bodies its 0.99 answers are right 99.06% of the time, at the edge of
    the promise, with 11 of the 36 tables below 99%, so the promise is not shown to hold there; at 9 bodies it
    holds (99.62%, none below). From r = 0.5 up it loses about 5 to 13 points (7.7 to 13.4 at 3 bodies, about
    what 12 to 25 people lose there; at 1 body r = 0.8 and r = 1 lose more than 12 people do), and breaks the
    promise at 3 bodies: all 8 fresh tables at r = 0.5 fall below 99% there. At 9 bodies it breaks at r = 1
    (97.84%, table SD 0.27) and, narrowly, at r = 0.8 (98.53%, table SD 0.52, worst table 98.07%), both on the
    note's 4 tables alone; no fresh tables check either.
  - Read harshly, with every region's shift drawn apart and the sampling error left in both parts, it loses 11
    to 17 points.
  - Over all ten measures, the pedicles and facets with them, the level-by-level part is larger: 0.28 to 0.40 SD
    pooled with each level's own SD and 0.18 to 0.34 with one SD per group, so roughly 0.18 to 0.40, over 19
    measure-and-region groups. With each level's own SD its largest group is the cervical endplate area (EPAl,
    0.77), whose earlier rows the papers attribute to another definition. With one SD per group EPAl falls to
    0.32, sixth of the 19, and the lumbar pedicle width (PDW, 0.65) is the largest (verify/pooled_sd_split.py).
    The ten measures' shift is 0.48 to 0.56. Read as seen, the ten-measure tables lose 9 to 17 points
    (part_b_seven_observed-0.28_observed-0.4.txt). The record kind-0.28 takes the sampling error out of both
    parts at once, which the split shows cannot hold, so it is kept but not quoted.
  - With the rows the papers attribute to another definition left out (part B), the five's median shift is 0.53
    in place of 0.59 (0.44 in place of 0.51 with all of the sampling error taken out of the shift), their
    thoracic and lumbar shifts are correlated 0.88 over 12 pairs in place of 0.70 over 16, and their
    level-by-level part stays 0 to 0.28. Over the ten, with the area rows and the three depth rows out, the
    level-by-level part is 0.24 to 0.37 in place of 0.28 to 0.40, and the shift 0.40 to 0.49 in place of 0.48 to
    0.56 (verify/definitions.py). The rows above keep every cell; none was run with those rows left out.
- **Predictive tables.** Widening the table's SD raises the precision of the 0.99 answers by answering fewer
  fields, and leaves the share named exactly about as it was. For 12 people it stays below 99% at 3 and 9 bodies
  (97.28% and 96.67%); at 1 body it is right 95.16% of the time, on answers too few to read against 99%. For the
  published series on the note's 4 tables it keeps the promise at 3 and 9 bodies up to r = 0.8, narrowly there
  (99.26% and 99.19%), and falls just short of it at r = 1 (98.9% and 98.6%) and read harshly (98.3% and 98.4%). On
  16 fresh r = 0 tables at 3 bodies its answers are right 99.46% of the time (3 of the 16 below 99%), so there a
  predictive table keeps the promise that the nominal one misses on the same 16 (98.88%).

**The published-series rows, table by table.** The SD of the share named exactly from one of the 4 tables to the
next, in points (part_c_table.py, verify/part_c_table.log):

| reading | 1 body | 3 bodies | 9 bodies |
|---|---|---|---|
| r = 0 | 2.6 | 3.3 | 0.6 |
| r = 0.5 | 0.4 | 1.0 | 1.4 |
| r = 0.8 | 1.8 | 2.1 | 1.8 |
| r = 1 | 2.5 | 2.2 | 0.9 |
| read harshly | 1.7 | 3.9 | 3.3 |

At 3 bodies the 4 r = 0 tables lose 0.3 to 8.0 points each. They were drawn mild: their region shifts have a
pooled RMS of 0.46 against the reading's 0.57 (verify/draws.py), and four tables of that reading come out as mild
only 1.6% of the time (verify/summarise_runs.py).

**Fresh tables.** The reviewers drew more tables of the same readings; verify/summarise_runs.py reads their logs,
pooled_shift.py's through the log pooled_shift_read.py made from its saved results, and nothing was scored again
for this note. Losses are in points against the same 2,000-person table, the mean over the tables with the
table-to-table SD in brackets; then how often the 0.99 answers are right, with the tables below 99%. The
shared-draw tables give every reading the same random draws, scaled to its sizes.

| tables | 1 body | 3 bodies | 9 bodies | 0.99 right, 3 bodies | 0.99 right, 9 bodies |
|---|---|---|---|---|---|
| r = 0, the note's 4 | -3.5 (2.6) | -3.3 (3.3) | -1.1 (0.6) | 99.39%, 0 of 4 below | 99.81%, 0 of 4 below |
| r = 0, 8 shared-draw tables (crn.py) | not run | -4.46 (0.76) | -1.79 (1.01) | 98.90%, 3 of 8 below | 99.55%, 0 of 8 below |
| r = 0, 16 tables at other seeds (run.py) | -4.91 (1.85) | -5.51 (3.46) | -1.88 (1.19) | 98.88%, 7 of 16 below | 99.60%, 0 of 16 below |
| r = 0, 8 tables at seed 9090, 4 at 1 body (pooled_shift.py) | -3.13 (0.58) | -4.03 (2.75) | -1.26 (0.80) | 99.41%, 1 of 8 below | 99.64%, 0 of 8 below |
| r = 0, all of the above: 24, 36 and 36 tables | -4.38 (1.93) | -4.70 (2.89) | -1.64 (1.03) | 99.06%, 11 of 36 below | 99.62%, 0 of 36 below |
| r = 0.5, crn.py's 8 shared draws | not run | -8.65 (1.45) | -4.49 (1.20) | 98.18%, 8 of 8 below | 99.25%, 1 of 8 below |
| r = 0 with the shift pooled (0.736), crn.py's 8 (crn2.py) | not run | -7.11 (1.05) | -3.36 (1.87) | 97.58%, 7 of 8 below (worst 93.90%) | 99.06%, 4 of 8 below |
| r = 0 with the shift pooled (0.7355), the note's 4 and pooled_shift.py's 8, 4 at 1 body | -5.01 (2.55) | -6.17 (4.34) | -2.16 (1.40) | 98.73%, 6 of 12 below (worst 96.32%) | 99.59%, 0 of 12 below |
| r = 0 with the shift pooled, both: 20 tables at 3 and 9 bodies | the 8 above | -6.55 (3.40) | -2.64 (1.67) | 98.28%, 13 of 20 below | 99.38%, 4 of 20 below |
| one shift of 0.5 for every region, crn.py's 8 | not run | -1.81 (0.80) | not run | 99.56%, 0 of 8 below | not run |

- Over all 36 r = 0 tables at 3 bodies the loss is 4.70 points (SE 0.48), and the 0.99 answers are right 99.06%
  of the time, 11 of the 36 below 99%: at the edge of the promise, and not shown to keep it. At 9 bodies all 36
  keep it (99.62%).
- On crn.py's shared draws, r = 0.5 loses 4.18 points more than r = 0 at 3 bodies (SE 0.40) and 2.70 more at 9
  (SE 0.27); the pooled shift loses 2.64 more than the median shift at 3 bodies (SE 0.18) and 1.57 more at 9 (SE
  0.32). On pooled_shift.py's 12, each the same draw at both shifts, the pooled shift loses 2.39 more at 3
  bodies (SE 0.46), 0.95 more at 9 (SE 0.21) and 1.69 more at 1 (SE 0.30, over 8).
- The pooled shift is 0.753 over the five measures' 37 degrees of freedom, 0.736 at r = 0 once the sampling
  error is split (shift_profile_seven.json). Over all 20 of its tables r = 0 loses 6.55 points at 3 bodies (SE
  0.76) and its 0.99 answers are right 98.28% of the time, 13 of the 20 below 99%; at 9 bodies it loses 2.64
  and is right 99.38% of the time, 4 of the 20 below.
- pooled_shift.py draws its fresh tables as tables() draws the r = 0 reading, at a seed of its own, and makes
  each pooled table by scaling a median-shift table, which is exact since the level-by-level part at r = 0 is
  zero. Its run printed no log; pooled_shift_read.py reads the .npz files it saved.
- The pooled shift was run at r = 0 only. It is larger at every r (0.716, 0.703 and 0.695 at r = 0.5, 0.8 and
  1, against 0.54, 0.53 and 0.51; shift_profile_seven.json), so it would cost more there too; that was not run.

**Larger earlier series.** The split takes 1/12 of a person's variance out of every study's mean. If only
Panjabi's study held 12 and each earlier series held n specimens, less sampling error is in the level-by-level
mean square (0.0777 over 62 degrees of freedom, of which Panjabi's own means hold 17.6), and at r = 0 a
level-by-level part is left: 0.135 at n = 20, 0.174 at 30, 0.199 at 50, 0.217 at 100 and 0.233 for very large
series, which leave 0.233 to 0.279 at any r (verify/sampling_share.py). The note's 4 r = 0 tables, on the same
draws, with that part added (verify/r0_large.py), in points against the 2,000-person table; both the shift kept
at 0.57 and those mild draws favour the series:

| level-by-level part at r = 0 | 1 body | 3 bodies | 9 bodies | 0.99 right, 3 bodies | 0.99 right, 9 bodies |
|---|---|---|---|---|---|
| 0: earlier series of 12 (the r = 0 row) | -3.5 | -3.3 | -1.1 | 99.39% | 99.81% |
| 0.135: earlier series of 20 | -5.1 | -6.6 | -3.0 | 99.28% | 99.59% |
| 0.174: earlier series of 30 | -5.9 | -8.0 | -4.3 | 99.18% | 99.35% |
| 0.233: very large earlier series | -7.1 | -10.5 | -6.6 | 98.69% | 98.82% |

At 20 and 30 specimens the promise holds only narrowly, and single tables already fall to about 99% (worst 98.96%
and 98.88% at 3 bodies). With very large earlier series it breaks at 3 and 9 bodies at r = 0. Such series leave
a level-by-level part of 0.233 to 0.279 at any r (verify/sampling_share.py), so it should break at every r, but
only r = 0 was run. Where between 30 and very many specimens it starts to break was not run, and neither were
these rows on fresh draws, on which the first row loses 4.7 points at 3 bodies, not 3.3 (Fresh tables).

**Tables from CTs.** The reviewers drew tables from simulated CTs, each level's SD with the CT error's variance
taken out unless the row says otherwise (verify/ct_people.py, 6 tables at 3 bodies; verify/ct_tables.py, 3 to 6
tables at 1, 3 and 9 bodies), in points against the same 2,000-person table:

| table | 1 body | 3 bodies | 9 bodies | answered at 0.99, 3 bodies | 0.99 right, 3 bodies |
|---|---|---|---|---|---|
| 50 people measured exactly (the row above) | -2.5 | -4.0 | -2.1 | 16.7% | 99.58% |
| 58 CTs, no size spread (ct_people.py) | not run | -4.21 (SD 0.69) | not run | 17.6% | 99.41% |
| 58 CTs, no size spread (ct_tables.py) | -3.0 | -4.5 | -2.5 | 17.3% | 99.28% |
| 58 CTs, each person's own size divided out (ct_tables.py) | -3.2 | -4.2 | -3.0 | 16.8% | 99.33% |
| 58 CTs, the generator's size spread left in (ct_people.py) | not run | -6.08 (SD 0.90) | not run | 8.7% | 99.94% |
| 58 CTs, the size spread left in (ct_tables.py) | -4.2 | -6.2 | -4.6 | 8.4% | 99.97% |
| 50 CTs taken plainly, the error and the size left in (ct_tables.py) | -4.8 | -7.2 | -5.5 | 7.3% | 99.73% |

So about 60 CTs (50 r, a median of 58 over the seven's 154 cells, part A) come within about half a point of the
50-person table once the error's variance is out of each SD: with no size spread, the 58-CT rows fall 0.2 to 0.5
points short of it at each width. With each person's own size divided out, the best TODO.md item 5's estimator could do,
they fall 0.2 to 0.9 points short. With the size left in, the table answers about half as many fields at 0.99,
though those answers stay right.

## What it changes for TODO.md item 5 and the attached analysis

**TODO.md item 5** is item 4, "An estimator ready for the CT table", of the handoff document written for greg's
other account; bordercall does not hold that document, and it is not archive/HANDOFF.md, whose item 4 is
something else.

**Where the table comes from.** The calculation says to take each level's mean and SD, and the correlations,
from the CTs, measured the way the rule reads them (SPINEPS masks), with the CT error's variance taken out of
each SD and the rule's size term taken out of the table. The published series then do two jobs:

- a prior on those means, whose width is the spread between studies;
- a check of CT chords against caliper chords.

**How much the prior matters** turns on where the CTs come from. If they are of the population the rule will
name, 2,000 of them leave the prior little to do, since it is worth at most about 2 to 16 scans per level mean
(about 4 to 16 without the cervical endplate area's 6 cells, part B; 3 to 10 for the measures the rule reads); it
matters for a small CT set, or for a level that few scans hold. If they are pooled from a few other populations,
their means carry a population term too. All of the 0.39 being population, a pool from 3 to 20 populations is
worth 5.8 to 7.3 scans of the population named (medians over the 704 cells), about what the prior is worth; with a
tenth of its variance population, 59 to 75 (part A). What the CTs surely add then is that they are measured as the
rule reads, which takes the definitional and method share of the spread away, and the SDs and the correlations.

**What to take from the attached analysis.** Its Gaussian copula and LKJ prior fit the correlation part of
TODO.md item 5. The scale decides how to use them:

- An LKJ prior on the 32-by-32 correlation between measures can be estimated from 2,000 people.
- Keep the structure across levels as the rule's offset loading, or as a Kronecker product of a level matrix and
  a measure matrix.
- An unstructured 704-by-704 matrix (22 levels by 32 measures, 247,456 correlations) is far too many parameters
  for NUTS.

**What to leave out.** The analysis's other half, Chamfer-distance registration solved with L-BFGS-B, is
segmentation, and SPINEPS does that here.

**Where it overstates.** Its premise that anatomists' tables give exact marginals is the claim that part B
measures, and it does not hold.

## What is not known

- Whether the 2,000 CTs sample the population the rule will name, and how much of the spread between
  populations a pool of them would carry (part A); and how many of the census's SPINEPS masks count from C2,
  which only the full run will say. The pilot says it only for the rows it reads, at most 4,000 in the order of
  tier, collection and case id, stopping at 300 countable (SchwingNet grid/bordercall.sbatch and
  tools/bordercall_corpus.py; The answer).
- Whether the population named is exchangeable with those the studies sampled. The ceiling rests on it; were the
  population named at the studies' centre, there would be no ceiling (part A).
- The specimen counts of the earlier studies in Panjabi's comparison tables, which print means only. With more
  than 12 each, f is higher than part B gives, and the r = 0 end of part C loses more (Larger earlier series).
- How much of the spread is definitions and how much is populations, beyond the rows the papers themselves
  attribute (part B). Differences in body size between populations are partly absorbed by the rule's size
  integral (the shift rows of part C).
- r, the correlation of one measure across a person's levels. It decides how the comparison tables' sampling
  error splits between a shift and a level-by-level part, and so how far the published series fall short (part
  C). The CTs would give it.
- Panjabi's person SDs. Each comes from 12 specimens, so it is itself uncertain by about a fifth, and every f here
  with it. With one SD per measure-and-region group in place of each level's own, the ten-measure level-by-level
  part falls from 0.28 to 0.40 to 0.18 to 0.34 (part C).
- The upper endplate. No comparison table gives it, so part C lets the lower endplate stand for it.
- The CT errors. measures.py assumes them (1 mm for a length, sqrt(pi A / 2) mm2 for an area, 3 degrees for an
  angle), and the 1,700 cadavers become 1,184 or 1,917 with them doubled or halved (part A).
- The calipers' error. It is taken as zero, which favours the cadavers.
- Whether a caliper chord and a SPINEPS chord measure the same thing. bordercall's scanimport/README.md says the
  phantoms cannot show whether a mask's chords are Panjabi's on real bone (a whole-vertebra label includes the
  cortex, a segmenter can swell a body by a voxel, and the calipers sat on landmarks no mask names), and that no
  training-free CT chord measure in the sources it read has been validated in millimetres against calipers. A
  match needs any bias between the two within about 0.06 mm (part A).

## How to rerun

From a bordercall checkout holding the pool of 32 measures (pull request 15 or later), with the Python that has
its packages, in this folder:

    python3 -I between_studies.py --bordercall PATH --out between_studies.json
    python3 -I shift_profile.py between_studies.json --out shift_profile.json
    python3 -I shift_profile.py between_studies.json --measures EPDl EPWl VBHp SCD SCW --out shift_profile_seven.json
    python3 -I cadaver_power.py --bordercall PATH --out DIR --part-a-only    # part_a.json alone, in seconds
    python3 -I cadaver_power.py --bordercall PATH --out DIR --columns 300      # every row, about 20 minutes on 4 CPUs
    python3 -I cadaver_power.py --bordercall PATH --out DIR --columns 300 --arms seven-r0 seven-r1   # some rows
    python3 -I part_c_table.py DIR/part_b_seven*.json > verify/part_c_table.log   # this note's: DIR is seven

The rows of part C came from one run without --arms, before the disagreement arms were added, and four runs with
it (the part_b_seven*.json files): observed-0.28 and observed-0.4; kind-0.28; kind-0.28 with seven-seen and
seven-kind; and seven-r0 to seven-r1. A row is the same either way, since every table is drawn in the same order
and a run with --arms only leaves some out: kind-0.28 came out the same to the digit in two runs. The observed run
used an earlier cadaver_power.py, whose settings have no thoracic_lumbar key, and the current code gives its
3-body row to the digit (verify/r_arms_w3.log). The option --measures pool, all 32 measures at once, was not run
here.

The checks under verify/ run from this folder, with D the synthetic_spine data folder
(spine-program/synthetic_spine/data) and BC a bordercall checkout. These were run for the note, each in seconds to
a minute, and wrote the logs beside them:

    python3 -I verify/count_series.py D > verify/count_series.log
    python3 -I verify/series_totals.py D > verify/series_totals.log
    python3 -I verify/recorded_counts.py D BC > verify/recorded_counts.log
    python3 -I verify/per_cell.py D BC > verify/per_cell.log
    python3 -I verify/worth_real.py D BC > verify/worth_real.log
    python3 -I verify/worth_real.py D BC "Bonczar 2024" > verify/worth_real_no_bonczar.log
    python3 -I verify/extremes.py BC > verify/extremes.log
    python3 -I verify/definitions.py between_studies.json > verify/definitions.log
    python3 -I verify/pooled_sd_split.py between_studies.json > verify/pooled_sd_split.log
    python3 -I verify/paired_sd.py between_studies.json > verify/paired_sd.log
    python3 -I verify/sampling_share.py between_studies.json > verify/sampling_share.log
    python3 -I verify/median_bias2.py between_studies.json > verify/median_bias2.log
    python3 -I verify/zeros_by_group.py between_studies.json > verify/zeros_by_group.log
    python3 -I verify/epal_share.py between_studies.json seven/part_a.json > verify/epal_share.log
    python3 -I verify/one_body.py seven/part_b_seven*.json > verify/one_body.log
    python3 -I -B verify/draws.py BC seven-r0 4102 > verify/draws.log
    python3 -I -B verify/median_shift.py between_studies.json 0.753 0.279 > verify/median_shift.log
    python3 -I -B verify/pooled_shift_read.py BC R/fresh_w1.npz R/fresh_w3.npz R/fresh_w9.npz \
        > verify/pooled_shift_read.log
    python3 -I verify/summarise_runs.py seven/part_b_seven.json verify > verify/summarise_runs.log

R is a folder of its own that holds pooled_shift.py's .npz files, which this note does not carry (below); not this
folder, where run.py's header command writes .npz files of the same names.

The simulations under verify/ (crn.py, crn2.py, run.py, run_rule.py, run_jobs.py, ct_people.py, ct_tables.py,
r0_large.py and pooled_shift.py) are the reviewers' part C runs, copied with their logs and not run again for the
note. Each script's first lines give the command that made its output, and summarise_runs.py reads those logs.
They import this folder's cadaver_power.py, whose tables() draws as it did when they ran (verify/draws.py gives the
same draws). Their .npz outputs, up to 1.5 MB each, were left out. Only pooled_shift.py printed no log of its
tables, so pooled_shift_read.py reads its three .npz files (fresh_w1, fresh_w3 and fresh_w9, 1.0 to 1.5 MB) into
pooled_shift_read.log, which gives that reviewer's figures (6.17 points and 98.73% at 3 bodies at the pooled
shift); without those files, pooled_shift.py makes them again. median_shift.py refits the split only and scores
no rule, so it was run for the note, in seconds.

## Files

- README.md, this note; handoff-item4.md, the paragraph written for item 4 of that handoff document (TODO.md item
  5 here).
- cadaver_power.py, parts A and C: seven/part_a.json, and the part_b_seven*.json and .txt records of part C under
  seven/. between_studies.py, part B: between_studies.json. shift_profile.py, part C's split:
  shift_profile.json over the ten measures and shift_profile_seven.json over the five. part_c_table.py, part C's
  table with each row's tables and the table-to-table SDs of its share named exactly and of its precision, into
  verify/part_c_table.log.
- seven.log, seven_arms.log, seven_r.log, observed.log and kind.log: what the five part C runs printed. Their
  first part is part A as it stood before this rewrite, which seven/part_a.json replaces.
- corrections.md: an earlier copy of the corrections list, left as it was below a first line that says the list
  above replaces it; its "item 4" is TODO.md item 5 here.
- verify/: the checks behind the figures, with their logs. Each is copied from a reviewer's folder, or
  epal_share.py from an earlier fix's, with its paths made arguments (its first lines say what changed), except
  summarise_runs.py, written for the note; and part_c_table.log is the output of this folder's part_c_table.py:

| script | log | what the note takes from it |
|---|---|---|
| count_series.py | count_series.log | 27 and 13 series in synthetic_spine's two tables, 39 distinct, Bonczar 2024's meta-analysis among them; at most 13 in a cell |
| series_totals.py | series_totals.log | 15 cadaveric or skeletal series by the tables' cohort columns, 1,163 recorded specimens, three with no count |
| recorded_counts.py | recorded_counts.log | cadaveric specimens per cell and their worth at f = 0; every series' count per cell, specimens and people, 22 to 4,241 with Bonczar's pooled 1,481; 29 cells with a series beside Panjabi's and 675 with his alone, worth 14 |
| per_cell.py | per_cell.log | each cell's series, 776 pedicle cadavers with Zindrick at 41, and the series' own spread, 0.87 (0.42 to 1.94) over 28 cells |
| worth_real.py | worth_real.log, worth_real_no_bonczar.log | the recorded series' worth at f = 0, 0.39 and 0.87, each series taken as exact and one with no count as 12; and the same with Bonczar 2024 left out |
| extremes.py | extremes.log | the cells at the ends of part A's ranges; 396, 132 and 176 cells by kind |
| definitions.py | definitions.log | the median and the splits with the definition rows left out |
| pooled_sd_split.py | pooled_sd_split.log | the level-by-level part with one SD per group: 0.18 to 0.34 over the ten, 0 to 0.27 over the five; EPAl's 0.77 and 0.32, and PDW L's 0.65, the largest with one SD per group |
| paired_sd.py | paired_sd.log | the median at left-right correlations of 0.8 and 0.5 |
| sampling_share.py | sampling_share.log | the level-by-level part at r = 0 for earlier series of 6 to very many specimens; Panjabi's 17.6 of 62 degrees of freedom |
| median_bias2.py | median_bias2.log | the median a true common spread gives: about 0.31 for 0.39, and 0.39 for about 0.48 |
| zeros_by_group.py | zeros_by_group.log | the common spread the five and the pedicles fit |
| epal_share.py | epal_share.log | EPAl's 6 cells, 12 of the 229 degrees of freedom, carrying 38% (52.2 of 136.2) of the df-weighted sum of f^2; the pooled spread 0.72 with them and 0.55 without, worth medians of 2.3 and 3.9 scans over the 704 cells |
| one_body.py | one_body.log | every part C row's 0.99 answers at 1 body per table and how many are wrong, with the binomial chance that a table keeping the promise gets that many wrong: 0.006 for 12 people's 4 of 72 |
| draws.py | draws.log | the region shifts of the note's 4 r = 0 tables, pooled RMS 0.46 |
| part_c_table.py, in the folder above | part_c_table.log | each part C row's tables, and the table-to-table SDs of its share named exactly and of its precision |
| median_shift.py | median_shift.log | the median of the five's 11 shift SDs under one shared SD: 0.91 of the pooled value on average, below it in 85% of draws, the observed 0.78 at the 10th percentile |
| crn.py, crn2.py | crn_a_w3.log, crn_b_w3.log, crn_c_w9.log | the 8 shared-draw tables at r = 0, r = 0.5, the pooled shift and one shift for every region |
| run.py, run_rule.py | orig_w3.log, fresh_w1.log, fresh_w3.log, fresh_w9.log, fresh_pred_w3.log | the note's 4 r = 0 tables again, and 16 at other seeds, nominal and predictive |
| run_jobs.py | r_arms_w3.log | the note's own r and observed-0.28 tables at 3 bodies, table by table |
| ct_people.py | ct58_w3.log, ct58size_w3.log | 58 CTs without and with the size spread |
| ct_tables.py | ct_run1_w3.log, ct_run2_w3.log, ct_run3_w9.log, ct_run4_w1.log | CT tables at 1, 3 and 9 bodies: the error out, the size left in, plain, each person's size divided out |
| r0_large.py | run1_base_lbl0.233.json, run2_lbl0.174_lbl0.135.json | the r = 0 tables with the level-by-level part that larger earlier series leave |
| pooled_shift.py, pooled_shift_read.py | pooled_shift_read.log, read from the run's .npz files | the note's 4 r = 0 tables and 4 to 8 fresh ones, each at the median shift and at the pooled shift 0.7355 |
| summarise_runs.py | summarise_runs.log | every part C figure above from those logs: means, table SDs, tables below 99%, paired differences, the totals over all r = 0 tables, the 1.6% chance |
