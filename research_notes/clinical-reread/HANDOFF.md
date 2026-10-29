# Handoff: the clinical reread, stopped at the owner's word

Source: thread "Reread every paper for clinical detail", project symphony_4, 2026-10-28, written at about 21:25 UTC.

## Why it stopped here

The owner wound up every thread of the project. At 20:40 UTC he asked for all threads to wrap up; at 20:41 UTC, "no
please continue checking but after finishing that stop"; at 21:17 UTC, "please wrap up all threads and get a final
handoff done, pushj everything to git so another account can continue this work". The checking ran on until the
session's usage limit stopped four of its last checks, and then this handoff was written.

## Where it stands

- 43 notes, one per paper, in [notes/](notes/). 39 have been read by a first reader and checked against the whole PDF
  by a second; their structured records are notes/<id>.json. Four were drafted by the first reader only, each marked
  so under its source line: kunkel2011, moncadahabib2025, otsuki2021 (Irie 2021) and twomey1985.
- Every note passes tools/check_notes.py (ASCII, headings, no download stamp, no copied run of 13 or more words), but
  for the four missing records.
- The synthesis (tools/synthesis.js) is written and has not been run. Nothing in [README.md](README.md)'s first findings
  comes from it; each is read from its note.
- Nothing went to the grid; no file outside research_notes/clinical-reread/ changed in this repository.

## Next, in order

1. **Check the four drafted notes.** Run the second stage of tools/reread_group.js alone for kunkel2011,
   moncadahabib2025, otsuki2021 and twomey1985: in the script, replace the first stage of the pipeline with one that
   returns null when notes/<id>.md exists, and pass the four papers' entries (id, file, pages, origin, sha256 prefix and
   focus; tools/PAPERS.sha256 has the hashes, the origins are in the notes' source lines). The skeptic writes
   notes/<id>.json last, so a note with a record is a checked note. Then run
   `python3 -I tools/check_notes.py notes <folder of the PDFs>` and reword any copied run it reports.
2. **Run the synthesis.** `python3 tools/prep_synth.py notes <scratch>/in`, then the Workflow tool with
   tools/synthesis.js and args `{"dirs": {"repo": "<bordercall clone>", "notes": "<...>/notes", "papers": "<PDF folder>",
   "syn": "<scratch>"}}`. It writes four parts (anomalies and the junctions; every measure as a recipe for a CT mask and a
   radiograph, ending in a feature-extraction line per generator measure in schwingcheck/measures.py; measurement error
   and covariates; a level atlas C2 to S1 with a playbook for the autonomous anatomist), integrates them into
   SYNTHESIS.md, has an accuracy critic and a completeness critic read it against all 43 notes, and applies what holds.
   Commit SYNTHESIS.md and the parts here, with a line in README.md.
3. **Tell the Panjabi thread, or whoever holds bordercall pull request 20 (the chain of levels)**, the anomaly priors the
   synthesis gives for its L6 and T13 transitions, by population, with what each count is made of. Until then, the
   notes' anomaly sections are the source: eisenstein1977, duman2026 and ahn2001 hold the only prevalences in the set.
4. **Two corrections for others' files, not made here:**
   - archive/bordercall/SPINEPS_MAPPING.md (line 88) and archive/bordercall/covariance.py (line 28) call Panjabi's
     specimens embalmed; his lumbar paper says fresh autopsy specimens and the thoracic paper says they were cleaned by
     boiling, bleach and ethanol ([notes/panjabi1992.md](notes/panjabi1992.md), its Gaps section). The archive is kept
     unchanged, so this waits for the owner's word on whether to correct it there or only in the new package.
   - spine-program PR 239 waits on the owner's decision of how Eisenstein measured: the note answers it (a vernier
     caliper on each dry vertebra, the canal's sagittal diameter as a minimum, the interpedicular distance as a maximum,
     film factors from 55 vertebrae of 11 skeletons at 110 cm; [notes/eisenstein1977.md](notes/eisenstein1977.md)).
5. The owner's list of 20:40 UTC asks, as its item 4, for the whole tables of Tan 2004, Busscher 2010, Lien 2007 and
   Kunkel 2011, of which only the lower rows were ever copied. Their notes say what each table holds and how it was
   measured; the tables themselves are still to be transcribed, from page images, two passes per table.

## Where the papers are, and what a new project needs

Since the owner's word of 2026-10-29 00:33 UTC all 44 PDFs are in this repository, in [papers/](papers/README.md),
each matching tools/PAPERS.sha256, so a new project needs nothing fetched or uploaded. Before that they lived only in
the project's files (literature/synthetic_spine/ with its MANIFEST.md, and the owner's uploads), and this is how they
were got, kept for anyone who must get them again:

