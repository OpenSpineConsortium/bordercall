# Validation of the readings: the blind re-read and the plausibility flags

Source: thread "Plan clinical reread next steps", project symphony_2, 2026-10-29, on the branch of pull request 39
at ed111b5, for the owner's ask of 2026-10-29 15:15 UTC that the measures and their data be shown to be of good
quality (../../clinical-reread/HANDOFF.md, step 2, parts a, b and c). Confidential, like the rest of this repository. Everything here ran in a cloud session on the page images;
no grid job, nothing fetched.

Reviewed on 2026-10-30 (thread "Finish the clinical reread", project symphony_5): one reader checked 84 claims of
this page against the files and the tools, rerunning the sampler, the comparison and the plausibility rule, and found
11 wrong or imprecise; another checked 71 claims of it and of mapping_audit.csv against the papers' pages and found
8. A refuter for each tried to show every finding wrong, reproducing the files from commit 66576c5 (the validation,
before the fixes) and 1119506 (the mapping audit with them), and held all 19; they are corrected here and in the
reasons of mapping_audit.csv. The papers support all 17 held fixes and the named judgements on their values and
definitions, and no correction changes a key, a level or a grade. The four items it left for the owner were settled
on 2026-10-30 (Decided, below): Abbas 2021's seven cells and Bach 2019's eight carry the corrected note, Mitra 2002's
18.5 is as printed, and Irie 2021's pedicle heights are close at L1 to L3. The record is
[review/](../../prior-art-measurement/review/README.md).

## The blind re-read (step 2a)

The question: how often does a cell of data/readings/ hold a number other than the one printed on the page? The
readings were made twice and reconciled on the page image, so the rate was expected to be low, but it had been
assumed, not measured.

The sample: tools/validation_sample.py, seed 2026, twelve cells a paper from the cells the paper itself prints with
a page to read, 468 cells over 39 papers and 141 pages, the same draw for anyone who runs it. A reader got
tasks/<paper>.csv, the locators without the value (table, page, row and column labels, level, side, sex, group,
statistic), and the page rendered at 200 dpi by pdftoppm, re-rendered at 300 dpi where the digits were small.

The readers: ten, each given three or four papers, told to read every cell from the image alone, never to open
the record, the readings or the notes, never to extract the PDF's text, and to write the number as printed with a
legibility and a note. Their reads are reads/<paper>.csv; every one of the 468 cells was read, 464 as clear and 4
as poor (Frontiers 2026's figure annotations, blurred screenshots in the paper itself).

The comparison: tools/validation_compare.py sets each read beside the record's number (the `value` column; the
`printed_as` column holds the whole printed string, "4.4 (1.0)", "+/-1.99", "17.6-30.54", "(42)" or "Ten", which the
first comparison matched as text and so called 53 reads wrong, 50 of them right). Three reads differed from the
record, and the adjudicator re-read each on the page (mismatches.csv, column `record` and `adjudication`): all three
are the reader's, where the locator alone did not say which printed number the cell holds (Ahn 2001's 32 patients
behind the printed 5/32; Frontiers 2026's 8.8 mm segment beside the 25.2 mm line in Figure 1A; its "10 - 20%
difference" beside the 0.8 mm thickness in Discussion 4.3), and the record holds the printed number in each.

The rate: 0 record faults in 468 cells, Wilson 95 percent interval 0.0 to 0.8 percent. Under the upper bound, 0.81
percent, fewer than one cell in 120 is a transcription fault: at most about 195 of the 23,918 cells, or about 120 of
the 14,795 the sample was drawn from. The sample is of the paper's own printed numbers with a page, 14,795 of the
23,918 cells (the statistics mean, SD, n, single, SE, median, min, max and range ends); a cell read from text or a
figure is in it as often as among its paper's own, twelve a paper (391 table, 55 text and 22 figure cells), while
the 3,119 cells quoted from other studies and the paper's own percents, p-values, SEMs, differences and the like are
outside it, so the rate is measured on the paper's own numbers; and a cell whose locator is ambiguous is the one
kind the re-read cannot judge.

