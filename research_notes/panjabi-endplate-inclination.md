# Panjabi's end-plate inclinations at L1 to L5: which printed rows are the original

Status at the checkpoint of 2026-10-29 00:40 UTC: a draft. Its writer checked it against the page images; the skeptic
that was to try to refute it, and the revision after, were stopped by the owner's checkpoint before they finished.
Read it as one reader's verdict until a second reader has tried to refute it (clinical-reread/HANDOFF.md, "Since").


Source: thread "Finish the clinical reread", project symphony_4, 2026-10-28. Built from the three evidence lines that thread gathered: panjabi (Panjabi's own papers, work/panjabi-own/), others (other papers' values set on his footing, work/others/) and errata (errata, letters and later readers, work/errata/). Its work folders were in that session's scratch space and are not kept. This note's own checks are panjabi-endplate-inclination-scripts/calibrate.py and runs.py beside it. Every Panjabi value quoted here was checked against the page images (panjabi-own/hi/crop_c_t2.png, crop_l_t2.png, crop_t3_bot.png, crop_c_p864_text.png) and tan2004's against its text layer.

Paper ids and pages. Each citation gives the printed page, then the PDF page of the scan in clinical-reread/papers/.

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

The cervical row (panjabi1991c Table 2, C3 to C7) is the original, and the lumbar row (panjabi1992 Table 2, L1 to L5) is a copy of it with the C2 column dropped, so Panjabi's lumbar paper prints no lumbar end-plate inclination at all. That the two rows are one set of numbers printed twice is near certain (20 numbers repeat in order, and no other lumbar series shares a run longer than two values with any cervical or thoracic series), while that the set is cervical is probable but not proven: every cue in Panjabi's own papers and every independent L5 source points that way, yet at positions 1 to 4 the row fits tan2004's lumbar values better than its cervical ones. The authors' data, an erratum in the print issues or a lumbar publication by his group would settle it, and a same-definition series that found L5 lower end plates near 2 deg would reopen it.

## 2. The evidence

### 2.1 Panjabi's own papers

**One set of spines, one method.** All three papers measured the same twelve specimens.

- panjabi1991t p. 890 (PDF 3): 12 spines from C2 to L5 were studied, and this paper reports 144 thoracic vertebrae (12 spines x 12 levels).
- panjabi1991c p. 861 (PDF 1): twelve fresh autopsy specimens, mean age 46.3 years (range 19 to 59), 8 men to 4 women. On p. 863 (PDF 3) it reports 72 vertebrae, C2 to C7 (12 x 6).
- panjabi1992 p. 299 (PDF 1): twelve specimens from the axis to the last lumbar vertebra, with the same age and sex summary. Its abstract counts 60 vertebrae (12 x 5).
- The lumbar Methods (p. 299, PDF 1) set the vertebra's frontal, transverse and sagittal planes by least squares from four points on the posterior wall, with the origin at the centre of the upper end plate. The cervical and thoracic papers describe the same morphometer and the same origin (p. 861, PDF 1; p. 888, PDF 1), and the cervical paper says it follows the thoracic paper's method (p. 861, PDF 1).

**Where each paper deals with end-plate inclination.**

- Cervical (panjabi1991c).
  - Table 1, p. 863 (PDF 3) lists EPI as end-plate inclination, and the suffix t as the transverse plane.
  - The side view of Figure 1, p. 862 (PDF 2), draws EPItu and EPItl, and both plates' lines fall toward +Z, the anterior direction.
  - Table 2, p. 863 (PDF 3) prints the values.
  - Results, p. 864 (PDF 4): for C3 to C7 the text puts the upper plates' tilt from the transverse plane at 2 to 5 deg and the lower plates' at 2 to 4 deg. It says the upper-lower difference stays below 2 deg at every level, with no significant trend.
  - The text agrees with the table. Upper C3 to C7 runs 1.7 to 4.7, which rounds to 2 to 5, and lower 1.8 to 4.0, which rounds to 2 to 4. The stated C3-C7 scope correctly leaves out C2's 4.2. The differences per level are 1.3, 1.4, 1.0, 2.0 and 0.4. Inference: C6's 2.0 is "below 2" only after rounding.
  - The panjabi reader found nothing more in Figure 2 (p. 865), the Discussion (pp. 866 to 868) or Table 7 (p. 868).
