# Validation of the readings: the blind re-read and the plausibility flags

Source: thread "Plan clinical reread next steps", project symphony_2, 2026-10-29, on the branch of pull request 39
at ed111b5, for the owner's ask of 2026-10-29 15:15 UTC that the measures and their data be shown to be of good
quality (../../clinical-reread/HANDOFF.md, step 2, parts a and b; part c, the mapping audit, is not in this folder
yet). Confidential, like the rest of this repository. Everything here ran in a cloud session on the page images;
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

## What this does and does not show

The numbers in the readings are the numbers on the pages, to within one cell in 120 at worst, and no value a
rule finds implausible is a misread. What it does not show: whether each number was mapped to the right measure,
level, side, sex and units (step 2c, the mapping audit, one reader a paper and a refuter a flag, not done), and
whether a paper's own number is right, which no re-read of its page can tell.