Rerun: `python3 -I tools/validation_sample.py data/readings <out>`, readers over `<out>/tasks/` writing
`<out>/reads/`, then `python3 -I tools/validation_compare.py <out> --adjudicated validation/mismatches.csv`.

## The plausibility flags (step 2b)

tools/plausibility.py over data/series.csv (3,760 series) and the cohorts files: an outlier beyond four scaled median
absolute deviations of the other papers' means at the same measure and level (among series standing to Panjabi's
definition the same way, four other papers at least), an SD above the mean of a size, a count above the cohort's
people, and a step between neighbouring levels against the direction four or more other papers agree on, at least
half their median step. flags.csv is the run as it stood before the fix of 2026-10-29 to Irie 2021's (file
otsuki2021) isthmus diameters, its pedicle_h series then graded close: 116 flags over 24 papers, 69 outliers and 47
reversals, 35 of them on values a paper quotes from another study; no SD above its mean and no count above its
cohort's people, which the four review rounds had already caught. The Rerun line on today's series.csv gives the same
totals with one flag changed: Irie 2021's L5 longitudinal diameter 24.2 leaves with its stratum, Mitra 2002's L5
female roentgenogram pedicle height 18.5 enters (4.9 scaled MADs from 50 other papers' means) and has no row in
flags_checked.csv (read on the page on 2026-10-30: as printed, the mean of two specimens), and, with Irie 2021's
pedicle heights close at L1 to L3 since the decisions of 2026-10-30, 7 pedicle_h outliers at L4 and L5 carry new
medians and MADs.

Four checkers, each a share of the papers, found every flagged cell in the readings and read it again from the page
at 300 dpi (flags_checked.csv, one row a flag with the printed value and the page): 116 record_right, no
record_wrong, no mapping fault, none unreadable. So each outlier is the paper's own (Ahn 2001's Marfan patients'
interpediculate distances; Mitra 2002's two female cadavers; Olsewski 1990's radiographic sagittal diameters,
daggered by the paper as above its direct ones; Tan 2004's ten Singaporean Chinese cadavers; Ahmed 2019's,
Arockiaraj 2025's, Chaudhary 2015's, Hou 1993's, Masharawi 2021's and Mitra 2002's quoted comparators (El-Rakhawy,
Piera and Tacar; Dzierzanowski; Sudha Chhabra; Zindrick; Olsewski; Hou and Olsewski), 14 outliers in all), and each
reversal a step the paper prints and often names in its text (Lien 2007's L1 pedicle below L2; Yadav 2020's quoted
Singh et al. width falling at L3; Zindrick 1987's T12 below T11).

Rerun: `python3 -I tools/plausibility.py data/series.csv data/cohorts tools/vocabulary.csv validation/flags.csv`.

## The mapping audit (step 2c)

The question: is each number mapped to what the paper measured? mapping_sheet.csv is the unit of audit: every
distinct (measure_label, key, factor, units, canonical units, technique, vs_panjabi) a paper's own values carry, 765
rows over the 39 papers (596 distinct on measure_label, key, factor and technique alone), with the cells, tables and
pages each covers; the vocabulary's definition is in tools/vocabulary.csv and the reading's own definition of the
paper's measure in the readings' definition column, neither in the sheet. Ten auditors, three or four papers each,
read each row against the paper's methods, figures and table headings (the PDF's text, the page rendered where a
figure mattered, the paper's note) and judged the key, the level and side conventions, the units and factor, the
technique and vs_panjabi; a flag was anything a second reader should look at. They flagged 107 rows of 765 and found
658 to fit (the sheet's audit column); mapping_audit.csv holds 109 flags (63 on the key, 29 on vs_panjabi, 10 on the
level, 6 on units, 1 on technique), 104 on flagged rows and five on rows the sheet marks as fitting: Abbas 2021's
share of controls in range and four on Olsewski 1990's sagittal angle.

Five refuters, each a share of the flagged papers, then tried to show each flag wrong from the paper's own words
(mapping_audit.csv, one row a flag with the verdict, the fix and the reason): 51 refuted, 41 judgement (the paper
settles neither reading; what each rests on is written), 17 held. Of the 17, eleven changed a key, a level, a factor
or a grade in the readings on 2026-10-29, each cell's note saying so (Irie 2021's two rows, file otsuki2021; Bach
2019's; Hou 1993's; Eisenstein 1977's three; Kunkel 2011's two; Masharawi 2021's two); Yu 2015's and Abbas 2021's
changed a note (Abbas 2021's on three of the ten cells that carry it); Alonge 2021's four changed nothing, its Table
3 and 4 notes already saying one level, one sex. The 17, paper by paper:

- Irie 2021's (the file otsuki2021; results/README.md calls it Irie 2021) "longitudinal diameter (major axis of
  isthmus)" is the longest diameter of the isthmus section perpendicular to the pedicle axis (pp. 3 to 4, Fig. 2),
  oblique to the vertical at L4 and L5 by Robertson 2000's coaxial view (axis 31.0 to 55.0 deg there, under 8 deg at
  L1 to L3; Table 1, p. 711), so at L5 it exceeds the vertical extent (24.2 mm against Panjabi's PDH 19.6); its
  pedicle_h rows are therefore differs, not close: five series left the comparison, the one fix that reaches it;
  since 2026-10-30 that holds at L4 and L5 only, the section being upright at L1 to L3 (Decided, below).
- Bach 2019's "maximum height of the interbody space" is printed L4/5 but is Figure 8's L5/S1 (8.900 and 8.566; the
  Results give L5/S1 women 8.6 +/- 1.8): level L5-S1. Hou 1993's Discussion "depth of pedicle parallel to the
  midline" (p. 1852) prints L1 but 50.3 and 48.6 are Table 3's L2 LI means (p. 1853): level L2.
- Eisenstein 1977's 20 mm lower limit of normal is the dry-bone 18 mm greatest interpedicular distance times the
  film's magnification 1.14 (p. 175): keyed canal_w with the paper's other greatest-interpedicular rows, not
  interpedicular.
- Kunkel 2011's percent rows, of MDH over average disc height (Table 3's column, p. 379; the Abstract's and Results'
  22.7 and the Results' 40 percent, p. 380) as the Figure 3 cells already did, and of ADH over PDH (the Results'
  21.25 and 21 percent, p. 380) as the 2.77 percent row already did, take factor 0.01 to the ratio disc_index's unit
  is.
