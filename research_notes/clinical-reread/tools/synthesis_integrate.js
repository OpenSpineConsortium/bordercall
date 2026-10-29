export const meta = {
  name: 'synthesis-integrate',
  description: 'Write SYNTHESIS.md over the four checked parts, check it with two independent readers, apply what holds',
  phases: [
    { title: 'Integrate', detail: 'one writer: the front points, the table of 43 papers, the parts' },
    { title: 'Check', detail: 'an accuracy reader and a usefulness reader, each report only' },
    { title: 'Apply', detail: 'one agent applies the readers findings it confirms' },
  ],
}
const SP = args.sp
const REPO = args.repo
const CR = `${REPO}/research_notes/clinical-reread`
const SYN = `${CR}/synthesis`
const COMMON = `
CONTEXT. The owner, a spine surgeon-scientist, had 43 papers reread for clinical and anatomical detail to direct an
"autonomous anatomist": an agent that names every vertebra on a CT mask (SPINEPS instances) and on radiographs and
fluoroscopy. His Bayesian generator (bordercall's schwingcheck, built on Panjabi's four cadaver papers; measures in
${REPO}/schwingcheck/measures.py, README ${REPO}/schwingcheck/README.md) gives each instance a probability over levels,
and a sequence decoder (the chain of levels) names them, with transitions for a missing body, an L6 or a T13.
Files: one checked note per paper, ${CR}/notes/<id>.md with its record <id>.json (43 papers); the PDFs ${CR}/papers/<id>.pdf;
the synthesis parts in ${SYN}/: anomalies.md, measures.md, error.md, atlas.md, each read by critics, fixed and checked by
a second reader, and anomaly-priors.md, the checked table of anomaly priors. Two other research notes the synthesis
links: ${REPO}/research_notes/panjabi-endplate-inclination.md (Panjabi's lumbar end-plate inclination rows reprint his
cervical rows; drop both angles from the pool for now) and ${REPO}/research_notes/paper-tables/results/README.md (the
other papers' tables set beside Panjabi's).
RULES: every statement cited by part section or note id and page; every count says what it is made of (numerator,
denominator, population; living, cadaver, dry bone or imaging); anything derived labelled "Inference:" with its
arithmetic; no invented value; paraphrase, quote at most 12 words of a paper; ASCII only with LF; no machine path
(link files relatively: notes as ../notes/<id>.md, parts as anomalies.md etc., the end-plate note as
../../panjabi-endplate-inclination.md); plain prose that says why, no emoji, no marketing words. Scratch:
${SP}/work/<your label>/. Never run git.`

phase('Integrate')
const written = await agent(`You write ${SYN}/SYNTHESIS.md and rewrite ${SYN}/README.md.
${COMMON}
Read the four parts and anomaly-priors.md whole first, and the 43 note records for the table.
SYNTHESIS.md, in this order:
1. Title "The clinical reread: synthesis" and a Source line: 'Source: thread "Finish the clinical reread", project
   symphony_4, 2026-10-29: the synthesis of the 43 checked notes in ../notes/; each part was drafted by one writer, read
   by an accuracy critic and four completeness critics, fixed against them and checked again by a second reader.'
2. "## What this means for the naming model": at most 15 numbered points, the ones that change what the generator,
   the measurer or the decoder should do, most consequential first. Each point: the finding in one or two sentences,
   what to do about it, and links to the part section(s) and notes that hold the evidence. Draw them from all four parts
   and the anomaly priors (the decoder's transitions), the end-plate inclination verdict, measurement error that bounds
   what a measure can tell apart, the junction cues, magnification on films and fluoroscopy, and the covariates.
   Say plainly where the papers give no answer.
3. "## The 43 papers": one table row per note, ordered by year: paper (author year, linked to ../notes/<id>.md),
   what it measured, material and population with n (living imaging, cadaver, dry bone), modality, levels, and which
   parts lean on it most. Build it from the records with python, then check each row against its note.
4. "## The parts": one paragraph each for anomalies.md, measures.md, error.md, atlas.md and anomaly-priors.md (what it
   holds, who should read it, its size), then why the parts stay separate files: together they are about 600 KB, too
   long to read or render as one page, and each serves a different reader (the decoder, the measurer, the error model,
   the agent's playbook); this file is the way in.
5. "## What the set does not give": the gaps that matter for naming, from the parts and anomaly-priors.md.
README.md: replace the draft's text with a short page saying what each file is, how it was made and checked, and that
SYNTHESIS.md is the place to start. Return a summary of what you wrote and every place you were unsure.`,
  { label: 'integrate', phase: 'Integrate' })

