export const meta = {
  name: 'synthesis-critique',
  description: 'Accuracy critics per synthesis part and completeness critics per group of notes, against the 43 checked reread notes',
  phases: [
    { title: 'Critique', detail: 'four accuracy critics (one per part) and four completeness critics (one per quarter of the notes)' },
  ],
}

const SP = args.sp
const REPO = args.repo
const SYN = `${REPO}/research_notes/clinical-reread/synthesis`
const NOTES = `${REPO}/research_notes/clinical-reread/notes`
const PARTS = [
  { key: 'anomalies', file: 'anomalies.md', title: 'Anomalies, numbering and the junctions' },
  { key: 'measures', file: 'measures.md', title: 'Every measure, as a recipe for a CT mask and a radiograph' },
  { key: 'error', file: 'error.md', title: 'Measurement error, modality agreement and covariates' },
  { key: 'atlas', file: 'atlas.md', title: 'Level by level, and a playbook for the autonomous anatomist' },
]
const COMMON = `
CONTEXT. The owner (a spine surgeon-scientist) had 43 papers reread for clinical and anatomical detail to direct an
"autonomous anatomist": an agent that names every vertebra. His pipeline: a Bayesian generator (bordercall's schwingcheck,
on Panjabi's four cadaver papers; its measures are in ${REPO}/schwingcheck/measures.py and ${REPO}/schwingcheck/README.md,
"The measures") draws per-level dimensions with a patient size factor; code computes the same dimensions from each vertebra
instance of a real 3D CT mask (SPINEPS); the Bayes rule gives each instance a probability over levels; a sequence decoder
(HMM or Viterbi over the ordered instances, with transitions for a missing body, an L6 or a T13) turns them into names.
The same names are wanted on lateral and AP radiographs and fluoroscopy.

INPUTS. One note per paper, each checked by two readers: ${NOTES}/<id>.md and its record <id>.json. The notes are the
authority. The PDFs are ${SP}/papers/<id>.pdf (Read tool with pages; render a page with pdftoppm -r 200 into
${SP}/work/<your label>/ where a printed digit matters). The synthesis has four parts in ${SYN}/: anomalies.md, measures.md,
error.md, atlas.md, drafted by one writer each and never checked.

RULES the synthesis must keep: every statement cited by note id and page; disagreements given side by side with
population and method, never averaged silently; every count says what it is made of (numerator, denominator, population,
living, cadaver, dry bone or imaging); anything derived is labelled "Inference:" with its arithmetic; no invented value;
paraphrase, quote at most 12 words of a paper; ASCII only with LF; no machine paths (a path such as /home/user/... or
scratchpad/... is a fault: the notes folder is ../notes/ and the PDFs are not in git).

YOU: never edit any file and never run a git command; report only. Default to doubt: a statement you could not trace
to its note is "unsupported". Give each finding the part file it is in and the exact section heading, and a fix that a
writer can apply without reading your mind.
`
const FINDINGS = {
  type: 'object',
  properties: {
    checked: { type: 'integer', description: 'how many statements you checked' },
    findings: { type: 'array', items: { type: 'object', properties: {
      part: { type: 'string', enum: ['anomalies', 'measures', 'error', 'atlas'] },
      kind: { type: 'string', enum: ['wrong', 'unsupported', 'missing', 'rule', 'unclear'] },
      where: { type: 'string', description: 'section heading and, if useful, the first words of the line' },
      what: { type: 'string' }, fix: { type: 'string' },
      source: { type: 'string', description: 'note id and page (or PDF page) that proves it' } },
      required: ['part', 'kind', 'where', 'what', 'fix'] } },
    summary: { type: 'string' },
  },
  required: ['checked', 'findings', 'summary'],
}

const accuracy = PARTS.map(p => () => agent(`You are the accuracy critic of ${SYN}/${p.file} ("${p.title}").
Assume it is wrong until the notes prove otherwise.
${COMMON}
Read the whole part. Check at least 80 of its statements against the note and page each cites (and the PDF where the note
is unclear): every number, prevalence, error figure and Inference arithmetic first (recompute them with python3), then the
recipes and instructions. ${p.key === 'measures' ? `Also check its closing feature-extraction specification against ${REPO}/schwingcheck/measures.py: every generator measure key must have exactly one line, every key named must exist, and each line's definition must match how Panjabi (the notes panjabi1991c, panjabi1991t, panjabi1992, panjabi1993f) measured it.` : ''}${p.key === 'anomalies' ? ' Another verifier is checking sections 1.1, 1.2 and 3 closely; spend most of your effort on sections 1.3 to 1.6, 2 and 4.' : ''}${p.key === 'atlas' ? ' Check the playbook steps for any step that contradicts a note, or that a note shows would misname a level.' : ''}
Report every wrong, unsupported or unclear statement, every count that does not say what it is made of, every Inference not
labelled, and every rule broken. Use part "${p.key}" for findings in this file.`, { label: `accuracy:${p.key}`, phase: 'Critique', schema: FINDINGS }))

const completeness = args.groups.map((g, i) => () => agent(`You are a completeness critic of the synthesis in ${SYN}/
(anomalies.md, measures.md, error.md, atlas.md).
${COMMON}
Read every one of these ${g.length} notes whole (not a sample): ${g.map(id => `${NOTES}/${id}.md`).join(', ')}.
For each clinically or anatomically useful detail they hold that matters for naming vertebrae, or for extracting the
generator's measures from a CT mask or a radiograph, search the four parts (grep by the note id and by the detail's
keywords) and report every detail the synthesis leaves out, states more weakly than the note, or states wrongly:
anomalies and prevalences, numbering and transitional handling, measure definitions and their radiographic projections,
level-specific features, junction criteria, error and reliability figures, magnification, covariates, pearls and pitfalls,
playbook steps. Say which part the detail belongs in (part field) and the section. Give the note id and page for each.`,
  { label: `completeness:${i + 1}`, phase: 'Critique', schema: FINDINGS }))

phase('Critique')
const out = await parallel([...accuracy, ...completeness])
const labels = [...PARTS.map(p => `accuracy:${p.key}`), ...args.groups.map((g, i) => `completeness:${i + 1}`)]
const failed = labels.filter((l, i) => !out[i])
if (failed.length) log(`failed: ${failed.join(', ')}`)
return { results: out.map((r, i) => r ? { critic: labels[i], ...r } : { critic: labels[i], failed: true }) }