# Where every number in Panjabi's four papers comes from

Every printed value of the numeric tables of the four Panjabi papers in [../papers/](../papers/)
is one row of [provenance.csv](provenance.csv), with the image of the cell it was read from, and
one page per table under [tables/](tables/) sets each value beside that image, so anyone can
check that it is true. This folder is step b of TODO.md's item P (the owner, 27 October 2026).

## How the numbers were read

**Rendered pages, read by eye, twice. Never by text extraction.** The papers are scans; a text
layer, where a PDF carries one, was never read (an earlier attempt to extract the thoracic canal
table by text produced plausible, wrong numbers). The steps, each a committed command or a
recorded reading:

1. **Render.** `python render.py` renders every page of the four PDFs at 300 dpi with
   `pdftoppm -r 300 -png -singlefile` (poppler 24.02.0), turning the thoracic paper's pages 6
   and 7, which print their tables sideways, by a quarter turn. [pages.json](pages.json) records
   each PDF's sha256, each rendered page's size and sha256, the dpi and the pdftoppm version, so
   a box in provenance.csv names a place on an image anyone can make again. `python render.py
   thoracic-p892` renders one key alone and merges it into the record, which is how the page
   that came later (below) was rendered without rendering the rest again.
2. **Lay out.** [tables.py](tables.py) says where each of the 28 numeric tables sits on its page
   (the region, the heading line, the body, the row labels' right edge) and what its rows and
   columns mean, in print order, with nothing numeric in it. [layout.py](layout.py) reads the
   pixels inside each region: it finds the rule lines and masks them, the lines of print, the
   column boundaries from the heading's labels, the page's tilt (corrected by a shear before the
   runs of ink are found), and each run of ink in each line, and cuts one box per run, with a
   5-pixel margin. [cells.csv](cells.csv) is the result, one row per box, and [cells/](cells/)
   holds the crop of every box. Every table's overlay (the boxes drawn on the page) was checked
   by eye before any reading began.
3. **Read, twice, independently.** Pass 1 read strips of whole rows with the column headings
   above them, eight rows at a time, and wrote one string per cell. Pass 2 read sheets of twenty
   numbered cell crops at twice their size, with no heading and no neighbour, and wrote one
   string per crop. The readers were Claude agents working from the images alone, 34 of one kind
   and 63 of the other, none of which saw the other pass, the CSVs or this repository's code. The
   conventions: `+/-` for the printed plus-minus sign, `^` for a dagger, `-` alone for a printed
   dash, `?` for a digit that could not be read. The two passes agreed on 3,533 of the 3,534
   cells at the first reading; the one they did not, the total per rib at T1 of the thoracic
   paper's Table 6, had a box that took in the tail of its row label, so it was cut again (the
   labels' edge of that table moved from 300 to 400 pixels, the one change to the layout) and
   read again by one fresh reader of each kind, who both read 132.0, as the first pass had.
   [reads/pass1.csv](reads/pass1.csv) and [reads/pass2.csv](reads/pass2.csv) keep every read as
   it was made, round by round, with who read it. The thoracic body table (Table 3, printed page
   892) was read on 27 October 2026 from the owner's second scan, the one page cut out as a file
   of its own ([../papers/README.md](../papers/README.md)), by the thread's own session in the
   same two presentations, the strips first and the numbered crops after, since no agent could
   be started that hour; the two readings agree on all 252 cells, the 120 values the archive's
   CSV carries from that table match to the digit, and Table 8's 36 restatements of it hold but
   one (below), three comparisons made independently of each other. Its digits at T7 and T12 of
   the ratio rows are printed pale, so its boxes were cut at a lighter ink threshold than the
   other tables' (`ink` in tables.py).
4. **Compile.** `python compile.py` sets the two reads beside each cell, parses the string into
   its values (a `mean +/- SEM` or `mean (SEM)` cell is two rows), gives each its units from
   Panjabi's mnemonic, and writes provenance.csv, the table pages and pages.json. A cell the
   passes read differently stays in provenance.csv with no value and `agree=no`; the test fails
   until it is read again (`python compile.py disagree` lists them).
5. **Read the prose, twice, independently.** Every number the four papers state in their
   abstracts, results, discussions and figure labels was read the same way, by two further
   passes over quadrant crops of every page, one reading the pages forward and one backward.
   What the papers print about their specimens was read on 27 October 2026 by two more passes:
   the number of vertebrae each abstract says the study rests on (4 numbers), the summary of the
   twelve spines that the cervical, lumbar and facets papers each print in their Methods (12
   numbers in each, 36), and three more from the facets paper's Methods, its 12 spines, 276
   vertebrae and 12 vertebrae at each level. The readers
   were Claude agents that saw nothing but the twenty quadrant crops of the five pages that hold
   them (`python render.py quadrants cervical-01 thoracic-01 lumbar-01 facets-01 facets-02`
   cuts them, each quadrant reaching 60 pixels past the page's middle), one reading forward and
   one backward, and they agreed on all 43 numbers. [prose_rows.py](prose_rows.py) is the record
   of each such number: where it is, the digits as printed, the cells it speaks of and the rule
   that turns them into the number (one cell's value, the mean of several, the lowest or highest
   of a run, the mean of a left and a right, a difference, a ratio, a percentage, a count of
   rows). `python prose_rows.py` writes [prose.csv](prose.csv) with what each pass read, and
   [reads/prose.csv](reads/prose.csv) keeps every prose read. The first passes' own files were
   never committed, so the script reads their reads back from that record, adds those of any
   later pass's files under archive/out/provenance/reads/, and makes prose.csv from the
   repository alone.
7. **Report the contradictions.** `python contradictions.py` writes
   [CONTRADICTIONS.md](CONTRADICTIONS.md) from the three records above and the arithmetic inside
   the tables (every printed ratio and sum against its own table's means, and every X-card angle
   of the facets paper's Table 8 against the negative of the transverse-plane angle its Tables 6
   and 7 print for the same facet, level and side, each allowing for rounding):
   every place a paper disagrees with itself, counted by paper and by what happened, for the
   owner's ask of 27 October 2026 that the papers' own consistency be measured.
6. **Hold the CSVs to it.** `python check_csv.py` sets every value of
   [../panjabi_full_spine.csv](../panjabi_full_spine.csv) and [../panjabi_1992.csv](../panjabi_1992.csv)
   beside the cell it should have come from and writes [changes.csv](changes.csv), the list of
   every existing value that differs.

The tests are [../../../tests/test_provenance.py](../../../tests/test_provenance.py): the two
passes agree on every cell; every cell was read by both; every value a paper also states in
prose agrees with its cells, or the record says, cell by cell, that the paper contradicts itself,
and a contradiction that stops holding fails the test too; prose.csv is what prose_rows.py makes
from the reads it keeps, and the specimens' summary in each of the three later papers is held to
Table 1 of the first; every value the CSVs carry was read
from a cell; each paper's comparison table restates its own dimension tables
as [crosstable.csv](crosstable.csv) records, which `python check_tables.py` writes (a single-sided
dimension to the digit, a paired one as the mean of right and left); the papers are the exact
bytes the record names; every image is there and every box lies on its page; every table page
shows every cell; the body table of page 892 was read from that one page alone; and the
contradictions report is what its code writes from the record.

## What is in provenance.csv

One row per printed value: 4,468 rows from 3,786 cells of 28 tables, of which
685 are printed dashes (a dash is a printed symbol with no value, kept so a reader knows the
absence was read, not missed). The columns:

| column | meaning |
|---|---|
| id | `table/cell/statistic`, the cell's name from cells.csv and which of its values this row is |
| paper, file, sha256 | the PDF the value was read from, and its exact bytes |
| pdf_page, printed_page | the page of the PDF and the page number printed on it |
| table, title | the table's key in tables.py and its printed title |
| row, col, row_label, col_label | the cell's place in the table and the labels printed on its row and column |
| study | `present` for Panjabi's own value; the other study's name in a comparison table |
| measure, level | Panjabi's mnemonic and the vertebral level |
| statistic | mean, sem, ratio, value, label or text |
| fmt | how the cell is printed: num, pm (`mean +/- SEM`), paren (`mean (SEM)`), ratio, label, text |
| printed | the string exactly as printed, in the conventions above |
| value, units, kind | the number this row carries, its units (mm, mm2, deg, years, kg, cm) and its kind (length, area, angle, ratio, count, mass, text) |
| dpi, x0, y0, x1, y1, image | the cell's box on the rendered page, and its crop under cells/ |
| pass1, pass2, agree | what each reading pass read, and whether they agree |
| note | what followed the number in the cell (a level note such as `(C3-5)`, a dagger), or why there is no value |

Every dispersion the papers print is a standard error of the mean, as each table's own note
says; the population SD is sem x sqrt(12).

## The inventory: what the four papers measure, and what can read it

Every mnemonic in the tables, what it measures, where it is tabulated, and what could read it
on a patient: a SPINEPS mask of a CT (the seven measures the rule uses today are marked), an AP
radiograph, a lateral radiograph, or only a CT. "Derived" is a ratio of two others.

| mnemonic | what it measures | levels | tables | mask | AP | lateral | CT only |
|---|---|---|---|---|---|---|---|
| EPWu, EPWl | upper and lower end-plate width | C3-L5 (EPWl from C2) | cervical 2, thoracic 3, lumbar 2 | yes, in use | yes | no | |
| EPDu, EPDl | upper and lower end-plate depth (anteroposterior) | C3-L5 (EPDl from C2) | the same | yes, in use | no | yes | |
| VBHp | posterior vertebral body height | C3-L5 | the same | yes, in use | no | yes | |
| EPWu/EPDu, EPWl/EPDl | end-plate width to depth | C3-L5 (lower from C2) | the same | derived | | | |
| EPAu, EPAl | upper and lower end-plate surface area | C3-L5 | the same | yes | no | no | |
| EPItu, EPItl | end-plate inclination to the transverse plane | C3-L5 | the same | yes | no | yes | |
| SCW, SCD | spinal canal width and depth | C2-L5 | cervical 3, thoracic 4, lumbar 3 | yes, in use | SCW | SCD | |
| SCW/SCD | canal width to depth | C2-L5 | the same | derived | | | |
| SCA | spinal canal cross-sectional area | C2-L5 | the same | yes | no | no | |
| PDWr, PDWl | pedicle width, right and left | C2-L5 | cervical 4, thoracic 5, lumbar 4 | yes | yes | no | |
| PDHr, PDHl | pedicle height | C2-L5 | the same | yes | no | yes | |
| PDH/PDW | pedicle height to width | C2-L5 | the same | derived | | | |
| PDAr, PDAl | pedicle cross-sectional area | C2-L5 | the same | yes | no | no | |
| PDIsr, PDIsl | pedicle axis inclination to the sagittal plane | C2-L5 | the same | yes | no | no | |
| PDItr, PDItl | pedicle axis inclination to the transverse plane | C2-L5 | the same | yes | no | yes | |
| SPL | spinous process length | C2-L5 | cervical 5, thoracic 7, lumbar 5 | yes | no | yes | |
| TPW | transverse process width (tip to tip) | C2-L5 | the same | yes | yes | no | |
| PIAr, PIAl | pars interarticularis cross-sectional area | T3-L5 | thoracic 7, lumbar 5 | yes | no | no | |
| UJAru, UJAlu, UJArl, UJAll | uncovertebral joint area, upper and lower, right and left | upper C3-C7, lower C2-C7 | cervical 6 | no | no | no | yes |
| UJIfu, UJIsu, UJIfl, UJIsl | uncovertebral joint inclination, frontal and sagittal, upper and lower | upper C3-C7, lower C2-C7 | cervical 6 | no | no | no | yes |
| CVAur, CVAul, CVAlr, CVAll, CVA | costovertebral articulation area, upper and lower, right and left, and the total per rib | T1-T12 | thoracic 6 | no | no | no | yes |
| CTAr, CTAl, CVA + CTA | costotransverse articulation area, and the total per rib | T1-T12 | thoracic 6 | no | no | no | yes |
| FCWsr, FCWsl, FCWir, FCWil | facet width, superior and inferior, right and left | C2-L5 | facets 2, 3 | yes | no | no | |
| FCHsr, FCHsl, FCHir, FCHil | facet height | C2-L5 | facets 2, 3 | yes | no | no | |
| FCW/FCH | facet width to height | C2-L5 | facets 2, 3 | derived | | | |
| FCAsr, FCAsl, FCAir, FCAil | facet surface area | C2-L5 | facets 4 | yes | no | no | |
| IFWs, IFWi | interfacet width, superior and inferior (right facet centre to left) | C2-L5 | facets 5 | yes | yes | no | |
| IFHr, IFHl | interfacet height (superior facet centre to inferior), right and left | C2-L5 | facets 5 | yes | no | yes | |
| IFWs/IFWi, IFW/IFH | interfacet ratios | C2-L5 | facets 5 | derived | | | |
| Tsr, Tsl, Tir, Til | facet angle to the transverse plane, superior and inferior, right and left | C2-L5 | facets 6, 7 | yes | no | no | |
| Ssr, Ssl, Sir, Sil | facet angle to the sagittal plane | C2-L5 | facets 6, 7 | yes | no | no | |
| CAXsr, CAYsr, CAXsl, CAYsl, CAXir, CAYir, CAXil, CAYil | card angles of the facet normal about X and Y | C2-L5 | facets 8 | yes | no | no | |

The thoracic specimen table (Table 1: age, sex, weight, height, cause of death of the twelve
spines) and the four comparison tables (cervical 7, thoracic 8, lumbar 6, facets 9 and 10, each
setting Panjabi's means beside earlier studies') are read too, so every printed number of the
four papers is in the file; their rows carry `study` other than `present` where the value is
another study's.

Counting the dimensions a patient's spine could give the rule: the seven in use today; areas
(EPA, SCA, PDA, PIA, FCA) and the facet linear dimensions and interfacet distances from a mask;
the pedicle and end-plate inclinations and the facet angles from a mask; and nothing of the
uncovertebral joints or the rib articulations without a CT read for them. Step e of item P adds
them to the model by kind.

## What the papers say in prose, held to the tables

[prose.csv](prose.csv) holds 249 numbers the four papers state outside their tables, in the
abstracts, the results, the discussions, the labels of Figure 8 and, about the specimens, the
Methods, each read by both prose passes and agreeing between them. 193 of them speak of cells the
tables hold and are held to them by test under the rule the sentence states: a cell's value, the
mean of the right and left, the end of a run, a difference, a ratio, a count of rows; a number the
paper rounds, with "about" or "approximately", to a multiple of five is held within 5, and one it
rounds to a whole unit within 1. Among them is the summary of the twelve spines that the cervical,
lumbar and facets papers each print in their Methods, the same 12 numbers in each paper (12
spines, 8 men and 4 women, and the mean, least and greatest age, weight and height), held to the
thoracic paper's Table 1, since the cervical paper names that study for its specimens' details
and the lumbar and facets papers refer to it for their methods and print the same summary to the
decimal. The other 56,
the counts of vertebrae (twelve spines times the levels a paper covers: 72, 144, 60 and 276),
areas approximated by a formula, rates per level, bounds and round statements, other studies'
values and quantities no table prints, are recorded alone. 175 agree with their cells. Eighteen
do not, three of them the one weight the three later papers print alike, and prose.csv records
each as a contradiction, with the cells:

| paper, page | the sentence says | the table prints |
|---|---|---|
| cervical, 861; lumbar, 299; facets, 1299 (Methods) | the twelve spines weighed 54 to 85 kg | the thoracic paper's Table 1: 54 to 84 kg, the heaviest S15 at 84 |
| lumbar, 301 | the pedicle width at L5 was 18.9 mm | Table 4: 18.0 right, 19.2 left, mean 18.6 |
| lumbar, 302 | the pars area at L5 was 81 mm2 | Table 5: 92.9 right, 71.7 left, mean 82.3 |
| thoracic, 890 | the end-plate dimensions grow from T1 to T12 by 55% for the lower width and 73% for the upper depth | Table 3: the lower width grows 51.4% and the upper 59.2%, the upper depth 77.3% and the lower 69.5%; 55.3 and 73.4 are the means of the two widths' and the two depths' increases |
| thoracic, 890 | the posterior body height at T1 is 14.3 mm | Table 3: 14.1, and Table 8's Present Study column restates 14.1 |
| thoracic, 891 | the narrowest canal, at T3, is 189 mm2 | Table 4: 180.0 at T3, the least of its row |
| thoracic, 893 | the pars area at T3 was about 90 mm2 | Table 7: 118 right, 73 left, mean 95.5 |
| thoracic, 893 | the pars area at T12 decreased to 98 mm2 | Table 7: 86 right, 98 left; the text quotes the left side |
| facets, 1298, abstract | the least facet width from C3 to L5 is 9.6 mm | Table 3: 9.5, the inferior right facet at T12 |
| facets, 1298, abstract | the least facet area from C3 to L5 is 72.3 mm2 | Table 4: 69.4, the inferior right facet at T6 |
| facets, 1298, abstract | the least Y card angle from C3 to L5 is 5.8 deg | Table 8: 4.1, the superior right facet at T1, which the results call the dip at T1 |
| facets, 1305 | the X card angle at C2 is about -41 deg | Table 8: -40.7 right, -33.5 left; the text quotes the right side |
| facets, 1307, Figure 8 | the C5 superior right Y card angle is +9.8 | Table 8, and the results on page 1306: +9.2 |
| facets, 1307 | the cervical transverse angles are 30-50 deg | Table 6: 59.4, the superior right facet at C7 |
| facets, 1307 | the transverse angle is 80 deg at L5 | Table 6: 86.0 right, 85.1 left, mean 85.6; the results say approximately 80 for the lumbar spine as a whole, which holds |

The tables decide. Where a sentence quotes one side, the table prints both; where the abstract
states a range, its ends are the tables' ends in every case but the three minima above; and the
weight's range of the specimens, printed alike in the three later papers, ends one kilogram past
the heaviest weight Table 1 prints, the papers' one slip about their specimens.

[crosstable.csv](crosstable.csv) sets the 214 Present Study values of the comparison tables
(cervical Table 7, thoracic Table 8, lumbar Table 6, facets Tables 9 and 10) beside the
dimension tables they restate: 205 agree, a single-sided dimension to the digit, a paired one as
the mean of right and left to the comparison table's rounding, the facets' sagittal angles as
the mean of the right and left magnitudes within a degree; one, Table 10's S1 row, has no cell
to be held to; and eight do not agree and are recorded as such. The thoracic paper's Table 8
restates the lower end-plate depth at T3 as 23.2 where its Table 3 prints 23.3 (the one value
the archive's transcription was once thought to have wrong, below); the lumbar paper's Table 6
restates the pedicle's sagittal inclination at L4 as 16.0 where its Table 4 prints 18.4 and
14.7, mean 16.6; the facets paper's Table 9 gives the superior facet heights at C4 to C7 as
12.0, 11.3, 10.8 and 11.0 and the widths at C4 and C7 as 11.3 and 13.4, where its Table 2's
right and left average to 12.2, 11.6, 11.0, 11.4, 11.5 and 12.6, and the paper does not say how
it formed them. [CONTRADICTIONS.md](CONTRADICTIONS.md) gathers these, the prose contradictions
and the arithmetic inside the tables (288 printed ratios and sums, 6 of which their own means
do not give even allowing for rounding) into one report with counts by paper and by kind.

## What the reference CSVs rest on, and what changes

`python check_csv.py` sets each of the 651 values of [../panjabi_full_spine.csv](../panjabi_full_spine.csv)
(296 rows of a mean and a standard error, the derived left-right means among them) and
[../panjabi_1992.csv](../panjabi_1992.csv) (30 rows) beside its cell. All 651 were read from a
cell and agree with it to the digit, the 120 of the thoracic body table since page 892 was read.
**No existing value changed in either pull request.** [changes.csv](changes.csv) is the list of
CSV values that differ from the provenance as the files stand, and is empty.

## The thoracic body table came from a second scan

Printed page 892 of the thoracic paper, Table 3 (vertebral body dimensions), is not in
[../papers/Panjabi_1991_Thoracic_Spine_16-8_888-901.pdf](../papers/Panjabi_1991_Thoracic_Spine_16-8_888-901.pdf):
the PDF's page 4 is printed page 891 and its page 5 is 893. When the provenance was first made
the 120 values the CSV carries from it rested on an earlier transcription and on Table 8's
restatement of 36 of them, and that restatement contradicted one, the lower end-plate depth at
T3, 23.3 in the transcription and 23.2 in Table 8. On 27 October 2026 the owner supplied a second
scan of the paper and asked that only the missing page be read; it is
[../papers/Panjabi_1991_Thoracic_Spine_16-8_888-901_p892.pdf](../papers/Panjabi_1991_Thoracic_Spine_16-8_888-901_p892.pdf),
one page, rendered, laid out and read twice like every other table (step 3 above), its cells
under [cells/thoracic-t3/](cells/thoracic-t3/) and its page [tables/thoracic-t3.md](tables/thoracic-t3.md).
Table 3 prints 23.3 ([cells/thoracic-t3/r07_c02.png](cells/thoracic-t3/r07_c02.png)), so the
archive's value stands, Table 8's 23.2 is the paper's own contradiction and is recorded as such
in crosstable.csv, and every one of the 120 values matches its cell; the file absent.csv, which
listed what those values rested on, is gone. The page's own text, page 890's account of the body
dimensions, is held to the table now too, and contradicts it three times (above).

## Files

| file | what it is |
|---|---|
| render.py | renders the pages (needs pdftoppm and Pillow), writing out/provenance/pages.json, and cuts the quadrant crops the prose passes read (`quadrants`) |
| tables.py | where each table sits and what its rows and columns mean |
| layout.py | finds the cells; writes cells.csv, cells/, the overlays and the reading strips (needs numpy and Pillow) |
| compile.py | sets the reads beside the cells; writes provenance.csv, tables/, pages.json, reads/pass1.csv, reads/pass2.csv |
| prose_rows.py | the prose record; makes prose.csv from the reads reads/prose.csv keeps and any later pass's files, and writes both |
| check_csv.py | holds the reference CSVs to the provenance; writes changes.csv |
| check_prose.py | holds the prose record to the cells |
| check_tables.py | holds each comparison table's Present Study column to the dimension tables it restates; writes crosstable.csv |
| contradictions.py | the report of every contradiction, between tables, between the text and the tables and inside the tables' arithmetic; writes CONTRADICTIONS.md |
| cells.csv, cells/ | every cell's box and crop |
| provenance.csv | the record, one row per printed value |
| tables/*.md | one page per table, every value beside its image |
| prose.csv, changes.csv, crosstable.csv, pages.json | the prose record, the CSV values that differ, the comparison tables' restatements, the page record |
| CONTRADICTIONS.md | the contradictions report |
| reads/ | every read of both table passes and both prose passes, as made |