phase('Check')
const SCHEMA = { type: 'object', properties: { checked: { type: 'integer' },
  findings: { type: 'array', items: { type: 'object', properties: { kind: { type: 'string', enum: ['wrong', 'unsupported', 'missing', 'overstated', 'rule', 'unclear'] },
    where: { type: 'string' }, what: { type: 'string' }, fix: { type: 'string' }, source: { type: 'string' } },
    required: ['kind', 'where', 'what', 'fix'] } }, summary: { type: 'string' } }, required: ['checked', 'findings', 'summary'] }
const checks = await parallel([
  () => agent(`You are the accuracy reader of ${SYN}/SYNTHESIS.md, just written. Assume each statement is wrong until the
part section and the note it rests on prove it.
${COMMON}
Check every numbered point and every number in it against the part it links and that part's note and page; recompute
every Inference; check every row of the table of 43 papers against its note (author, year, material, n, modality,
levels); check every link resolves (relative to ${SYN}/); check the rules (ASCII, no machine path, quotes, Source line),
and run python3 -I ${SP}/copycheck.py ${SP}/pdftext ${SYN}/SYNTHESIS.md ${SYN}/README.md. Report only, never edit.`,
    { label: 'check:accuracy', phase: 'Check', schema: SCHEMA }),
  () => agent(`You are the usefulness reader of ${SYN}/SYNTHESIS.md, just written, read as the person who will change the
generator, the measurer and the decoder next. Report what is missing, overstated or unclear.
${COMMON}
Read the four parts' section headings and the anomaly-priors table, schwingcheck/README.md "The measures", and
the end-plate note's section 3. Ask of the front points: is anything in the parts that would change the naming model
left out, or ranked too low? Is any point a summary with no action? Does any overstate what the papers show (a
single small cadaver series given as a population fact, a ceiling given as a point)? Does each action say which file or
component it changes? Is any point beyond the 15? Is "What the set does not give" complete for naming? Report only,
never edit; each finding with a fix a writer can apply as written.`,
    { label: 'check:usefulness', phase: 'Check', schema: SCHEMA }),
])
const findings = checks.filter(Boolean).flatMap((c, i) => c.findings.map(f => ({ reader: i === 0 ? 'accuracy' : 'usefulness', ...f })))
log(`${findings.length} findings from the two readers`)

phase('Apply')
const applied = findings.length ? await agent(`You apply two independent readers' findings to ${SYN}/SYNTHESIS.md (and
${SYN}/README.md where a finding names it).
${COMMON}
For each finding (numbered from 0 below): check it against the part and the note; apply it with the Edit tool if it
holds, skip it with the reason if not. Keep the front list at 15 points or fewer. Then rerun the ASCII and machine-path
greps (grep -nP '[^\\x00-\\x7F]', grep -nE '/home/|/tmp/|scratchpad'), check every relative link resolves, and run
python3 -I ${SP}/copycheck.py ${SP}/pdftext ${SYN}/SYNTHESIS.md ${SYN}/README.md, fixing what they report.
Findings: ${JSON.stringify(findings)}`,
  { label: 'apply', phase: 'Apply', schema: { type: 'object', properties: {
    outcomes: { type: 'array', items: { type: 'object', properties: { index: { type: 'integer' }, outcome: { type: 'string', enum: ['applied', 'partly', 'skipped'] }, why: { type: 'string' } }, required: ['index', 'outcome', 'why'] } },
    summary: { type: 'string' } }, required: ['outcomes', 'summary'] } }) : null
return { written, checks, applied }