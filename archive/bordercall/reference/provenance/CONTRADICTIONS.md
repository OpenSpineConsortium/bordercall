# Where the four Panjabi papers contradict themselves

Written by `python3 contradictions.py` from the provenance record of 27 October 2026 (README.md), for the owner's
ask of that day: a report of all the contradictions in the papers between tables, as a measure of how carefully
the numbers were carried from the measurement tables into the rest of each paper. Three records feed it, each
held by test to the images of the cells: [crosstable.csv](crosstable.csv), the Present Study column of every
comparison table against the dimension tables it restates; [prose.csv](prose.csv), every number the running
text states against the cells it speaks of; and the arithmetic inside the tables, computed here, the printed
ratio columns against the ratio of the printed means and the printed sums against their parts. A ratio or a
sum is consistent when some unrounded means inside the rounding of the printed ones give a value that rounds to
the printed one, so a difference that rounding alone explains is not a contradiction. Nothing here speaks of
the measurements' accuracy, which no record of a paper can test; it speaks of the papers' internal
consistency, which is what a reader has.

## Summary

| paper | cells read | text values | held to cells | contradict | within a stated tolerance only | restated by a comparison table | disagree | ratios and sums checked | inconsistent |
|---|---|---|---|---|---|---|---|---|---|
| Cervical, Spine 1991;16(8):861-869 | 589 | 35 | 26 | 1 | 2 | 35 | 0 | 29 | 0 |
| Thoracic, Spine 1991;16(8):888-901 | 1688 | 70 | 50 | 6 | 6 | 108 | 1 | 96 | 3 |
| Lumbar, Spine 1992;17(3):299-306 | 515 | 51 | 40 | 3 | 1 | 45 | 1 | 25 | 0 |
| Articular facets, Spine 1993;18(10):1298-1310 | 994 | 93 | 77 | 8 | 14 | 25 | 6 | 138 | 3 |
| all four | 3786 | 249 | 193 | 18 | 23 | 213 | 8 | 288 | 6 |

The 26 contradictions of the text and the comparison tables, by what the cells show:

| what happened | count |
|---|---|
| a range whose end is not the table's extreme | 7 |
| a restated mean that is not the mean of the printed sides | 7 |
| a figure no table prints | 5 |
| a round figure the table's value does not round to | 2 |
| one side of a right-left pair quoted as the value | 2 |
| the average of the upper and lower increases given as one of them | 2 |
| one digit off | 1 |

## Between tables: the comparison tables against the dimension tables

Each paper's comparison table restates its own means beside earlier studies' (cervical Table 7, thoracic Table 8,
lumbar Table 6, facets Tables 9 and 10). crosstable.csv holds every restated value to the dimension table it comes
from: a single-sided dimension to the digit, a paired one as the mean of right and left to the comparison table's
rounding. Those that do not hold:

| comparison table | level | measure | prints | the dimension table gives | difference | what happened | cells |
|---|---|---|---|---|---|---|---|
| thoracic Table 8A | T3 | EPDl | 23.2 | 23.3 (the cell) | -0.1 (0.4%) | one digit off | [r03_c01](cells/thoracic-t8a/r03_c01.png); [r07_c02](cells/thoracic-t3/r07_c02.png) |
| lumbar Table 6 | L4 | PDIs | 16.0 | 16.55 (mean of right and left) | -0.55 (3.3%) | a restated mean that is not the mean of the printed sides | [r40_c01](cells/lumbar-t6/r40_c01.png); [r11_c03](cells/lumbar-t4/r11_c03.png) [r13_c03](cells/lumbar-t4/r13_c03.png) |
| facets Table 9 | C4 | FCHs | 12.0 | 12.15 (mean of right and left) | -0.15 (1.2%) | a restated mean that is not the mean of the printed sides | [r02_c01](cells/facets-t9/r02_c01.png); [r02_c02](cells/facets-t2/r02_c02.png) [r02_c03](cells/facets-t2/r02_c03.png) |
| facets Table 9 | C5 | FCHs | 11.3 | 11.6 (mean of right and left) | -0.3 (2.6%) | a restated mean that is not the mean of the printed sides | [r03_c01](cells/facets-t9/r03_c01.png); [r03_c02](cells/facets-t2/r03_c02.png) [r03_c03](cells/facets-t2/r03_c03.png) |
| facets Table 9 | C6 | FCHs | 10.8 | 10.95 (mean of right and left) | -0.15 (1.4%) | a restated mean that is not the mean of the printed sides | [r04_c01](cells/facets-t9/r04_c01.png); [r04_c02](cells/facets-t2/r04_c02.png) [r04_c03](cells/facets-t2/r04_c03.png) |
| facets Table 9 | C7 | FCHs | 11.0 | 11.4 (mean of right and left) | -0.4 (3.5%) | a restated mean that is not the mean of the printed sides | [r05_c01](cells/facets-t9/r05_c01.png); [r05_c02](cells/facets-t2/r05_c02.png) [r05_c03](cells/facets-t2/r05_c03.png) |
| facets Table 9 | C4 | FCWs | 11.3 | 11.5 (mean of right and left) | -0.2 (1.7%) | a restated mean that is not the mean of the printed sides | [r08_c01](cells/facets-t9/r08_c01.png); [r02_c00](cells/facets-t2/r02_c00.png) [r02_c01](cells/facets-t2/r02_c01.png) |
| facets Table 9 | C7 | FCWs | 13.4 | 12.55 (mean of right and left) | 0.85 (6.8%) | a restated mean that is not the mean of the printed sides | [r11_c01](cells/facets-t9/r11_c01.png); [r05_c00](cells/facets-t2/r05_c00.png) [r05_c01](cells/facets-t2/r05_c01.png) |

