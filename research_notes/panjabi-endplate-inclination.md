# Panjabi's end-plate inclinations at L1 to L5: which printed rows are the original

Status, 2026-10-29: checked by second readers and revised. In the thread "Finish the clinical reread", the draft of the 00:40 UTC checkpoint went to three second readers, one per part, each told to refute it: panjabi-own (section 2.1, 46 claims checked on page images rendered at up to 400 dpi), others (section 2.2 and the parts of 2.3 the PDFs in hand can test, 31 claims) and rule (sections 3 and 4 against the code in bordercall/schwingcheck, 34 claims). All three finished and none refuted the main conclusion. Of their 67 findings, 18 held as written and 49 asked for a change; some of the 49 overlap (the cervical upper-plate gap and "every independent L5 source" were each raised twice). This revision checked each of the 49 against the page image, the note or the code it cites, applied all 49, and skipped none, since each held on the check; where one held only in a narrower form, the narrower form is what is written. The optional fixes of seven findings that held were applied too (the non-consecutive repeat test, the borrowed depths, Kunkel 2011 at C7 only, why option 2 takes no stand-in, the ranks under option 1, the comparison that already leaves the angles out, and the stale script path). What still rests on one reader: section 2.3's database searches (PubMed, Europe PMC, Crossref, Semantic Scholar), which this machine cannot reach, and the later readers whose files are not in hand (Kunkel 2010's page, Breglia, Ceran, Bellina, Lavecchia). The verdict after the check: that the two rows are one set of numbers printed twice is near certain; that the set is cervical is probable but not proven, and rests mainly on Panjabi's own papers, since the outside evidence is close to neutral except at the L5 lower plate; the recommendation to drop both measures does not depend on the direction and stands, with its implementation corrected (section 3).

Source: thread "Finish the clinical reread", project symphony_4, 2026-10-28, revised there on 2026-10-29. Built from the three evidence lines that thread gathered: panjabi (Panjabi's own papers), others (other papers' values set on his footing) and errata (errata, letters and later readers). Their work folders (work/panjabi-own/, work/others/, work/errata/), the page crops the draft cited and the second readers' renders and scripts were all in that session's scratch space and are not kept. This note's own checks are panjabi-endplate-inclination-scripts/calibrate.py and runs.py beside it (run from the repository root: runs.py takes the long table's path, `runs.py schwingcheck/data/panjabi_long.csv`; calibrate.py takes none). Every Panjabi value quoted here was checked against the page images by two readers, and tan2004's against its text layer and its page images.

Paper ids and pages. Each citation gives the printed page, then the PDF page of the scan whose sha256 clinical-reread/tools/PAPERS.sha256 records. Panjabi's five scans, the same bytes, are kept in archive/bordercall/reference/papers/; the other papers are in clinical-reread/papers/, the same bytes as clinical-reread/tools/PAPERS.sha256 records.

- panjabi1991c, cervical, Spine 1991;16(8):861-869: printed 861 to 869 = PDF 1 to 9.
- panjabi1991t, thoracic, Spine 1991;16(8):888-901: printed 888 to 891 = PDF 1 to 4, 893 to 901 = PDF 5 to 13. Printed 892 is the separate scan panjabi1991t_p892, PDF 1.
- panjabi1992, lumbar, Spine 1992;17(3):299-306: printed 299 to 306 = PDF 1 to 8.
- panjabi1993f, facets, Spine 1993;18:1298-1310: PDF 1 to 13.
- tan2004, Tan, Teo and Chua, Eur Spine J 2004;13:137-146: printed 137 to 146 = PDF 1 to 10.

In bordercall's rule, endplate_incl is Panjabi's EPItu and endplate_lower_incl is his EPItl (bordercall/schwingcheck/mnemonics.py, lines 52 and 53). "The row" below means the 20 numbers in dispute: 2 measures x 5 levels x (mean, SEM), in degrees.

| Position | EPItu mean / SEM | EPItl mean / SEM |
|---|---|---|
| 1 (C3 or L1) | 2.7 / 0.77 | 4.0 / 0.84 |
| 2 (C4 or L2) | 3.5 / 1.5 | 2.1 / 0.4 |
| 3 (C5 or L3) | 1.7 / 0.43 | 2.7 / 1.1 |
| 4 (C6 or L4) | 4.7 / 1.1 | 2.7 / 0.69 |
| 5 (C7 or L5) | 2.2 / 0.54 | 1.8 / 0.42 |

panjabi1991c Table 2, p. 863 (PDF 3) prints it at C3 to C7, mean above SEM, with a C2 column before it (EPItu a dash, EPItl 4.2 / 1.2). panjabi1992 Table 2, p. 301 (PDF 3) prints it at L1 to L5 as mean +/- SEM.

## 1. The answer

The two rows are one set of numbers printed twice: cervical Table 2 at C3 to C7 (panjabi1991c) and lumbar Table 2 at L1 to L5 (panjabi1992) carry the same 20 numbers in the same order. That is near certain: two readers rendered both tables, no other lumbar series shares a run longer than two values with any cervical or thoracic series, and no lumbar series matches any cervical, thoracic or facet series in three or more positions at any alignment except these four (2.1). Which paper holds the original is probable but not proven: most probably the cervical, and if so Panjabi's lumbar paper prints no lumbar end-plate inclination at all.

- The cues that bear on direction lean cervical, each of them weakly: the cervical Results text describes the row (p. 864), while no lumbar text names it; the lumbar Methods text and tables were drafted on the cervical ones, down to a shared misprint and the same row templates; the one-decimal SEMs are native to the cervical EPI rows, C2 included, and foreign to the lumbar tables; the C2 to C3 step of the lower plate is typical of adjacent levels; and the block's SEMs fit cervical plates rather than lumbar ones.
- The C2 column, the C7/T1 and T12/L1 junctions and the acceptance dates do not decide it. Nothing in the papers excludes an early lumbar computation pasted into the cervical draft before November 1990.
- The outside evidence (2.2) is close to neutral, except at the L5 lower plate. There the two same-definition series in reach, tan2004 at 10.5 deg and Tan 2002 at about 12 by a back-out from bonczar2024's pool, sit far from the printed 1.8. So the direction rests mainly on section 2.1.

The authors' data, an erratum in the print issues or a lumbar publication by his group would settle it, and a same-definition series that found L5 lower end plates near 2 deg would reopen it. Section 3's recommendation, to drop both measures, does not depend on the direction; the advice to keep C3 to C7 as printed does.

## 2. The evidence

### 2.1 Panjabi's own papers

**One set of spines, one measuring frame.** All three papers measured the same twelve specimens with the same morphometer and origin; the preparations they print differ.

