# Round 3: the review after the data fixes

Source: thread "Plan clinical reread next steps", project symphony_2, 2026-10-29, on the branch of pull request 39 at
6f51947 (the round-2 data fixes applied, the comparison rerun). Confidential, like the rest of this repository.

Four independent readers, one lens each, told to report only what they had reproduced: the data rules of
tools/series.py against the readings and cohorts files; the counts and statistics (every series' n against its
cohort's people, the pooling, the halving, the record); the page against the record and the notes that quote it;
and each fix of 3aff843's findings against the paper's own page, trying to refute it. What they found, and what
was done:

## Refuted

Nothing. Every rule the fixes added holds against its paper's page; three of their comments were corrected: Kunkel
2011's twelve bodies a level is an inference from Fig. 1a, not a stated count (six a disc is stated); Tan 2004's
Table 1 spans pp. 140 to 141; Olsewski 1990's Table III footnote is on p. 545.

## Found and fixed

1. Olsewski 1990's pedicle counts were halved before the sexes were pooled, so the pooled means were weighted by
   people rounded up, not by the printed pedicles (up to 0.035 mm, 6 percent of an SD; 14 cells in the
   comparison). The count now stays as printed while the sexes and sides are pooled, and the series written
   carries half of it (series.py halve_pedicles). Found by two readers.
2. The halving split Olsewski's Part 3 CT cell at L2 into two sex series, one of one man, which cannot pool, and
   tools/cross_naming.py let both into the transport since it asked for an SD but no count; Duman 2026's six age
   bands with no n entered the same way. The transport now asks for a count of two or more, as the pools do. (With
   fix 1 that L2 cell pools again, to one series of four people, three women and the man, which passes the rule
   and is in the transport, at L2 to L5; round 4 found this item said otherwise. The rule keeps out Duman's bands.)
3. An n printed for a measure at one level stood for every level of that measure (Olsewski's caudad counts at L5
   for L1 to L3), and a count printed for a measure stood as its n (Krag 1988's bin counts, once the level
   joined the key). printed_counts now takes an n alone, at the cell's level or at none.
4. Olsewski 1990's cephalad and caudad transverse angles are groups chosen by the measure's own sign, which the
   docstring already called no population; 35 series, none in the comparison (vs_panjabi differs), make no series
   now (NOT_POPULATIONS).
5. Cizmic 2023's reading spelled a quoted source two ways, so the quoted study made two series at L1 and L5; one
   spelling now.
6. The docstring said the cohort's people stand in for any series with no count; the code gives them only to a
   series of both sexes, which is right (Duman 2026's sex and age bands). The docstring says so.
7. Two stale sentences: HANDOFF.md said round 2's data findings waited; measures.md 3.5 stated as fact which
   end-plate row Panjabi printed twice.

data/series.csv: 4,116 to 4,077 series. The comparison and the page were rerun after these fixes.

## Open, no change made

- Shin 2024's Tables 4 and 5 captions call their means adjusted for weight, height, BMI and ethnicity or sex;
  the mapping read them as raw because the sexes average to Table 2's. If they are model estimates they are the
  Griffith 2016 class. Disc heights are outside Panjabi's measures, so nothing in the comparison depends on it; a
  reader of the paper settles it.
- Bach 2019's decade-80 figure point stays as a series with no n: Table 1 counts nobody at 80 but the Discussion
  names the group.
- Zindrick 1987's printed N counts studies (films and CT examinations), one vertebra each, with no number of
  people in the paper; the pools weight it by studies.

## Checked and found clean

Every series' n is at most its cohort's people; no both-sex mean lies outside its sexes' and no plain side
outside its sides' in any table; the SE-to-SD conversion reaches Tan 2004 alone; the pooled-sex and averaged-side
formulas and the DerSimonian-Laird pool are as documented; every rule's entries hit rows, none silently; every
cell of the disagreement table that moved between the old and new records traces to a round-2 fix; the page
reproduces from the record byte for byte and every number the notes quote from it is current.