- Thoracic (panjabi1991t).
  - Table 3, printed p. 892 (p892 PDF 1) prints EPItu, EPItl (the label is misprinted as "EPIlt") and EPIt at T1 to T12. EPIt equals EPItu + EPItl in all 12 cells; I checked each one.
  - Results, p. 890 (PDF 3): inclination stays constant through the thoracic spine. The upper plate averages 1.7 deg and the lower 2.1 deg. The wedge angle is defined as the sum of the two and averages 3.8 deg, and a radiographic side study found 3.9 deg.
  - Inference: the 12-level means of the printed means are 1.70, 2.075 and 3.775.
  - Discussion, p. 898 (PDF 10) repeats 3.8 deg per vertebra and about 45.6 deg over the thoracic spine. Inference: 45.6 is 12 x 3.8, and the printed EPIt cells sum to 45.3.
  - Figure 3B, p. 891 (PDF 4) draws EPItu falling and EPItl rising toward +Z, which are opposite senses.
- Lumbar (panjabi1992).
  - Table 1, p. 301 (PDF 3) lists EPI, and Table 2 on the same page prints the two rows. Nothing else in the paper mentions them.
  - Figure 1, p. 300 (PDF 2) draws no EPI. I checked the crop panjabi-own/hi/crop_l_fig1.png.
  - The Results "Vertebral Body" paragraphs, p. 301 (PDF 3), cover end-plate widths, depths, their ratio and areas only. I checked this.
  - Per the panjabi reader, Figure 2 (p. 303), the transition-zone Discussion (p. 304) and Table 6 (p. 305) say nothing about end-plate inclination.
  - The lumbar paper never says how the two angles combine.
- Facets (panjabi1993f): no end-plate data in any table or text (pp. 1298 to 1310, PDF 1 to 13).
- Inference: the cervical paper treats the two angles as a difference and draws the plates tilting the same way, while the thoracic paper treats them as a sum and draws them tilting opposite ways. No table prints a sign. So the lumbar rows carry the cervical figure's convention, or none.

**The C2 column fits the cervical table.** Cervical Table 2's C2 column has 20 cells: nine measures with a mean and an SEM (18 cells) plus two ratios (2 cells).

- All 11 dashes fall on upper-end-plate measures or VBHp: EPDu 2, EPWu 2, VBHp 2, EPWu/EPDu 1, EPAu 2, EPItu 2.
- All 9 numbers fall on lower-end-plate measures: EPDl 2, EPWl 2, EPWl/EPDl 1, EPAl 2, EPItl 2.
- The EPI rows follow this split: EPItu is a dash and EPItl is 4.2 / 1.2 (p. 863, PDF 3; checked).
- Inference: C2 has no upper end plate because of the dens.
- The panjabi reader found 4.2 as a mean nowhere else in the three papers' dimension tables.
- Inference: this shows the cervical EPI rows are whole and coherent. On its own it does not prove direction, since a copy that overwrote only C3 to C7 would have left C2 in place.

**The decimals travelled with the block.**

- In lumbar Tables 2 to 5, every SEM prints to two decimals except the four EPI cells 1.5, 1.1, 0.4 and 1.1. Two-decimal examples are 1.10 and 49.00 in Table 2, p. 301 (PDF 3).
- In the cervical tables, 5 of 179 SEMs print to one decimal, and all five are EPI cells: 1.5, 1.1, 1.2 (C2), 0.4 and 1.1.
- I checked Table 2 of both papers. The counts over Tables 2 to 5 and the 179 SEMs are the panjabi reader's.
- Inference: the quirk shows the block was carried over as typed, but not which way it went.

**The repeat is unique.**

- The panjabi reader compared every row against every row at every alignment, forward and reversed, across statistics:
  - lumbar: 57 rows, 285 numbers (130 means, 130 SEMs, 25 ratios);
  - cervical Tables 2 to 6: 69 rows, 387 numbers and 27 dashes;
  - thoracic Tables 3 to 7: 72 rows, 844 numbers and 18 dashes.
