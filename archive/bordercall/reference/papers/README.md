# Panjabi's quantitative three-dimensional anatomy: the four papers

The reference values in `panjabi_full_spine.csv` come from the first three papers below, one
per region. They are one series: the same twelve-specimen method, the same nomenclature, the
same instrument, published over two years. The fourth paper, on the articular facets of the
whole column, is the same group's, the same instrument and the same twelve-specimen means and
standard errors, and was added on 27 October 2026 (TODO.md, item P, step a); nothing of it is
in the CSV yet.

| File | Region | Citation | Levels |
|---|---|---|---|
| `Panjabi_1991_Cervical_Spine_16-8_861-869.pdf` | cervical | Panjabi MM, Duranceau J, Goel V, Oxland T, Takata K. *Cervical human vertebrae. Quantitative three-dimensional anatomy of the middle and lower regions.* Spine 1991;16(8):861-869 | C2-C7 |
| `Panjabi_1991_Thoracic_Spine_16-8_888-901.pdf` | thoracic | Panjabi MM, Takata K, Goel V, Federico D, Oxland T, Duranceau J, Krag M. *Thoracic human vertebrae. Quantitative three-dimensional anatomy.* Spine 1991;16(8):888-901 | T1-T12 |
| `Panjabi_1992_Lumbar_Spine_17-3_299-306.pdf` | lumbar | Panjabi MM, Goel V, Oxland T, Takata K, Duranceau J, Krag M, Price M. *Human lumbar vertebrae. Quantitative three-dimensional anatomy.* Spine 1992;17(3):299-306 | L1-L5 |
| `Panjabi_1993_Facets_Spine_18-10_1298-1310.pdf` | facets, whole column | Panjabi MM, Oxland T, Takata K, Goel V, Duranceau J, Krag M. *Articular facets of the human spine. Quantitative three-dimensional anatomy.* Spine 1993;18(10):1298-1310 | C2-L5 |

The cervical and thoracic papers are the **same journal issue**, Spine volume 16 number 8,
27 pages apart. The lumbar paper says so itself: *"this report is the third in a series of
three, the others having covered the cervical and thoracic vertebrae."* The facets paper
reports the facets of the same 276 vertebrae, C2 to L5, in one paper two years later, and
takes its citation from its own first page (Spine volume 18, number 10, pages 1298-1310,
copyright 1993 J. B. Lippincott Company).

The sha256 of each file, so a value's provenance can name the exact bytes it was read from:

| File | sha256 |
|---|---|
| `Panjabi_1991_Cervical_Spine_16-8_861-869.pdf` | a95f369e673c6567cd6061a8d0925883f78edbe643f92bcaaca45cbd4ec99391 |
| `Panjabi_1991_Thoracic_Spine_16-8_888-901.pdf` | f4078fa2cd2cf2c140fcee7f018917e055d2ca825c42e9b01d84cf1f4b7c1e2c |
| `Panjabi_1992_Lumbar_Spine_17-3_299-306.pdf` | 842736d7102c0327c690af3605c5248ca4516253ac330157875bfb783d6b5eac |
| `Panjabi_1993_Facets_Spine_18-10_1298-1310.pdf` | 2b22fe5e6c14d2289a4366f3c94879db1da0f79ae54e05a7f8e54a07e1c0279f |

An earlier note here named a second copy of the thoracic paper from document delivery, with a
partial text layer. It is not in this folder and never was in this repository; the thoracic
scan above is the one every value was read from.

## Which table each value in the CSV came from

| Measure | Cervical | Thoracic | Lumbar |
|---|---|---|---|
| end-plate width (EPWu) | Table 2, p. 863 | Table 3, p. 892 | Table 2, p. 301 |
| posterior body height (VBHp) | Table 2, p. 863 | Table 3, p. 892 | Table 2, p. 301 |
| canal width (SCW) | Table 3, p. 864 | Table 4, p. 893 | Table 3, p. 302 |
| canal depth (SCD) | Table 3, p. 864 | Table 4, p. 893 | Table 3, p. 302 |
| pedicle width (PDW) | Table 4, p. 864 | Table 5, p. 894 | Table 4, p. 302 |

