export const meta = {
  name: 'synthesis-fix-parts',
  description: 'Fix each synthesis part against its critics findings, verify each fix independently, apply what the verifier finds',
  phases: [
    { title: 'Fix', detail: 'one fixer per part applies the critics findings it confirms against the notes' },
    { title: 'Verify', detail: 'one independent verifier per part checks the fixes and looks for new errors' },
    { title: 'Apply', detail: 'one agent per part applies the verifier findings it confirms' },
  ],
}

const SP = args.sp
const REPO = args.repo
const SYN = `${REPO}/research_notes/clinical-reread/synthesis`
const NOTES = `${REPO}/research_notes/clinical-reread/notes`
const FD = `${SP}/syn/findings`
const PARTS = [
  { key: 'measures', file: 'measures.md', title: 'Every measure, as a recipe for a CT mask and a radiograph',
    extra: `Its closing feature-extraction specification must have exactly one line per generator measure key in ${REPO}/schwingcheck/measures.py (check by script), each defined as Panjabi measured it. Mark endplate_incl and endplate_lower_incl there and in their sections as left out of the pool for now, with one sentence on why and a link to ../../panjabi-endplate-inclination.md (Panjabi's lumbar L1-L5 rows of these two angles reprint his cervical C3-C7 rows; read that note's section 1 and 3 for the exact wording).` },
  { key: 'anomalies', file: 'anomalies.md', title: 'Anomalies, numbering and the junctions',
    extra: `The findings whose critic is "priors verifier" come from a second reader who checked sections 1.1, 1.2 and 3 against the rendered pages; its corrected priors are the table in ${SYN}/anomaly-priors.md, which is already committed and checked. Make sections 1.1, 1.2 and 3 agree with that table (counts, intervals, what each is made of, the caveats on sacralisation, T13, no_rib_t12, Marfan) and link to it as anomaly-priors.md. Do not edit anomaly-priors.md.` },
  { key: 'error', file: 'error.md', title: 'Measurement error, modality agreement and covariates', extra: '' },
  { key: 'atlas', file: 'atlas.md', title: 'Level by level, and a playbook for the autonomous anatomist',
    extra: `The playbook steps direct an agent that names vertebrae; make sure no step contradicts a note or the corrected anomaly priors in ${SYN}/anomaly-priors.md, and that the end-plate inclination angles are not used as cues (../../panjabi-endplate-inclination.md).` },
]
const COMMON = `
CONTEXT. The owner, a spine surgeon-scientist, had 43 papers reread for clinical and anatomical detail to direct an
"autonomous anatomist": an agent that names every vertebra on a CT mask (SPINEPS instances) and on radiographs and
fluoroscopy. His Bayesian generator (bordercall's schwingcheck, on Panjabi's four cadaver papers; measures in
${REPO}/schwingcheck/measures.py) gives each instance a probability over levels and a sequence decoder names them, with
transitions for a missing body, an L6 or a T13. The synthesis has four parts in ${SYN}/ (anomalies.md, measures.md,
error.md, atlas.md), each drafted by one writer and then read by critics.

AUTHORITY. One note per paper, each checked by two readers: ${NOTES}/<id>.md with its record <id>.json. The PDFs are
${SP}/papers/<id>.pdf (outside git; Read tool with pages, or render a page with pdftoppm -r 200 into ${SP}/work/<your
label>/ where a printed digit matters). Text layers are in ${SP}/pdftext/<id>.txt.

RULES every part keeps: every statement cited by note id and page; disagreements side by side with population and
method, never averaged silently; every count says what it is made of (numerator, denominator, population; living,
cadaver, dry bone or imaging); anything derived is labelled "Inference:" with its arithmetic (recompute with python3);
no invented value; paraphrase, quote at most 12 words of a paper; ASCII only with LF line ends; no machine path (no
/home/..., /tmp/..., scratchpad/...; the notes are linked as ../notes/<id>.md, and the PDFs are not in git, so cite a
paper by note id and page, never by a file path). The file's first lines are a title and a Source line:
'Source: thread "Finish the clinical reread", project symphony_4, 2026-10-29: the synthesis of the 43 checked notes
in ../notes/, drafted by one writer, read by an accuracy critic and four completeness critics, fixed and checked again.'
Plain prose, no emoji.

NEVER run git, never edit any file but your own part file, never write outside ${SYN}/<your part> and ${SP}/work/<your label>/.
`
const OUTCOMES = {
  type: 'object',
  properties: {
    outcomes: { type: 'array', items: { type: 'object', properties: {
      index: { type: 'integer', description: 'position of the finding in the findings list, from 0' },
      outcome: { type: 'string', enum: ['applied', 'partly', 'skipped'] },
      why: { type: 'string', description: 'what you checked and, for partly or skipped, why' } },
      required: ['index', 'outcome', 'why'] } },
    other_changes: { type: 'array', items: { type: 'string' }, description: 'any change not asked by a finding, with why' },
    summary: { type: 'string' },
  },
  required: ['outcomes', 'other_changes', 'summary'],
}
const FINDINGS = {
  type: 'object',
  properties: {
    checked: { type: 'integer' },
    findings: { type: 'array', items: { type: 'object', properties: {
      kind: { type: 'string', enum: ['fix_wrong', 'fix_missing', 'skip_wrong', 'new_error', 'rule', 'missing'] },
      where: { type: 'string' }, what: { type: 'string' }, fix: { type: 'string' }, source: { type: 'string' } },
      required: ['kind', 'where', 'what', 'fix'] } },
    summary: { type: 'string' },
  },
  required: ['checked', 'findings', 'summary'],
}