- It found exactly 4 runs of 3 or more equal values: the lumbar EPItu means, EPItu SEMs, EPItl means and EPItl SEMs against the cervical ones, each 5 of 5. Runs of two outside the repeat occur 11 times against cervical and 27 times against thoracic, mostly 1.10 against a ratio of 1.1.
- I repeated the search on bordercall's long table (bordercall/schwingcheck/data/panjabi_long.csv, means and SEMs only) with verdict/scripts/runs.py. It compared 52 lumbar series (one measure's means, or its SEMs, over its levels) against 131 cervical and thoracic series (64 and 67), forward and reversed: 52 x 131 x 2 = 13,624 comparisons.
  - Longest run 5: 4 comparisons, exactly the four EPI series at L1-L5 against C3-C7.
  - Longest run 2: 10.
  - Longest run 1: 522.
  - Longest run 0: 13,088.
  - No run of 3 or 4.
- Inference: twenty numbers in order are not chance.

**The lumbar manuscript was drafted from the cervical one.**

- Inference, from setting the pages side by side: the lumbar Methods (p. 299, PDF 1) follow the cervical Methods (p. 861, PDF 1) nearly sentence for sentence. They share the specimen summary, the threaded rods of 2 mm diameter and 2.5 mm length, the pin markers and morphometer, and the sentence that introduces Table 1 and Figure 1, with the cervical example of an uncovertebral facet turned into an articular facet.
- The thoracic Methods (p. 888, PDF 1) differ: rods 3.0 mm by 3.2 cm, and soft tissue softened by boiling.
- The lumbar paper calls itself the third and final paper of the series (p. 299, PDF 1). The cervical paper calls itself the second and points to the initial study in the same issue at p. 888 (p. 861, PDF 1).
- Acceptance dates: thoracic 18 July 1990 (p. 888, PDF 1), cervical 8 November 1990 (p. 861, PDF 1), lumbar 19 April 1991 (p. 299, PDF 1).
- Inference: building a later manuscript on an earlier one is the natural route for a block of cervical cells to reach a lumbar table. This gives a mechanism, not proof: all twelve spines were measured before any paper was accepted, so lumbar values could have existed by November 1990.

**Continuity at the junctions does not decide it.** Values are mean / SEM in degrees.

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

**What bordercall's archive says.**

- bordercall/TODO.md line 16 records the finding: lumbar-t2 rows 12 and 13 against cervical-t2 rows 19 to 22. It leaves the question to the owner, records no lean, and says the rule scores the lumbar values as printed.
- CONTRADICTIONS.md compares each paper only with itself, so it could not catch the repeat.

### 2.2 The other papers, on Panjabi's footing

**Footing.** All three points are Inference.

- Panjabi prints his angles with no sign. For one population, the mean of an unsigned angle is at least the magnitude of the mean signed angle, so a signed source's absolute mean is a lower bound for comparison.
- Only tan2004 uses his definition. gilad1985 is a two-dimensional analogue built from corner lines, and the other sources give only a body wedge.
- From Panjabi's own pair at a level, a body's mean sagittal wedge cannot exceed EPItu + EPItl in size, by the triangle inequality for small angles between planes.

**tan2004, the one same-definition series.**

- What was measured: C3 to L5 of 10 Chinese Singaporean cadavers, mean age 65.7 (range 56 to 77), cleaned, air dried and measured with a 3-D digitiser (p. 137, PDF 1). Its 220 vertebrae are 10 spines x 22 levels, C3 to L5 (Inference: n = 10 per level).
- Definition: Panjabi's EPItu and EPItl, measured against a transverse plane perpendicular to the posterior-wall plane (Fig. 1, p. 138, PDF 2; frame, p. 139, PDF 3).
- Signs: values carry a sign, but no convention is stated (p. 143, PDF 7).
  - The others reader inferred that positive means the plate's anterior end lies caudal: EPItl - EPItu reproduces Tan's height-based wedge at L1 (-4.4 against -4.5), L2 (-4.5 against -4.6) and L5 (3.6 against 3.9).
  - I add, as Inference, that Tan's thoracic EPItu is positive and EPItl negative at all 12 levels, the opposite senses Panjabi's thoracic figure draws, while Tan's C3 to C7 are positive on both plates, the same sense Panjabi's cervical figure draws.
- SEM: defined as SD over the sample size (p. 139, PDF 3), which leaves its meaning ambiguous; its C3 and C4 upper-plate SEMs are 4.1 and 5.2.
- Values (Table 1, mean +/- SEM; C3 to C7 on p. 140, PDF 4; L1 to L5 on p. 141, PDF 5):