Not held to anything: facets Table 10 at S1, Ss (no cell of facets-t6 prints Ssr/Ssl at S1).

## The text against the tables

prose.csv holds every number the four papers state in their abstracts, results, discussions and figure labels
to the cells the sentence speaks of, under the rule the sentence states (one cell's value, the mean of right and
left, the end of a run, a ratio, a percentage, a count of rows) and a tolerance set for the sentence's own
rounding. The summary of the twelve spines that the cervical, lumbar and facets papers each print in their
Methods is held to the thoracic paper's Table 1, which each of them names as its specimens' record, so the one
number of it that does not hold, printed alike in all three, contradicts the first paper rather than its own
tables. Those that do not hold:

| paper, page | the sentence | says | the table gives | difference | what happened | cells |
|---|---|---|---|---|---|---|
| cervical, 861 | The subjects had an average age of 46.3 years (range, 19-59 years), weight of 67.8 kg (range, 54-85 kg), height of 167.8 cm (range, 157-178 cm), and male-to-female ratio of 8 to 4. | weight 85 | 84 (high) | 1 (1.2%) | a range whose end is not the table's extreme | [r00_c03](cells/thoracic-t1/r00_c03.png) [r01_c03](cells/thoracic-t1/r01_c03.png) [r02_c03](cells/thoracic-t1/r02_c03.png) [r03_c03](cells/thoracic-t1/r03_c03.png) [r04_c03](cells/thoracic-t1/r04_c03.png) [r05_c03](cells/thoracic-t1/r05_c03.png) [r06_c03](cells/thoracic-t1/r06_c03.png) [r07_c03](cells/thoracic-t1/r07_c03.png) [r08_c03](cells/thoracic-t1/r08_c03.png) [r09_c03](cells/thoracic-t1/r09_c03.png) [r10_c03](cells/thoracic-t1/r10_c03.png) [r11_c03](cells/thoracic-t1/r11_c03.png) |
| lumbar, 299 | The subjects had an average age of 46.3 (range, 19-59) years, weight of 67.8 (range, 54-85) kg, height of 167.8 (range, 157-178) cm, and the male/female ratio was 8/4. | weight 85 | 84 (high) | 1 (1.2%) | a range whose end is not the table's extreme | [r00_c03](cells/thoracic-t1/r00_c03.png) [r01_c03](cells/thoracic-t1/r01_c03.png) [r02_c03](cells/thoracic-t1/r02_c03.png) [r03_c03](cells/thoracic-t1/r03_c03.png) [r04_c03](cells/thoracic-t1/r04_c03.png) [r05_c03](cells/thoracic-t1/r05_c03.png) [r06_c03](cells/thoracic-t1/r06_c03.png) [r07_c03](cells/thoracic-t1/r07_c03.png) [r08_c03](cells/thoracic-t1/r08_c03.png) [r09_c03](cells/thoracic-t1/r09_c03.png) [r10_c03](cells/thoracic-t1/r10_c03.png) [r11_c03](cells/thoracic-t1/r11_c03.png) |
| lumbar, 301 | At L5, the width was 18.9 mm. | PDW L5 18.9 | 18.6 (lr_mean) | 0.3 (1.6%) | a figure no table prints | [r01_c04](cells/lumbar-t4/r01_c04.png) [r03_c04](cells/lumbar-t4/r03_c04.png) |
| lumbar, 302 | The cross-sectional area at L1 was about 62 mm2, and at L5, it was 81 mm2. | PIA L5 81 | 82.3 (lr_mean) | -1.3 (1.6%) | a figure no table prints | [r01_c04](cells/lumbar-t5/r01_c04.png) [r02_c04](cells/lumbar-t5/r02_c04.png) |
| thoracic, 890 | There existed a gradual increase from T1 to T12 in all four dimensions, ranging from 55% for the lower end-plate width to 73% for the upper end-plate depth (Figure 4A). | EPWl T12 over T1 T1-T12 55 | 51.44 (percent) | 3.56 (6.9%) | the average of the upper and lower increases given as one of them | [r05_c11](cells/thoracic-t3/r05_c11.png) [r05_c00](cells/thoracic-t3/r05_c00.png) |
| thoracic, 890 | There existed a gradual increase from T1 to T12 in all four dimensions, ranging from 55% for the lower end-plate width to 73% for the upper end-plate depth (Figure 4A). | EPDu T12 over T1 T1-T12 73 | 77.3 (percent) | -4.3 (5.6%) | the average of the upper and lower increases given as one of them | [r03_c11](cells/thoracic-t3/r03_c11.png) [r03_c00](cells/thoracic-t3/r03_c00.png) |
| thoracic, 890 | There was a gradual increase in the posterior vertebral height from a value of 14.3 mm at T1 to 22.7 mm at T12, an increase of 60% (Figure 4D). | VBHp T1 14.3 | 14.1 (equal) | 0.2 (1.4%) | a figure no table prints | [r09_c00](cells/thoracic-t3/r09_c00.png) |
| thoracic, 891 | The narrowest portion of the thoracic spinal canal occurred at T3, with a cross-sectional area of 189 mm2. | SCA T3 189 | 180 (equal) | 9 (5.0%) | a figure no table prints | [r07_c02](cells/thoracic-t4/r07_c02.png) |
| thoracic, 893 | The cross-sectional area at T3 was about 90 mm2, and at T11 it was 160 mm2. | PIA T3 90 | 95.5 (lr_mean) | -5.5 (5.8%) | a round figure the table's value does not round to | [r01_c02](cells/thoracic-t7/r01_c02.png) [r03_c02](cells/thoracic-t7/r03_c02.png) |
| thoracic, 893 | At T12, it decreased suddenly to 98 mm2 due to the inferior facets changing from the thoracic to the lumbar type. | PIA T12 98 | 92 (lr_mean) | 6 (6.5%) | one side of a right-left pair quoted as the value | [r01_c11](cells/thoracic-t7/r01_c11.png) [r03_c11](cells/thoracic-t7/r03_c11.png) |
| facets, 1298 | Excluding the superior C2 facet, the following minimum and maximum dimensions were found for the facets from C3 to L5: width = 9.6-16.3 mm | FCW C3-L5 9.6 | 9.5 (low) | 0.1 (1.1%) | a range whose end is not the table's extreme | [r01_c00](cells/facets-t2/r01_c00.png) [r02_c00](cells/facets-t2/r02_c00.png) [r03_c00](cells/facets-t2/r03_c00.png) [r04_c00](cells/facets-t2/r04_c00.png) [r05_c00](cells/facets-t2/r05_c00.png) [r06_c00](cells/facets-t2/r06_c00.png) [r07_c00](cells/facets-t2/r07_c00.png) [r08_c00](cells/facets-t2/r08_c00.png) [r09_c00](cells/facets-t2/r09_c00.png) [r10_c00](cells/facets-t2/r10_c00.png) [r11_c00](cells/facets-t2/r11_c00.png) [r12_c00](cells/facets-t2/r12_c00.png) [r13_c00](cells/facets-t2/r13_c00.png) [r14_c00](cells/facets-t2/r14_c00.png) [r15_c00](cells/facets-t2/r15_c00.png) [r16_c00](cells/facets-t2/r16_c00.png) [r17_c00](cells/facets-t2/r17_c00.png) [r18_c00](cells/facets-t2/r18_c00.png) [r19_c00](cells/facets-t2/r19_c00.png) [r20_c00](cells/facets-t2/r20_c00.png) [r21_c00](cells/facets-t2/r21_c00.png) [r22_c00](cells/facets-t2/r22_c00.png) [r01_c01](cells/facets-t2/r01_c01.png) [r02_c01](cells/facets-t2/r02_c01.png) [r03_c01](cells/facets-t2/r03_c01.png) [r04_c01](cells/facets-t2/r04_c01.png) [r05_c01](cells/facets-t2/r05_c01.png) [r06_c01](cells/facets-t2/r06_c01.png) [r07_c01](cells/facets-t2/r07_c01.png) [r08_c01](cells/facets-t2/r08_c01.png) [r09_c01](cells/facets-t2/r09_c01.png) [r10_c01](cells/facets-t2/r10_c01.png) [r11_c01](cells/facets-t2/r11_c01.png) [r12_c01](cells/facets-t2/r12_c01.png) [r13_c01](cells/facets-t2/r13_c01.png) [r14_c01](cells/facets-t2/r14_c01.png) [r15_c01](cells/facets-t2/r15_c01.png) [r16_c01](cells/facets-t2/r16_c01.png) [r17_c01](cells/facets-t2/r17_c01.png) [r18_c01](cells/facets-t2/r18_c01.png) [r19_c01](cells/facets-t2/r19_c01.png) [r20_c01](cells/facets-t2/r20_c01.png) [r21_c01](cells/facets-t2/r21_c01.png) [r22_c01](cells/facets-t2/r22_c01.png) [r01_c00](cells/facets-t3/r01_c00.png) [r02_c00](cells/facets-t3/r02_c00.png) [r03_c00](cells/facets-t3/r03_c00.png) [r04_c00](cells/facets-t3/r04_c00.png) [r05_c00](cells/facets-t3/r05_c00.png) [r06_c00](cells/facets-t3/r06_c00.png) [r07_c00](cells/facets-t3/r07_c00.png) [r08_c00](cells/facets-t3/r08_c00.png) [r09_c00](cells/facets-t3/r09_c00.png) [r10_c00](cells/facets-t3/r10_c00.png) [r11_c00](cells/facets-t3/r11_c00.png) [r12_c00](cells/facets-t3/r12_c00.png) [r13_c00](cells/facets-t3/r13_c00.png) [r14_c00](cells/facets-t3/r14_c00.png) [r15_c00](cells/facets-t3/r15_c00.png) [r16_c00](cells/facets-t3/r16_c00.png) [r17_c00](cells/facets-t3/r17_c00.png) [r18_c00](cells/facets-t3/r18_c00.png) [r19_c00](cells/facets-t3/r19_c00.png) [r20_c00](cells/facets-t3/r20_c00.png) [r21_c00](cells/facets-t3/r21_c00.png) [r22_c00](cells/facets-t3/r22_c00.png) [r01_c01](cells/facets-t3/r01_c01.png) [r02_c01](cells/facets-t3/r02_c01.png) [r03_c01](cells/facets-t3/r03_c01.png) [r04_c01](cells/facets-t3/r04_c01.png) [r05_c01](cells/facets-t3/r05_c01.png) [r06_c01](cells/facets-t3/r06_c01.png) [r07_c01](cells/facets-t3/r07_c01.png) [r08_c01](cells/facets-t3/r08_c01.png) [r09_c01](cells/facets-t3/r09_c01.png) [r10_c01](cells/facets-t3/r10_c01.png) [r11_c01](cells/facets-t3/r11_c01.png) [r12_c01](cells/facets-t3/r12_c01.png) [r13_c01](cells/facets-t3/r13_c01.png) [r14_c01](cells/facets-t3/r14_c01.png) [r15_c01](cells/facets-t3/r15_c01.png) [r16_c01](cells/facets-t3/r16_c01.png) [r17_c01](cells/facets-t3/r17_c01.png) [r18_c01](cells/facets-t3/r18_c01.png) [r19_c01](cells/facets-t3/r19_c01.png) [r20_c01](cells/facets-t3/r20_c01.png) [r21_c01](cells/facets-t3/r21_c01.png) [r22_c01](cells/facets-t3/r22_c01.png) |
| facets, 1298 | surface area = 72.3-211.9 mm2; | FCA C3-L5 72.3 | 69.4 (low) | 2.9 (4.2%) | a range whose end is not the table's extreme | [r01_c00](cells/facets-t4/r01_c00.png) [r02_c00](cells/facets-t4/r02_c00.png) [r03_c00](cells/facets-t4/r03_c00.png) [r04_c00](cells/facets-t4/r04_c00.png) [r05_c00](cells/facets-t4/r05_c00.png) [r06_c00](cells/facets-t4/r06_c00.png) [r07_c00](cells/facets-t4/r07_c00.png) [r08_c00](cells/facets-t4/r08_c00.png) [r09_c00](cells/facets-t4/r09_c00.png) [r10_c00](cells/facets-t4/r10_c00.png) [r11_c00](cells/facets-t4/r11_c00.png) [r12_c00](cells/facets-t4/r12_c00.png) [r13_c00](cells/facets-t4/r13_c00.png) [r14_c00](cells/facets-t4/r14_c00.png) [r15_c00](cells/facets-t4/r15_c00.png) [r16_c00](cells/facets-t4/r16_c00.png) [r17_c00](cells/facets-t4/r17_c00.png) [r18_c00](cells/facets-t4/r18_c00.png) [r19_c00](cells/facets-t4/r19_c00.png) [r20_c00](cells/facets-t4/r20_c00.png) [r21_c00](cells/facets-t4/r21_c00.png) [r22_c00](cells/facets-t4/r22_c00.png) [r01_c01](cells/facets-t4/r01_c01.png) [r02_c01](cells/facets-t4/r02_c01.png) [r03_c01](cells/facets-t4/r03_c01.png) [r04_c01](cells/facets-t4/r04_c01.png) [r05_c01](cells/facets-t4/r05_c01.png) [r06_c01](cells/facets-t4/r06_c01.png) [r07_c01](cells/facets-t4/r07_c01.png) [r08_c01](cells/facets-t4/r08_c01.png) [r09_c01](cells/facets-t4/r09_c01.png) [r10_c01](cells/facets-t4/r10_c01.png) [r11_c01](cells/facets-t4/r11_c01.png) [r12_c01](cells/facets-t4/r12_c01.png) [r13_c01](cells/facets-t4/r13_c01.png) [r14_c01](cells/facets-t4/r14_c01.png) [r15_c01](cells/facets-t4/r15_c01.png) [r16_c01](cells/facets-t4/r16_c01.png) [r17_c01](cells/facets-t4/r17_c01.png) [r18_c01](cells/facets-t4/r18_c01.png) [r19_c01](cells/facets-t4/r19_c01.png) [r20_c01](cells/facets-t4/r20_c01.png) [r21_c01](cells/facets-t4/r21_c01.png) [r22_c01](cells/facets-t4/r22_c01.png) [r01_c02](cells/facets-t4/r01_c02.png) [r02_c02](cells/facets-t4/r02_c02.png) [r03_c02](cells/facets-t4/r03_c02.png) [r04_c02](cells/facets-t4/r04_c02.png) [r05_c02](cells/facets-t4/r05_c02.png) [r06_c02](cells/facets-t4/r06_c02.png) [r07_c02](cells/facets-t4/r07_c02.png) [r08_c02](cells/facets-t4/r08_c02.png) [r09_c02](cells/facets-t4/r09_c02.png) [r10_c02](cells/facets-t4/r10_c02.png) [r11_c02](cells/facets-t4/r11_c02.png) [r12_c02](cells/facets-t4/r12_c02.png) [r13_c02](cells/facets-t4/r13_c02.png) [r14_c02](cells/facets-t4/r14_c02.png) [r15_c02](cells/facets-t4/r15_c02.png) [r16_c02](cells/facets-t4/r16_c02.png) [r17_c02](cells/facets-t4/r17_c02.png) [r18_c02](cells/facets-t4/r18_c02.png) [r19_c02](cells/facets-t4/r19_c02.png) [r20_c02](cells/facets-t4/r20_c02.png) [r21_c02](cells/facets-t4/r21_c02.png) [r22_c02](cells/facets-t4/r22_c02.png) [r01_c03](cells/facets-t4/r01_c03.png) [r02_c03](cells/facets-t4/r02_c03.png) [r03_c03](cells/facets-t4/r03_c03.png) [r04_c03](cells/facets-t4/r04_c03.png) [r05_c03](cells/facets-t4/r05_c03.png) [r06_c03](cells/facets-t4/r06_c03.png) [r07_c03](cells/facets-t4/r07_c03.png) [r08_c03](cells/facets-t4/r08_c03.png) [r09_c03](cells/facets-t4/r09_c03.png) [r10_c03](cells/facets-t4/r10_c03.png) [r11_c03](cells/facets-t4/r11_c03.png) [r12_c03](cells/facets-t4/r12_c03.png) [r13_c03](cells/facets-t4/r13_c03.png) [r14_c03](cells/facets-t4/r14_c03.png) [r15_c03](cells/facets-t4/r15_c03.png) [r16_c03](cells/facets-t4/r16_c03.png) [r17_c03](cells/facets-t4/r17_c03.png) [r18_c03](cells/facets-t4/r18_c03.png) [r19_c03](cells/facets-t4/r19_c03.png) [r20_c03](cells/facets-t4/r20_c03.png) [r21_c03](cells/facets-t4/r21_c03.png) [r22_c03](cells/facets-t4/r22_c03.png) |
| facets, 1298 | and Y-card angle = 5.8-66.1. | CAY C3-L5 5.8 | 4.1 (abs_low) | 1.7 (41.5%) | a range whose end is not the table's extreme | [r01_c01](cells/facets-t8/r01_c01.png) [r02_c01](cells/facets-t8/r02_c01.png) [r03_c01](cells/facets-t8/r03_c01.png) [r04_c01](cells/facets-t8/r04_c01.png) [r05_c01](cells/facets-t8/r05_c01.png) [r06_c01](cells/facets-t8/r06_c01.png) [r07_c01](cells/facets-t8/r07_c01.png) [r08_c01](cells/facets-t8/r08_c01.png) [r09_c01](cells/facets-t8/r09_c01.png) [r10_c01](cells/facets-t8/r10_c01.png) [r11_c01](cells/facets-t8/r11_c01.png) [r12_c01](cells/facets-t8/r12_c01.png) [r13_c01](cells/facets-t8/r13_c01.png) [r14_c01](cells/facets-t8/r14_c01.png) [r15_c01](cells/facets-t8/r15_c01.png) [r16_c01](cells/facets-t8/r16_c01.png) [r17_c01](cells/facets-t8/r17_c01.png) [r18_c01](cells/facets-t8/r18_c01.png) [r19_c01](cells/facets-t8/r19_c01.png) [r20_c01](cells/facets-t8/r20_c01.png) [r21_c01](cells/facets-t8/r21_c01.png) [r22_c01](cells/facets-t8/r22_c01.png) [r01_c03](cells/facets-t8/r01_c03.png) [r02_c03](cells/facets-t8/r02_c03.png) [r03_c03](cells/facets-t8/r03_c03.png) [r04_c03](cells/facets-t8/r04_c03.png) [r05_c03](cells/facets-t8/r05_c03.png) [r06_c03](cells/facets-t8/r06_c03.png) [r07_c03](cells/facets-t8/r07_c03.png) [r08_c03](cells/facets-t8/r08_c03.png) [r09_c03](cells/facets-t8/r09_c03.png) [r10_c03](cells/facets-t8/r10_c03.png) [r11_c03](cells/facets-t8/r11_c03.png) [r12_c03](cells/facets-t8/r12_c03.png) [r13_c03](cells/facets-t8/r13_c03.png) [r14_c03](cells/facets-t8/r14_c03.png) [r15_c03](cells/facets-t8/r15_c03.png) [r16_c03](cells/facets-t8/r16_c03.png) [r17_c03](cells/facets-t8/r17_c03.png) [r18_c03](cells/facets-t8/r18_c03.png) [r19_c03](cells/facets-t8/r19_c03.png) [r20_c03](cells/facets-t8/r20_c03.png) [r21_c03](cells/facets-t8/r21_c03.png) [r22_c03](cells/facets-t8/r22_c03.png) [r01_c05](cells/facets-t8/r01_c05.png) [r02_c05](cells/facets-t8/r02_c05.png) [r03_c05](cells/facets-t8/r03_c05.png) [r04_c05](cells/facets-t8/r04_c05.png) [r05_c05](cells/facets-t8/r05_c05.png) [r06_c05](cells/facets-t8/r06_c05.png) [r07_c05](cells/facets-t8/r07_c05.png) [r08_c05](cells/facets-t8/r08_c05.png) [r09_c05](cells/facets-t8/r09_c05.png) [r10_c05](cells/facets-t8/r10_c05.png) [r11_c05](cells/facets-t8/r11_c05.png) [r12_c05](cells/facets-t8/r12_c05.png) [r13_c05](cells/facets-t8/r13_c05.png) [r14_c05](cells/facets-t8/r14_c05.png) [r15_c05](cells/facets-t8/r15_c05.png) [r16_c05](cells/facets-t8/r16_c05.png) [r17_c05](cells/facets-t8/r17_c05.png) [r18_c05](cells/facets-t8/r18_c05.png) [r19_c05](cells/facets-t8/r19_c05.png) [r20_c05](cells/facets-t8/r20_c05.png) [r21_c05](cells/facets-t8/r21_c05.png) [r22_c05](cells/facets-t8/r22_c05.png) [r01_c07](cells/facets-t8/r01_c07.png) [r02_c07](cells/facets-t8/r02_c07.png) [r03_c07](cells/facets-t8/r03_c07.png) [r04_c07](cells/facets-t8/r04_c07.png) [r05_c07](cells/facets-t8/r05_c07.png) [r06_c07](cells/facets-t8/r06_c07.png) [r07_c07](cells/facets-t8/r07_c07.png) [r08_c07](cells/facets-t8/r08_c07.png) [r09_c07](cells/facets-t8/r09_c07.png) [r10_c07](cells/facets-t8/r10_c07.png) [r11_c07](cells/facets-t8/r11_c07.png) [r12_c07](cells/facets-t8/r12_c07.png) [r13_c07](cells/facets-t8/r13_c07.png) [r14_c07](cells/facets-t8/r14_c07.png) [r15_c07](cells/facets-t8/r15_c07.png) [r16_c07](cells/facets-t8/r16_c07.png) [r17_c07](cells/facets-t8/r17_c07.png) [r18_c07](cells/facets-t8/r18_c07.png) [r19_c07](cells/facets-t8/r19_c07.png) [r20_c07](cells/facets-t8/r20_c07.png) [r21_c07](cells/facets-t8/r21_c07.png) [r22_c07](cells/facets-t8/r22_c07.png) |
| facets, 1299 | The average age of the subjects was 46.3 years (range, 19-59), weight was 67.8 kg (range, 54-85), height was 167.8 cm (range, 157-178), and the male:female ratio was 8:4. | weight 85 | 84 (high) | 1 (1.2%) | a range whose end is not the table's extreme | [r00_c03](cells/thoracic-t1/r00_c03.png) [r01_c03](cells/thoracic-t1/r01_c03.png) [r02_c03](cells/thoracic-t1/r02_c03.png) [r03_c03](cells/thoracic-t1/r03_c03.png) [r04_c03](cells/thoracic-t1/r04_c03.png) [r05_c03](cells/thoracic-t1/r05_c03.png) [r06_c03](cells/thoracic-t1/r06_c03.png) [r07_c03](cells/thoracic-t1/r07_c03.png) [r08_c03](cells/thoracic-t1/r08_c03.png) [r09_c03](cells/thoracic-t1/r09_c03.png) [r10_c03](cells/thoracic-t1/r10_c03.png) [r11_c03](cells/thoracic-t1/r11_c03.png) |
| facets, 1305 | As seen in Figure 7A for the superior facets, the X-axis card angle CAX changed more or less in a linear fashion from about -41 deg at C2 to -86 deg at L5 with no dramatic changes in between. | CAXs C2 -41 | -37.1 (mean) | -3.9 (10.5%) | one side of a right-left pair quoted as the value | [r00_c00](cells/facets-t8/r00_c00.png) [r00_c02](cells/facets-t8/r00_c02.png) |
| facets, 1307 | C5 +9.8 -45.8 | CAYsr C5 +9.8 | 9.2 (equal) | 0.6 (6.5%) | a figure no table prints | [r03_c01](cells/facets-t8/r03_c01.png) |
| facets, 1307 | The angular characteristics that single out the cervical vertebrae are the relatively small angles made with the transverse plane (i.e., 30-50 deg), and large angles made with the sagittal plane. | Ts C2-C7 50 | 59.4 (high) | -9.4 (15.8%) | a range whose end is not the table's extreme | [r00_c00](cells/facets-t6/r00_c00.png) [r01_c00](cells/facets-t6/r01_c00.png) [r02_c00](cells/facets-t6/r02_c00.png) [r03_c00](cells/facets-t6/r03_c00.png) [r04_c00](cells/facets-t6/r04_c00.png) [r05_c00](cells/facets-t6/r05_c00.png) [r00_c02](cells/facets-t6/r00_c02.png) [r01_c02](cells/facets-t6/r01_c02.png) [r02_c02](cells/facets-t6/r02_c02.png) [r03_c02](cells/facets-t6/r03_c02.png) [r04_c02](cells/facets-t6/r04_c02.png) [r05_c02](cells/facets-t6/r05_c02.png) |
| facets, 1307 | The transverse plane angle of the facets is part of the uniform increase from 35 deg at C2 to 80 deg at L5. | Ts L5 80 | 85.55 (mean) | -5.55 (6.5%) | a round figure the table's value does not round to | [r22_c00](cells/facets-t6/r22_c00.png) [r22_c02](cells/facets-t6/r22_c02.png) |

