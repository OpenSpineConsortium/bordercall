export const meta = {
  name: 'paper-tables-map',
  description: 'Give every row of each reconciled paper reading its measure in the vocabulary, its cohort and technique and its units, then have a second reader check the mapping against the paper',
  phases: [
    { title: 'Map', detail: 'one mapper per paper writes the mapped reading' },
    { title: 'Verify', detail: 'one checker per paper rereads the methods and corrects the mapping' },
  ],
}

const D = args.dirs
const WHY = `
WHY. greg (the owner, a spine surgeon-scientist) asked for every measurement table of 42 spine papers as data, each paper
"assumed to be completely different measurement techniques on completely different cadavers/persons unless textual
information confirms they share measurement methods or subjects". The tables have been transcribed and checked cell by
cell. To compare them with each other and with Panjabi's tables, on which bordercall's naming rule is built, every row now
needs: which measure it is in one shared vocabulary, which of the paper's cohorts (sets of subjects) and techniques (ways of
measuring) it belongs to, and its value in the vocabulary's units. A row mapped to the wrong measure, or a pedicle angle
mapped to the wrong plane, puts a false difference between papers into the comparison, so the definition each paper uses
is read from its Methods, never guessed from the label.
`

const SPEC = `
INPUTS.
- The reconciled reading: ${D.final}/<id>.csv (one row per printed cell and statistic; columns paper ... check_note).
- The paper's cohorts and techniques: ${D.final}/<id>.cohorts.json (cohort ids, technique ids, what each is).
- The vocabulary: ${D.tools}/vocabulary.csv (key, kind, units, whether Panjabi measured it, mnemonic, definition). Panjabi's
  keys carry his definitions; read them closely. Two traps: Panjabi's pedicle_incl_sag is the pedicle axis's angle to the
  sagittal plane, the direction most papers call the transverse or medial pedicle angle seen on an axial cut; his
  pedicle_incl_trans is the angle to the transverse plane, what most papers call the sagittal or cephalad pedicle angle.
  His canal_w is the canal's transverse diameter at the pedicles (interpedicular), his canal_ap the midline sagittal
  diameter; his end-plate widths and depths are of the end-plates, not of the body at mid-height.
- The PDF: ${D.papers}/<id>.pdf (Read with pages, at most 20 a call), for the Methods' definitions and figures.
- The clinical note on the paper: ${D.notes}/<id>.md, which describes how each measure was taken (a help, not an authority).

THE MAPPED READING: ${D.mapped}/<id>.csv, ASCII, LF line ends, written with Python's csv module from a script in your work
folder, with every row of the reconciled reading in the same order and its columns unchanged, plus these columns in order:
key, cohort, technique, factor, canonical_value, canonical_units, definition, vs_panjabi, map_note
- key: the vocabulary key the row's measure is. A row that is a subject characteristic (age, height, weight, count) takes
  its subject_ key; a reliability figure takes reliability; an anomaly count or share takes prevalence; anything no key fits
  takes other, with map_note saying what it is. Choose by the paper's definition, not by its label.
- cohort and technique: the ids of ${D.final}/<id>.cohorts.json the row's values are of. A value quoted from another study
  (source_of_values is not "this paper") takes the cohort and technique ids the cohorts file gives for quoted values; if it
  gives none, add them to the cohorts file (an entry per quoted study, "subjects": "quoted from <study>") and use them.
  technique "none" only for a row that is no measurement (a count of subjects).
- factor: what multiplies value to give the vocabulary's units (cm to mm 10, mm2 from cm2 100, rad to deg 57.2958; 1 when
  the units already match). canonical_value: value times factor, as a plain decimal, empty when value is empty.
  canonical_units: the vocabulary's units for the key; for a statistic n, count, p, r, icc, kappa or percent, the row's own.
- definition: how this paper measures the key, in your words, short (landmarks, plane, instrument), the same text on every
  row of one measure.
- vs_panjabi: for a Panjabi key, "same" where the paper's definition is Panjabi's in landmarks and plane, "close" where it
  differs in a way that moves the value little (say how in map_note), "differs" where the value means something else (say
  how); "none" for a key Panjabi did not measure.
- map_note: anything a user of the comparison must know: a sign convention (which direction is positive), a side, a
  definition you could not find in the paper (then say so and mark the key Inference).
Then run
  python3 -I ${D.tools}/check_mapped.py ${D.mapped}/<id>.csv ${D.final}/<id>.cohorts.json
and fix every problem until it prints 0 problems.
RULES. Never copy a sentence of the paper; a quote is at most 12 words. No download stamps. ASCII only.
`

function mapPrompt(id) {
  return `You map one transcribed paper's table rows to a shared measure vocabulary.
${WHY}
PAPER: ${id}. Your work folder: ${D.work}/${id}-m/ (make it).
${SPEC}
Return one paragraph: the keys you used with their row counts, every key you were unsure of and why.`
}

function verifyPrompt(id) {
  return `You are the second reader of one paper's measure mapping. Another reader mapped it; assume it is wrong until the
paper's Methods prove otherwise.
${WHY}
PAPER: ${id}. Your work folder: ${D.work}/${id}-v/ (make it).
${SPEC}
Do this:
1. List the distinct (table, measure_label, key, cohort, technique, factor, vs_panjabi) combinations of ${D.mapped}/${id}.csv.
2. For each, find the paper's own definition in its Methods (and figures) and check the key, the plane of every angle and
   its sign convention, the factor and units, the cohort and technique, and vs_panjabi against Panjabi's definition in the
   vocabulary. Check that the cohorts file's "shared" entries are what the paper states.
3. Correct every error in ${D.mapped}/${id}.csv (rewrite it with a script; keep every row and its order) and in the cohorts
   file, and run check_mapped.py until it prints 0 problems.
Return a list of what you changed, each with its page, or "no change" with what you checked.`
}

const results = await pipeline(
  args.ids,
  id => agent(mapPrompt(id), { label: `map:${id}`, phase: 'Map' }),
  (m, id) => agent(verifyPrompt(id), { label: `verify:${id}`, phase: 'Verify' })
    .then(v => ({ id, map: m ? m.slice(0, 800) : null, verify: v ? v.slice(0, 1500) : null })),
)
log(`${results.filter(r => r && r.verify).length} of ${args.ids.length} papers mapped and verified`)
return results