- Masharawi 2021's "DS more sagittal than control" 10 deg is Table 2's L4 inter-facet difference, the angle between
  the two joint lines: keyed other with the TIFA rows, not facet_angle_axial. - Yu 2015's two "PH difference" cells
  name their level (L1 for 2.07 mm, L2 for 0.94) in the note; Abbas 2021's note that the Results and the Discussion
  assigned the shares to opposite groups was wrong: the three Results cells for the controls' share now say the
  passages agree (mapping audit of 2026-10-29), while the two Results cells for the stenosis band and the five
  Discussion cells (the stenosis share and both bands) carried the old note until 2026-10-30, when they took the same
  correction; Alonge 2021's Table 3 and 4 notes already said one reading per patient at the level, so nothing changed
  there.

The 41 judgements were decided on 2026-10-30 (Decided, below). Two findings outside the readings: the vocabulary's
own definition of spinous_length ("from the posterior wall of the canal") matches neither Panjabi nor Tan 2004, and
Bonczar 2024's Figure 2 swaps the words of its end-plate width and depth, where the readings key by value (31 to 34
mm cannot be a lumbar end-plate's mediolateral span).

Rerun: the sheet was built from data/readings/ as they stood before the 17 fixes, one row per distinct
measure_label, key, factor, units, canonical units, technique and vs_panjabi of the paper's own values, the keys
other, prevalence, reliability and the subject keys left out; built from today's readings it has 763 rows and 15,174
cells, since 13 of its rows changed with the fixes: eleven stand in their corrected form (Eisenstein 1977's three
limits as canal_w, Kunkel 2011's six percent rows at factor 0.01 and unit ratio, Irie 2021's two as differs) and
Masharawi 2021's two deltas, now keyed other, leave it; the audits and refutations are readers' work.