Numbers the text rounds or approximates, held by the tolerance stated in prose.csv and not by the rounding of
the digits printed (23):

| paper, page | the sentence | says | the table gives | difference |
|---|---|---|---|---|
| cervical, 866 | In addition, from C3 to C7, the angle the pedicle axes made with the sagittal plane decreased from about 40 deg to about 29 deg (Figure 4D). | PDIs C3 40 | 42.25 (lr_mean) | -2.25 |
| cervical, 866 | In addition, from C3 to C7, the angle the pedicle axes made with the sagittal plane decreased from about 40 deg to about 29 deg (Figure 4D). | PDIs C7 29 | 29.9 (lr_mean) | -0.9 |
| thoracic, 890 | There was a gradual increase in the posterior vertebral height from a value of 14.3 mm at T1 to 22.7 mm at T12, an increase of 60% (Figure 4D). | VBHp T12 over T1 T1-T12 60 | 60.99 (percent) | -0.99 |
| thoracic, 891 | The cross-sectional area of the spinal canal remained relatively constant between T2 and T10, averaging 198 mm2 (Figure 5C). | SCA T2-T10 198 | 197.11 (mean) | 0.89 |
| thoracic, 893 | The progression of inclination relative to the sagittal plane decreased generally from approximately 27 deg at T1 and T2, to 10 deg at T12. | PDIs T1-T2 27 | 27.82 (mean) | -0.82 |
| thoracic, 893 | The cross-sectional area at T3 was about 90 mm2, and at T11 it was 160 mm2. | PIA T11 160 | 162 (lr_mean) | -2 |
| thoracic, 893 | The length of the process continued to be about 50 mm until T11, where it decreased to 46 mm. | SPL T1-T10 50 | 51.48 (mean) | -1.48 |
| thoracic, 898 | In our study, we found a vertebral wedge angle of 3.8 deg per vertebra, giving a total of approximately 45.6 deg for the entire thoracic spine; this is the bony angle. | sum of the wedge angles T1-T12 45.6 | 45.3 (sum) | 0.3 |
| lumbar, 302 | With progression down the lumbar spine, the ratio decreased to approximately 1.0 at L5. | PDH/PDW L5 1.0 | 1.06 (mean) | -0.06 |
| facets, 1304 | Note that the ratio had a magnitude of between 1.5 and 3 in the cervical region | IFW/IFH C2-C7 1.5 | 1.64 (low) | -0.14 |
| facets, 1304 | The superior facet angle decreased significantly from 116 deg at C2 to 75 deg at C3. | Ss C3 75 | 74.2 (abs_mean) | 0.8 |
| facets, 1304 | Continuing down the cervical spine, the average of the left and right sagittal plane angles increased from 75 deg at C3 to 80 deg at C7, as shown in Figure 6A. | Ss C7 80 | 82.85 (abs_mean) | -2.85 |
| facets, 1304 | In the thoracic spine from T2 to T11, these angles remained constant at approximately 70-75 deg. | Ss T2-T11 70 | 71.6 (abs_low) | -1.6 |
| facets, 1304 | In the thoracic spine from T2 to T11, these angles remained constant at approximately 70-75 deg. | Ss T2-T11 75 | 77.2 (abs_high) | -2.2 |
| facets, 1304 | With progression down the lumbar spine, the sagittal angle decreased from approximately 137 deg at L1 to 118 deg at L5. | Ss L5 118 | 118.7 (abs_mean) | -0.7 |
| facets, 1304 | From C2 to T4 the angle increased gradually from approximately 35 deg to 75 deg. | Ts C2 35 | 37.1 (mean) | -2.1 |
| facets, 1304 | From C2 to T4 the angle increased gradually from approximately 35 deg to 75 deg. | Ts T4 75 | 73 (mean) | 2 |
| facets, 1304 | In the lumbar spine, the transverse plane angle was slightly larger, approximately 80 deg. | Ts L1-L5 80 | 83.33 (mean) | -3.33 |
| facets, 1307 | The angular characteristics that single out the cervical vertebrae are the relatively small angles made with the transverse plane (i.e., 30-50 deg), and large angles made with the sagittal plane. | Ts C2-C7 30 | 33.5 (low) | -3.5 |
| facets, 1307 | The transverse plane angle of the facets is part of the uniform increase from 35 deg at C2 to 80 deg at L5. | Ts C2 35 | 37.1 (mean) | -2.1 |
| facets, 1307 | The CAY angle was approximately 16 deg throughout the thoracic region, similar to that of the middle and lower cervical spine regions, but very different from the lumbar spine region. | CAYsr T1-T12 16 | 15.24 (abs_mean) | 0.76 |
| facets, 1307 | The most significant difference between the individual thoracic vertebrae was the interfacet superior to inferior width ratio which decreased from 1.15 at T1 to 0.95 at T9. | IFWs/IFWi T1 1.15 | 1.18 (equal) | -0.03 |
| facets, 1307 | The most significant difference between the individual thoracic vertebrae was the interfacet superior to inferior width ratio which decreased from 1.15 at T1 to 0.95 at T9. | IFWs/IFWi T9 0.95 | 0.93 (equal) | 0.02 |