- panjabi1991t p. 890 (PDF 3): 12 spines from C2 to L5 were studied, and this paper reports 144 thoracic vertebrae (12 spines x 12 levels).
- panjabi1991c p. 861 (PDF 1): twelve fresh autopsy specimens, mean age 46.3 years (range 19 to 59), 8 men to 4 women. On p. 863 (PDF 3) it reports 72 vertebrae, C2 to C7 (12 x 6).
- panjabi1992 p. 299 (PDF 1): twelve specimens from the axis to the last lumbar vertebra, with the same age and sex summary. Its abstract counts 60 vertebrae (12 x 5).
- The lumbar Methods (p. 299, PDF 1) set the vertebra's frontal, transverse and sagittal planes by least squares from four points on the posterior wall, with the origin at the centre of the upper end plate. The cervical and thoracic papers describe the same morphometer and the same origin (p. 861, PDF 1; p. 888, PDF 1), and the cervical paper says it follows the thoracic paper's method (p. 861, PDF 1).
- The printed preparations disagree. Thoracic: rods 3.0 mm by 3.2 cm, soft tissue softened by boiling (p. 888, PDF 1). Cervical and lumbar: rods 2 mm thick (p. 861, PDF 1; p. 299, PDF 1). Facets: 2 mm rods for all 276 vertebrae of the same spines (p. 1299, PDF 2), which contradicts the thoracic 3.0 mm.
- The grants differ too: the thoracic, lumbar and facet papers cite NIH AR39209 (p. 888; p. 299; p. 1298, each PDF 1), the cervical AR30361 (p. 861, PDF 1). Neutral on direction.

**Where each paper deals with end-plate inclination.**

- Cervical (panjabi1991c).
  - Table 1, p. 863 (PDF 3) lists EPI as end-plate inclination, and the suffix t as the transverse plane.
  - The side view of Figure 1, p. 862 (PDF 2), draws EPItu and EPItl, and both plates' lines fall toward +Z, the anterior direction.
  - Table 2, p. 863 (PDF 3) prints the values.
  - Results, p. 864 (PDF 4): for C3 to C7 the text puts the upper plates' tilt from the transverse plane at 2 to 5 deg and the lower plates' at 2 to 4 deg. It says the upper-lower difference stays below 2 deg at every level, with no significant trend.
  - The text agrees with the table. Upper C3 to C7 runs 1.7 to 4.7, which rounds to 2 to 5, and lower 1.8 to 4.0, which rounds to 2 to 4. The stated C3-C7 scope correctly leaves out C2's 4.2. The differences per level are 1.3, 1.4, 1.0, 2.0 and 0.4.
  - Inference: C6's printed 2.0 is not below 2. The statement holds only if the unrounded means (4.65 to 4.75 and 2.65 to 2.75) differ by less than 2. A writer who said "less than 2" beside a printed 2.0 may have worked from unrounded data, which fits a text written from this row's source data better than one written from a pasted, rounded table. A weak cue.
  - Neither reader found more in Figure 2 (p. 865), the Discussion (pp. 866 to 868) or Table 7 (p. 868).
- Thoracic (panjabi1991t).
  - Table 3, printed p. 892 (p892 PDF 1) prints EPItu, EPItl (the label is misprinted as "EPIlt") and EPIt at T1 to T12. EPIt equals EPItu + EPItl in all 12 cells; both readers checked each one.
  - Results, p. 890 (PDF 3): inclination stays constant through the thoracic spine. The upper plate averages 1.7 deg and the lower 2.1 deg. The wedge angle is defined as the sum of the two and averages 3.8 deg. A radiographic side study found 3.9 deg, which the paper calls the average angular difference between the plates.
  - Inference: the 12-level means of the printed means are 1.70, 2.075 and 3.775.
  - Discussion, p. 898 (PDF 10) repeats 3.8 deg per vertebra and about 45.6 deg over the thoracic spine. Inference: 45.6 is 12 x 3.8, and the printed EPIt cells sum to 45.3.
  - Figure 3B, p. 891 (PDF 4) draws EPItu falling and EPItl rising toward +Z, which are opposite senses.
- Lumbar (panjabi1992).
  - Table 1, p. 301 (PDF 3) lists EPI, and Table 2 on the same page prints the two rows. No text names EPI or describes its values. The abstract says means and SEMs of angular dimensions of the vertebral bodies were obtained (p. 299, PDF 1), and "Angular Parameters" (p. 300, PDF 2) says each part's angles were taken between its best-fit plane and the anatomic planes; both imply EPI without naming it.
  - Figure 1, p. 300 (PDF 2) draws PDIt, PDIs and the end-plate depths but no EPI (both readers).
  - The Results "Vertebral Body" paragraphs, p. 301 (PDF 3), cover end-plate widths, depths, their ratio and areas only.
  - The pedicle Results (p. 302, PDF 4), Figures 2 to 4 (p. 303), the transition-zone Discussion (p. 304) and Table 6 (p. 305), which compares PDIs and PDIt but not EPI, say nothing about end-plate inclination (both readers).
  - The lumbar paper never says how the two angles combine.
- Facets (panjabi1993f): no end-plate data in any table or text (pp. 1298 to 1310, PDF 1 to 13).
- Inference: the cervical paper treats the two angles as a difference (|u - l| below 2 at every level) and draws the plates tilting the same way, while the thoracic paper treats them as a sum and draws them tilting opposite ways. Both call the angle between the plates a difference (p. 864, PDF 4; p. 890, PDF 3), so the contrast lies in the arithmetic and the figures, not in the wording. No EPI row prints a sign, though the pedicle rows do: cervical Table 4 gives PDItr -9.2, -8.6, -6.3 and PDItl -7.1, -6.5, -5.7 (p. 864, PDF 4). So the lumbar rows carry the cervical figure's convention, or none.

**The C2 column fits the cervical table.** Cervical Table 2's C2 column has 20 cells: nine measures with a mean and an SEM (18 cells) plus two ratios (2 cells).