The lumbar column above was corrected on 27 October 2026 from "Tables 2-5, p. 301" to the
pages the paper prints, as build_panjabi.py already had them; the end-plate depths, the lower
end-plate rows and the pedicle heights come from the same tables as their widths. The map of
every table of all four papers, with every value's cell, is [../provenance/](../provenance/README.md)
(step b of TODO.md's item P): one row per printed value in provenance.csv, one page per table
under tables/ with the image of every cell, and the thoracic body table's page 892, which this
scan does not carry, listed in absent.csv.

## The facets paper's tables

Printed page = PDF page + 1297. Tables 2 to 7 print the mean with the standard error of the
mean in parentheses in one cell, for the right (r) and left (l) facets where a dimension has a
side, at every level from C2 to L5, except their ratio columns, which print the ratio alone;
Table 8 prints the card angles as means alone, computed from the mean plane angles, with no
standard error; the comparison tables quote other authors beside this series and enter no
reference table.

| Table | Printed page | PDF page | What it holds |
|---|---|---|---|
| Table 1 | 1299 | 2 | the mnemonics of every facet dimension |
| Table 2 | 1301 | 4 | superior facet linear dimensions: width FCW and height FCH, right and left, and their ratio |
| Table 3 | 1301 | 4 | inferior facet linear dimensions: the same for the inferior facets |
| Table 4 | 1302 | 5 | surface areas FCA of the superior and inferior facets, right and left |
| Table 5 | 1302 | 5 | interfacet distances: the widths IFW between the superior and between the inferior facets, the heights IFH right and left, and their ratios |
| Table 6 | 1303 | 6 | superior facet orientations with respect to the transverse and sagittal planes, right and left |
| Table 7 | 1303 | 6 | inferior facet orientations with respect to the transverse and sagittal planes, right and left |
| Table 8 | 1304 | 7 | card angles CAX and CAY of the superior and inferior facets, right and left |
| Table 9 | 1308 | 11 | comparison with previous studies: linear dimensions |
| Table 10 | 1308 | 11 | comparison with previous studies: angular dimensions |

Figures 3 to 7 (PDF pages 8 and 9) plot the tables against level, mostly as left-right
averages; Figure 4 also draws the elliptical approximation pi x FCW x FCH / 4 of each area,
which no table prints; Figure 8 (PDF page 10) is a diagram that prints the superior right card
angles of C5, T6 and L3, and its C5 CAY reads +9.8 where Table 8 and the text of page 1306
say 9.2, a disagreement step b records.

## Four things to know before using the numbers

**Dispersion is the STANDARD ERROR, not the SD.** Every table of the first three papers says
so in its note: "the upper row shows the means, while the lower row shows the standard error of
the means", and Tables 2 to 7 of the facets paper say "Means (and Standard Errors of the Mean)"
in their titles, while its Table 8 prints averages alone. The population SD
is `sem * sqrt(12)`. Drawing the standard error as if it were an SD gives an interval 3.5x too
narrow and makes any cohort look aberrant for a reason that is arithmetic rather than
anatomical.

**Pedicle width is published per side.** The papers print PDWr and PDWl separately. The
reference table carries their mean, with the two standard errors averaged. The facets are
published per side too.

**C2 has no upper end-plate row.** The cervical paper prints a dash for EPWu, EPDu and VBHp at
C2, because the dens occupies where that end-plate would be. Those values do not exist; they
are omitted rather than filled. So end-plate width and posterior body height start at C3,
while canal and pedicle run from C2.

**The first three papers are scans with no text layer, and no paper is read by text
extraction.** Every value in the CSV was read from rendered page images. Automatic text
extraction, tried on a document-delivery copy of the thoracic paper that carried a partial text
layer, interleaved the canal table's rows and columns and produced plausible, wrong numbers;
that copy is not in this repository, and the committed scans carry no text to extract. The
facets paper carries a text layer written by the OCR program that scanned it (ABBYY
FineReader), which is not read either. The builder that produced the CSV re-checks its own T11
and T12 values against an earlier independent transcription and fails on any disagreement; all
ten match. Since 27 October 2026 every value of the CSV is also held by test to the cell it was
read from in [../provenance/provenance.csv](../provenance/provenance.csv), read twice by eye.

## The CSV

`panjabi_full_spine.csv`, 296 rows: C2-C7, T1-T12, L1-L5 for thirteen measures, the eleven
mnemonics of the body, canal and pedicle tables (EPWu, EPDu, EPWl, EPDl, VBHp, SCW, SCD, PDWr,
PDWl, PDHr, PDHl) and the two left/right means the package uses (pedicle, pedicle_h). Columns
are `measure, level, mean, sem, n, panjabi_name, source_table, source_page, citation`, so
every row names the table and page it came from. Rebuilt by
`reference/build_panjabi.py` in the bordercall repository.

These PDFs are copyrighted by Lippincott Williams & Wilkins and are here as personal
reference copies.
