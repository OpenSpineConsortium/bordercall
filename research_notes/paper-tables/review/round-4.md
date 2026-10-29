# Round 4: the review after round 3

Source: thread "Plan clinical reread next steps", project symphony_2, 2026-10-29, on the branch of pull request 39 at
a92f4dc (round 3's fixes applied, the comparison rerun). Confidential, like the rest of this repository.

Two independent readers, told to report only what they had reproduced: one over the data rules of tools/series.py
against the readings and cohorts files, every series' count, and the question round 3 left open on Shin 2024; one
over the page, the record and the notes that quote it, with the question why the transport's by-paper rows moved
broadly between round 2's record and round 3's. Both reproduced data/series.csv and the page byte for byte first.

## Refuted

Nothing. Round 3's fixes hold; one of its sentences was wrong (item 7 below).

## Found and fixed

Nothing below moves a number of the comparison: no series among Panjabi's measures with a same or close definition,
an SD and a count changed. The record changed through item 1 alone.

1. The transport seeded each series' draws by its place in the sorted list of series, so a series added or dropped
   redrew every series after it alphabetically: round 3's eight dropped series moved 125 of the record's 160
   by-paper rows with no change in those series' inputs, Gilad 1985's three-body row by six points. The reader
   showed it by rerunning one series at its old and its new place and reproducing each record exactly. Each
   series' stream now comes from a digest of its id (cross_naming.stream_of), so the record depends on no other
   series; this changes every drawn number once more, and the page says that a by-paper row at 200 fields a place
   carries sampling noise of several points, which these moves measured.
2. Bach 2019's Table 1 counts each decade and sex as "decade 10" to "decade 70" where Tables 2 to 5 name the same
   people First to Seventh Decade, so the paper's printed counts reached none of its 504 decade cells, which stood
   as sex series with no n where the sexes should have pooled: one spelling now (REGROUPED), 252 pooled series
   with the paper's counts in place of 504 without. Twomey 1985 bounds its young adults three ways (18-35, 20-36,
   20-35), the same class: one group, so 24 a sex reaches its 25 series. Disc heights and foramina are outside
   Panjabi's measures, so the comparison does not see either.
3. Shin 2024's Tables 4 and 5 are estimated marginal means of a two-way ANCOVA adjusted for weight, height, BMI and
   ethnicity or sex (Methods 2.2, p. 3; the captions, p. 4), the Griffith 2016 class: the sex pairs averaging to
   Table 2 proves nothing, since equal groups make an ANCOVA's marginal means average to the raw grand mean by
   construction. Both tables make no series now (NOT_POPULATION_TABLES); Table 5 had made 60, none of Panjabi's
   measures.
4. A subject count printed at one level stood for the subgroup as a whole (Robertson 2000's 20 sides of S1 beside
   its 10 specimens, dropped only because the set then held two values; Hou 1993's 40 at L5 under a group no
   series carries): a count at a level now feeds that level alone. Mitra 2002's quoted Olsewski radiograph series
   gain their 49 by it, since the L5 counts no longer spoil the subgroup's.
5. A level's count printed in every table of a cohort alike now reaches a mean the text gives (Krag 1988's Results
   means at T9, T12 and L5, which took the cohort's 41 spines for the level's 14, 24 and 20; none has an SD).
6. halve_pedicles halved any Olsewski 1990 series whose count came from a cell; every such cell is printed for both
   sides, so nothing changed, but a one-side cell counts people, and the halving now asks the side.
7. Three readings spelled a quoted source two ways (Ahmed 2019's Alam, Arockiaraj 2025's Makino Takahiro, Yu 2015's
   Marchesi), each spelling on a measure of its own, so no cell doubled; one spelling each.
8. Stale text: HANDOFF.md's 209 paper-measure pairs are 208 since round 3; two READMEs said two review rounds; the
   transport's docstring said its streams were independent of the process count alone; the n-of-two rule's
   docstring and round-3.md item 2 said Olsewski's L2 CT cell was kept out, where with round 3's own fix 1 it pools
   to one series of four people and is in the transport (L2 to L5); and results.py and cross_naming.py each parsed
   the "with" of a shared entry with a parser of its own, the page's stripping the clauses that rule a paper out
   and the record's not, harmless on today's entries and now one parser.

data/series.csv: 4,077 to 3,760 series (Bach 504 to 252, Shin 60 fewer, Twomey 25 to 20, the quoted spellings).
The comparison and the page were rerun after these fixes.

## Open, no change made

- Arockiaraj 2025's reading names "Tall et al. [11]" on six rows and "Tall et al. [23]" on twelve, where reference
  11 is Olsewski in the same reading; a reader of the paper settles which number is the misprint. Its Discussion's
  joint statement of Olsewski and Zindrick at L1 stands as a cohort of its own beside Table 3's Olsewski row.
- Tan 2004's and Zindrick 1987's signed pedicle angles, mirrored to one convention, lie lateral where Panjabi's are
  medial: a disagreement between papers the mapping calls same or close, a reader's question and not a rule's.
- Bach 2019's decade-80 figure point and Zindrick 1987's studies as the unit stay as round 3 left them.

## Checked and found clean

Every series' n is at most its cohort's people; no both-sex mean lies outside its sexes' but Hou 1993's T9, which
MISPRINTS handles; round 3's pooled-then-halved arithmetic reproduced by hand; the n-of-two rule removes Duman
2026's 24 sex-by-age series and nothing else; the level-keyed counts serve Gilad 1985 and Zindrick 1987 and the
measure-keyed count wins for no series; every Olsewski transverse angle carries one of the eight no-population
groups; no text series sits beside a table series of the same cell; SYNTHESIS.md points 5 and 7, measures.md 3.5
and the end-plate note quote the round-3 page exactly; every cell of the record that moved between round 2's
record and round 3's traces to a round-3 fix or to the seeding of item 1; the sharing table's citations match the
prose; every transport series' first record row is width 1, as the page assumes.