- All 11 dashes fall on upper-end-plate measures or VBHp: EPDu 2, EPWu 2, VBHp 2, EPWu/EPDu 1, EPAu 2, EPItu 2.
- All 9 numbers fall on lower-end-plate measures: EPDl 2, EPWl 2, EPWl/EPDl 1, EPAl 2, EPItl 2.
- The EPI rows follow this split: EPItu is a dash and EPItl is 4.2 / 1.2 (p. 863, PDF 3; both readers).
- Inference: C2 has no upper end plate because of the dens.
- 4.2 is a mean nowhere else in the long table, the facet paper included (the second reader's numeric search of panjabi_long.csv).
- Inference: this shows the cervical EPI rows are whole and coherent. On its own it does not prove direction, since a copy that overwrote only C3 to C7 would have left C2 in place.

**The one-decimal SEMs belong to the cervical EPI rows.**

- In lumbar Tables 2 to 5, every SEM prints to two decimals except the four EPI cells 1.5, 1.1, 0.4 and 1.1: 4 of 130. Two-decimal examples are 1.10 and 49.00 in Table 2, p. 301 (PDF 3). All 25 lumbar ratios print two decimals as well.
- In the cervical tables, 5 of 179 SEMs print to one decimal, and all five are EPI cells: 1.5, 1.1, 1.2 (C2), 0.4 and 1.1. Both readers counted these.
- C2's 1.2 lies outside the repeated block. Every cervical EPI SEM of 1 or more prints to one decimal (two significant figures), and 0.4 has lost a trailing zero.
- One-decimal cells occur elsewhere, but not as lumbar SEMs: the cervical ratios PDHr/PDWr (1.3, 1.3, 1.1, 1.1, 1.1) and PDHl/PDWl at C3 (1.3) (Table 4, p. 864, PDF 4); thoracic Table 3's area SEMs and ratios, while its EPI SEMs keep their trailing zeros (T11 EPItl 0.60; p. 892).
- Inference: the format is native to the cervical EPI rows, C2 included, and foreign to the otherwise uniform lumbar tables. That leans weakly cervical. It is not by itself a mark of copying.

**The repeat is unique.**

- The first panjabi reader compared every row against every row at every alignment, forward and reversed, across statistics:
  - lumbar: 57 rows, 285 numbers (130 means, 130 SEMs, 25 ratios);
  - cervical Tables 2 to 6: 69 rows, 387 numbers and 27 dashes;
  - thoracic Tables 3 to 7: 72 rows, 844 numbers and 18 dashes.
- It found exactly 4 runs of 3 or more equal values: the lumbar EPItu means, EPItu SEMs, EPItl means and EPItl SEMs against the cervical ones, each 5 of 5. It also counted runs of two outside the repeat, 11 against cervical and 27 against thoracic, mostly 1.10 against a ratio of 1.1. These counts are that reader's and are not reproduced: its script was not kept and the long table holds no ratios. The second reader recounted the lumbar and cervical numbers, dashes and rows on the pages and agrees; it did not read thoracic Tables 4 to 7.
- I repeated the search on bordercall's long table (bordercall/schwingcheck/data/panjabi_long.csv, means and SEMs only) with panjabi-endplate-inclination-scripts/runs.py. It compared 52 lumbar series (one measure's means, or its SEMs, over its levels) against 131 cervical and thoracic series (64 and 67), forward and reversed: 52 x 131 x 2 = 13,624 comparisons. The second reader reran it and got the same counts.
  - Longest run 5: 4 comparisons, exactly the four EPI series at L1-L5 against C3-C7.
  - Longest run 2: 10.
  - Longest run 1: 522.
  - Longest run 0: 13,088.
  - No run of 3 or 4.
- The second reader also counted matching values at every alignment, consecutive or not, and this revision repeated that with a scratch script, not kept (Inference). Lumbar against cervical, thoracic and facet series, forward and reversed, gives 19,448 comparisons: 18,526 with no match, 876 with one, 42 with two, and only the four EPI series with five. The four cervical EPI series against thoracic and facet series give no comparison above two. So no near-copy broken by one cell exists, and no third table within the four papers holds the block.
- Inference: twenty numbers in order are not chance.

**The lumbar manuscript was drafted from the cervical one.**

- Inference, from setting the pages side by side: the lumbar Methods (p. 299, PDF 1) follow the cervical Methods (p. 861, PDF 1) nearly sentence for sentence. They share the specimen summary; the threaded rods of 2 mm diameter and 2.5 mm length; the three marker points (the cervical text calls them pin markers) and the morphometer; and the sentence that introduces Table 1 and Figure 1, with the cervical example of an uncovertebral facet turned into an articular facet.
- The shared rod length is very probably a shared misprint. The facet paper, on the same 12 spines, gives the rods as 2 mm thick and at least 2.5 cm long (p. 1299, PDF 2), and the thoracic paper gives 3.2 cm (p. 888, PDF 1). A shared error is stronger evidence of copying than shared true facts.
- The lumbar tables reuse the cervical row templates. Lumbar Table 2 (p. 301, PDF 3) lists EPDu, EPWu, EPDl, EPWl, VBHp, the two ratios, EPAu, EPAl, EPItu and EPItl in exactly cervical Table 2's order (p. 863, PDF 3). Thoracic Table 3 instead puts width before depth and adds an EPIt row (p. 892). Lumbar Table 4 (p. 302, PDF 4) likewise repeats cervical Table 4's row order (p. 864, PDF 4). Inference: a lumbar table drafted on the cervical one, with its last two rows never overwritten and its C2 column deleted, gives exactly the observed pattern.
- The thoracic Methods (p. 888, PDF 1) differ: rods 3.0 mm by 3.2 cm, and soft tissue softened by boiling.
- The lumbar paper calls itself the third and final paper of the series (p. 299, PDF 1). The cervical paper calls itself the second and points to the initial study in the same issue at p. 888 (p. 861, PDF 1).
- Acceptance dates: thoracic 18 July 1990 (p. 888, PDF 1), cervical 8 November 1990 (p. 861, PDF 1), lumbar 19 April 1991 (p. 299, PDF 1). These bound only the drafts. The cervical paper was printed in Spine 16(8) of 1991 (p. 864 header), after the lumbar acceptance (Inference: the eighth issue of a monthly volume), so its revision or proofs could postdate April 1991.
- Inference: building a later manuscript on an earlier one is the natural route for a block of cervical cells to reach a lumbar table. With the misprint and the templates this is a mechanism that leans cervical, not proof. No paper says when each region was digitized, so lumbar values could have existed by November 1990; an early lumbar computation pasted into the cervical draft, with the cervical Results text then written from it, is not excluded. A late, proof-stage paste into the cervical paper is unlikely, because the cervical Results sentence (p. 864) matches the row and would have had to be rewritten too.

**Continuity at the junctions mostly does not decide it.** Values are mean / SEM in degrees.

| Level | EPItu | EPItl | Source |
|---|---|---|---|
| T11 | 2.3 / 0.65 | 2.2 / 0.60 | panjabi1991t p. 892 (p892 PDF 1) |
| T12 | 2.2 / 0.79 | 1.8 / 0.32 | same |
| L1 as printed | 2.7 / 0.77 | 4.0 / 0.84 | panjabi1992 p. 301 (PDF 3) |
| C7 | 2.2 / 0.54 | 1.8 / 0.42 | panjabi1991c p. 863 (PDF 3) |
| T1 | 1.8 / 0.65 | 3.9 / 0.61 | panjabi1991t p. 892 (p892 PDF 1) |
| T2 | 1.7 / 0.32 | 1.9 / 0.67 | same |