## Inside the tables: the printed ratios and sums against their parts

Every ratio column (end-plate width to depth, canal width to depth, pedicle height to width, facet width to height,
the interfacet ratios) and every printed sum (the thoracic wedge angle EPIt = EPItu + EPItl, Table 6's
costovertebral area per rib as the mean of the two upper facets plus the mean of the two lower, and its total
with the costotransverse area) is computed from the printed means of its own table. Consistent means that
unrounded means inside the printed ones' rounding can give the printed value.

| table | column | computed from | checked | consistent | not | largest difference |
|---|---|---|---|---|---|---|
| cervical Table 2 | EPWu/EPDu | EPWu / EPDu | 5 | 5 | 0 | -0.004 at C7 |
| cervical Table 2 | EPWl/EPDl | EPWl / EPDl | 6 | 6 | 0 | -0.004 at C5 |
| cervical Table 3 | SCW/SCD | SCW / SCD | 6 | 6 | 0 | -0.005 at C6 |
| cervical Table 4 | PDHr/PDWr | PDHr / PDWr | 6 | 6 | 0 | -0.036 at C7 |
| cervical Table 4 | PDHl/PDWl | PDHl / PDWl | 6 | 6 | 0 | -0.033 at C3 |
| thoracic Table 3 | EPWu/EPDu | EPWu / EPDu | 12 | 11 | 1 | -0.057 at T8 |
| thoracic Table 3 | EPWl/EPDl | EPWl / EPDl | 12 | 12 | 0 | -0.048 at T6 |
| thoracic Table 3 | EPIt | EPItu + EPItl | 12 | 12 | 0 | 0 at T2 |
| thoracic Table 4 | SCW/SCD | SCW / SCD | 12 | 12 | 0 | -0.049 at T4 |
| thoracic Table 5 | PDH/PDWr | PDHr / PDWr | 12 | 12 | 0 | 0.036 at T4 |
| thoracic Table 5 | PDH/PDWl | PDHl / PDWl | 12 | 10 | 2 | -0.446 at T3 |
| thoracic Table 6 | CVA | mean(CVAur, CVAul) + mean(CVAlr, CVAll) | 12 | 12 | 0 | 0.05 at T1 |
| thoracic Table 6 | CVA + CTA | CVA + mean(CTAr, CTAl) | 12 | 12 | 0 | -0.05 at T1 |
| lumbar Table 2 | EPWu/EPDu | EPWu / EPDu | 5 | 5 | 0 | -0.003 at L5 |
| lumbar Table 2 | EPWl/EPDl | EPWl / EPDl | 5 | 5 | 0 | -0.004 at L2 |
| lumbar Table 3 | SCW/SCD | SCW / SCD | 5 | 5 | 0 | 0.004 at L4 |
| lumbar Table 4 | PDHr/PDWr | PDHr / PDWr | 5 | 5 | 0 | -0.013 at L2 |
| lumbar Table 4 | PDHl/PDWl | PDHl / PDWl | 5 | 5 | 0 | -0.006 at L3 |
| facets Table 2 | FCW/FCHsr | FCWsr / FCHsr | 23 | 21 | 2 | -0.016 at C4 |
| facets Table 2 | FCW/FCHsl | FCWsl / FCHsl | 23 | 23 | 0 | 0.011 at T5 |
| facets Table 3 | FCW/FCHir | FCWir / FCHir | 23 | 23 | 0 | -0.011 at T2 |
| facets Table 3 | FCW/FCHil | FCWil / FCHil | 23 | 23 | 0 | 0.005 at C4 |
| facets Table 5 | IFWs/IFWi | IFWs / IFWi | 23 | 23 | 0 | -0.007 at T6 |
| facets Table 5 | IFW/IFH | mean(IFWs, IFWi) / mean(IFHr, IFHl) | 23 | 22 | 1 | -0.014 at T4 |