## Decided on 2026-10-30

The owner left the 41 judgements to the session ("Can you decide?", 2026-10-30). They are 21 questions, of which
seven change what enters the comparison. One rule decided all of them: the key follows the paper's words, then its
figure, a value only breaking a tie the two leave; the grade is same or close where the landmarks, plane and sense
are Panjabi's and the construction moves the value little, differs where they or the construction move it materially;
what stays open is kept out of the comparison; like is graded like, and a grade may differ by level where the
geometry does. For each of the seven a judge read the pages and a checker tried to refute any decision that changed
the sheet or was not certain; the checker overturned one (Busscher 2010). Robertson 2000's bearing on Irie 2021, the
one owner item that was a judgement, went through the same two steps. Each row's decision is in the fix column of
mapping_audit.csv. The comparison, rerun in the same environment from the series as they stood before, reproduces the
committed record byte for byte, so every change in it comes from these decisions. The three items round 4 left open
were decided the same day (../review/round-4.md): Tan 2004's and Zindrick 1987's lateral thoracic pedicle angles are
a real disagreement, each paper's own stated sense, and stay in the comparison.

| Question | Decided | Cells |
| --- | --- | ---: |
| Masharawi 2021, facet width | differs, was close: an axial chord of the joint line against Panjabi's face-on facet, 1.2 to 6.7 mm above his | 89 |
| Irie 2021, pedicle height | close at L1 to L3, was differs: the section is within 7.5 deg of upright there (Robertson 2000), so the major axis is the height to 0.15 mm | 6 |
| Irie 2021, pedicle width | differs at L4, L5 and the average, was close: the same tilt leaves the minor axis 3 to 9 mm short of the width | 8 |
| Busscher 2010, PedA | close, kept: 0 to 3 deg at T10 to T12 (Fig. 8b) rule out a line pinned at the anterior midline, so it is the pedicle axis | 8 |
| Arockiaraj 2025, pedicle height | close, kept: Fig. 3A draws it between the outer outlines of the notches | 135 |
| Amonoo-Kuofi 1985, body depth | body_d_mid, kept: "measured at mid-waist level" (p. 72) | 20 |
| Chen 2011, end-plate diameter | differs, kept: the authors set it apart from the border-to-border extent Panjabi took | 60 |
| Olsewski 1990, sagittal angle | differs, kept: the end-plate line against the transverse plane, drawn in opposite senses | 129 |
| Alonge 2021, canal depth | same, kept: Panjabi's SCD landmarks, graded as the other CT papers with them | 138 |

The other 14 questions stand as read: every reading of them keeps the cells out of the comparison, and each map_note
already names the other. Alongside, Abbas 2021's seven cells and Bach 2019's eight took the corrected note,
and Mitra 2002's L5 female radiograph pedicle height was read on the page: 18.5 as printed, the mean of two
specimens.

## What this does and does not show

The numbers in the readings are the numbers on the pages, to within one cell in 120 at worst; no value a rule finds
implausible is a misread; and of 765 mappings, the refuters held 17 flags, 13 of them a fault the paper settles
(eleven in a key, level, factor or grade, two in a note), one of them reaching the comparison, with 41 open to a
second reading, decided on 2026-10-30 by one rule, which took Masharawi 2021's facet widths out of the comparison and
brought Irie 2021's upright pedicle heights in. What it does not show is whether a paper's own number is right, which
no re-read of its page can tell.
