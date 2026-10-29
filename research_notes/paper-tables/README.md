# Every measurement table of the papers, as data

Source: thread "Finish the clinical reread", project symphony_4, 2026-10-28, from 22:11 UTC.
Confidential, like the rest of this repository: nothing here goes to a public place.

## Why

On 2026-10-28 at 22:10 UTC the owner asked for the naming rule's evaluation to be made again "with all the tables from
these 42 ... papers of measurements assumed to be completely different measurement techniques on completely different
cadavers/persons unless textual information confims they share measurement methods or subjects". Panjabi's four papers
are already held cell by cell in archive/bordercall/reference/provenance/. This folder holds the other papers' tables,
read the same careful way, and the code that sets them beside Panjabi's: how far each paper's means sit from his, and
what naming fields drawn from each paper's own tables with his rule costs.

## How a table becomes data

1. **Read twice, blind** (tools/read_tables.js, a Workflow script). Two readers per paper read every measurement table
   from the page images, each blind to the other and to any earlier reading, one row per printed cell and statistic;
   tools/check_reading.py refuses a reading whose header, values, levels or statistics are malformed.
2. **Reconciled on the page.** tools/compare_passes.py lists, table by table, every cell the two readings part on, and a
   third reader settles each one from the page image and records the paper's cohorts (sets of subjects) and techniques
   (ways of measuring) in <id>.cohorts.json, with every place the text says two of them share subjects or a method.
3. **Mapped to one vocabulary** (tools/map_measures.js). Each row gets its measure as a key of tools/vocabulary.csv
   (Panjabi's 32 measures and the other papers' own), its cohort and technique, its value in the vocabulary's units, the
   paper's own definition, and whether that definition is Panjabi's ("same", "close", "differs" or "none"); a second
   reader rechecks every combination against the Methods. tools/check_mapped.py holds every mapped file to the
   vocabulary and the cohorts.
4. **Series** (tools/series.py). One mean, population SD and count per measure, level, cohort, technique, sex and
   subgroup, by rules written in its docstring (an SE times the root of its count; the two sides averaged; the two
   sexes pooled with the difference between them taken into the SD; subgroups kept apart).
5. **Set beside Panjabi** (tools/cross_naming.py, in schwingcheck's environment): disagreement (each source's mean in
   Panjabi's SDs and in levels, and the between-source spread of a random-effects pool), transport (fields drawn from a
   source's series named by Panjabi's rule, against fields drawn from his own table at the same places), and a rule
   widened by the papers' disagreement, scored leaving each paper out.

Each paper counts as its own subjects and its own technique unless its text says otherwise; Panjabi's four papers
measured the same twelve spines.

## Where it stands

All 39 papers of the list other than Panjabi's four are read, reconciled and mapped (2026-10-29): 23,918 cells, of
which the two blind readings agreed on 20,750, a third reader settled 2,271 from the page and 897 were read by one
reader and checked on the page; every mapped file passes tools/check_mapped.py, and a second reader checked every
paper's mapping against its Methods.

- data/readings/<id>.csv: each paper's reconciled reading with its mapping (the columns of step 3).
- data/cohorts/<id>.cohorts.json: its cohorts, techniques and every stated or inferred sharing, with the page. A
  cohort that is not human carries "species" (Busscher 2010's and van der Houwen 2009's pig spines), and
  tools/cross_naming.py leaves it out of everything.
- data/series.csv: tools/series.py over all 39, 4,477 series.

The comparison with Panjabi (tools/cross_naming.py, step 5) and the evaluation's tables and figures follow in
results/. The PDFs read are in ../clinical-reread/papers/ (the owner's word of 2026-10-29); no page image or run of a
paper's text is kept, and a reading holds only the printed cells and the short labels that name them.