| Level | EPItu | EPItl | Level | EPItu | EPItl |
|---|---|---|---|---|---|
| C3 | 5.0 +/- 4.1 | 3.3 +/- 0.5 | L1 | 1.8 +/- 0.4 | -2.6 +/- 0.4 |
| C4 | 5.2 +/- 5.2 | 3.5 +/- 0.7 | L2 | 3.4 +/- 0.4 | -1.1 +/- 0.2 |
| C5 | 7.1 +/- 1.2 | 2.7 +/- 0.3 | L3 | 1.9 +/- 0.3 | 1.8 +/- 0.1 |
| C6 | 5.8 +/- 0.6 | 4.2 +/- 0.4 | L4 | 3.7 +/- 0.6 | 3.2 +/- 0.6 |
| C7 | 5.8 +/- 0.8 | 5.1 +/- 0.5 | L5 | 6.9 +/- 0.9 | 10.5 +/- 0.8 |

**A calibration I added, from data nobody disputes.**

- Panjabi's thoracic rows are not in question. Their gap from Tan's thoracic magnitudes therefore shows how far two honest same-definition series sit apart.
- Gaps are Panjabi minus abs(Tan), in degrees (verdict/scripts/calibrate.py). Thoracic values are panjabi1991t p. 892 (p892 PDF 1) and tan2004 pp. 140 to 141 (PDF 4 to 5).

| Comparison | Upper plate | Lower plate |
|---|---|---|
| Thoracic T1 to T12, uncontested | mean -1.08; -5.4 at T1, T2 to T12 within +/-2.3 | mean -0.88; range -2.0 to +1.0 |
| Row read as C3 to C7 | -2.3, -1.7, -5.4, -1.1, -3.6 (mean -2.82) | +0.7, -1.4, 0.0, -1.5, -3.3 (mean -1.10) |
| Row read as L1 to L4 | +0.9, +0.1, -0.2, +1.0 | +1.4, +1.0, +0.9, -0.5 |
| Row read as L5 | -4.7 | -8.7 |

All Inference:

- Read as L1 to L4, the row fits Tan's lumbar values more closely than Panjabi's own thoracic rows fit Tan's thoracic ones. Over L1 to L4, the others reader found an RMS difference of 0.86 deg over the 8 cells and r = +0.89 for the upper plates, though on only 4 points.
- Read as C3 to C7, the upper plates sit below Tan by more than any thoracic gap except T1's.
- At position 5 the lumbar reading fails. The L5 lower-plate gap of 8.7 deg is more than four times the largest thoracic lower-plate gap, 2.0. The C7 reading's gaps of 3.6 and 3.3 are smaller.

**Every independent L5 source puts L5 steeper than the printed row.** These values are the others reader's (work/others/epi_values.csv).

- L5 lower plate:
  - printed 1.8 +/- 0.42;
  - tan2004 +10.5 +/- 0.8. With Tan's SEM taken as printed, z = -9.6; with SD = SEM x 10 instead of SEM x sqrt(10), z = -3.4;
  - gilad1985: 6.8, derived from mean corner distances of 156 films of living men aged 20 to 38 (Table 1, p. 118, PDF 4; Fig. 1, p. 116, PDF 2). Inference: a two-dimensional analogue, not a fitted plane;
  - bonczar2024's pooled 8.20 (SE 3.72; p. 9, PDF 9), even though the pool contains Panjabi's 1.8.
- L5 upper plate: printed 2.2 against Tan's 6.9 (z -4.5, or -1.6 on the other SEM reading).
- L5 body wedge. The printed pair caps it at 2.2 + 1.8 = 4.0 deg, with a 95% upper limit of 5.3 (SEMs added in quadrature; Inference). The eight independent values are one each from seven sources, two from Abbas (men and women):
  - tan2004 3.9;
  - gilad1985 4.4;
  - frontphys2026 5.3 (5.27; 100 living adults, CT, depth borrowed);
  - bonczar2024 5.65;
  - moncadahabib2025 6.5 (37 living adults, CT);
  - abbas2021 6.9 (men) and 7.0 (women) (90 control men and 90 control women, CT, read off Figs. 5 and 6, pp. 4 and 5);
  - busscher2010 7.2 (6 cadaver spines, CT).
  - Seven of the eight exceed 4.0. Five clearly exceed 5.3, and frontphys2026 sits at it. Without bonczar2024, which contains Panjabi, six of seven exceed 4.0 and four of seven exceed 5.3. All of these wedges are Inference from printed heights and depths.
