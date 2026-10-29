export const meta = {
  name: 'paper-tables-read',
  description: 'Read every measurement table of a group of spine papers twice, blind, from the page images, then reconcile the two readings cell by cell on the page',
  phases: [
    { title: 'Read', detail: 'two readers per paper, each blind to the other and to every earlier reading' },
    { title: 'Reconcile', detail: 'one reconciler per paper settles every cell the readers part on, from the page, and records the cohorts' },
  ],
}

const D = args.dirs
const COLUMNS = 'paper,table,pdf_page,journal_page,row_label,column_label,measure_label,level,side,sex,group,statistic,printed_as,value,units,legibility,source_of_values,note'

const WHY = `
WHY. greg (the owner, a spine surgeon-scientist) is building a Bayesian rule that names vertebral levels from their
measured dimensions. He asked for "all the tables from these 42 papers of measurements", each paper "assumed to be
completely different measurement techniques on completely different cadavers/persons unless textual information confirms
they share measurement methods or subjects". So every measurement each paper prints is wanted as data, cell by cell, with
where it is on the page, which subjects it is of and how it was measured; nothing summarised, nothing left out because
it looks unimportant. A value read wrong goes straight into the naming model, so every number is taken from the page image.
`

const SCHEMA = `
THE READING: one CSV, ASCII, LF line ends, this header exactly:
${COLUMNS}
One row per printed cell and statistic (a cell printing "23.4 +/- 1.2" is two rows: mean 23.4 and sd 1.2; "45 (30-60)"
is three: the statistic of 45, min 30 and max 60; a cell printing only a range "30-60" is two rows, min and max).
- paper: the id given to you. table: the table's name as printed ("Table 2", "Table II", "Table S3"); a figure whose
  plot prints numbers is "Figure N"; a number given only in the text is "Text: <section>" (e.g. "Text: Results").
- pdf_page: the PDF page (1-based); journal_page: the printed page number, empty if none.
- row_label, column_label: the row's and the column's headings as printed, joined with " / " where nested (a column under
  "Male" and "Mean" is "Male / Mean"); keep them short, as printed, ASCII.
- measure_label: the measure the cell is of, as the table names it, with its abbreviation if printed ("Pedicle width (PDW)").
- level: the vertebra C1..C7, T1..T13, L1..L6, S1..S5; a disc or a space between two vertebrae as "L4-L5"; a value over
  several levels (a mean of L1 to L5) as "L1 to L5"; empty where the cell is of no level (age, height, a whole sample).
- side: empty for a midline or whole-body measure; "right", "left", "both" (the table pools the sides) or "mean of sides".
- sex: "male", "female", "all" (both sexes together), or "not stated".
- group: any other subgroup the column or row names (an age band "20-29", a population "Zulu", "stenosis", "control",
  "Part 1 cadavers", "radiographs", "CT", "direct"), as printed; empty if none.
- statistic: one of mean, sd, sem, n, min, max, median, mode, range, p, r, icc, kappa, ci_low, ci_high, percent, count,
  total, variance, iqr, q1, q3, percentile, single, ratio, difference, other. Use the table's own: an SE is sem, never sd.
  "single" is one specimen's value; "other" says in note what it is.
- printed_as: the cell's characters as printed, the one number this row is about (or the whole small cell); value: that
  number as a plain decimal (a printed ".85" is 0.85; a minus sign kept); both empty for a cell printed blank or as a dash,
  with note saying so.
- units: as printed or as the table's header gives them (mm, cm, deg, mm2, %, count, years, kg); "not printed" if none.
- legibility: "clear" or "unclear" (say in note what you could not read and what it might be).
- source_of_values: "this paper" for the paper's own subjects; for a value a comparison table quotes from another study,
  that study as the table cites it ("Panjabi et al. [12]", "Zindrick 1987").
- note: anything a user of the number must know (a footnote, a misprint you see, a unit change), paraphrased, short.
Write the file with Python's csv module (csv.writer(f, lineterminator="\\n")) from a script kept in your work folder, so
every field with a comma is quoted. Then run
  python3 -I ${D.tools}/check_reading.py <your csv> <paper id>
and fix every problem it prints until it prints 0 problems.
`

const RULES = `
RULES.
- Read the WHOLE paper, every page, as page images: the Read tool on the PDF with the pages parameter (at most 20 pages
  a call). Render every page that holds a table or a figure with numbers at 250 to 300 dpi
  (pdftoppm -r 300 -f N -l N -png <pdf> <your work folder>/pN) and Read the PNG, so that small digits are read right.
  pdftotext may help you find things, but OCR text layers misread digits: every value comes from the image.
- Transcribe EVERY table that prints a measurement, a count of subjects or a characteristic of them (age, height, weight,
  sex counts), whole: every row, every column, every cell, including tables comparing this paper with other studies
  (with source_of_values naming them), supplementary tables inside the PDF, and every number a figure prints as a data
  label. Also every measurement or count stated only in the text (Methods, Results, Discussion), and every reliability
  figure (ICC, kappa, repeat differences). Leave out only reference lists, p-values printed in prose without a table, and
  page furniture.
- Never copy a sentence of the paper into a label or a note.
- Never copy any download stamp, IP address or institutional access line a publisher printed on the page.
- ASCII only: "+/-", "deg", "mm2", "<=", no Unicode.
`

function paperBlock(p) {
  return `PAPER: ${p.id}
PDF: ${D.papers}/${p.id}.pdf (${p.pages} pages${p.scan ? '; a scan with no reliable text layer' : ''})
Tables its text layer names (may be incomplete; scans name none): ${p.tables || 'none found'}
`
}

