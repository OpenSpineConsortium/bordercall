# Validation of the readings: the blind re-read and the plausibility flags

Source: thread "Plan clinical reread next steps", project symphony_2, 2026-10-29, on the branch of pull request 39
at ed111b5, for the owner's ask of 2026-10-29 15:15 UTC that the measures and their data be shown to be of good
quality (../../clinical-reread/HANDOFF.md, step 2, parts a, b and c). Confidential, like the rest of this repository. Everything here ran in a cloud session on the page images;
no grid job, nothing fetched.

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
`printed_as` column holds the whole printed string, "4.4 (1.0)", "+/-1.99", "17.6-30.54", "(42)" or "Ten", which
the first comparison matched as text and so called 53 reads wrong that were right). Three reads differed from
the record, and the adjudicator re-read each on the page (mismatches.csv, column `record` and `adjudication`):
all three are the reader's, where the locator alone did not say which printed number the cell holds (Ahn 2001's
32 patients behind the printed 5/32; Frontiers 2026's 8.8 mm segment beside the 25.2 mm line in Figure 1A; its
"10 - 20% difference" beside the 0.8 mm thickness in Discussion 4.3), and the record holds the printed number in
each.

The rate: 0 record faults in 468 cells, Wilson 95 percent interval 0.0 to 0.8 percent. Under the upper bound,
fewer than one cell in 120 of the 23,918 is a transcription fault, at most about 190 cells. The sample is of
printed numbers with a page; a cell read from text, a figure or a quoted source is in it in proportion, and a
cell whose locator is ambiguous is the one kind the re-read cannot judge.

Rerun: `python3 -I tools/validation_sample.py data/readings <out>`, readers over `<out>/tasks/` writing
`<out>/reads/`, then `python3 -I tools/validation_compare.py <out> --adjudicated validation/mismatches.csv`.

## The plausibility flags (step 2b)

tools/plausibility.py over data/series.csv (3,760 series) and the cohorts files: an outlier beyond four scaled
median absolute deviations of the other papers' means at the same measure and level (among series standing to
Panjabi's definition the same way, four other papers at least), an SD above the mean of a size, a count above
the cohort's people, and a step between neighbouring levels against the direction four or more other papers
agree on, at least half their median step. flags.csv is the run: 116 flags over 24 papers, 69 outliers and 47
reversals, 35 of them on values a paper quotes from another study; no SD above its mean and no count above its
cohort's people, which the four review rounds had already caught.

Four checkers, each a share of the papers, found every flagged cell in the readings and read it again from the
page at 300 dpi (flags_checked.csv, one row a flag with the printed value and the page): 116 record_right, no
record_wrong, no mapping fault, none unreadable. So each outlier is the paper's own (Ahn 2001's Marfan patients'
interpediculate distances; Mitra 2002's two female cadavers; Olsewski 1990's radiographic sagittal diameters,
daggered by the paper as above its direct ones; Tan 2004's ten Singaporean Chinese cadavers; Griffith 2016's and
Shin 2024's quoted comparators), and each reversal a step the paper prints and often names in its text (Lien
2007's L1 pedicle below L2; Yadav 2020's quoted Singh et al. width falling at L3; Zindrick 1987's T12 below T11).

Rerun: `python3 -I tools/plausibility.py data/series.csv data/cohorts tools/vocabulary.csv validation/flags.csv`.

## The mapping audit (step 2c)

The question: is each number mapped to what the paper measured? mapping_sheet.csv is the unit of audit: every
distinct (measure_label, key, factor, technique) a paper's own values carry, 765 over the 39 papers, with the
vocabulary's definition, the reading's own definition of the paper's measure, the units and canonical units,
the technique and vs_panjabi. Ten auditors, three or four papers each, read each row against the paper's
methods, figures and table headings (the PDF's text, the page rendered where a figure mattered, the paper's note)
and judged the key, the level and side conventions, the units and factor, the technique and vs_panjabi; a flag was
anything a second reader should look at. They flagged 109 rows of 765 (63 on the key, 29 on vs_panjabi, 10 on the
level, 6 on units, 1 on technique) and found 656 to fit.