The 6 that rounding does not explain:

| table | column | level | prints | its parts give | difference | from | cell |
|---|---|---|---|---|---|---|---|
| thoracic Table 3 | EPWu/EPDu | T8 | 1 | 1.057 | -0.057 (5.4%) | EPWu 29.5 / EPDu 27.9 | [r11_c07](cells/thoracic-t3/r11_c07.png) |
| thoracic Table 5 | PDH/PDWl | T3 | 1.4 | 1.846 | -0.446 (24.2%) | PDHl 12.0 / PDWl 6.5 | [r10_c02](cells/thoracic-t5/r10_c02.png) |
| thoracic Table 5 | PDH/PDWl | T4 | 1.4 | 1.743 | -0.343 (19.7%) | PDHl 12.2 / PDWl 7.0 | [r10_c03](cells/thoracic-t5/r10_c03.png) |
| facets Table 2 | FCW/FCHsr | C4 | 0.96 | 0.976 | -0.016 (1.6%) | FCWsr 12.0 / FCHsr 12.3 | [r02_c04](cells/facets-t2/r02_c04.png) |
| facets Table 2 | FCW/FCHsr | C5 | 1.04 | 1.025 | 0.015 (1.5%) | FCWsr 12.3 / FCHsr 12.0 | [r03_c04](cells/facets-t2/r03_c04.png) |
| facets Table 5 | IFW/IFH | T4 | 1.04 | 1.054 | -0.014 (1.3%) | IFWs 22.1 and IFWi 21.1 / IFHr 20.9 and IFHl 20.1 | [r09_c05](cells/facets-t5/r09_c05.png) |

