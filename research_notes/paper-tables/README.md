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

The tools are here; the readings, the mapped tables, the series and the comparison's record land beside them as each
step finishes. No PDF, page image or run of a paper's text is kept in git; the PDFs stay in the project's files.
