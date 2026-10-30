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
   subgroup, by rules written in its docstring (an SE times the root of its count; the two sides averaged, a left side
   printed with the opposite sign negated first; the two sexes pooled with the difference between them taken into the
   SD; subgroups kept apart; a plain value with no SD giving way to the sides or sexes printed apart with theirs; a
   cell's mean taken from the table that prints its SD; the count read per level where a table prints one). A
   meta-analysis's SE or variance gives no SD, since it is the uncertainty of a pooled mean, not the spread of
   people. A printed value that cannot be the measure, a misprint, stays in the reading as printed but out of the
   series, each with its reason (MISPRINTS), and so do a paper's own values printed again under another label
   (REPRINTS) and those it quotes from another work on its own subjects (REPRINTED_SOURCES), so no subjects count
   twice; a side the mapping says not to use leaves the other alone (RIGHT_ONLY), and a group label the mapping
   overruled is read as its cohort's (REGROUPED), each with its reason.
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
- data/series.csv: tools/series.py over all 39, 3,760 series. Three misprints are left out: Tan 2004's L3 lower
  end-plate area, printed 172.0 mm2 between 1,090.9 and 1,199.3, Robertson 2000's left L3 pedicle height,
  printed with an SD of 13.0 mm where every other is 2.5 to 3.9, and Hou 1993's T9 cumulative pedicle height,
  12.9 mm outside its sexes' 12.2 and 12.5. Griffith 2016's model-adjusted estimates and its quartiles chosen by
  the measure, and Shin 2024's covariate-adjusted Tables 4 and 5, are no populations and make no series; the counts a paper prints for pedicles, end-plates or a range
  of levels are brought to people (series.py's docstring says how). Four rounds of independent readers checked
  series.py, cross_naming.py and results.py against the pages and the records, and each fault they found was fixed
  and checked again (tools/code_review.js, code_fix.js and code_fix_2.js, Workflow scripts).
- [validation/](validation/README.md): the validation the owner asked for on 2026-10-29 (../clinical-reread/HANDOFF.md,
  step 2). tools/validation_sample.py draws the blind re-read sample (468 cells, twelve a paper, seed 2026), ten
  readers read them from the page images without the record, and tools/validation_compare.py gives the rate: 0
  record faults in 468, Wilson interval 0.0 to 0.8 percent. tools/plausibility.py flags outliers and level
  reversals against the other papers (116 flags, every one the paper's own number on its page). The mapping audit
  (step 2c) read all 765 distinct mappings against the papers: 109 flagged, 17 held and fixed (Otsuki 2021's
  isthmus major axis is not Panjabi's pedicle height, the one fix that reaches the comparison), and 41 judgements
  the papers leave open, decided on 2026-10-30 by one rule (validation/README.md): Masharawi 2021's facet widths
  leave the comparison and Irie 2021's (filed as otsuki2021) pedicle heights at L1 to L3 rejoin it.
- [review/](review/README.md): what the four review rounds found, and round 2's findings with the refuters'
  verdicts and, for each fixed, its resolution; the data findings were fixed on 2026-10-29 and the comparison
  rerun, then a third and a fourth round read the result (pull request 39).
- data/cross_naming.json and results/: the comparison with Panjabi (step 5) at 200 fields a setting, seed 2026, with
  all 32 of Panjabi's measures scored as printed, the owner's choice of 2026-10-29 though the two end-plate
  inclinations' lumbar row repeats the cervical one (../panjabi-endplate-inclination.md), and the evaluation written
  from it by tools/results.py, its tables, figures and CSVs; [results/README.md](results/README.md) is the page to
  read and ends with the commands that remake it. A pool member with an SD of 0 (Tan 2004's SEM of 0.0 for the upper
  end-plate width at C6) is left out of the pools, and cross_naming.py refuses to write a record holding NaN or an
  infinity.

No page image or run of a paper's text is kept in git; a reading holds only the printed cells and the short labels
that name them. The 44 PDFs the readings cite are in ../clinical-reread/papers/, each matching
../clinical-reread/tools/PAPERS.sha256, on the owner's choice of 2026-10-29 03:30 UTC to keep them in main.