- At L4 there is no conflict. The sources give wedges from -0.3 to +2.2, against a printed cap of 4.7 + 2.7 = 7.4.

**Read as cervical, the row passes the only test that binds.** The cervical body wedges from tan2004, busscher2010, gilad1985 and kunkel2011 run from -6.6 to +0.3 deg.

- Every one is inside the printed caps except Tan's C5, at 6.6 in size. That exceeds the point cap of 1.7 + 2.7 = 4.4 but not its 95% limit of 6.7.
- At C7 the wedges are -0.6 to -2.2 against a cap of 4.0.

**What does not compare.**

- gilad1985's cervical corner lines run to the anterior lip and give 5 to 14 deg, which is not a fitted-plane angle.
- bonczar2024 pools Panjabi's unsigned values with Tan's signed ones, so its values are not independent. Its Table 1 (p. 3, PDF 3) also labels Panjabi 1992 as radiographs from India, which is wrong.
- vanderhouwen2009's disc wedges (L4-L5 9.5 deg, Fig. 3, p. 39, PDF 7) depend on how two vertebrae sit, which per-vertebra angles do not fix.

**Summary of the outside evidence (Inference).**

- At positions 1 to 4, small tilts fit either region, and they fit Tan's lumbar values somewhat better.
- At position 5 the outside evidence contradicts the lumbar reading, and contradicts the cervical reading less.

### 2.3 Errata and later readers

**No erratum, correction or letter was found** for either paper.

- PubMed records: lumbar PMID 1566168, cervical PMID 1948369 and thoracic PMID 1948374 carry no erratum or comment link, and their efetch XML has no CommentsCorrections element.
- Panjabi's 16 Spine papers of 1991 and 1992 have no correction link.
- Europe PMC's commentCorrectionList is empty for all three papers. Crossref holds no update relation on the three DOIs: 10.1097/00007632-199203000-00010 (lumbar), 10.1097/00007632-199108000-00001 (cervical) and 10.1097/00007632-199108000-00006 (thoracic).
- All 1,170 PubMed records of Spine for 1991 to 1993 were scanned. Two carry an erratum link, and neither is Panjabi's: PMID 1387977 and PMID 1825891.
- All 80 PubMed letters and comments in Spine for 1991 to 1995 were read. Five touch vertebral topics, and none comments on these papers.
- Caveat: PubMed indexed few Spine errata in those years (one standalone erratum in 1991, none in 1992 to 1996). The print issues were not read, because journals.lww.com returned 402. So the absence is weak evidence (Inference).

**The repeat is in the print, not in our scans.** Breglia's 2006 Ohio University MS thesis photocopies the cervical and lumbar Table 2 as Appendix D (p. 87) and Appendix L (p. 95); its printed pages match its PDF pages. Both show the same EPI rows; I checked the Appendix L image at errata/dl/breglia/ap-95.png.

**Later work copied the lumbar rows as printed, and nobody remarked on the repeat.**

- Kunkel, Schmidt and Wilke 2010, J Anat 216:320-328 (PMID 20039978). Read through a summary of the PMC HTML; the printed page was not read.
  - Its EPIS and EPII equations, cubic in VBHp, were fitted on Panjabi's T1 to T12 and L1 to L4 means.
  - Rerunning errata/kunkel_fit.py on bordercall's long table reproduces EPIS exactly: coefficients -66.833, 12.035, -0.691, 0.013; R2 0.606; residual SD 0.699. For EPII it reproduces the coefficients 66.233, -9.095, 0.418, -0.006 and SD 0.606, with R2 0.511 against the printed 0.514.
  - The thoracic inputs in the long table match my reading of p. 892.
  - Inference: Kunkel's four "lumbar" inputs are the cervical C3 to C6 numbers.