function fixPrompt(p) {
  return `You are the fixer of ${SYN}/${p.file} ("${p.title}").
${COMMON}
Your findings are the JSON list in ${FD}/${p.key}.json, from an accuracy critic, four completeness critics${p.key === 'anomalies' ? ' and a priors verifier' : ''}; each has kind, where, what, fix, source and critic. Number them from 0 in list order.
A critic can be wrong. For EACH finding: open the note (and the PDF page if a printed value is at stake), decide whether it
holds, and if it does apply the fix in the part file with the Edit tool, keeping the part's structure and citation style.
A "missing" finding means adding the detail, cited, in the section it names (or the nearest fitting one). Where two
findings conflict, the note decides. Then fix every machine path and non-ASCII byte in the file (check with
grep -nP '[^\\x00-\\x7F]' and grep -nE '/home/|/tmp/|scratchpad'), set the Source line as the rules say, and run
python3 -I ${SP}/copycheck.py ${SP}/pdftext ${SYN}/${p.file} and reword every run it reports that is not a paper's title.
${p.extra}
Return one outcome per finding (applied, partly or skipped, with what you checked), the other changes you made, and a summary.`
}

function verifyPrompt(p, fixed) {
  return `You are the independent verifier of ${SYN}/${p.file} ("${p.title}"), just revised by a fixer. Assume the fixer
made mistakes until the notes prove otherwise.
${COMMON}
The findings the fixer was given are ${FD}/${p.key}.json (numbered from 0). The fixer's report is:
${JSON.stringify(fixed)}

Check, reading the part file as it now stands:
1. Every finding the fixer marked applied or partly: does the file now say the right thing, and does the note (and page) support it? Report kind fix_wrong where not.
2. Every finding marked skipped: was the reason sound? Open the note. Report kind skip_wrong where the finding held after all.
3. New errors: check at least 40 statements the fixer changed or added (find them by searching for the findings' where text and the other changes) and 20 others at random, against note and page; recompute every number and Inference. Report kind new_error.
4. Rules: Source line, ASCII (grep -nP '[^\\x00-\\x7F]'), no machine path (grep -nE '/home/|/tmp/|scratchpad'), links to ../notes/<id>.md that exist, quotes of 12 words at most, and python3 -I ${SP}/copycheck.py ${SP}/pdftext ${SYN}/${p.file} (a paper's title is allowed). Report kind rule.
${p.extra}
Never edit any file; report only, with a fix a writer can apply as written.`
}

function applyPrompt(p, review) {
  return `You apply an independent verifier's findings to ${SYN}/${p.file} ("${p.title}").
${COMMON}
The verifier's findings are below, numbered from 0. For each, check it against the note (and the PDF page where a
printed value is at stake); apply it with the Edit tool if it holds, skip it with the reason if not. Then rerun the ASCII
and machine-path greps and python3 -I ${SP}/copycheck.py ${SP}/pdftext ${SYN}/${p.file}, and fix what they report.
${p.extra}
Findings: ${JSON.stringify(review.findings)}`
}

const results = await pipeline(PARTS,
  p => agent(fixPrompt(p), { label: `fix:${p.key}`, phase: 'Fix', schema: OUTCOMES }),
  (fixed, p) => fixed ? agent(verifyPrompt(p, fixed), { label: `verify:${p.key}`, phase: 'Verify', schema: FINDINGS })
    .then(review => ({ fixed, review })) : { fixed: null, review: null },
  async (r, p) => {
    if (!r.review || !r.review.findings.length) return { part: p.key, ...r, applied: null }
    const applied = await agent(applyPrompt(p, r.review), { label: `apply:${p.key}`, phase: 'Apply', schema: OUTCOMES })
    return { part: p.key, ...r, applied }
  })
const failed = PARTS.filter((p, i) => !results[i] || !results[i].fixed).map(p => p.key)
if (failed.length) log(`no fix result for: ${failed.join(', ')}`)
return { results }