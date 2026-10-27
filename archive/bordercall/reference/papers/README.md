# Panjabi's quantitative three-dimensional anatomy — the three papers

The reference values in `panjabi_full_spine.csv` come from these three papers, one per
region. They are one series: the same twelve-specimen method, the same nomenclature, the
same instrument, published over two years.

| File | Region | Citation | Levels |
|---|---|---|---|
| `Panjabi_1991_Cervical_Spine_16-8_861-869.pdf` | cervical | Panjabi MM, Duranceau J, Goel V, Oxland T, Takata K. *Cervical human vertebrae. Quantitative three-dimensional anatomy of the middle and lower regions.* Spine 1991;16(8):861–869 | C2–C7 |
| `Panjabi_1991_Thoracic_Spine_16-8_888-901.pdf` | thoracic | Panjabi MM, Takata K, Goel V, Federico D, Oxland T, Duranceau J, Krag M. *Thoracic human vertebrae. Quantitative three-dimensional anatomy.* Spine 1991;16(8):888–901 | T1–T12 |
| `Panjabi_1992_Lumbar_Spine_17-3_299-306.pdf` | lumbar | Panjabi MM, Goel V, Oxland T, Takata K, Duranceau J, Krag M, Price M. *Human lumbar vertebrae. Quantitative three-dimensional anatomy.* Spine 1992;17(3):299–306 | L1–L5 |

The cervical and thoracic papers are the **same journal issue**, Spine volume 16 number 8,
27 pages apart. The lumbar paper says so itself: *"this report is the third in a series of
three, the others having covered the cervical and thoracic vertebrae."*

`Panjabi_1991_Thoracic_full_scan_with_ILL_cover.pdf` is a second copy of the thoracic paper
from document delivery (Rapid #-27455721, cross-ref 1058131, Internet Archive to Wayne
State). It is the one with a partial text layer. Kept because its page images are cleaner on
the tables that matter.

## Which table each value came from

| Measure | Cervical | Thoracic | Lumbar |
|---|---|---|---|
| end-plate width (EPWu) | Table 2, p. 863 | Table 3, p. 892 | Tables 2–5, p. 301 |
| posterior body height (VBHp) | Table 2, p. 863 | Table 3, p. 892 | Tables 2–5, p. 301 |
| canal width (SCW) | Table 3, p. 864 | Table 4, p. 893 | Tables 2–5, p. 301 |
| canal depth (SCD) | Table 3, p. 864 | Table 4, p. 893 | Tables 2–5, p. 301 |
| pedicle width (PDW) | Table 4, p. 864 | Table 5, p. 894 | Tables 2–5, p. 301 |

## Four things to know before using the numbers

**Dispersion is the STANDARD ERROR, not the SD.** Every table says so in its note: "the upper
row shows the means, while the lower row shows the standard error of the means." The
population SD is `sem * sqrt(12)`. Drawing the standard error as if it were an SD gives an
interval 3.5x too narrow and makes any cohort look aberrant for a reason that is arithmetic
rather than anatomical.

**Pedicle width is published per side.** The papers print PDWr and PDWl separately. The
reference table carries their mean, with the two standard errors averaged.

**C2 has no upper end-plate row.** The cervical paper prints a dash for EPWu, EPDu and VBHp at
C2, because the dens occupies where that end-plate would be. Those values do not exist; they
are omitted rather than filled. So end-plate width and posterior body height start at C3,
while canal and pedicle run from C2.

**Both 1991 papers are scans with no text layer.** Every value in the CSV was read from
rendered page images. Automatic text extraction of the thoracic canal table interleaves rows
and columns and produces plausible, wrong numbers — do not parse it. The builder that
produced the CSV re-checks its own T11 and T12 values against an earlier independent
transcription and fails on any disagreement; all ten match.

## The CSV

`panjabi_full_spine.csv`, 108 rows: C2–C7, T1–T12, L1–L5 for the five measures above. Columns
are `measure, level, mean, sem, n, panjabi_name, source_table, source_page, citation`, so
every row names the table and page it came from. Rebuilt by
`reference/build_panjabi.py` in the bordercall repository.

These PDFs are copyrighted by Lippincott Williams & Wilkins and are here as personal
reference copies.