- Bellina et al. 2024, J Biomech 164:111951, Supplementary Table 1 (mmc1, PDF p. 2): cites Panjabi 1992 Table 2 for EPIS and EPII. A T1 to L5 refit comes close to its coefficients but not exactly (Inference).
- Ceran 2006, Loughborough PhD thesis, Fig. 8.3, printed p. 175 (PDF 193): the lumbar model's VBIus takes the printed EPItu (2.70, 3.50, 1.70, 4.70, 2.20; errata reader). Its VBIls column holds -4.00, -2.10, -2.70, -2.70 and -1.80, which is the printed EPItl with its sign flipped; I checked the crop.
- Lavecchia 2018, Birmingham PhD thesis, Table 4.4 (p. 65, PDF 89): copies Breglia's regressions but drops EPItu and EPItl.
- tan2004 Table 2, pp. 142 to 143 (PDF 6 to 7): sets 16 parameters beside Panjabi's, and end-plate inclination is not among them.
- Semantic Scholar: 484 papers cite the lumbar paper, 135 of them with context snippets. 465 cite the cervical paper, 137 with snippets. No snippet mentions the repeat.
- **No republication by Panjabi's group** was found. A PubMed title search found 11 Panjabi anatomy records, and the only ones from this specimen set are the three papers and panjabi1993f, which reports no end-plate inclination. The 1990 second edition of White and Panjabi was not reached; Inference: it predates both papers, so it cannot hold the 1992 table as published.

## 3. What it means for the rule

**What the rule does with these two measures today.** Facts from bordercall/schwingcheck:

- Both measures are in the pool of 32. Neither is among the seven, and no measurer reads either one (schwingcheck/README.md, "The pool"): the archive's spineps_map.py measures only the seven. So no result on a real spine has used them yet.
- The rule takes a measure only if the table has a row at every level it runs over. measures.select refuses a measure that lacks one, and measures.pool leaves it out (schwingcheck/measures.py).
- Each angle enters as a normal. Its table SD is SEM x sqrt(12) (schwingcheck/table.py, line 275), and its measurement error is 3 deg (schwingcheck/README.md, "Each kind its own term").

**The options at L1 to L5.**

1. Keep the lumbar row as printed. Not recommended.
   - The L5 cells conflict with every independent L5 source, and L1 to L4 are, most probably, cervical numbers.
   - Inference, from the rule's own terms: on a real spine, a body whose lower plate tilts 10.5 deg (tan2004's L5 mean) would score -5.53 as L5 against -3.56 as L1 and -3.79 as L3 (log density per body). On this one measure that makes it 2.0 nats more like an L1 than an L5.
2. Mark L1 to L5 missing. As the code stands, this is the same as dropping both measures over C3 to L5.
   - Teaching the rule to leave out a term wherever the table has no row would compare places on unlike terms (Inference).
   - A present angle term is at most about -2.0 nats per body. That is the peak log density of a normal with SD 3 deg, -2.02, and -2.08 at T12's lower plate. An absent term is 0.
   - So every body placed in L1 to L5 would gain about 2 nats per measure over one placed at T12 or above. That bias lands at the thoracolumbar border, which is the call bordercall exists to make.
   - A missing level needs a stand-in density, such as a wide prior over the unknown mean, not an absent term.
3. Replace the values from tan2004. For both angles Tan prints all 22 levels, C3 to L5 (Table 1, pp. 140 to 141, PDF 4 to 5). A replacement should therefore take Tan's whole series. Replacing L1 to L5 alone would join two studies at T12/L1 whose thoracic plates differ by about 1 deg on average (the calibration above). The caveats:
   - the population: 10 Chinese Singaporean cadavers of mean age 65.7, against Panjabi's 12 of mean age 46.3;
   - the sign convention is never stated and is only inferred;
   - the SEM is ambiguous;
   - a measurer would have to read signed angles in the posterior-wall frame;
   - the generator would draw from the new table too, so every result with all 32 measures would be rescored.

   A signed series carries what an unsigned one cannot: Tan's lower plate changes sign between L2 and L3, and between the cervical and thoracic spines.
4. Drop both measures from the pool. Recommended for now.

**My recommendation.**

- **Now:** take option 4, and record the reason in measures.left_out: the lumbar rows reprint the cervical C3-C7 values, with a pointer to this note.
- Keep every cell in the provenance record and the long table as printed, flagged rather than changed, since that record's job is to show what the papers print.
- **Later, when a measurer for end-plate inclination exists:** come back with option 3, a whole C3-L5 series from tan2004, or better, a table from the CTs of TODO.md item 5 read by that same measurer.
- Why option 4 now:
  - nothing measured on a real spine depends on these measures;
  - their gain in the generator's world is small (below);
  - each other option adds an assumption nobody has checked.