- 20 can be fetched again by a script with a plain GET, as this thread did: 13 from PMC's Cloud Service, the public bucket
  pmc-oa-opendata (key <PMCID>.1/<PMCID>.1.pdf: abbas2021, arockiaraj2025, bonczar2024, busscher2010, cizmic2023,
  duman2026, frontphys2026, italianmri, masharawi2021, moncadahabib2025, otsuki2021, shin2024, vanderhouwen2009), yadav2020
  and ahn2001 from their publishers' open copies, and griffith2016, twomey1985, alonge2021, ahmed2019 and chaudhary2015
  from the publisher addresses in the MANIFEST. The thread's cloud environment needs full network access for it.
- 19 need the owner to upload them again, as he did here: zindrick1987, krag1988, hou1993, olsewski1990, robertson2000,
  mitra2002, yu2015, tang2016, bach2019, hinck1966, gilad1985, amonookuofi1985, amonookuofi1982, kunkel2011, lien2007,
  makino2012, eisenstein1977, tan2004 and chen2011. Springer answers a script with a JavaScript challenge, which is
  never passed, and PMC's terms leave its non-open-access papers to a person.
- Check every file against tools/PAPERS.sha256 before reading it; the notes cite pages of exactly those bytes.

## Since: the checkpoint of 2026-10-29 00:40 UTC

Source: thread "Finish the clinical reread", project symphony_4. The owner called a checkpoint at 00:38 UTC with his
usage nearly gone; this is where the next account starts. Everything below is on branch claude/project-thread-ljtlt9,
draft pull request 24, which supersedes 21.

Done:

- Step 1: the four drafted notes were checked by a second reader (commit 5edfd82); all 43 notes now have records.
- The papers: all 44 PDFs are in [papers/](papers/README.md), each matching tools/PAPERS.sha256 (the owner's word of
  00:33 UTC asked for them in git). Nothing needs fetching or uploading.
- Step 5, the whole tables: every table of the 39 papers besides Panjabi's was read twice blind, reconciled on the page
  image and mapped to schwingcheck's measures with a second reader, Tan 2004, Busscher 2010, Lien 2007 and Kunkel 2011
  among them; Griffith 2016's and Busscher 2010's second-reader checks finished last and are in. The data are
  ../paper-tables/data/ (readings, cohorts, series.csv; commit d22cbd1), and ../paper-tables/README.md says how they
  were made.
- The cadaver-power note's counts were redone on spine-program #241's corrected tables (../cadaver-power/README.md).

Started, not finished, in the order to take them:

1. **The comparison with Panjabi.** The full run was stopped part way; rerun it from the repository root in a Python
   with schwingcheck's requirements:
   `python research_notes/paper-tables/tools/cross_naming.py research_notes/paper-tables/data/series.csv research_notes/paper-tables/data/cross_naming.json --fields 200 --processes 4 --cohorts research_notes/paper-tables/data/cohorts --leave-out endplate_incl,endplate_lower_incl`
   (a two-field smoke run took 4 s; 200 fields ran over 8 minutes on 4 processes without finishing). It prints a
   RuntimeWarning at its line 181 where a pool has one zero-variance member; check the record for NaN before use.
   Then `python research_notes/paper-tables/tools/results.py research_notes/paper-tables/data research_notes/paper-tables/data/cross_naming.json research_notes/clinical-reread/notes research_notes/paper-tables/results`
   writes the evaluation as markdown with its figures and CSVs. It ran clean on the smoke record; two things to fix
   first: in transport.png panel A is drawn far wider than B and C (the panel widths), and the sharing table repeats a
   row where a paper states the same sharing twice (duman2026, mitra2002). Pig cohorts (Busscher, van der Houwen) are
   already marked species pig in the cohorts files and left out.
2. **Panjabi's end-plate inclinations.** The verdict is ../panjabi-endplate-inclination.md, a draft: one reader, checked
   on the page images; its skeptic and revision were stopped. Its recommendation is to drop endplate_incl and
   endplate_lower_incl from the pool for now (the comparison above already leaves them out) and later take Tan 2004's
   whole C3 to L5 series. Give the note to a second reader told to refute it, then tell whoever holds bordercall pull
   request 20 (the chain of levels). The page renders it cites are not kept (no page image goes in git); render them
   again from papers/.
3. **The synthesis.** Its four parts are drafted in [synthesis-draft/](synthesis-draft/README.md); the integration into
   SYNTHESIS.md and both critics did not run. Run tools/synthesis.js from its integrate step with the four parts as
   input, then the critics, then step 3 above (the anomaly priors to pull request 20's holder).
4. **The evaluation Claude Doc** (claude.ai/artifact/RF7zs7UAEGwE4ZMaQWtn8F, the owner's): its later sections are still
   placeholders. Fill them from paper-tables/results/README.md once step 1 has run; the markdown in git is the record,
   the doc a view of it.
5. Still waiting for the owner, unchanged: the "embalmed" correction in the archive (step 4 above).

Elsewhere: the chain thread's speed record is bordercall records/chain-2026-10-28/speed.json on branch
claude/project-thread-tkihxo (draft pull request 23, commit 30887cb); its re-timing on a quiet machine is left to the
next account too.