## What the counts say

- The dimension tables are arithmetically whole but for 6 entries: of the 288 ratios and sums they print, 282
  are what their own printed means give once rounding is allowed for, which is what columns computed from the
  unrounded means look like, since a ratio of two means printed to one decimal cannot be read back exactly.
  The 6 that are not differ by 0.014 to 0.446, the largest PDH/PDWl at thoracic Table 5 T3, printed 1.4 where PDHl 12.0 / PDWl 6.5 gives 1.846.
- The comparison tables restate 213 values and get 8 wrong (3.8%): one digit in the thoracic Table 8, and
  7 right-and-left means the lumbar Table 6 and the facets Table 9 print that are not the mean of the
  sides their own tables print, with no word on how they were formed; the largest is 0.85 mm.
- The running text states 193 numbers the tables also hold and contradicts them 18 times (9.3%): a side of a
  pair given as the value, a range whose end is not the table's extreme, an average given as one of its parts,
  a round figure past rounding, and figures no table prints, as the kinds above count them. No contradiction
  changes a table's value: the tables are the record of the measurements and the text restates them, so
  where the two differ the table stands.
- What this can be used for: these rates are the papers' own record of how often a number was carried wrongly
  from a measurement table into a sentence or a comparison table, and so a prior on the error of any hand copy
  of such a table, including the transcriptions this repository checks (README.md). They say nothing about the
  measurements: the standard errors in the tables are the papers' own statement of that, from twelve
  specimens, and only a re-measurement could test them.