- EPItu moves smoothly at both junctions: +0.5 from T12 to L1, and -0.4 from C7 to T1.
- EPItl jumps +2.2 from T12 to L1. But it also jumps +2.1 from C7 to T1 and falls -2.0 from T1 to T2, so steps of about 2 deg occur in the uncontested data.
- T12's means equal C7's, but their SEMs differ. Inference: a coincidence at one decimal.
- These two junctions are symmetric between the readings. One is not: C2 to C3 within the cervical table, EPItl 4.2 to 4.0 (p. 863, PDF 3). Inference from panjabi_long.csv: of the 13 undisputed EPItl means (C2, T1 to T12), none but C2 lies within 0.2 of 4.2 (the nearest is T1's 3.9), and 5 of the 11 adjacent thoracic steps are 0.2 or less. Read as cervical, 4.2 to 4.0 is a typical adjacent-level step. Read as lumbar, the printed 4.0 would be L1's and would land 0.2 from the genuine C2 by chance. A weak cue toward the cervical reading.

**The block's SEMs fit cervical plates.** Inference from panjabi_long.csv, weak and resting on assumptions.

- In the thoracic paper, the mean EPI SEM times the mean end-plate depth stays about constant: T1 to T6, 0.587 x 23.0 = 13.5; T7 to T12, 0.476 x 30.5 = 14.5.
- The block's mean SEM is 0.779. With the cervical depth (16.5 mm) the product is 12.8, which fits. With the lumbar depth (34.6 mm) it is 27.0, about twice the thoracic product. The thoracic relation would predict a lumbar SEM near 0.4.
- Caveats: this assumes the spread is driven by plate size; the regional biological spread is unknown; and the thoracic relation rests on two halves of six levels.

**What bordercall's archive says.**

- bordercall/TODO.md line 16 records the finding: lumbar-t2 rows 12 and 13 against cervical-t2 rows 19 to 22. It leaves the question to the owner, records no lean, and says the rule scores the lumbar values as printed.
- CONTRADICTIONS.md compares each paper only with itself, so it could not catch the repeat.

### 2.2 The other papers, on Panjabi's footing

**Footing.** All three points are Inference.

- Panjabi prints his EPI with no sign. If he averaged unsigned values per specimen, which no paper says, then within one sample the mean unsigned angle is at least the magnitude of the mean signed one. Across samples that does not hold: in the uncontested thoracic data Panjabi's mean sits below abs(Tan) at 9 of 12 levels on each plate (calibrate.py). So a signed source's absolute mean is a comparison, not a bound.
- Only tan2004, among the papers in hand, uses a definition like his (below). gilad1985 is a two-dimensional analogue built from corner lines, and the other sources give only a body wedge. bonczar2024's pool holds a second Tan series, Tan 2002, which is not in hand (below).
- Within one sample and one fitted-plane definition, a body's sagittal wedge cannot exceed EPItu + EPItl in size. For one specimen with both plane angles taken from a common reference, |s_l - s_u| <= |s_u| + |s_l| holds with no small-angle assumption, and the bound passes to the means. It does not carry over to other people's bodies or to wedges from corner heights. In Tan's own data the height wedge and the plane wedge differ by up to 5.6 deg (T1: -4.47 against -10.1) and by 1.5 to 3.8 deg at C3 to C7 (tan2004 pp. 140 to 141, PDF 4 to 5). So the wedge cap used below is a comparison, not a bound.

**tan2004, the one same-definition series in hand.**

- What was measured: C3 to L5 of 10 Chinese Singaporean cadavers, mean age 65.7 (range 56 to 77), cleaned, air dried and measured with a 3-D digitiser (p. 137, PDF 1). Its 220 vertebrae are 10 spines x 22 levels, C3 to L5 (Inference: n = 10 per level).
- Definition: its authors call their definitions similar to Panjabi's (p. 138, PDF 2). EPItu and EPItl are measured against a transverse plane perpendicular to the posterior-wall plane (Fig. 1, p. 138, PDF 2). That plane is set from three points, digitised a and b and the mean of c and d (p. 139, PDF 3), where Panjabi fits it by least squares from four (panjabi1992 p. 299).
- Signs: Tan names the sign in words, not its reference end (p. 143, PDF 7). Both cervical plates, positive in Table 1, are called angled cephalad, the lower less than the upper. The lumbar lower plate runs caudally at L1 to L2 (negative) and cephalad from L3 to L5 (positive). The thoracic plates are in opposite senses. So positive is cephalad and negative caudal, but the text never says which end of the plate is meant.
  - The others reader inferred that positive means the plate's anterior end lies caudal, which is the opposite of the most natural reading of "cephalad" (anterior end raised) and rests only on the height-wedge sign. Inference, rerun by the second reader: EPItl - EPItu agrees in sign with Tan's height wedge (atan of anterior minus posterior height over mean depth) at 21 of 22 levels, L4 a tie (-0.5 against 0.0), and the opposite convention would get every sign wrong. In size it matches at L1 (-4.4 against -4.5), L2 (-4.5 against -4.6) and L5 (3.6 against 3.9), but differs by 1.5 to 3.8 deg at C3 to C7 and by 2.4 to 5.6 deg at T1 to T4. The convention survives in sign, not in size, and plane wedges and height wedges are different measures.
  - I add, as Inference, that Tan's thoracic EPItu is positive and EPItl negative at all 12 levels, the opposite senses Panjabi's thoracic figure draws, while Tan's C3 to C7 are positive on both plates, the same sense Panjabi's cervical figure draws.
- SEM: defined as the SD over the sample size (p. 139, PDF 3), which leaves its meaning ambiguous. Its C3 and C4 upper-plate SEMs are 4.1 and 5.2, against 1.2 or less at every other level. Inference, n = 10: these give SDs of 13 to 16 deg if SD = SEM x sqrt(10), and 41 to 52 deg if SD = SEM x 10, both implausible beside means of 5.0 and 5.2.
- Values (Table 1, mean +/- SEM; C3 to C7 on p. 140, PDF 4; L1 to L5 on p. 141, PDF 5; the second reader checked all 20 cells and calibrate.py's thoracic inputs at 400 dpi):

| Level | EPItu | EPItl | Level | EPItu | EPItl |
|---|---|---|---|---|---|
| C3 | 5.0 +/- 4.1 | 3.3 +/- 0.5 | L1 | 1.8 +/- 0.4 | -2.6 +/- 0.4 |
| C4 | 5.2 +/- 5.2 | 3.5 +/- 0.7 | L2 | 3.4 +/- 0.4 | -1.1 +/- 0.2 |
| C5 | 7.1 +/- 1.2 | 2.7 +/- 0.3 | L3 | 1.9 +/- 0.3 | 1.8 +/- 0.1 |
| C6 | 5.8 +/- 0.6 | 4.2 +/- 0.4 | L4 | 3.7 +/- 0.6 | 3.2 +/- 0.6 |
| C7 | 5.8 +/- 0.8 | 5.1 +/- 0.5 | L5 | 6.9 +/- 0.9 | 10.5 +/- 0.8 |

**A calibration I added, from data nobody disputes.**

- Panjabi's thoracic rows are not in question. Their gap from Tan's thoracic magnitudes therefore shows how far two honest same-definition series sit apart.
- Gaps are Panjabi minus abs(Tan), in degrees (panjabi-endplate-inclination-scripts/calibrate.py). Thoracic values are panjabi1991t p. 892 (p892 PDF 1) and tan2004 pp. 140 to 141 (PDF 4 to 5).

| Comparison | Upper plate | Lower plate |
|---|---|---|
| Thoracic T1 to T12, uncontested | mean -1.08; -5.4 at T1, T2 to T12 within +/-2.3 | mean -0.88; range -2.0 to +1.0 |
| Row read as C3 to C7 | -2.3, -1.7, -5.4, -1.1, -3.6 (mean -2.82) | +0.7, -1.4, 0.0, -1.5, -3.3 (mean -1.10) |
| Row read as L1 to L4 | +0.9, +0.1, -0.2, +1.0 | +1.4, +1.0, +0.9, -0.5 |
| Row read as L5 | -4.7 | -8.7 |

All Inference:

- Read as L1 to L4, the row's raw gaps from Tan's lumbar values are small: the others reader found an RMS difference of 0.86 deg over the 8 cells and r = +0.89 for the upper plates, on only 4 points. But in the uncontested data Panjabi runs about 1 deg below Tan (mean gaps -1.08 and -0.88), while the L1 to L4 reading puts him above (+0.45, +0.70). With the thoracic offset taken out, positions 1 to 4 fit the two readings about equally: RMS 1.68 read as lumbar, 1.75 read as cervical (8 cells each).
- Read as C3 to C7, the upper-plate gap is larger on average than the thoracic one: mean -2.82 against -1.08. Per level, C5 (-5.4) and C7 (-3.6) exceed every thoracic gap but T1's; C3 (-2.3) equals T12's; C4 (-1.7) and C6 (-1.1) lie inside the thoracic range.
- At position 5 the lumbar reading sits far from Tan. The L5 lower-plate gap of 8.7 deg is four times the largest thoracic lower-plate gap (2.0) and 1.6 times the largest thoracic gap on either plate (5.4, T1 upper, where Tan's 7.2 is its own regional peak). The C7 reading's gaps are 3.6 and 3.3.
- Panjabi's thoracic means barely follow Tan's level pattern. Fitted on the uncontested thoracic data, Panjabi = 1.39 + 0.11 abs(Tan) for the upper plates (r +0.34) and 2.05 + 0.01 abs(Tan) for the lower (r +0.01). Extended to Tan's L5 lower plate of 10.5, the pooled fit predicts about 2.7 against 1.8 printed (residual -1.4 SD). That is an extrapolation beyond Tan's thoracic range, but it shows Panjabi does not follow Tan's large values (T1 upper: 1.8 against 7.2). So the calibration alone cannot turn the L5 gap into a contradiction.

**At L5, the lower plate separates the readings; the other measures do not.** The values are the others reader's (work/others/epi_values.csv, not kept); the second reader checked them against the pages and recomputed the wedges.

- L5 lower plate:
  - printed 1.8 +/- 0.42;
  - tan2004 +10.5 +/- 0.8. With Tan's SEM taken as printed, z = -9.6; with SD = SEM x 10 instead of SEM x sqrt(10), z = -3.4. For scale (Inference, the second reader's computation, rerun): the same z on the uncontested thoracic rows reaches -5.65 (T1 upper) and -5.36 (T10 lower) with printed SEMs, and -2.34 and -2.62 on the other reading. Between two populations a z measures sampling error only and ignores the 1 to 5 deg systematic gaps of the calibration. So the L5 lower plate stands out, but under the second reading only modestly (-3.39 against an uncontested -2.62);
  - Tan 2002 (Eur Spine J 11:152-158, not in hand). bonczar2024's Table 1 (p. 3, PDF 3) lists two digitiser studies besides Panjabi: "Tan S. H. 2003", n 10, age 65.7, 61.6 kg, which is tan2004, and "Tan S. H. 2001", n 12, age 67, 62 kg, which is its ref. 32, Tan, Teo and Chua 2002 (p. 12, PDF 12). The different n, age and weight argue against one set of spines. Inference, the second reader's back-out, rerun: a DerSimonian-Laird pool of Panjabi 1.8 +/- 0.42 and tan2004 10.5 +/- 0.8 alone gives 6.12 (SE 4.35), not bonczar's printed 8.20 (SE 3.72; p. 9, PDF 9). A third series at about 12.4 (SE about 0.8) reproduces both exactly. At L1 to L4 the same back-out gives Tan-like lower-plate values (-2.8, -1.2, about 2.3, 3.5). This assumes the pool holds exactly these three studies;
  - gilad1985: 6.8, derived from mean corner distances of 156 films of living men aged 20 to 38 (Table 1, p. 118, PDF 4: L5 a 33.9, d 25.7, k 44.9; Fig. 1, p. 116, PDF 2). Inference: the law of cosines on these means gives an a-d angle of 96.8 deg, and 88.0, 92.0, 92.0 and 93.6 at L1 to L4. But the authors themselves say the a-d angle was about 90 deg for every lumbar vertebra (p. 119, PDF 5); the cosine rule on means is not the mean angle, and its result moves about 3 deg per mm of k. Weak, and not an independent contradiction;
  - bonczar2024's pooled 8.20 (SE 3.72; p. 9, PDF 9) contains Panjabi's 1.8 and both Tan series, so it is not independent of them.
- L5 upper plate: printed 2.2 against Tan's 6.9 (z -4.5, or -1.6 on the other SEM reading). That is within the thoracic range above, and the cervical reading itself gives -5.05 at the C7 lower plate, -4.24 at C5 upper and -3.73 at C7 upper. No evidence either way.
- L5 body wedge. The printed pair gives a cap of 2.2 + 1.8 = 4.0 deg, with a 95% upper limit of 5.3 (Panjabi's SEMs added in quadrature; Inference). The eight independent values are one each from seven sources, two from Abbas (men and women); all are Inference from printed heights and depths, some of them borrowed:
  - tan2004 3.9;
  - gilad1985 4.4;
  - frontphys2026 5.3 (5.27; 100 living adults, CT). Its depth, 33.6 mm, is bonczar2024's pooled L5 depth; with Panjabi's own L5 depth it gives 5.22, with Tan's 5.99;
  - bonczar2024 5.65;
  - moncadahabib2025 6.5 (37 living adults, CT);
  - abbas2021 6.9 (men) and 7.0 (women) (90 control men and 90 control women, CT, a height ratio read off Figs. 5 and 6, pp. 4 and 5). The posterior height and depth it needs are not printed and were borrowed; with Panjabi's L5 VBHp of 22.9, the men come to about 6.5 to 6.8 (the second reader's reading of Fig. 5);
  - busscher2010 7.2 (6 cadaver spines, CT; Table 3, p. 1107, PDF 4, with a depth of about 36.3 mm read from Fig. 3, p. 1109, PDF 6).
  - Seven of the eight exceed 4.0. Five exceed 5.3, and frontphys2026 sits at it. Without bonczar2024, which contains Panjabi, six of seven exceed 4.0 and four of seven exceed 5.3. But 5.3 carries only Panjabi's SEMs. With each source's own error (Inference, the second reader), bonczar's 5.65 has a wedge error near 2.3 deg, busscher's 7.2 near 1.6 to 2.6 (6 men aged 55 to 84, VBHp SD 3.8), and moncadahabib's 6.5 near 1.1, so none of the three is clearly above 5.3.
  - Data-quality flags: moncadahabib2025's Table 1 holds an impossible row (L1 AH 243.1 +/- 19.1 with a range of 200 to 248; p. 4, PDF 4); frontphys2026's SDs (L5 VBHa +/- 0.6 mm in 100 adults aged 20 to 70) are implausibly small; abbas2021's controls are abdominal-CT patients aged 40 to 99 (p. 2, PDF 2).
  - The same cap fails as often on Panjabi's uncontested thoracic rows. Inference, the second reader's computation, rerun: independent height wedges from tan2004 (pp. 140 to 141), kunkel2011 (Table 2, p. 379, PDF 5, with Panjabi's thoracic depths) and busscher2010 (Table 3, p. 1107, PDF 4, with Panjabi's depths) exceed his thoracic point cap at 22 of 36 source-level pairs (Tan 6, Kunkel 8, Busscher 8, of 12 each) and his 95% limit at 13 of 36 (5, 5, 3). From T7 to T12 every source is over the point cap at every level. At T10 the cap is 1.7 (95% limit 2.30) against 3.55, 2.53 and 3.69. The L5 rate (7 of 8 over the point cap, 5 of 8 over the 95% limit) is no worse. So the cap test does not tell the two readings apart: Panjabi's caps fall short of other people's height wedges in data nobody disputes.
- At L4 there is no conflict. The sources give wedges from -0.3 to +2.2, against a printed cap of 4.7 + 2.7 = 7.4.

**Read as cervical, the row also passes the cap test, which does not discriminate.** The cervical body wedges from tan2004, busscher2010, gilad1985 and kunkel2011 run from -6.6 to +0.3 deg; kunkel2011 is a thoracic study and supplies C7 only (radiographic, about 6 bodies; its reading note).

- Every one is inside the printed caps except Tan's C5, at 6.6 in size. That exceeds the point cap of 1.7 + 2.7 = 4.4 but not its 95% limit of 6.7.
- At C7 the wedges are -0.6 to -2.2 against a cap of 4.0.

**What does not compare.**

- gilad1985's cervical corner lines run to the anterior lip and give 5 to 14 deg, which is not a fitted-plane angle.
- bonczar2024 pools Panjabi's unsigned values with Tan's signed ones, so its values are not independent. Its Table 1 (p. 3, PDF 3) also labels Panjabi 1992 as radiographs from India, which is wrong.
- vanderhouwen2009's disc wedges (L4-L5 9.5 deg, Fig. 3, p. 39, PDF 7) depend on how two vertebrae sit, which per-vertebra angles do not fix.

**Summary of the outside evidence (Inference).**

- At positions 1 to 4, small tilts fit either region; with the thoracic offset taken out, they fit both about equally.
- At position 5, the body-wedge cap and the upper plate do not discriminate. The lower plate does: tan2004's 10.5 and Tan 2002's inferred 12.4 against the printed 1.8 lean against the lumbar reading, though Panjabi's thoracic means not following Tan's large values weakens even that.
- So the outside evidence is close to neutral, with one weighted point at the L5 lower plate, and the direction rests mainly on section 2.1.

### 2.3 Errata and later readers

What this section rests on: every database search below was one reader's (errata) and none could be rechecked here, since this machine's network refuses PubMed, Europe PMC and Crossref, and Semantic Scholar was not retried. The later readers' files (Kunkel 2010's printed page, Breglia, Ceran, Bellina, Lavecchia) are not in hand, and the errata work folder was not kept. Only tan2004 Table 2 and the Kunkel refit below were rechecked.

**No erratum, correction or letter was found** for either paper (one reader's searches, not rechecked).

- PubMed records: lumbar PMID 1566168, cervical PMID 1948369 and thoracic PMID 1948374 carry no erratum or comment link, and their efetch XML has no CommentsCorrections element.
- Panjabi's 16 Spine papers of 1991 and 1992 have no correction link.
- Europe PMC's commentCorrectionList is empty for all three papers. Crossref holds no update relation on the three DOIs: 10.1097/00007632-199203000-00010 (lumbar), 10.1097/00007632-199108000-00001 (cervical) and 10.1097/00007632-199108000-00006 (thoracic).
- All 1,170 PubMed records of Spine for 1991 to 1993 were scanned. Two carry an erratum link, and neither is Panjabi's: PMID 1387977 and PMID 1825891.
- All 80 PubMed letters and comments in Spine for 1991 to 1995 were read. Five touch vertebral topics, and none comments on these papers.
- Caveat: PubMed indexed few Spine errata in those years (one standalone erratum in 1991, none in 1992 to 1996). The print issues were not read, because journals.lww.com returned 402. So the absence is weak evidence (Inference).

**The repeat is in the print, not in our scans.** Breglia's 2006 Ohio University MS thesis photocopies the cervical and lumbar Table 2 as Appendix D (p. 87) and Appendix L (p. 95); its printed pages match its PDF pages. Both show the same EPI rows; the note's writer checked the Appendix L image (errata/dl/breglia/ap-95.png, not kept). One reader's reading until the thesis is attached.

**Later work copied the lumbar rows as printed, and nobody remarked on the repeat.**

- Kunkel, Schmidt and Wilke 2010, J Anat 216:320-328 (PMID 20039978). Read through a summary of the PMC HTML; the printed page was not read.
  - Its EPIS and EPII equations, cubic in VBHp, were fitted on Panjabi's T1 to T12 and L1 to L4 means.
  - Rerunning errata/kunkel_fit.py on bordercall's long table reproduces EPIS exactly: coefficients -66.833, 12.035, -0.691, 0.013; R2 0.606; residual SD 0.699. For EPII it reproduces the coefficients 66.233, -9.095, 0.418, -0.006 and SD 0.606, with R2 0.511 against the printed 0.514. The second reader's own cubic fits on panjabi_long.csv give the same coefficients, R2 and SD, and adding L5 does not; the match to Kunkel's printed coefficients is unverified from the page.
  - The thoracic inputs in the long table match my reading of p. 892.
  - Inference: Kunkel's lumbar inputs are the printed L1 to L4 values, which equal the cervical C3 to C6 values whichever paper they came from.
- Bellina et al. 2024, J Biomech 164:111951, Supplementary Table 1 (mmc1, PDF p. 2): cites Panjabi 1992 Table 2 for EPIS and EPII. A T1 to L5 refit comes close to its coefficients but not exactly (Inference; one reader).
- Ceran 2006, Loughborough PhD thesis, Fig. 8.3, printed p. 175 (PDF 193): the lumbar model's VBIus takes the printed EPItu (2.70, 3.50, 1.70, 4.70, 2.20; errata reader). Its VBIls column holds -4.00, -2.10, -2.70, -2.70 and -1.80, which is the printed EPItl with its sign flipped; the note's writer checked the crop (not kept). One reader's reading.
- Lavecchia 2018, Birmingham PhD thesis, Table 4.4 (p. 65, PDF 89): copies Breglia's regressions but drops EPItu and EPItl (one reader).
- tan2004 Table 2, pp. 142 to 143 (PDF 6 to 7): sets 16 parameters beside Panjabi's, and end-plate inclination is not among them (checked by the second reader).
- Semantic Scholar: 484 papers cite the lumbar paper, 135 of them with context snippets. 465 cite the cervical paper, 137 with snippets. No snippet mentions the repeat (one reader, not rechecked).
- **No republication by Panjabi's group** was found. A PubMed title search found 11 Panjabi anatomy records, and the only ones from this specimen set are the three papers and panjabi1993f, which reports no end-plate inclination (one reader, not rechecked). The 1990 second edition of White and Panjabi was not reached; Inference: it predates both papers, so it cannot hold the 1992 table as published.

## 3. What it means for the rule

**What the rule does with these two measures today.** Facts from bordercall/schwingcheck:

- Both measures are in the pool of 32. Neither is among the seven, and no measurer reads either one (schwingcheck/README.md, "The pool"). The archive's spineps_map.py measures the seven and two unregistered process extents, tp_span and spinous_length (archive/bordercall/spineps_map.py lines 133 to 160; schwingcheck/measures.py lines 72 to 76), and nothing reads a plate angle. So no result from a mask has used them. The name command takes any registered measure from a hand-made FIELD.csv (schwingcheck/__main__.py lines 133 to 141), so whether anyone named a real field on them cannot be checked from the code.
- The rule takes a measure only if the table has a row at every level it runs over. measures.select refuses a measure that lacks one, and measures.pool leaves it out (schwingcheck/measures.py lines 242 to 277).
- Each angle enters as a normal. Its table SD is SEM x sqrt(12) (schwingcheck/table.py, line 275), and its measurement error is 3 deg (schwingcheck/README.md, "Each kind its own term").
- The paper-tables comparison already applies option 4 below, by the flag `--leave-out endplate_incl,endplate_lower_incl` (research_notes/paper-tables/data/cross_naming.json, its command and left_out_measures; results/README.md). The flag is empty by default (paper-tables/tools/cross_naming.py line 408), so only a run that passes it leaves them out, as the HANDOFF's rerun line does. The record's panjabi_measures still lists both, and data/series.csv still holds their 54 tan2004 and bonczar2024 rows, filtered at run time.

**The options at L1 to L5.**

1. Keep the lumbar row as printed. Not recommended.
   - The L5 lower-plate cell conflicts with the two same-definition series (2.2), the body-wedge evidence does not discriminate, and L1 to L4 are, most probably, cervical numbers.
   - Inference, from the rule's own terms: on a real spine, a body whose lower plate tilts 10.5 deg (tan2004's L5 mean) would score -5.53 as L5 against -3.56 as L1 and -3.79 as L3 (log density per body). On this one measure that makes it 2.0 nats more like an L1 than an L5. Its best places are C3 and L1, tied since their rows are identical; L5 ranks 18th of 22, and T12 scores -5.78, worse than L5 (rule.loglik, rerun in this revision).
2. Mark L1 to L5 missing. As the code stands, this is the same as dropping both measures over C3 to L5.
   - Teaching the rule to leave out a term wherever the table has no row would compare places on unlike terms (Inference).
   - A present angle term is at most about -2.03 nats per body: the peak log density of a normal with SD 3 deg is -2.02, the highest at any level is -2.03 (upper plate, T10), and T12's lower plate peaks at -2.08. A typical value scores half a nat below its peak: -2.58 at T12's lower plate and -2.82 at its upper. An absent term is 0.
   - So every body placed in L1 to L5 would gain at least 2 nats per measure over one placed at T12 or above, typically 2.6 to 2.8, about 5 to 6 for the pair. That bias lands at the thoracolumbar border, which is the call bordercall exists to make.
   - A missing level needs a stand-in density, such as a wide prior over the unknown mean, not an absent term. No stand-in is chosen now, since any stand-in at L1 to L5 adds an assumption at exactly the border that matters.
3. Replace the values from tan2004. For both angles Tan prints all 22 levels, C3 to L5 (Table 1, pp. 140 to 141, PDF 4 to 5). A replacement should therefore take Tan's whole series. Replacing L1 to L5 alone would join two studies at T12/L1 whose thoracic plates differ by about 1 deg on average (the calibration above). The caveats:
   - first, the SD rule: Tan's C3 and C4 upper-plate SEMs (4.1 and 5.2) give implausible SDs on either reading of its SEM (2.2), so the SD rule and those two cells must be settled before a table can be built;
   - the population: 10 Chinese Singaporean cadavers of mean age 65.7, against Panjabi's 12 of mean age 46.3;
   - the sign is named only in words, with no reference end, and its geometric sense is only inferred;
   - a measurer would have to read signed angles in the posterior-wall frame;
   - the generator would draw from the new table too, so every result with all 32 measures would be rescored.

   A signed series carries what an unsigned one cannot: Tan's lower plate changes sign between L2 and L3, and between the cervical and thoracic spines. Tan 2002, a second same-method lumbar series of 12 spines, would be worth reading first.
4. Drop both measures from the pool. Recommended; as the code stands it needs new code (below).

**My recommendation.**

- **Now:** decide option 4. Implement it as one exclusion list, measure key to reason ("the lumbar rows reprint the cervical C3-C7 values", with a pointer to this note), that measures.pool, measures.left_out and measures.select all read. pool then leaves the two angles out, left_out gives that reason, and select, which the name command uses (schwingcheck/__main__.py lines 133 to 141), refuses them with it.
  - Recording a reason in measures.left_out alone, as the draft said, is not possible as the code stands: left_out works out each reason from the table and has no place for one written by hand (measures.py lines 280 to 296).
  - Dropping them from pool alone would leave `name --measures endplate_incl` naming a real field on the reprinted row, which is the real-spine risk option 1 warns against.
  - The same list makes cross_naming's --leave-out redundant.
- Keep every cell in the provenance record and the long table as printed, since that record's job is to show what the papers print. table.py's FIELDS have no flag column, and `table check` demands that the long CSV equal what write gives, to the byte (table.py lines 53 to 54 and 237 to 239). So the flag is best the exclusion list above, not a new column.
- What option 4 costs, which the draft did not count (it charged a rescore to option 3 only):
  - tests that assert a pool of 32, kinds (18, 6, 8) and 17 left out (tests/test_schwingcheck_table.py lines 337 to 359) and a shape of 32 and prefix-32 (tests/test_schwingcheck_curve.py lines 138, 182, 509 to 530) change to 30, (18, 6, 6) and 19;
  - schwingcheck/README.md states 32 throughout (for example lines 116, 491 and 722);
  - curve.draw_pool draws every measure outside the seven in one call (schwingcheck/curve.py line 237; schwingcheck/columns.py lines 172 to 188), so removing two shifts the random stream: after option 4 the code would reproduce none of records/curve-2026-10-28's numbers outside the seven, the subsets without the angles included. The seven are drawn from a seed of their own and stay as they are;
  - pull request 20 (the chain of levels) is built on this pool (clinical-reread/HANDOFF.md).
  So the change goes in one pull request with the tests, the README and a rerun of the build-up study, or, if the rerun waits, a line in the README that the committed record was made on the pool of 32.
- **Later, when a measurer for end-plate inclination exists:** come back with option 3, a whole C3-L5 series from tan2004 (with Tan 2002 read first), or better, a table from the CTs of TODO.md item 5 read by that same measurer.
- Why option 4 now:
  - nothing measured on a real spine depends on these measures;
  - in the generator's world their gain is small with all 32 measures, but not in the lateral view (below), which makes a real lumbar table the better later path;
  - each other option adds an assumption nobody has checked.

**At C3 to C7.** The printed cells are the original as far as the papers can tell (probable, section 1), so keep them as they are. That advice, unlike the drop, depends on the direction.

- If the measures leave the pool, they leave at C3 to C7 too, because the pool runs over all of C3 to L5.
- If a later rule takes measures over part of the levels, C3 to T12 may stand only with a stand-in density at L1 to L5, for the reason given under option 2. The caveat: on average the cervical upper plates sit 2.8 deg below tan2004's, against 1.1 deg for the thoracic rows; per level, C5 and C7 exceed every thoracic gap but T1's, while C3, C4 and C6 do not.

**Housekeeping (panjabi reader, small).**

- The archive's inventory gives EPItl and EPAl as C3-L5, but both are printed at C2 as well (EPItl 4.2 / 1.2; EPAl 194.4 / 9.64; p. 863, PDF 3).
- thoracic-t3 labels the printed "EPIlt" row as EPItl. That reading is right, but the misprint itself is worth noting.
- TODO.md line 16 can point to this note.

**What the synthetic results keep and lose.** The generator draws from the same table, so its own world is consistent, and the identical rows at C3-C7 and L1-L5 are simply two runs of levels these angles cannot tell apart while the other measures can. Every build-up result is drawn from Panjabi's table, so all of them are statements about the generator's world (schwingcheck/README.md line 491); only runs on SPINEPS masks speak of real spines.

- **Unaffected by the reprinted row:**
  - everything on the seven (rung 0): the archive record of 2026-10-26 (exact.json with its 127 subsets) and its rescore, and 73.1% of three-body fields named exactly; these stay reproducible after option 4, since the seven are drawn from their own seed;
  - any run on SPINEPS masks, since the measurer reads only the seven;
  - the prefixes of the greedy order up to step 23, and every subset without the two angles, such as the seven with the pedicles, the processes and the facets (24 measures). These carry no input known to be misprinted, but after option 4 they are kept only as recorded, since the code would no longer reproduce them.
- **Carrying the two angles, kept as statements about the generator's world only:**
  - every result with all 32 measures, such as 98.3% at three bodies;
  - the prefixes from step 24 on;
  - the family "the rest of the body and the canal" (the seven plus endplate_area, endplate_lower_area, the two angles and canal_area, 12 measures);
  - the angle subsets;
  - the lateral view (10 measures) and both views (17 measures; README line 564: 77.1%, 95.0%, 73.2%), since both angles carry the planes mask and lateral (mnemonics.py lines 52 and 53; curve.py lines 207 to 221);
  - the robustness arms run on all 32.
- **Lost as claims about real spines:** whatever these numbers owe to the two measures (schwingcheck/README.md, the curve table, rows 23 to 24 and 30 to 31):

| Step | Measure added | Named exactly, 1 body | Named exactly, 3 bodies | Named at 0.99, 3 bodies |
|---|---|---|---|---|
| 24 | endplate_incl | 84.1% to 84.5% | 97.4% to 97.5% | 82.4% to 83.0% |
| 31 | endplate_lower_incl | 86.9% to 87.0% | stays 98.2% | 86.6% to 86.8% |

  Inference: the greedy steps sum to +0.5 points at one body, +0.1 named exactly at three and +0.8 at 0.99 at three, but removing both at the end differs from adding them. A paired run of the rule refuter on the first 300 of the study's typical columns (seeds 97 and 197, rule.name on the trapezoid's nodes), rerun in this revision, gives for all 32: 86.52% to 86.26% named exactly at one body, 97.95% unchanged at three, 86.93% to 86.25% at 0.99 at three. So dropping both would cost roughly a quarter to a half point at one body, nothing named exactly at three and under a point at 0.99. Only a rescore can say exactly, because the greedy order after step 24 was chosen with them in.