function readPrompt(p, pass) {
  return `You transcribe the printed tables of one published spine paper from its page images. You are one of two readers
who read it independently; the other reader's work, every earlier reading and every note about this paper are kept from
you on purpose: do not open any file but the PDF and your own work folder, and do not search the repositories.
${WHY}
${paperBlock(p)}
Your work folder: ${D.work}/${p.id}-${pass}/ (make it). Write your reading to ${D.passes}/${p.id}.${pass}.csv.
${SCHEMA}
${RULES}
Return one paragraph: the tables and figures you read, the rows each gave, and every cell you could not read for sure.`
}

function reconcilePrompt(p) {
  const earlier = p.earlier ? `${D.existing}/${p.id}.csv` : null
  return `You reconcile two independent readings of one published spine paper's tables into one checked reading, and record
whose subjects and which technique every table is of.
${WHY}
${paperBlock(p)}
Readings: pass a ${D.passes}/${p.id}.a.csv, pass b ${D.passes}/${p.id}.b.csv.${earlier ? `
An earlier blind reading of some of its tables, made on 2026-10-28 for spine-program PR 239, is ${earlier} (its columns lack
source_of_values; it is a third witness, not an authority).` : ''}
The clinical note on the paper, for its population and methods (not for its values): ${D.notes}/${p.id}.md.
Your work folder: ${D.work}/${p.id}-r/ (make it).

Do this:
1. Run python3 -I ${D.tools}/compare_passes.py ${D.passes}/${p.id}.a.csv ${D.passes}/${p.id}.b.csv${earlier ? ' ' + earlier : ''}
   It matches cells within each table by (level, statistic, value) and lists every cell left over on either side. If a pass
   file is missing or empty, read every table of the paper yourself as that pass would have, then compare.
2. For every leftover cell, every table only one pass read, and every cell either pass marked unclear: render its page at
   300 dpi (pdftoppm -r 300 -f N -l N -png) and settle it on the image. Also look for any table, figure label or text
   value that BOTH passes missed, and add it.
3. Write the reconciled reading to ${D.final}/${p.id}.csv with the reading's header plus two columns, check and check_note:
   ${COLUMNS},check,check_note
   check is "agreed" (both passes read the cell the same), "resolved" (they differed or one marked it unclear, and you
   settled it on the page; check_note says what each read and what the page shows) or "single" (one pass alone read it
   and you confirmed it on the page, or you added it). Keep pass a's wording of labels unless it is wrong. Keep the
   schema below exactly. Run python3 -I ${D.tools}/check_reading.py ${D.final}/${p.id}.csv ${p.id} until 0 problems.
4. Write ${D.final}/${p.id}.cohorts.json, pretty JSON, ASCII:
   {"paper": "${p.id}",
    "cohorts": [ one per distinct set of subjects measured: {"cohort": short id, "labels": [the sex/group labels of the
       reading's rows that are this cohort's], "tables": [tables holding its values], "subjects": what and who (living
       patients, cadavers, dry bone, which collection or hospital, country, ethnicity as printed, inclusion and exclusion),
       "n_people": number or null, "n_units": "e.g. 2,166 vertebrae of 433 skeletons", "ages": "...", "sexes": "...",
       "page": "p. N (PDF N)"} ],
    "techniques": [ one per way of measuring: {"technique": short id, "cohorts": [...], "modality": "dry bone caliper |
       3D digitiser | CT axial | CT MPR | CT 3D | MRI | AP radiograph | lateral radiograph | micro-CT | meta-analysis |
       other", "instrument": "...", "how": "landmarks and plane in your words", "magnification": "corrected or not, and how",
       "observers": "...", "page": "..."} ],
    "shared": [ every statement in the paper that its subjects, its measurements or its method are the same as, or taken
       from, another study's, including any study of this list: abbas2021 ahmed2019 ahn2001 alonge2021 amonookuofi1982
       amonookuofi1985 arockiaraj2025 bach2019 bonczar2024 busscher2010 chaudhary2015 chen2011 cizmic2023 duman2026
       eisenstein1977 frontphys2026 gilad1985 griffith2016 hinck1966 hou1993 italianmri krag1988 kunkel2011 lien2007
       makino2012 masharawi2021 mitra2002 moncadahabib2025 olsewski1990 otsuki2021 panjabi1991c panjabi1991t panjabi1992
       robertson2000 shin2024 tan2004 tang2016 twomey1985 vanderhouwen2009 yadav2020 yu2015 zindrick1987:
       {"with": "the study as cited, and its id from the list if it is one", "what": "subjects | method | values quoted |
       data pooled", "evidence": "your paraphrase, or a quote of at most 12 words", "page": "..."} ],
    "within_paper": "whether the paper's own cohorts share subjects with each other (e.g. the same specimens measured by two
       methods), with the page" }
   Say only what the paper states; mark your own inference "Inference:".
${SCHEMA}
${RULES}
Return one paragraph: cells matched, resolved and single, and the cohorts and techniques you found.`
}

const results = await pipeline(
  args.group,
  p => parallel(['a', 'b'].map(pass => () =>
    agent(readPrompt(p, pass), { label: `read:${p.id}:${pass}`, phase: 'Read' }))),
  (reads, p) => agent(reconcilePrompt(p), { label: `reconcile:${p.id}`, phase: 'Reconcile' })
    .then(r => ({ id: p.id, reads: reads.map(x => x ? x.slice(0, 600) : null), reconcile: r ? r.slice(0, 1200) : null })),
)
log(`${results.filter(r => r && r.reconcile).length} of ${args.group.length} papers reconciled`)
return results