Five refuters, each a share of the flagged papers, then tried to show each flag wrong from the paper's own
words (mapping_audit.csv, one row a flag with the verdict, the fix and the reason): 51 refuted, 41 judgement
(the paper settles neither reading; what each rests on is written), 17 held. The 17 were fixed in the readings
on 2026-10-29, each cell's note saying so:

- Otsuki 2021's "longitudinal diameter (major axis of isthmus)" is the longest diameter of the isthmus section
  perpendicular to the pedicle axis (pp. 3 to 4, Fig. 2), oblique at a lumbar pedicle (L5 24.2 mm against
  Panjabi's PDH 19.6), so its pedicle_h rows are differs, not close: five series leave the comparison, the one
  fix that reaches it.
- Bach 2019's "maximum height of the interbody space" is printed L4/5 but is Figure 8's L5/S1 (8.900 and 8.566;
  the Results give L5/S1 women 8.6 +/- 1.8): level L5-S1. Hou 1993's Discussion "pedicle depth parallel to the
  midline" prints L1 but 50.3 and 48.6 are Table 3's L2 means: level L2.
- Eisenstein 1977's 20 mm lower limit of normal is the dry-bone 18 mm greatest interpedicular distance times the
  film's magnification 1.14 (p. 175): keyed canal_w with the paper's other greatest-interpedicular rows, not
  interpedicular.
- Kunkel 2011's percent-of-average-disc-height rows (Table 3's column, the Abstract's and Results' 22.7, 40, 21.25
  and 21 percent) take factor 0.01 to the ratio disc_index's unit is, as the Figure 3 cells already did.
- Masharawi 2021's "DS more sagittal than control" 10 deg is Table 2's L4 inter-facet difference, the angle between
  the two joint lines: keyed other with the TIFA rows, not facet_angle_axial.
- Yu 2015's two "PH difference" cells name their level (L1 for 2.07 mm, L2 for 0.94) in the note; Abbas 2021's
  note that the Results and the Discussion assigned the shares to opposite groups was wrong; Alonge 2021's
  Table 3 and 4 notes already said one reading per patient at the level, so nothing changed there.

The 41 judgements stand as mapped, each with what the other reading would rest on, and these reach the comparison
if read the other way: Chen 2011's end-plate sagittal diameter (differs by the authors' own words setting it
apart from Panjabi, p. 1819; close by its landmarks, the rims on the midsagittal plane, where Busscher 2010's
same chord is graded same); Alonge 2021's canal AP diameter (same, where Abbas 2021's and Ahmed 2019's are close);
Olsewski 1990's sagittal pedicle angle (differs, since Panjabi's PDIt is drawn from the plane square to the
posterior wall and Olsewski's from the end-plate line in the opposite sense; close if Panjabi's drawing is read as
schematic); Arockiaraj 2025's pedicle height (close by "superior and inferior cortex at the isthmus", or the inner
height by its values, 4 to 8 mm under every CT series it quotes); Busscher 2010's pedicle angle (its line is
pinned at the anterior body midline, not the pedicle axis); Amonoo-Kuofi 1985's body AP diameter (maximum or
mid-waist, the Methods say both). The owner's word settles these; none was changed. Two findings outside the
readings: the vocabulary's own definition of spinous_length ("from the posterior wall of the canal") matches
neither Panjabi nor Tan 2004, and Bonczar 2024's Figure 2 swaps the words of its end-plate width and depth, where
the readings key by value (31 to 34 mm cannot be a lumbar end-plate's mediolateral span).

Rerun: the sheet is built from data/readings/ (one row per distinct measure_label, key, factor and technique of
the paper's own values, subject and summary keys left out); the audits and refutations are readers' work.

## What this does and does not show

The numbers in the readings are the numbers on the pages, to within one cell in 120 at worst; no value a rule
finds implausible is a misread; and of 765 mappings, 17 were wrong in a way the paper settles, one of them
reaching the comparison, with 41 open to a second reading that the owner settles. What it does not show is
whether a paper's own number is right, which no re-read of its page can tell.
