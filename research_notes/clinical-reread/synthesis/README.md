# The synthesis of the clinical reread

Source: thread "Finish the clinical reread", project symphony_4, 2026-10-29: the synthesis of the 43 checked notes in
../notes/. Confidential, like the rest of this repository.

Start with [SYNTHESIS.md](SYNTHESIS.md). It says in fifteen points what the 43 papers mean for the model that names
every vertebra, lists the papers with what each measured and on whom, introduces the parts below and names what the
set does not give.

## The files

| File | What it is | Size |
|---|---|---|
| [SYNTHESIS.md](SYNTHESIS.md) | The way in: the fifteen points for the naming model, the 43 papers by year, the parts, the gaps | 51 KB |
| [anomalies.md](anomalies.md) | Anomalies, numbering and the junctions: every prevalence, how to recognise each variant, the decoder's priors, every junction criterion | 96 KB |
| [anomaly-priors.md](anomaly-priors.md) | The decoder's priors as a second reader checked them, each count with its material, population, page and Wilson interval | 10 KB |
| [measures.md](measures.md) | Every measure as a recipe for a CT instance mask and a radiograph, a feature-extraction line per generator key, the generator's corrections | 239 KB |
| [error.md](error.md) | Measurement error, modality agreement and covariates, with the recommended error, size, sex and population terms | 91 KB |
| [atlas.md](atlas.md) | A level atlas from C2 to S1 and the autonomous anatomist's playbook for CT, films and fluoroscopy | 147 KB |

## How they were made and checked

- The four parts (anomalies.md, measures.md, error.md, atlas.md) were drafted, one writer each, by the workflow
  tools/synthesis.js from the 43 notes and their records as tools/prep_synth.py prepares them. Each draft was then
  read against the notes by an accuracy critic and four completeness critics, fixed against what held, and checked
  again by a second reader (each part's source line).
- anomaly-priors.md is a second reader's table: every count of anomalies.md, sections 1 and 3, checked against the
  rendered pages of the papers, and every share and interval recomputed (its source line). anomalies.md agrees with it.
- SYNTHESIS.md was written last, from the four parts, anomaly-priors.md, the end-plate note
  ([../../panjabi-endplate-inclination.md](../../panjabi-endplate-inclination.md)) and the evaluation on every
  paper's tables ([../../paper-tables/results/README.md](../../paper-tables/results/README.md)). Its table of papers
  was built by a script from the notes' records and each row checked against its note; the script, kept only in
  that session's scratch space, is not in git.
- The copy rule of tools/check_notes.py (no run of 13 or more words of a paper; a quote is 12 words at most) was run
  over all seven files here against the text of the papers in ../papers/ on 2026-10-29 and found no run. Seven of
  the PDFs are scans with no text layer and could not be checked that way: hou1993, krag1988, panjabi1991c,
  panjabi1991t (both files), panjabi1992 and zindrick1987.
- Every file is ASCII with LF line ends. The notes (../notes/<id>.md) stay the authority: where a file here and a
  note differ, the note wins.