**At C3 to C7.** The printed cells are the original as far as the papers can tell, so keep them as they are.

- If the measures leave the pool, they leave at C3 to C7 too, because the pool runs over all of C3 to L5.
- If a later rule takes measures over part of the levels, C3 to T12 may stand. The caveat: the cervical upper plates sit 1.1 to 5.4 deg below tan2004's, more than the thoracic gaps except at T1.

**Housekeeping (panjabi reader, small).**

- The archive's inventory gives EPItl and EPAl as C3-L5, but both are printed at C2 as well (EPItl 4.2 / 1.2; EPAl 194.4 / 9.64; p. 863, PDF 3).
- thoracic-t3 labels the printed "EPIlt" row as EPItl. That reading is right, but the misprint itself is worth noting.
- TODO.md line 16 can point to this note.

**What the synthetic results keep and lose.** The generator draws from the same table, so its own world is consistent, and the identical rows at C3-C7 and L1-L5 are simply two runs of levels these angles cannot tell apart while the other measures can.

- **Kept whole:**
  - everything on the seven (rung 0): the archive record of 2026-10-26 (exact.json with its 127 subsets) and its rescore;
  - 73.1% of three-body fields named exactly;
  - any run on SPINEPS masks, since the measurer reads only the seven;
  - the prefixes of the greedy order up to step 23, and every subset without the two angles, such as the seven with the pedicles, the processes and the facets (24 measures).
- **Kept as statements about the generator's world only:**
  - every result with all 32 measures, such as 98.3% at three bodies;
  - the prefixes from step 24 on;
  - the family "the rest of the body and the canal" (the seven plus endplate_area, endplate_lower_area, the two angles and canal_area, 12 measures);
  - the angle subsets;
  - the lateral view;
  - the robustness arms run on all 32.
- **Lost as claims about real spines:** whatever these numbers owe to the two measures, which in that world is small (schwingcheck/README.md, the curve table, rows 23 to 24 and 30 to 31):

| Step | Measure added | Named exactly, 1 body | Named exactly, 3 bodies | Named at 0.99, 3 bodies |
|---|---|---|---|---|
| 24 | endplate_incl | 84.1% to 84.5% | 97.4% to 97.5% | 82.4% to 83.0% |
| 31 | endplate_lower_incl | 86.9% to 87.0% | stays 98.2% | 86.6% to 86.8% |

  Inference: dropping both would lower the all-32 figures by about half a point at one body and a few tenths at three. Only a rescore can say exactly, because the greedy order after step 24 was chosen with them in.
- On a real spine the cost of keeping them would not be this small gain. It would be the misdirection shown in option 1, at L5 and at the T12/L1 border.

## 4. What is still not known

- **Panjabi's real lumbar values.** His twelve spines' lumbar EPItu and EPItl appear in no printed source found, though the lumbar paper's Table 1 lists the measure and its abstract claims angular dimensions of the bodies (p. 299, PDF 1).
- **How the duplication arose,** in which file, and whether any other lumbar cell came from the same slip. The repeat search finds no other repeated run longer than two values.
- **Whether the cervical values are right.** Beyond agreeing with their own text, they are unconfirmed: they sit below tan2004's by more than the thoracic calibration gap at the upper plate, which could reflect population or method (Tan's spines are older; how the end-plate points were chosen around the uncinate processes is not stated).
- **The sign conventions.** Panjabi prints no sign, and his cervical and thoracic figures draw opposite senses; tan2004 states no convention, and its SEM is ambiguous.
- **Sources not reached:**
  - the Spine print issues of 1991 to 1993, read for an erratum;
  - Tan 2002 (Eur Spine J 11:152-158), whose full text Europe PMC indexes with EPItu and EPItl (Inference: perhaps the same lumbar spines as tan2004, so not independent of it);
  - later editions of White and Panjabi, and Miele, Panjabi and Benzel 2012;
  - Kunkel 2010's printed page, and Lavecchia's 2018 journal paper;
  - Kumar 2000 (Anat Rec) and Masharawi 2008 (Clin Anat).
- **Whether the L1 to L4 fit to tan2004 is chance.** It rests on four levels, against a cervical fit that is worse.
- **What a measurer would read on CT or a SPINEPS mask.** No measurer yet reads a fitted-plane end-plate angle in the posterior-wall frame, so how such a reading compares with a cadaver digitizer's is not measured.