- The gain is not small in the lateral view. On the same 300 columns (Inference), the lateral view falls from 57.52% to 55.85% named exactly at one body, from 86.33% to 84.97% at three, and from 47.37% to 43.30% at 0.99 at three, as its 10 measures become 8; both views (17 to 15) fall from 76.50% to 75.83%, 94.88% to 94.60% and 73.53% to 71.95%. So the generator credits the two angles with about 1.5 points named exactly and 4 points at 0.99 in the view a lateral radiograph reads.
- On a real spine the cost of keeping them would not be this gain. It would be the misdirection shown in option 1, at L5. The draft also put a cost at the T12/L1 border, but that bias belongs to option 2, an absent term, not to keeping the printed row: the calibration puts the printed L1 to L4 within -0.5 to +1.4 deg of tan2004's lumbar values.

## 4. What is still not known

- **Panjabi's real lumbar values.** His twelve spines' lumbar EPItu and EPItl appear in no printed source found, though the lumbar paper's Table 1 lists the measure and its abstract claims angular dimensions of the bodies (p. 299, PDF 1).
- **How the duplication arose,** in which file, and whether any other lumbar cell came from the same slip. The repeat searches find no other repeated run longer than two values, and no three matching values at any alignment, among the four papers' tables in the long table.
- **Whether the cervical values are right.** Beyond agreeing with their own text, they are unconfirmed: on average their upper plates sit further below tan2004's than the thoracic calibration gap (2.8 against 1.1 deg), though only C5 and C7 exceed the thoracic range. That could reflect population or method (Tan's spines are older; how the end-plate points were chosen around the uncinate processes is not stated).
- **The sign conventions.** Panjabi's EPI rows print no sign. His cervical figure draws the two plates tilting the same way and his thoracic figure draws them tilting opposite ways. tan2004 names its sign in words (cephalad, caudal) without its reference end, and its SEM is ambiguous.
- **Sources not reached:**
  - the Spine print issues of 1991 to 1993, read for an erratum;
  - Tan 2002 (Eur Spine J 11:152-158), a second same-method series of 12 lumbar spines in bonczar2024's pool (2.2), whose full text, per the errata reader's Europe PMC search (not rechecked here), carries EPItu and EPItl;
  - later editions of White and Panjabi, and Miele, Panjabi and Benzel 2012;
  - Kunkel 2010's printed page, and Lavecchia's 2018 journal paper;
  - Kumar 2000 (Anat Rec) and Masharawi 2008 (Clin Anat).
- **Whether the L1 to L4 fit to tan2004 is chance.** It rests on four levels, and with the thoracic offset taken out it ties the cervical fit (2.2).
- **What a measurer would read on CT or a SPINEPS mask.** No measurer yet reads a fitted-plane end-plate angle in the posterior-wall frame, so how such a reading compares with a cadaver digitizer's is not measured.
